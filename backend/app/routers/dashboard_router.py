"""仪表盘统计路由"""
from datetime import datetime, timedelta
from fastapi import APIRouter
from app.database import Database
from app.utils.response import success

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    db = Database.get_db()

    # 今日零点
    today_start = datetime.combine(datetime.now().date(), datetime.min.time())

    # 今日接收数
    today_received = db.transform_logs.count_documents(
        {"createdAt": {"$gte": today_start}}
    )

    # 今日成功数
    today_success = db.transform_logs.count_documents(
        {"createdAt": {"$gte": today_start}, "status": "success"}
    )

    # 今日失败数
    today_failed = db.transform_logs.count_documents(
        {"createdAt": {"$gte": today_start}, "status": "failed"}
    )

    # 今日未识别数
    today_unrecognized = db.transform_logs.count_documents(
        {"createdAt": {"$gte": today_start}, "status": "unrecognized"}
    )

    # 定时任务数
    scheduler_jobs = 0
    try:
        scheduler_jobs = db.scheduler_tasks.count_documents({"enabled": True})
    except Exception:
        pass

    # 今日同步数
    today_sync_count = 0
    try:
        today_sync_count = db.sync_logs.count_documents(
            {"createdAt": {"$gte": today_start}}
        )
    except Exception:
        pass

    # 今日回传数
    today_callback_count = 0
    try:
        today_callback_count = db.callback_logs.count_documents(
            {"createdAt": {"$gte": today_start}}
        )
    except Exception:
        pass

    # 今日回传失败数
    today_callback_failed = 0
    try:
        today_callback_failed = db.callback_logs.count_documents(
            {"createdAt": {"$gte": today_start}, "status": "failed"}
        )
    except Exception:
        pass

    return success({
        "todayReceived": today_received,
        "todaySuccess": today_success,
        "todayFailed": today_failed,
        "todayUnrecognized": today_unrecognized,
        "schedulerJobs": scheduler_jobs,
        "todaySyncCount": today_sync_count,
        "todayCallbackCount": today_callback_count,
        "todayCallbackFailed": today_callback_failed,
    })
