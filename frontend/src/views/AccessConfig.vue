<template>
  <div class="access-config-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px" @change="handleVendorChange">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- 接入配置表单 -->
    <el-card shadow="never" class="config-card" v-if="selectedVendor">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- HTTP推送 -->
        <el-tab-pane label="HTTP推送" name="http_push">
          <el-form ref="httpPushFormRef" :model="httpPushConfig" :rules="httpPushRules" label-width="120px" style="max-width: 600px">
            <el-form-item label="接口路径" prop="endpointPath">
              <el-input v-model="httpPushConfig.endpointPath" placeholder="/api/receive/temperature" />
            </el-form-item>
            <el-form-item label="认证方式" prop="authType">
              <el-select v-model="httpPushConfig.authType" placeholder="请选择认证方式" style="width: 100%">
                <el-option label="无认证" value="none" />
                <el-option label="Token认证" value="token" />
                <el-option label="Basic认证" value="basic" />
              </el-select>
            </el-form-item>
            <el-form-item label="认证令牌" prop="authToken" v-if="httpPushConfig.authType === 'token'">
              <el-input v-model="httpPushConfig.authToken" placeholder="请输入认证令牌" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testHttpPush" :loading="testing">测试连接</el-button>
              <el-button type="success" @click="saveHttpPush" :loading="saving">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- HTTP拉取 -->
        <el-tab-pane label="HTTP拉取" name="http_pull">
          <el-form ref="httpPullFormRef" :model="httpPullConfig" :rules="httpPullRules" label-width="120px" style="max-width: 700px">
            <el-form-item label="请求地址" prop="url">
              <el-input v-model="httpPullConfig.url" placeholder="https://api.example.com/temperature" />
            </el-form-item>
            <el-form-item label="请求方式" prop="method">
              <el-radio-group v-model="httpPullConfig.method">
                <el-radio value="GET">GET</el-radio>
                <el-radio value="POST">POST</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="请求头" prop="headers">
              <el-input v-model="httpPullConfig.headers" type="textarea" :rows="4" placeholder='{"Content-Type": "application/json"}' />
            </el-form-item>
            <el-form-item label="请求体模板" prop="bodyTemplate" v-if="httpPullConfig.method === 'POST'">
              <el-input v-model="httpPullConfig.bodyTemplate" type="textarea" :rows="6" placeholder="请输入请求体模板" />
            </el-form-item>
            <el-form-item label="定时表达式" prop="cronExpression">
              <el-input v-model="httpPullConfig.cronExpression" placeholder="0 0/5 * * * ?" />
              <div class="form-tip">Cron表达式，如：0 0/5 * * * ? 表示每5分钟执行</div>
            </el-form-item>
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number v-model="httpPullConfig.timeout" :min="1" :max="300" />
            </el-form-item>
            <el-form-item label="重试次数" prop="retryTimes">
              <el-input-number v-model="httpPullConfig.retryTimes" :min="0" :max="10" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testHttpPull" :loading="testing">测试连接</el-button>
              <el-button type="success" @click="saveHttpPull" :loading="saving">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 数据库视图 -->
        <el-tab-pane label="数据库视图" name="db_view">
          <el-form ref="dbViewFormRef" :model="dbViewConfig" :rules="dbViewRules" label-width="120px" style="max-width: 700px">
            <el-form-item label="数据库类型" prop="dbType">
              <el-select v-model="dbViewConfig.dbType" placeholder="请选择数据库类型" style="width: 100%">
                <el-option label="Oracle" value="oracle" />
                <el-option label="MySQL" value="mysql" />
                <el-option label="PostgreSQL" value="postgresql" />
                <el-option label="SQL Server" value="sqlserver" />
              </el-select>
            </el-form-item>
            <el-form-item label="JDBC地址" prop="jdbcUrl">
              <el-input v-model="dbViewConfig.jdbcUrl" placeholder="jdbc:oracle:thin:@host:port:orcl" />
            </el-form-item>
            <el-form-item label="用户名" prop="username">
              <el-input v-model="dbViewConfig.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="dbViewConfig.password" type="password" placeholder="请输入密码" show-password />
            </el-form-item>
            <el-form-item label="SQL模板" prop="sqlTemplate">
              <el-input v-model="dbViewConfig.sqlTemplate" type="textarea" :rows="6" placeholder="SELECT * FROM temperature_view WHERE ..." />
            </el-form-item>
            <el-form-item label="定时表达式" prop="cronExpression">
              <el-input v-model="dbViewConfig.cronExpression" placeholder="0 0/5 * * * ?" />
              <div class="form-tip">Cron表达式，如：0 0/5 * * * ? 表示每5分钟执行</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testDbView" :loading="testing">测试连接</el-button>
              <el-button type="success" @click="saveDbView" :loading="saving">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 未选择厂家时的提示 -->
    <el-card shadow="never" class="empty-card" v-else>
      <el-empty description="请先选择厂家" />
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

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const activeTab = ref('http_push')
const testing = ref(false)
const saving = ref(false)
const loading = ref(false)

