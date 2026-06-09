<template>
  <div class="field-mapping-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px" @change="handleVendorChange">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- Root字段映射 -->
    <el-card shadow="never" class="mapping-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>Root字段映射</span>
          <el-button type="primary" size="small" @click="addMapping('root')">
            <el-icon><Plus /></el-icon>
            添加映射
          </el-button>
        </div>
      </template>
      <el-table :data="rootMappings" stripe border size="small">
        <el-table-column label="目标字段" min-width="180">
          <template #default="{ row }">
            <el-select v-model="row.targetField" placeholder="请选择" size="small" style="width: 100%">
              <el-option v-for="field in targetFieldOptions" :key="field.value" :label="field.label" :value="field.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="来源路径" min-width="220">
          <template #default="{ row }">
            <el-input v-model="row.sourcePath" size="small" placeholder="如: $.hospital_code" />
          </template>
        </el-table-column>
        <el-table-column label="数据类型" width="140">
          <template #default="{ row }">
            <el-select v-model="row.dataType" size="small" style="width: 100%">
              <el-option label="string" value="string" />
              <el-option label="number" value="number" />
              <el-option label="datetime" value="datetime" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="日期格式" width="180">
          <template #default="{ row }">
            <el-input v-model="row.dateFormat" size="small" placeholder="yyyy-MM-dd HH:mm:ss" v-if="row.dataType === 'datetime'" />
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="70" align="center">
          <template #default="{ row }">
            <el-checkbox v-model="row.required" />
          </template>
        </el-table-column>
        <el-table-column label="默认值" width="160">
          <template #default="{ row }">
            <el-input v-model="row.defaultValue" size="small" placeholder="可选" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeMapping('root', $index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Record字段映射 -->
    <el-card shadow="never" class="mapping-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>Record字段映射</span>
          <el-button type="primary" size="small" @click="addMapping('record')">
            <el-icon><Plus /></el-icon>
            添加映射
          </el-button>
        </div>
      </template>
      <el-table :data="recordMappings" stripe border size="small">
        <el-table-column label="目标字段" min-width="180">
          <template #default="{ row }">
            <el-select v-model="row.targetField" placeholder="请选择" size="small" style="width: 100%">
              <el-option v-for="field in targetFieldOptions" :key="field.value" :label="field.label" :value="field.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="来源路径" min-width="220">
          <template #default="{ row }">
            <el-input v-model="row.sourcePath" size="small" placeholder="如: $.patient_id" />
          </template>
        </el-table-column>
        <el-table-column label="数据类型" width="140">
          <template #default="{ row }">
            <el-select v-model="row.dataType" size="small" style="width: 100%">
              <el-option label="string" value="string" />
              <el-option label="number" value="number" />
              <el-option label="datetime" value="datetime" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="日期格式" width="180">
          <template #default="{ row }">
            <el-input v-model="row.dateFormat" size="small" placeholder="yyyy-MM-dd HH:mm:ss" v-if="row.dataType === 'datetime'" />
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="70" align="center">
          <template #default="{ row }">
            <el-checkbox v-model="row.required" />
          </template>
        </el-table-column>
        <el-table-column label="默认值" width="160">
          <template #default="{ row }">
            <el-input v-model="row.defaultValue" size="small" placeholder="可选" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeMapping('record', $index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Item字段映射 -->
    <el-card shadow="never" class="mapping-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>Item字段映射</span>
          <el-button type="primary" size="small" @click="addMapping('item')">
            <el-icon><Plus /></el-icon>
            添加映射
          </el-button>
        </div>
      </template>
      <el-table :data="itemMappings" stripe border size="small">
        <el-table-column label="目标字段" min-width="180">
          <template #default="{ row }">
            <el-select v-model="row.targetField" placeholder="请选择" size="small" style="width: 100%">
              <el-option v-for="field in targetFieldOptions" :key="field.value" :label="field.label" :value="field.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="来源路径" min-width="220">
          <template #default="{ row }">
            <el-input v-model="row.sourcePath" size="small" placeholder="如: $.value" />
          </template>
        </el-table-column>
        <el-table-column label="数据类型" width="140">
          <template #default="{ row }">
            <el-select v-model="row.dataType" size="small" style="width: 100%">
              <el-option label="string" value="string" />
              <el-option label="number" value="number" />
              <el-option label="datetime" value="datetime" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="日期格式" width="180">
          <template #default="{ row }">
            <el-input v-model="row.dateFormat" size="small" placeholder="yyyy-MM-dd HH:mm:ss" v-if="row.dataType === 'datetime'" />
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="70" align="center">
          <template #default="{ row }">
            <el-checkbox v-model="row.required" />
          </template>
        </el-table-column>
        <el-table-column label="默认值" width="160">
          <template #default="{ row }">
            <el-input v-model="row.defaultValue" size="small" placeholder="可选" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeMapping('item', $index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 保存按钮 -->
    <el-card shadow="never" class="action-card" v-if="selectedVendor">
      <div class="action-row">
        <el-button type="primary" size="large" @click="handleSave" :loading="saving">
          <el-icon><Check /></el-icon>
          保存映射配置
        </el-button>
        <el-button size="large" @click="handleReset">
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
      </div>
    </el-card>

    <!-- 未选择厂家提示 -->
    <el-card shadow="never" class="empty-card" v-if="!selectedVendor">
      <el-empty description="请先选择厂家以配置字段映射" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Delete, Check, RefreshLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

// 厂家接口
interface Vendor {
  vendorCode: string
  vendorName: string
}

// 字段映射接口
interface FieldMapping {
  targetField: string
  sourcePath: string
  dataType: string
  dateFormat: string
  required: boolean
  defaultValue: string
}

// 目标字段选项
const targetFieldOptions = [
  { label: 'patientId (患者ID)', value: 'patientId' },
  { label: 'visitNo (就诊号)', value: 'visitNo' },
  { label: 'patientVisitId (患者就诊ID)', value: 'patientVisitId' },
  { label: 'wardCode (病区编码)', value: 'wardCode' },
  { label: 'bedNo (床号)', value: 'bedNo' },
  { label: 'recordTime (记录时间)', value: 'recordTime' },
  { label: 'operatorCode (操作员编码)', value: 'operatorCode' },
  { label: 'operatorName (操作员姓名)', value: 'operatorName' },
  { label: 'temperature (体温)', value: 'temperature' },
  { label: 'pulse (脉搏)', value: 'pulse' },
  { label: 'breathing (呼吸)', value: 'breathing' },
  { label: 'bloodPressureHigh (收缩压)', value: 'bloodPressureHigh' },
  { label: 'bloodPressureLow (舒张压)', value: 'bloodPressureLow' },
  { label: 'hospitalCode (医院编码)', value: 'hospitalCode' },
  { label: 'hospitalName (医院名称)', value: 'hospitalName' },
  { label: 'deptCode (科室编码)', value: 'deptCode' },
  { label: 'deptName (科室名称)', value: 'deptName' }
]

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const saving = ref(false)
const loading = ref(false)

// 创建空的映射行
const createEmptyMapping = (): FieldMapping => ({
  targetField: '',
  sourcePath: '',
  dataType: 'string',
  dateFormat: '',
  required: false,
  defaultValue: ''
})

// 三个区域的映射数据
const rootMappings = ref<FieldMapping[]>([])
const recordMappings = ref<FieldMapping[]>([])
const itemMappings = ref<FieldMapping[]>([])

// 厂家切换
const handleVendorChange = (vendorCode: string) => {
  if (vendorCode) {
    loadMappings(vendorCode)
  } else {
    rootMappings.value = []
    recordMappings.value = []
    itemMappings.value = []
  }
}

// 加载映射配置
const loadMappings = async (vendorCode: string) => {
  try {
    // 实际应调用API加载配置
    // 模拟加载已有配置
    console.log('加载厂家映射配置:', vendorCode)
    rootMappings.value = [
      { targetField: 'hospitalCode', sourcePath: '$.hospital_code', dataType: 'string', dateFormat: '', required: true, defaultValue: '' },
      { targetField: 'hospitalName', sourcePath: '$.hospital_name', dataType: 'string', dateFormat: '', required: true, defaultValue: '' }
    ]
    recordMappings.value = [
      { targetField: 'patientId', sourcePath: '$.patient_id', dataType: 'string', dateFormat: '', required: true, defaultValue: '' },
      { targetField: 'visitNo', sourcePath: '$.visit_no', dataType: 'string', dateFormat: '', required: true, defaultValue: '' },
      { targetField: 'recordTime', sourcePath: '$.record_time', dataType: 'datetime', dateFormat: 'yyyy-MM-dd HH:mm:ss', required: true, defaultValue: '' }
    ]
    itemMappings.value = [
      { targetField: 'temperature', sourcePath: '$.temperature', dataType: 'number', dateFormat: '', required: true, defaultValue: '' }
    ]
  } catch {
    ElMessage.error('加载映射配置失败')
  }
}

// 添加映射
const addMapping = (section: 'root' | 'record' | 'item') => {
  const newMapping = createEmptyMapping()
  switch (section) {
    case 'root':
      rootMappings.value.push(newMapping)
      break
    case 'record':
      recordMappings.value.push(newMapping)
      break
    case 'item':
      itemMappings.value.push(newMapping)
      break
  }
}

// 删除映射
const removeMapping = (section: 'root' | 'record' | 'item', index: number) => {
  switch (section) {
    case 'root':
      rootMappings.value.splice(index, 1)
      break
    case 'record':
      recordMappings.value.splice(index, 1)
      break
    case 'item':
      itemMappings.value.splice(index, 1)
      break
  }
}

// 保存映射配置
const handleSave = async () => {
  // 校验
  const allMappings = [...rootMappings.value, ...recordMappings.value, ...itemMappings.value]
  const emptyFields = allMappings.filter((m) => !m.targetField || !m.sourcePath)
  if (emptyFields.length > 0) {
    ElMessage.warning('请确保所有映射的目标字段和来源路径都已填写')
    return
  }

  // 检查目标字段重复
  const fieldSet = new Set<string>()
  for (const m of allMappings) {
    if (fieldSet.has(m.targetField)) {
      ElMessage.warning(`目标字段 "${m.targetField}" 存在重复`)
      return
    }
    fieldSet.add(m.targetField)
  }

  try {
    await ElMessageBox.confirm('确定要保存当前映射配置吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    saving.value = true
    // 实际调用保存API
    await new Promise((resolve) => setTimeout(resolve, 1000))
    ElMessage.success('映射配置保存成功')
  } catch {
    // 取消操作
  } finally {
    saving.value = false
  }
}

// 重置
const handleReset = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有映射配置吗？这将丢失未保存的更改。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    if (selectedVendor.value) {
      loadMappings(selectedVendor.value)
    }
    ElMessage.success('已重置')
  } catch {
    // 取消操作
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

// 初始化
onMounted(() => {
  fetchVendorList()
})
</script>

<style scoped lang="scss">
.field-mapping-container {
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

.mapping-card {
  margin-bottom: 16px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .text-muted {
    color: #c0c4cc;
    font-size: 12px;
  }
}

.action-card {
  margin-bottom: 16px;

  .action-row {
    display: flex;
    justify-content: center;
    gap: 16px;
  }
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
