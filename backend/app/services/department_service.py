"""Department / Ward configuration service."""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.database import Database
from app.models.domain import DepartmentConfig, gen_object_id

logger = logging.getLogger(__name__)


class DepartmentService:
    """科室/病区配置服务"""

    COLLECTION = "department_configs"

    def list_departments(self, vendor_code: Optional[str] = None, enabled_only: bool = False) -> list:
        """Return all department configs, optionally filtered by vendor and enabled status."""
        col = Database.get_collection(self.COLLECTION)
        query: dict = {}
        if vendor_code:
            query["vendorCode"] = vendor_code
        if enabled_only:
            query["enabled"] = True
        return list(col.find(query).sort("createdAt", -1))

    def get_department(self, dept_id: str) -> Optional[dict]:
        """Return a single department config by ID, or None."""
        col = Database.get_collection(self.COLLECTION)
        return col.find_one({"_id": dept_id})

    def save_department(self, data: dict) -> dict:
        """Insert a new department config and return the created document."""
        col = Database.get_collection(self.COLLECTION)
        now = datetime.now(timezone.utc)

        dept = DepartmentConfig(
            vendorCode=data.get("vendorCode"),
            wardCode=data.get("wardCode", ""),
            wardName=data.get("wardName", ""),
            hospitalCode=data.get("hospitalCode"),
            hisDeptCode=data.get("hisDeptCode"),
            hisDeptName=data.get("hisDeptName"),
            hisWardCode=data.get("hisWardCode"),
            hisWardName=data.get("hisWardName"),
            bedRangeStart=data.get("bedRangeStart"),
            bedRangeEnd=data.get("bedRangeEnd"),
            enabled=data.get("enabled", True),
            syncEnabled=data.get("syncEnabled", True),
            callbackEnabled=data.get("callbackEnabled", True),
            remark=data.get("remark"),
            createdAt=now,
            updatedAt=now,
        )
        doc = dept.to_dict()
        col.insert_one(doc)
        logger.info("Created department config '%s' (%s)", dept.wardCode, dept.wardName)
        return doc

    def update_department(self, dept_id: str, data: dict) -> dict:
        """Update an existing department config and return the updated document."""
        col = Database.get_collection(self.COLLECTION)

        existing = col.find_one({"_id": dept_id})
        if not existing:
            raise ValueError(f"Department '{dept_id}' not found")

        update_fields: dict = {}
        for key in (
            "vendorCode", "wardCode", "wardName", "hospitalCode",
            "hisDeptCode", "hisDeptName", "hisWardCode", "hisWardName",
            "bedRangeStart", "bedRangeEnd", "enabled",
            "syncEnabled", "callbackEnabled", "remark",
        ):
            if key in data:
                update_fields[key] = data[key]

        update_fields["updatedAt"] = datetime.now(timezone.utc)
        col.update_one({"_id": dept_id}, {"$set": update_fields})
        logger.info("Updated department config '%s'", dept_id)
        return col.find_one({"_id": dept_id})

    def delete_department(self, dept_id: str) -> dict:
        """Delete a department config by ID."""
        col = Database.get_collection(self.COLLECTION)

        existing = col.find_one({"_id": dept_id})
        if not existing:
            raise ValueError(f"Department '{dept_id}' not found")

        col.delete_one({"_id": dept_id})
        logger.info("Deleted department config '%s'", dept_id)
        return {"deleted": True, "id": dept_id}

    def batch_save(self, vendor_code: str, departments: list) -> dict:
        """Batch save department configs for a vendor.

        Existing departments (matched by vendorCode + wardCode) are updated;
        new ones are inserted.
        """
        col = Database.get_collection(self.COLLECTION)
        now = datetime.now(timezone.utc)
        inserted = 0
        updated = 0
        errors = []

        for dept_data in departments:
            try:
                ward_code = dept_data.get("wardCode", "")
                existing = col.find_one({
                    "vendorCode": vendor_code,
                    "wardCode": ward_code,
                })

                if existing:
                    update_fields: dict = {}
                    for key in (
                        "wardName", "hospitalCode", "hisDeptCode", "hisDeptName",
                        "hisWardCode", "hisWardName", "bedRangeStart", "bedRangeEnd",
                        "enabled", "syncEnabled", "callbackEnabled", "remark",
                    ):
                        if key in dept_data:
                            update_fields[key] = dept_data[key]
                    update_fields["updatedAt"] = now
                    col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
                    updated += 1
                else:
                    dept = DepartmentConfig(
                        vendorCode=vendor_code,
                        wardCode=ward_code,
                        wardName=dept_data.get("wardName", ""),
                        hospitalCode=dept_data.get("hospitalCode"),
                        hisDeptCode=dept_data.get("hisDeptCode"),
                        hisDeptName=dept_data.get("hisDeptName"),
                        hisWardCode=dept_data.get("hisWardCode"),
                        hisWardName=dept_data.get("hisWardName"),
                        bedRangeStart=dept_data.get("bedRangeStart"),
                        bedRangeEnd=dept_data.get("bedRangeEnd"),
                        enabled=dept_data.get("enabled", True),
                        syncEnabled=dept_data.get("syncEnabled", True),
                        callbackEnabled=dept_data.get("callbackEnabled", True),
                        remark=dept_data.get("remark"),
                        createdAt=now,
                        updatedAt=now,
                    )
                    col.insert_one(dept.to_dict())
                    inserted += 1
            except Exception as e:
                errors.append({"wardCode": dept_data.get("wardCode", ""), "error": str(e)})

        logger.info(
            "Batch save for vendor '%s': inserted=%d, updated=%d, errors=%d",
            vendor_code, inserted, updated, len(errors),
        )
        return {
            "inserted": inserted,
            "updated": updated,
            "errors": errors,
            "total": len(departments),
        }
