"""Bedside sync service — incremental sync based on editTime.

Sync strategy:
- **Full sync** at configured hours (e.g. 2am, 4am, 8am UTC+8): pull all
  bedside data for that time window.
- **Incremental check** every N minutes: query records whose editTime >=
  last checkpoint, push any updates.
- **Lookback window** (default 7 days): on startup or full sync, scan for
  records modified in the last N days to catch late edits.

All bedside ``time`` values are in UTC+8 (Asia/Shanghai).
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database import Database

logger = logging.getLogger(__name__)

# UTC+8 timezone
TZ_CN = timezone(timedelta(hours=8))

SYNC_STATE_COLLECTION = "bedside_sync_state"


def _now_cn() -> datetime:
    """Current time in UTC+8."""
    return datetime.now(TZ_CN)


def _today_cn() -> datetime:
    """Start of today in UTC+8."""
    now = _now_cn()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


class BedsideSyncService:
    """Manage incremental bedside data sync from SmartCare.

    Sync state is persisted per-vendor in ``bedside_sync_state`` collection:
    {
        vendorCode: str,
        datasourceId: str,
        lastSyncTime: datetime,       # last successful sync checkpoint
        lastFullSyncTime: datetime,   # last full sync timestamp
        syncCount: int,
        lastError: str | null,
    }
    """

    def get_sync_state(self, vendor_code: str) -> Optional[dict]:
        col = Database.get_collection(SYNC_STATE_COLLECTION)
        return col.find_one({"vendorCode": vendor_code})

    def save_sync_state(self, vendor_code: str, update: dict):
        col = Database.get_collection(SYNC_STATE_COLLECTION)
        existing = col.find_one({"vendorCode": vendor_code})
        if existing:
            col.update_one({"vendorCode": vendor_code}, {"$set": update})
        else:
            col.insert_one({"vendorCode": vendor_code, **update})

    # ------------------------------------------------------------------
    # Full sync — at specific hours (e.g. 2am, 4am, 8am)
    # ------------------------------------------------------------------

    def full_sync(
        self,
        vendor_code: str,
        datasource_id: str,
        lookback_days: int = 7,
        callback_url: Optional[str] = None,
        ward_codes: Optional[list] = None,
    ) -> dict:
        """Full sync: pull all bedside data modified in the lookback window.

        Called at scheduled time points (e.g. 2:00, 4:00, 8:00 UTC+8).

        Steps:
        1. Determine time window: now - lookback_days to now
        2. Query SmartCare bedside for records with editTime in window
        3. Transform and push to target (via callback or direct HTTP)
        4. Update sync checkpoint
        """
        from app.services.smartcare_service import SmartCareService
        sc_service = SmartCareService()

        now_cn = _now_cn()
        lookback_start = now_cn - timedelta(days=lookback_days)

        logger.info(
            "[BedsideSync] Full sync vendor='%s': lookback %s → %s (UTC+8)",
            vendor_code, lookback_start.isoformat(), now_cn.isoformat(),
        )

        try:
            records = sc_service.get_bedside_modified(
                datasource_id=datasource_id,
                since=lookback_start,
                ward_codes=ward_codes,
                limit=10000,
            )

            logger.info(
                "[BedsideSync] Full sync vendor='%s': found %d modified records",
                vendor_code, len(records),
            )

            # Push records to target
            push_result = self._push_records(vendor_code, records, callback_url)

            # Update state
            self.save_sync_state(vendor_code, {
                "datasourceId": datasource_id,
                "lastSyncTime": now_cn,
                "lastFullSyncTime": now_cn,
                "lastError": None,
                "$inc": {"syncCount": 1},
            })

            return {
                "success": True,
                "syncType": "full",
                "recordCount": len(records),
                "pushResult": push_result,
                "syncTime": now_cn.isoformat(),
            }

        except Exception as e:
            logger.exception("[BedsideSync] Full sync failed for vendor '%s'", vendor_code)
            self.save_sync_state(vendor_code, {
                "lastError": str(e),
            })
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Incremental check — every N minutes
    # ------------------------------------------------------------------

    def incremental_sync(
        self,
        vendor_code: str,
        datasource_id: str,
        callback_url: Optional[str] = None,
        ward_codes: Optional[list] = None,
    ) -> dict:
        """Incremental sync: check for records modified since last checkpoint.

        Called every 5 minutes (or configured interval).

        Steps:
        1. Read lastSyncTime from state
        2. Query bedside where editTime >= lastSyncTime
        3. If any found, transform and push
        4. Update checkpoint to now
        """
        from app.services.smartcare_service import SmartCareService
        sc_service = SmartCareService()

        state = self.get_sync_state(vendor_code)
        last_sync = state.get("lastSyncTime") if state else None

        # First run: default to 7 days ago
        if not last_sync:
            last_sync = _now_cn() - timedelta(days=7)
            logger.info(
                "[BedsideSync] No previous sync state for vendor '%s', defaulting to %s",
                vendor_code, last_sync.isoformat(),
            )

        now_cn = _now_cn()

        logger.info(
            "[BedsideSync] Incremental check vendor='%s': editTime >= %s",
            vendor_code, last_sync.isoformat(),
        )

        try:
            records = sc_service.get_bedside_modified(
                datasource_id=datasource_id,
                since=last_sync,
                ward_codes=ward_codes,
                limit=5000,
            )

            if not records:
                logger.info("[BedsideSync] No updates for vendor '%s'", vendor_code)
                self.save_sync_state(vendor_code, {
                    "lastSyncTime": now_cn,
                    "lastError": None,
                })
                return {"success": True, "syncType": "incremental", "recordCount": 0}

            logger.info(
                "[BedsideSync] Found %d updated records for vendor '%s'",
                len(records), vendor_code,
            )

            push_result = self._push_records(vendor_code, records, callback_url)

            self.save_sync_state(vendor_code, {
                "datasourceId": datasource_id,
                "lastSyncTime": now_cn,
                "lastError": None,
                "$inc": {"syncCount": 1},
            })

            return {
                "success": True,
                "syncType": "incremental",
                "recordCount": len(records),
                "pushResult": push_result,
                "syncTime": now_cn.isoformat(),
            }

        except Exception as e:
            logger.exception("[BedsideSync] Incremental sync failed for vendor '%s'", vendor_code)
            self.save_sync_state(vendor_code, {"lastError": str(e)})
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Push records to target
    # ------------------------------------------------------------------

    def _push_records(self, vendor_code: str, records: list, callback_url: Optional[str] = None) -> dict:
        """Push bedside records to the target system.

        Uses the callback service if configured, otherwise direct HTTP.
        """
        if not records:
            return {"sent": 0}

        if callback_url:
            return self._push_via_http(callback_url, records)

        # Try callback service
        try:
            from app.services.callback_service import CallbackService
            cb_service = CallbackService()
            config = cb_service.get_config(vendor_code)
            if config and config.get("callbackUrl"):
                # Push as a batch
                payload = {
                    "vendorCode": vendor_code,
                    "syncType": "bedside",
                    "recordCount": len(records),
                    "records": records,
                    "syncTime": _now_cn().isoformat(),
                }
                import json
                result = cb_service._send_request(config, json.dumps(payload, default=str, ensure_ascii=False))
                return {"sent": len(records), "statusCode": result.get("status_code")}
        except Exception as e:
            logger.warning("[BedsideSync] Callback push failed: %s", e)

        return {"sent": len(records), "method": "no_target"}

    @staticmethod
    def _push_via_http(url: str, records: list) -> dict:
        """Direct HTTP push to target URL."""
        import httpx
        import json

        payload = {
            "syncType": "bedside",
            "recordCount": len(records),
            "records": records,
            "syncTime": _now_cn().isoformat(),
        }

        with httpx.Client(timeout=60) as client:
            resp = client.post(
                url,
                content=json.dumps(payload, default=str, ensure_ascii=False),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return {"sent": len(records), "statusCode": resp.status_code, "body": resp.text[:500]}


# Singleton
bedside_sync_service = BedsideSyncService()
