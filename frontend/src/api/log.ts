import request from './request'

/** 查询原始记录 */
export const getRawRecords = (params?: Record<string, any>) =>
  request.get('/api/log/raw-records', { params })

/** 查询温度记录 */
export const getTemperatureRecords = (params?: Record<string, any>) =>
  request.get('/api/log/temperature-records', { params })

/** 查询转换日志 */
export const getTransformLogs = (params?: Record<string, any>) =>
  request.get('/api/log/transform-logs', { params })

/** 查询未识别指标 */
export const getUnmatchedItems = (params?: Record<string, any>) =>
  request.get('/api/log/unmatched-items', { params })

/** 查询重试任务 */
export const getRetryTasks = (params?: Record<string, any>) =>
  request.get('/api/log/retry-tasks', { params })
