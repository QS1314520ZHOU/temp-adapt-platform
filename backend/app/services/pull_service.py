"""HTTP pull service for fetching data from vendor APIs."""
import logging
from typing import Optional

import httpx

from app.database import Database
from app.services.transform_service import TransformService

logger = logging.getLogger(__name__)


class PullService:
    """Fetch data from vendors via HTTP pull and trigger transformation."""

    def __init__(self) -> None:
        self._transform_service = TransformService()

    def pull_from_vendor(self, vendor_code: str) -> dict:
        """Manually trigger a data pull for a vendor.

        Steps:
            1. Load vendor and access configs
            2. Execute the HTTP pull
            3. Call transform_and_save on the fetched data

        Returns:
            {"success": bool, "vendorCode": str, "result": dict, "error": str}
        """
        # Validate vendor exists and is enabled
        vendor_col = Database.get_collection("vendor_configs")
        vendor = vendor_col.find_one({"vendorCode": vendor_code})
        if not vendor:
            return {"success": False, "vendorCode": vendor_code, "error": f"Vendor '{vendor_code}' not found"}
        if not vendor.get("enabled", True):
            return {"success": False, "vendorCode": vendor_code, "error": f"Vendor '{vendor_code}' is disabled"}

        # Load access config
        access_col = Database.get_collection("access_configs")
        access_config = access_col.find_one({"vendorCode": vendor_code})
        if not access_config:
            return {"success": False, "vendorCode": vendor_code, "error": f"No access config for vendor '{vendor_code}'"}

        if access_config.get("accessType") != "http_pull":
            return {"success": False, "vendorCode": vendor_code, "error": "Vendor access type is not http_pull"}

        try:
            raw_data = self._execute_pull(vendor_code)
        except Exception as e:
            logger.exception("Pull failed for vendor '%s'", vendor_code)
            return {"success": False, "vendorCode": vendor_code, "error": str(e)}

        # Transform the fetched data
        result = self._transform_service.transform_and_save(
            vendor_code=vendor_code,
            raw_data=raw_data,
            access_type="http_pull",
        )

        return {"success": result.get("success", False), "vendorCode": vendor_code, "result": result}

    def _execute_pull(self, vendor_code: str) -> str:
        """Execute the HTTP pull for a vendor and return the raw response body.

        Args:
            vendor_code: The vendor code whose pull config to use.

        Returns:
            The raw response body as a string.

        Raises:
            ValueError: If no pull config is found.
            httpx.HTTPError: On HTTP errors.
        """
        access_col = Database.get_collection("access_configs")
        access_config = access_col.find_one({"vendorCode": vendor_code})
        if not access_config:
            raise ValueError(f"No access config for vendor '{vendor_code}'")

        pull_cfg = access_config.get("httpPullConfig") or {}
        url = pull_cfg.get("url", "")
        method = pull_cfg.get("method", "GET").upper()
        headers = pull_cfg.get("headers") or {}
        body = pull_cfg.get("body")
        timeout = pull_cfg.get("timeout", 60)

        logger.info("Pulling data from vendor '%s': %s %s", vendor_code, method, url)

        with httpx.Client(timeout=timeout) as client:
            if method == "POST":
                resp = client.post(url, headers=headers, content=body)
            else:
                resp = client.get(url, headers=headers)

        resp.raise_for_status()
        logger.info("Pull succeeded for vendor '%s': %d bytes", vendor_code, len(resp.text))
        return resp.text
