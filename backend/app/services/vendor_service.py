"""Vendor configuration management service."""
import logging
from datetime import datetime
from typing import Optional

from app.database import Database
from app.models.domain import VendorConfig, gen_object_id

logger = logging.getLogger(__name__)

COLLECTION = "vendor_configs"


def _convert_doc(doc: Optional[dict]) -> Optional[dict]:
    """Convert ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class VendorService:
    """CRUD operations for vendor configurations."""

    def list_vendors(self, enabled_only: bool = False) -> list[dict]:
        """Return a list of all vendor configs, optionally filtered to enabled only."""
        col = Database.get_collection(COLLECTION)
        query: dict = {}
        if enabled_only:
            query["enabled"] = True
        docs = list(col.find(query).sort("createdAt", -1))
        return [_convert_doc(doc) for doc in docs]

    def get_vendor(self, vendor_code: str) -> Optional[dict]:
        """Return a single vendor config by vendorCode, or None."""
        col = Database.get_collection(COLLECTION)
        return _convert_doc(col.find_one({"vendorCode": vendor_code}))

    def create_vendor(self, data: dict) -> dict:
        """Insert a new vendor config and return the created document."""
        col = Database.get_collection(COLLECTION)

        # Check for duplicate vendorCode
        if col.find_one({"vendorCode": data["vendorCode"]}):
            raise ValueError(f"Vendor with code '{data['vendorCode']}' already exists")

        now = datetime.utcnow()
        vendor = VendorConfig(
            vendorCode=data["vendorCode"],
            vendorName=data["vendorName"],
            hospitalCode=data.get("hospitalCode"),
            hospitalName=data.get("hospitalName"),
            enabled=data.get("enabled", True),
            accessType=data.get("accessType", "http_push"),
            description=data.get("description"),
            contactInfo=data.get("contactInfo"),
            createdAt=now,
            updatedAt=now,
            createdBy=data.get("createdBy"),
        )
        doc = vendor.to_dict()
        col.insert_one(doc)
        logger.info("Created vendor '%s'", data["vendorCode"])
        return _convert_doc(doc)

    def update_vendor(self, vendor_code: str, data: dict) -> dict:
        """Update an existing vendor config and return the updated document."""
        col = Database.get_collection(COLLECTION)

        existing = col.find_one({"vendorCode": vendor_code})
        if not existing:
            raise ValueError(f"Vendor '{vendor_code}' not found")

        update_fields: dict = {}
        for key in (
            "vendorName",
            "hospitalCode",
            "hospitalName",
            "enabled",
            "accessType",
            "description",
            "contactInfo",
        ):
            if key in data:
                update_fields[key] = data[key]

        update_fields["updatedAt"] = datetime.utcnow()

        col.update_one({"vendorCode": vendor_code}, {"$set": update_fields})
        logger.info("Updated vendor '%s'", vendor_code)
        return _convert_doc(col.find_one({"vendorCode": vendor_code}))

    def toggle_vendor(self, vendor_code: str, enabled: bool) -> dict:
        """Enable or disable a vendor and return the updated document."""
        col = Database.get_collection(COLLECTION)

        result = col.update_one(
            {"vendorCode": vendor_code},
            {"$set": {"enabled": enabled, "updatedAt": datetime.utcnow()}},
        )
        if result.matched_count == 0:
            raise ValueError(f"Vendor '{vendor_code}' not found")

        logger.info("Vendor '%s' enabled=%s", vendor_code, enabled)
        return _convert_doc(col.find_one({"vendorCode": vendor_code}))

    def delete_vendor(self, vendor_code: str) -> bool:
        """Delete a vendor config by vendorCode. Returns True if deleted."""
        col = Database.get_collection(COLLECTION)
        result = col.delete_one({"vendorCode": vendor_code})
        if result.deleted_count == 0:
            raise ValueError(f"Vendor '{vendor_code}' not found")
        logger.info("Deleted vendor '%s'", vendor_code)
        return True
