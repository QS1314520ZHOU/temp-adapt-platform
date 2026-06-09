import logging
import traceback
from fastapi import APIRouter, Request
from app.services.transform_service import TransformService
from app.utils.response import success, error

logger = logging.getLogger(__name__)

router = APIRouter(tags=["数据推送接收"])

transform_service = TransformService()


@router.post("/{vendor_code}")
async def receive_push_data(vendor_code: str, request: Request):
    """接收厂家推送的原始数据。

    始终返回200状态码，即使转换过程出现错误——
    转换错误仅记录日志，不返回给厂家。
    """
    try:
        raw_data = await request.body()
        raw_data_str = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else str(raw_data)
        client_ip = request.client.host if request.client else "unknown"
        try:
            result = transform_service.transform_and_save(
                vendor_code=vendor_code,
                raw_data=raw_data_str,
                access_type="http_push",
                source_ip=client_ip,
            )
            logger.info("推送数据转换完成 vendor_code=%s result=%s", vendor_code, result)
        except Exception as transform_err:
            logger.error("推送数据转换失败 vendor_code=%s error=%s\n%s", vendor_code, str(transform_err), traceback.format_exc())
        return success(None, "数据接收成功")
    except Exception as e:
        logger.error("推送数据接收异常 vendor_code=%s error=%s\n%s", vendor_code, str(e), traceback.format_exc())
        return success(None, "数据接收成功")


@router.post("/{vendor_code}/test")
async def test_push_data(vendor_code: str, request: Request):
    """测试推送 - 返回转换结果"""
    try:
        raw_data = await request.body()
        raw_data_str = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else str(raw_data)
        client_ip = request.client.host if request.client else "unknown"

        result = transform_service.transform_and_save(
            vendor_code=vendor_code,
            raw_data=raw_data_str,
            access_type="http_push",
            source_ip=client_ip,
        )
        return success(result, "转换完成")
    except Exception as e:
        logger.error("测试推送失败 vendor_code=%s error=%s\n%s", vendor_code, str(e), traceback.format_exc())
        return error(str(e), code=500)
