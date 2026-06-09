from fastapi import APIRouter, Query, Body
from app.services.intake_output_service import IntakeOutputService
from app.utils.response import success, error

router = APIRouter(tags=["出入量"])

intake_output_service = IntakeOutputService()


@router.post("/item-config")
def save_item_config(data: dict = Body(...)):
    try:
        result = intake_output_service.save_item_config(data)
        return success(result, "保存出入量项目配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/item-config/list")
def list_item_configs(datasource_id: str = Query(None)):
    try:
        result = intake_output_service.get_item_configs(datasource_id)
        return success(result, "获取出入量项目配置列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/stat-rule")
def save_stat_rule(data: dict = Body(...)):
    try:
        result = intake_output_service.save_stat_rule(data)
        return success(result, "保存统计规则成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/stat-rule/list")
def list_stat_rules(datasource_id: str = Query(None)):
    try:
        result = intake_output_service.get_stat_rules(datasource_id)
        return success(result, "获取统计规则列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/preview")
def preview_calculation(data: dict = Body(...)):
    try:
        result = intake_output_service.preview(data)
        return success(result, "预览计算结果成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/calculate")
def calculate_and_save(data: dict = Body(...)):
    try:
        result = intake_output_service.calculate(data)
        return success(result, "计算并保存成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/results")
def get_results(
    datasource_id: str = Query(None),
    patient_id: str = Query(None),
):
    try:
        result = intake_output_service.get_results(
            datasource_id=datasource_id,
            patient_id=patient_id,
        )
        return success(result, "获取出入量结果成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/logs")
def get_calculation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        result = intake_output_service.get_logs()
        return success(result, "获取计算日志成功")
    except Exception as e:
        return error(str(e), code=500)
