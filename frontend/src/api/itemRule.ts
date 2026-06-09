import request from './request'

/** 获取指标规则列表 */
export const getItemRules = (params?: Record<string, any>) =>
  request.get('/api/item-rule/list', { params })

/** 获取单个指标规则 */
export const getItemRule = (id: number) =>
  request.get(`/api/item-rule/${id}`)

/** 保存指标规则（新建或更新） */
export const saveItemRule = (data: Record<string, any>) =>
  request.post('/api/item-rule', data)

/** 删除指标规则 */
export const deleteItemRule = (id: number) =>
  request.delete(`/api/item-rule/${id}`)

/** 添加规则到指定厂家 */
export const addItemRule = (vendorCode: string, data: Record<string, any>) =>
  request.post(`/api/item-rule/vendor/${vendorCode}`, data)

/** 删除指定厂家下的规则 */
export const deleteItemRuleFromVendor = (vendorCode: string, ruleId: number) =>
  request.delete(`/api/item-rule/vendor/${vendorCode}/${ruleId}`)

/** 预览指标映射效果 */
export const previewItemRule = (params?: Record<string, any>) =>
  request.get('/api/item-rule/preview', { params })
