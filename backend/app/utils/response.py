"""统一 API 响应格式"""
from typing import Any, Dict, List, Optional


def success(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data,
    }


def error(message: str, code: int = -1) -> Dict[str, Any]:
    """失败响应"""
    return {
        "code": code,
        "message": message,
        "data": None,
    }


def paginated(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
) -> Dict[str, Any]:
    """分页响应"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }
