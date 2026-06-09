"""Transform orchestration service."""
import logging
import time
from datetime import datetime
from typing import Optional

from app.database import Database
from app.engine.transform_engine import TransformEngine
from app.models.domain import (
    RawRecord,
    TemperatureRecord,
    TransformLog,
    UnmatchedItem,
    gen_object_id,
)
from app.utils.idempotent import make_idempotent_key

logger = logging.getLogger(__name__)


class TransformService:
    """Orchestrate the full transform flow: parse, match, transform, persist."""

    def transform_and_save(
        self,
        vendor_code: str,
        raw_data: str,
        access_type: str = "manual",
        source_ip: Optional[str] = None,
    ) -> dict:
        """Run the full transform pipeline for a vendor's raw data.

        Steps:
            1. Save raw record
            2. Load parser config and item rules
            3. Run TransformEngine
            4. Save temperature records (idempotent dedup)
            5. Save unmatched items
            6. Save transform log
            7. Return results

        Returns:
            A dict with transform results and metadata.
        """
        start_time = time.time()
        batch_id = gen_object_id()

        # 1. Save raw record
        raw_record_id = self._save_raw_record(vendor_code, raw_data, access_type, batch_id, source_ip)

        # 2. Load parser config and item rules
        parser_col = Database.get_collection("parser_configs")
        parser_doc = parser_col.find_one({"vendorCode": vendor_code})
        if not parser_doc:
            error_msg = f"No parser config for vendor '{vendor_code}'"
            self._update_raw_record_status(raw_record_id, "failed", error_msg)
            return {"success": False, "error": error_msg, "batchId": batch_id}

        # Convert list-based field mappings to dict format for the engine
        def _list_to_dict(mappings):
            if isinstance(mappings, dict):
                return mappings
            if isinstance(mappings, list):
                result = {}
                for m in mappings:
                    if isinstance(m, dict) and "targetField" in m:
                        result[m["targetField"]] = m
                return result
            return {}

        parser_config: dict = {
            "format": parser_doc.get("dataFormat", "json"),
            "recordPath": parser_doc.get("recordPath", "$"),
            "itemPath": parser_doc.get("itemPath"),
            "rootFieldMappings": _list_to_dict(parser_doc.get("rootFieldMappings", [])),
            "recordFieldMappings": _list_to_dict(parser_doc.get("recordFieldMappings", [])),
            "itemFieldMappings": _list_to_dict(parser_doc.get("itemFieldMappings", [])),
        }

        rules_col = Database.get_collection("item_mapping_rules")
        rules_doc = rules_col.find_one({"vendorCode": vendor_code})
        item_rules: list[dict] = rules_doc.get("rules", []) if rules_doc else []

        # 3. Run TransformEngine
        engine = TransformEngine(parser_config, item_rules)
        result = engine.transform(raw_data, vendor_code)

        temp_record_ids: list[str] = []
        unmatched_ids: list[str] = []

        # 4. Save temperature records
        if result["records"]:
            temp_record_ids = self._save_temperature_records(
                result["records"], vendor_code, batch_id, raw_record_id
            )

        # 5. Save unmatched items
        if result["unmatched"]:
            unmatched_ids = self._save_unmatched_items(
                result["unmatched"], vendor_code, batch_id
            )

        # 6. Save transform log
        duration = int((time.time() - start_time) * 1000)
        log_status = "success" if result["fail"] == 0 else ("partial" if result["success"] > 0 else "failed")
        log_id = self._save_transform_log(
            batch_id=batch_id,
            vendor_code=vendor_code,
            access_type=access_type,
            status=log_status,
            total_records=result["total"],
            success_count=result["success"],
            fail_count=result["fail"],
            unmatched_count=len(result["unmatched"]),
            raw_record_ids=[raw_record_id],
            temperature_record_ids=temp_record_ids,
            errors=result["errors"],
            duration=duration,
        )

        # Update raw record status
        self._update_raw_record_status(raw_record_id, log_status)

        logger.info(
            "Transform complete for vendor '%s': batch=%s, success=%d, fail=%d, unmatched=%d, duration=%dms",
            vendor_code, batch_id, result["success"], result["fail"],
            len(result["unmatched"]), duration,
        )

        return {
            "success": result["fail"] == 0,
            "batchId": batch_id,
            "rawRecordId": raw_record_id,
            "transformLogId": log_id,
            "totalRecords": result["total"],
            "successCount": result["success"],
            "failCount": result["fail"],
            "unmatchedCount": len(result["unmatched"]),
            "temperatureRecordIds": temp_record_ids,
            "errors": result["errors"],
            "duration": duration,
        }

    def transform_single(self, raw_record_id: str) -> dict:
        """Re-transform a single raw record by its ID.

        Returns:
            Transform result dict (same shape as ``transform_and_save``).
        """
        raw_col = Database.get_collection("raw_records")
        raw_doc = raw_col.find_one({"_id": raw_record_id})
        if not raw_doc:
            return {"success": False, "error": f"Raw record '{raw_record_id}' not found"}

        vendor_code = raw_doc.get("vendorCode", "")
        raw_content = raw_doc.get("rawContent", "")
        access_type = raw_doc.get("accessType", "manual")

        return self.transform_and_save(vendor_code, raw_content, access_type)

    def _save_raw_record(
        self,
        vendor_code: str,
        raw_data: str,
        access_type: str,
        batch_id: str,
        source_ip: Optional[str],
    ) -> str:
        """Persist a raw record and return its ID."""
        col = Database.get_collection("raw_records")
        record = RawRecord(
            vendorCode=vendor_code,
            accessType=access_type,
            batchId=batch_id,
            rawContent=raw_data,
            contentType="json",
            sourceIp=source_ip,
            status="pending",
        )
        doc = record.to_dict()
        col.insert_one(doc)
        logger.debug("Saved raw record '%s' for vendor '%s'", record.id, vendor_code)
        return record.id

    def _save_temperature_records(
        self,
        records: list[dict],
        vendor_code: str,
        batch_id: str,
        raw_record_id: str,
    ) -> list[str]:
        """Save transformed temperature records with idempotent dedup.

        Returns a list of inserted record IDs.  Records whose idempotentKey
        already exists are skipped.
        """
        col = Database.get_collection("temperature_records")
        inserted_ids: list[str] = []

        for rec_data in records:
            # Build the domain model to ensure consistent structure
            temp_rec = TemperatureRecord(
                patientId=rec_data.get("patientId", ""),
                vendorCode=vendor_code,
                batchId=batch_id,
                rawRecordId=raw_record_id,
                visitNo=rec_data.get("visitNo"),
                patientVisitId=rec_data.get("patientVisitId"),
                wardCode=rec_data.get("wardCode"),
                bedNo=rec_data.get("bedNo"),
                recordTime=rec_data.get("recordTime"),
                operatorCode=rec_data.get("operatorCode"),
                operatorName=rec_data.get("operatorName"),
                items=rec_data.get("items", []),
                idempotentKey=rec_data.get("idempotentKey"),
                status="transformed",
            )

            # Idempotent dedup: skip if key already exists
            if temp_rec.idempotentKey:
                existing = col.find_one({"idempotentKey": temp_rec.idempotentKey})
                if existing:
                    logger.debug("Skipping duplicate record with key '%s'", temp_rec.idempotentKey)
                    inserted_ids.append(str(existing["_id"]))
                    continue

            doc = temp_rec.to_dict()
            col.insert_one(doc)
            inserted_ids.append(temp_rec.id)

        logger.info("Saved %d temperature records for vendor '%s'", len(inserted_ids), vendor_code)
        return inserted_ids

    def _save_unmatched_items(
        self,
        unmatched: list[dict],
        vendor_code: str,
        batch_id: str,
    ) -> list[str]:
        """Persist unmatched items and return their IDs."""
        col = Database.get_collection("unmatched_items")
        ids: list[str] = []

        for item_data in unmatched:
            unmatched_item = UnmatchedItem(
                vendorCode=vendor_code,
                batchId=batch_id,
                itemData=item_data,
                status="pending",
            )
            doc = unmatched_item.to_dict()
            col.insert_one(doc)
            ids.append(unmatched_item.id)

        logger.info("Saved %d unmatched items for vendor '%s'", len(ids), vendor_code)
        return ids

    def _save_transform_log(
        self,
        batch_id: str,
        vendor_code: str,
        access_type: str,
        status: str,
        total_records: int,
        success_count: int,
        fail_count: int,
        unmatched_count: int,
        raw_record_ids: list[str],
        temperature_record_ids: list[str],
        errors: list[dict],
        duration: int,
    ) -> str:
        """Persist a transform log entry and return its ID."""
        col = Database.get_collection("transform_logs")
        log = TransformLog(
            batchId=batch_id,
            vendorCode=vendor_code,
            accessType=access_type,
            status=status,
            totalRecords=total_records,
            successCount=success_count,
            failCount=fail_count,
            unmatchedCount=unmatched_count,
            rawRecordIds=raw_record_ids,
            temperatureRecordIds=temperature_record_ids,
            errors=errors,
            duration=duration,
        )
        doc = log.to_dict()
        col.insert_one(doc)
        logger.debug("Saved transform log '%s' for vendor '%s'", log.id, vendor_code)
        return log.id

    def _update_raw_record_status(self, raw_record_id: str, status: str, error: Optional[str] = None) -> None:
        """Update the status of a raw record."""
        col = Database.get_collection("raw_records")
        update: dict = {"status": status}
        if error:
            update["lastError"] = error
        col.update_one({"_id": raw_record_id}, {"$set": update})
