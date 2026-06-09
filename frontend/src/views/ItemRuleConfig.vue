<template>
  <div class="item-rule-config">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>指标规则配置</span>
          <div class="header-actions">
            <el-select
              v-model="selectedVendor"
              placeholder="请选择厂商"
              clearable
              style="width: 200px; margin-right: 12px"
              @change="loadRules"
            >
              <el-option
                v-for="v in vendorList"
                :key="v.code"
                :label="v.name"
                :value="v.code"
              />
            </el-select>
            <el-button type="primary" @click="openAddDialog">新增规则</el-button>
            <el-button @click="openTestDialog">测试匹配</el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="ruleList"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="ruleId" label="规则ID" width="100" />
        <el-table-column prop="matchField" label="匹配字段" width="120">
          <template #default="{ row }">
            <el-tag>{{ matchFieldLabel(row.matchField) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="matchType" label="匹配方式" width="120">
          <template #default="{ row }">
            {{ matchTypeLabel(row.matchType) }}
          </template>
        </el-table-column>
        <el-table-column prop="matchValue" label="匹配值" min-width="150" show-overflow-tooltip />
        <el-table-column prop="targetCode" label="目标编码" width="120" />
        <el-table-column prop="targetName" label="目标名称" width="120" />
        <el-table-column prop="dataType" label="数据类型" width="110" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="priority" label="优先级" width="80" align="center" />
        <el-table-column prop="enabled" label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="toggleEnabled(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm
              title="确定删除该规则？"
              @confirm="deleteRule(row.ruleId)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑规则对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑规则' : '新增规则'"
      width="680px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="110px"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="匹配字段" prop="matchField">
              <el-select v-model="formData.matchField" placeholder="请选择" style="width: 100%">
                <el-option label="item_id" value="item_id" />
                <el-option label="item_name" value="item_name" />
                <el-option label="item_tag" value="item_tag" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="匹配方式" prop="matchType">
              <el-select v-model="formData.matchType" placeholder="请选择" style="width: 100%">
                <el-option label="精确匹配(equals)" value="equals" />
                <el-option label="包含(contains)" value="contains" />
                <el-option label="正则(regex)" value="regex" />
                <el-option label="前缀(starts_with)" value="starts_with" />
                <el-option label="列表(in_list)" value="in_list" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="匹配值" prop="matchValue">
          <el-input v-model="formData.matchValue" placeholder="多个值用逗号分隔" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标编码" prop="targetCode">
              <el-input v-model="formData.targetCode" placeholder="如 HR, SpO2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标名称" prop="targetName">
              <el-input v-model="formData.targetName" placeholder="如 心率, 血氧" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="数据类型" prop="dataType">
              <el-select v-model="formData.dataType" placeholder="请选择" style="width: 100%">
                <el-option label="number" value="number" />
                <el-option label="string" value="string" />
                <el-option label="blood_pressure" value="blood_pressure" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="formData.unit" placeholder="如 bpm, mmHg" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="formData.priority" :min="0" :max="9999" />
        </el-form-item>

        <!-- 血压特殊字段 -->
        <template v-if="formData.dataType === 'blood_pressure'">
          <el-divider content-position="left">血压分割配置</el-divider>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="分割符">
                <el-input v-model="formData.splitSeparator" placeholder="如 /" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="分割字段">
                <el-checkbox-group v-model="formData.splitFields">
                  <el-checkbox label="systolic">收缩压</el-checkbox>
                  <el-checkbox label="diastolic">舒张压</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <el-divider content-position="left">高级配置</el-divider>
        <el-form-item label="值字典映射">
          <el-input
            v-model="formData.valueDict"
            type="textarea"
            :rows="3"
            placeholder='JSON格式，如 {"1":"阳性","0":"阴性"}'
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="正则表达式">
              <el-input v-model="formData.regexPattern" placeholder="正则表达式" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="正则分组">
              <el-input v-model="formData.regexGroup" placeholder="如 $1" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试匹配对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试匹配"
      width="780px"
      destroy-on-close
    >
      <el-form label-width="100px">
        <el-form-item label="厂商">
          <el-select v-model="testVendor" placeholder="请选择厂商" style="width: 300px">
            <el-option
              v-for="v in vendorList"
              :key="v.code"
              :label="v.name"
              :value="v.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="样本数据">
          <el-input
            v-model="testSampleData"
            type="textarea"
            :rows="8"
            placeholder='粘贴JSON格式的指标数据，如 [{"item_id":"HR","item_name":"心率","value":"75"}]'
          />
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="runTestMatch" :loading="testLoading" style="margin-bottom: 16px">
        执行测试
      </el-button>
      <el-table v-if="testResults.length" :data="testResults" border>
        <el-table-column prop="item_id" label="指标ID" width="120" />
        <el-table-column prop="item_name" label="指标名称" width="120" />
        <el-table-column prop="matched" label="是否匹配" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.matched ? 'success' : 'danger'">
              {{ row.matched ? '匹配' : '未匹配' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="matchedRule" label="匹配规则" width="140" />
        <el-table-column prop="targetCode" label="目标编码" width="100" />
        <el-table-column prop="targetName" label="目标名称" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import request from '@/api/request'

interface VendorOption {
  code: string
  name: string
}

interface RuleRow {
  ruleId: string
  matchField: string
  matchType: string
  matchValue: string
  targetCode: string
  targetName: string
  dataType: string
  unit: string
  priority: number
  enabled: boolean
  splitSeparator?: string
  splitFields?: string[]
  valueDict?: string
  regexPattern?: string
  regexGroup?: string
}

interface TestResult {
  item_id: string
  item_name: string
  matched: boolean
  matchedRule: string
  targetCode: string
  targetName: string
}

const loading = ref(false)
const submitLoading = ref(false)
const testLoading = ref(false)
const selectedVendor = ref('')
const vendorList = ref<VendorOption[]>([])
const ruleList = ref<RuleRow[]>([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingRuleId = ref('')
const formRef = ref<FormInstance>()

const testDialogVisible = ref(false)
const testVendor = ref('')
const testSampleData = ref('')
const testResults = ref<TestResult[]>([])

const matchFieldMap: Record<string, string> = {
  item_id: 'item_id',
  item_name: 'item_name',
  item_tag: 'item_tag'
}

const matchTypeMap: Record<string, string> = {
  equals: '精确匹配',
  contains: '包含',
  regex: '正则',
  starts_with: '前缀',
  in_list: '列表'
}

const formData = reactive({
  matchField: '',
  matchType: '',
  matchValue: '',
  targetCode: '',
  targetName: '',
  dataType: '',
  unit: '',
  priority: 100,
  splitSeparator: '/',
  splitFields: ['systolic', 'diastolic'] as string[],
  valueDict: '',
  regexPattern: '',
  regexGroup: ''
})

const formRules: FormRules = {
  matchField: [{ required: true, message: '请选择匹配字段', trigger: 'change' }],
  matchType: [{ required: true, message: '请选择匹配方式', trigger: 'change' }],
  matchValue: [{ required: true, message: '请输入匹配值', trigger: 'blur' }],
  targetCode: [{ required: true, message: '请输入目标编码', trigger: 'blur' }],
  targetName: [{ required: true, message: '请输入目标名称', trigger: 'blur' }],
  dataType: [{ required: true, message: '请选择数据类型', trigger: 'change' }]
}

function matchFieldLabel(field: string): string {
  return matchFieldMap[field] || field
}

function matchTypeLabel(type: string): string {
  return matchTypeMap[type] || type
}

async function loadVendorList() {
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

async function loadRules() {
  if (!selectedVendor.value) {
    ruleList.value = []
    return
  }
  loading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.getItemRules(selectedVendor.value)
    ruleList.value = []
  } catch {
    ElMessage.error('加载规则列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formData.matchField = ''
  formData.matchType = ''
  formData.matchValue = ''
  formData.targetCode = ''
  formData.targetName = ''
  formData.dataType = ''
  formData.unit = ''
  formData.priority = 100
  formData.splitSeparator = '/'
  formData.splitFields = ['systolic', 'diastolic']
  formData.valueDict = ''
  formData.regexPattern = ''
  formData.regexGroup = ''
}

function openAddDialog() {
  isEdit.value = false
  editingRuleId.value = ''
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: RuleRow) {
  isEdit.value = true
  editingRuleId.value = row.ruleId
  formData.matchField = row.matchField
  formData.matchType = row.matchType
  formData.matchValue = row.matchValue
  formData.targetCode = row.targetCode
  formData.targetName = row.targetName
  formData.dataType = row.dataType
  formData.unit = row.unit
  formData.priority = row.priority
  formData.splitSeparator = row.splitSeparator || '/'
  formData.splitFields = row.splitFields || ['systolic', 'diastolic']
  formData.valueDict = row.valueDict || ''
  formData.regexPattern = row.regexPattern || ''
  formData.regexGroup = row.regexGroup || ''
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const payload = { ...formData, vendorCode: selectedVendor.value }
    if (isEdit.value) {
      // TODO: await api.updateItemRule(editingRuleId.value, payload)
      ElMessage.success('规则更新成功')
    } else {
      // TODO: await api.createItemRule(payload)
      ElMessage.success('规则创建成功')
    }
    dialogVisible.value = false
    loadRules()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function deleteRule(ruleId: string) {
  try {
    // TODO: await api.deleteItemRule(ruleId)
    ElMessage.success('删除成功')
    loadRules()
  } catch {
    ElMessage.error('删除失败')
  }
}

async function toggleEnabled(row: RuleRow) {
  try {
    // TODO: await api.updateItemRule(row.ruleId, { enabled: row.enabled })
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  }
}

function openTestDialog() {
  testVendor.value = selectedVendor.value
  testSampleData.value = ''
  testResults.value = []
  testDialogVisible.value = true
}

async function runTestMatch() {
  if (!testVendor.value) {
    ElMessage.warning('请选择厂商')
    return
  }
  if (!testSampleData.value.trim()) {
    ElMessage.warning('请输入样本数据')
    return
  }
  let sampleItems: any[]
  try {
    sampleItems = JSON.parse(testSampleData.value)
  } catch {
    ElMessage.error('JSON格式错误')
    return
  }
  testLoading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.testMatch(testVendor.value, sampleItems)
    testResults.value = sampleItems.map((item: any) => ({
      item_id: item.item_id || '',
      item_name: item.item_name || '',
      matched: false,
      matchedRule: '-',
      targetCode: '-',
      targetName: '-'
    }))
  } catch {
    ElMessage.error('测试匹配失败')
  } finally {
    testLoading.value = false
  }
}

onMounted(() => {
  loadVendorList()
})
</script>

<style scoped>
.item-rule-config {
  padding: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-actions {
  display: flex;
  align-items: center;
}
</style>
