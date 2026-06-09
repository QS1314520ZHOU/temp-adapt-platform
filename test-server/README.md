# 测试服务

用于测试 HTTP POST 和 WebService (SOAP) 数据推送。

## 启动

```bash
cd test-server
python server.py
```

或双击 `start.bat`

## 接口说明

| 接口 | 说明 |
|------|------|
| `POST http://localhost:9999/api/receive` | HTTP POST 接收数据 |
| `POST http://localhost:9999/soap` | SOAP WebService 接收数据 |
| `GET http://localhost:9999/soap?wsdl` | 获取 WSDL |
| `GET http://localhost:9999/admin/logs` | 查看接收到的数据 |
| `POST http://localhost:9999/admin/clear` | 清空日志 |
| `GET http://localhost:9999/admin/status` | 服务状态 |

## 测试示例

### HTTP POST 测试

```bash
curl -X POST http://localhost:9999/api/receive \
  -H "Content-Type: application/json" \
  -d '{"vendorCode":"test","data":"hello"}'
```

### SOAP 测试

```bash
curl -X POST http://localhost:9999/soap \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ReceiveDataRequest xmlns="http://tempadapt.test/"><VendorCode>test</VendorCode><Data>hello</Data></ReceiveDataRequest></soap:Body></soap:Envelope>'
```

### 查看日志

```bash
curl http://localhost:9999/admin/logs
```
