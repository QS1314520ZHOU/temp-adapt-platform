import logging
import re
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ValueParser:
    """Parse and transform raw values into the expected Python types."""

    # ------------------------------------------------------------------
    # Core type parsing
    # ------------------------------------------------------------------

    def parse(self, value: Any, data_type: str, date_format: Optional[str] = None) -> Any:
        """Convert *value* to the target *data_type*.

        Args:
            value: The raw value to convert.
            data_type: One of ``"string"``, ``"number"``, ``"datetime"``,
                ``"boolean"``.
            date_format: An optional ``strptime``-compatible format string
                used when *data_type* is ``"datetime"``.  When omitted the
                function falls back to ``dateutil.parser.parse``.

        Returns:
            The converted value, or ``None`` when conversion fails.
        """
        if value is None:
            return None

        data_type = data_type.lower()

        if data_type == "string":
            return str(value)

        if data_type == "number":
            return self._to_number(value)

        if data_type == "datetime":
            return self._to_datetime(value, date_format)

        if data_type == "boolean":
            return self._to_boolean(value)

        logger.warning("Unknown data_type '%s', returning value as-is", data_type)
        return value

    # ------------------------------------------------------------------
    # Specialised helpers
    # ------------------------------------------------------------------

    def split_blood_pressure(self, value: str, separator: str = "/") -> dict:
        """Split a blood-pressure string into systolic / diastolic components.

        Args:
            value: A string such as ``"154/97"``.
            separator: The delimiter between the two values (default ``"/"``).

        Returns:
            A dict ``{"systolic": int, "diastolic": int}``, or an empty dict
            if parsing fails.
        """
        try:
            parts = value.split(separator)
            if len(parts) != 2:
                logger.warning("Blood pressure value '%s' did not split into two parts", value)
                return {}
            systolic = int(parts[0].strip())
            diastolic = int(parts[1].strip())
            return {"systolic": systolic, "diastolic": diastolic}
        except (ValueError, AttributeError) as e:
            logger.error("Failed to split blood pressure value '%s': %s", value, e)
            return {}

    def apply_regex(self, value: str, pattern: str, group: int = 0) -> Optional[str]:
        """Extract a substring from *value* using a regular expression.

        Args:
            value: The input string.
            pattern: A regular expression pattern.
            group: The capture group index to return (default ``0`` = entire
                match).

        Returns:
            The matched substring, or ``None`` if there is no match.
        """
        try:
            match = re.search(pattern, value)
            if match:
                return match.group(group)
            return None
        except (re.error, IndexError) as e:
            logger.error("Regex apply failed (pattern='%s'): %s", pattern, e)
            return None

    def apply_dict_mapping(self, value: str, mapping: dict) -> str:
        """Map *value* through a dictionary, returning it unchanged on miss.

        Args:
            value: The key to look up.
            mapping: A ``{source: target}`` mapping dictionary.

        Returns:
            The mapped value if the key exists, otherwise the original value.
        """
        return mapping.get(value, value)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_number(value: Any) -> Any:
        """Convert value to a number. Returns int when the value is a whole
        number written without a decimal point, float otherwise.

        Medical semantics matter: ``37.0`` (one decimal place, measured as
        exactly 37.0℃) is kept as ``37.0`` (float), while ``37`` (no decimal)
        becomes ``37`` (int).  This preserves the precision intent of the
        original measurement."""
        try:
            s = str(value).strip()
            f = float(s)
            # If the original string contains a decimal point, keep as float
            # to preserve precision semantics (37.0 ≠ 37 in medical context).
            if "." in s:
                return f
            # No decimal point → return int if representable.
            i = int(f)
            if f == i:
                return i
            return f
        except (ValueError, TypeError):
            logger.warning("Cannot convert '%s' to number", value)
            return None

    @staticmethod
    def _convert_java_date_format(java_format: str) -> str:
        """Convert Java date format (yyyy-MM-dd) to Python format (%Y-%m-%d)."""
        mapping = {
            "yyyy": "%Y", "yy": "%y",
            "MM": "%m", "dd": "%d",
            "HH": "%H", "mm": "%M", "ss": "%S",
            "SSS": "%f",
        }
        result = java_format
        for java, python in mapping.items():
            result = result.replace(java, python)
        return result

    @staticmethod
    def _to_datetime(value: Any, date_format: Optional[str] = None) -> Optional[datetime]:
        # Fast path -- already a datetime object.
        if isinstance(value, datetime):
            return value

        value_str = str(value).strip()

        # Explicit format supplied -- convert Java format to Python if needed.
        if date_format:
            py_format = ValueParser._convert_java_date_format(date_format)
            try:
                return datetime.strptime(value_str, py_format)
            except ValueError as e:
                logger.warning("strptime failed for '%s' with format '%s' (py: '%s'): %s", value_str, date_format, py_format, e)
                return None

        # Fallback to dateutil for flexible parsing.
        try:
            from dateutil.parser import parse as dateutil_parse

            return dateutil_parse(value_str)
        except (ImportError, ValueError) as e:
            logger.warning("dateutil parse failed for '%s': %s", value_str, e)
            return None

    @staticmethod
    def _to_boolean(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        truthy = {"true", "1", "yes", "on", "y", "t"}
        return str(value).strip().lower() in truthy
