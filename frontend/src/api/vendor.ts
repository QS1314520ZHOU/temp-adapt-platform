import request from './request'

/** 获取厂家列表 */
export const getVendors = (params?: Record<string, any>) =>
  request.get('/api/vendor/list', { params })

/** 获取单个厂家详情 */
export const getVendor = (code: string) =>
  request.get(`/api/vendor/${code}`)

/** 创建厂家 */
export const createVendor = (data: Record<string, any>) =>
  request.post('/api/vendor', data)

/** 更新厂家 */
export const updateVendor = (code: string, data: Record<string, any>) =>
  request.put(`/api/vendor/${code}`, data)

/** 删除厂家 */
export const deleteVendor = (code: string) =>
  request.delete(`/api/vendor/${code}`)

/** 切换厂家启用/禁用 */
export const toggleVendor = (code: string, enabled: boolean) =>
  request.put(`/api/vendor/${code}/toggle`, { enabled })
