import request from './request'

// ============================================================
// 数据源配置
// ============================================================

/** 获取 SmartCare 数据源列表 */
export const getDatasources = (params?: Record<string, any>) =>
  request.get('/api/smartcare/datasource/list', { params })

/** 获取单个数据源 */
export const getDatasource = (id: number) =>
  request.get(`/api/smartcare/datasource/${id}`)

/** 创建数据源 */
export const createDatasource = (data: Record<string, any>) =>
  request.post('/api/smartcare/datasource', data)

/** 更新数据源 */
export const updateDatasource = (id: number, data: Record<string, any>) =>
  request.put(`/api/smartcare/datasource/${id}`, data)

/** 删除数据源 */
export const deleteDatasource = (id: number) =>
  request.delete(`/api/smartcare/datasource/${id}`)

/** 测试数据源连接 */
export const testDatasource = (id: number) =>
  request.post(`/api/smartcare/datasource/${id}/test`)

// ============================================================
// 配置参数
// ============================================================

/** 获取配置参数列表 */
export const getConfigParams = (datasourceId: number, params?: Record<string, any>) =>
  request.get(`/api/smartcare/datasource/${datasourceId}/config-params`, { params })

/** 同步配置参数 */
export const syncConfigParams = (datasourceId: number) =>
  request.post(`/api/smartcare/datasource/${datasourceId}/config-params/sync`)

// ============================================================
// 字段映射
// ============================================================

/** 获取字段映射列表 */
export const getFieldMappings = (params?: Record<string, any>) =>
  request.get('/api/smartcare/field-mapping/list', { params })

/** 保存字段映射 */
export const saveFieldMapping = (data: Record<string, any>) =>
  request.post('/api/smartcare/field-mapping', data)

/** 删除字段映射 */
export const deleteFieldMapping = (id: number) =>
  request.delete(`/api/smartcare/field-mapping/${id}`)

/** 批量保存字段映射 */
export const batchSaveFieldMappings = (datasourceId: number, mappings: Record<string, any>[]) =>
  request.post(`/api/smartcare/field-mapping/batch`, { datasource_id: datasourceId, mappings })

// ============================================================
// 患者 & 床旁数据
// ============================================================

/** 获取患者列表 */
export const getPatients = (datasourceId: number, params?: Record<string, any>) =>
  request.get(`/api/smartcare/datasource/${datasourceId}/patients`, { params })

/** 获取床旁数据 */
export const getBedsideData = (datasourceId: number, params?: Record<string, any>) =>
  request.get(`/api/smartcare/datasource/${datasourceId}/bedside`, { params })
