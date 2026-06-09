"""SmartCare MongoDB datasource management service."""
import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pymongo import MongoClient

from app.database import Database
from app.models.domain import SmartCareDatasourceConfig, SmartCareFieldMapping
from app.utils.encrypt import decrypt, encrypt

logger = logging.getLogger(__name__)

DATASOURCE_COLLECTION = "smartcare_datasource_config"
FIELD_MAPPING_COLLECTION = "smartcare_field_mapping"


class SmartCareService:
    """Manage SmartCare MongoDB connections, field mappings, and patient data queries."""

    # ------------------------------------------------------------------
    # Datasource config
    # ------------------------------------------------------------------

    def save_datasource(self, data: dict) -> dict:
        """Insert or update a SmartCare datasource config.

        Accepts either:
        - ``mongoUri`` directly, or
        - Separate fields: ``host``, ``port``, ``database``, ``username``,
          ``password`` (assembled into a URI internally).

        Returns:
            The saved datasource document.
        """
        col = Database.get_collection(DATASOURCE_COLLECTION)
        now = datetime.now(timezone.utc)

        # Build URI from separate fields if mongoUri not provided
        mongo_uri = data.get("mongoUri", "")
        if not mongo_uri and data.get("host"):
            mongo_uri = self._build_mongo_uri(
                host=data.get("host", "localhost"),
                port=data.get("port", 27017),
                database=data.get("database", "SmartCare"),
                username=data.get("username", ""),
                password=data.get("password", ""),
            )

        # Encrypt the URI
        mongo_uri_encrypted = data.get("mongoUri_encrypted", "")
        if mongo_uri:
            mongo_uri_encrypted = encrypt(mongo_uri)

        existing = col.find_one({"name": data["name"]}) if "name" in data else None
        ds_id = data.get("id") or data.get("_id")
        if ds_id:
            existing = col.find_one({"_id": ds_id})

        if existing:
            update_fields: dict = {
                "name": data.get("name", existing.get("name")),
                "host": data.get("host", existing.get("host")),
                "port": data.get("port", existing.get("port", 27017)),
                "username": data.get("username", existing.get("username")),
                "mongoUri_encrypted": mongo_uri_encrypted or existing.get("mongoUri_encrypted"),
                "database": data.get("database", existing.get("database", "SmartCare")),
                "collections": data.get("collections", existing.get("collections", {})),
                "enabled": data.get("enabled", True),
                "updatedAt": now,
            }
            # Only update password if provided
            if data.get("password"):
                update_fields["password_encrypted"] = encrypt(data["password"])
            col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
            doc = col.find_one({"_id": existing["_id"]})
        else:
            ds = SmartCareDatasourceConfig(
                name=data["name"],
                mongoUri_encrypted=mongo_uri_encrypted,
                database=data.get("database", "SmartCare"),
                collections=data.get("collections", {}),
                enabled=data.get("enabled", True),
                createdAt=now,
                updatedAt=now,
            )
            doc = ds.to_dict()
            # Store connection fields for display/re-edit
            doc["host"] = data.get("host", "")
            doc["port"] = data.get("port", 27017)
            doc["username"] = data.get("username", "")
            if data.get("password"):
                doc["password_encrypted"] = encrypt(data["password"])
            col.insert_one(doc)

        logger.info("Saved SmartCare datasource '%s'", doc.get("name"))
        return self._decrypt_doc_uri(doc)

    @staticmethod
    def _build_mongo_uri(host: str, port: int, database: str, username: str = "", password: str = "") -> str:
        """Build a MongoDB connection URI from separate fields."""
        if username and password:
            from urllib.parse import quote_plus
            user = quote_plus(username)
            pwd = quote_plus(password)
            return f"mongodb://{user}:{pwd}@{host}:{port}/{database}"
        return f"mongodb://{host}:{port}/{database}"

    def get_datasource(self, datasource_id: Optional[str] = None) -> dict | list:
        """Return one datasource (by ID) or all datasources.

        Args:
            datasource_id: Optional ObjectId string.  When omitted, all
                datasources are returned.

        Returns:
            A single datasource dict or a list of dicts.
        """
        col = Database.get_collection(DATASOURCE_COLLECTION)

        if datasource_id:
            doc = col.find_one({"_id": datasource_id})
            if not doc:
                return {}
            return self._decrypt_doc_uri(doc)

        docs = list(col.find().sort("createdAt", -1))
        return [self._decrypt_doc_uri(d) for d in docs]

    def test_connection(self, datasource_id: str) -> dict:
        """Test connectivity to a SmartCare datasource by ID.

        Returns:
            {"success": bool, "message": str}
        """
        col = Database.get_collection(DATASOURCE_COLLECTION)
        doc = col.find_one({"_id": datasource_id})
        if not doc:
            return {"success": False, "message": f"Datasource '{datasource_id}' not found"}

        uri = decrypt(doc.get("mongoUri_encrypted", ""))
        if not uri:
            return {"success": False, "message": "MongoDB URI is empty"}

        return self._do_test_connection(uri, doc.get("database", "SmartCare"))

    def test_connection_direct(self, data: dict) -> dict:
        """Test connectivity using direct connection parameters.

        Accepts either ``mongoUri`` or separate ``host``/``port``/``database``/
        ``username``/``password`` fields.

        Returns:
            {"success": bool, "message": str}
        """
        mongo_uri = data.get("mongoUri", "")
        if not mongo_uri and data.get("host"):
            mongo_uri = self._build_mongo_uri(
                host=data.get("host", "localhost"),
                port=data.get("port", 27017),
                database=data.get("database", "SmartCare"),
                username=data.get("username", ""),
                password=data.get("password", ""),
            )

        if not mongo_uri:
            return {"success": False, "message": "未提供连接信息"}

        db_name = data.get("database", "SmartCare")
        return self._do_test_connection(mongo_uri, db_name)

    def _do_test_connection(self, uri: str, db_name: str) -> dict:
        """Low-level connection test."""
        try:
            client: MongoClient = Database.get_smartcare_client(uri)
            client.admin.command("ping")
            db = client[db_name]
            collection_names = db.list_collection_names()
            return {
                "success": True,
                "message": f"连接成功，数据库 '{db_name}'，共 {len(collection_names)} 个集合",
                "collections": collection_names,
            }
        except Exception as e:
            logger.exception("SmartCare connection test failed")
            return {"success": False, "message": f"连接失败: {e}"}

    # ------------------------------------------------------------------
    # Field mapping
    # ------------------------------------------------------------------

    def save_field_mapping(self, data: dict) -> dict:
        """Insert or update a field mapping for a SmartCare collection.

        Returns:
            The saved field mapping document.
        """
        col = Database.get_collection(FIELD_MAPPING_COLLECTION)
        now = datetime.now(timezone.utc)

        ds_id = data.get("datasourceId", "")
        coll_name = data.get("collectionName", "")

        existing = col.find_one({"datasourceId": ds_id, "collectionName": coll_name})

        if existing:
            col.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "fieldMappings": data.get("fieldMappings", {}),
                    "updatedAt": now,
                }},
            )
            return col.find_one({"_id": existing["_id"]})

        mapping = SmartCareFieldMapping(
            collectionName=coll_name,
            datasourceId=ds_id,
            fieldMappings=data.get("fieldMappings", {}),
            createdAt=now,
            updatedAt=now,
        )
        doc = mapping.to_dict()
        col.insert_one(doc)
        return doc

    def get_field_mapping(self, collection_name: str, datasource_id: Optional[str] = None) -> Optional[dict]:
        """Return the field mapping for a collection, optionally filtered by datasource.

        Returns:
            The field mapping document, or None.
        """
        col = Database.get_collection(FIELD_MAPPING_COLLECTION)
        query: dict = {"collectionName": collection_name}
        if datasource_id:
            query["datasourceId"] = datasource_id
        return col.find_one(query)

    # ------------------------------------------------------------------
    # SmartCare data access helpers
    # ------------------------------------------------------------------

    def _get_sc_db(self, datasource_id: str):
        """Return a pymongo Database handle for the SmartCare datasource.

        Raises:
            ValueError: If the datasource is not found or URI is missing.
        """
        col = Database.get_collection(DATASOURCE_COLLECTION)
        doc = col.find_one({"_id": datasource_id})
        if not doc:
            raise ValueError(f"Datasource '{datasource_id}' not found")

        uri = decrypt(doc.get("mongoUri_encrypted", ""))
        if not uri:
            raise ValueError(f"MongoDB URI is empty for datasource '{datasource_id}'")

        client: MongoClient = Database.get_smartcare_client(uri)
        db_name = doc.get("database", "SmartCare")
        return client[db_name]

    def _get_sc_collection(self, datasource_id: str, collection_name: str):
        """Return a pymongo Collection handle for a SmartCare collection."""
        db = self._get_sc_db(datasource_id)
        return db[collection_name]

    def _apply_field_mapping(self, doc: dict, field_mappings: dict, reverse: bool = False) -> dict:
        """Translate field names using a mapping dict.

        Args:
            doc: The document to translate.
            field_mappings: A dict ``{standardName: actualName}`` or
                ``{actualName: standardName}`` depending on ``reverse``.
            reverse: If True, map from actual -> standard; otherwise
                standard -> actual.

        Returns:
            A new dict with translated keys.
        """
        if not field_mappings:
            return doc

        if reverse:
            # actual -> standard
            reverse_map = {v: k for k, v in field_mappings.items()}
            return {reverse_map.get(k, k): v for k, v in doc.items()}

        # standard -> actual
        return {field_mappings.get(k, k): v for k, v in doc.items()}

    def _get_field_mappings(self, datasource_id: str, collection_name: str) -> dict:
        """Retrieve field mappings for a SmartCare collection.

        Returns:
            A dict ``{standardName: actualFieldName}`` or empty dict.
        """
        mapping_doc = self.get_field_mapping(collection_name, datasource_id)
        if mapping_doc:
            return mapping_doc.get("fieldMappings", {})
        return {}

    # ------------------------------------------------------------------
    # ConfigParam
    # ------------------------------------------------------------------

    def sync_config_params(self, datasource_id: str) -> dict:
        """Read configParam documents from SmartCare and return them.

        Returns:
            {"success": bool, "data": list, "count": int, "error": str}
        """
        try:
            field_map = self._get_field_mappings(datasource_id, "configParam")
            coll = self._get_sc_collection(datasource_id, "configParam")

            docs = list(coll.find())
            result: list[dict] = []
            for doc in docs:
                doc.pop("_id", None)
                mapped = self._apply_field_mapping(doc, field_map, reverse=True)
                result.append(mapped)

            return {"success": True, "data": result, "count": len(result)}
        except Exception as e:
            logger.exception("Failed to sync configParam for datasource '%s'", datasource_id)
            return {"success": False, "data": [], "count": 0, "error": str(e)}

    def get_config_param_list(self, datasource_id: str) -> list:
        """Return the list of configParam documents from SmartCare.

        Returns:
            A list of configParam dicts (field names translated to standard names).
        """
        field_map = self._get_field_mappings(datasource_id, "configParam")
        coll = self._get_sc_collection(datasource_id, "configParam")

        docs = list(coll.find())
        result: list[dict] = []
        for doc in docs:
            doc.pop("_id", None)
            mapped = self._apply_field_mapping(doc, field_map, reverse=True)
            result.append(mapped)
        return result

    # ------------------------------------------------------------------
    # Patient
    # ------------------------------------------------------------------

    def get_patient(
        self,
        datasource_id: str,
        patient_id: Optional[str] = None,
        his_pid: Optional[str] = None,
        mrn: Optional[str] = None,
    ) -> Optional[dict]:
        """Look up a single patient by one of the provided identifiers.

        Uses field mappings to translate standard field names to actual
        SmartCare field names before querying.

        Returns:
            The patient document (standard field names), or None.
        """
        field_map = self._get_field_mappings(datasource_id, "patient")
        coll = self._get_sc_collection(datasource_id, "patient")

        # Build query using actual field names
        query: dict = {}
        if patient_id:
            actual_key = field_map.get("patientId", "patientId")
            query[actual_key] = patient_id
        elif his_pid:
            actual_key = field_map.get("hisPid", "hisPid")
            query[actual_key] = his_pid
        elif mrn:
            actual_key = field_map.get("mrn", "mrn")
            query[actual_key] = mrn
        else:
            return None

        doc = coll.find_one(query)
        if not doc:
            return None

        doc.pop("_id", None)
        return self._apply_field_mapping(doc, field_map, reverse=True)

    def search_patients(
        self,
        datasource_id: str,
        keyword: Optional[str] = None,
        ward_code: Optional[str] = None,
        status: str = "active",
    ) -> list:
        """Search patients by keyword, ward, and status.

        Returns:
            A list of patient docs (standard field names).
        """
        field_map = self._get_field_mappings(datasource_id, "patient")
        coll = self._get_sc_collection(datasource_id, "patient")

        query: dict = {}

        if status:
            actual_key = field_map.get("status", "status")
            query[actual_key] = status

        if ward_code:
            actual_key = field_map.get("wardCode", "wardCode")
            query[actual_key] = ward_code

        if keyword:
            # Search across patientName and patientId
            name_key = field_map.get("patientName", "patientName")
            id_key = field_map.get("patientId", "patientId")
            query["$or"] = [
                {name_key: {"$regex": keyword, "$options": "i"}},
                {id_key: {"$regex": keyword, "$options": "i"}},
            ]

        docs = list(coll.find(query).limit(200))
        result: list[dict] = []
        for doc in docs:
            doc.pop("_id", None)
            result.append(self._apply_field_mapping(doc, field_map, reverse=True))
        return result

    # ------------------------------------------------------------------
    # Bedside records
    # ------------------------------------------------------------------

    def get_bedside_records(
        self,
        datasource_id: str,
        patient_id: str,
        start_time,
        end_time,
        param_codes: Optional[list] = None,
    ) -> list:
        """Query bedside records for a patient within a time range.

        Uses field mappings to translate standard field names to actual
        SmartCare field names.

        Returns:
            A list of bedside record dicts (standard field names).
        """
        field_map = self._get_field_mappings(datasource_id, "bedside")
        coll = self._get_sc_collection(datasource_id, "bedside")

        # Map standard field names to actual field names
        patient_key = field_map.get("patientId", "patientId")
        time_key = field_map.get("recordTime", "recordTime")
        code_key = field_map.get("paramCode", "paramCode")

        query: dict = {
            patient_key: patient_id,
            time_key: {"$gte": start_time, "$lte": end_time},
        }

        if param_codes:
            query[code_key] = {"$in": param_codes}

        docs = list(coll.find(query).sort(time_key, 1))
        result: list[dict] = []
        for doc in docs:
            doc.pop("_id", None)
            result.append(self._apply_field_mapping(doc, field_map, reverse=True))
        return result

    # ------------------------------------------------------------------
    # Bedside sync support (editTime-based incremental)
    # ------------------------------------------------------------------

    def get_bedside_modified(
        self,
        datasource_id: str,
        since,
        ward_codes: Optional[list] = None,
        patient_ids: Optional[list] = None,
        time_start=None,
        time_end=None,
        limit: int = 5000,
    ) -> list:
        """Query bedside records modified after *since* (editTime-based).

        This is the core method for incremental sync: it returns records
        whose ``editTime`` is newer than the last sync checkpoint, optionally
        filtered by bedside ``time`` range and ward.

        Args:
            datasource_id: SmartCare datasource ID.
            since: Only return records with editTime >= this value.
            ward_codes: Optional list of ward codes to filter.
            patient_ids: Optional list of patient IDs to filter.
            time_start: Optional bedside time range start (UTC+8).
            time_end: Optional bedside time range end (UTC+8).
            limit: Max records to return.

        Returns:
            List of bedside record dicts with standard field names.
        """
        field_map = self._get_field_mappings(datasource_id, "bedside")
        coll = self._get_sc_collection(datasource_id, "bedside")

        # Map standard → actual field names
        edit_key = field_map.get("editTime", "editTime")
        time_key = field_map.get("recordTime", "recordTime")  # bedside time
        patient_key = field_map.get("patientId", "patientId")
        ward_key = field_map.get("wardCode", "wardCode")

        query: dict = {edit_key: {"$gte": since}}

        # Optional: filter by bedside time range (for full sync at specific hours)
        if time_start or time_end:
            time_filter: dict = {}
            if time_start:
                time_filter["$gte"] = time_start
            if time_end:
                time_filter["$lte"] = time_end
            query[time_key] = time_filter

        if patient_ids:
            query[patient_key] = {"$in": patient_ids}

        if ward_codes:
            query[ward_key] = {"$in": ward_codes}

        docs = list(coll.find(query).sort(edit_key, 1).limit(limit))
        result: list[dict] = []
        for doc in docs:
            doc.pop("_id", None)
            result.append(self._apply_field_mapping(doc, field_map, reverse=True))
        return result

    def get_latest_edit_time(self, datasource_id: str) -> Optional[datetime]:
        """Return the most recent editTime across all bedside records.

        Used to set the initial sync checkpoint.
        """
        field_map = self._get_field_mappings(datasource_id, "bedside")
        coll = self._get_sc_collection(datasource_id, "bedside")
        edit_key = field_map.get("editTime", "editTime")

        doc = coll.find_one(sort=[(edit_key, -1)])
        if doc and edit_key in doc:
            return doc[edit_key]
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _decrypt_doc_uri(self, doc: dict) -> dict:
        """Add a decrypted ``mongoUri`` field to a datasource doc for the caller.
        Also ensure host/port fields are present for the frontend."""
        doc = dict(doc)
        encrypted = doc.get("mongoUri_encrypted", "")
        doc["mongoUri"] = decrypt(encrypted) if encrypted else ""
        # Ensure host/port are present (for docs saved before this field existed)
        if "host" not in doc and doc["mongoUri"]:
            # Try to extract host from URI
            try:
                from urllib.parse import urlparse
                parsed = urlparse(doc["mongoUri"].replace("mongodb+srv", "mongodb"))
                doc["host"] = parsed.hostname or ""
                doc["port"] = parsed.port or 27017
                doc["username"] = parsed.username or ""
            except Exception:
                pass
        doc.setdefault("host", "")
        doc.setdefault("port", 27017)
        doc.setdefault("username", "")
        # Never expose password in response
        doc.pop("password_encrypted", None)
        return doc
