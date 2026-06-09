"""Database view reading service."""
import logging
from typing import Optional

from app.database import Database
from app.engine.sql_extractor import SqlExtractor
from app.services.transform_service import TransformService

logger = logging.getLogger(__name__)


class DbViewService:
    """Read data from vendor database views and trigger transformation."""

    def __init__(self) -> None:
        self._transform_service = TransformService()

    def read_from_view(self, vendor_code: str) -> dict:
        """Read data from a vendor's configured database view.

        Steps:
            1. Load vendor access config (dbViewConfig)
            2. Execute the SQL query
            3. Serialize results and call transform_and_save

        Returns:
            {"success": bool, "vendorCode": str, "rowCount": int,
             "result": dict, "error": str}
        """
        access_col = Database.get_collection("access_configs")
        access_config = access_col.find_one({"vendorCode": vendor_code})
        if not access_config:
            return {"success": False, "vendorCode": vendor_code,
                    "error": f"No access config for vendor '{vendor_code}'", "rowCount": 0}

        if access_config.get("accessType") != "db_view":
            return {"success": False, "vendorCode": vendor_code,
                    "error": "Vendor access type is not db_view", "rowCount": 0}

        db_cfg = access_config.get("dbViewConfig") or {}

        try:
            rows = self._execute_query(db_cfg)
        except Exception as e:
            logger.exception("DB view query failed for vendor '%s'", vendor_code)
            return {"success": False, "vendorCode": vendor_code, "error": str(e), "rowCount": 0}

        if not rows:
            return {"success": True, "vendorCode": vendor_code, "rowCount": 0,
                    "result": {"success": True, "totalRecords": 0, "message": "No data returned from view"}}

        # Serialize rows to JSON string for the transform engine
        import json
        raw_data = json.dumps(rows, default=str)

        result = self._transform_service.transform_and_save(
            vendor_code=vendor_code,
            raw_data=raw_data,
            access_type="db_view",
        )

        return {
            "success": result.get("success", False),
            "vendorCode": vendor_code,
            "rowCount": len(rows),
            "result": result,
        }

    def _execute_query(self, config: dict) -> list[dict]:
        """Execute a SQL query using the provided DB view config.

        Args:
            config: Dict with keys ``connectionString``, ``dbType``, ``sql``.

        Returns:
            A list of row dicts.

        Raises:
            ValueError: If required config fields are missing.
            SQLAlchemyError: If the query fails.
        """
        connection_string = config.get("connectionString", "")
        db_type = config.get("dbType", "mysql")
        sql = config.get("sql", "")

        if not connection_string:
            raise ValueError("connectionString is required")
        if not sql:
            raise ValueError("sql is required")

        extractor = SqlExtractor(connection_string, db_type)
        try:
            rows = extractor.execute_query(sql)
            logger.info("DB view query returned %d rows", len(rows))
            return rows
        finally:
            extractor.close()
