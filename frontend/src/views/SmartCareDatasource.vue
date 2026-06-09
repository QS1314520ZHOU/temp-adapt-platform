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
        label-width="160px"
        style="max-width: 650px"
      >
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="formData.name" placeholder="如 SmartCare-ICU" />
        </el-form-item>
        <el-form-item label="MongoDB连接URI" prop="mongoUri">
          <el-input
            v-model="formData.mongoUri"
            type="password"
            show-password
            placeholder="mongodb://user:password@host:port/database"
          />
        </el-form-item>
        <el-form-item label="数据库名称" prop="database">
          <el-input v-model="formData.database" placeholder="如 smartcare_db" />
        </el-form-item>
        <el-divider content-position="left">集合配置</el-divider>
        <el-form-item label="配置参数集合" prop="configParamCollection">
          <el-input v-model="formData.configParamCollection" placeholder="如 config_param" />
        </el-form-item>
        <el-form-item label="床旁数据集合" prop="bedsideCollection">
          <el-input v-model="formData.bedsideCollection" placeholder="如 bedside_data" />
        </el-form-item>
        <el-form-item label="患者信息集合" prop="patientCollection">
          <el-input v-model="formData.patientCollection" placeholder="如 patient_info" />
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
          <span class="test-time">测试时间: {{ lastTestTime }}</span>
          <span v-if="lastTestMessage" class="test-message">{{ lastTestMessage }}</span>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

const formRef = ref<FormInstance>()
const testLoading = ref(false)
const saveLoading = ref(false)
const lastTestStatus = ref('')
const lastTestTime = ref('')
const lastTestMessage = ref('')

const formData = reactive({
  name: '',
  mongoUri: '',
  database: '',
  configParamCollection: 'config_param',
  bedsideCollection: 'bedside_data',
  patientCollection: 'patient_info'
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  mongoUri: [{ required: true, message: '请输入MongoDB连接URI', trigger: 'blur' }],
  database: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  configParamCollection: [{ required: true, message: '请输入配置参数集合名称', trigger: 'blur' }],
  bedsideCollection: [{ required: true, message: '请输入床旁数据集合名称', trigger: 'blur' }],
  patientCollection: [{ required: true, message: '请输入患者信息集合名称', trigger: 'blur' }]
}

async function loadConfig() {
  try {
    // TODO: Replace with actual API call
    // const res = await api.getSmartCareDatasource()
    // Object.assign(formData, res.data)
  } catch {
    ElMessage.error('加载配置失败')
  }
}

async function testConnection() {
  if (!formRef.value) return
  // Validate URI and database at minimum
  try {
    await formRef.value.validateField(['mongoUri', 'database'])
  } catch {
    return
  }
  testLoading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.testSmartCareConnection(formData)
    lastTestStatus.value = 'success'
    lastTestTime.value = new Date().toLocaleString('zh-CN')
    lastTestMessage.value = '连接成功，数据库可访问'
    ElMessage.success('连接测试成功')
  } catch (err: any) {
    lastTestStatus.value = 'failed'
    lastTestTime.value = new Date().toLocaleString('zh-CN')
    lastTestMessage.value = err?.message || '连接失败，请检查URI和网络配置'
    ElMessage.error('连接测试失败')
  } finally {
    testLoading.value = false
  }
}

async function saveConfig() {
  if (!formRef.value) return
  await formRef.value.validate()
  saveLoading.value = true
  try {
    // TODO: Replace with actual API call
    // await api.saveSmartCareDatasource(formData)
    ElMessage.success('配置保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.smartcare-datasource {
  padding: 16px;
}
.test-status {
  display: flex;
  align-items: center;
  gap: 16px;
}
.test-time {
  color: #909399;
  font-size: 13px;
}
.test-message {
  color: #606266;
  font-size: 13px;
}
</style>
