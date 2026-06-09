<template>
  <div class="smartcare-field-mapping">
    <el-card shadow="never">
      <template #header>
        <span>SmartCare字段映射</span>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 患者信息映射 -->
        <el-tab-pane label="患者信息(patient)" name="patient">
          <el-form label-width="180px" style="max-width: 650px">
            <el-form-item
              v-for="field in patientFields"
              :key="field.standard"
              :label="field.standard"
            >
              <el-input
                v-model="field.actual"
                :placeholder="`默认: ${field.default}`"
              />
              <div class="field-hint">{{ field.description }}</div>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="saveMapping('patient')" :loading="saveLoading">
                保存
              </el-button>
              <el-button @click="resetMapping('patient')">重置默认</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 床旁数据映射 -->
        <el-tab-pane label="床旁数据(bedside)" name="bedside">
          <el-form label-width="180px" style="max-width: 650px">
            <el-form-item
              v-for="field in bedsideFields"
              :key="field.standard"
              :label="field.standard"
            >
              <el-input
                v-model="field.actual"
                :placeholder="`默认: ${field.default}`"
              />
              <div class="field-hint">{{ field.description }}</div>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="saveMapping('bedside')" :loading="saveLoading">
                保存
              </el-button>
              <el-button @click="resetMapping('bedside')">重置默认</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 配置参数映射 -->
        <el-tab-pane label="配置参数(configParam)" name="configParam">
          <el-form label-width="180px" style="max-width: 650px">
            <el-form-item
              v-for="field in configParamFields"
              :key="field.standard"
              :label="field.standard"
            >
              <el-input
                v-model="field.actual"
                :placeholder="`默认: ${field.default}`"
              />
              <div class="field-hint">{{ field.description }}</div>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="saveMapping('configParam')" :loading="saveLoading">
                保存
              </el-button>
              <el-button @click="resetMapping('configParam')">重置默认</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface FieldMapping {
  standard: string
  actual: string
  default: string
  description: string
}

const activeTab = ref('patient')
const saveLoading = ref(false)

const patientFields = reactive<FieldMapping[]>([
  { standard: 'patientId', actual: '', default: '_id', description: '患者唯一标识' },
  { standard: 'hisPid', actual: '', default: 'hisPid', description: 'HIS系统患者ID' },
  { standard: 'mrn', actual: '', default: 'mrn', description: '病案号' },
  { standard: 'name', actual: '', default: 'name', description: '患者姓名' },
  { standard: 'bedNo', actual: '', default: 'hisBed', description: '床号' },
  { standard: 'deptCode', actual: '', default: 'deptCode', description: '科室编码' },
  { standard: 'status', actual: '', default: 'status', description: '患者状态' }
])

const bedsideFields = reactive<FieldMapping[]>([
  { standard: 'patientId', actual: '', default: 'pid', description: '患者标识' },
  { standard: 'recordTime', actual: '', default: 'time', description: '记录时间' },
  { standard: 'itemCode', actual: '', default: 'code', description: '指标编码' },
  { standard: 'itemValue', actual: '', default: 'strVal', description: '指标值' },
  { standard: 'dataType', actual: '', default: 'dataType', description: '数据类型' }
])

const configParamFields = reactive<FieldMapping[]>([
  { standard: 'paramCode', actual: '', default: 'code', description: '参数编码' },
  { standard: 'paramName', actual: '', default: 'name', description: '参数名称' },
  { standard: 'dataType', actual: '', default: 'dataType', description: '数据类型' },
  { standard: 'unit', actual: '', default: 'unit', description: '单位' },
  { standard: 'calculation', actual: '', default: 'calculation', description: '计算方式' }
])

function resetMapping(collection: string) {
  let fields: FieldMapping[]
  if (collection === 'patient') fields = patientFields
  else if (collection === 'bedside') fields = bedsideFields
  else fields = configParamFields

  fields.forEach((f) => {
    f.actual = f.default
  })
  ElMessage.info('已重置为默认值')
}

async function loadMapping() {
  try {
    // TODO: Replace with actual API call
    // const res = await api.getSmartCareFieldMapping()
    // Apply defaults
    resetMappingSilent(patientFields)
    resetMappingSilent(bedsideFields)
    resetMappingSilent(configParamFields)
  } catch {
    ElMessage.error('加载字段映射失败')
  }
}

function resetMappingSilent(fields: FieldMapping[]) {
  fields.forEach((f) => {
    f.actual = f.default
  })
}

async function saveMapping(collection: string) {
  saveLoading.value = true
  try {
    let fields: FieldMapping[]
    if (collection === 'patient') fields = patientFields
    else if (collection === 'bedside') fields = bedsideFields
    else fields = configParamFields

    const mapping: Record<string, string> = {}
    fields.forEach((f) => {
      mapping[f.standard] = f.actual || f.default
    })

    // TODO: Replace with actual API call
    // await api.saveSmartCareFieldMapping(collection, mapping)
    ElMessage.success('字段映射保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

onMounted(() => {
  loadMapping()
})
</script>

<style scoped>
.smartcare-field-mapping {
  padding: 16px;
}
.field-hint {
  color: #909399;
  font-size: 12px;
  line-height: 1.4;
  margin-top: 2px;
}
</style>
