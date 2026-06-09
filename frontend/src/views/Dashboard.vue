<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon received">
              <el-icon><Download /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日接收数</div>
              <div class="stat-value">{{ stats.todayReceived }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日成功数</div>
              <div class="stat-value">{{ stats.todaySuccess }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon failed">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日失败数</div>
              <div class="stat-value">{{ stats.todayFailed }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon unknown">
              <el-icon><QuestionFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日未识别数</div>
              <div class="stat-value">{{ stats.todayUnrecognized }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon timer">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">定时任务数</div>
              <div class="stat-value">{{ stats.schedulerJobs }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sync">
              <el-icon><Refresh /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日同步数</div>
              <div class="stat-value">{{ stats.todaySyncCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon callback">
              <el-icon><Promotion /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日回传数</div>
              <div class="stat-value">{{ stats.todayCallbackCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon callback-failed">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日回传失败数</div>
              <div class="stat-value">{{ stats.todayCallbackFailed }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 厂家状态列表 -->
    <el-row :gutter="20" class="content-row">
      <el-col :span="12">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <span>厂家状态</span>
            </div>
          </template>
          <el-table :data="vendorList" stripe style="width: 100%" max-height="400">
            <el-table-column prop="vendorCode" label="厂家编码" width="120" />
            <el-table-column prop="vendorName" label="厂家名称" min-width="150" />
            <el-table-column prop="enabled" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
                  {{ row.enabled ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastReceiveTime" label="最近接收时间" min-width="160">
              <template #default="{ row }">
                {{ row.lastReceiveTime || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 最近日志 -->
      <el-col :span="12">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <span>最近转换日志</span>
              <el-button type="primary" link @click="refreshLogs">刷新</el-button>
            </div>
          </template>
          <el-table :data="recentLogs" stripe style="width: 100%" max-height="400">
            <el-table-column prop="vendorCode" label="厂家编码" width="120" />
            <el-table-column prop="receiveTime" label="接收时间" min-width="160" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 定时任务状态 -->
    <el-row :gutter="20" class="content-row">
      <el-col :span="24">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <span>定时任务状态</span>
              <el-button type="primary" link @click="fetchSchedulerJobs">刷新</el-button>
            </div>
          </template>
          <el-table :data="schedulerJobs" stripe style="width: 100%" max-height="400">
            <el-table-column prop="id" label="任务ID" min-width="200" />
            <el-table-column prop="name" label="任务名称" min-width="150" />
            <el-table-column prop="next_run_time" label="下次执行时间" width="180" />
            <el-table-column prop="trigger" label="触发器" min-width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Download, CircleCheck, CircleClose, QuestionFilled, Timer, Refresh, Promotion, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// 统计数据
const stats = reactive({
  todayReceived: 0,
  todaySuccess: 0,
  todayFailed: 0,
  todayUnrecognized: 0,
  schedulerJobs: 0,
  todaySyncCount: 0,
  todayCallbackCount: 0,
  todayCallbackFailed: 0
})

// 定时任务列表
interface SchedulerJob {
  id: string
  name: string
  next_run_time: string
  trigger: string
  status: string
}

const schedulerJobs = ref<SchedulerJob[]>([])

// 获取定时任务列表
const fetchSchedulerJobs = async () => {
  try {
    const res = await request.get('/api/scheduler/jobs')
    const data = res.data?.data || res.data
    schedulerJobs.value = Array.isArray(data) ? data : data?.items || data?.list || []
  } catch {
    schedulerJobs.value = []
  }
}

// 厂家列表
interface Vendor {
  vendorCode: string
  vendorName: string
  enabled: boolean
  lastReceiveTime: string | null
}

const vendorList = ref<Vendor[]>([])

// 日志列表
interface TransformLog {
  vendorCode: string
  receiveTime: string
  status: string
  message: string
}

const recentLogs = ref<TransformLog[]>([])
const loading = ref(false)

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    unrecognized: 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    success: '成功',
    failed: '失败',
    unrecognized: '未识别'
  }
  return labelMap[status] || status
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await request.get('/api/dashboard/stats')
    const data = res.data?.data || res.data
    if (data) {
      Object.assign(stats, data)
    }
  } catch {
    // 模拟数据，实际应调用API
    stats.todayReceived = 156
    stats.todaySuccess = 142
    stats.todayFailed = 8
    stats.todayUnrecognized = 6
    stats.schedulerJobs = 5
    stats.todaySyncCount = 24
    stats.todayCallbackCount = 89
    stats.todayCallbackFailed = 3
  }
}

// 获取厂家列表
const fetchVendorList = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/vendor/list')
    if (res.data.code === 0) {
      vendorList.value = res.data.data || []
    }
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

// 获取最近日志
const fetchRecentLogs = async () => {
  try {
    const res = await request.get('/api/log/transform', { params: { page: 1, page_size: 10 } })
    if (res.data.code === 0) {
      recentLogs.value = res.data.data?.items || []
    }
  } catch {
    // silent
  }
}

// 刷新日志
const refreshLogs = () => {
  fetchRecentLogs()
}

// 初始化
onMounted(() => {
  fetchStats()
  fetchVendorList()
  fetchRecentLogs()
  fetchSchedulerJobs()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;

    &.received {
      background-color: #e6f7ff;
      color: #1890ff;
    }

    &.success {
      background-color: #f6ffed;
      color: #52c41a;
    }

    &.failed {
      background-color: #fff2f0;
      color: #ff4d4f;
    }

    &.unknown {
      background-color: #fffbe6;
      color: #faad14;
    }

    &.timer {
      background-color: #f0f5ff;
      color: #2f54eb;
    }

    &.sync {
      background-color: #e6fffb;
      color: #13c2c2;
    }

    &.callback {
      background-color: #f9f0ff;
      color: #722ed1;
    }

    &.callback-failed {
      background-color: #fff1f0;
      color: #f5222d;
    }
  }

  .stat-info {
    .stat-label {
      font-size: 14px;
      color: #666;
      margin-bottom: 4px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #333;
    }
  }
}

.content-row {
  .table-card {
    height: 100%;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
