<template>
  <div class="intake-output-config">
    <el-card shadow="never">
      <template #header>
        <span>出入量配置</span>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 项目配置 Tab -->
        <el-tab-pane label="项目配置" name="project">
          <div style="margin-bottom: 16px">
            <el-button type="primary" @click="syncFromSmartCare" :loading="syncLoading">
              从SmartCare同步
            </el-button>
          </div>

          <el-table :data="projectList" border v-loading="projectLoading">
            <el-table-column prop="paramCode" label="参数编码" width="130" />
            <el-table-column prop="paramName" label="参数名称" width="150" />
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                <el-select
                  v-model="row.category"
                  size="small"
                  style="width: 100%"
                >
                  <el-option label="入量(input)" value="input" />
                  <el-option label="出量(output)" value="output" />
                  <el-option label="尿液(urine)" value="urine" />
                  <el-option label="大便(stool)" value="stool" />
                  <el-option label="引流(drainage)" value="drainage" />
                  <el-option label="呕吐(vomit)" value="vomit" />
                  <el-option label="其他(other)" value="other" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="statType" label="统计方式" width="130">
              <template #default="{ row }">
                <el-select
                  v-model="row.statType"
                  size="small"
                  style="width: 100%"
                >
                  <el-option label="求和(sum)" value="sum" />
                  <el-option label="计数(count)" value="count" />
                  <el-option label="最新值(latest)" value="latest" />
                  <el-option label="文本合并(text_merge)" value="text_merge" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="100">
              <template #default="{ row }">
                <el-input v-model="row.unit" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="计入总入量" width="110" align="center">
              <template #default="{ row }">
                <el-checkbox v-model="row.includeInTotalInput" />
              </template>
            </el-table-column>
            <el-table-column label="计入总出量" width="110" align="center">
              <template #default="{ row }">
                <el-checkbox v-model="row.includeInTotalOutput" />
              </template>
            </el-table-column>
            <el-table-column prop="enabled" label="启用" width="80" align="center">
              <template #default="{ row }">
                <el-switch v-model="row.enabled" />
              </template>
            </el-table-column>
          </el-table>

          <div style="margin-top: 16px; text-align: right">
            <el-button type="success" @click="saveProjectConfig" :loading="saveProjectLoading">
              保存配置
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 统计规则 Tab -->
        <el-tab-pane label="统计规则" name="rules">
          <div style="margin-bottom: 16px">
            <el-button type="primary" @click="openRuleDialog()">新增规则</el-button>
          </div>

          <el-table :data="ruleList" border v-loading="ruleLoading">
            <el-table-column prop="code" label="规则编码" width="120" />
            <el-table-column prop="name" label="规则名称" width="150" />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                {{ categoryLabel(row.category) }}
              </template>
            </el-table-column>
            <el-table-column prop="statType" label="统计方式" width="110">
              <template #default="{ row }">
                {{ statTypeLabel(row.statType) }}
              </template>
            </el-table-column>
            <el-table-column label="时间窗口" width="180">
              <template #default="{ row }">
                {{ formatTimeWindow(row.timeWindow) }}
              </template>
            </el-table-column>
            <el-table-column prop="targetItemCode" label="目标指标编码" width="130" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="enabled" label="启用" width="80" align="center">
              <template #default="{ row }">
                <el-switch v-model="row.enabled" @change="toggleRule(row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openRuleDialog(row)">编辑</el-button>
                <el-popconfirm title="确定删除该规则？" @confirm="deleteRule(row.code)">
                  <template #reference>
                    <el-button link type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 统计规则新增/编辑对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      :title="isEditRule ? '编辑统计规则' : '新增统计规则'"
      width="620px"
      destroy-on-close
    >
      <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        :rules="ruleFormRules"
        label-width="120px"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="规则编码" prop="code">
              <el-input v-model="ruleForm.code" :disabled="isEditRule" placeholder="如 URINE_24H" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="ruleForm.name" placeholder="如 24小时尿量" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="ruleForm.category" style="width: 100%">
                <el-option label="入量(input)" value="input" />
                <el-option label="出量(output)" value="output" />
                <el-option label="尿液(urine)" value="urine" />
                <el-option label="大便(stool)" value="stool" />
                <el-option label="引流(drainage)" value="drainage" />
                <el-option label="呕吐(vomit)" value="vomit" />
                <el-option label="其他(other)" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="统计方式" prop="statType">
              <el-select v-model="ruleForm.statType" style="width: 100%">
                <el-option label="求和(sum)" value="sum" />
                <el-option label="计数(count)" value="count" />
                <el-option label="最新值(latest)" value="latest" />
                <el-option label="文本合并(text_merge)" value="text_merge" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">时间窗口</el-divider>
        <el-form-item label="窗口类型" prop="timeWindowType">
          <el-select v-model="ruleForm.timeWindowType" style="width: 100%" @change="onTimeWindowTypeChange">
            <el-option label="滚动(rolling)" value="rolling" />
            <el-option label="自然日(day)" value="day" />
            <el-option label="班次(shift)" value="shift" />
            <el-option label="自定义(custom)" value="custom" />
          </el-select>
        </el-form-item>

        <!-- 滚动窗口 -->
        <template v-if="ruleForm.timeWindowType === 'rolling'">
          <el-form-item label="滚动小时数">
            <el-input-number v-model="ruleForm.rollingHours" :min="1" :max="72" />
            <span style="margin-left: 8px; color: #909399">小时</span>
          </el-form-item>
        </template>

        <!-- 自然日窗口 -->
        <template v-if="ruleForm.timeWindowType === 'day'">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="开始时间">
                <el-time-picker v-model="ruleForm.startTime" format="HH:mm" value-format="HH:mm" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束时间">
                <el-time-picker v-model="ruleForm.endTime" format="HH:mm" value-format="HH:mm" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <el-divider content-position="left">目标指标</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标指标编码" prop="targetItemCode">
              <el-input v-model="ruleForm.targetItemCode" placeholder="如 TOTAL_URINE" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标指标名称">
              <el-input v-model="ruleForm.targetItemName" placeholder="如 总尿量" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="单位">
          <el-input v-model="ruleForm.unit" placeholder="如 ml" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRule" :loading="submitRuleLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

