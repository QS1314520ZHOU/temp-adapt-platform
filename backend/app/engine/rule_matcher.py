import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class RuleMatcher:
    """Match incoming data items against a prioritised list of mapping rules.

    Each rule dict is expected to contain at least::

        {
            "matchField": "item_name",
            "matchType": "equals" | "contains" | "regex" | "starts_with" | "in_list",
            "matchValue": "temperature",
            "priority": 1,
            ...   # additional fields are preserved and returned on match
        }

    Rules are sorted by ``priority`` (ascending -- lower number = higher
    priority).  The first matching rule wins.

    Regex patterns are pre-compiled at init time and cached on the rule
    dict (``rule["_compiled_re"]``) to avoid repeated compilation on every
    match call.
    """

    def __init__(self, rules: list[dict]) -> None:
        self.rules: list[dict] = sorted(rules, key=lambda r: r.get("priority", 9999))
        # Pre-compile regex patterns to avoid re.compile on every match.
        for rule in self.rules:
            if rule.get("matchType") == "regex" and rule.get("matchValue"):
                try:
                    rule["_compiled_re"] = re.compile(str(rule["matchValue"]))
                except re.error as e:
                    logger.error("Invalid regex pattern '%s' in rule %s: %s", rule["matchValue"], rule, e)
                    rule["_compiled_re"] = None

    def match(self, item: dict) -> Optional[dict]:
        """Try to match *item* against every rule, in priority order.

        Args:
            item: The data item (dict) to evaluate.

        Returns:
            The first matching rule dict, or ``None`` if no rule matches.
        """
        for rule in self.rules:
            if self._evaluate_rule(item, rule):
                return rule
        return None

    def match_all(self, items: list[dict]) -> tuple[list[dict], list[dict]]:
        """Match a list of items against the rules.

        Args:
            items: A list of data-item dicts.

        Returns:
            A 2-tuple ``(matched, unmatched)`` where *matched* contains dicts
            of ``{"item": <item>, "rule": <rule>}`` and *unmatched* contains
            the raw item dicts that did not match any rule.
        """
        matched: list[dict] = []
        unmatched: list[dict] = []

        for item in items:
            rule = self.match(item)
            if rule is not None:
                matched.append({"item": item, "rule": rule})
            else:
                unmatched.append(item)

        return matched, unmatched

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _evaluate_rule(self, item: dict, rule: dict) -> bool:
        """Return True if *item* satisfies the condition described by *rule*."""
        match_field = rule.get("matchField")
        match_type = rule.get("matchType")
        match_value = rule.get("matchValue")

        if not match_field or not match_type:
            logger.warning("Rule is missing matchField or matchType: %s", rule)
            return False

        item_value = item.get(match_field)
        if item_value is None:
            return False

        item_value_str = str(item_value)

        try:
            if match_type in ("equals", "exact"):
                return item_value_str == str(match_value)

            if match_type == "contains":
                return str(match_value) in item_value_str

            if match_type == "regex":
                compiled = rule.get("_compiled_re")
                if compiled is None:
                    return False
                return bool(compiled.search(item_value_str))

            if match_type == "starts_with":
                return item_value_str.startswith(str(match_value))

            if match_type == "in_list":
                # Support list, newline-separated, or comma-separated values.
                # Priority: list > newline > comma.
                # Using newline in the UI lets users include commas in values.
                if isinstance(match_value, list):
                    allowed = [str(v).strip() for v in match_value]
                elif "\n" in str(match_value):
                    allowed = [v.strip() for v in str(match_value).split("\n") if v.strip()]
                else:
                    allowed = [v.strip() for v in str(match_value).split(",")]
                return item_value_str in allowed

        except Exception as e:
            logger.error("Rule evaluation error (rule=%s): %s", rule, e)
            return False

        logger.warning("Unknown matchType '%s' in rule %s", match_type, rule)
        return False
