"""Callback service - manage temperature record data callback to target systems."""
import json
import logging
import time
from datetime import datetime
from typing import Optional

import httpx

from app.database import Database
from app.models.domain import CallbackConfig, CallbackLog, gen_object_id

logger = logging.getLogger(__name__)


class CallbackService:
    """回传服务 - 管理体温单数据回传到目标系统"""

    COLLECTION = "callback_configs"
    LOG_COLLECTION = "callback_logs"

    def get_config(self, vendor_code: str) -> Optional[dict]:
        """Return callback config for a vendor, or None."""
        col = Database.get_collection(self.COLLECTION)
        return col.find_one({"vendorCode": vendor_code})

    def save_config(self, data: dict) -> dict:
        """Insert or update a callback config (upsert by vendorCode)."""
        col = Database.get_collection(self.COLLECTION)
        now = datetime.utcnow()

        existing = col.find_one({"vendorCode": data["vendorCode"]})
        if existing:
            update_fields = {}
            for key in (
                "enabled", "callbackType", "callbackUrl", "callbackMethod",
                "callbackHeaders", "callbackFormat", "cronExpression",
                "delayMinutes", "includeItems", "excludeItems",
                "retryEnabled", "maxRetryCount", "retryIntervalSeconds",
                "dataTemplate",
            ):
                if key in data:
                    update_fields[key] = data[key]
            update_fields["updatedAt"] = now
            col.update_one({"vendorCode": data["vendorCode"]}, {"$set": update_fields})
            logger.info("Updated callback config for vendor '%s'", data["vendorCode"])
            return col.find_one({"vendorCode": data["vendorCode"]})
        else:
            config = CallbackConfig(
                vendorCode=data["vendorCode"],
                enabled=data.get("enabled", True),
                callbackType=data.get("callbackType", "realtime"),
                callbackUrl=data.get("callbackUrl"),
                callbackMethod=data.get("callbackMethod", "POST"),
                callbackHeaders=data.get("callbackHeaders", {}),
                callbackFormat=data.get("callbackFormat", "json"),
                cronExpression=data.get("cronExpression"),
                delayMinutes=data.get("delayMinutes", 0),
                includeItems=data.get("includeItems"),
                excludeItems=data.get("excludeItems"),
                retryEnabled=data.get("retryEnabled", True),
                maxRetryCount=data.get("maxRetryCount", 3),
                retryIntervalSeconds=data.get("retryIntervalSeconds", 60),
                dataTemplate=data.get("dataTemplate"),
                createdAt=now,
                updatedAt=now,
            )
            doc = config.to_dict()
            col.insert_one(doc)
            logger.info("Created callback config for vendor '%s'", data["vendorCode"])
            return doc

    def execute_callback(self, vendor_code: str, temperature_record: dict) -> dict:
        """Execute callback: send temperature record data to target system.

        Steps:
            1. Load callback config
            2. Check if enabled
            3. Filter includeItems / excludeItems
            4. Build request data (support dataTemplate substitution)
            5. Send HTTP request
            6. Record callback log
            7. On failure, retry if retryEnabled
        """
        config = self.get_config(vendor_code)
        if not config:
            return {"success": False, "error": f"No callback config for vendor '{vendor_code}'"}

        if not config.get("enabled", True):
            return {"success": False, "error": f"Callback is disabled for vendor '{vendor_code}'"}

        callback_url = config.get("callbackUrl")
        if not callback_url:
            return {"success": False, "error": "callbackUrl is not configured"}

        # Filter items
        record = self._filter_items(temperature_record, config)

        # Build request payload
        payload_str = self._build_request_data(record, config)

        # Send HTTP request
        log_id = None
        start_time = time.time()
        try:
            result = self._send_request(config, payload_str)
            duration = int((time.time() - start_time) * 1000)

            # Record success log
            log_id = self._save_log(
                vendor_code=vendor_code,
                temperature_record_id=temperature_record.get("_id", ""),
                callback_url=callback_url,
                callback_method=config.get("callbackMethod", "POST"),
                request_payload=payload_str,
                response_status=result["status_code"],
                response_body=result["body"],
                status="success",
                duration=duration,
            )
            return {"success": True, "logId": log_id, "statusCode": result["status_code"]}

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            logger.error("Callback failed for vendor '%s': %s", vendor_code, str(e))

            # Record failure log
            log_id = self._save_log(
                vendor_code=vendor_code,
                temperature_record_id=temperature_record.get("_id", ""),
                callback_url=callback_url,
                callback_method=config.get("callbackMethod", "POST"),
                request_payload=payload_str,
                status="failed",
                error=str(e),
                duration=duration,
            )

            # Retry if enabled
            if config.get("retryEnabled", True):
                self._schedule_retry(config, log_id, payload_str, temperature_record.get("_id", ""))

            return {"success": False, "logId": log_id, "error": str(e)}

    def batch_callback(self, vendor_code: str, record_ids: list) -> dict:
        """Execute callbacks for multiple temperature records."""
        col = Database.get_collection("temperature_records")
        total = len(record_ids)
        success_count = 0
        fail_count = 0
        results = []

        for record_id in record_ids:
            record = col.find_one({"_id": record_id})
            if not record:
                results.append({"recordId": record_id, "success": False, "error": "Record not found"})
                fail_count += 1
                continue

            result = self.execute_callback(vendor_code, record)
            results.append({"recordId": record_id, **result})
            if result.get("success"):
                success_count += 1
            else:
                fail_count += 1

        return {
            "total": total,
            "successCount": success_count,
            "failCount": fail_count,
            "results": results,
        }

    def get_logs(
        self,
        vendor_code: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Query callback logs with optional filters and pagination."""
        col = Database.get_collection(self.LOG_COLLECTION)
        query: dict = {}
        if vendor_code:
            query["vendorCode"] = vendor_code
        if status:
            query["status"] = status

        total = col.count_documents(query)
        skip = (page - 1) * page_size
        docs = list(col.find(query).sort("createdAt", -1).skip(skip).limit(page_size))
        return {"items": docs, "total": total, "page": page, "page_size": page_size}

    def retry_failed(self, log_id: str) -> dict:
        """Retry a failed callback by log ID."""
        log_col = Database.get_collection(self.LOG_COLLECTION)
        log_doc = log_col.find_one({"_id": log_id})
        if not log_doc:
            return {"success": False, "error": f"Callback log '{log_id}' not found"}

        if log_doc.get("status") != "failed":
            return {"success": False, "error": "Only failed callbacks can be retried"}

        vendor_code = log_doc.get("vendorCode", "")
        config = self.get_config(vendor_code)
        if not config:
            return {"success": False, "error": f"No callback config for vendor '{vendor_code}'"}

        payload_str = log_doc.get("requestPayload", "")
        temperature_record_id = log_doc.get("temperatureRecordId", "")

        start_time = time.time()
        try:
            result = self._send_request(config, payload_str)
            duration = int((time.time() - start_time) * 1000)

            # Update the log entry with success
            retry_count = log_doc.get("retryCount", 0) + 1
            log_col.update_one(
                {"_id": log_id},
                {"$set": {
                    "status": "success",
                    "responseStatus": result["status_code"],
                    "responseBody": result["body"],
                    "retryCount": retry_count,
                    "error": None,
                    "duration": duration,
                    "updatedAt": datetime.utcnow(),
                }},
            )
            return {"success": True, "logId": log_id, "statusCode": result["status_code"]}

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            retry_count = log_doc.get("retryCount", 0) + 1
            log_col.update_one(
                {"_id": log_id},
                {"$set": {
                    "status": "failed",
                    "retryCount": retry_count,
                    "error": str(e),
                    "duration": duration,
                    "updatedAt": datetime.utcnow(),
                }},
            )
            return {"success": False, "logId": log_id, "error": str(e)}

    def _build_request_data(self, record: dict, config: dict) -> str:
        """Build callback request data based on config.

        If dataTemplate is configured, use template substitution.
        Otherwise serialize the record as JSON.
        """
        template = config.get("dataTemplate")
        if template:
            # Template substitution: replace {{fieldName}} placeholders
            result = template
            for key, value in record.items():
                placeholder = "{{" + key + "}}"
                if placeholder in result:
                    if isinstance(value, (dict, list)):
                        result = result.replace(placeholder, json.dumps(value, default=str))
                    else:
                        result = result.replace(placeholder, str(value) if value is not None else "")
            return result
        else:
            return json.dumps(record, default=str, ensure_ascii=False)

    def _filter_items(self, record: dict, config: dict) -> dict:
        """Filter record items based on includeItems / excludeItems config."""
        include_items = config.get("includeItems")
        exclude_items = config.get("excludeItems")

        if not include_items and not exclude_items:
            return record

        items = record.get("items", [])
        if not items:
            return record

        filtered = items
        if include_items:
            include_set = set(include_items)
            filtered = [item for item in filtered if item.get("code") in include_set]
        if exclude_items:
            exclude_set = set(exclude_items)
            filtered = [item for item in filtered if item.get("code") not in exclude_set]

        result = dict(record)
        result["items"] = filtered
        return result

    def _send_request(self, config: dict, payload: str) -> dict:
        """Send HTTP request to the callback URL.

        Returns:
            {"status_code": int, "body": str}
        Raises:
            httpx.HTTPError on request failure.
        """
        url = config.get("callbackUrl", "")
        method = config.get("callbackMethod", "POST").upper()
        headers = config.get("callbackHeaders", {})
        callback_format = config.get("callbackFormat", "json")

        if callback_format == "json" and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        with httpx.Client(timeout=60) as client:
            if method == "GET":
                resp = client.get(url, headers=headers)
            elif method == "PUT":
                resp = client.put(url, headers=headers, content=payload)
            elif method == "PATCH":
                resp = client.patch(url, headers=headers, content=payload)
            else:
                resp = client.post(url, headers=headers, content=payload)

        resp.raise_for_status()
        return {"status_code": resp.status_code, "body": resp.text}

    def _save_log(
        self,
        vendor_code: str,
        temperature_record_id: str,
        callback_url: str,
        callback_method: str,
        request_payload: str,
        status: str,
        response_status: Optional[int] = None,
        response_body: Optional[str] = None,
        error: Optional[str] = None,
        duration: Optional[int] = None,
    ) -> str:
        """Save a callback log entry and return its ID."""
        col = Database.get_collection(self.LOG_COLLECTION)
        log = CallbackLog(
            vendorCode=vendor_code,
            temperatureRecordId=temperature_record_id,
            callbackUrl=callback_url,
            callbackMethod=callback_method,
            requestPayload=request_payload,
            responseStatus=response_status,
            responseBody=response_body,
            status=status,
            retryCount=0,
            error=error,
            duration=duration,
        )
        doc = log.to_dict()
        col.insert_one(doc)
        return log.id

    def _schedule_retry(
        self,
        config: dict,
        log_id: str,
        payload: str,
        temperature_record_id: str,
    ) -> None:
        """Schedule a retry for a failed callback.

        For simplicity, this performs a synchronous retry with backoff.
        In production, this could delegate to a background task queue.
        """
        max_retries = config.get("maxRetryCount", 3)
        retry_interval = config.get("retryIntervalSeconds", 60)
        vendor_code = config.get("vendorCode", "")

        log_col = Database.get_collection(self.LOG_COLLECTION)

        for attempt in range(1, max_retries + 1):
            logger.info(
                "Retrying callback for vendor '%s', attempt %d/%d",
                vendor_code, attempt, max_retries,
            )
            time.sleep(min(retry_interval, 5))  # Cap sleep for synchronous retry

            try:
                result = self._send_request(config, payload)
                log_col.update_one(
                    {"_id": log_id},
                    {"$set": {
                        "status": "success",
                        "responseStatus": result["status_code"],
                        "responseBody": result["body"],
                        "retryCount": attempt,
                        "error": None,
                    }},
                )
                logger.info("Retry succeeded for log '%s' on attempt %d", log_id, attempt)
                return
            except Exception as e:
                logger.warning("Retry attempt %d failed for log '%s': %s", attempt, log_id, str(e))
                log_col.update_one(
                    {"_id": log_id},
                    {"$set": {
                        "retryCount": attempt,
                        "error": str(e),
                    }},
                )

        logger.error("All %d retries exhausted for log '%s'", max_retries, log_id)

    def delete_config(self, vendor_code: str) -> bool:
        """Delete callback config for a vendor."""
        col = Database.get_collection(self.COLLECTION)
        result = col.delete_one({"vendorCode": vendor_code})
        if result.deleted_count == 0:
            raise ValueError(f"回传配置 '{vendor_code}' 不存在")
        logger.info("Deleted callback config for vendor '%s'", vendor_code)
        return True
