<template>
  <div class="callback-config-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px" @change="handleVendorChange">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- 回传配置表单 -->
    <el-card shadow="never" class="config-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>回传配置</span>
        </div>
      </template>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="140px" style="max-width: 700px">
        <el-form-item label="启用回传">
          <el-switch v-model="formData.enabled" />
        </el-form-item>

        <el-form-item label="回传类型" prop="callbackType">
          <el-select v-model="formData.callbackType" placeholder="请选择回传类型" style="width: 100%">
            <el-option label="实时回传" value="realtime" />
            <el-option label="延迟回传" value="delayed" />
            <el-option label="定时回传" value="scheduled" />
          </el-select>
        </el-form-item>

        <el-form-item label="回传地址" prop="callbackUrl">
          <el-input v-model="formData.callbackUrl" placeholder="https://example.com/api/callback" />
        </el-form-item>

        <el-form-item label="请求方式" prop="callbackMethod">
          <el-select v-model="formData.callbackMethod" placeholder="请选择请求方式" style="width: 100%">
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
          </el-select>
        </el-form-item>

        <el-form-item label="请求头">
          <el-input v-model="formData.callbackHeaders" type="textarea" :rows="3" placeholder='{"Authorization": "Bearer xxx"}' />
          <div class="form-tip">JSON格式的请求头</div>
        </el-form-item>

        <el-form-item label="数据格式" prop="callbackFormat">
          <el-select v-model="formData.callbackFormat" placeholder="请选择数据格式" style="width: 100%">
            <el-option label="JSON" value="json" />
            <el-option label="XML" value="xml" />
          </el-select>
        </el-form-item>

        <el-form-item label="定时表达式" prop="cronExpression" v-if="formData.callbackType === 'scheduled'">
          <el-input v-model="formData.cronExpression" placeholder="0 */5 * * *" />
          <div class="form-tip">如: 0 */5 * * *</div>
        </el-form-item>

        <el-form-item label="延迟分钟数" prop="delayMinutes" v-if="formData.callbackType === 'delayed'">
          <el-input-number v-model="formData.delayMinutes" :min="1" :max="1440" />
        </el-form-item>

        <el-form-item label="包含目标编码">
          <el-input v-model="formData.includeItems" placeholder="多个编码用逗号分隔，如: TEMP,HR,RR" />
          <div class="form-tip">留空表示回传所有目标编码</div>
        </el-form-item>

        <el-form-item label="排除目标编码">
          <el-input v-model="formData.excludeItems" placeholder="多个编码用逗号分隔" />
        </el-form-item>

        <el-form-item label="启用重试">
          <el-switch v-model="formData.retryEnabled" />
        </el-form-item>

        <el-form-item label="最大重试次数" v-if="formData.retryEnabled">
          <el-input-number v-model="formData.maxRetryCount" :min="1" :max="10" />
        </el-form-item>

        <el-form-item label="重试间隔(秒)" v-if="formData.retryEnabled">
          <el-input-number v-model="formData.retryIntervalSeconds" :min="1" :max="3600" />
        </el-form-item>

        <el-form-item label="数据模板">
          <el-input v-model="formData.dataTemplate" type="textarea" :rows="6" placeholder='JSON模板，支持 ${patientId} ${items} 等变量' />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          <el-button type="warning" @click="handleTestCallback" :loading="testing">测试回传</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 未选择厂家时的提示 -->
    <el-card shadow="never" class="empty-card" v-else>
      <el-empty description="请先选择厂家" />
    </el-card>

    <!-- 最近回传日志 -->
    <el-card shadow="never" class="log-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>最近回传日志</span>
          <el-button type="primary" link @click="fetchCallbackLogs">刷新</el-button>
        </div>
      </template>
      <el-table :data="callbackLogs" stripe style="width: 100%">
        <el-table-column prop="vendorCode" label="厂家编码" width="120" />
        <el-table-column prop="callbackUrl" label="回传地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responseStatus" label="响应状态码" width="110" />
        <el-table-column prop="duration" label="耗时(ms)" width="100" />
        <el-table-column prop="error" label="错误信息" min-width="180" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="创建时间" width="170" />
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="logPagination.page"
          v-model:page-size="logPagination.pageSize"
          :total="logPagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchCallbackLogs"
          @current-change="fetchCallbackLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import request from '@/api/request'

