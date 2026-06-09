<template>
  <div class="sync-config-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px" @change="handleVendorChange">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- 同步配置表单 -->
    <el-card shadow="never" class="config-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>同步任务配置</span>
        </div>
      </template>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="140px" style="max-width: 700px">
        <el-form-item label="启用同步">
          <el-switch v-model="formData.enabled" />
        </el-form-item>

        <el-form-item label="同步类型" prop="syncType">
          <el-select v-model="formData.syncType" placeholder="请选择同步类型" style="width: 100%">
            <el-option label="HTTP拉取" value="pull" />
            <el-option label="数据库视图" value="db_view" />
          </el-select>
        </el-form-item>

        <el-form-item label="定时表达式" prop="cronExpression">
          <el-input v-model="formData.cronExpression" placeholder="0 */5 * * *" />
          <div class="form-tip">如: 0 */5 * * * 表示每5分钟</div>
        </el-form-item>

        <el-form-item label="回溯天数" prop="lookbackDays">
          <el-input-number v-model="formData.lookbackDays" :min="1" :max="30" />
          <div class="form-tip">每次同步回溯多少天的数据</div>
        </el-form-item>

        <el-form-item label="同步窗口(小时)" prop="syncWindowHours">
          <el-input-number v-model="formData.syncWindowHours" :min="1" :max="48" />
          <div class="form-tip">同步时间窗口（小时）</div>
        </el-form-item>

        <el-form-item label="批次大小" prop="batchSize">
          <el-input-number v-model="formData.batchSize" :min="1" :max="1000" />
        </el-form-item>

        <el-form-item label="科室编码">
          <el-input v-model="formData.wardCodes" placeholder="多个编码用逗号分隔" />
          <div class="form-tip">留空表示同步所有科室</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          <el-button type="warning" @click="handleManualSync" :loading="syncing">立即同步</el-button>
        </el-form-item>
      </el-form>

      <!-- 最近同步状态 -->
      <el-divider />
      <el-descriptions title="最近同步状态" :column="2" border>
        <el-descriptions-item label="最近同步时间">{{ syncStatus.lastSyncTime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="最近同步状态">
          <el-tag :type="syncStatus.lastSyncStatus === 'success' ? 'success' : syncStatus.lastSyncStatus === 'failed' ? 'danger' : 'info'" size="small">
            {{ syncStatusLabel }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="同步数据量">{{ syncStatus.lastSyncCount ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="最近错误">
          <span :class="{ 'error-text': syncStatus.lastError }">{{ syncStatus.lastError || '-' }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 未选择厂家时的提示 -->
    <el-card shadow="never" class="empty-card" v-else>
      <el-empty description="请先选择厂家" />
    </el-card>

    <!-- 所有同步任务 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>所有同步任务</span>
          <el-button type="primary" link @click="fetchAllSyncConfigs">刷新</el-button>
        </div>
      </template>
      <el-table :data="allSyncConfigs" stripe style="width: 100%">
        <el-table-column prop="vendorCode" label="厂家编码" width="120" />
        <el-table-column prop="enabled" label="启用状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="syncType" label="同步类型" width="120">
          <template #default="{ row }">
            {{ row.syncType === 'pull' ? 'HTTP拉取' : '数据库视图' }}
          </template>
        </el-table-column>
        <el-table-column prop="cronExpression" label="定时表达式" width="150" />
        <el-table-column prop="lookbackDays" label="回溯天数" width="100" />
        <el-table-column prop="lastSyncTime" label="最近同步时间" min-width="170" />
        <el-table-column prop="lastSyncStatus" label="最近状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.lastSyncStatus === 'success' ? 'success' : row.lastSyncStatus === 'failed' ? 'danger' : 'info'" size="small">
              {{ row.lastSyncStatus === 'success' ? '成功' : row.lastSyncStatus === 'failed' ? '失败' : '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="selectVendor(row.vendorCode)">配置</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 定时任务列表 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>定时任务列表</span>
          <el-button type="primary" link @click="fetchSchedulerJobs">刷新</el-button>
        </div>
      </template>
      <el-table :data="schedulerJobs" stripe style="width: 100%">
        <el-table-column prop="id" label="任务ID" min-width="200" />
        <el-table-column prop="next_run_time" label="下次执行时间" width="180" />
        <el-table-column prop="trigger" label="触发器" min-width="200" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import request from '@/api/request'

// 厂家接口
interface Vendor {
  vendorCode: string
  vendorName: string
}

// 同步配置表单接口
interface SyncConfigForm {
  enabled: boolean
  syncType: string
  cronExpression: string
  lookbackDays: number
  syncWindowHours: number
  batchSize: number
  wardCodes: string
}

// 同步状态
interface SyncStatus {
  lastSyncTime: string | null
  lastSyncStatus: string | null
  lastSyncCount: number | null
  lastError: string | null
}

// 所有同步配置
interface AllSyncConfig {
  vendorCode: string
  enabled: boolean
  syncType: string
  cronExpression: string
  lookbackDays: number
  lastSyncTime: string | null
  lastSyncStatus: string | null
}

// 定时任务
interface SchedulerJob {
  id: string
  next_run_time: string
  trigger: string
}

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const saving = ref(false)
const syncing = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<SyncConfigForm>({
  enabled: false,
  syncType: 'pull',
  cronExpression: '',
  lookbackDays: 1,
  syncWindowHours: 24,
  batchSize: 100,
  wardCodes: ''
})

const formRules: FormRules = {
  syncType: [{ required: true, message: '请选择同步类型', trigger: 'change' }],
  cronExpression: [{ required: true, message: '请输入定时表达式', trigger: 'blur' }]
}

// 同步状态
const syncStatus = reactive<SyncStatus>({
  lastSyncTime: null,
  lastSyncStatus: null,
  lastSyncCount: null,
  lastError: null
})

const syncStatusLabel = computed(() => {
  if (!syncStatus.lastSyncStatus) return '未知'
  const map: Record<string, string> = { success: '成功', failed: '失败', running: '运行中' }
  return map[syncStatus.lastSyncStatus] || syncStatus.lastSyncStatus
})

// 所有同步配置
const allSyncConfigs = ref<AllSyncConfig[]>([])

// 定时任务
const schedulerJobs = ref<SchedulerJob[]>([])

// 获取厂家列表
const fetchVendorList = async () => {
  try {
    const res = await request.get('/api/vendor/list')
    vendorList.value = res.data?.data || res.data || []
  } catch {
    vendorList.value = []
  }
}

// 选择厂家
const selectVendor = (vendorCode: string) => {
  selectedVendor.value = vendorCode
  handleVendorChange(vendorCode)
}

// 厂家切换
const handleVendorChange = (vendorCode: string) => {
  if (vendorCode) {
    loadConfig(vendorCode)
    fetchSyncStatus(vendorCode)
  }
}

// 加载配置
const loadConfig = async (vendorCode: string) => {
  try {
    const res = await request.get(`/api/sync/config/${vendorCode}`)
    const data = res.data?.data || res.data
    if (data) {
      Object.assign(formData, data)
    }
  } catch {
    ElMessage.error('加载同步配置失败')
  }
}

// 获取同步状态
const fetchSyncStatus = async (vendorCode: string) => {
  try {
    const res = await request.get(`/api/sync/status/${vendorCode}`)
    const data = res.data?.data || res.data
    if (data) {
      Object.assign(syncStatus, data)
    }
  } catch {
    // ignore
  }
}

// 保存配置
const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await request.post('/api/sync/config', {
          vendorCode: selectedVendor.value,
          ...formData
        })
        ElMessage.success('保存成功')
        fetchAllSyncConfigs()
      } catch {
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 立即同步
const handleManualSync = async () => {
  syncing.value = true
  try {
    await request.post('/api/sync/trigger', {
      vendorCode: selectedVendor.value
    })
    ElMessage.success('同步任务已触发')
    setTimeout(() => fetchSyncStatus(selectedVendor.value), 2000)
  } catch {
    ElMessage.error('触发同步失败')
  } finally {
    syncing.value = false
  }
}

// 获取所有同步配置
const fetchAllSyncConfigs = async () => {
  try {
    const res = await request.get('/api/sync/configs')
    const data = res.data?.data || res.data
    allSyncConfigs.value = Array.isArray(data) ? data : data?.items || data?.list || []
  } catch {
    allSyncConfigs.value = []
  }
}

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

// 初始化
onMounted(() => {
  fetchVendorList()
  fetchAllSyncConfigs()
  fetchSchedulerJobs()
})
</script>

<style scoped lang="scss">
.sync-config-container {
  padding: 20px;
}

.selector-card {
  margin-bottom: 16px;

  .selector-row {
    display: flex;
    align-items: center;
    gap: 12px;

    .selector-label {
      font-size: 14px;
      font-weight: 500;
      color: #606266;
      white-space: nowrap;
    }
  }
}

.config-card {
  margin-bottom: 16px;

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }

  .error-text {
    color: #f56c6c;
  }
}

.table-card {
  margin-bottom: 16px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
