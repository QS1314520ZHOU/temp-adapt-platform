"""Sync task service - manage scheduled sync configurations and execution."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database import Database
from app.models.domain import SyncTaskConfig

logger = logging.getLogger(__name__)


class SyncService:
    """同步任务服务 - 管理定时同步配置和执行"""

    COLLECTION = "sync_task_configs"

    def get_config(self, vendor_code: str) -> Optional[dict]:
        """Return sync task config for a vendor, or None."""
        col = Database.get_collection(self.COLLECTION)
        return col.find_one({"vendorCode": vendor_code})

    def save_config(self, data: dict) -> dict:
        """Insert or update a sync task config (upsert by vendorCode)."""
        col = Database.get_collection(self.COLLECTION)
        now = datetime.now(timezone.utc)

        existing = col.find_one({"vendorCode": data["vendorCode"]})
        if existing:
            update_fields = {}
            for key in (
                "enabled", "syncType", "cronExpression", "lookbackDays",
                "syncWindowHours", "batchSize", "wardCodes",
                "datasourceId", "fullSyncHours", "incrementalIntervalMinutes",
                "callbackUrl",
            ):
                if key in data:
                    update_fields[key] = data[key]
            update_fields["updatedAt"] = now
            col.update_one({"vendorCode": data["vendorCode"]}, {"$set": update_fields})
            logger.info("Updated sync config for vendor '%s'", data["vendorCode"])
            return col.find_one({"vendorCode": data["vendorCode"]})
        else:
            config = SyncTaskConfig(
                vendorCode=data["vendorCode"],
                enabled=data.get("enabled", True),
                syncType=data.get("syncType", "pull"),
                cronExpression=data.get("cronExpression", "0 */5 * * *"),
                lookbackDays=data.get("lookbackDays", 1),
                syncWindowHours=data.get("syncWindowHours", 24),
                batchSize=data.get("batchSize", 100),
                wardCodes=data.get("wardCodes"),
                datasourceId=data.get("datasourceId"),
                fullSyncHours=data.get("fullSyncHours", [2, 4, 8]),
                incrementalIntervalMinutes=data.get("incrementalIntervalMinutes", 5),
                callbackUrl=data.get("callbackUrl"),
                createdAt=now,
                updatedAt=now,
            )
            doc = config.to_dict()
            col.insert_one(doc)
            logger.info("Created sync config for vendor '%s'", data["vendorCode"])
            return doc

    def list_configs(self, enabled_only: bool = False) -> list:
        """Return all sync task configs, optionally filtered to enabled only."""
        col = Database.get_collection(self.COLLECTION)
        query: dict = {}
        if enabled_only:
            query["enabled"] = True
        return list(col.find(query).sort("createdAt", -1))

    def execute_sync(self, vendor_code: str) -> dict:
        """Execute a sync task for a vendor.

        Steps:
            1. Load sync config
            2. Calculate sync time window:
               - If lastSyncTime exists, start from lastSyncTime
               - Otherwise start from now - lookbackDays
               - End at now
            3. Execute based on syncType:
               - pull: call PullService
               - db_view: call DbViewService
            4. Update lastSyncTime, lastSyncStatus, lastSyncCount
            5. Record errors
        """
        config = self.get_config(vendor_code)
        if not config:
            return {"success": False, "error": f"No sync config for vendor '{vendor_code}'"}

        if not config.get("enabled", True):
            return {"success": False, "error": f"Sync is disabled for vendor '{vendor_code}'"}

        col = Database.get_collection(self.COLLECTION)
        now = datetime.now(timezone.utc)

        # Calculate sync time window
        last_sync_time = config.get("lastSyncTime")
        lookback_days = config.get("lookbackDays", 1)

        if last_sync_time:
            sync_from = last_sync_time
        else:
            sync_from = now - timedelta(days=lookback_days)

        sync_to = now

        logger.info(
            "Executing sync for vendor '%s': from=%s to=%s, type=%s",
            vendor_code, sync_from, sync_to, config.get("syncType"),
        )

        sync_type = config.get("syncType", "pull")
        result = {}

        try:
            if sync_type == "pull":
                from app.services.pull_service import PullService
                pull_service = PullService()
                result = pull_service.pull_from_vendor(vendor_code)
            elif sync_type == "db_view":
                from app.services.db_view_service import DbViewService
                db_view_service = DbViewService()
                result = db_view_service.read_from_view(vendor_code)
            else:
                return {"success": False, "error": f"Unknown sync type: {sync_type}"}

            # Update sync status
            sync_count = 0
            if isinstance(result, dict):
                inner = result.get("result", result)
                if isinstance(inner, dict):
                    sync_count = inner.get("totalRecords", 0) or inner.get("rowCount", 0) or 0

            update_fields = {
                "lastSyncTime": now,
                "lastSyncStatus": "success" if result.get("success", False) else "failed",
                "lastSyncCount": sync_count,
                "lastError": None,
                "updatedAt": now,
            }
            col.update_one({"vendorCode": vendor_code}, {"$set": update_fields})

            logger.info(
                "Sync completed for vendor '%s': success=%s, count=%d",
                vendor_code, result.get("success", False), sync_count,
            )
            return {
                "success": result.get("success", False),
                "vendorCode": vendor_code,
                "syncCount": sync_count,
                "detail": result,
            }

        except Exception as e:
            logger.exception("Sync failed for vendor '%s'", vendor_code)

            # Update sync status with error
            col.update_one(
                {"vendorCode": vendor_code},
                {"$set": {
                    "lastSyncTime": now,
                    "lastSyncStatus": "failed",
                    "lastSyncCount": 0,
                    "lastError": str(e),
                    "updatedAt": now,
                }},
            )
            return {"success": False, "vendorCode": vendor_code, "error": str(e)}

    def execute_all_enabled(self) -> dict:
        """Execute sync tasks for all enabled configurations."""
        configs = self.list_configs(enabled_only=True)
        total = len(configs)
        success_count = 0
        fail_count = 0
        results = []

        for cfg in configs:
            vendor_code = cfg.get("vendorCode", "")
            result = self.execute_sync(vendor_code)
            results.append({"vendorCode": vendor_code, **result})
            if result.get("success"):
                success_count += 1
            else:
                fail_count += 1

        logger.info(
            "Batch sync complete: total=%d, success=%d, fail=%d",
            total, success_count, fail_count,
        )
        return {
            "total": total,
            "successCount": success_count,
            "failCount": fail_count,
            "results": results,
        }
