"""
Domain models for MongoDB documents.
These represent the structure of documents stored in MongoDB collections.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId


def gen_object_id() -> str:
    """Generate a new ObjectId as string."""
    return str(ObjectId())


# ---------------------------------------------------------------------------
# Vendor & Access Configuration
# ---------------------------------------------------------------------------

class VendorConfig:
    """Configuration for a vendor that sends temperature data."""

    def __init__(
        self,
        vendorCode: str,
        vendorName: str,
        id: Optional[str] = None,
        hospitalCode: Optional[str] = None,
        hospitalName: Optional[str] = None,
        enabled: bool = True,
        accessType: str = "http_push",
        description: Optional[str] = None,
        contactInfo: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
        createdBy: Optional[str] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.vendorName = vendorName
        self.hospitalCode = hospitalCode
        self.hospitalName = hospitalName
        self.enabled = enabled
        self.accessType = accessType
        self.description = description
        self.contactInfo = contactInfo
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()
        self.createdBy = createdBy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "vendorName": self.vendorName,
            "hospitalCode": self.hospitalCode,
            "hospitalName": self.hospitalName,
            "enabled": self.enabled,
            "accessType": self.accessType,
            "description": self.description,
            "contactInfo": self.contactInfo,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
            "createdBy": self.createdBy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VendorConfig":
        return cls(
            id=str(data.get("_id", "")),
            vendorCode=data["vendorCode"],
            vendorName=data["vendorName"],
            hospitalCode=data.get("hospitalCode"),
            hospitalName=data.get("hospitalName"),
            enabled=data.get("enabled", True),
            accessType=data.get("accessType", "http_push"),
            description=data.get("description"),
            contactInfo=data.get("contactInfo"),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
            createdBy=data.get("createdBy"),
        )


class AccessConfig:
    """Access configuration for how a vendor connects."""

    def __init__(
        self,
        vendorCode: str,
        accessType: str,
        id: Optional[str] = None,
        httpPushConfig: Optional[Dict[str, Any]] = None,
        httpPullConfig: Optional[Dict[str, Any]] = None,
        dbViewConfig: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.accessType = accessType
        self.httpPushConfig = httpPushConfig
        self.httpPullConfig = httpPullConfig
        self.dbViewConfig = dbViewConfig
        self.enabled = enabled
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "accessType": self.accessType,
            "httpPushConfig": self.httpPushConfig,
            "httpPullConfig": self.httpPullConfig,
            "dbViewConfig": self.dbViewConfig,
            "enabled": self.enabled,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessConfig":
        return cls(
            id=str(data.get("_id", "")),
            vendorCode=data["vendorCode"],
            accessType=data["accessType"],
            httpPushConfig=data.get("httpPushConfig"),
            httpPullConfig=data.get("httpPullConfig"),
            dbViewConfig=data.get("dbViewConfig"),
            enabled=data.get("enabled", True),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Parser Configuration
# ---------------------------------------------------------------------------

class FieldMapping:
    """A single field mapping entry used inside ParserConfig."""

    def __init__(
        self,
        targetField: str,
        sourcePath: str,
        dataType: str,
        dateFormat: Optional[str] = None,
        required: Optional[bool] = None,
        defaultValue: Optional[str] = None,
    ):
        self.targetField = targetField
        self.sourcePath = sourcePath
        self.dataType = dataType
        self.dateFormat = dateFormat
        self.required = required
        self.defaultValue = defaultValue

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "targetField": self.targetField,
            "sourcePath": self.sourcePath,
            "dataType": self.dataType,
        }
        if self.dateFormat is not None:
            d["dateFormat"] = self.dateFormat
        if self.required is not None:
            d["required"] = self.required
        if self.defaultValue is not None:
            d["defaultValue"] = self.defaultValue
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldMapping":
        return cls(
            targetField=data["targetField"],
            sourcePath=data["sourcePath"],
            dataType=data["dataType"],
            dateFormat=data.get("dateFormat"),
            required=data.get("required"),
            defaultValue=data.get("defaultValue"),
        )


class ParserConfig:
    """Configuration for parsing raw vendor data."""

    def __init__(
        self,
        vendorCode: str,
        recordPath: str,
        id: Optional[str] = None,
        dataFormat: str = "json",
        encoding: str = "UTF-8",
        rootPath: str = "$",
        itemPath: Optional[str] = None,
        recordPathType: str = "jsonpath",
        itemPathType: str = "jsonpath",
        rootFieldMappings: Optional[List[Dict[str, Any]]] = None,
        recordFieldMappings: Optional[List[Dict[str, Any]]] = None,
        itemFieldMappings: Optional[List[Dict[str, Any]]] = None,
        xmlConfig: Optional[Dict[str, Any]] = None,
        sqlConfig: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.dataFormat = dataFormat
        self.encoding = encoding
        self.rootPath = rootPath
        self.recordPath = recordPath
        self.itemPath = itemPath
        self.recordPathType = recordPathType
        self.itemPathType = itemPathType
        self.rootFieldMappings = rootFieldMappings or []
        self.recordFieldMappings = recordFieldMappings or []
        self.itemFieldMappings = itemFieldMappings or []
        self.xmlConfig = xmlConfig
        self.sqlConfig = sqlConfig
        self.enabled = enabled
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "dataFormat": self.dataFormat,
            "encoding": self.encoding,
            "rootPath": self.rootPath,
            "recordPath": self.recordPath,
            "itemPath": self.itemPath,
            "recordPathType": self.recordPathType,
            "itemPathType": self.itemPathType,
            "rootFieldMappings": self.rootFieldMappings,
            "recordFieldMappings": self.recordFieldMappings,
            "itemFieldMappings": self.itemFieldMappings,
            "xmlConfig": self.xmlConfig,
            "sqlConfig": self.sqlConfig,
            "enabled": self.enabled,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParserConfig":
        return cls(
            id=str(data.get("_id", "")),
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
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Item Mapping Rules
# ---------------------------------------------------------------------------

class ItemMappingRule:
    """Rules for mapping raw items to standard temperature item codes."""

    def __init__(
        self,
        vendorCode: str,
        rules: List[Dict[str, Any]],
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.rules = rules
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "rules": self.rules,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemMappingRule":
        return cls(
            id=str(data.get("_id", "")),
            vendorCode=data["vendorCode"],
            rules=data.get("rules", []),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Raw & Temperature Records
# ---------------------------------------------------------------------------

class RawRecord:
    """A raw record received from a vendor before transformation."""

    def __init__(
        self,
        vendorCode: Optional[str] = None,
        accessType: Optional[str] = None,
        batchId: Optional[str] = None,
        rawContent: Optional[str] = None,
        contentType: Optional[str] = None,
        sourceIp: Optional[str] = None,
        status: str = "pending",
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.accessType = accessType
        self.batchId = batchId
        self.rawContent = rawContent
        self.contentType = contentType
        self.sourceIp = sourceIp
        self.status = status
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "accessType": self.accessType,
            "batchId": self.batchId,
            "rawContent": self.rawContent,
            "contentType": self.contentType,
            "sourceIp": self.sourceIp,
            "status": self.status,
            "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RawRecord":
        return cls(
            id=str(data.get("_id", "")),
            vendorCode=data.get("vendorCode"),
            accessType=data.get("accessType"),
            batchId=data.get("batchId"),
            rawContent=data.get("rawContent"),
            contentType=data.get("contentType"),
            sourceIp=data.get("sourceIp"),
            status=data.get("status", "pending"),
            createdAt=data.get("createdAt"),
        )


class TemperatureItem:
    """An individual temperature/vital-sign item embedded in a TemperatureRecord."""

    def __init__(
        self,
        code: Optional[str] = None,
        name: Optional[str] = None,
        value: Any = None,
        unit: Optional[str] = None,
        source: Optional[str] = None,
        rawItemId: Optional[str] = None,
        rawItemName: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        statTimeRange: Optional[Dict[str, Any]] = None,
        matched: bool = True,
    ):
        self.code = code
        self.name = name
        self.value = value
        self.unit = unit
        self.source = source
        self.rawItemId = rawItemId
        self.rawItemName = rawItemName
        self.extra = extra
        self.statTimeRange = statTimeRange
        self.matched = matched

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "code": self.code,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "rawItemId": self.rawItemId,
            "rawItemName": self.rawItemName,
            "matched": self.matched,
        }
        if self.extra is not None:
            d["extra"] = self.extra
        if self.statTimeRange is not None:
            d["statTimeRange"] = self.statTimeRange
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemperatureItem":
        return cls(
            code=data.get("code"),
            name=data.get("name"),
            value=data.get("value"),
            unit=data.get("unit"),
            source=data.get("source"),
            rawItemId=data.get("rawItemId"),
            rawItemName=data.get("rawItemName"),
            extra=data.get("extra"),
            statTimeRange=data.get("statTimeRange"),
            matched=data.get("matched", True),
        )


class TemperatureRecord:
    """A transformed temperature record ready for downstream consumption."""

    def __init__(
        self,
        patientId: str,
        id: Optional[str] = None,
        vendorCode: Optional[str] = None,
        batchId: Optional[str] = None,
        rawRecordId: Optional[str] = None,
        visitNo: Optional[str] = None,
        patientVisitId: Optional[str] = None,
        wardCode: Optional[str] = None,
        bedNo: Optional[str] = None,
        recordTime: Optional[datetime] = None,
        operatorCode: Optional[str] = None,
        operatorName: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        idempotentKey: Optional[str] = None,
        status: str = "pending",
        source: str = "vendor",
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.batchId = batchId
        self.rawRecordId = rawRecordId
        self.patientId = patientId
        self.visitNo = visitNo
        self.patientVisitId = patientVisitId
        self.wardCode = wardCode
        self.bedNo = bedNo
        self.recordTime = recordTime
        self.operatorCode = operatorCode
        self.operatorName = operatorName
        self.items = items or []
        self.idempotentKey = idempotentKey
        self.status = status
        self.source = source
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "batchId": self.batchId,
            "rawRecordId": self.rawRecordId,
            "patientId": self.patientId,
            "visitNo": self.visitNo,
            "patientVisitId": self.patientVisitId,
            "wardCode": self.wardCode,
            "bedNo": self.bedNo,
            "recordTime": self.recordTime,
            "operatorCode": self.operatorCode,
            "operatorName": self.operatorName,
            "items": self.items,
            "idempotentKey": self.idempotentKey,
            "status": self.status,
            "source": self.source,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemperatureRecord":
        return cls(
            id=str(data.get("_id", "")),
            vendorCode=data.get("vendorCode"),
            batchId=data.get("batchId"),
            rawRecordId=data.get("rawRecordId"),
            patientId=data["patientId"],
            visitNo=data.get("visitNo"),
            patientVisitId=data.get("patientVisitId"),
            wardCode=data.get("wardCode"),
            bedNo=data.get("bedNo"),
            recordTime=data.get("recordTime"),
            operatorCode=data.get("operatorCode"),
            operatorName=data.get("operatorName"),
            items=data.get("items", []),
            idempotentKey=data.get("idempotentKey"),
            status=data.get("status", "pending"),
            source=data.get("source", "vendor"),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Unmatched Items
# ---------------------------------------------------------------------------

class UnmatchedItem:
    """A raw item that could not be matched to a known mapping rule."""

    def __init__(
        self,
        id: Optional[str] = None,
        vendorCode: Optional[str] = None,
        rawRecordId: Optional[str] = None,
        batchId: Optional[str] = None,
        patientId: Optional[str] = None,
        recordTime: Optional[datetime] = None,
        itemData: Optional[Dict[str, Any]] = None,
        status: str = "pending",
        resolvedRuleId: Optional[str] = None,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.rawRecordId = rawRecordId
        self.batchId = batchId
        self.patientId = patientId
        self.recordTime = recordTime
        self.itemData = itemData
        self.status = status
        self.resolvedRuleId = resolvedRuleId
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "vendorCode": self.vendorCode,
            "rawRecordId": self.rawRecordId,
            "batchId": self.batchId,
            "patientId": self.patientId,
            "recordTime": self.recordTime,
            "itemData": self.itemData,
            "status": self.status,
            "resolvedRuleId": self.resolvedRuleId,
            "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnmatchedItem":
        return cls(
            id=str(data.get("_id", "")),
            vendorCode=data.get("vendorCode"),
            rawRecordId=data.get("rawRecordId"),
            batchId=data.get("batchId"),
            patientId=data.get("patientId"),
            recordTime=data.get("recordTime"),
            itemData=data.get("itemData"),
            status=data.get("status", "pending"),
            resolvedRuleId=data.get("resolvedRuleId"),
            createdAt=data.get("createdAt"),
        )


# ---------------------------------------------------------------------------
# Transform & Retry
# ---------------------------------------------------------------------------

class TransformLog:
    """Log entry for a batch transform operation."""

    def __init__(
        self,
        batchId: Optional[str] = None,
        vendorCode: Optional[str] = None,
        accessType: Optional[str] = None,
        status: Optional[str] = None,
        totalRecords: int = 0,
        successCount: int = 0,
        failCount: int = 0,
        unmatchedCount: int = 0,
        rawRecordIds: Optional[List[str]] = None,
        temperatureRecordIds: Optional[List[str]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        duration: Optional[int] = None,
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.batchId = batchId
        self.vendorCode = vendorCode
        self.accessType = accessType
        self.status = status
        self.totalRecords = totalRecords
        self.successCount = successCount
        self.failCount = failCount
        self.unmatchedCount = unmatchedCount
        self.rawRecordIds = rawRecordIds or []
        self.temperatureRecordIds = temperatureRecordIds or []
        self.errors = errors or []
        self.duration = duration
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "batchId": self.batchId,
            "vendorCode": self.vendorCode,
            "accessType": self.accessType,
            "status": self.status,
            "totalRecords": self.totalRecords,
            "successCount": self.successCount,
            "failCount": self.failCount,
            "unmatchedCount": self.unmatchedCount,
            "rawRecordIds": self.rawRecordIds,
            "temperatureRecordIds": self.temperatureRecordIds,
            "errors": self.errors,
            "duration": self.duration,
            "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransformLog":
        return cls(
            id=str(data.get("_id", "")),
            batchId=data.get("batchId"),
            vendorCode=data.get("vendorCode"),
            accessType=data.get("accessType"),
            status=data.get("status"),
            totalRecords=data.get("totalRecords", 0),
            successCount=data.get("successCount", 0),
            failCount=data.get("failCount", 0),
            unmatchedCount=data.get("unmatchedCount", 0),
            rawRecordIds=data.get("rawRecordIds", []),
            temperatureRecordIds=data.get("temperatureRecordIds", []),
            errors=data.get("errors", []),
            duration=data.get("duration"),
            createdAt=data.get("createdAt"),
        )


class RetryTask:
    """A task for retrying a failed raw record transformation."""

    def __init__(
        self,
        rawRecordId: Optional[str] = None,
        vendorCode: Optional[str] = None,
        retryCount: int = 0,
        maxRetryCount: int = 5,
        status: str = "pending",
        lastError: Optional[str] = None,
        nextRetryTime: Optional[datetime] = None,
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.rawRecordId = rawRecordId
        self.vendorCode = vendorCode
        self.retryCount = retryCount
        self.maxRetryCount = maxRetryCount
        self.status = status
        self.lastError = lastError
        self.nextRetryTime = nextRetryTime
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "rawRecordId": self.rawRecordId,
            "vendorCode": self.vendorCode,
            "retryCount": self.retryCount,
            "maxRetryCount": self.maxRetryCount,
            "status": self.status,
            "lastError": self.lastError,
            "nextRetryTime": self.nextRetryTime,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RetryTask":
        return cls(
            id=str(data.get("_id", "")),
            rawRecordId=data.get("rawRecordId"),
            vendorCode=data.get("vendorCode"),
            retryCount=data.get("retryCount", 0),
            maxRetryCount=data.get("maxRetryCount", 5),
            status=data.get("status", "pending"),
            lastError=data.get("lastError"),
            nextRetryTime=data.get("nextRetryTime"),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# SmartCare Datasource Configuration
# ---------------------------------------------------------------------------

class SmartCareDatasourceConfig:
    """Configuration for a SmartCare MongoDB datasource."""

    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        mongoUri_encrypted: Optional[str] = None,
        database: str = "SmartCare",
        collections: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        testStatus: Optional[str] = None,
        lastTestTime: Optional[datetime] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.name = name
        self.mongoUri_encrypted = mongoUri_encrypted
        self.database = database
        self.collections = collections or {}
        self.enabled = enabled
        self.testStatus = testStatus
        self.lastTestTime = lastTestTime
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "name": self.name,
            "mongoUri_encrypted": self.mongoUri_encrypted,
            "database": self.database,
            "collections": self.collections,
            "enabled": self.enabled,
            "testStatus": self.testStatus,
            "lastTestTime": self.lastTestTime,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SmartCareDatasourceConfig":
        return cls(
            id=str(data.get("_id", "")),
            name=data["name"],
            mongoUri_encrypted=data.get("mongoUri_encrypted"),
            database=data.get("database", "SmartCare"),
            collections=data.get("collections", {}),
            enabled=data.get("enabled", True),
            testStatus=data.get("testStatus"),
            lastTestTime=data.get("lastTestTime"),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


class SmartCareFieldMapping:
    """Field mapping configuration for a SmartCare collection."""

    def __init__(
        self,
        collectionName: str,
        datasourceId: Optional[str] = None,
        fieldMappings: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.datasourceId = datasourceId
        self.collectionName = collectionName
        self.fieldMappings = fieldMappings or {}
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "datasourceId": self.datasourceId,
            "collectionName": self.collectionName,
            "fieldMappings": self.fieldMappings,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SmartCareFieldMapping":
        return cls(
            id=str(data.get("_id", "")),
            datasourceId=data.get("datasourceId"),
            collectionName=data["collectionName"],
            fieldMappings=data.get("fieldMappings", {}),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Intake/Output Configuration
# ---------------------------------------------------------------------------

class IntakeOutputItemConfig:
    """Configuration for a single intake/output measurement item."""

    def __init__(
        self,
        paramCode: str,
        datasourceId: Optional[str] = None,
        id: Optional[str] = None,
        paramName: Optional[str] = None,
        category: Optional[str] = None,
        subCategory: Optional[str] = None,
        statType: str = "sum",
        unit: Optional[str] = None,
        includeInTotalInput: Optional[bool] = None,
        includeInTotalOutput: Optional[bool] = None,
        enabled: bool = True,
        autoDetected: bool = False,
        calculation: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.datasourceId = datasourceId
        self.paramCode = paramCode
        self.paramName = paramName
        self.category = category
        self.subCategory = subCategory
        self.statType = statType
        self.unit = unit
        self.includeInTotalInput = includeInTotalInput
        self.includeInTotalOutput = includeInTotalOutput
        self.enabled = enabled
        self.autoDetected = autoDetected
        self.calculation = calculation
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "datasourceId": self.datasourceId,
            "paramCode": self.paramCode,
            "paramName": self.paramName,
            "category": self.category,
            "subCategory": self.subCategory,
            "statType": self.statType,
            "unit": self.unit,
            "includeInTotalInput": self.includeInTotalInput,
            "includeInTotalOutput": self.includeInTotalOutput,
            "enabled": self.enabled,
            "autoDetected": self.autoDetected,
            "calculation": self.calculation,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntakeOutputItemConfig":
        return cls(
            id=str(data.get("_id", "")),
            datasourceId=data.get("datasourceId"),
            paramCode=data["paramCode"],
            paramName=data.get("paramName"),
            category=data.get("category"),
            subCategory=data.get("subCategory"),
            statType=data.get("statType", "sum"),
            unit=data.get("unit"),
            includeInTotalInput=data.get("includeInTotalInput"),
            includeInTotalOutput=data.get("includeInTotalOutput"),
            enabled=data.get("enabled", True),
            autoDetected=data.get("autoDetected", False),
            calculation=data.get("calculation"),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
        )


class IntakeOutputStatRule:
    """A rule defining how to compute an intake/output statistic."""

    def __init__(
        self,
        code: str,
        datasourceId: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        subCategory: Optional[str] = None,
        statType: Optional[str] = None,
        timeWindow: Optional[Dict[str, Any]] = None,
        targetItemCode: Optional[str] = None,
        targetItemName: Optional[str] = None,
        unit: Optional[str] = None,
        enabled: bool = True,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.datasourceId = datasourceId
        self.code = code
        self.name = name
        self.category = category
        self.subCategory = subCategory
        self.statType = statType
        self.timeWindow = timeWindow
        self.targetItemCode = targetItemCode
        self.targetItemName = targetItemName
        self.unit = unit
        self.enabled = enabled
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "datasourceId": self.datasourceId,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "subCategory": self.subCategory,
            "statType": self.statType,
            "timeWindow": self.timeWindow,
            "targetItemCode": self.targetItemCode,
            "targetItemName": self.targetItemName,
            "unit": self.unit,
            "enabled": self.enabled,
            "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntakeOutputStatRule":
        return cls(
            id=str(data.get("_id", "")),
            datasourceId=data.get("datasourceId"),
            code=data["code"],
            name=data.get("name"),
            category=data.get("category"),
            subCategory=data.get("subCategory"),
            statType=data.get("statType"),
            timeWindow=data.get("timeWindow"),
            targetItemCode=data.get("targetItemCode"),
            targetItemName=data.get("targetItemName"),
            unit=data.get("unit"),
            enabled=data.get("enabled", True),
            createdAt=data.get("createdAt"),
        )


class IntakeOutputResult:
    """Computed intake/output results for a patient at a point in time."""

    def __init__(
        self,
        datasourceId: Optional[str] = None,
        patientId: Optional[str] = None,
        hisPid: Optional[str] = None,
        mrn: Optional[str] = None,
        patientName: Optional[str] = None,
        bedNo: Optional[str] = None,
        wardCode: Optional[str] = None,
        calcTime: Optional[datetime] = None,
        statTimeRange: Optional[Dict[str, Any]] = None,
        results: Optional[List[Dict[str, Any]]] = None,
        rawBedsideIds: Optional[List[str]] = None,
        status: str = "completed",
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.datasourceId = datasourceId
        self.patientId = patientId
        self.hisPid = hisPid
        self.mrn = mrn
        self.patientName = patientName
        self.bedNo = bedNo
        self.wardCode = wardCode
        self.calcTime = calcTime
        self.statTimeRange = statTimeRange
        self.results = results or []
        self.rawBedsideIds = rawBedsideIds or []
        self.status = status
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "datasourceId": self.datasourceId,
            "patientId": self.patientId,
            "hisPid": self.hisPid,
            "mrn": self.mrn,
            "patientName": self.patientName,
            "bedNo": self.bedNo,
            "wardCode": self.wardCode,
            "calcTime": self.calcTime,
            "statTimeRange": self.statTimeRange,
            "results": self.results,
            "rawBedsideIds": self.rawBedsideIds,
            "status": self.status,
            "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntakeOutputResult":
        return cls(
            id=str(data.get("_id", "")),
            datasourceId=data.get("datasourceId"),
            patientId=data.get("patientId"),
            hisPid=data.get("hisPid"),
            mrn=data.get("mrn"),
            patientName=data.get("patientName"),
            bedNo=data.get("bedNo"),
            wardCode=data.get("wardCode"),
            calcTime=data.get("calcTime"),
            statTimeRange=data.get("statTimeRange"),
            results=data.get("results", []),
            rawBedsideIds=data.get("rawBedsideIds", []),
            status=data.get("status", "completed"),
            createdAt=data.get("createdAt"),
        )


class IntakeOutputUnmatchedItem:
    """A bedside measurement item that could not be matched to a known param code."""

    def __init__(
        self,
        datasourceId: Optional[str] = None,
        patientId: Optional[str] = None,
        bedsideRecordId: Optional[str] = None,
        paramCode: Optional[str] = None,
        paramName: Optional[str] = None,
        strVal: Optional[str] = None,
        time: Optional[datetime] = None,
        status: str = "pending",
        id: Optional[str] = None,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.datasourceId = datasourceId
        self.patientId = patientId
        self.bedsideRecordId = bedsideRecordId
        self.paramCode = paramCode
        self.paramName = paramName
        self.strVal = strVal
        self.time = time
        self.status = status
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "datasourceId": self.datasourceId,
            "patientId": self.patientId,
            "bedsideRecordId": self.bedsideRecordId,
            "paramCode": self.paramCode,
            "paramName": self.paramName,
            "strVal": self.strVal,
            "time": self.time,
            "status": self.status,
            "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntakeOutputUnmatchedItem":
        return cls(
            id=str(data.get("_id", "")),
            datasourceId=data.get("datasourceId"),
            patientId=data.get("patientId"),
            bedsideRecordId=data.get("bedsideRecordId"),
            paramCode=data.get("paramCode"),
            paramName=data.get("paramName"),
            strVal=data.get("strVal"),
            time=data.get("time"),
            status=data.get("status", "pending"),
            createdAt=data.get("createdAt"),
        )


# ---------------------------------------------------------------------------
# Callback Configuration (回传配置)
# ---------------------------------------------------------------------------

class CallbackConfig:
    """Configuration for when/how to send temperature data back to the target system."""

    def __init__(
        self,
        vendorCode: str,
        id: Optional[str] = None,
        enabled: bool = True,
        callbackType: str = "realtime",
        callbackUrl: Optional[str] = None,
        callbackMethod: str = "POST",
        callbackHeaders: Optional[Dict[str, str]] = None,
        callbackFormat: str = "json",
        cronExpression: Optional[str] = None,
        delayMinutes: int = 0,
        includeItems: Optional[List[str]] = None,
        excludeItems: Optional[List[str]] = None,
        retryEnabled: bool = True,
        maxRetryCount: int = 3,
        retryIntervalSeconds: int = 60,
        dataTemplate: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.enabled = enabled
        self.callbackType = callbackType
        self.callbackUrl = callbackUrl
        self.callbackMethod = callbackMethod
        self.callbackHeaders = callbackHeaders or {}
        self.callbackFormat = callbackFormat
        self.cronExpression = cronExpression
        self.delayMinutes = delayMinutes
        self.includeItems = includeItems
        self.excludeItems = excludeItems
        self.retryEnabled = retryEnabled
        self.maxRetryCount = maxRetryCount
        self.retryIntervalSeconds = retryIntervalSeconds
        self.dataTemplate = dataTemplate
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id, "vendorCode": self.vendorCode, "enabled": self.enabled,
            "callbackType": self.callbackType, "callbackUrl": self.callbackUrl,
            "callbackMethod": self.callbackMethod, "callbackHeaders": self.callbackHeaders,
            "callbackFormat": self.callbackFormat, "cronExpression": self.cronExpression,
            "delayMinutes": self.delayMinutes, "includeItems": self.includeItems,
            "excludeItems": self.excludeItems, "retryEnabled": self.retryEnabled,
            "maxRetryCount": self.maxRetryCount, "retryIntervalSeconds": self.retryIntervalSeconds,
            "dataTemplate": self.dataTemplate, "createdAt": self.createdAt, "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallbackConfig":
        return cls(
            id=str(data.get("_id", "")), vendorCode=data["vendorCode"],
            enabled=data.get("enabled", True), callbackType=data.get("callbackType", "realtime"),
            callbackUrl=data.get("callbackUrl"), callbackMethod=data.get("callbackMethod", "POST"),
            callbackHeaders=data.get("callbackHeaders", {}), callbackFormat=data.get("callbackFormat", "json"),
            cronExpression=data.get("cronExpression"), delayMinutes=data.get("delayMinutes", 0),
            includeItems=data.get("includeItems"), excludeItems=data.get("excludeItems"),
            retryEnabled=data.get("retryEnabled", True), maxRetryCount=data.get("maxRetryCount", 3),
            retryIntervalSeconds=data.get("retryIntervalSeconds", 60), dataTemplate=data.get("dataTemplate"),
            createdAt=data.get("createdAt"), updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Sync Task Configuration (同步任务配置)
# ---------------------------------------------------------------------------

class SyncTaskConfig:
    """Configuration for scheduled data synchronization tasks."""

    def __init__(
        self,
        vendorCode: str,
        id: Optional[str] = None,
        enabled: bool = True,
        syncType: str = "pull",
        cronExpression: str = "0 */5 * * *",
        lookbackDays: int = 1,
        syncWindowHours: int = 24,
        batchSize: int = 100,
        wardCodes: Optional[List[str]] = None,
        lastSyncTime: Optional[datetime] = None,
        lastSyncStatus: Optional[str] = None,
        lastSyncCount: int = 0,
        lastError: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.enabled = enabled
        self.syncType = syncType
        self.cronExpression = cronExpression
        self.lookbackDays = lookbackDays
        self.syncWindowHours = syncWindowHours
        self.batchSize = batchSize
        self.wardCodes = wardCodes or []
        self.lastSyncTime = lastSyncTime
        self.lastSyncStatus = lastSyncStatus
        self.lastSyncCount = lastSyncCount
        self.lastError = lastError
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id, "vendorCode": self.vendorCode, "enabled": self.enabled,
            "syncType": self.syncType, "cronExpression": self.cronExpression,
            "lookbackDays": self.lookbackDays, "syncWindowHours": self.syncWindowHours,
            "batchSize": self.batchSize, "wardCodes": self.wardCodes,
            "lastSyncTime": self.lastSyncTime, "lastSyncStatus": self.lastSyncStatus,
            "lastSyncCount": self.lastSyncCount, "lastError": self.lastError,
            "createdAt": self.createdAt, "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncTaskConfig":
        return cls(
            id=str(data.get("_id", "")), vendorCode=data["vendorCode"],
            enabled=data.get("enabled", True), syncType=data.get("syncType", "pull"),
            cronExpression=data.get("cronExpression", "0 */5 * * *"),
            lookbackDays=data.get("lookbackDays", 1), syncWindowHours=data.get("syncWindowHours", 24),
            batchSize=data.get("batchSize", 100), wardCodes=data.get("wardCodes", []),
            lastSyncTime=data.get("lastSyncTime"), lastSyncStatus=data.get("lastSyncStatus"),
            lastSyncCount=data.get("lastSyncCount", 0), lastError=data.get("lastError"),
            createdAt=data.get("createdAt"), updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Department / Ward Configuration (科室/病区配置)
# ---------------------------------------------------------------------------

class DepartmentConfig:
    """Configuration for departments/wards that participate in data sync."""

    def __init__(
        self,
        id: Optional[str] = None,
        vendorCode: Optional[str] = None,
        wardCode: str = "",
        wardName: str = "",
        hospitalCode: Optional[str] = None,
        hisDeptCode: Optional[str] = None,
        hisDeptName: Optional[str] = None,
        hisWardCode: Optional[str] = None,
        hisWardName: Optional[str] = None,
        bedRangeStart: Optional[str] = None,
        bedRangeEnd: Optional[str] = None,
        enabled: bool = True,
        syncEnabled: bool = True,
        callbackEnabled: bool = True,
        remark: Optional[str] = None,
        createdAt: Optional[datetime] = None,
        updatedAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.wardCode = wardCode
        self.wardName = wardName
        self.hospitalCode = hospitalCode
        self.hisDeptCode = hisDeptCode
        self.hisDeptName = hisDeptName
        self.hisWardCode = hisWardCode
        self.hisWardName = hisWardName
        self.bedRangeStart = bedRangeStart
        self.bedRangeEnd = bedRangeEnd
        self.enabled = enabled
        self.syncEnabled = syncEnabled
        self.callbackEnabled = callbackEnabled
        self.remark = remark
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id, "vendorCode": self.vendorCode, "wardCode": self.wardCode,
            "wardName": self.wardName, "hospitalCode": self.hospitalCode,
            "hisDeptCode": self.hisDeptCode, "hisDeptName": self.hisDeptName,
            "hisWardCode": self.hisWardCode, "hisWardName": self.hisWardName,
            "bedRangeStart": self.bedRangeStart, "bedRangeEnd": self.bedRangeEnd,
            "enabled": self.enabled, "syncEnabled": self.syncEnabled,
            "callbackEnabled": self.callbackEnabled, "remark": self.remark,
            "createdAt": self.createdAt, "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepartmentConfig":
        return cls(
            id=str(data.get("_id", "")), vendorCode=data.get("vendorCode"),
            wardCode=data.get("wardCode", ""), wardName=data.get("wardName", ""),
            hospitalCode=data.get("hospitalCode"), hisDeptCode=data.get("hisDeptCode"),
            hisDeptName=data.get("hisDeptName"), hisWardCode=data.get("hisWardCode"),
            hisWardName=data.get("hisWardName"), bedRangeStart=data.get("bedRangeStart"),
            bedRangeEnd=data.get("bedRangeEnd"), enabled=data.get("enabled", True),
            syncEnabled=data.get("syncEnabled", True), callbackEnabled=data.get("callbackEnabled", True),
            remark=data.get("remark"), createdAt=data.get("createdAt"), updatedAt=data.get("updatedAt"),
        )


# ---------------------------------------------------------------------------
# Callback Log (回传日志)
# ---------------------------------------------------------------------------

class CallbackLog:
    """Log entry for a callback attempt."""

    def __init__(
        self,
        id: Optional[str] = None,
        vendorCode: Optional[str] = None,
        temperatureRecordId: Optional[str] = None,
        callbackUrl: Optional[str] = None,
        callbackMethod: Optional[str] = None,
        requestPayload: Optional[str] = None,
        responseStatus: Optional[int] = None,
        responseBody: Optional[str] = None,
        status: str = "pending",
        retryCount: int = 0,
        error: Optional[str] = None,
        duration: Optional[int] = None,
        createdAt: Optional[datetime] = None,
    ):
        self.id = id or gen_object_id()
        self.vendorCode = vendorCode
        self.temperatureRecordId = temperatureRecordId
        self.callbackUrl = callbackUrl
        self.callbackMethod = callbackMethod
        self.requestPayload = requestPayload
        self.responseStatus = responseStatus
        self.responseBody = responseBody
        self.status = status
        self.retryCount = retryCount
        self.error = error
        self.duration = duration
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id, "vendorCode": self.vendorCode,
            "temperatureRecordId": self.temperatureRecordId,
            "callbackUrl": self.callbackUrl, "callbackMethod": self.callbackMethod,
            "requestPayload": self.requestPayload, "responseStatus": self.responseStatus,
            "responseBody": self.responseBody, "status": self.status,
            "retryCount": self.retryCount, "error": self.error,
            "duration": self.duration, "createdAt": self.createdAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallbackLog":
        return cls(
            id=str(data.get("_id", "")), vendorCode=data.get("vendorCode"),
            temperatureRecordId=data.get("temperatureRecordId"),
            callbackUrl=data.get("callbackUrl"), callbackMethod=data.get("callbackMethod"),
            requestPayload=data.get("requestPayload"), responseStatus=data.get("responseStatus"),
            responseBody=data.get("responseBody"), status=data.get("status", "pending"),
            retryCount=data.get("retryCount", 0), error=data.get("error"),
            duration=data.get("duration"), createdAt=data.get("createdAt"),
        )
