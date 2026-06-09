"""SOAP WebService 端点 - 接收厂家推送的 SOAP 数据"""
import json
import logging
import traceback
from fastapi import APIRouter, Request, Response
from lxml import etree
from app.services.transform_service import TransformService
from app.engine.xml_record_transformer import XmlRecordTransformer
from app.utils.response import success

logger = logging.getLogger(__name__)

router = APIRouter(tags=["SOAP推送"])

transform_service = TransformService()

# SOAP 响应模板
SOAP_RESPONSE_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s="http://www.w3.org/2001/XMLSchema">
   <SOAP-ENV:Body>
      <HIPMessageServerResponse xmlns="http://www.dhcc.com.cn">
         <HIPMessageServerResult><![CDATA[<Response><Header><SourceSystem></SourceSystem><MessageID></MessageID></Header><Body><ResultCode>0</ResultCode><ResultContent>成功</ResultContent></Body></Response>]]></HIPMessageServerResult>
      </HIPMessageServerResponse>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''


@router.post("/{vendor_code}")
async def receive_soap_data(vendor_code: str, request: Request):
    """接收 SOAP 格式的推送数据

    支持两种格式:
    1. 标准 SOAP Envelope 包装，CDATA 中包含 XML
    2. 直接 XML 数据
    """
    try:
        raw_data = await request.body()
        raw_data_str = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else str(raw_data)
        client_ip = request.client.host if request.client else "unknown"

        # 尝试解析 SOAP
        inner_xml = extract_soap_body(raw_data_str)

        try:
            result = transform_service.transform_and_save(
                vendor_code=vendor_code,
                raw_data=inner_xml,
                access_type="soap",
                source_ip=client_ip,
            )
            logger.info("SOAP数据转换完成 vendor_code=%s result=%s", vendor_code, result)
        except Exception as transform_err:
            logger.error("SOAP数据转换失败 vendor_code=%s error=%s\n%s",
                        vendor_code, str(transform_err), traceback.format_exc())

        # 返回 SOAP 响应
        return Response(content=SOAP_RESPONSE_TEMPLATE, media_type="text/xml")

    except Exception as e:
        logger.error("SOAP数据接收异常 vendor_code=%s error=%s\n%s",
                    vendor_code, str(e), traceback.format_exc())
        return Response(content=SOAP_RESPONSE_TEMPLATE, media_type="text/xml")


@router.post("/{vendor_code}/test")
async def test_soap_data(vendor_code: str, request: Request):
    """测试 SOAP 推送 - 返回转换结果"""
    try:
        raw_data = await request.body()
        raw_data_str = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else str(raw_data)
        client_ip = request.client.host if request.client else "unknown"

        # 尝试解析 SOAP
        inner_xml = extract_soap_body(raw_data_str)

        # 使用 XML 转换器提取记录
        records = XmlRecordTransformer.transform_xml_to_records(inner_xml)

        if records:
            # 转换为 JSON 格式供 transform_service 处理
            json_data = json.dumps(records[0], ensure_ascii=False)
            result = transform_service.transform_and_save(
                vendor_code=vendor_code,
                raw_data=json_data,
                access_type="soap",
                source_ip=client_ip,
            )
            return success({
                "transform_result": result,
                "extracted_records": records
            }, "SOAP转换完成")
        else:
            return success({"error": "无法解析XML数据"}, "SOAP转换失败")

    except Exception as e:
        logger.error("SOAP测试失败 vendor_code=%s error=%s\n%s",
                    vendor_code, str(e), traceback.format_exc())
        return success({"error": str(e)}, "SOAP转换失败")


def extract_soap_body(raw_xml: str) -> str:
    """从 SOAP Envelope 中提取 Body 内容

    如果是标准 SOAP 格式，提取 CDATA 中的 XML
    如果是普通 XML，直接返回
    """
    try:
        root = etree.fromstring(raw_xml.encode('utf-8'))

        # 检查是否是 SOAP Envelope
        ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
              'dhcc': 'http://www.dhcc.com.cn'}

        # 尝试提取 CDATA 内容
        message_elem = root.find('.//{http://www.dhcc.com.cn}message')
        if message_elem is not None and message_elem.text:
            return message_elem.text.strip()

        # 尝试其他命名空间
        for elem in root.iter():
            if 'message' in elem.tag.lower() and elem.text and '<' in elem.text:
                return elem.text.strip()

        # 如果没有找到 SOAP 包装，返回原始 XML
        return raw_xml

    except Exception as e:
        logger.warning("SOAP解析失败，使用原始数据: %s", e)
        return raw_xml
