import logging
from typing import Optional

from lxml import etree

logger = logging.getLogger(__name__)


class XPathExtractor:
    """Extract values from XML data using XPath expressions."""

    def extract_from_string(
        self,
        xml_string: str,
        xpath: str,
        namespaces: Optional[dict] = None,
    ) -> list:
        """Parse an XML string and extract nodes matching an XPath expression.

        Args:
            xml_string: Raw XML content as a string.
            xpath: An XPath expression (e.g. "//record/item").
            namespaces: Optional dict of namespace prefixes to URIs
                        (e.g. {"ns": "http://example.com/ns"}).

        Returns:
            A list of matching ``lxml.etree._Element`` nodes.
            Returns an empty list on parse or evaluation errors.
        """
        try:
            root = etree.fromstring(xml_string.encode("utf-8") if isinstance(xml_string, str) else xml_string)
            results = root.xpath(xpath, namespaces=namespaces or {})
            if isinstance(results, list):
                return results
            # XPath can return a string/number for some expressions; wrap it.
            return [results]
        except etree.XMLSyntaxError as e:
            logger.error("XML syntax error while parsing input: %s", e)
            return []
        except Exception as e:
            logger.error("XPath extract failed for path '%s': %s", xpath, e)
            return []

    def extract_from_node(
        self,
        node,
        xpath: str,
        namespaces: Optional[dict] = None,
    ) -> list:
        """Extract nodes matching an XPath expression from an existing lxml node.

        Unlike :meth:`extract_from_string`, this does **not** re-parse XML;
        it operates directly on the given node, avoiding the bug of passing
        an empty string to ``etree.fromstring``.

        Args:
            node: An ``lxml.etree._Element`` node.
            xpath: An XPath expression relative to *node*.
            namespaces: Optional dict of namespace prefixes to URIs.

        Returns:
            A list of matching ``lxml.etree._Element`` nodes.
        """
        try:
            results = node.xpath(xpath, namespaces=namespaces or {})
            if isinstance(results, list):
                return results
            return [results]
        except Exception as e:
            logger.error("XPath extract_from_node failed for path '%s': %s", xpath, e)
            return []

    def extract_text(self, node, xpath: str) -> Optional[str]:
        """Extract the text content from an lxml node using an XPath expression.

        Args:
            node: An ``lxml.etree._Element`` node.
            xpath: An XPath expression relative to *node*.

        Returns:
            The text content of the first matching sub-element, or None.
        """
        try:
            results = node.xpath(xpath)
            if not results:
                return None
            first = results[0]
            # If the result is an element, return its text.
            if hasattr(first, "text"):
                return first.text
            # If it is already a string (e.g. from text() or @attr), return directly.
            return str(first)
        except Exception as e:
            logger.error("extract_text failed for xpath '%s': %s", xpath, e)
            return None
