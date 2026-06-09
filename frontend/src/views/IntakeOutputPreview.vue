<template>
  <div class="intake-output-preview">
    <el-card shadow="never">
      <template #header>
        <span>出入量计算预览</span>
      </template>

      <!-- 顶部查询区 -->
      <el-form :inline="true" class="filter-bar">
        <el-form-item label="数据源">
          <el-select v-model="selectedDatasource" placeholder="请选择数据源" style="width: 200px">
            <el-option
              v-for="ds in datasourceList"
              :key="ds.id"
              :label="ds.name"
              :value="ds.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="患者">
          <el-input
            v-model="patientSearch"
            placeholder="输入患者ID或姓名"
            clearable
            style="width: 220px"
            @keyup.enter="searchPatient"
          >
            <template #append>
              <el-button @click="searchPatient" :loading="patientSearching">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
          <el-select
            v-if="patientOptions.length"
            v-model="selectedPatient"
            placeholder="选择患者"
            style="width: 220px; margin-left: 8px"
            value-key="patientId"
            @change="onPatientSelect"
          >
            <el-option
              v-for="p in patientOptions"
              :key="p.patientId"
              :label="`${p.name} (${p.patientId}) — ${p.bedNo}`"
              :value="p"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doPreview" :loading="previewLoading">
            计算预览
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 结果区 -->
      <template v-if="showResult">
        <!-- 患者信息卡片 -->
        <el-card shadow="hover" class="patient-info-card">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="姓名">{{ patientInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="床号">{{ patientInfo.bedNo }}</el-descriptions-item>
            <el-descriptions-item label="病区">{{ patientInfo.wardCode }}</el-descriptions-item>
          </el-descriptions>
          <div class="time-range-display">
            统计时间范围: {{ dateRange?.[0] || '-' }} 至 {{ dateRange?.[1] || '-' }}
          </div>
        </el-card>

        <!-- 计算结果表格 -->
        <el-table :data="calcResults" border style="margin-top: 16px">
          <el-table-column prop="code" label="指标编码" width="140" />
          <el-table-column prop="name" label="指标名称" width="160" />
          <el-table-column prop="value" label="值" width="120" align="right">
            <template #default="{ row }">
              <strong>{{ row.value }}</strong>
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="statType" label="统计方式" width="100">
            <template #default="{ row }">
              {{ statTypeLabel(row.statType) }}
            </template>
          </el-table-column>
          <el-table-column prop="itemCount" label="数据条数" width="100" align="center" />
        </el-table>

        <!-- 收支平衡卡片 -->
        <el-card shadow="hover" class="balance-card">
          <div class="balance-content">
            <div class="balance-item">
              <span class="balance-label">总入量</span>
              <span class="balance-value input-value">{{ balanceData.totalInput }} ml</span>
            </div>
            <span class="balance-operator">-</span>
            <div class="balance-item">
              <span class="balance-label">总出量</span>
              <span class="balance-value output-value">{{ balanceData.totalOutput }} ml</span>
            </div>
            <span class="balance-operator">=</span>
            <div class="balance-item">
              <span class="balance-label">出入量平衡</span>
              <span
                class="balance-value"
                :class="balanceData.balance >= 0 ? 'positive' : 'negative'"
              >
                {{ balanceData.balance }} ml
              </span>
            </div>
          </div>
          <div style="text-align: right; margin-top: 16px">
            <el-button type="success" @click="saveToVitalChart" :loading="saveLoading">
              保存到体温单
            </el-button>
          </div>
        </el-card>

        <!-- 原始床旁数据详情 -->
        <el-collapse style="margin-top: 16px">
          <el-collapse-item title="原始床旁数据详情" name="raw">
            <el-table :data="rawBedsideData" border size="small">
              <el-table-column prop="recordTime" label="记录时间" width="180" />
              <el-table-column prop="itemCode" label="指标编码" width="120" />
              <el-table-column prop="itemName" label="指标名称" width="140" />
              <el-table-column prop="itemValue" label="原始值" width="120" />
              <el-table-column prop="unit" label="单位" width="80" />
              <el-table-column prop="category" label="分类" width="100">
                <template #default="{ row }">
                  {{ categoryLabel(row.category) }}
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </template>

      <el-empty v-if="!showResult && !previewLoading" description="请选择数据源和患者后点击计算预览" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

interface DatasourceOption {
  id: string
  name: string
}

interface PatientOption {
  patientId: string
  name: string
  bedNo: string
  wardCode: string
}

interface CalcResult {
  code: string
  name: string
  value: number | string
  unit: string
  statType: string
  itemCount: number
}

interface RawBedsideRecord {
  recordTime: string
  itemCode: string
  itemName: string
  itemValue: string
  unit: string
  category: string
}

const previewLoading = ref(false)
const patientSearching = ref(false)
const saveLoading = ref(false)
const showResult = ref(false)

const selectedDatasource = ref('')
const datasourceList = ref<DatasourceOption[]>([])
const patientSearch = ref('')
const patientOptions = ref<PatientOption[]>([])
const selectedPatient = ref<PatientOption | null>(null)
const dateRange = ref<string[] | null>(null)

const patientInfo = reactive<PatientOption>({
  patientId: '',
  name: '',
  bedNo: '',
  wardCode: ''
})

const calcResults = ref<CalcResult[]>([])
const rawBedsideData = ref<RawBedsideRecord[]>([])

const balanceData = computed(() => {
  let totalInput = 0
  let totalOutput = 0
  calcResults.value.forEach((r) => {
    const v = typeof r.value === 'number' ? r.value : parseFloat(String(r.value)) || 0
    if (r.code.startsWith('IN_') || r.code.includes('input')) {
      totalInput += v
    } else if (r.code.startsWith('OUT_') || r.code.includes('output') || r.code.includes('urine')) {
      totalOutput += v
    }
  })
  return {
    totalInput,
    totalOutput,
    balance: totalInput - totalOutput
  }
})

const statTypeLabelMap: Record<string, string> = {
  sum: '求和',
  count: '计数',
  latest: '最新值',
  text_merge: '文本合并'
}

const categoryLabelMap: Record<string, string> = {
  input: '入量',
  output: '出量',
  urine: '尿液',
  stool: '大便',
  drainage: '引流',
  vomit: '呕吐',
  other: '其他'
}

function statTypeLabel(s: string): string {
  return statTypeLabelMap[s] || s
}

function categoryLabel(c: string): string {
  return categoryLabelMap[c] || c
}

async function loadDatasourceList() {
  try {
    // TODO: Replace with actual API call
    datasourceList.value = []
  } catch {
    ElMessage.error('加载数据源列表失败')
  }
}

async function searchPatient() {
  if (!patientSearch.value.trim()) {
    ElMessage.warning('请输入患者ID或姓名')
    return
  }
  patientSearching.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.searchPatient(selectedDatasource.value, patientSearch.value)
    patientOptions.value = []
    if (!patientOptions.value.length) {
      ElMessage.info('未找到匹配的患者')
    }
  } catch {
    ElMessage.error('搜索患者失败')
  } finally {
    patientSearching.value = false
  }
}

function onPatientSelect(patient: PatientOption) {
  patientInfo.patientId = patient.patientId
  patientInfo.name = patient.name
  patientInfo.bedNo = patient.bedNo
  patientInfo.wardCode = patient.wardCode
}

async function doPreview() {
  if (!selectedDatasource.value) {
    ElMessage.warning('请选择数据源')
    return
  }
  if (!selectedPatient.value) {
    ElMessage.warning('请选择患者')
    return
  }
  if (!dateRange.value || dateRange.value.length < 2) {
    ElMessage.warning('请选择日期范围')
    return
  }
  previewLoading.value = true
  showResult.value = false
  try {
    // TODO: Replace with actual API call
    // const res = await api.previewIntakeOutput({
    //   datasourceId: selectedDatasource.value,
    //   patientId: selectedPatient.value.patientId,
    //   startDate: dateRange.value[0],
    //   endDate: dateRange.value[1]
    // })
    calcResults.value = []
    rawBedsideData.value = []
    showResult.value = true
  } catch {
    ElMessage.error('计算预览失败')
  } finally {
    previewLoading.value = false
  }
}

async function saveToVitalChart() {
  if (!calcResults.value.length) {
    ElMessage.warning('暂无计算结果可保存')
    return
  }
  saveLoading.value = true
  try {
    // TODO: Replace with actual API call
    // await api.saveToVitalChart({
    //   datasourceId: selectedDatasource.value,
    //   patientId: patientInfo.patientId,
    //   dateRange: dateRange.value,
    //   results: calcResults.value
    // })
    ElMessage.success('已保存到体温单')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

loadDatasourceList()
</script>

<style scoped>
.intake-output-preview {
  padding: 16px;
}
.filter-bar {
  margin-bottom: 8px;
}
.patient-info-card {
  margin-top: 16px;
}
.time-range-display {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}
.balance-card {
  margin-top: 16px;
}
.balance-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}
.balance-item {
  text-align: center;
}
.balance-label {
  display: block;
  color: #909399;
  font-size: 13px;
  margin-bottom: 4px;
}
.balance-value {
  font-size: 24px;
  font-weight: bold;
}
.input-value {
  color: #409eff;
}
.output-value {
  color: #e6a23c;
}
.balance-operator {
  font-size: 24px;
  color: #909399;
}
.positive {
  color: #67c23a;
}
.negative {
  color: #f56c6c;
}
</style>
