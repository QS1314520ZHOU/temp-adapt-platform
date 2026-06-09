"""Sync task configuration and execution router."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Body, Request

from app.services.sync_service import SyncService
from app.utils.response import success, error

router = APIRouter(tags=["同步任务"])

sync_service = SyncService()


@router.post("/config")
def save_sync_config(data: dict = Body(...)):
    """保存同步配置"""
    try:
        if not data.get("vendorCode"):
            return error("缺少 vendorCode 字段", code=400)
        result = sync_service.save_config(data)
        return success(result, "保存同步配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/config/list")
def list_sync_configs(enabled_only: bool = Query(False)):
    """列出所有同步配置"""
    try:
        result = sync_service.list_configs(enabled_only=enabled_only)
        return success(result, "获取同步配置列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/config/{vendor_code}")
def get_sync_config(vendor_code: str):
    """获取同步配置"""
    try:
        result = sync_service.get_config(vendor_code)
        if not result:
            return error(f"未找到 vendor '{vendor_code}' 的同步配置", code=404)
        return success(result, "获取同步配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/execute/{vendor_code}")
def execute_sync(vendor_code: str):
    """手动执行同步"""
    try:
        result = sync_service.execute_sync(vendor_code)
        if result.get("success"):
            return success(result, "同步执行完成")
        else:
            return error(result.get("error", "同步执行失败"), code=500)
    except Exception as e:
        return error(str(e), code=500)


@router.post("/execute-all")
def execute_all_sync():
    """执行所有启用的同步任务"""
    try:
        result = sync_service.execute_all_enabled()
        return success(result, "批量同步执行完成")
    except Exception as e:
        return error(str(e), code=500)


# ------------------------------------------------------------------
# Bedside sync endpoints
# ------------------------------------------------------------------

@router.post("/bedside/full/{vendor_code}")
def bedside_full_sync(vendor_code: str):
    """手动触发 bedside 全量同步"""
    try:
        from app.services.bedside_sync_service import bedside_sync_service
        from app.database import Database

        col = Database.get_collection("sync_task_configs")
        config = col.find_one({"vendorCode": vendor_code, "syncType": "bedside_sync"})
        if not config:
            return error(f"未找到 vendor '{vendor_code}' 的 bedside 同步配置", code=404)

        result = bedside_sync_service.full_sync(
            vendor_code=vendor_code,
            datasource_id=config.get("datasourceId", ""),
            lookback_days=config.get("lookbackDays", 7),
            callback_url=config.get("callbackUrl"),
            ward_codes=config.get("wardCodes"),
        )
        if result.get("success"):
            return success(result, "bedside 全量同步完成")
        else:
            return error(result.get("error", "同步失败"), code=500)
    except Exception as e:
        return error(str(e), code=500)


@router.post("/bedside/incremental/{vendor_code}")
def bedside_incremental_sync(vendor_code: str):
    """手动触发 bedside 增量检查"""
    try:
        from app.services.bedside_sync_service import bedside_sync_service
        from app.database import Database

        col = Database.get_collection("sync_task_configs")
        config = col.find_one({"vendorCode": vendor_code, "syncType": "bedside_sync"})
        if not config:
            return error(f"未找到 vendor '{vendor_code}' 的 bedside 同步配置", code=404)

        result = bedside_sync_service.incremental_sync(
            vendor_code=vendor_code,
            datasource_id=config.get("datasourceId", ""),
            callback_url=config.get("callbackUrl"),
            ward_codes=config.get("wardCodes"),
        )
        if result.get("success"):
            return success(result, "bedside 增量检查完成")
        else:
            return error(result.get("error", "同步失败"), code=500)
    except Exception as e:
        return error(str(e), code=500)


@router.get("/bedside/state/{vendor_code}")
def get_bedside_sync_state(vendor_code: str):
    """获取 bedside 同步状态"""
    try:
        from app.services.bedside_sync_service import bedside_sync_service
        state = bedside_sync_service.get_sync_state(vendor_code)
        return success(state or {}, "获取同步状态成功")
    except Exception as e:
        return error(str(e), code=500)
