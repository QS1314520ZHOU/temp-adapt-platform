"""Scheduler management router."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Body, Request

from app.services.scheduler_service import scheduler_service
from app.utils.response import success, error

router = APIRouter(tags=["定时任务"])


@router.get("/jobs")
def get_scheduled_jobs():
    """获取所有定时任务"""
    try:
        jobs = scheduler_service.get_jobs()
        return success(jobs, "获取定时任务列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/refresh")
def refresh_jobs():
    """刷新定时任务"""
    try:
        scheduler_service.refresh_jobs()
        jobs = scheduler_service.get_jobs()
        return success(jobs, "刷新定时任务成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/start")
def start_scheduler():
    """启动调度器"""
    try:
        scheduler_service.start()
        return success(None, "调度器已启动")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/stop")
def stop_scheduler():
    """停止调度器"""
    try:
        scheduler_service.stop()
        return success(None, "调度器已停止")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/sync-now/{vendor_code}")
def sync_now(vendor_code: str):
    """立即执行一次同步"""
    try:
        from app.services.sync_service import SyncService
        sync_service = SyncService()
        result = sync_service.execute_sync(vendor_code)
        if result.get("success"):
            return success(result, "同步执行完成")
        else:
            return error(result.get("error", "同步执行失败"), code=500)
    except Exception as e:
        return error(str(e), code=500)
