"""Access configuration management service."""
import logging
from datetime import datetime
from typing import Optional

import httpx

from app.database import Database
from app.engine.sql_extractor import SqlExtractor
from app.models.domain import AccessConfig

logger = logging.getLogger(__name__)

COLLECTION = "access_configs"


class AccessConfigService:
    """Manage vendor access configurations (HTTP push/pull, DB view)."""

    def get_config(self, vendor_code: str) -> Optional[dict]:
        """Return the access config for a vendor, or None."""
        col = Database.get_collection(COLLECTION)
        return col.find_one({"vendorCode": vendor_code})

    def save_config(self, data: dict) -> dict:
        """Insert or upsert an access config and return the saved document."""
        col = Database.get_collection(COLLECTION)
        now = datetime.utcnow()

        existing = col.find_one({"vendorCode": data["vendorCode"]})

        if existing:
            update_fields: dict = {
                "accessType": data["accessType"],
                "httpPushConfig": data.get("httpPushConfig"),
                "httpPullConfig": data.get("httpPullConfig"),
                "dbViewConfig": data.get("dbViewConfig"),
                "enabled": data.get("enabled", True),
                "updatedAt": now,
            }
            col.update_one({"vendorCode": data["vendorCode"]}, {"$set": update_fields})
            logger.info("Updated access config for vendor '%s'", data["vendorCode"])
        else:
            config = AccessConfig(
                vendorCode=data["vendorCode"],
                accessType=data["accessType"],
                httpPushConfig=data.get("httpPushConfig"),
                httpPullConfig=data.get("httpPullConfig"),
                dbViewConfig=data.get("dbViewConfig"),
                enabled=data.get("enabled", True),
                createdAt=now,
                updatedAt=now,
            )
            doc = config.to_dict()
            col.insert_one(doc)
            logger.info("Created access config for vendor '%s'", data["vendorCode"])

        return col.find_one({"vendorCode": data["vendorCode"]})

    def test_http_connection(self, config: dict) -> dict:
        """Test an HTTP connection using the provided config.

        Args:
            config: Dict with keys ``url``, ``method``, ``headers``, ``body``, ``timeout``.

        Returns:
            {"success": bool, "message": str, "sample_data": str}
        """
        url = config.get("url", "")
        method = config.get("method", "GET").upper()
        headers = config.get("headers") or {}
        body = config.get("body")
        timeout = config.get("timeout", 30)

        try:
            with httpx.Client(timeout=timeout) as client:
                if method == "POST":
                    resp = client.post(url, headers=headers, content=body)
                else:
                    resp = client.get(url, headers=headers)

            resp.raise_for_status()
            sample = resp.text[:2000] if resp.text else ""
            return {
                "success": True,
                "message": f"HTTP {resp.status_code} OK ({len(resp.text)} bytes)",
                "sample_data": sample,
            }
        except httpx.TimeoutException:
            return {"success": False, "message": f"Connection timed out after {timeout}s", "sample_data": ""}
        except httpx.HTTPStatusError as e:
            return {"success": False, "message": f"HTTP {e.response.status_code}: {e.response.text[:500]}", "sample_data": ""}
        except Exception as e:
            logger.exception("HTTP connection test failed")
            return {"success": False, "message": str(e), "sample_data": ""}

    def test_db_connection(self, config: dict) -> dict:
        """Test a database connection using the provided config.

        Args:
            config: Dict with keys ``connectionString``, ``dbType``, ``testSql``.

        Returns:
            {"success": bool, "message": str, "sample_data": str}
        """
        connection_string = config.get("connectionString", "")
        db_type = config.get("dbType", "mysql")
        test_sql = config.get("testSql", "SELECT 1")

        extractor = SqlExtractor(connection_string, db_type)
        try:
            ok = extractor.test_connection()
            if not ok:
                return {"success": False, "message": "Connection test returned False", "sample_data": ""}

            rows = extractor.execute_query(test_sql)
            sample = str(rows[:5]) if rows else "[]"
            return {
                "success": True,
                "message": f"Connected successfully, test query returned {len(rows)} rows",
                "sample_data": sample,
            }
        except Exception as e:
            logger.exception("DB connection test failed")
            return {"success": False, "message": str(e), "sample_data": ""}
        finally:
            extractor.close()

    def preview_data(self, vendor_code: str) -> dict:
        """Fetch sample data from the configured source for a vendor.

        Returns:
            {"success": bool, "data": str, "message": str}
        """
        config = self.get_config(vendor_code)
        if not config:
            return {"success": False, "data": "", "message": f"No access config for vendor '{vendor_code}'"}

        access_type = config.get("accessType", "")

        if access_type == "http_pull":
            pull_cfg = config.get("httpPullConfig") or {}
            result = self.test_http_connection(pull_cfg)
            return {"success": result["success"], "data": result.get("sample_data", ""), "message": result["message"]}

        if access_type == "db_view":
            db_cfg = config.get("dbViewConfig") or {}
            result = self.test_db_connection(db_cfg)
            return {"success": result["success"], "data": result.get("sample_data", ""), "message": result["message"]}

        if access_type == "http_push":
            # No live preview for push mode; return the most recent raw record
            raw_col = Database.get_collection("raw_records")
            doc = raw_col.find_one(
                {"vendorCode": vendor_code},
                sort=[("createdAt", -1)],
            )
            if doc:
                return {"success": True, "data": doc.get("rawContent", ""), "message": "Using latest pushed raw record"}
            return {"success": False, "data": "", "message": "No raw records found for this vendor"}

        return {"success": False, "data": "", "message": f"Unknown access type '{access_type}'"}

    def delete_config(self, vendor_code: str) -> bool:
        """Delete the access config for a vendor."""
        col = Database.get_collection(COLLECTION)
        result = col.delete_one({"vendorCode": vendor_code})
        if result.deleted_count == 0:
            raise ValueError(f"接入配置 '{vendor_code}' 不存在")
        logger.info("Deleted access config for vendor '%s'", vendor_code)
        return True
