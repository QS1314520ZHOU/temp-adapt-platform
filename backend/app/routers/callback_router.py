"""Callback configuration and execution router."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Body, Request

from app.services.callback_service import CallbackService
from app.utils.response import success, error, paginated

router = APIRouter(tags=["回传配置"])

callback_service = CallbackService()


@router.post("/config")
def save_callback_config(data: dict = Body(...)):
    """保存回传配置"""
    try:
        if not data.get("vendorCode"):
            return error("缺少 vendorCode 字段", code=400)
        result = callback_service.save_config(data)
        # 如果是定时任务，刷新调度器
        if data.get("callbackType") == "scheduled" and data.get("cronExpression"):
            from app.services.scheduler_service import scheduler_service
            scheduler_service.refresh_jobs()
        return success(result, "保存回传配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/config/{vendor_code}")
def get_callback_config(vendor_code: str):
    """获取回传配置"""
    try:
        result = callback_service.get_config(vendor_code)
        if not result:
            return error(f"未找到 vendor '{vendor_code}' 的回传配置", code=404)
        return success(result, "获取回传配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/execute/{vendor_code}")
def execute_callback(vendor_code: str, data: dict = Body(...)):
    """手动执行回传"""
    try:
        record_ids = data.get("record_ids", [])
        if not record_ids:
            return error("缺少 record_ids 字段", code=400)
        result = callback_service.batch_callback(vendor_code, record_ids)
        return success(result, "执行回传完成")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/logs")
def get_callback_logs(
    vendor_code: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
):
    """查询回传日志"""
    try:
        result = callback_service.get_logs(
            vendor_code=vendor_code,
            status=status,
            page=page,
            page_size=page_size,
        )
        return paginated(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )
    except Exception as e:
        return error(str(e), code=500)


@router.post("/retry/{log_id}")
def retry_failed_callback(log_id: str):
    """重试失败的回传"""
    try:
        result = callback_service.retry_failed(log_id)
        if result.get("success"):
            return success(result, "重试回传成功")
        else:
            return error(result.get("error", "重试失败"), code=500)
    except Exception as e:
        return error(str(e), code=500)


@router.get("/configs")
def list_callback_configs():
    """获取所有回传配置"""
    try:
        from app.database import Database
        col = Database.get_collection("callback_configs")
        configs = list(col.find().sort("createdAt", -1))
        return success(configs, "获取回传配置列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/config/{vendor_code}")
def delete_callback_config(vendor_code: str):
    """删除回传配置"""
    try:
        result = callback_service.delete_config(vendor_code)
        return success(result, "删除回传配置成功")
    except Exception as e:
        return error(str(e), code=500)