interface ProjectItem {
  paramCode: string
  paramName: string
  category: string
  statType: string
  unit: string
  includeInTotalInput: boolean
  includeInTotalOutput: boolean
  enabled: boolean
}

interface TimeWindow {
  type: string
  hours?: number
  startTime?: string
  endTime?: string
}

interface RuleItem {
  code: string
  name: string
  category: string
  statType: string
  timeWindow: TimeWindow
  targetItemCode: string
  targetItemName: string
  unit: string
  enabled: boolean
}

const activeTab = ref('project')
const syncLoading = ref(false)
const projectLoading = ref(false)
const saveProjectLoading = ref(false)
const ruleLoading = ref(false)
const submitRuleLoading = ref(false)

const projectList = ref<ProjectItem[]>([])
const ruleList = ref<RuleItem[]>([])

const categoryLabelMap: Record<string, string> = {
  input: '入量',
  output: '出量',
  urine: '尿液',
  stool: '大便',
  drainage: '引流',
  vomit: '呕吐',
  other: '其他'
}

const statTypeLabelMap: Record<string, string> = {
  sum: '求和',
  count: '计数',
  latest: '最新值',
  text_merge: '文本合并'
}

function categoryLabel(c: string): string {
  return categoryLabelMap[c] || c
}

function statTypeLabel(s: string): string {
  return statTypeLabelMap[s] || s
}

function formatTimeWindow(tw: TimeWindow): string {
  if (!tw) return '-'
  if (tw.type === 'rolling') return `滚动 ${tw.hours}小时`
  if (tw.type === 'day') return `自然日 ${tw.startTime || '00:00'} - ${tw.endTime || '24:00'}`
  if (tw.type === 'shift') return '班次'
  if (tw.type === 'custom') return '自定义'
  return tw.type
}

// Rule dialog
const ruleDialogVisible = ref(false)
const isEditRule = ref(false)
const ruleFormRef = ref<FormInstance>()

const ruleForm = reactive({
  code: '',
  name: '',
  category: 'urine',
  statType: 'sum',
  timeWindowType: 'rolling',
  rollingHours: 24,
  startTime: '07:00',
  endTime: '07:00',
  targetItemCode: '',
  targetItemName: '',
  unit: 'ml'
})

