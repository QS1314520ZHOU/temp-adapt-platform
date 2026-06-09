import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from lxml import etree

from app.engine.jsonpath_extractor import JsonPathExtractor
from app.engine.rule_matcher import RuleMatcher
from app.engine.value_parser import ValueParser
from app.engine.xpath_extractor import XPathExtractor
from app.utils.idempotent import make_idempotent_key_safe

logger = logging.getLogger(__name__)


class TransformEngine:
    """Core engine that transforms vendor-specific data into the standard
    ``TemperatureRecord`` format.

    The engine is configured with a *parser_config* dict (describing how to
    locate and map fields) and a list of *item_rules* (ItemMappingRule dicts
    used by :class:`RuleMatcher`).

    Args:
        parser_config: Parser / mapping configuration dict.  Expected keys
            include ``format`` (``"json"`` or ``"xml"``), ``recordPath``,
            ``rootFieldMappings``, ``recordFieldMappings``, ``itemPath``,
            ``itemMappings``, etc.
        item_rules: A list of ``ItemMappingRule`` dicts consumed by
            :class:`RuleMatcher`.
    """

    def __init__(self, parser_config: dict, item_rules: list[dict]) -> None:
        self.parser_config: dict = parser_config
        self.item_rules: list[dict] = item_rules

        self._jsonpath = JsonPathExtractor()
        self._xpath = XPathExtractor()
        self._value_parser = ValueParser()
        self._rule_matcher = RuleMatcher(item_rules)

    # ==================================================================
    # Public API
    # ==================================================================

    def transform(self, raw_data: str, vendor_code: str) -> dict:
        """Transform *raw_data* into a standardised result dict.

        Args:
            raw_data: The raw payload as a string (JSON or XML).
            vendor_code: An identifier for the data vendor.

        Returns:
            A dict with keys ``records``, ``unmatched``, ``errors``,
            ``total``, ``success``, ``fail``.
        """
        records: list[dict] = []
        unmatched_items: list[dict] = []
        errors: list[dict] = []

        try:
            raw_records, parsed_data = self._extract_records(raw_data)
        except Exception as e:
            logger.error("Failed to extract records: %s", e)
            return self._build_result([], [], [{"error": str(e), "stage": "extract"}], 0, 0, 0)

        root_fields = self._map_root_fields(raw_data, parsed_data)

        # Get item field mappings for value extraction
        item_field_mappings = self.parser_config.get("itemFieldMappings", {})

        for idx, raw_record in enumerate(raw_records):
            try:
                mapped_record = self._map_record_fields(raw_record)
                raw_items = self._map_item_fields(raw_record)

                matched, unmatched = self._rule_matcher.match_all(raw_items)
                unmatched_items.extend(unmatched)

                parsed_items: list[dict] = []
                for pair in matched:
                    item_data = pair["item"]
                    rule = pair["rule"]

                    # Extract the raw value from item using itemFieldMappings
                    # Default: try "itemValue" mapped field, then "value", then "item_data"
                    raw_value = None
                    if isinstance(item_field_mappings, dict):
                        value_mapping = item_field_mappings.get("itemValue", {})
                        source = value_mapping.get("sourcePath") if isinstance(value_mapping, dict) else value_mapping
                        if source:
                            if isinstance(source, str) and source.startswith("$"):
                                raw_value = self._jsonpath.extract_single(item_data, source)
                            else:
                                raw_value = item_data.get(source)
                    if raw_value is None:
                        raw_value = item_data.get("itemValue") or item_data.get("value") or item_data.get("item_data")

                    parsed = self._transform_value(raw_value, rule)

                    # Build the standard temperature item
                    temp_item: dict = {
                        "code": rule.get("targetCode"),
                        "name": rule.get("targetName"),
                        "value": parsed,
                        "unit": rule.get("unit"),
                        "source": "vendor",
                        "matched": True,
                    }

                    # Handle blood pressure splitting
                    if rule.get("dataType") == "blood_pressure" and isinstance(parsed, (int, float, str)):
                        bp = self._value_parser.split_blood_pressure(str(parsed), rule.get("splitSeparator", "/"))
                        if bp:
                            temp_item["extra"] = bp

                    # Preserve raw item identifiers
                    if isinstance(item_field_mappings, dict):
                        id_mapping = item_field_mappings.get("itemCode", {})
                        name_mapping = item_field_mappings.get("itemName", {})
                        id_source = id_mapping.get("sourcePath") if isinstance(id_mapping, dict) else None
                        name_source = name_mapping.get("sourcePath") if isinstance(name_mapping, dict) else None
                        if id_source:
                            temp_item["rawItemId"] = self._jsonpath.extract_single(item_data, id_source) if id_source.startswith("$") else item_data.get(id_source)
                        if name_source:
                            temp_item["rawItemName"] = self._jsonpath.extract_single(item_data, name_source) if name_source.startswith("$") else item_data.get(name_source)

                    parsed_items.append(temp_item)

                temperature_record = self._build_temperature_record(
                    mapped_record, parsed_items, root_fields
                )
                temperature_record["idempotentKey"] = make_idempotent_key_safe(
                    vendor_code,
                    str(mapped_record.get("visitNo", "")),
                    str(mapped_record.get("patientVisitId", "")),
                    str(mapped_record.get("recordTime", "")),
                    payload=raw_data,
                )
                temperature_record["vendorCode"] = vendor_code
                records.append(temperature_record)

            except Exception as e:
                logger.error("Failed to transform record #%d: %s", idx, e)
                errors.append({"index": idx, "error": str(e), "stage": "transform"})

        success = len(records)
        fail = len(errors)
        total = success + fail

        logger.info(
            "Transform complete for vendor '%s': total=%d, success=%d, fail=%d, unmatched_items=%d",
            vendor_code, total, success, fail, len(unmatched_items),
        )

        return self._build_result(records, unmatched_items, errors, total, success, fail)

    # ==================================================================
    # Internal helpers
    # ==================================================================

    def _extract_records(self, raw_data: str) -> tuple[list[dict], Any]:
        """Parse *raw_data* and extract individual record dicts using the
        configured ``recordPath``.

        Returns:
            A tuple of ``(records, parsed_data)`` where *parsed_data* is the
            full parsed object (JSON dict or raw XML string) needed by
            :meth:`_map_root_fields`.  Previously this was stashed on
            ``self._last_parsed``, which made the engine non-thread-safe.
        """
        fmt = self.parser_config.get("format") or self.parser_config.get("dataFormat", "json")
        record_path = self.parser_config.get("recordPath", "$")

        if fmt == "json":
            data = json.loads(raw_data)
            matches = self._jsonpath.extract(data, record_path)
            if not matches:
                logger.warning("recordPath '%s' matched nothing", record_path)
                return [], data
            # Each match should be a dict (a single record).
            records = []
            for m in matches:
                if isinstance(m, dict):
                    records.append(m)
                else:
                    logger.warning(
                        "recordPath '%s' returned a non-dict scalar (%s: %r); "
                        "wrapped as {'_value': ...} -- field mappings will not "
                        "match unless they target '_value'. Consider updating "
                        "your recordPath to return objects.",
                        record_path, type(m).__name__, m,
                    )
                    records.append({"_value": m})
            return records, data

        if fmt == "xml":
            nodes = self._xpath.extract_from_string(raw_data, record_path)
            return [{"_xml_node": node} for node in nodes], raw_data

        raise ValueError(f"Unsupported data format: '{fmt}'")

    def _map_root_fields(self, raw_data: str, parsed_data: Any) -> dict:
        """Map root-level fields from the top-level parsed data.

        Args:
            raw_data: The original raw string (used for XML re-parse fallback).
            parsed_data: The already-parsed data from :meth:`_extract_records`.
                For JSON this is the deserialised dict; for XML this is the
                raw XML string.
        """
        mappings: dict = self.parser_config.get("rootFieldMappings", {})
        result: dict = {}

        fmt = self.parser_config.get("format") or self.parser_config.get("dataFormat", "json")

        for target_field, mapping in mappings.items():
            source_path = mapping.get("sourcePath") if isinstance(mapping, dict) else mapping
            if not source_path:
                continue

            if fmt == "json":
                value = self._jsonpath.extract_single(parsed_data, source_path)
            else:
                nodes = self._xpath.extract_from_string(raw_data, source_path)
                value = nodes[0] if nodes else None

            result[target_field] = value

        return result

    def _map_record_fields(self, record: dict) -> dict:
        """Map fields within a single record according to
        ``recordFieldMappings``.

        Supports both JSON records (plain dicts) and XML records (dicts
        with an ``_xml_node`` key containing an lxml node).
        """
        mappings: dict = self.parser_config.get("recordFieldMappings", {})
        result: dict = {}

        # Detect whether this is an XML-backed record.
        xml_node = record.get("_xml_node")

        for target_field, mapping in mappings.items():
            # Support both sourceField and sourcePath keys
            source_path = None
            if isinstance(mapping, dict):
                source_path = mapping.get("sourcePath") or mapping.get("sourceField")
            else:
                source_path = mapping

            if not source_path:
                continue

            # Extract value
            value = None
            if xml_node is not None:
                # XML record: use XPath on the node.
                nodes = self._xpath.extract_from_node(xml_node, source_path)
                if nodes:
                    first = nodes[0]
                    value = first.text.strip() if hasattr(first, "text") and first.text else str(first)
            elif isinstance(source_path, str) and source_path.startswith("$"):
                value = self._jsonpath.extract_single(record, source_path)
            else:
                value = record.get(source_path) if isinstance(record, dict) else None

            if value is not None and isinstance(mapping, dict):
                data_type = mapping.get("dataType")
                if data_type:
                    value = self._value_parser.parse(
                        value, data_type, mapping.get("dateFormat")
                    )

            # Apply default value if value is None
            if value is None and isinstance(mapping, dict):
                value = mapping.get("defaultValue")

            result[target_field] = value

        return result

    def _map_item_fields(self, record: dict) -> list[dict]:
        """Extract item-level data from *record* using ``itemPath``."""
        item_path = self.parser_config.get("itemPath")
        if not item_path:
            return []

        fmt = self.parser_config.get("format") or self.parser_config.get("dataFormat", "json")

        if fmt == "json":
            return self._jsonpath.extract(record, item_path) or []

        # XML: item_path is an XPath relative to the record node.
        node = record.get("_xml_node")
        if node is None:
            return []

        if item_path == ".":
            # Special case: itemPath "." means the record node itself IS the
            # item container.  Each child element is treated as a separate item.
            # This is the DHCC/EStatusParameter pattern where fields like
            # Temperature, Pulse, etc. are direct child elements.
            items = []
            for child in node:
                tag = etree.QName(child).localname if hasattr(child, 'tag') else str(child.tag)
                text = child.text.strip() if child.text else ""
                if text:
                    items.append({"fieldName": tag, "value": text, "_xml_node": child})
            return items

        nodes = self._xpath.extract_from_node(node, item_path)
        return [{"_xml_node": n} for n in nodes]

    def _transform_value(self, value: Any, mapping: dict) -> Any:
        """Transform a single *value* according to the rule *mapping*."""
        data_type = mapping.get("dataType", "string")
        date_format = mapping.get("dateFormat")

        result = self._value_parser.parse(value, data_type, date_format)

        # NOTE: Blood-pressure splitting is handled exclusively in the
        # caller (transform main loop) via ``dataType == "blood_pressure"``.
        # Do NOT split here -- the old ``splitBloodPressure`` branch caused
        # a double-split when both conditions were true.

        # Regex extraction.
        regex_pattern = mapping.get("regexExtract")
        if regex_pattern and result is not None:
            extracted = self._value_parser.apply_regex(str(result), regex_pattern)
            return extracted if extracted is not None else result

        # Dict mapping.
        dict_map = mapping.get("valueMapping")
        if dict_map and result is not None:
            return self._value_parser.apply_dict_mapping(str(result), dict_map)

        return result

    def _build_temperature_record(
        self,
        mapped_record: dict,
        items: list[dict],
        root_fields: dict,
    ) -> dict:
        """Assemble the final standardised temperature record."""
        record: dict = {
            **root_fields,
            **mapped_record,
            "items": items,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        return record

    # ------------------------------------------------------------------
    # Result builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_result(
        records: list[dict],
        unmatched: list[dict],
        errors: list[dict],
        total: int,
        success: int,
        fail: int,
    ) -> dict:
        return {
            "records": records,
            "unmatched": unmatched,
            "errors": errors,
            "total": total,
            "success": success,
            "fail": fail,
        }
