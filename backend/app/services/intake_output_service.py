"""Intake/Output calculation and management service."""
import logging
from datetime import datetime
from typing import Optional

from app.database import Database
from app.models.domain import (
    IntakeOutputItemConfig,
    IntakeOutputResult,
    IntakeOutputStatRule,
    IntakeOutputUnmatchedItem,
    gen_object_id,
)
from app.services.intake_output_calculator import IntakeOutputCalculator
from app.services.smartcare_service import SmartCareService

logger = logging.getLogger(__name__)

RESULTS_COLLECTION = "intake_output_results"
ITEM_CONFIGS_COLLECTION = "intake_output_item_configs"
STAT_RULES_COLLECTION = "intake_output_stat_rules"
LOGS_COLLECTION = "intake_output_logs"
UNMATCHED_COLLECTION = "intake_output_unmatched_items"


class IntakeOutputService:
    """Manage intake/output calculations for SmartCare bedside data."""

    def __init__(self) -> None:
        self.calculator = IntakeOutputCalculator()
        self._smartcare_service = SmartCareService()

    def preview(
        self,
        datasource_id: str,
        patient_id: str,
        start_time,
        end_time,
    ) -> dict:
        """Preview intake/output calculation without saving results.

        Returns:
            A dict with calculation results, unmatched items, and patient info.
        """
        return self._run_calculation(
            datasource_id, patient_id, start_time, end_time, save=False
        )

    def calculate(
        self,
        datasource_id: str,
        patient_id: str,
        start_time,
        end_time,
    ) -> dict:
        """Calculate and save intake/output results.

        Returns:
            A dict with calculation results and the saved result ID.
        """
        return self._run_calculation(
            datasource_id, patient_id, start_time, end_time, save=True
        )

    def _run_calculation(
        self,
        datasource_id: str,
        patient_id: str,
        start_time,
        end_time,
        save: bool = False,
    ) -> dict:
        """Core calculation flow shared by preview and calculate.

        Returns:
            {
                "patientId": str,
                "patientName": str,
                "bedNo": str,
                "wardCode": str,
                "calcTime": str,
                "statTimeRange": dict,
                "results": list,
                "unmatched": list,
                "rawBedsideIds": list,
                "resultId": str (if saved)
            }
        """
        # Get patient info
        patient_info = self._smartcare_service.get_patient(datasource_id, patient_id=patient_id) or {}

        # Get bedside records
        bedside_records = self._smartcare_service.get_bedside_records(
            datasource_id, patient_id, start_time, end_time
        )

        # Get item configs
        item_configs = self._get_item_configs_list(datasource_id)

        # Get stat rules
        stat_rules = self._get_stat_rules_list(datasource_id)

        # Get field mappings for bedside collection
        field_mappings = self._smartcare_service._get_field_mappings(datasource_id, "bedside")

        # Run calculation
        calc_result = self.calculator.calculate(
            bedside_records=bedside_records,
            item_configs=item_configs,
            stat_rules=stat_rules,
            patient_info=patient_info,
            start_time=start_time,
            end_time=end_time,
            field_mappings=field_mappings,
        )

        now = datetime.utcnow()
        raw_bedside_ids = [
            str(r.get("_id", "")) for r in bedside_records if r.get("_id")
        ]

        # Map patient fields using field mappings
        name_key = field_mappings.get("patientName", "patientName") if field_mappings else "patientName"
        bed_key = field_mappings.get("bedNo", "bedNo") if field_mappings else "bedNo"
        ward_key = field_mappings.get("wardCode", "wardCode") if field_mappings else "wardCode"

        response: dict = {
            "patientId": patient_id,
            "patientName": patient_info.get(name_key, patient_info.get("patientName", "")),
            "bedNo": patient_info.get(bed_key, patient_info.get("bedNo", "")),
            "wardCode": patient_info.get(ward_key, patient_info.get("wardCode", "")),
            "calcTime": now.isoformat(),
            "statTimeRange": {
                "start": start_time.isoformat() if isinstance(start_time, datetime) else str(start_time),
                "end": end_time.isoformat() if isinstance(end_time, datetime) else str(end_time),
            },
            "results": calc_result["results"],
            "unmatched": calc_result["unmatched"],
            "rawBedsideIds": raw_bedside_ids,
        }

        if save:
            # Save the result
            result_doc = IntakeOutputResult(
                datasourceId=datasource_id,
                patientId=patient_id,
                hisPid=patient_info.get("hisPid"),
                mrn=patient_info.get("mrn"),
                patientName=response["patientName"],
                bedNo=response["bedNo"],
                wardCode=response["wardCode"],
                calcTime=now,
                statTimeRange=response["statTimeRange"],
                results=calc_result["results"],
                rawBedsideIds=raw_bedside_ids,
                status="completed",
            )
            col = Database.get_collection(RESULTS_COLLECTION)
            col.insert_one(result_doc.to_dict())
            response["resultId"] = result_doc.id

            # Save unmatched items
            if calc_result["unmatched"]:
                self._save_unmatched_items(
                    datasource_id, patient_id, calc_result["unmatched"], field_mappings
                )

            # Save log
            self._save_log(datasource_id, patient_id, len(bedside_records),
                           len(calc_result["results"]), len(calc_result["unmatched"]))

            logger.info(
                "Saved intake/output result for patient '%s': %d results, %d unmatched",
                patient_id, len(calc_result["results"]), len(calc_result["unmatched"]),
            )

        return response

    def get_results(
        self,
        datasource_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        """Return saved intake/output results.

        Returns:
            A list of result documents.
        """
        col = Database.get_collection(RESULTS_COLLECTION)
        query: dict = {}
        if datasource_id:
            query["datasourceId"] = datasource_id
        if patient_id:
            query["patientId"] = patient_id
        return list(col.find(query).sort("createdAt", -1).limit(limit))

    def get_logs(self, datasource_id: Optional[str] = None, limit: int = 50) -> list:
        """Return intake/output calculation logs.

        Returns:
            A list of log documents.
        """
        col = Database.get_collection(LOGS_COLLECTION)
        query: dict = {}
        if datasource_id:
            query["datasourceId"] = datasource_id
        return list(col.find(query).sort("createdAt", -1).limit(limit))

    # ------------------------------------------------------------------
    # Item config CRUD
    # ------------------------------------------------------------------

    def save_item_config(self, data: dict) -> dict:
        """Insert or update an intake/output item config.

        Returns:
            The saved item config document.
        """
        col = Database.get_collection(ITEM_CONFIGS_COLLECTION)
        now = datetime.utcnow()

        ds_id = data.get("datasourceId", "")
        param_code = data.get("paramCode", "")

        existing = col.find_one({"datasourceId": ds_id, "paramCode": param_code})

        if existing:
            update_fields: dict = {
                "paramName": data.get("paramName"),
                "category": data.get("category"),
                "subCategory": data.get("subCategory"),
                "statType": data.get("statType", "sum"),
                "unit": data.get("unit"),
                "includeInTotalInput": data.get("includeInTotalInput"),
                "includeInTotalOutput": data.get("includeInTotalOutput"),
                "enabled": data.get("enabled", True),
                "autoDetected": data.get("autoDetected", False),
                "calculation": data.get("calculation"),
                "updatedAt": now,
            }
            col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
            return col.find_one({"_id": existing["_id"]})

        item = IntakeOutputItemConfig(
            datasourceId=ds_id,
            paramCode=param_code,
            paramName=data.get("paramName"),
            category=data.get("category"),
            subCategory=data.get("subCategory"),
            statType=data.get("statType", "sum"),
            unit=data.get("unit"),
            includeInTotalInput=data.get("includeInTotalInput"),
            includeInTotalOutput=data.get("includeInTotalOutput"),
            enabled=data.get("enabled", True),
            autoDetected=data.get("autoDetected", False),
            calculation=data.get("calculation"),
            createdAt=now,
            updatedAt=now,
        )
        doc = item.to_dict()
        col.insert_one(doc)
        return doc

    def get_item_configs(self, datasource_id: str) -> list:
        """Return all item configs for a datasource.

        Returns:
            A list of item config documents.
        """
        col = Database.get_collection(ITEM_CONFIGS_COLLECTION)
        return list(col.find({"datasourceId": datasource_id}).sort("paramCode", 1))

    def _get_item_configs_list(self, datasource_id: str) -> list[dict]:
        """Return enabled item configs as plain dicts for the calculator."""
        col = Database.get_collection(ITEM_CONFIGS_COLLECTION)
        docs = list(col.find({"datasourceId": datasource_id, "enabled": True}))
        # Remove MongoDB _id for cleaner processing
        for doc in docs:
            doc.pop("_id", None)
        return docs

    # ------------------------------------------------------------------
    # Stat rule CRUD
    # ------------------------------------------------------------------

    def save_stat_rule(self, data: dict) -> dict:
        """Insert or update an intake/output stat rule.

        Returns:
            The saved stat rule document.
        """
        col = Database.get_collection(STAT_RULES_COLLECTION)
        now = datetime.utcnow()

        ds_id = data.get("datasourceId", "")
        code = data.get("code", "")

        existing = col.find_one({"datasourceId": ds_id, "code": code})

        if existing:
            update_fields: dict = {
                "name": data.get("name"),
                "category": data.get("category"),
                "subCategory": data.get("subCategory"),
                "statType": data.get("statType"),
                "timeWindow": data.get("timeWindow"),
                "targetItemCode": data.get("targetItemCode"),
                "targetItemName": data.get("targetItemName"),
                "unit": data.get("unit"),
                "enabled": data.get("enabled", True),
            }
            col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
            return col.find_one({"_id": existing["_id"]})

        rule = IntakeOutputStatRule(
            datasourceId=ds_id,
            code=code,
            name=data.get("name"),
            category=data.get("category"),
            subCategory=data.get("subCategory"),
            statType=data.get("statType"),
            timeWindow=data.get("timeWindow"),
            targetItemCode=data.get("targetItemCode"),
            targetItemName=data.get("targetItemName"),
            unit=data.get("unit"),
            enabled=data.get("enabled", True),
            createdAt=now,
        )
        doc = rule.to_dict()
        col.insert_one(doc)
        return doc

    def get_stat_rules(self, datasource_id: str) -> list:
        """Return all stat rules for a datasource.

        Returns:
            A list of stat rule documents.
        """
        col = Database.get_collection(STAT_RULES_COLLECTION)
        return list(col.find({"datasourceId": datasource_id}).sort("code", 1))

    def _get_stat_rules_list(self, datasource_id: str) -> list[dict]:
        """Return enabled stat rules as plain dicts for the calculator."""
        col = Database.get_collection(STAT_RULES_COLLECTION)
        docs = list(col.find({"datasourceId": datasource_id, "enabled": True}))
        for doc in docs:
            doc.pop("_id", None)
        return docs

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _save_unmatched_items(
        self,
        datasource_id: str,
        patient_id: str,
        unmatched: list[dict],
        field_mappings: dict,
    ) -> None:
        """Save unmatched bedside records for later review."""
        col = Database.get_collection(UNMATCHED_COLLECTION)
        code_key = field_mappings.get("paramCode", "paramCode") if field_mappings else "paramCode"
        name_key = field_mappings.get("paramName", "paramName") if field_mappings else "paramName"
        time_key = field_mappings.get("recordTime", "recordTime") if field_mappings else "recordTime"
        strval_key = field_mappings.get("strVal", "strVal") if field_mappings else "strVal"
        id_key = field_mappings.get("_id", "_id") if field_mappings else "_id"

        for item in unmatched:
            unmatched_doc = IntakeOutputUnmatchedItem(
                datasourceId=datasource_id,
                patientId=patient_id,
                bedsideRecordId=str(item.get(id_key, "")),
                paramCode=item.get(code_key, ""),
                paramName=item.get(name_key, ""),
                strVal=item.get(strval_key, ""),
                time=item.get(time_key),
                status="pending",
            )
            col.insert_one(unmatched_doc.to_dict())

    def _save_log(
        self,
        datasource_id: str,
        patient_id: str,
        total_records: int,
        result_count: int,
        unmatched_count: int,
    ) -> None:
        """Save a calculation log entry."""
        col = Database.get_collection(LOGS_COLLECTION)
        log = {
            "_id": gen_object_id(),
            "datasourceId": datasource_id,
            "patientId": patient_id,
            "totalRecords": total_records,
            "resultCount": result_count,
            "unmatchedCount": unmatched_count,
            "createdAt": datetime.utcnow(),
        }
        col.insert_one(log)
