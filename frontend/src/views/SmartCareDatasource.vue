<template>
  <div class="smartcare-datasource">
    <el-card shadow="never">
      <template #header>
        <span>SmartCare数据源配置</span>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        style="max-width: 650px"
      >
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="formData.name" placeholder="如 SmartCare-ICU" />
        </el-form-item>

        <el-divider content-position="left">连接信息</el-divider>

        <el-form-item label="主机/IP" prop="host">
          <el-input v-model="formData.host" placeholder="如 192.168.1.100 或 localhost" />
        </el-form-item>

        <el-form-item label="端口" prop="port">
          <el-input-number v-model="formData.port" :min="1" :max="65535" style="width: 200px" />
        </el-form-item>

        <el-form-item label="数据库名称" prop="database">
          <el-input v-model="formData.database" placeholder="如 SmartCare" />
        </el-form-item>

        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="留空表示无认证" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="formData.password" type="password" show-password placeholder="留空表示无认证" />
        </el-form-item>

        <el-divider content-position="left">集合配置</el-divider>

        <el-form-item label="配置参数集合" prop="configParamCollection">
          <el-input v-model="formData.configParamCollection" placeholder="如 configParam" />
        </el-form-item>
        <el-form-item label="床旁数据集合" prop="bedsideCollection">
          <el-input v-model="formData.bedsideCollection" placeholder="如 bedside" />
        </el-form-item>
        <el-form-item label="患者信息集合" prop="patientCollection">
          <el-input v-model="formData.patientCollection" placeholder="如 patient" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="testConnection" :loading="testLoading">
            测试连接
          </el-button>
          <el-button type="success" @click="saveConfig" :loading="saveLoading">
            保存
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 连接测试状态 -->
      <el-card v-if="lastTestStatus" shadow="never" style="max-width: 650px; margin-top: 16px">
        <div class="test-status">
          <el-tag :type="lastTestStatus === 'success' ? 'success' : 'danger'" size="large">
            {{ lastTestStatus === 'success' ? '连接成功' : '连接失败' }}
          </el-tag>
          <span class="test-time">{{ lastTestTime }}</span>
        </div>
        <div v-if="lastTestMessage" class="test-message">{{ lastTestMessage }}</div>
        <div v-if="lastTestCollections.length" class="test-collections">
          <el-tag v-for="c in lastTestCollections" :key="c" size="small" type="info" effect="plain" class="coll-tag">{{ c }}</el-tag>
        </div>
      </el-card>
    </el-card>

    <!-- 已保存的数据源列表 -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>已保存的数据源</span>
          <el-button type="primary" link @click="loadDatasourceList">刷新</el-button>
        </div>
      </template>
      <el-table :data="datasourceList" stripe>
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="host" label="主机" width="180">
          <template #default="{ row }">
            {{ row.host || '-' }}:{{ row.port || 27017 }}
          </template>
        </el-table-column>
        <el-table-column prop="database" label="数据库" width="150" />
        <el-table-column prop="testStatus" label="连接状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.testStatus === 'success' ? 'success' : row.testStatus === 'failed' ? 'danger' : 'info'" size="small">
              {{ row.testStatus === 'success' ? '成功' : row.testStatus === 'failed' ? '失败' : '未测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editDatasource(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="testSaved(row)">测试</el-button>
            <el-button type="danger" link size="small" @click="deleteDatasource(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import request from '@/api/request'

const formRef = ref<FormInstance>()
const testLoading = ref(false)
const saveLoading = ref(false)
const lastTestStatus = ref('')
const lastTestTime = ref('')
const lastTestMessage = ref('')
const lastTestCollections = ref<string[]>([])
const datasourceList = ref<any[]>([])
const editingId = ref('')

const formData = reactive({
  name: '',
  host: '',
  port: 27017,
  database: 'SmartCare',
  username: '',
  password: '',
  configParamCollection: 'configParam',
  bedsideCollection: 'bedside',
  patientCollection: 'patient'
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机IP', trigger: 'blur' }],
  database: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
}

async function loadDatasourceList() {
  try {
    const res = await request.get('/api/smartcare/datasource')
    const data = res.data?.data || res.data
    datasourceList.value = Array.isArray(data) ? data : [data].filter(Boolean)
  } catch {
    datasourceList.value = []
  }
}

function editDatasource(row: any) {
  editingId.value = row._id || row.id || ''
  formData.name = row.name || ''
  formData.host = row.host || ''
  formData.port = row.port || 27017
  formData.database = row.database || 'SmartCare'
  formData.username = row.username || ''
  formData.password = ''  // 不回填密码
  const cols = row.collections || {}
  formData.configParamCollection = cols.configParam || 'configParam'
  formData.bedsideCollection = cols.bedside || 'bedside'
  formData.patientCollection = cols.patient || 'patient'
}

async function testConnection() {
  if (!formRef.value) return
  try {
    await formRef.value.validateField(['host', 'database'])
  } catch {
    return
  }
  testLoading.value = true
  lastTestCollections.value = []
  try {
    const res = await request.post('/api/smartcare/datasource/test', {
      host: formData.host,
      port: formData.port,
      database: formData.database,
      username: formData.username,
      password: formData.password,
    })
    const data = res.data?.data || res.data
    lastTestStatus.value = data?.success ? 'success' : 'failed'
    lastTestTime.value = new Date().toLocaleString('zh-CN')
    lastTestMessage.value = data?.message || ''
    lastTestCollections.value = data?.collections || []
    if (data?.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(data?.message || '连接失败')
    }
  } catch (err: any) {
    lastTestStatus.value = 'failed'
    lastTestTime.value = new Date().toLocaleString('zh-CN')
    lastTestMessage.value = err?.response?.data?.message || err?.message || '连接失败'
    ElMessage.error('连接测试失败')
  } finally {
    testLoading.value = false
  }
}

async function testSaved(row: any) {
  testLoading.value = true
  try {
    const res = await request.post('/api/smartcare/datasource/test', {
      host: row.host,
      port: row.port,
      database: row.database,
      username: row.username,
    })
    const data = res.data?.data || res.data
    lastTestStatus.value = data?.success ? 'success' : 'failed'
    lastTestTime.value = new Date().toLocaleString('zh-CN')
    lastTestMessage.value = data?.message || ''
    lastTestCollections.value = data?.collections || []
    if (data?.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(data?.message || '连接失败')
    }
  } catch {
    ElMessage.error('测试失败')
  } finally {
    testLoading.value = false
  }
}

async function saveConfig() {
  if (!formRef.value) return
  await formRef.value.validate()
  saveLoading.value = true
  try {
    const payload: any = {
      name: formData.name,
      host: formData.host,
      port: formData.port,
      database: formData.database,
      username: formData.username,
      collections: {
        configParam: formData.configParamCollection,
        bedside: formData.bedsideCollection,
        patient: formData.patientCollection,
      },
    }
    if (formData.password) {
      payload.password = formData.password
    }
    if (editingId.value) {
      payload.id = editingId.value
    }
    await request.post('/api/smartcare/datasource', payload)
    ElMessage.success('保存成功')
    editingId.value = ''
    loadDatasourceList()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

async function deleteDatasource(row: any) {
  try {
    await ElMessageBox.confirm('确定删除该数据源？', '提示', { type: 'warning' })
    await request.delete(`/api/smartcare/datasource/${row._id || row.id}`)
    ElMessage.success('删除成功')
    loadDatasourceList()
  } catch {
    // cancelled
  }
}

onMounted(() => {
  loadDatasourceList()
})
</script>

<style scoped>
.smartcare-datasource {
  padding: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.test-status {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.test-time {
  color: #909399;
  font-size: 13px;
}
.test-message {
  color: #606266;
  font-size: 13px;
  margin-top: 4px;
}
.test-collections {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.coll-tag {
  font-size: 11px;
}
</style>
