"""
Pydantic V2 schemas (request/response DTOs) for the temperature chart adaptation platform.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Generic response wrappers
# ---------------------------------------------------------------------------

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    model_config = ConfigDict(populate_by_name=True)

    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    model_config = ConfigDict(populate_by_name=True)

    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    pageSize: int = 20


# ---------------------------------------------------------------------------
# VendorConfig
# ---------------------------------------------------------------------------

class VendorConfigCreate(BaseModel):
    """Request body for creating a vendor configuration."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: str
    vendorName: str
    hospitalCode: Optional[str] = None
    hospitalName: Optional[str] = None
    enabled: bool = True
    accessType: str = "http_push"
    description: Optional[str] = None
    contactInfo: Optional[str] = None
    createdBy: Optional[str] = None


class VendorConfigUpdate(BaseModel):
    """Request body for updating a vendor configuration."""

    model_config = ConfigDict(populate_by_name=True)

    vendorName: Optional[str] = None
    hospitalCode: Optional[str] = None
    hospitalName: Optional[str] = None
    enabled: Optional[bool] = None
    accessType: Optional[str] = None
    description: Optional[str] = None
    contactInfo: Optional[str] = None


# ---------------------------------------------------------------------------
# AccessConfig
# ---------------------------------------------------------------------------

class AccessConfigCreate(BaseModel):
    """Request body for creating an access configuration."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: str
    accessType: str
    httpPushConfig: Optional[Dict[str, Any]] = None
    httpPullConfig: Optional[Dict[str, Any]] = None
    dbViewConfig: Optional[Dict[str, Any]] = None
    enabled: bool = True


# ---------------------------------------------------------------------------
# ParserConfig
# ---------------------------------------------------------------------------

class FieldMappingSchema(BaseModel):
    """A single field mapping entry."""

    model_config = ConfigDict(populate_by_name=True)

    targetField: str
    sourcePath: str
    dataType: str
    dateFormat: Optional[str] = None
    required: Optional[bool] = None
    defaultValue: Optional[str] = None


class ParserConfigCreate(BaseModel):
    """Request body for creating a parser configuration."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: str
    dataFormat: str = "json"
    encoding: str = "UTF-8"
    rootPath: str = "$"
    recordPath: str
    itemPath: Optional[str] = None
    recordPathType: str = "jsonpath"
    itemPathType: str = "jsonpath"
    rootFieldMappings: List[FieldMappingSchema] = Field(default_factory=list)
    recordFieldMappings: List[FieldMappingSchema] = Field(default_factory=list)
    itemFieldMappings: List[FieldMappingSchema] = Field(default_factory=list)
    xmlConfig: Optional[Dict[str, Any]] = None
    sqlConfig: Optional[Dict[str, Any]] = None
    enabled: bool = True


# ---------------------------------------------------------------------------
# ItemMappingRule
# ---------------------------------------------------------------------------

class ItemRuleEntry(BaseModel):
    """A single item mapping rule entry."""

    model_config = ConfigDict(populate_by_name=True)

    ruleId: str
    matchField: str
    matchType: str = Field(
        description="One of: equals, contains, regex, starts_with, in_list"
    )
    matchValue: Any
    targetCode: str
    targetName: str
    dataType: Optional[str] = None
    unit: Optional[str] = None
    priority: int = 0
    enabled: bool = True
    splitSeparator: Optional[str] = None
    splitFields: Optional[List[str]] = None
    valueDict: Optional[Dict[str, Any]] = None
    regexPattern: Optional[str] = None
    regexGroup: Optional[int] = None


class ItemRuleCreate(BaseModel):
    """Request body for creating item mapping rules."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: str
    rules: List[ItemRuleEntry] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Transform Preview
# ---------------------------------------------------------------------------

class TransformPreviewRequest(BaseModel):
    """Request body for previewing a data transformation."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: str
    rawData: str


class TemperatureItemSchema(BaseModel):
    """Schema for a single temperature item in preview results."""

    model_config = ConfigDict(populate_by_name=True)

    code: Optional[str] = None
    name: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    source: Optional[str] = None
    rawItemId: Optional[str] = None
    rawItemName: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    statTimeRange: Optional[Dict[str, Any]] = None
    matched: bool = True


class TransformPreviewRecord(BaseModel):
    """A single transformed record returned in the preview response."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: Optional[str] = None
    patientId: Optional[str] = None
    visitNo: Optional[str] = None
    patientVisitId: Optional[str] = None
    wardCode: Optional[str] = None
    bedNo: Optional[str] = None
    recordTime: Optional[datetime] = None
    operatorCode: Optional[str] = None
    operatorName: Optional[str] = None
    items: List[TemperatureItemSchema] = Field(default_factory=list)
    idempotentKey: Optional[str] = None


class UnmatchedItemSchema(BaseModel):
    """Schema for an unmatched item in the preview response."""

    model_config = ConfigDict(populate_by_name=True)

    vendorCode: Optional[str] = None
    patientId: Optional[str] = None
    recordTime: Optional[datetime] = None
    itemData: Optional[Dict[str, Any]] = None


class TransformPreviewResponse(BaseModel):
    """Response body for a transform preview."""

    model_config = ConfigDict(populate_by_name=True)

    records: List[TransformPreviewRecord] = Field(default_factory=list)
    unmatchedItems: List[UnmatchedItemSchema] = Field(default_factory=list)
    totalRecords: int = 0
    successCount: int = 0
    failCount: int = 0
    unmatchedCount: int = 0


# ---------------------------------------------------------------------------
# Intake/Output Preview
# ---------------------------------------------------------------------------

class IntakeOutputPreviewRequest(BaseModel):
    """Request body for previewing intake/output calculations."""

    model_config = ConfigDict(populate_by_name=True)

    datasourceId: str
    patientId: str
    startTime: datetime
    endTime: datetime


class IntakeOutputResultItem(BaseModel):
    """A single intake/output result item in the preview response."""

    model_config = ConfigDict(populate_by_name=True)

    code: Optional[str] = None
    name: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    statType: Optional[str] = None
    itemCount: int = 0
    detailCodes: List[str] = Field(default_factory=list)


class IntakeOutputPreviewResponse(BaseModel):
    """Response body for an intake/output preview."""

    model_config = ConfigDict(populate_by_name=True)

    patientId: Optional[str] = None
    patientName: Optional[str] = None
    bedNo: Optional[str] = None
    wardCode: Optional[str] = None
    calcTime: Optional[datetime] = None
    statTimeRange: Optional[Dict[str, Any]] = None
    results: List[IntakeOutputResultItem] = Field(default_factory=list)
    rawBedsideIds: List[str] = Field(default_factory=list)
    unmatchedItems: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Batch Retry
# ---------------------------------------------------------------------------

class BatchRetryRequest(BaseModel):
    """Request body for batch retrying failed records."""

    model_config = ConfigDict(populate_by_name=True)

    recordIds: List[str] = Field(default_factory=list)
