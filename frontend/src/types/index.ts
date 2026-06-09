// ============================================================
// 通用响应类型
// ============================================================

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T = any> {
  total: number
  page: number
  page_size: number
  items: T[]
}

// ============================================================
// 厂家配置
// ============================================================

export interface VendorConfig {
  code: string
  name: string
  description?: string
  enabled: boolean
  created_at?: string
  updated_at?: string
}

// ============================================================
// 接入配置
// ============================================================

export interface AccessConfig {
  id?: number
  vendor_code: string
  name: string
  protocol: 'http' | 'tcp' | 'mqtt' | 'file'
  endpoint?: string
  port?: number
  auth_type?: string
  auth_config?: Record<string, any>
  enabled: boolean
  description?: string
  created_at?: string
  updated_at?: string
}

// ============================================================
// 报文解析配置
// ============================================================

export interface ParserConfig {
  id?: number
  vendor_code: string
  name: string
  format: 'json' | 'xml' | 'hl7' | 'csv' | 'custom'
  encoding?: string
  root_path?: string
  field_mappings: FieldMapping[]
  description?: string
  created_at?: string
  updated_at?: string
}

export interface FieldMapping {
  source_field: string
  source_path?: string
  target_field: string
  transform?: string
  default_value?: string
  description?: string
}

// ============================================================
// 指标规则
// ============================================================

export interface ItemMappingRule {
  id?: number
  vendor_code: string
  source_item_name: string
  source_item_code?: string
  target_item_code: string
  target_item_name: string
  unit?: string
  conversion_factor?: number
  value_range_min?: number
  value_range_max?: number
  description?: string
  created_at?: string
  updated_at?: string
}

// ============================================================
// 原始记录 & 转换结果
// ============================================================

export interface RawRecord {
  id: number
  vendor_code: string
  access_config_id: number
  raw_data: string
  received_at: string
  status: 'pending' | 'parsed' | 'failed' | 'transformed'
  error_message?: string
}

export interface TemperatureRecord {
  id: number
  raw_record_id: number
  patient_id: string
  patient_name?: string
  visit_id?: string
  record_time: string
  source_vendor: string
  items: TemperatureItem[]
  status: 'success' | 'partial' | 'failed'
  created_at: string
}

export interface TemperatureItem {
  item_code: string
  item_name: string
  value: number | string
  unit?: string
  record_time: string
}

export interface UnmatchedItem {
  id: number
  vendor_code: string
  source_item_name: string
  source_item_code?: string
  raw_value?: string
  raw_record_id: number
  patient_id?: string
  record_time?: string
  created_at: string
}

// ============================================================
// 转换日志 & 重试任务
// ============================================================

export interface TransformLog {
  id: number
  raw_record_id: number
  temperature_record_id?: number
  vendor_code: string
  action: 'parse' | 'transform' | 'push' | 'retry'
  status: 'success' | 'failed'
  message?: string
  duration_ms?: number
  created_at: string
}

export interface RetryTask {
  id: number
  raw_record_id: number
  vendor_code: string
  retry_count: number
  max_retries: number
  next_retry_at?: string
  last_error?: string
  status: 'pending' | 'running' | 'success' | 'failed' | 'exhausted'
  created_at: string
  updated_at: string
}

// ============================================================
// SmartCare 数据源
// ============================================================

export interface SmartCareDatasourceConfig {
  id?: number
  name: string
  db_type: 'mysql' | 'oracle' | 'sqlserver' | 'postgresql'
  host: string
  port: number
  database_name: string
  username: string
  password?: string
  description?: string
  enabled: boolean
  created_at?: string
  updated_at?: string
}

export interface SmartCareFieldMapping {
  id?: number
  datasource_id: number
  source_table: string
  source_field: string
  target_field: string
  field_type?: string
  transform_expression?: string
  description?: string
  created_at?: string
  updated_at?: string
}

// ============================================================
// 出入量配置
// ============================================================

export interface IntakeOutputItemConfig {
  id?: number
  item_code: string
  item_name: string
  category: 'intake' | 'output'
  unit?: string
  default_value?: number
  sort_order?: number
  enabled: boolean
  description?: string
  created_at?: string
  updated_at?: string
}

export interface IntakeOutputStatRule {
  id?: number
  rule_name: string
  item_codes: string[]
  stat_type: 'sum' | 'avg' | 'max' | 'min' | 'count'
  time_range: 'shift' | 'day' | 'custom'
  custom_hours?: number
  description?: string
  enabled: boolean
  created_at?: string
  updated_at?: string
}

export interface IntakeOutputResult {
  id: number
  patient_id: string
  patient_name?: string
  visit_id?: string
  record_time: string
  stat_time_start: string
  stat_time_end: string
  item_code: string
  item_name: string
  category: 'intake' | 'output'
  value: number
  unit?: string
  rule_id?: number
  created_at: string
}