const ruleFormRules: FormRules = {
  code: [{ required: true, message: '请输入规则编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  statType: [{ required: true, message: '请选择统计方式', trigger: 'change' }],
  timeWindowType: [{ required: true, message: '请选择时间窗口类型', trigger: 'change' }],
  targetItemCode: [{ required: true, message: '请输入目标指标编码', trigger: 'blur' }]
}

function onTimeWindowTypeChange() {
  // Reset values when type changes
  if (ruleForm.timeWindowType === 'rolling') {
    ruleForm.rollingHours = 24
  } else if (ruleForm.timeWindowType === 'day') {
    ruleForm.startTime = '07:00'
    ruleForm.endTime = '07:00'
  }
}

async function loadProjectConfig() {
  projectLoading.value = true
  try {
    // TODO: Replace with actual API call
    projectList.value = []
  } catch {
    ElMessage.error('加载项目配置失败')
  } finally {
    projectLoading.value = false
  }
}

async function loadRuleList() {
  ruleLoading.value = true
  try {
    // TODO: Replace with actual API call
    ruleList.value = []
  } catch {
    ElMessage.error('加载统计规则失败')
  } finally {
    ruleLoading.value = false
  }
}

async function syncFromSmartCare() {
  syncLoading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.syncConfigParamFromSmartCare()
    ElMessage.success('同步完成')
    loadProjectConfig()
  } catch {
    ElMessage.error('同步失败')
  } finally {
    syncLoading.value = false
  }
}

async function saveProjectConfig() {
  saveProjectLoading.value = true
  try {
    // TODO: Replace with actual API call
    // await api.saveProjectConfig(projectList.value)
    ElMessage.success('项目配置保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saveProjectLoading.value = false
  }
}

function resetRuleForm() {
  ruleForm.code = ''
  ruleForm.name = ''
  ruleForm.category = 'urine'
  ruleForm.statType = 'sum'
  ruleForm.timeWindowType = 'rolling'
  ruleForm.rollingHours = 24
  ruleForm.startTime = '07:00'
  ruleForm.endTime = '07:00'
  ruleForm.targetItemCode = ''
  ruleForm.targetItemName = ''
  ruleForm.unit = 'ml'
}

function openRuleDialog(row?: RuleItem) {
  if (row) {
    isEditRule.value = true
    ruleForm.code = row.code
    ruleForm.name = row.name
    ruleForm.category = row.category
    ruleForm.statType = row.statType
    ruleForm.timeWindowType = row.timeWindow?.type || 'rolling'
    ruleForm.rollingHours = row.timeWindow?.hours || 24
    ruleForm.startTime = row.timeWindow?.startTime || '07:00'
    ruleForm.endTime = row.timeWindow?.endTime || '07:00'
    ruleForm.targetItemCode = row.targetItemCode
    ruleForm.targetItemName = row.targetItemName || ''
    ruleForm.unit = row.unit || ''
  } else {
    isEditRule.value = false
    resetRuleForm()
  }
  ruleDialogVisible.value = true
}

async function submitRule() {
  if (!ruleFormRef.value) return
  await ruleFormRef.value.validate()
  submitRuleLoading.value = true
  try {
    const timeWindow: TimeWindow = { type: ruleForm.timeWindowType }
    if (ruleForm.timeWindowType === 'rolling') {
      timeWindow.hours = ruleForm.rollingHours
    } else if (ruleForm.timeWindowType === 'day') {
      timeWindow.startTime = ruleForm.startTime
      timeWindow.endTime = ruleForm.endTime
    }

    const payload: Omit<RuleItem, 'enabled'> = {
      code: ruleForm.code,
      name: ruleForm.name,
      category: ruleForm.category,
      statType: ruleForm.statType,
      timeWindow,
      targetItemCode: ruleForm.targetItemCode,
      targetItemName: ruleForm.targetItemName,
      unit: ruleForm.unit
    }

    if (isEditRule.value) {
      // TODO: await api.updateStatRule(ruleForm.code, payload)
      ElMessage.success('规则更新成功')
    } else {
      // TODO: await api.createStatRule(payload)
      ElMessage.success('规则创建成功')
    }
    ruleDialogVisible.value = false
    loadRuleList()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitRuleLoading.value = false
  }
}

async function deleteRule(code: string) {
  try {
    // TODO: await api.deleteStatRule(code)
    ElMessage.success('删除成功')
    loadRuleList()
  } catch {
    ElMessage.error('删除失败')
  }
}

async function toggleRule(row: RuleItem) {
  try {
    // TODO: await api.updateStatRule(row.code, { enabled: row.enabled })
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadProjectConfig()
  loadRuleList()
})
</script>

<style scoped>
.intake-output-config {
  padding: 16px;
}
</style>
