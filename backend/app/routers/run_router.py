from fastapi import APIRouter, Body
from app.services.pull_service import PullService
from app.services.transform_service import TransformService
from app.services.retry_service import RetryService
from app.utils.response import success, error

router = APIRouter(tags=["运行操作"])

pull_service = PullService()
transform_service = TransformService()
retry_service = RetryService()


@router.post("/pull/{vendor_code}")
def manual_pull(vendor_code: str):
    try:
        result = pull_service.pull_from_vendor(vendor_code)
        return success(result, "手动拉取完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/transform/{raw_record_id}")
def manual_transform(raw_record_id: str):
    try:
        result = transform_service.transform_single(raw_record_id)
        return success(result, "手动转换完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/retry/{raw_record_id}")
def retry_record(raw_record_id: str):
    try:
        result = retry_service.retry_raw_record(raw_record_id)
        return success(result, "重试完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/batch-retry")
def batch_retry(data: dict = Body(...)):
    try:
        record_ids = data.get("record_ids")
        if not record_ids or not isinstance(record_ids, list):
            return error("缺少 record_ids 字段或格式不正确", code=400)
        result = retry_service.batch_retry(record_ids)
        return success(result, "批量重试完成")
    except Exception as e:
        return error(str(e), code=500)
