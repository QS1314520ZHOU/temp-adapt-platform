from fastapi import APIRouter, Query, Body
from app.services.smartcare_service import SmartCareService
from app.utils.response import success, error

router = APIRouter(tags=["SmartCare数据源"])

smartcare_service = SmartCareService()


@router.post("/datasource")
def save_datasource(data: dict = Body(...)):
    try:
        result = smartcare_service.save_datasource(data)
        return success(result, "保存数据源配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/datasource")
def get_datasource(id: str = Query(None)):
    try:
        result = smartcare_service.get_datasource(id)
        return success(result, "获取数据源配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/datasource/{datasource_id}")
def delete_datasource(datasource_id: str):
    try:
        from app.database import Database
        col = Database.get_collection("smartcare_datasource_config")
        result = col.delete_one({"_id": datasource_id})
        if result.deleted_count == 0:
            return error("数据源不存在", code=404)
        return success(None, "删除数据源成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/datasource/test")
def test_datasource_connection(data: dict = Body(...)):
    """测试数据源连接 — 支持直接传 host/port/database/username/password"""
    try:
        result = smartcare_service.test_connection_direct(data)
        return success(result, "数据源连接测试完成")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/config-param/list")
def list_config_params(datasource_id: str = Query(...)):
    try:
        result = smartcare_service.get_config_param_list(datasource_id)
        return success(result, "获取配置参数列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/config-param/sync")
def sync_config_params(data: dict = Body(...)):
    try:
        result = smartcare_service.sync_config_params(data)
        return success(result, "同步配置参数成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/field-mapping")
def save_field_mapping(data: dict = Body(...)):
    try:
        result = smartcare_service.save_field_mapping(data)
        return success(result, "保存字段映射成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/field-mapping/{collection_name}")
def get_field_mapping(collection_name: str):
    try:
        result = smartcare_service.get_field_mapping(collection_name)
        return success(result, "获取字段映射成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/patients")
def search_patients(
    datasource_id: str = Query(...),
    keyword: str = Query(None),
    ward_code: str = Query(None),
):
    try:
        result = smartcare_service.search_patients(
            datasource_id=datasource_id,
            keyword=keyword,
            ward_code=ward_code,
        )
        return success(result, "查询患者成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/patient/{patient_id}")
def get_patient_detail(patient_id: str, datasource_id: str = Query(...)):
    try:
        result = smartcare_service.get_patient(patient_id=patient_id, datasource_id=datasource_id)
        return success(result, "获取患者详情成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/bedside")
def get_bedside_records(
    datasource_id: str = Query(...),
    patient_id: str = Query(...),
    start_time: str = Query(None),
    end_time: str = Query(None),
):
    try:
        result = smartcare_service.get_bedside_records(
            datasource_id=datasource_id,
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
        )
        return success(result, "获取床旁记录成功")
    except Exception as e:
        return error(str(e), code=500)
