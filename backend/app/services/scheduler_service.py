"""Scheduled task scheduler service using APScheduler."""
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import Database

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._started = False

    def start(self):
        """Start the scheduler and load all configured jobs."""
        if not self._started:
            self.scheduler.start()
            self._started = True
            logger.info("Scheduler started")
            self._load_sync_tasks()
            self._load_callback_tasks()

    def stop(self):
        """Stop the scheduler."""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            logger.info("Scheduler stopped")

    def _load_sync_tasks(self):
        """Load all enabled sync task configs from database and register cron jobs."""
        col = Database.get_collection("sync_task_configs")
        configs = list(col.find({"enabled": True}))

        for config in configs:
            vendor_code = config.get("vendorCode", "")
            sync_type = config.get("syncType", "pull")

            if sync_type == "bedside_sync":
                self._load_bedside_sync_job(config)
                continue

            cron_expr = config.get("cronExpression")
            if not cron_expr:
                continue
            try:
                self.add_sync_job(vendor_code, cron_expr)
                logger.info("Loaded sync job for vendor '%s': %s", vendor_code, cron_expr)
            except Exception as e:
                logger.error("Failed to load sync job for vendor '%s': %s", vendor_code, str(e))

    def _load_callback_tasks(self):
        """Load all scheduled callback configs from database and register cron jobs."""
        col = Database.get_collection("callback_configs")
        configs = list(col.find({
            "callbackType": "scheduled",
            "enabled": True,
        }))

        for config in configs:
            vendor_code = config.get("vendorCode", "")
            cron_expr = config.get("cronExpression")
            if not cron_expr:
                continue
            try:
                self.add_callback_job(vendor_code, cron_expr)
                logger.info("Loaded callback job for vendor '%s': %s", vendor_code, cron_expr)
            except Exception as e:
                logger.error("Failed to load callback job for vendor '%s': %s", vendor_code, str(e))

    def _load_bedside_sync_job(self, config: dict):
        """Load a bedside_sync config and register two cron jobs:
        1. Full sync at specific hours (e.g. 2am, 4am, 8am UTC+8)
        2. Incremental check every N minutes
        """
        vendor_code = config.get("vendorCode", "")
        datasource_id = config.get("datasourceId", "")
        full_sync_hours = config.get("fullSyncHours", [2, 4, 8])
        interval_minutes = config.get("incrementalIntervalMinutes", 5)
        lookback_days = config.get("lookbackDays", 7)
        callback_url = config.get("callbackUrl")
        ward_codes = config.get("wardCodes", [])

        if not datasource_id:
            logger.warning("Bedside sync for vendor '%s' has no datasourceId, skipping", vendor_code)
            return

        # 1. Full sync job: at specific hours, minute 0
        hours_str = ",".join(str(h) for h in full_sync_hours)
        full_cron = f"0 {hours_str} * * *"
        full_job_id = f"bedside_full_{vendor_code}"
        self.scheduler.add_job(
            self._run_bedside_full_sync,
            CronTrigger.from_crontab(full_cron),
            args=[vendor_code, datasource_id, lookback_days, callback_url, ward_codes],
            id=full_job_id,
            replace_existing=True,
        )
        logger.info("Loaded bedside full sync job '%s': hours=%s, lookback=%dd", full_job_id, full_sync_hours, lookback_days)

        # 2. Incremental check job: every N minutes
        incr_cron = f"*/{interval_minutes} * * * *"
        incr_job_id = f"bedside_incr_{vendor_code}"
        self.scheduler.add_job(
            self._run_bedside_incr_sync,
            CronTrigger.from_crontab(incr_cron),
            args=[vendor_code, datasource_id, callback_url, ward_codes],
            id=incr_job_id,
            replace_existing=True,
        )
        logger.info("Loaded bedside incremental sync job '%s': every %d min", incr_job_id, interval_minutes)

    def add_sync_job(self, vendor_code: str, cron_expression: str):
        """Add or update a sync cron job for a vendor."""
        job_id = f"sync_{vendor_code}"
        self.scheduler.add_job(
            self._run_sync,
            CronTrigger.from_crontab(cron_expression),
            args=[vendor_code],
            id=job_id,
            replace_existing=True,
        )
        logger.info("Added sync job '%s' with cron: %s", job_id, cron_expression)

    def add_callback_job(self, vendor_code: str, cron_expression: str):
        """Add or update a callback cron job for a vendor."""
        job_id = f"callback_{vendor_code}"
        self.scheduler.add_job(
            self._run_callback,
            CronTrigger.from_crontab(cron_expression),
            args=[vendor_code],
            id=job_id,
            replace_existing=True,
        )
        logger.info("Added callback job '%s' with cron: %s", job_id, cron_expression)

    def remove_job(self, job_id: str):
        """Remove a scheduled job by ID."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info("Removed job '%s'", job_id)
        except Exception:
            logger.debug("Job '%s' not found or already removed", job_id)

    def get_jobs(self) -> list:
        """Return a list of all scheduled jobs with their metadata."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs

    def refresh_jobs(self):
        """Refresh all scheduled jobs by removing existing ones and reloading from database."""
        # Remove all existing jobs
        for job in self.scheduler.get_jobs():
            self.scheduler.remove_job(job.id)

        logger.info("Refreshing all scheduled jobs")
        self._load_sync_tasks()
        self._load_callback_tasks()

    def _run_sync(self, vendor_code: str):
        """Execute a sync task (called by the scheduler)."""
        from app.services.sync_service import SyncService
        sync_service = SyncService()
        try:
            result = sync_service.execute_sync(vendor_code)
            logger.info("Scheduled sync for vendor '%s': success=%s", vendor_code, result.get("success"))
        except Exception as e:
            logger.exception("Scheduled sync failed for vendor '%s': %s", vendor_code, str(e))

    def _run_bedside_full_sync(self, vendor_code: str, datasource_id: str,
                                lookback_days: int, callback_url: str, ward_codes: list):
        """Execute bedside full sync at scheduled hours."""
        from app.services.bedside_sync_service import bedside_sync_service
        try:
            result = bedside_sync_service.full_sync(
                vendor_code=vendor_code,
                datasource_id=datasource_id,
                lookback_days=lookback_days,
                callback_url=callback_url,
                ward_codes=ward_codes or None,
            )
            logger.info("Bedside full sync vendor='%s': %s", vendor_code, result)
        except Exception as e:
            logger.exception("Bedside full sync failed for vendor '%s': %s", vendor_code, str(e))

    def _run_bedside_incr_sync(self, vendor_code: str, datasource_id: str,
                                callback_url: str, ward_codes: list):
        """Execute bedside incremental check."""
        from app.services.bedside_sync_service import bedside_sync_service
        try:
            result = bedside_sync_service.incremental_sync(
                vendor_code=vendor_code,
                datasource_id=datasource_id,
                callback_url=callback_url,
                ward_codes=ward_codes or None,
            )
            if result.get("recordCount", 0) > 0:
                logger.info("Bedside incr sync vendor='%s': %d updates", vendor_code, result["recordCount"])
        except Exception as e:
            logger.exception("Bedside incr sync failed for vendor '%s': %s", vendor_code, str(e))

    def _run_callback(self, vendor_code: str):
        """Execute a callback task (called by the scheduler).

        Queries recent successfully transformed records that haven't been
        sent via callback yet, then calls batch_callback.
        """
        from app.services.callback_service import CallbackService
        callback_service = CallbackService()
        try:
            # Query recent transformed records for this vendor
            temp_col = Database.get_collection("temperature_records")
            log_col = Database.get_collection("callback_logs")

            # Find records with status=transformed
            records = list(temp_col.find({
                "vendorCode": vendor_code,
                "status": "transformed",
            }).limit(100))

            if not records:
                logger.debug("No pending records for callback vendor '%s'", vendor_code)
                return

            # Filter out records that have already been successfully sent
            record_ids = []
            for rec in records:
                rec_id = rec.get("_id", "")
                existing_success = log_col.find_one({
                    "temperatureRecordId": rec_id,
                    "status": "success",
                })
                if not existing_success:
                    record_ids.append(rec_id)

            if not record_ids:
                logger.debug("All records already sent for callback vendor '%s'", vendor_code)
                return

            result = callback_service.batch_callback(vendor_code, record_ids)
            logger.info(
                "Scheduled callback for vendor '%s': total=%d, success=%d, fail=%d",
                vendor_code,
                result.get("total", 0),
                result.get("successCount", 0),
                result.get("failCount", 0),
            )
        except Exception as e:
            logger.exception("Scheduled callback failed for vendor '%s': %s", vendor_code, str(e))


# Singleton instance
scheduler_service = SchedulerService()
