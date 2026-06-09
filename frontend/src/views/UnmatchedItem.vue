<template>
  <div class="unmatched-item">
    <el-card shadow="never">
      <template #header>
        <span>未识别指标处理</span>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" class="filter-bar">
        <el-form-item label="厂商">
          <el-select v-model="filter.vendorCode" placeholder="全部厂商" clearable style="width: 180px">
            <el-option
              v-for="v in vendorList"
              :key="v.code"
              :label="v.name"
              :value="v.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filter.status" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="未处理" value="unresolved" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="dataList" border v-loading="loading" row-key="id">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <el-descriptions title="指标原始数据" :column="3" border size="small">
                <el-descriptions-item
                  v-for="(val, key) in row.itemData"
                  :key="key"
                  :label="String(key)"
                >
                  {{ val }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="vendorCode" label="厂商编码" width="120" />
        <el-table-column prop="patientId" label="患者ID" width="140" />
        <el-table-column prop="recordTime" label="记录时间" width="180" />
        <el-table-column label="指标摘要" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ summarizeItem(row.itemData) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openAddRuleDialog(row)">
              一键添加规则
            </el-button>
            <el-button
              v-if="row.status === 'unresolved'"
              link type="info" size="small"
              @click="ignoreItem(row)"
            >
              忽略
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="loadData"
        @current-change="loadData"
      />
    </el-card>

    <!-- 一键添加规则对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      title="添加指标规则"
      width="680px"
      destroy-on-close
    >
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      >
        <template #title>
          基于未识别指标 <strong>{{ currentItem?.vendorCode }}</strong> 自动填充匹配条件，请补充目标映射信息。
        </template>
      </el-alert>

      <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        :rules="ruleFormRules"
        label-width="110px"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="匹配字段" prop="matchField">
              <el-select v-model="ruleForm.matchField" placeholder="请选择" style="width: 100%">
                <el-option label="item_id" value="item_id" />
                <el-option label="item_name" value="item_name" />
                <el-option label="item_tag" value="item_tag" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="匹配方式" prop="matchType">
              <el-select v-model="ruleForm.matchType" placeholder="请选择" style="width: 100%">
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
          <el-input v-model="ruleForm.matchValue" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标编码" prop="targetCode">
              <el-input v-model="ruleForm.targetCode" placeholder="如 HR, SpO2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标名称" prop="targetName">
              <el-input v-model="ruleForm.targetName" placeholder="如 心率, 血氧" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="数据类型" prop="dataType">
              <el-select v-model="ruleForm.dataType" placeholder="请选择" style="width: 100%">
                <el-option label="number" value="number" />
                <el-option label="string" value="string" />
                <el-option label="blood_pressure" value="blood_pressure" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="ruleForm.unit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="ruleForm.priority" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRule" :loading="submitLoading">保存规则并标记已解决</el-button>
      </template>
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

interface UnmatchedRow {
  id: string
  vendorCode: string
  patientId: string
  recordTime: string
  itemData: Record<string, any>
  status: string
}

const loading = ref(false)
const submitLoading = ref(false)
const vendorList = ref<VendorOption[]>([])
const dataList = ref<UnmatchedRow[]>([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const filter = reactive({
  vendorCode: '',
  status: ''
})

// Rule dialog
const ruleDialogVisible = ref(false)
const currentItem = ref<UnmatchedRow | null>(null)
const ruleFormRef = ref<FormInstance>()

const ruleForm = reactive({
  matchField: 'item_id',
  matchType: 'equals',
  matchValue: '',
  targetCode: '',
  targetName: '',
  dataType: 'number',
  unit: '',
  priority: 100
})

const ruleFormRules: FormRules = {
  matchField: [{ required: true, message: '请选择匹配字段', trigger: 'change' }],
  matchType: [{ required: true, message: '请选择匹配方式', trigger: 'change' }],
  matchValue: [{ required: true, message: '请输入匹配值', trigger: 'blur' }],
  targetCode: [{ required: true, message: '请输入目标编码', trigger: 'blur' }],
  targetName: [{ required: true, message: '请输入目标名称', trigger: 'blur' }],
  dataType: [{ required: true, message: '请选择数据类型', trigger: 'change' }]
}

function statusTagType(status: string): string {
  const map: Record<string, string> = {
    unresolved: 'danger',
    resolved: 'success',
    ignored: 'info'
  }
  return map[status] || 'info'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    unresolved: '未处理',
    resolved: '已解决',
    ignored: '已忽略'
  }
  return map[status] || status
}

function summarizeItem(itemData: Record<string, any>): string {
  if (!itemData) return '-'
  const name = itemData.item_name || itemData.name || ''
  const id = itemData.item_id || itemData.code || ''
  const value = itemData.value || itemData.item_value || ''
  return [id, name, value].filter(Boolean).join(' / ')
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

async function loadData() {
  loading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.getUnmatchedItems({ ...filter, page: pagination.page, pageSize: pagination.pageSize })
    dataList.value = []
    pagination.total = 0
  } catch {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

function openAddRuleDialog(row: UnmatchedRow) {
  currentItem.value = row
  const itemData = row.itemData || {}
  // Auto-fill matchField and matchValue from itemData
  if (itemData.item_id) {
    ruleForm.matchField = 'item_id'
    ruleForm.matchValue = String(itemData.item_id)
  } else if (itemData.item_name) {
    ruleForm.matchField = 'item_name'
    ruleForm.matchValue = String(itemData.item_name)
  } else if (itemData.item_tag) {
    ruleForm.matchField = 'item_tag'
    ruleForm.matchValue = String(itemData.item_tag)
  } else {
    ruleForm.matchField = 'item_id'
    ruleForm.matchValue = ''
  }
  ruleForm.matchType = 'equals'
  ruleForm.targetCode = ''
  ruleForm.targetName = ''
  ruleForm.dataType = 'number'
  ruleForm.unit = ''
  ruleForm.priority = 100
  ruleDialogVisible.value = true
}

async function submitRule() {
  if (!ruleFormRef.value) return
  await ruleFormRef.value.validate()
  submitLoading.value = true
  try {
    const payload = {
      ...ruleForm,
      vendorCode: currentItem.value?.vendorCode
    }
    // TODO: await api.createItemRule(payload)
    ElMessage.success('规则创建成功')
    // Mark as resolved
    if (currentItem.value) {
      // TODO: await api.updateUnmatchedItemStatus(currentItem.value.id, 'resolved')
    }
    ruleDialogVisible.value = false
    loadData()
  } catch {
    ElMessage.error('创建规则失败')
  } finally {
    submitLoading.value = false
  }
}

async function ignoreItem(row: UnmatchedRow) {
  try {
    // TODO: await api.updateUnmatchedItemStatus(row.id, 'ignored')
    ElMessage.success('已忽略')
    loadData()
  } catch {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadVendorList()
  loadData()
})
</script>

<style scoped>
.unmatched-item {
  padding: 16px;
}
.filter-bar {
  margin-bottom: 8px;
}
.expand-content {
  padding: 16px 24px;
}
</style>
