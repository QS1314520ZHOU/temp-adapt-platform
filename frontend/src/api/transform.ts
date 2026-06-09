import request from './request'

/** 拉取原始数据 */
export const pullRawData = (data: { vendor_code: string; access_config_id?: number }) =>
  request.post('/api/transform/pull', data)

/** 执行转换 */
export const transformData = (data: { raw_record_ids?: number[]; vendor_code?: string }) =>
  request.post('/api/transform/run', data)

/** 重试单条记录 */
export const retryTransform = (retryTaskId: number) =>
  request.post(`/api/transform/retry/${retryTaskId}`)

/** 批量重试 */
export const batchRetryTransform = (data: { retry_task_ids: number[] }) =>
  request.post('/api/transform/batch-retry', data)

/** 获取重试任务列表 */
export const getRetryTasks = (params?: Record<string, any>) =>
  request.get('/api/transform/retry-tasks', { params })
