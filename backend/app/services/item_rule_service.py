"""Item mapping rule management service."""
import logging
from datetime import datetime
from typing import Optional

from app.database import Database
from app.engine.rule_matcher import RuleMatcher
from app.models.domain import ItemMappingRule, gen_object_id

logger = logging.getLogger(__name__)

COLLECTION = "item_mapping_rules"


class ItemRuleService:
    """Manage item mapping rules for matching raw vendor items to standard codes."""

    def get_rules(self, vendor_code: str) -> Optional[dict]:
        """Return the item mapping rules document for a vendor, or None."""
        col = Database.get_collection(COLLECTION)
        return col.find_one({"vendorCode": vendor_code})

    def save_rules(self, data: dict) -> dict:
        """Insert or upsert item mapping rules and return the saved document."""
        col = Database.get_collection(COLLECTION)
        now = datetime.utcnow()

        existing = col.find_one({"vendorCode": data["vendorCode"]})

        if existing:
            col.update_one(
                {"vendorCode": data["vendorCode"]},
                {"$set": {"rules": data.get("rules", []), "updatedAt": now}},
            )
            logger.info("Updated item rules for vendor '%s'", data["vendorCode"])
        else:
            rule_doc = ItemMappingRule(
                vendorCode=data["vendorCode"],
                rules=data.get("rules", []),
                createdAt=now,
                updatedAt=now,
            )
            doc = rule_doc.to_dict()
            col.insert_one(doc)
            logger.info("Created item rules for vendor '%s'", data["vendorCode"])

        return col.find_one({"vendorCode": data["vendorCode"]})

    def add_rule(self, vendor_code: str, rule: dict) -> dict:
        """Add a single rule to the vendor's rule set.

        If the vendor has no existing rule document, one is created.

        Returns:
            The updated rules document.
        """
        col = Database.get_collection(COLLECTION)
        now = datetime.utcnow()

        existing = col.find_one({"vendorCode": vendor_code})

        if not existing:
            # Ensure the rule has an ID
            if "ruleId" not in rule:
                rule["ruleId"] = gen_object_id()
            new_doc = ItemMappingRule(
                vendorCode=vendor_code,
                rules=[rule],
                createdAt=now,
                updatedAt=now,
            )
            col.insert_one(new_doc.to_dict())
            logger.info("Created rule document for vendor '%s' with first rule", vendor_code)
        else:
            # Ensure the rule has an ID
            if "ruleId" not in rule:
                rule["ruleId"] = gen_object_id()
            col.update_one(
                {"vendorCode": vendor_code},
                {"$push": {"rules": rule}, "$set": {"updatedAt": now}},
            )
            logger.info("Added rule to vendor '%s'", vendor_code)

        return col.find_one({"vendorCode": vendor_code})

    def delete_rule(self, vendor_code: str, rule_id: str) -> dict:
        """Remove a rule (by ruleId) from the vendor's rule set.

        Returns:
            The updated rules document.

        Raises:
            ValueError: If the vendor or rule is not found.
        """
        col = Database.get_collection(COLLECTION)
        now = datetime.utcnow()

        existing = col.find_one({"vendorCode": vendor_code})
        if not existing:
            raise ValueError(f"No rules found for vendor '{vendor_code}'")

        # Check that the rule exists before removing
        rules = existing.get("rules", [])
        matching = [r for r in rules if r.get("ruleId") == rule_id]
        if not matching:
            raise ValueError(f"Rule '{rule_id}' not found for vendor '{vendor_code}'")

        col.update_one(
            {"vendorCode": vendor_code},
            {"$pull": {"rules": {"ruleId": rule_id}}, "$set": {"updatedAt": now}},
        )
        logger.info("Deleted rule '%s' from vendor '%s'", rule_id, vendor_code)
        return col.find_one({"vendorCode": vendor_code})

    def preview_rules(self, vendor_code: str, sample_items: list) -> dict:
        """Match sample items against the vendor's rules and return the results.

        Returns:
            {"matched": list, "unmatched": list, "total": int,
             "matched_count": int, "unmatched_count": int}
        """
        rules_doc = self.get_rules(vendor_code)
        rules: list[dict] = rules_doc.get("rules", []) if rules_doc else []

        matcher = RuleMatcher(rules)
        matched, unmatched = matcher.match_all(sample_items)

        return {
            "matched": matched,
            "unmatched": unmatched,
            "total": len(sample_items),
            "matched_count": len(matched),
            "unmatched_count": len(unmatched),
        }
