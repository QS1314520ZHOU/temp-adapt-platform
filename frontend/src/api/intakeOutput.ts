import request from './request'

// ============================================================
// 出入量项目配置
// ============================================================

/** 获取出入量项目列表 */
export const getItemConfigs = (params?: Record<string, any>) =>
  request.get('/api/intake-output/item-config/list', { params })

/** 获取单个项目配置 */
export const getItemConfig = (id: number) =>
  request.get(`/api/intake-output/item-config/${id}`)

/** 创建项目配置 */
export const createItemConfig = (data: Record<string, any>) =>
  request.post('/api/intake-output/item-config', data)

/** 更新项目配置 */
export const updateItemConfig = (id: number, data: Record<string, any>) =>
  request.put(`/api/intake-output/item-config/${id}`, data)

/** 删除项目配置 */
export const deleteItemConfig = (id: number) =>
  request.delete(`/api/intake-output/item-config/${id}`)

// ============================================================
// 统计规则
// ============================================================

/** 获取统计规则列表 */
export const getStatRules = (params?: Record<string, any>) =>
  request.get('/api/intake-output/stat-rule/list', { params })

/** 获取单个统计规则 */
export const getStatRule = (id: number) =>
  request.get(`/api/intake-output/stat-rule/${id}`)

/** 创建统计规则 */
export const createStatRule = (data: Record<string, any>) =>
  request.post('/api/intake-output/stat-rule', data)

/** 更新统计规则 */
export const updateStatRule = (id: number, data: Record<string, any>) =>
  request.put(`/api/intake-output/stat-rule/${id}`, data)

/** 删除统计规则 */
export const deleteStatRule = (id: number) =>
  request.delete(`/api/intake-output/stat-rule/${id}`)

// ============================================================
// 预览 & 计算 & 结果
// ============================================================

/** 预览出入量数据 */
export const previewIntakeOutput = (params?: Record<string, any>) =>
  request.get('/api/intake-output/preview', { params })

/** 执行出入量计算 */
export const calculateIntakeOutput = (data: Record<string, any>) =>
  request.post('/api/intake-output/calculate', data)

/** 获取计算结果列表 */
export const getResults = (params?: Record<string, any>) =>
  request.get('/api/intake-output/results', { params })

/** 获取出入量日志 */
export const getIntakeOutputLogs = (params?: Record<string, any>) =>
  request.get('/api/intake-output/logs', { params })
