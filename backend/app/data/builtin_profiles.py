"""内置适配器模板 — 常见 HIS 厂家的预配置方案。

每个模板包含完整的接入配置，用户选择后可直接使用，无需手动配置。
"""

BUILTIN_PROFILES = [
    # =================================================================
    # 1. 东华 HIS (SOAP/XML)
    # =================================================================
    {
        "profileCode": "dhcc_soap",
        "profileName": "东华 HIS (SOAP/XML)",
        "description": "东华医疗 HIS 系统，通过 SOAP WebService 推送 EStatusParameter 格式的体温单数据。"
                       "适用于 DHCC/DHC 系列产品。",
        "tags": ["SOAP", "XML", "东华", "DHCC", "HTTP Push"],
        "accessType": "soap_push",
        "vendorTemplate": {
            "accessType": "soap_push",
            "description": "东华 HIS SOAP 接入",
        },
        "accessConfigTemplate": {
            "accessType": "soap_push",
            "httpPushConfig": {
                "endpointPath": "/api/soap/{vendor_code}",
                "authType": "none",
            },
        },
        "parserConfigTemplate": {
            "dataFormat": "xml",
            "encoding": "UTF-8",
            "rootPath": "/",
            "recordPath": "//EStatusParameter",
            "itemPath": ".",
            "recordPathType": "xpath",
            "itemPathType": "xpath",
            "rootFieldMappings": {},
            "recordFieldMappings": {
                "patientId": {"sourcePath": "PATPatientID", "dataType": "string"},
                "visitNo": {"sourcePath": "PAADMVisitNumber", "dataType": "string"},
                "wardCode": {"sourcePath": "WARDCode", "dataType": "string"},
                "recordDate": {"sourcePath": "Date", "dataType": "string"},
                "recordTime": {"sourcePath": "Time", "dataType": "string"},
                "operatorCode": {"sourcePath": "UpdateUserCode", "dataType": "string"},
                "operatorName": {"sourcePath": "UpdateUserName", "dataType": "string"},
            },
            "itemFieldMappings": {},
        },
        "itemRulesTemplate": [
            {"ruleId": "dhcc_temp", "matchField": "fieldName", "matchType": "equals", "matchValue": "Temperature", "targetCode": "TEMP", "targetName": "腋温", "dataType": "number", "unit": "℃", "priority": 1},
            {"ruleId": "dhcc_temp_rectal", "matchField": "fieldName", "matchType": "equals", "matchValue": "RecTemperature", "targetCode": "TEMP_RECTAL", "targetName": "肛温", "dataType": "number", "unit": "℃", "priority": 2},
            {"ruleId": "dhcc_temp_oral", "matchField": "fieldName", "matchType": "equals", "matchValue": "oraltemperature", "targetCode": "TEMP_ORAL", "targetName": "口温", "dataType": "number", "unit": "℃", "priority": 3},
            {"ruleId": "dhcc_temp_ear", "matchField": "fieldName", "matchType": "equals", "matchValue": "eartemperature", "targetCode": "TEMP_EAR", "targetName": "耳温", "dataType": "number", "unit": "℃", "priority": 4},
            {"ruleId": "dhcc_pulse", "matchField": "fieldName", "matchType": "equals", "matchValue": "Pulse", "targetCode": "PULSE", "targetName": "脉搏", "dataType": "number", "unit": "次/分", "priority": 10},
            {"ruleId": "dhcc_resp", "matchField": "fieldName", "matchType": "equals", "matchValue": "Breath", "targetCode": "RESP", "targetName": "呼吸", "dataType": "number", "unit": "次/分", "priority": 11},
            {"ruleId": "dhcc_resp_machine", "matchField": "fieldName", "matchType": "equals", "matchValue": "BreathB", "targetCode": "RESP_MACHINE", "targetName": "机控呼吸", "dataType": "number", "unit": "次/分", "priority": 12},
            {"ruleId": "dhcc_bp_sys", "matchField": "fieldName", "matchType": "equals", "matchValue": "SysPressure", "targetCode": "SYS_BP", "targetName": "收缩压", "dataType": "number", "unit": "mmHg", "priority": 20},
            {"ruleId": "dhcc_bp_dia", "matchField": "fieldName", "matchType": "equals", "matchValue": "DiaPressure", "targetCode": "DIA_BP", "targetName": "舒张压", "dataType": "number", "unit": "mmHg", "priority": 21},
            {"ruleId": "dhcc_spo2", "matchField": "fieldName", "matchType": "equals", "matchValue": "DegrBlood", "targetCode": "SPO2", "targetName": "血氧饱和度", "dataType": "number", "unit": "%", "priority": 30},
            {"ruleId": "dhcc_hr", "matchField": "fieldName", "matchType": "equals", "matchValue": "Heartbeat", "targetCode": "HR", "targetName": "心率", "dataType": "number", "unit": "次/分", "priority": 31},
            {"ruleId": "dhcc_cooling", "matchField": "fieldName", "matchType": "equals", "matchValue": "PhyCooling", "targetCode": "PHY_COOLING", "targetName": "物理降温", "dataType": "string", "unit": "", "priority": 40},
            {"ruleId": "dhcc_pain", "matchField": "fieldName", "matchType": "equals", "matchValue": "PainInten", "targetCode": "PAIN", "targetName": "疼痛评分", "dataType": "number", "unit": "分", "priority": 41},
            {"ruleId": "dhcc_stool", "matchField": "fieldName", "matchType": "equals", "matchValue": "DefFreq", "targetCode": "STOOL", "targetName": "大便次数", "dataType": "number", "unit": "次", "priority": 42},
            {"ruleId": "dhcc_height", "matchField": "fieldName", "matchType": "equals", "matchValue": "Height", "targetCode": "HEIGHT", "targetName": "身高", "dataType": "number", "unit": "cm", "priority": 50},
            {"ruleId": "dhcc_weight", "matchField": "fieldName", "matchType": "equals", "matchValue": "Weight", "targetCode": "WEIGHT", "targetName": "体重", "dataType": "number", "unit": "kg", "priority": 51},
            {"ruleId": "dhcc_input", "matchField": "fieldName", "matchType": "equals", "matchValue": "Liquidln", "targetCode": "TOTAL_INPUT", "targetName": "总入量", "dataType": "number", "unit": "ml", "priority": 60},
            {"ruleId": "dhcc_ingestion", "matchField": "fieldName", "matchType": "equals", "matchValue": "Ingestion", "targetCode": "INGESTION", "targetName": "摄入量", "dataType": "number", "unit": "ml", "priority": 61},
            {"ruleId": "dhcc_urine", "matchField": "fieldName", "matchType": "equals", "matchValue": "UriVolume", "targetCode": "URINE", "targetName": "尿量", "dataType": "number", "unit": "ml", "priority": 62},
            {"ruleId": "dhcc_output", "matchField": "fieldName", "matchType": "equals", "matchValue": "LiquidOut", "targetCode": "TOTAL_OUTPUT", "targetName": "总出量", "dataType": "number", "unit": "ml", "priority": 63},
            {"ruleId": "dhcc_barthel", "matchField": "fieldName", "matchType": "equals", "matchValue": "Barthel", "targetCode": "BARTHEL", "targetName": "Barthel评分", "dataType": "number", "unit": "分", "priority": 70},
            {"ruleId": "dhcc_bedsore", "matchField": "fieldName", "matchType": "equals", "matchValue": "Bedsore", "targetCode": "BEDSORE", "targetName": "压疮风险评估", "dataType": "string", "unit": "", "priority": 71},
            {"ruleId": "dhcc_fbs", "matchField": "fieldName", "matchType": "equals", "matchValue": "FBS", "targetCode": "FBS", "targetName": "空腹血糖", "dataType": "number", "unit": "mmol/L", "priority": 80},
        ],
    },

    # =================================================================
    # 2. 中联 HIS S8009 (JSON)
    # =================================================================
    {
        "profileCode": "zhonglian_json",
        "profileName": "中联 HIS S8009 (JSON)",
        "description": "中联医疗 HIS 系统（S8009 接口），通过 HTTP POST 推送 JSON 格式的体温单数据。"
                       "数据结构为 {input: {head: {action_no, bizno, sysno, tarno, time}, "
                       "pat_list: [{pid, inpno, pvid, data_time, ward_id, user_name, item_list}]}}。",
        "tags": ["JSON", "中联", "S8009", "HTTP Push"],
        "accessType": "http_push",
        "vendorTemplate": {
            "accessType": "http_push",
            "description": "中联 HIS S8009 JSON 接入",
        },
        "accessConfigTemplate": {
            "accessType": "http_push",
            "httpPushConfig": {
                "endpointPath": "/api/push/{vendor_code}",
                "authType": "none",
            },
        },
        "parserConfigTemplate": {
            "dataFormat": "json",
            "encoding": "UTF-8",
            "rootPath": "$.input",
            "recordPath": "$.input.pat_list[*]",
            "itemPath": "item_list[*]",
            "recordPathType": "jsonpath",
            "itemPathType": "jsonpath",
            "rootFieldMappings": {
                "actionNo": {"sourcePath": "$.input.head.action_no", "dataType": "string"},
                "bizNo": {"sourcePath": "$.input.head.bizno", "dataType": "string"},
                "sysNo": {"sourcePath": "$.input.head.sysno", "dataType": "string"},
                "tarNo": {"sourcePath": "$.input.head.tarno", "dataType": "string"},
            },
            "recordFieldMappings": {
                "patientId": {"sourcePath": "$.pid", "dataType": "string"},
                "visitNo": {"sourcePath": "$.inpno", "dataType": "string"},
                "patientVisitId": {"sourcePath": "$.pvid", "dataType": "string"},
                "wardCode": {"sourcePath": "$.ward_id", "dataType": "string"},
                "recordTime": {"sourcePath": "$.data_time", "dataType": "datetime", "dateFormat": "yyyy-MM-dd HH:mm:ss"},
                "operatorName": {"sourcePath": "$.user_name", "dataType": "string"},
            },
            "itemFieldMappings": {
                "itemCode": {"sourcePath": "$.item_id"},
                "itemName": {"sourcePath": "$.item_name"},
                "itemValue": {"sourcePath": "$.item_data"},
            },
        },
        "itemRulesTemplate": [
            {"ruleId": "zl_temp", "matchField": "item_name", "matchType": "exact", "matchValue": "体温", "targetCode": "TEMP", "targetName": "体温", "dataType": "number", "unit": "℃", "priority": 1},
            {"ruleId": "zl_resp", "matchField": "item_name", "matchType": "exact", "matchValue": "呼吸", "targetCode": "RESP", "targetName": "呼吸", "dataType": "number", "unit": "次/分", "priority": 10},
            {"ruleId": "zl_hr", "matchField": "item_name", "matchType": "exact", "matchValue": "心率", "targetCode": "HR", "targetName": "心率", "dataType": "number", "unit": "次/分", "priority": 11},
            {"ruleId": "zl_bp_sys", "matchField": "item_name", "matchType": "exact", "matchValue": "收缩压", "targetCode": "SYS_BP", "targetName": "收缩压", "dataType": "number", "unit": "mmHg", "priority": 20},
            {"ruleId": "zl_bp_dia", "matchField": "item_name", "matchType": "exact", "matchValue": "舒张压", "targetCode": "DIA_BP", "targetName": "舒张压", "dataType": "number", "unit": "mmHg", "priority": 21},
            {"ruleId": "zl_stool", "matchField": "item_name", "matchType": "exact", "matchValue": "大便量", "targetCode": "STOOL", "targetName": "大便量", "dataType": "number", "unit": "", "priority": 40},
        ],
    },

    # =================================================================
    # 3. 通用 JSON HTTP Push
    # =================================================================
    {
        "profileCode": "generic_json_push",
        "profileName": "通用 JSON HTTP Push",
        "description": "通用的 JSON 格式 HTTP Push 接入模板。适用于自行开发的系统或标准 REST API。"
                       "选择后需要根据实际数据格式调整字段映射。",
        "tags": ["JSON", "HTTP Push", "通用"],
        "accessType": "http_push",
        "vendorTemplate": {
            "accessType": "http_push",
        },
        "accessConfigTemplate": {
            "accessType": "http_push",
            "httpPushConfig": {
                "endpointPath": "/api/push/{vendor_code}",
                "authType": "none",
            },
        },
        "parserConfigTemplate": {
            "dataFormat": "json",
            "encoding": "UTF-8",
            "rootPath": "$",
            "recordPath": "$.records[*]",
            "itemPath": "items[*]",
            "recordPathType": "jsonpath",
            "itemPathType": "jsonpath",
            "rootFieldMappings": {},
            "recordFieldMappings": {
                "patientId": {"sourcePath": "$.patientId", "dataType": "string"},
                "visitNo": {"sourcePath": "$.visitNo", "dataType": "string"},
                "wardCode": {"sourcePath": "$.wardCode", "dataType": "string"},
                "recordTime": {"sourcePath": "$.recordTime", "dataType": "datetime"},
            },
            "itemFieldMappings": {
                "itemCode": {"sourcePath": "$.code"},
                "itemName": {"sourcePath": "$.name"},
                "itemValue": {"sourcePath": "$.value"},
            },
        },
        "itemRulesTemplate": [
            {"ruleId": "gen_temp", "matchField": "name", "matchType": "contains", "matchValue": "体温", "targetCode": "TEMP", "targetName": "体温", "dataType": "number", "unit": "℃", "priority": 1},
            {"ruleId": "gen_pulse", "matchField": "name", "matchType": "contains", "matchValue": "脉搏", "targetCode": "PULSE", "targetName": "脉搏", "dataType": "number", "unit": "次/分", "priority": 10},
            {"ruleId": "gen_resp", "matchField": "name", "matchType": "contains", "matchValue": "呼吸", "targetCode": "RESP", "targetName": "呼吸", "dataType": "number", "unit": "次/分", "priority": 11},
            {"ruleId": "gen_bp", "matchField": "name", "matchType": "contains", "matchValue": "血压", "targetCode": "BP", "targetName": "血压", "dataType": "blood_pressure", "unit": "mmHg", "splitSeparator": "/", "priority": 20},
            {"ruleId": "gen_spo2", "matchField": "name", "matchType": "contains", "matchValue": "血氧", "targetCode": "SPO2", "targetName": "血氧饱和度", "dataType": "number", "unit": "%", "priority": 30},
        ],
    },

    # =================================================================
    # 4. 通用 SOAP/XML
    # =================================================================
    {
        "profileCode": "generic_soap",
        "profileName": "通用 SOAP/XML",
        "description": "通用的 SOAP WebService XML 接入模板。适用于标准 SOAP 协议推送的数据。"
                       "选择后需要根据实际 WSDL 和 XML 结构调整字段映射。",
        "tags": ["SOAP", "XML", "通用"],
        "accessType": "soap_push",
        "vendorTemplate": {
            "accessType": "soap_push",
        },
        "accessConfigTemplate": {
            "accessType": "soap_push",
            "httpPushConfig": {
                "endpointPath": "/api/soap/{vendor_code}",
                "authType": "none",
            },
        },
        "parserConfigTemplate": {
            "dataFormat": "xml",
            "encoding": "UTF-8",
            "rootPath": "/",
            "recordPath": "//record",
            "itemPath": ".",
            "recordPathType": "xpath",
            "itemPathType": "xpath",
            "rootFieldMappings": {},
            "recordFieldMappings": {
                "patientId": {"sourcePath": "patientId", "dataType": "string"},
                "visitNo": {"sourcePath": "visitNo", "dataType": "string"},
                "wardCode": {"sourcePath": "wardCode", "dataType": "string"},
                "recordTime": {"sourcePath": "recordTime", "dataType": "string"},
            },
            "itemFieldMappings": {},
        },
        "itemRulesTemplate": [
            {"ruleId": "soap_temp", "matchField": "fieldName", "matchType": "regex", "matchValue": "(?i)temp", "targetCode": "TEMP", "targetName": "体温", "dataType": "number", "unit": "℃", "priority": 1},
            {"ruleId": "soap_pulse", "matchField": "fieldName", "matchType": "regex", "matchValue": "(?i)pulse|hr", "targetCode": "PULSE", "targetName": "脉搏", "dataType": "number", "unit": "次/分", "priority": 10},
            {"ruleId": "soap_resp", "matchField": "fieldName", "matchType": "regex", "matchValue": "(?i)breath|resp", "targetCode": "RESP", "targetName": "呼吸", "dataType": "number", "unit": "次/分", "priority": 11},
            {"ruleId": "soap_bp_sys", "matchField": "fieldName", "matchType": "regex", "matchValue": "(?i)sys.*press", "targetCode": "SYS_BP", "targetName": "收缩压", "dataType": "number", "unit": "mmHg", "priority": 20},
            {"ruleId": "soap_bp_dia", "matchField": "fieldName", "matchType": "regex", "matchValue": "(?i)dia.*press", "targetCode": "DIA_BP", "targetName": "舒张压", "dataType": "number", "unit": "mmHg", "priority": 21},
            {"ruleId": "soap_spo2", "matchField": "fieldName", "matchType": "regex", "matchValue": "(?i)spo2|blood", "targetCode": "SPO2", "targetName": "血氧饱和度", "dataType": "number", "unit": "%", "priority": 30},
        ],
    },

    # =================================================================
    # 5. 通用 JSON HTTP Pull
    # =================================================================
    {
        "profileCode": "generic_json_pull",
        "profileName": "通用 JSON HTTP Pull",
        "description": "通用的 JSON 格式 HTTP Pull 接入模板。平台定时从厂家 API 拉取数据。"
                       "选择后需要配置拉取地址和认证信息。",
        "tags": ["JSON", "HTTP Pull", "定时拉取", "通用"],
        "accessType": "http_pull",
        "vendorTemplate": {
            "accessType": "http_pull",
        },
        "accessConfigTemplate": {
            "accessType": "http_pull",
            "httpPullConfig": {
                "url": "http://vendor-api.example.com/api/vitals",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "bodyTemplate": '{"startDate": "{{startDate}}", "endDate": "{{endDate}}"}',
                "cronExpression": "*/5 * * * *",
                "timeout": 30,
            },
        },
        "parserConfigTemplate": {
            "dataFormat": "json",
            "encoding": "UTF-8",
            "rootPath": "$",
            "recordPath": "$.data[*]",
            "itemPath": "items[*]",
            "recordPathType": "jsonpath",
            "itemPathType": "jsonpath",
            "rootFieldMappings": {},
            "recordFieldMappings": {
                "patientId": {"sourcePath": "$.patientId", "dataType": "string"},
                "visitNo": {"sourcePath": "$.visitNo", "dataType": "string"},
                "wardCode": {"sourcePath": "$.wardCode", "dataType": "string"},
                "recordTime": {"sourcePath": "$.recordTime", "dataType": "datetime"},
            },
            "itemFieldMappings": {
                "itemCode": {"sourcePath": "$.code"},
                "itemName": {"sourcePath": "$.name"},
                "itemValue": {"sourcePath": "$.value"},
            },
        },
        "itemRulesTemplate": [
            {"ruleId": "pull_temp", "matchField": "name", "matchType": "contains", "matchValue": "体温", "targetCode": "TEMP", "targetName": "体温", "dataType": "number", "unit": "℃", "priority": 1},
            {"ruleId": "pull_pulse", "matchField": "name", "matchType": "contains", "matchValue": "脉搏", "targetCode": "PULSE", "targetName": "脉搏", "dataType": "number", "unit": "次/分", "priority": 10},
            {"ruleId": "pull_resp", "matchField": "name", "matchType": "contains", "matchValue": "呼吸", "targetCode": "RESP", "targetName": "呼吸", "dataType": "number", "unit": "次/分", "priority": 11},
            {"ruleId": "pull_bp", "matchField": "name", "matchType": "contains", "matchValue": "血压", "targetCode": "BP", "targetName": "血压", "dataType": "blood_pressure", "unit": "mmHg", "splitSeparator": "/", "priority": 20},
        ],
    },

    # =================================================================
    # 6. 迈瑞 监护仪 (JSON)
    # =================================================================
    {
        "profileCode": "mindray_json",
        "profileName": "迈瑞监护仪 (JSON)",
        "description": "迈瑞医疗监护设备，通过 HTTP 推送 JSON 格式的体征数据。"
                       "适用于 BeneView 系列监护仪的数据导出。",
        "tags": ["JSON", "迈瑞", "Mindray", "监护仪", "HTTP Push"],
        "accessType": "http_push",
        "vendorTemplate": {
            "accessType": "http_push",
            "description": "迈瑞监护仪 JSON 接入",
        },
        "accessConfigTemplate": {
            "accessType": "http_push",
            "httpPushConfig": {
                "endpointPath": "/api/push/{vendor_code}",
                "authType": "none",
            },
        },
        "parserConfigTemplate": {
            "dataFormat": "json",
            "encoding": "UTF-8",
            "rootPath": "$",
            "recordPath": "$.vitalSigns[*]",
            "itemPath": "measurements[*]",
            "recordPathType": "jsonpath",
            "itemPathType": "jsonpath",
            "rootFieldMappings": {},
            "recordFieldMappings": {
                "patientId": {"sourcePath": "$.patientId", "dataType": "string"},
                "visitNo": {"sourcePath": "$.admissionNo", "dataType": "string"},
                "wardCode": {"sourcePath": "$.wardCode", "dataType": "string"},
                "bedNo": {"sourcePath": "$.bedNo", "dataType": "string"},
                "recordTime": {"sourcePath": "$.measureTime", "dataType": "datetime", "dateFormat": "yyyy-MM-dd HH:mm:ss"},
            },
            "itemFieldMappings": {
                "itemCode": {"sourcePath": "$.paramCode"},
                "itemName": {"sourcePath": "$.paramName"},
                "itemValue": {"sourcePath": "$.value"},
            },
        },
        "itemRulesTemplate": [
            {"ruleId": "mr_temp", "matchField": "paramCode", "matchType": "equals", "matchValue": "Temp", "targetCode": "TEMP", "targetName": "体温", "dataType": "number", "unit": "℃", "priority": 1},
            {"ruleId": "mr_pulse", "matchField": "paramCode", "matchType": "equals", "matchValue": "HR", "targetCode": "PULSE", "targetName": "脉搏", "dataType": "number", "unit": "次/分", "priority": 10},
            {"ruleId": "mr_resp", "matchField": "paramCode", "matchType": "equals", "matchValue": "RR", "targetCode": "RESP", "targetName": "呼吸", "dataType": "number", "unit": "次/分", "priority": 11},
            {"ruleId": "mr_spo2", "matchField": "paramCode", "matchType": "equals", "matchValue": "SpO2", "targetCode": "SPO2", "targetName": "血氧饱和度", "dataType": "number", "unit": "%", "priority": 30},
            {"ruleId": "mr_bp_sys", "matchField": "paramCode", "matchType": "equals", "matchValue": "SysBP", "targetCode": "SYS_BP", "targetName": "收缩压", "dataType": "number", "unit": "mmHg", "priority": 20},
            {"ruleId": "mr_bp_dia", "matchField": "paramCode", "matchType": "equals", "matchValue": "DiaBP", "targetCode": "DIA_BP", "targetName": "舒张压", "dataType": "number", "unit": "mmHg", "priority": 21},
        ],
    },

    # =================================================================
    # 7. 自定义 (空白模板)
    # =================================================================
    {
        "profileCode": "custom",
        "profileName": "自定义配置",
        "description": "从零开始手动配置。适用于没有内置模板的厂家系统。"
                       "需要自行配置数据格式、字段映射和匹配规则。",
        "tags": ["自定义", "手动配置"],
        "accessType": "http_push",
        "vendorTemplate": {},
        "accessConfigTemplate": {},
        "parserConfigTemplate": {},
        "itemRulesTemplate": [],
    },
]
