"""Retry service for re-processing failed transform records."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database import Database
from app.models.domain import RetryTask, gen_object_id

logger = logging.getLogger(__name__)

RETRY_TASKS_COLLECTION = "retry_tasks"
RAW_RECORDS_COLLECTION = "raw_records"


class RetryService:
    """Manage retry tasks for failed raw record transformations."""

    def create_retry_task(self, raw_record_id: str, vendor_code: str, error: str) -> str:
        """Create a new retry task for a failed raw record.

        Args:
            raw_record_id: The ID of the failed raw record.
            vendor_code: The vendor code.
            error: The error message from the failed attempt.

        Returns:
            The retry task ID.
        """
        col = Database.get_collection(RETRY_TASKS_COLLECTION)

        # Check if a pending task already exists for this raw record
        existing = col.find_one({
            "rawRecordId": raw_record_id,
            "status": {"$in": ["pending", "running"]},
        })
        if existing:
            logger.info("Retry task already exists for raw record '%s'", raw_record_id)
            return str(existing["_id"])

        task = RetryTask(
            rawRecordId=raw_record_id,
            vendorCode=vendor_code,
            retryCount=0,
            maxRetryCount=5,
            status="pending",
            lastError=error,
            nextRetryTime=datetime.now(timezone.utc),
        )
        doc = task.to_dict()
        col.insert_one(doc)
        logger.info("Created retry task '%s' for raw record '%s'", task.id, raw_record_id)
        return task.id

    def retry(self, task_id: str) -> dict:
        """Execute a retry for a specific task.

        Args:
            task_id: The retry task ID.

        Returns:
            {"success": bool, "taskId": str, "error": str}
        """
        tasks_col = Database.get_collection(RETRY_TASKS_COLLECTION)
        task_doc = tasks_col.find_one({"_id": task_id})
        if not task_doc:
            return {"success": False, "taskId": task_id, "error": "Retry task not found"}

        task = RetryTask.from_dict(task_doc)

        if task.status not in ("pending", "failed"):
            return {"success": False, "taskId": task_id, "error": f"Task status is '{task.status}', cannot retry"}

        if task.retryCount >= task.maxRetryCount:
            tasks_col.update_one(
                {"_id": task_id},
                {"$set": {"status": "exhausted", "updatedAt": datetime.now(timezone.utc)}},
            )
            return {"success": False, "taskId": task_id, "error": "Max retry count reached"}

        # Mark as running
        tasks_col.update_one(
            {"_id": task_id},
            {"$set": {"status": "running", "updatedAt": datetime.now(timezone.utc)}},
        )

        try:
            result = self.retry_raw_record(task.rawRecordId)

            if result.get("success"):
                tasks_col.update_one(
                    {"_id": task_id},
                    {"$set": {
                        "status": "success",
                        "retryCount": task.retryCount + 1,
                        "updatedAt": datetime.now(timezone.utc),
                    }},
                )
                return {"success": True, "taskId": task_id}
            else:
                new_count = task.retryCount + 1
                next_retry = datetime.now(timezone.utc) + timedelta(minutes=min(2 ** new_count, 60))
                tasks_col.update_one(
                    {"_id": task_id},
                    {"$set": {
                        "status": "failed",
                        "retryCount": new_count,
                        "lastError": result.get("error", "Unknown error"),
                        "nextRetryTime": next_retry,
                        "updatedAt": datetime.now(timezone.utc),
                    }},
                )
                return {"success": False, "taskId": task_id, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.exception("Retry failed for task '%s'", task_id)
            tasks_col.update_one(
                {"_id": task_id},
                {"$set": {
                    "status": "failed",
                    "retryCount": task.retryCount + 1,
                    "lastError": str(e),
                    "updatedAt": datetime.now(timezone.utc),
                }},
            )
            return {"success": False, "taskId": task_id, "error": str(e)}

    def retry_raw_record(self, raw_record_id: str) -> dict:
        """Re-transform a single raw record by its ID.

        Delegates to TransformService.transform_single.

        Returns:
            Transform result dict.
        """
        from app.services.transform_service import TransformService

        raw_col = Database.get_collection(RAW_RECORDS_COLLECTION)
        raw_doc = raw_col.find_one({"_id": raw_record_id})
        if not raw_doc:
            return {"success": False, "error": f"Raw record '{raw_record_id}' not found"}

        transform_service = TransformService()
        return transform_service.transform_single(raw_record_id)

    def batch_retry(self, record_ids: list) -> dict:
        """Retry multiple raw records in batch.

        Args:
            record_ids: List of raw record IDs or retry task IDs.

        Returns:
            {"total": int, "success": int, "fail": int, "results": list}
        """
        results: list[dict] = []
        success_count = 0
        fail_count = 0

        for record_id in record_ids:
            result = self.retry_raw_record(record_id)
            results.append({"rawRecordId": record_id, **result})
            if result.get("success"):
                success_count += 1
            else:
                fail_count += 1

        return {
            "total": len(record_ids),
            "success": success_count,
            "fail": fail_count,
            "results": results,
        }

    def get_pending_tasks(self, limit: int = 50) -> list:
        """Return pending retry tasks ordered by nextRetryTime.

        Args:
            limit: Maximum number of tasks to return.

        Returns:
            List of retry task documents.
        """
        col = Database.get_collection(RETRY_TASKS_COLLECTION)
        return list(
            col.find({"status": "pending"})
            .sort("nextRetryTime", 1)
            .limit(limit)
        )

    def process_pending_retries(self) -> dict:
        """Auto-retry all pending tasks whose nextRetryTime has passed.

        Returns:
            {"processed": int, "success": int, "fail": int}
        """
        tasks = self.get_pending_tasks(limit=100)
        now = datetime.now(timezone.utc)

        success_count = 0
        fail_count = 0
        processed = 0

        for task_doc in tasks:
            next_retry = task_doc.get("nextRetryTime")
            if next_retry and next_retry > now:
                continue  # Not ready yet

            processed += 1
            task_id = str(task_doc.get("_id", ""))
            result = self.retry(task_id)
            if result.get("success"):
                success_count += 1
            else:
                fail_count += 1

        logger.info("Processed %d pending retries: %d success, %d fail", processed, success_count, fail_count)
        return {"processed": processed, "success": success_count, "fail": fail_count}
