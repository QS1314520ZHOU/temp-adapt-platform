"""XML 记录转换器 - 将 XML 字段转换为标准指标格式"""
import logging
from typing import Any, Dict, List, Optional
from lxml import etree

logger = logging.getLogger(__name__)


class XmlRecordTransformer:
    """将 XML 记录中的字段转换为标准指标列表

    适用于 SOAP/XML 格式的数据，其中每个字段（如 Temperature, Pulse 等）
    直接作为 XML 元素存在，而不是作为数组中的对象。
    """

    # 需要提取的字段及其对应的指标代码
    VITAL_FIELDS = {
        'Temperature': {'code': 'TEMP', 'name': '腋温', 'unit': '℃'},
        'RecTemperature': {'code': 'TEMP_RECTAL', 'name': '肛温', 'unit': '℃'},
        'oraltemperature': {'code': 'TEMP_ORAL', 'name': '口温', 'unit': '℃'},
        'eartemperature': {'code': 'TEMP_EAR', 'name': '耳温', 'unit': '℃'},
        'Pulse': {'code': 'PULSE', 'name': '脉搏', 'unit': '次/分'},
        'Breath': {'code': 'RESP', 'name': '呼吸', 'unit': '次/分'},
        'BreathB': {'code': 'RESP_MACHINE', 'name': '机控呼吸', 'unit': '次/分'},
        'SysPressure': {'code': 'SYS_BP', 'name': '收缩压', 'unit': 'mmHg'},
        'DiaPressure': {'code': 'DIA_BP', 'name': '舒张压', 'unit': 'mmHg'},
        'DegrBlood': {'code': 'SPO2', 'name': '血氧饱和度', 'unit': '%'},
        'Heartbeat': {'code': 'HR', 'name': '心率', 'unit': '次/分'},
        'PhyCooling': {'code': 'PHY_COOLING', 'name': '物理降温', 'unit': ''},
        'PainInten': {'code': 'PAIN', 'name': '疼痛评分', 'unit': '分'},
        'DefFreq': {'code': 'STOOL', 'name': '大便次数', 'unit': '次'},
        'Height': {'code': 'HEIGHT', 'name': '身高', 'unit': 'cm'},
        'Weight': {'code': 'WEIGHT', 'name': '体重', 'unit': 'kg'},
        'Liquidln': {'code': 'TOTAL_INPUT', 'name': '总入量', 'unit': 'ml'},
        'Ingestion': {'code': 'INGESTION', 'name': '摄入量', 'unit': 'ml'},
        'UriVolume': {'code': 'URINE', 'name': '尿量', 'unit': 'ml'},
        'LiquidOut': {'code': 'TOTAL_OUTPUT', 'name': '总出量', 'unit': 'ml'},
        'Barthel': {'code': 'BARTHEL', 'name': 'Barthel评分', 'unit': '分'},
        'Bedsore': {'code': 'BEDSORE', 'name': '压疮风险评估', 'unit': ''},
        'FBS': {'code': 'FBS', 'name': '空腹血糖', 'unit': 'mmol/L'},
    }

    @classmethod
    def extract_items_from_xml(cls, xml_element) -> List[Dict[str, Any]]:
        """从 XML 元素中提取指标列表

        Args:
            xml_element: lxml Element 对象（EStatusParameter 节点）

        Returns:
            指标列表，每个指标包含 code, name, value, unit
        """
        items = []

        for field_name, field_info in cls.VITAL_FIELDS.items():
            value_elem = xml_element.find(field_name)
            if value_elem is not None and value_elem.text:
                value_text = value_elem.text.strip()
                if value_text:  # 只提取非空值
                    items.append({
                        'fieldName': field_name,
                        'code': field_info['code'],
                        'name': field_info['name'],
                        'value': value_text,
                        'unit': field_info['unit'],
                        'matched': True,
                        'source': 'xml_field'
                    })

        return items

    @classmethod
    def extract_record_fields(cls, xml_element) -> Dict[str, Any]:
        """从 XML 元素中提取记录字段

        Args:
            xml_element: lxml Element 对象（EStatusParameter 节点）

        Returns:
            记录字段字典
        """
        fields = {}

        # 提取基础字段
        field_mapping = {
            'PATPatientID': 'patientId',
            'PAADMVisitNumber': 'visitNo',
            'WARDCode': 'wardCode',
            'Date': 'recordDate',
            'Time': 'recordTime',
            'UpdateUserCode': 'operatorCode',
            'UpdateUserName': 'operatorName',
            'UpdateDate': 'updateDate',
            'UpdateTime': 'updateTime',
        }

        for xml_field, target_field in field_mapping.items():
            elem = xml_element.find(xml_field)
            if elem is not None and elem.text:
                fields[target_field] = elem.text.strip()

        # 组合日期和时间
        if fields.get('recordDate') and fields.get('recordTime'):
            fields['recordTime'] = f"{fields['recordDate']} {fields['recordTime']}"

        return fields

    @classmethod
    def transform_xml_to_records(cls, xml_data: str, record_path: str = '/Request/Body/EStatusParameter') -> List[Dict[str, Any]]:
        """将 XML 数据转换为标准记录格式

        Args:
            xml_data: XML 字符串
            record_path: 记录的 XPath 路径

        Returns:
            记录列表，每个记录包含字段和指标
        """
        try:
            root = etree.fromstring(xml_data.encode('utf-8'))
            records = []

            # 查找所有记录
            for record_elem in root.xpath(record_path):
                # 提取记录字段
                record_fields = cls.extract_record_fields(record_elem)

                # 提取指标列表
                items = cls.extract_items_from_xml(record_elem)

                # 构建完整记录
                record = {
                    **record_fields,
                    'items': items,
                    'itemCount': len(items)
                }
                records.append(record)

            return records

        except Exception as e:
            logger.error("XML转换失败: %s", e)
            return []
