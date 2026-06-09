"""Adapter profile service - manage and apply built-in/custom adapter templates."""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.database import Database
from app.data.builtin_profiles import BUILTIN_PROFILES
from app.models.domain import AdapterProfile, gen_object_id

logger = logging.getLogger(__name__)

COLLECTION = "adapter_profiles"


def _convert_doc(doc: Optional[dict]) -> Optional[dict]:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class AdapterProfileService:
    """Manage adapter profiles and apply them to create vendor configurations."""

    def __init__(self):
        self._ensure_builtin_profiles()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def list_profiles(self) -> list[dict]:
        """Return all profiles (builtin + custom)."""
        col = Database.get_collection(COLLECTION)
        docs = list(col.find().sort("isBuiltin", -1))
        return [_convert_doc(d) for d in docs]

    def get_profile(self, profile_code: str) -> Optional[dict]:
        col = Database.get_collection(COLLECTION)
        return _convert_doc(col.find_one({"profileCode": profile_code}))

    def save_profile(self, data: dict) -> dict:
        """Create or update a custom profile."""
        col = Database.get_collection(COLLECTION)
        now = datetime.now(timezone.utc)
        profile_code = data["profileCode"]

        existing = col.find_one({"profileCode": profile_code})
        if existing:
            if existing.get("isBuiltin"):
                raise ValueError(f"内置模板 '{profile_code}' 不可修改")
            update_fields = {}
            for key in (
                "profileName", "description", "tags", "accessType",
                "vendorTemplate", "accessConfigTemplate", "parserConfigTemplate",
                "itemRulesTemplate", "callbackConfigTemplate",
            ):
                if key in data:
                    update_fields[key] = data[key]
            update_fields["updatedAt"] = now
            col.update_one({"profileCode": profile_code}, {"$set": update_fields})
            logger.info("Updated adapter profile '%s'", profile_code)
            return _convert_doc(col.find_one({"profileCode": profile_code}))

        profile = AdapterProfile(
            profileCode=profile_code,
            profileName=data["profileName"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            accessType=data.get("accessType", "http_push"),
            vendorTemplate=data.get("vendorTemplate", {}),
            accessConfigTemplate=data.get("accessConfigTemplate", {}),
            parserConfigTemplate=data.get("parserConfigTemplate", {}),
            itemRulesTemplate=data.get("itemRulesTemplate", []),
            callbackConfigTemplate=data.get("callbackConfigTemplate", {}),
            isBuiltin=False,
            createdAt=now,
            updatedAt=now,
        )
        doc = profile.to_dict()
        col.insert_one(doc)
        logger.info("Created adapter profile '%s'", profile_code)
        return _convert_doc(doc)

    def delete_profile(self, profile_code: str) -> bool:
        col = Database.get_collection(COLLECTION)
        existing = col.find_one({"profileCode": profile_code})
        if not existing:
            raise ValueError(f"模板 '{profile_code}' 不存在")
        if existing.get("isBuiltin"):
            raise ValueError(f"内置模板 '{profile_code}' 不可删除")
        col.delete_one({"profileCode": profile_code})
        logger.info("Deleted adapter profile '%s'", profile_code)
        return True

    # ------------------------------------------------------------------
    # Apply profile → create vendor configs
    # ------------------------------------------------------------------

    def apply_profile(self, profile_code: str, vendor_code: str, vendor_name: str, hospital_code: str = "") -> dict:
        """Apply a profile to create a fully-configured vendor.

        Creates/updates:
        1. VendorConfig
        2. AccessConfig
        3. ParserConfig
        4. ItemMappingRules

        Returns a summary of what was created.
        """
        profile = self.get_profile(profile_code)
        if not profile:
            raise ValueError(f"适配器模板 '{profile_code}' 不存在")

        created = {}

        # 1. VendorConfig
        from app.services.vendor_service import VendorService
        vendor_svc = VendorService()
        vendor_data = {
            "vendorCode": vendor_code,
            "vendorName": vendor_name,
            "hospitalCode": hospital_code,
            "accessType": profile.get("accessType", "http_push"),
            **profile.get("vendorTemplate", {}),
        }
        try:
            vendor_svc.create_vendor(vendor_data)
            created["vendor"] = vendor_code
            logger.info("Created vendor '%s' from profile '%s'", vendor_code, profile_code)
        except ValueError as e:
            if "already exists" in str(e):
                logger.info("Vendor '%s' already exists, updating access type", vendor_code)
                vendor_svc.update_vendor(vendor_code, {"accessType": profile.get("accessType", "http_push")})
                created["vendor"] = vendor_code
            else:
                raise

        # 2. AccessConfig
        access_tpl = profile.get("accessConfigTemplate", {})
        if access_tpl:
            from app.services.access_config_service import AccessConfigService
            access_svc = AccessConfigService()
            access_data = {
                "vendorCode": vendor_code,
                "accessType": profile.get("accessType", "http_push"),
                **access_tpl,
            }
            # Replace {vendor_code} placeholder in endpoint path
            if "httpPushConfig" in access_data:
                ep = access_data["httpPushConfig"].get("endpointPath", "")
                access_data["httpPushConfig"]["endpointPath"] = ep.replace("{vendor_code}", vendor_code)
            access_svc.save_config(access_data)
            created["accessConfig"] = vendor_code
            logger.info("Created access config for vendor '%s'", vendor_code)

        # 3. ParserConfig
        parser_tpl = profile.get("parserConfigTemplate", {})
        if parser_tpl:
            from app.services.parser_config_service import ParserConfigService
            parser_svc = ParserConfigService()
            parser_data = {
                "vendorCode": vendor_code,
                **parser_tpl,
            }
            parser_svc.save_config(parser_data)
            created["parserConfig"] = vendor_code
            logger.info("Created parser config for vendor '%s'", vendor_code)

        # 4. ItemMappingRules
        rules = profile.get("itemRulesTemplate", [])
        if rules:
            from app.services.item_rule_service import ItemRuleService
            rule_svc = ItemRuleService()
            rule_svc.save_rules({"vendorCode": vendor_code, "rules": rules})
            created["itemRules"] = vendor_code
            logger.info("Created %d item rules for vendor '%s'", len(rules), vendor_code)

        return {
            "profileCode": profile_code,
            "vendorCode": vendor_code,
            "created": created,
            "summary": f"已从模板 '{profile.get('profileName', profile_code)}' 创建厂家 '{vendor_name}' 的完整配置",
        }

    # ------------------------------------------------------------------
    # Save vendor config as new profile
    # ------------------------------------------------------------------

    def save_from_vendor(self, vendor_code: str, profile_code: str, profile_name: str,
                         description: str = "", tags: list = None) -> dict:
        """Export an existing vendor's config as a reusable profile template."""
        # Gather all configs for this vendor
        vendor_col = Database.get_collection("vendor_configs")
        vendor_doc = vendor_col.find_one({"vendorCode": vendor_code})
        if not vendor_doc:
            raise ValueError(f"厂家 '{vendor_code}' 不存在")

        access_col = Database.get_collection("access_configs")
        access_doc = access_col.find_one({"vendorCode": vendor_code}) or {}

        parser_col = Database.get_collection("parser_configs")
        parser_doc = parser_col.find_one({"vendorCode": vendor_code}) or {}

        rules_col = Database.get_collection("item_mapping_rules")
        rules_doc = rules_col.find_one({"vendorCode": vendor_code}) or {}

        callback_col = Database.get_collection("callback_configs")
        callback_doc = callback_col.find_one({"vendorCode": vendor_code}) or {}

        # Strip vendor-specific fields
        vendor_tpl = {k: v for k, v in vendor_doc.items() if k not in ("_id", "vendorCode", "vendorName", "hospitalCode", "hospitalName", "createdAt", "updatedAt", "createdBy")}
        access_tpl = {k: v for k, v in access_doc.items() if k not in ("_id", "vendorCode", "createdAt", "updatedAt")}

        # Parser config: remove _id and vendorCode
        parser_tpl = {k: v for k, v in parser_doc.items() if k not in ("_id", "vendorCode", "createdAt", "updatedAt")}

        # Item rules: extract just the rules list
        item_rules = rules_doc.get("rules", [])

        # Callback config: remove _id and vendorCode
        callback_tpl = {k: v for k, v in callback_doc.items() if k not in ("_id", "vendorCode", "createdAt", "updatedAt")} if callback_doc else {}

        return self.save_profile({
            "profileCode": profile_code,
            "profileName": profile_name,
            "description": description,
            "tags": tags or [],
            "accessType": vendor_doc.get("accessType", "http_push"),
            "vendorTemplate": vendor_tpl,
            "accessConfigTemplate": access_tpl,
            "parserConfigTemplate": parser_tpl,
            "itemRulesTemplate": item_rules,
            "callbackConfigTemplate": callback_tpl,
        })

    # ------------------------------------------------------------------
    # Init builtin profiles
    # ------------------------------------------------------------------

    def _ensure_builtin_profiles(self):
        """Insert or update builtin profiles in MongoDB.

        If a builtin profile already exists, update it with the latest data
        from code (so code changes propagate on restart). Custom profiles
        are never touched.
        """
        col = Database.get_collection(COLLECTION)
        for profile_data in BUILTIN_PROFILES:
            code = profile_data["profileCode"]
            existing = col.find_one({"profileCode": code})

            if not existing:
                profile = AdapterProfile(
                    profileCode=code,
                    profileName=profile_data["profileName"],
                    description=profile_data.get("description", ""),
                    tags=profile_data.get("tags", []),
                    accessType=profile_data.get("accessType", "http_push"),
                    vendorTemplate=profile_data.get("vendorTemplate", {}),
                    accessConfigTemplate=profile_data.get("accessConfigTemplate", {}),
                    parserConfigTemplate=profile_data.get("parserConfigTemplate", {}),
                    itemRulesTemplate=profile_data.get("itemRulesTemplate", []),
                    callbackConfigTemplate=profile_data.get("callbackConfigTemplate", {}),
                    isBuiltin=True,
                )
                col.insert_one(profile.to_dict())
                logger.info("Seeded builtin adapter profile '%s'", code)
            elif existing.get("isBuiltin"):
                # Update existing builtin profile with latest data from code
                col.update_one(
                    {"profileCode": code, "isBuiltin": True},
                    {"$set": {
                        "profileName": profile_data["profileName"],
                        "description": profile_data.get("description", ""),
                        "tags": profile_data.get("tags", []),
                        "accessType": profile_data.get("accessType", "http_push"),
                        "vendorTemplate": profile_data.get("vendorTemplate", {}),
                        "accessConfigTemplate": profile_data.get("accessConfigTemplate", {}),
                        "parserConfigTemplate": profile_data.get("parserConfigTemplate", {}),
                        "itemRulesTemplate": profile_data.get("itemRulesTemplate", []),
                        "callbackConfigTemplate": profile_data.get("callbackConfigTemplate", {}),
                        "updatedAt": datetime.now(timezone.utc),
                    }},
                )
                logger.info("Updated builtin adapter profile '%s'", code)