// 厂家接口
interface Vendor {
  vendorCode: string
  vendorName: string
}

// 回传日志接口
interface CallbackLog {
  vendorCode: string
  callbackUrl: string
  status: string
  responseStatus: number
  duration: number
  error: string
  createdAt: string
}

// 回传配置表单接口
interface CallbackConfigForm {
  enabled: boolean
  callbackType: string
  callbackUrl: string
  callbackMethod: string
  callbackHeaders: string
  callbackFormat: string
  cronExpression: string
  delayMinutes: number
  includeItems: string
  excludeItems: string
  retryEnabled: boolean
  maxRetryCount: number
  retryIntervalSeconds: number
  dataTemplate: string
}

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const saving = ref(false)
const testing = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<CallbackConfigForm>({
  enabled: false,
  callbackType: 'realtime',
  callbackUrl: '',
  callbackMethod: 'POST',
  callbackHeaders: '',
  callbackFormat: 'json',
  cronExpression: '',
  delayMinutes: 5,
  includeItems: '',
  excludeItems: '',
  retryEnabled: false,
  maxRetryCount: 3,
  retryIntervalSeconds: 30,
  dataTemplate: ''
})

const formRules: FormRules = {
  callbackType: [{ required: true, message: '请选择回传类型', trigger: 'change' }],
  callbackUrl: [{ required: true, message: '请输入回传地址', trigger: 'blur' }],
  callbackMethod: [{ required: true, message: '请选择请求方式', trigger: 'change' }],
  callbackFormat: [{ required: true, message: '请选择数据格式', trigger: 'change' }]
}

// 回传日志
const callbackLogs = ref<CallbackLog[]>([])
const logPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 获取厂家列表
const fetchVendorList = async () => {
  try {
    const res = await request.get('/api/vendor/list')
    vendorList.value = res.data?.data || res.data || []
  } catch {
    vendorList.value = []
  }
}

// 厂家切换
const handleVendorChange = (vendorCode: string) => {
  if (vendorCode) {
    loadConfig(vendorCode)
    fetchCallbackLogs()
  }
}

// 加载配置
const loadConfig = async (vendorCode: string) => {
  try {
    const res = await request.get(`/api/callback/config/${vendorCode}`)
    const data = res.data?.data || res.data
    if (data) {
      Object.assign(formData, data)
    }
  } catch {
    ElMessage.error('加载回传配置失败')
  }
}

// 保存配置
const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await request.post('/api/callback/config', {
          vendorCode: selectedVendor.value,
          ...formData
        })
        ElMessage.success('保存成功')
      } catch {
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 测试回传
const handleTestCallback = async () => {
  testing.value = true
  try {
    await request.post('/api/callback/test', {
      vendorCode: selectedVendor.value
    })
    ElMessage.success('测试回传已发送')
  } catch {
    ElMessage.error('测试回传失败')
  } finally {
    testing.value = false
  }
}

// 获取回传日志
const fetchCallbackLogs = async () => {
  try {
    const res = await request.get('/api/callback/logs', {
      params: {
        vendorCode: selectedVendor.value,
        page: logPagination.page,
        page_size: logPagination.pageSize
      }
    })
    const data = res.data?.data || res.data
    callbackLogs.value = data?.items || data?.list || []
    logPagination.total = data?.total || 0
  } catch {
    callbackLogs.value = []
  }
}

// 初始化
onMounted(() => {
  fetchVendorList()
})
</script>

<style scoped lang="scss">
.callback-config-container {
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
}

.log-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
