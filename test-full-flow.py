"""全流程测试脚本 - 使用中联HIS数据测试"""
import json
import requests
import time

BASE_URL = "http://localhost:8000"
VENDOR_CODE = "zhonglian"

# 测试数据
TEST_DATA = {
    "input": {
        "head": {
            "action_no": "S8009-1780383367426",
            "bizno": "S8009",
            "sysno": "SYZZ",
            "tarno": "ZLHIS",
            "time": "2026-06-02 14:56:07"
        },
        "pat_list": [
            {
                "user_name": "管理员",
                "specail_content": "",
                "pid": "799063",
                "baby_sno": "",
                "visit_sno": "",
                "record_id": "",
                "oprtr_type": "1",
                "user_code": "",
                "pvid": "3",
                "data_time": "2026-06-02 12:54:00",
                "item_list": [
                    {"item_part": "", "item_id": "3", "item_name": "呼吸", "item_tag": "", "item_data": "21"},
                    {"item_part": "", "item_id": "1", "item_name": "体温", "item_tag": "", "item_data": "36.6"},
                    {"item_part": "", "item_id": "", "item_name": "脉率", "item_tag": "", "item_data": "76"},
                    {"item_part": "", "item_id": "-1", "item_name": "心率", "item_tag": "", "item_data": "76"},
                    {"item_part": "", "item_id": "", "item_name": "血压", "item_tag": "", "item_data": "154/97"}
                ],
                "inpno": "14894225",
                "file_id": "",
                "file_formatid": "3243",
                "ward_id": "4703"
            },
            {
                "user_name": "管理员",
                "specail_content": "",
                "pid": "799063",
                "baby_sno": "",
                "visit_sno": "",
                "record_id": "",
                "oprtr_type": "1",
                "user_code": "",
                "pvid": "3",
                "data_time": "2026-06-02 14:00:00",
                "item_list": [
                    {"item_part": "", "item_id": "3", "item_name": "呼吸", "item_tag": "", "item_data": "21"},
                    {"item_part": "", "item_id": "1", "item_name": "体温", "item_tag": "", "item_data": "36.5"},
                    {"item_part": "", "item_id": "", "item_name": "脉率", "item_tag": "", "item_data": "67"},
                    {"item_part": "", "item_id": "-1", "item_name": "心率", "item_tag": "", "item_data": "67"},
                    {"item_part": "", "item_id": "", "item_name": "血压", "item_tag": "", "item_data": "112/65"}
                ],
                "inpno": "14894225",
                "file_id": "",
                "file_formatid": "3243",
                "ward_id": "4703"
            },
            {
                "user_name": "管理员",
                "specail_content": "",
                "pid": "799063",
                "baby_sno": "",
                "visit_sno": "",
                "record_id": "",
                "oprtr_type": "1",
                "user_code": "",
                "pvid": "3",
                "data_time": "2026-06-02 13:00:00",
                "item_list": [
                    {"item_part": "", "item_id": "3", "item_name": "呼吸", "item_tag": "", "item_data": "21"},
                    {"item_part": "", "item_id": "", "item_name": "脉率", "item_tag": "", "item_data": "68"},
                    {"item_part": "", "item_id": "-1", "item_name": "心率", "item_tag": "", "item_data": "68"},
                    {"item_part": "", "item_id": "", "item_name": "血压", "item_tag": "", "item_data": "153/84"}
                ],
                "inpno": "14894225",
                "file_id": "",
                "file_formatid": "3243",
                "ward_id": "4703"
            }
        ]
    }
}


def print_step(step, title):
    print(f"\n{'='*60}")
    print(f"  步骤 {step}: {title}")
    print(f"{'='*60}")


