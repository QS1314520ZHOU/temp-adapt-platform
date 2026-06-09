"""测试服务 - 支持 WebService(SOAP) 和 HTTP POST 切换"""
import json
import logging
import uvicorn
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(title="测试服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储接收到的数据
received_data = []
# 当前模式: "post" 或 "soap"
current_mode = "post"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== HTTP POST 模式 ==========

@app.post("/api/receive")
async def receive_post(request: Request):
    """HTTP POST 接收数据"""
    global received_data
    body = await request.body()
    body_str = body.decode("utf-8") if isinstance(body, bytes) else str(body)

    record = {
        "timestamp": datetime.now().isoformat(),
        "mode": "POST",
        "content_type": request.headers.get("content-type", ""),
        "body": body_str[:5000],  # 限制存储长度
        "client_ip": request.client.host if request.client else "unknown",
    }
    received_data.insert(0, record)

    logger.info("[POST] 收到数据: %s", body_str[:200])
    return {"code": 0, "message": "success", "data": None}


@app.get("/api/receive")
async def receive_get(request: Request):
    """HTTP GET 接收数据 (查询参数)"""
    global received_data
    params = dict(request.query_params)

    record = {
        "timestamp": datetime.now().isoformat(),
        "mode": "GET",
        "params": params,
        "client_ip": request.client.host if request.client else "unknown",
    }
    received_data.insert(0, record)

    logger.info("[GET] 收到数据: %s", params)
    return {"code": 0, "message": "success", "data": None}


# ========== WebService (SOAP) 模式 ==========

SOAP_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://tempadapt.test/">
  <soap:Body>
    <tns:ReceiveDataResponse>
      <tns:Result>
        <tns:Code>0</tns:Code>
        <tns:Message>success</tns:Message>
      </tns:Result>
    </tns:ReceiveDataResponse>
  </soap:Body>
</soap:Envelope>'''

WSDL_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://tempadapt.test/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             name="TempAdaptTestService"
             targetNamespace="http://tempadapt.test/">

  <types>
    <xsd:schema targetNamespace="http://tempadapt.test/">
      <xsd:element name="ReceiveDataRequest">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="VendorCode" type="xsd:string"/>
            <xsd:element name="Data" type="xsd:string"/>
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="ReceiveDataResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="Code" type="xsd:int"/>
            <xsd:element name="Message" type="xsd:string"/>
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
  </types>

  <message name="ReceiveDataInput">
    <part name="parameters" element="tns:ReceiveDataRequest"/>
  </message>
  <message name="ReceiveDataOutput">
    <part name="parameters" element="tns:ReceiveDataResponse"/>
  </message>

  <portType name="TempAdaptTestPortType">
    <operation name="ReceiveData">
      <input message="tns:ReceiveDataInput"/>
      <output message="tns:ReceiveDataOutput"/>
    </operation>
  </portType>

  <binding name="TempAdaptTestBinding" type="tns:TempAdaptTestPortType">
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
    <operation name="ReceiveData">
      <soap:operation soapAction="http://tempadapt.test/ReceiveData"/>
      <input>
        <soap:body use="literal"/>
      </input>
      <output>
        <soap:body use="literal"/>
      </output>
    </operation>
  </binding>

  <service name="TempAdaptTestService">
    <port name="TempAdaptTestPort" binding="tns:TempAdaptTestBinding">
      <soap:address location="http://localhost:9999/soap"/>
    </port>
  </service>
</definitions>'''


@app.get("/soap")
async def soap_wsdl():
    """返回 WSDL"""
    return Response(content=WSDL_CONTENT, media_type="text/xml")


@app.post("/soap")
async def soap_endpoint(request: Request):
    """SOAP 接收数据"""
    global received_data
    body = await request.body()
    body_str = body.decode("utf-8") if isinstance(body, bytes) else str(body)

    record = {
        "timestamp": datetime.now().isoformat(),
        "mode": "SOAP",
        "content_type": request.headers.get("content-type", ""),
        "body": body_str[:5000],
        "client_ip": request.client.host if request.client else "unknown",
    }
    received_data.insert(0, record)

    logger.info("[SOAP] 收到数据: %s", body_str[:200])
    return Response(content=SOAP_TEMPLATE, media_type="text/xml")


# ========== 管理接口 ==========

@app.get("/admin/logs")
async def get_logs(limit: int = 50):
    """获取接收到的数据日志"""
    return {
        "code": 0,
        "data": {
            "total": len(received_data),
            "items": received_data[:limit],
        }
    }


@app.post("/admin/clear")
async def clear_logs():
    """清空日志"""
    global received_data
    received_data = []
    return {"code": 0, "message": "日志已清空"}


@app.get("/admin/status")
async def get_status():
    """获取服务状态"""
    return {
        "code": 0,
        "data": {
            "mode": current_mode,
            "received_count": len(received_data),
            "endpoints": {
                "post": "http://localhost:9999/api/receive",
                "soap": "http://localhost:9999/soap",
                "wsdl": "http://localhost:9999/soap?wsdl",
            }
        }
    }


@app.post("/admin/mode/{mode}")
async def switch_mode(mode: str):
    """切换模式"""
    global current_mode
    if mode not in ("post", "soap"):
        return {"code": 400, "message": "模式只能是 post 或 soap"}
    current_mode = mode
    return {"code": 0, "message": f"已切换到 {mode} 模式"}


@app.get("/")
async def index():
    """首页 - 显示使用说明"""
    return {
        "service": "体温单回传适配平台 - 测试服务",
        "endpoints": {
            "POST /api/receive": "HTTP POST 接收数据",
            "POST /soap": "SOAP WebService 接收数据",
            "GET /soap": "获取 WSDL",
            "GET /admin/logs": "查看接收到的数据",
            "POST /admin/clear": "清空日志",
            "GET /admin/status": "服务状态",
            "POST /admin/mode/{mode}": "切换模式 (post/soap)",
        },
        "current_mode": current_mode,
        "received_count": len(received_data),
    }


if __name__ == "__main__":
    print("=" * 50)
    print("  测试服务已启动")
    print("  地址: http://localhost:9999")
    print("  POST 接口: http://localhost:9999/api/receive")
    print("  SOAP 接口: http://localhost:9999/soap")
    print("  WSDL 地址: http://localhost:9999/soap?wsdl")
    print("  管理后台: http://localhost:9999/admin/status")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=9999)
