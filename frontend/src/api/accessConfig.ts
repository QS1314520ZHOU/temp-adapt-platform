import request from './request'

/** 获取接入配置列表 */
export const getAccessConfigs = (params?: Record<string, any>) =>
  request.get('/api/access-config/list', { params })

/** 获取单个接入配置 */
export const getAccessConfig = (id: number) =>
  request.get(`/api/access-config/${id}`)

/** 创建接入配置 */
export const createAccessConfig = (data: Record<string, any>) =>
  request.post('/api/access-config', data)

/** 更新接入配置 */
export const updateAccessConfig = (id: number, data: Record<string, any>) =>
  request.put(`/api/access-config/${id}`, data)

/** 删除接入配置 */
export const deleteAccessConfig = (id: number) =>
  request.delete(`/api/access-config/${id}`)

/** 测试接入连接 */
export const testAccessConfig = (id: number) =>
  request.post(`/api/access-config/${id}/test`)

/** 预览接入数据 */
export const previewAccessConfig = (id: number, params?: Record<string, any>) =>
  request.get(`/api/access-config/${id}/preview`, { params })
