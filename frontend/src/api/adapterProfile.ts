import request from './request'

/** 获取所有适配器模板 */
export const getAdapterProfiles = () =>
  request.get('/api/adapter-profile/list')

/** 获取单个模板详情 */
export const getAdapterProfile = (profileCode: string) =>
  request.get(`/api/adapter-profile/${profileCode}`)

/** 应用模板到厂家 */
export const applyAdapterProfile = (data: {
  profileCode: string
  vendorCode: string
  vendorName: string
  hospitalCode?: string
}) => request.post('/api/adapter-profile/apply', data)

/** 保存自定义模板 */
export const saveAdapterProfile = (data: Record<string, any>) =>
  request.post('/api/adapter-profile/save', data)

/** 从现有厂家保存为模板 */
export const saveFromVendor = (data: {
  vendorCode: string
  profileCode: string
  profileName: string
  description?: string
  tags?: string[]
}) => request.post('/api/adapter-profile/save-from-vendor', data)

/** 删除自定义模板 */
export const deleteAdapterProfile = (profileCode: string) =>
  request.delete(`/api/adapter-profile/${profileCode}`)
