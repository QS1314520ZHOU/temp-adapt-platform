"""Parser configuration management service."""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from app.database import Database
from app.engine.jsonpath_extractor import JsonPathExtractor
from app.engine.transform_engine import TransformEngine
from app.engine.xpath_extractor import XPathExtractor
from app.models.domain import ParserConfig

logger = logging.getLogger(__name__)

COLLECTION = "parser_configs"


class ParserConfigService:
    """Manage parser configurations and test extraction expressions."""

    def __init__(self) -> None:
        self._jsonpath = JsonPathExtractor()
        self._xpath = XPathExtractor()

    def get_config(self, vendor_code: str) -> Optional[dict]:
        """Return the parser config for a vendor, or None."""
        col = Database.get_collection(COLLECTION)
        return col.find_one({"vendorCode": vendor_code})

    def save_config(self, data: dict) -> dict:
        """Insert or upsert a parser config and return the saved document."""
        col = Database.get_collection(COLLECTION)
        now = datetime.now(timezone.utc)

        existing = col.find_one({"vendorCode": data["vendorCode"]})

        update_fields: dict = {
            "dataFormat": data.get("dataFormat", "json"),
            "encoding": data.get("encoding", "UTF-8"),
            "rootPath": data.get("rootPath", "$"),
            "recordPath": data["recordPath"],
            "itemPath": data.get("itemPath"),
            "recordPathType": data.get("recordPathType", "jsonpath"),
            "itemPathType": data.get("itemPathType", "jsonpath"),
            "rootFieldMappings": data.get("rootFieldMappings", []),
            "recordFieldMappings": data.get("recordFieldMappings", []),
            "itemFieldMappings": data.get("itemFieldMappings", []),
            "xmlConfig": data.get("xmlConfig"),
            "sqlConfig": data.get("sqlConfig"),
            "enabled": data.get("enabled", True),
            "updatedAt": now,
        }

        if existing:
            col.update_one({"vendorCode": data["vendorCode"]}, {"$set": update_fields})
            logger.info("Updated parser config for vendor '%s'", data["vendorCode"])
        else:
            config = ParserConfig(
                vendorCode=data["vendorCode"],
                dataFormat=data.get("dataFormat", "json"),
                encoding=data.get("encoding", "UTF-8"),
                rootPath=data.get("rootPath", "$"),
                recordPath=data["recordPath"],
                itemPath=data.get("itemPath"),
                recordPathType=data.get("recordPathType", "jsonpath"),
                itemPathType=data.get("itemPathType", "jsonpath"),
                rootFieldMappings=data.get("rootFieldMappings", []),
                recordFieldMappings=data.get("recordFieldMappings", []),
                itemFieldMappings=data.get("itemFieldMappings", []),
                xmlConfig=data.get("xmlConfig"),
                sqlConfig=data.get("sqlConfig"),
                enabled=data.get("enabled", True),
                createdAt=now,
                updatedAt=now,
            )
            doc = config.to_dict()
            col.insert_one(doc)
            logger.info("Created parser config for vendor '%s'", data["vendorCode"])

        return col.find_one({"vendorCode": data["vendorCode"]})

    def test_jsonpath(self, data: str, path: str) -> dict:
        """Evaluate a JsonPath expression against JSON data.

        Returns:
            {"matches": list, "count": int}
        """
        try:
            parsed = json.loads(data)
            matches = self._jsonpath.extract(parsed, path)
            return {"matches": matches, "count": len(matches)}
        except json.JSONDecodeError as e:
            return {"matches": [], "count": 0}
        except Exception as e:
            logger.error("JsonPath test failed: %s", e)
            return {"matches": [], "count": 0}

    def test_xpath(self, data: str, path: str, namespaces: Optional[dict] = None) -> dict:
        """Evaluate an XPath expression against XML data.

        Returns:
            {"matches": list, "count": int}
        """
        try:
            nodes = self._xpath.extract_from_string(data, path, namespaces)
            # Convert nodes to string representations for JSON serialization
            matches = []
            for node in nodes:
                if hasattr(node, "text"):
                    matches.append(node.text or "")
                else:
                    matches.append(str(node))
            return {"matches": matches, "count": len(matches)}
        except Exception as e:
            logger.error("XPath test failed: %s", e)
            return {"matches": [], "count": 0}

    def preview_mapping(self, vendor_code: str, sample_data: str) -> dict:
        """Run a transform preview using the vendor's parser config and item rules.

        Returns:
            {"records": list, "unmatched": list, "errors": list,
             "total": int, "success": int, "fail": int}
        """
        config = self.get_config(vendor_code)
        if not config:
            return {"records": [], "unmatched": [], "errors": [{"error": f"No parser config for '{vendor_code}'"}],
                    "total": 0, "success": 0, "fail": 0}

        # Build engine config dict (TransformEngine expects a plain dict, not a domain model)
        # Convert list-based field mappings to dict format for the engine
        def _list_to_dict(mappings):
            """Convert [{targetField, sourcePath, ...}] to {targetField: {sourcePath, ...}}."""
            if isinstance(mappings, dict):
                return mappings
            if isinstance(mappings, list):
                result = {}
                for m in mappings:
                    if isinstance(m, dict) and "targetField" in m:
                        result[m["targetField"]] = m
                return result
            return {}

        parser_config: dict = {
            "format": config.get("dataFormat", "json"),
            "recordPath": config.get("recordPath", "$"),
            "itemPath": config.get("itemPath"),
            "rootFieldMappings": _list_to_dict(config.get("rootFieldMappings", [])),
            "recordFieldMappings": _list_to_dict(config.get("recordFieldMappings", [])),
            "itemFieldMappings": _list_to_dict(config.get("itemFieldMappings", [])),
        }

        # Load item rules
        rules_col = Database.get_collection("item_mapping_rules")
        rules_doc = rules_col.find_one({"vendorCode": vendor_code})
        item_rules: list[dict] = rules_doc.get("rules", []) if rules_doc else []

        engine = TransformEngine(parser_config, item_rules)
        return engine.transform(sample_data, vendor_code)

    def delete_config(self, vendor_code: str) -> bool:
        """Delete the parser config for a vendor."""
        col = Database.get_collection(COLLECTION)
        result = col.delete_one({"vendorCode": vendor_code})
        if result.deleted_count == 0:
            raise ValueError(f"解析配置 '{vendor_code}' 不存在")
        logger.info("Deleted parser config for vendor '%s'", vendor_code)
        return True
