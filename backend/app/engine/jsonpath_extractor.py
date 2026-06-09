import logging
from typing import Any

from jsonpath_ng.ext import parse as jsonpath_parse

logger = logging.getLogger(__name__)


class JsonPathExtractor:
    """Extract values from JSON data using JsonPath expressions."""

    def extract(self, data: dict, path: str) -> list:
        """Extract all matching values from JSON data using a JsonPath expression.

        Args:
            data: The JSON data (dict) to search.
            path: A JsonPath expression string (e.g. "$.store.book[*].author").

        Returns:
            A list of all matched values. Returns an empty list if no match.
        """
        try:
            expression = jsonpath_parse(path)
            matches = expression.find(data)
            return [match.value for match in matches]
        except Exception as e:
            logger.error("JsonPath extract failed for path '%s': %s", path, e)
            return []

    def extract_single(self, data: dict, path: str) -> Any:
        """Extract a single value from JSON data using a JsonPath expression.

        Args:
            data: The JSON data (dict) to search.
            path: A JsonPath expression string.

        Returns:
            The first matched value, or None if no match is found.
        """
        results = self.extract(data, path)
        return results[0] if results else None

    def evaluate_path(self, data: dict, path: str) -> list:
        """Evaluate a JsonPath expression and return all matches as a list.

        This is functionally equivalent to ``extract`` but kept as a separate
        entry-point so callers can choose the intent that reads most clearly.

        Args:
            data: The JSON data (dict) to evaluate against.
            path: A JsonPath expression string.

        Returns:
            A list of all matched values (empty list on no match).
        """
        return self.extract(data, path)