def print_result(success, data=None, error=None):
    if success:
        print(f"  [OK] 成功")
        if data:
            print(f"  数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
    else:
        print(f"  [FAIL] 失败: {error}")


def test_full_flow():
    print("\n" + "体温单回传适配平台 - 全流程测试".center(60))
    print(f"厂家代码: {VENDOR_CODE}")
    print(f"后端地址: {BASE_URL}")

    # 步骤1: 创建厂家
    print_step(1, "创建厂家")
    try:
        res = requests.post(f"{BASE_URL}/api/vendor", json={
            "vendorCode": VENDOR_CODE,
            "vendorName": "中联HIS",
            "hospitalCode": "H001",
            "hospitalName": "测试医院",
            "enabled": True,
            "accessType": "http_push",
            "description": "中联HIS体温数据推送"
        })
        data = res.json()
        if data.get("code") == 0:
            print_result(True, data.get("data"))
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤2: 配置接入方式 (HTTP推送)
    print_step(2, "配置接入方式 (HTTP推送)")
    try:
        res = requests.post(f"{BASE_URL}/api/access-config", json={
            "vendorCode": VENDOR_CODE,
            "accessType": "http_push",
            "httpPushConfig": {
                "endpointPath": f"/api/push/{VENDOR_CODE}",
                "authType": "none"
            },
            "enabled": True
        })
        data = res.json()
        if data.get("code") == 0:
            print_result(True, data.get("data"))
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤3: 配置解析规则
    print_step(3, "配置解析规则")
    try:
        res = requests.post(f"{BASE_URL}/api/parser-config", json={
            "vendorCode": VENDOR_CODE,
            "dataFormat": "json",
            "encoding": "UTF-8",
            "rootPath": "$.input",
            "recordPath": "$.input.pat_list[*]",
            "itemPath": "item_list[*]",
            "recordPathType": "jsonpath",
            "itemPathType": "jsonpath",
            "rootFieldMappings": [
                {"targetField": "action_no", "sourcePath": "$.input.head.action_no"},
                {"targetField": "sysno", "sourcePath": "$.input.head.sysno"}
            ],
            "recordFieldMappings": [
                {"targetField": "patientId", "sourcePath": "$.pid"},
                {"targetField": "measureTime", "sourcePath": "$.data_time"},
                {"targetField": "admissionNo", "sourcePath": "$.inpno"},
                {"targetField": "wardCode", "sourcePath": "$.ward_id"}
            ],
            "itemFieldMappings": [
                {"targetField": "itemName", "sourcePath": "$.item_name"},
                {"targetField": "itemValue", "sourcePath": "$.item_data"}
            ],
            "enabled": True
        })
        data = res.json()
        if data.get("code") == 0:
            print_result(True, data.get("data"))
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤4: 配置指标规则
    print_step(4, "配置指标规则")
    try:
        res = requests.post(f"{BASE_URL}/api/item-rule", json={
            "vendorCode": VENDOR_CODE,
            "rules": [
                {
                    "itemName": "体温",
                    "matchField": "item_name",
                    "matchValue": "体温",
                    "matchType": "exact",
                    "targetCode": "TEMP",
                    "unit": "℃",
                    "valueType": "number",
                    "enabled": True
                },
                {
                    "itemName": "呼吸",
                    "matchField": "item_name",
                    "matchValue": "呼吸",
                    "matchType": "exact",
                    "targetCode": "RESP",
                    "unit": "次/分",
                    "valueType": "number",
                    "enabled": True
                },
                {
                    "itemName": "脉率",
                    "matchField": "item_name",
                    "matchValue": "脉率",
                    "matchType": "exact",
                    "targetCode": "PULSE",
                    "unit": "次/分",
                    "valueType": "number",
                    "enabled": True
                },
                {
                    "itemName": "心率",
                    "matchField": "item_name",
                    "matchValue": "心率",
                    "matchType": "exact",
                    "targetCode": "HR",
                    "unit": "次/分",
                    "valueType": "number",
                    "enabled": True
                },
                {
                    "itemName": "血压",
                    "matchField": "item_name",
                    "matchValue": "血压",
                    "matchType": "exact",
                    "targetCode": "BP",
                    "unit": "mmHg",
                    "valueType": "string",
                    "enabled": True
                }
            ]
        })
        data = res.json()
        if data.get("code") == 0:
            print_result(True, data.get("data"))
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤5: 推送测试数据
    print_step(5, "推送测试数据")
    try:
        res = requests.post(
            f"{BASE_URL}/api/push/{VENDOR_CODE}",
            json=TEST_DATA,
            headers={"Content-Type": "application/json"}
        )
        data = res.json()
        if data.get("code") == 0:
            print_result(True, data.get("data"))
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    time.sleep(1)

    # 步骤6: 查看转换日志
    print_step(6, "查看转换日志")
    try:
        res = requests.get(f"{BASE_URL}/api/log/transform", params={
            "vendor_code": VENDOR_CODE,
            "page": 1,
            "page_size": 10
        })
        data = res.json()
        if data.get("code") == 0:
            items = data.get("data", {}).get("items", [])
            print(f"  找到 {len(items)} 条转换记录")
            for item in items[:3]:
                print(f"    - 状态: {item.get('status')}, 时间: {item.get('createdAt')}")
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤7: 查看未识别指标
    print_step(7, "查看未识别指标")
    try:
        res = requests.get(f"{BASE_URL}/api/log/unmatched", params={
            "vendor_code": VENDOR_CODE,
            "page": 1,
            "page_size": 10
        })
        data = res.json()
        if data.get("code") == 0:
            items = data.get("data", {}).get("items", [])
            print(f"  找到 {len(items)} 条未识别指标")
            for item in items[:5]:
                print(f"    - 指标: {item.get('itemName')}, 值: {item.get('itemValue')}")
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤8: 查看仪表盘统计
    print_step(8, "查看仪表盘统计")
    try:
        res = requests.get(f"{BASE_URL}/api/dashboard/stats")
        data = res.json()
        if data.get("code") == 0:
            print_result(True, data.get("data"))
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    # 步骤9: 查看定时任务
    print_step(9, "查看定时任务")
    try:
        res = requests.get(f"{BASE_URL}/api/scheduler/jobs")
        data = res.json()
        if data.get("code") == 0:
            jobs = data.get("data", [])
            print(f"  当前有 {len(jobs)} 个定时任务")
            for job in jobs:
                print(f"    - {job.get('id')}: {job.get('trigger')}")
        else:
            print_result(False, error=data.get("message"))
    except Exception as e:
        print_result(False, error=str(e))

    print(f"\n{'='*60}")
    print("  全流程测试完成!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_full_flow()
