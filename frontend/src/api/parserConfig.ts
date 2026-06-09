import request from './request'

/** 获取解析配置列表 */
export const getParserConfigs = (params?: Record<string, any>) =>
  request.get('/api/parser/list', { params })

/** 获取单个解析配置 */
export const getParserConfig = (id: number) =>
  request.get(`/api/parser/${id}`)

/** 保存解析配置（新建或更新） */
export const saveParserConfig = (data: Record<string, any>) =>
  request.post('/api/parser', data)

/** 删除解析配置 */
export const deleteParserConfig = (id: number) =>
  request.delete(`/api/parser/${id}`)

/** 测试 JSONPath 表达式 */
export const testJsonPath = (data: { expression: string; sample_data: string }) =>
  request.post('/api/parser/test-jsonpath', data)

/** 测试 XPath 表达式 */
export const testXPath = (data: { expression: string; sample_data: string }) =>
  request.post('/api/parser/test-xpath', data)

/** 预览字段映射结果 */
export const previewMapping = (id: number, params?: Record<string, any>) =>
  request.get(`/api/parser/${id}/preview-mapping`, { params })
