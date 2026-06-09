"""枚举定义"""
from enum import Enum


class AccessType(str, Enum):
    HTTP_PUSH = "http_push"
    HTTP_PULL = "http_pull"
    DB_VIEW = "db_view"


class DataFormat(str, Enum):
    JSON = "json"
    XML = "xml"
    SQL = "sql"


class PathType(str, Enum):
    JSONPATH = "jsonpath"
    XPATH = "xpath"
    SQL = "sql"


class DataType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    BLOOD_PRESSURE = "blood_pressure"


class MatchType(str, Enum):
    EQUALS = "equals"
    CONTAINS = "contains"
    REGEX = "regex"
    STARTS_WITH = "starts_with"
    IN_LIST = "in_list"


class RecordStatus(str, Enum):
    PENDING = "pending"
    TRANSFORMED = "transformed"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class CalculationType(str, Enum):
    IN = "in"
    OUT = "out"
    OBS = "obs"
    OTHER = "other"


class Category(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    URINE = "urine"
    STOOL = "stool"
    DRAINAGE = "drainage"
    VOMIT = "vomit"
    OTHER = "other"


class StatType(str, Enum):
    SUM = "sum"
    COUNT = "count"
    LATEST = "latest"
    TEXT_MERGE = "text_merge"
    CUSTOM = "custom"


class TimeWindowType(str, Enum):
    ROLLING = "rolling"
    DAY = "day"
    SHIFT = "shift"
    CUSTOM = "custom"
