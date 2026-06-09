"""FastAPI 应用入口"""
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from bson import ObjectId

from app.database import Database


class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles MongoDB ObjectId and datetime."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class MongoJSONResponse(JSONResponse):
    """Custom JSON response that handles MongoDB ObjectId."""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            cls=MongoJSONEncoder,
            ensure_ascii=False,
        ).encode("utf-8")

# 路由导入
from app.routers.vendor_router import router as vendor_router
from app.routers.access_config_router import router as access_config_router
from app.routers.parser_config_router import router as parser_config_router
from app.routers.item_rule_router import router as item_rule_router
from app.routers.run_router import router as run_router
from app.routers.push_router import router as push_router
from app.routers.log_router import router as log_router
from app.routers.smartcare_router import router as smartcare_router
from app.routers.intake_output_router import router as intake_output_router
from app.routers.callback_router import router as callback_router
from app.routers.sync_router import router as sync_router
from app.routers.department_router import router as department_router
from app.routers.scheduler_router import router as scheduler_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.soap_router import router as soap_router

app = FastAPI(title="体温单回传适配平台", version="1.0.0", default_response_class=MongoJSONResponse)

# CORS —— 开发阶段允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Database.init()
    # Start the scheduler after database is initialized
    from app.services.scheduler_service import scheduler_service
    scheduler_service.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    # Stop the scheduler before closing database
    from app.services.scheduler_service import scheduler_service
    scheduler_service.stop()
    Database.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 路由注册
app.include_router(vendor_router,        prefix="/api/vendor")
app.include_router(access_config_router, prefix="/api/access-config")
app.include_router(parser_config_router, prefix="/api/parser-config")
app.include_router(item_rule_router,     prefix="/api/item-rule")
app.include_router(run_router,           prefix="/api/run")
app.include_router(push_router,          prefix="/api/push")
app.include_router(log_router,           prefix="/api/log")
app.include_router(smartcare_router,     prefix="/api/smartcare")
app.include_router(intake_output_router, prefix="/api/intake-output")
app.include_router(callback_router,    prefix="/api/callback")
app.include_router(sync_router,        prefix="/api/sync")
app.include_router(department_router,  prefix="/api/department")
app.include_router(scheduler_router,   prefix="/api/scheduler")
app.include_router(dashboard_router,   prefix="/api/dashboard")
app.include_router(soap_router,        prefix="/api/soap")
