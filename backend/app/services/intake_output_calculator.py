"""Intake/Output calculation engine."""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class IntakeOutputCalculator:
    """Core calculation logic for intake/output statistics.

    Processes bedside records matched against item configs, grouped by
    category, with configurable stat types (sum, count, latest, text_merge).
    """

    def calculate(
        self,
        bedside_records: list,
        item_configs: list,
        stat_rules: list,
        patient_info: dict,
        start_time,
        end_time,
        field_mappings: Optional[dict] = None,
    ) -> dict:
        """Run the intake/output calculation.

        Args:
            bedside_records: Raw bedside measurement records from SmartCare.
            item_configs: List of IntakeOutputItemConfig dicts defining how
                to classify each paramCode.
            stat_rules: List of IntakeOutputStatRule dicts defining
                aggregation rules.
            patient_info: Patient metadata dict.
            start_time: Start of the calculation time window.
            end_time: End of the calculation time window.
            field_mappings: Optional field name mappings for bedside records.

        Returns:
            {
                "results": list[dict],     # aggregated results per code
                "unmatched": list[dict],   # records that didn't match any config
                "raw_details": list[dict]  # all records with category classification
            }
        """
        # Build a lookup from paramCode -> item_config
        code_key = (field_mappings or {}).get("paramCode", "paramCode")
        time_key = (field_mappings or {}).get("recordTime", "recordTime")
        strval_key = (field_mappings or {}).get("strVal", "strVal")

        config_by_code: dict[str, dict] = {}
        for cfg in item_configs:
            pc = cfg.get("paramCode", "")
            if pc:
                config_by_code[pc] = cfg

        # 1. Filter bedside records by time range and classify
        filtered_records: list[dict] = []
        unmatched: list[dict] = []
        raw_details: list[dict] = []

        for record in bedside_records:
            record_time = record.get(time_key)
            if record_time is None:
                continue

            # Ensure record_time is comparable
            if isinstance(record_time, str):
                try:
                    record_time = datetime.fromisoformat(record_time.replace("Z", "+00:00"))
                except ValueError:
                    continue

            if record_time < start_time or record_time > end_time:
                continue

            filtered_records.append(record)
            param_code = record.get(code_key, "")

            config = config_by_code.get(param_code)
            if config is None:
                unmatched.append(record)
                raw_details.append({
                    **record,
                    "_category": None,
                    "_matched": False,
                })
            else:
                raw_details.append({
                    **record,
                    "_category": config.get("category"),
                    "_subCategory": config.get("subCategory"),
                    "_matched": True,
                })

        # 2. Group matched records by category -> subCategory -> paramCode
        grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
        grouped_codes: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

        for record in filtered_records:
            param_code = record.get(code_key, "")
            config = config_by_code.get(param_code)
            if config is None:
                continue

            category = config.get("category", "other")
            sub_category = config.get("subCategory", param_code)
            grouped[category][sub_category].append(record)
            grouped_codes[category][sub_category].append(param_code)

        # 3. Build stat rules lookup: code -> rule
        rule_by_code: dict[str, dict] = {}
        for rule in stat_rules:
            rule_by_code[rule.get("code", "")] = rule

        # 4. Apply stat rules and compute results
        results: list[dict] = []

        # First, process records grouped by item configs
        for category, subcats in grouped.items():
            for sub_category, records_in_group in subcats.items():
                # Find the item config for this sub_category
                # Use the first matching config
                matching_configs = [
                    config_by_code[r.get(code_key, "")] for r in records_in_group
                    if config_by_code.get(r.get(code_key, ""))
                ]
                if not matching_configs:
                    continue

                cfg = matching_configs[0]
                stat_type = cfg.get("statType", "sum")
                unit = cfg.get("unit", "")
                param_name = cfg.get("paramName", sub_category)
                codes_in_group = list(set(grouped_codes[category][sub_category]))

                # Check if there's an override stat rule
                for rule in stat_rules:
                    if rule.get("targetItemCode") == sub_category or rule.get("code") == sub_category:
                        stat_type = rule.get("statType", stat_type)
                        unit = rule.get("unit", unit)
                        param_name = rule.get("name", param_name)
                        break

                value = self._aggregate(records_in_group, stat_type, strval_key)

                results.append({
                    "code": sub_category,
                    "name": param_name,
                    "value": value,
                    "unit": unit,
                    "statType": stat_type,
                    "itemCount": len(records_in_group),
                    "detailCodes": codes_in_group,
                    "category": category,
                    "subCategory": sub_category,
                })

        return {
            "results": results,
            "unmatched": unmatched,
            "raw_details": raw_details,
        }

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------

    def _aggregate(self, records: list[dict], stat_type: str, strval_key: str) -> Any:
        """Aggregate records according to the stat type.

        Args:
            records: The bedside records to aggregate.
            stat_type: One of "sum", "count", "latest", "text_merge".
            strval_key: The field name containing the string value.

        Returns:
            The aggregated value.
        """
        if stat_type == "sum":
            return self._aggregate_sum(records, strval_key)
        elif stat_type == "count":
            return self._aggregate_count(records, strval_key)
        elif stat_type == "latest":
            return self._aggregate_latest(records, strval_key)
        elif stat_type == "text_merge":
            return self._aggregate_text_merge(records, strval_key)
        else:
            logger.warning("Unknown stat type '%s', defaulting to sum", stat_type)
            return self._aggregate_sum(records, strval_key)

    def _aggregate_sum(self, records: list[dict], strval_key: str) -> float:
        """Sum all numeric strVal values."""
        total = 0.0
        for rec in records:
            val = rec.get(strval_key)
            if val is not None:
                try:
                    total += float(val)
                except (ValueError, TypeError):
                    logger.debug("Skipping non-numeric value '%s' in sum aggregation", val)
        return round(total, 2)

    def _aggregate_count(self, records: list[dict], strval_key: str) -> int:
        """Count distinct records, or sum if values represent counts."""
        # Check if the values themselves represent counts
        values = []
        for rec in records:
            val = rec.get(strval_key)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass

        # If all values are integers >= 1, they might be counts -- sum them
        if values and all(v == int(v) and v >= 1 for v in values):
            return int(sum(values))

        # Otherwise, count distinct records
        return len(records)

    def _aggregate_latest(self, records: list[dict], strval_key: str) -> Any:
        """Take the most recent value."""
        if not records:
            return None

        # Sort by time descending and take the first
        sorted_recs = sorted(records, key=lambda r: r.get("time") or r.get("recordTime") or datetime.min, reverse=True)
        return sorted_recs[0].get(strval_key)

    def _aggregate_text_merge(self, records: list[dict], strval_key: str) -> str:
        """Concatenate unique text values, comma-separated."""
        seen: set[str] = set()
        parts: list[str] = []
        for rec in records:
            val = rec.get(strval_key)
            if val is not None:
                val_str = str(val).strip()
                if val_str and val_str not in seen:
                    seen.add(val_str)
                    parts.append(val_str)
        return ", ".join(parts)