// HTTP推送配置接口
interface HttpPushConfig {
  endpointPath: string
  authType: string
  authToken: string
}

// HTTP拉取配置接口
interface HttpPullConfig {
  url: string
  method: string
  headers: string
  bodyTemplate: string
  cronExpression: string
  timeout: number
  retryTimes: number
}

// 数据库视图配置接口
interface DbViewConfig {
  dbType: string
  jdbcUrl: string
  username: string
  password: string
  sqlTemplate: string
  cronExpression: string
}

// HTTP推送配置
const httpPushFormRef = ref<FormInstance>()
const httpPushConfig = reactive<HttpPushConfig>({
  endpointPath: '',
  authType: 'none',
  authToken: ''
})

const httpPushRules: FormRules = {
  endpointPath: [{ required: true, message: '请输入接口路径', trigger: 'blur' }],
  authType: [{ required: true, message: '请选择认证方式', trigger: 'change' }]
}

// HTTP拉取配置
const httpPullFormRef = ref<FormInstance>()
const httpPullConfig = reactive<HttpPullConfig>({
  url: '',
  method: 'GET',
  headers: '',
  bodyTemplate: '',
  cronExpression: '',
  timeout: 30,
  retryTimes: 3
})

const httpPullRules: FormRules = {
  url: [{ required: true, message: '请输入请求地址', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求方式', trigger: 'change' }],
  cronExpression: [{ required: true, message: '请输入定时表达式', trigger: 'blur' }]
}

// 数据库视图配置
const dbViewFormRef = ref<FormInstance>()
const dbViewConfig = reactive<DbViewConfig>({
  dbType: '',
  jdbcUrl: '',
  username: '',
  password: '',
  sqlTemplate: '',
  cronExpression: ''
})

const dbViewRules: FormRules = {
  dbType: [{ required: true, message: '请选择数据库类型', trigger: 'change' }],
  jdbcUrl: [{ required: true, message: '请输入JDBC地址', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  sqlTemplate: [{ required: true, message: '请输入SQL模板', trigger: 'blur' }],
  cronExpression: [{ required: true, message: '请输入定时表达式', trigger: 'blur' }]
}

// 厂家切换
const handleVendorChange = (vendorCode: string) => {
  if (vendorCode) {
    loadConfig(vendorCode)
  }
}

// 加载配置
const loadConfig = async (vendorCode: string) => {
  try {
    const res = await request.get(`/api/access-config/${vendorCode}`)
    if (res.data.code === 0 && res.data.data) {
      const config = res.data.data
      activeTab.value = config.accessType || 'http_push'

      // 填充HTTP推送配置
      if (config.httpPushConfig) {
        Object.assign(httpPushConfig, config.httpPushConfig)
      }

      // 填充HTTP拉取配置
      if (config.httpPullConfig) {
        Object.assign(httpPullConfig, config.httpPullConfig)
        if (config.httpPullConfig.headers && typeof config.httpPullConfig.headers === 'object') {
          httpPullConfig.headers = JSON.stringify(config.httpPullConfig.headers, null, 2)
        }
      }

      // 填充数据库视图配置
      if (config.dbViewConfig) {
        Object.assign(dbViewConfig, config.dbViewConfig)
      }
    }
  } catch {
    // 首次配置，无数据
  }
}

// 测试HTTP推送
const testHttpPush = async () => {
  if (!httpPushFormRef.value) return
  await httpPushFormRef.value.validate(async (valid) => {
    if (valid) {
      testing.value = true
      try {
        const res = await request.post('/api/access-config/test-http', {
          url: `http://localhost:8000/api/push/${selectedVendor.value}`,
          method: 'POST',
          headers: httpPushConfig.authType === 'token' ? { Authorization: `Bearer ${httpPushConfig.authToken}` } : {},
          timeout: 30,
        })
        if (res.data.code === 0 && res.data.data?.success) {
          ElMessage.success('测试连接成功')
        } else {
          ElMessage.error(res.data.data?.message || '测试连接失败')
        }
      } catch (e: any) {
        ElMessage.error(e.message || '测试连接失败')
      } finally {
        testing.value = false
      }
    }
  })
}

// 保存HTTP推送
const saveHttpPush = async () => {
  if (!httpPushFormRef.value) return
  await httpPushFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const res = await request.post('/api/access-config', {
          vendorCode: selectedVendor.value,
          accessType: 'http_push',
          httpPushConfig: { ...httpPushConfig },
          enabled: true,
        })
        if (res.data.code === 0) {
          ElMessage.success('保存成功')
        } else {
          ElMessage.error(res.data.message || '保存失败')
        }
      } catch (e: any) {
        ElMessage.error(e.message || '保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 测试HTTP拉取
const testHttpPull = async () => {
  if (!httpPullFormRef.value) return
  await httpPullFormRef.value.validate(async (valid) => {
    if (valid) {
      testing.value = true
      try {
        let headers = {}
        try {
          headers = httpPullConfig.headers ? JSON.parse(httpPullConfig.headers) : {}
        } catch {
          ElMessage.error('请求头格式错误，请输入有效的JSON')
          testing.value = false
          return
        }

        const res = await request.post('/api/access-config/test-http', {
          url: httpPullConfig.url,
          method: httpPullConfig.method,
          headers,
          body: httpPullConfig.bodyTemplate,
          timeout: httpPullConfig.timeout,
        })
        if (res.data.code === 0 && res.data.data?.success) {
          ElMessage.success(`测试连接成功: ${res.data.data.message}`)
        } else {
          ElMessage.error(res.data.data?.message || '测试连接失败')
        }
      } catch (e: any) {
        ElMessage.error(e.message || '测试连接失败')
      } finally {
        testing.value = false
      }
    }
  })
}

// 保存HTTP拉取
const saveHttpPull = async () => {
  if (!httpPullFormRef.value) return
  await httpPullFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        let headers = {}
        try {
          headers = httpPullConfig.headers ? JSON.parse(httpPullConfig.headers) : {}
        } catch {
          ElMessage.error('请求头格式错误，请输入有效的JSON')
          saving.value = false
          return
        }

        const res = await request.post('/api/access-config', {
          vendorCode: selectedVendor.value,
          accessType: 'http_pull',
          httpPullConfig: {
            url: httpPullConfig.url,
            method: httpPullConfig.method,
            headers,
            bodyTemplate: httpPullConfig.bodyTemplate,
            cronExpression: httpPullConfig.cronExpression,
            timeout: httpPullConfig.timeout,
            retryTimes: httpPullConfig.retryTimes,
          },
          enabled: true,
        })
        if (res.data.code === 0) {
          ElMessage.success('保存成功')
        } else {
          ElMessage.error(res.data.message || '保存失败')
        }
      } catch (e: any) {
        ElMessage.error(e.message || '保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 测试数据库视图
const testDbView = async () => {
  if (!dbViewFormRef.value) return
  await dbViewFormRef.value.validate(async (valid) => {
    if (valid) {
      testing.value = true
      try {
        const res = await request.post('/api/access-config/test-db', {
          connectionString: dbViewConfig.jdbcUrl,
          dbType: dbViewConfig.dbType,
          testSql: dbViewConfig.sqlTemplate,
          username: dbViewConfig.username,
          password: dbViewConfig.password,
        })
        if (res.data.code === 0 && res.data.data?.success) {
          ElMessage.success(`测试连接成功: ${res.data.data.message}`)
        } else {
          ElMessage.error(res.data.data?.message || '测试连接失败')
        }
      } catch (e: any) {
        ElMessage.error(e.message || '测试连接失败')
      } finally {
        testing.value = false
      }
    }
  })
}

// 保存数据库视图
const saveDbView = async () => {
  if (!dbViewFormRef.value) return
  await dbViewFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const res = await request.post('/api/access-config', {
          vendorCode: selectedVendor.value,
          accessType: 'db_view',
          dbViewConfig: {
            dbType: dbViewConfig.dbType,
            jdbcUrl: dbViewConfig.jdbcUrl,
            username: dbViewConfig.username,
            password: dbViewConfig.password,
            sqlTemplate: dbViewConfig.sqlTemplate,
            cronExpression: dbViewConfig.cronExpression,
          },
          enabled: true,
        })
        if (res.data.code === 0) {
          ElMessage.success('保存成功')
        } else {
          ElMessage.error(res.data.message || '保存失败')
        }
      } catch (e: any) {
        ElMessage.error(e.message || '保存失败')
      } finally {
        saving.value = false
      }
    }
  })
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

// 初始化
onMounted(() => {
  fetchVendorList()
})
</script>

<style scoped lang="scss">
.access-config-container {
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
  :deep(.el-tabs__content) {
    padding: 24px;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
