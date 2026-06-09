<template>
  <div class="runtime-log">
    <el-card shadow="never">
      <template #header>
        <span>运行日志</span>
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
            <el-option label="待处理" value="pending" />
            <el-option label="已转换" value="transformed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filter.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 日志 Tabs -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 原始报文 -->
        <el-tab-pane label="原始报文" name="raw">
          <el-table :data="rawList" border v-loading="rawLoading">
            <el-table-column prop="vendorCode" label="厂商编码" width="120" />
            <el-table-column prop="accessType" label="接入类型" width="110" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="180" />
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewRawContent(row)">查看</el-button>
                <el-popconfirm title="确定重试该报文？" @confirm="retryRaw(row)">
                  <template #reference>
                    <el-button link type="warning" size="small">重试</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="rawPagination.page"
            v-model:page-size="rawPagination.pageSize"
            :total="rawPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end"
            @size-change="loadRawList"
            @current-change="loadRawList"
          />
        </el-tab-pane>

        <!-- 转换日志 -->
        <el-tab-pane label="转换日志" name="transform">
          <el-table :data="transformList" border v-loading="transformLoading">
            <el-table-column prop="batchId" label="批次ID" width="160" show-overflow-tooltip />
            <el-table-column prop="vendorCode" label="厂商编码" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total" label="总数" width="80" align="center" />
            <el-table-column prop="success" label="成功" width="80" align="center">
              <template #default="{ row }">
                <span style="color: #67c23a">{{ row.success }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="fail" label="失败" width="80" align="center">
              <template #default="{ row }">
                <span style="color: #f56c6c">{{ row.fail }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="unmatched" label="未识别" width="80" align="center">
              <template #default="{ row }">
                <span style="color: #e6a23c">{{ row.unmatched }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时(ms)" width="100" align="center" />
            <el-table-column prop="createdAt" label="创建时间" width="180" />
          </el-table>
          <el-pagination
            v-model:current-page="transformPagination.page"
            v-model:page-size="transformPagination.pageSize"
            :total="transformPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end"
            @size-change="loadTransformList"
            @current-change="loadTransformList"
          />
        </el-tab-pane>

        <!-- 重试任务 -->
        <el-tab-pane label="重试任务" name="retry">
          <div style="margin-bottom: 12px">
            <el-button type="warning" size="small" @click="batchRetry">批量重试</el-button>
          </div>
          <el-table
            :data="retryList"
            border
            v-loading="retryLoading"
            @selection-change="handleRetrySelectionChange"
          >
            <el-table-column type="selection" width="50" />
            <el-table-column prop="rawRecordId" label="原始记录ID" width="160" show-overflow-tooltip />
            <el-table-column prop="vendorCode" label="厂商编码" width="120" />
            <el-table-column prop="retryCount" label="重试次数" width="90" align="center" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastError" label="最近错误" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-popconfirm title="确定重试？" @confirm="retrySingle(row)">
                  <template #reference>
                    <el-button link type="primary" size="small">重试</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="retryPagination.page"
            v-model:page-size="retryPagination.pageSize"
            :total="retryPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end"
            @size-change="loadRetryList"
            @current-change="loadRetryList"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 查看原始内容对话框 -->
    <el-dialog v-model="rawContentDialogVisible" title="原始报文内容" width="700px">
      <pre class="raw-content-pre">{{ formattedRawContent }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

interface VendorOption {
  code: string
  name: string
}

interface RawRecord {
  id: string
  vendorCode: string
  accessType: string
  status: string
  createdAt: string
  rawContent?: string
}

interface TransformRecord {
  batchId: string
  vendorCode: string
  status: string
  total: number
  success: number
  fail: number
  unmatched: number
  duration: number
  createdAt: string
}

interface RetryRecord {
  id: string
  rawRecordId: string
  vendorCode: string
  retryCount: number
  status: string
  lastError: string
}

const activeTab = ref('raw')
const vendorList = ref<VendorOption[]>([])
const loading = ref(false)

const filter = reactive({
  vendorCode: '',
  status: '',
  dateRange: null as string[] | null
})

// Raw tab
const rawLoading = ref(false)
const rawList = ref<RawRecord[]>([])
const rawPagination = reactive({ page: 1, pageSize: 20, total: 0 })

// Transform tab
const transformLoading = ref(false)
const transformList = ref<TransformRecord[]>([])
const transformPagination = reactive({ page: 1, pageSize: 20, total: 0 })

// Retry tab
const retryLoading = ref(false)
const retryList = ref<RetryRecord[]>([])
const retryPagination = reactive({ page: 1, pageSize: 20, total: 0 })
const retrySelectedRows = ref<RetryRecord[]>([])

// Raw content dialog
const rawContentDialogVisible = ref(false)
const currentRawContent = ref('')

const formattedRawContent = computed(() => {
  try {
    return JSON.stringify(JSON.parse(currentRawContent.value), null, 2)
  } catch {
    return currentRawContent.value
  }
})

function statusTagType(status: string): string {
  const map: Record<string, string> = {
    pending: 'info',
    transformed: 'success',
    failed: 'danger',
    success: 'success',
    retrying: 'warning'
  }
  return map[status] || 'info'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: '待处理',
    transformed: '已转换',
    failed: '失败',
    success: '成功',
    retrying: '重试中'
  }
  return map[status] || status
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

function loadData() {
  if (activeTab.value === 'raw') loadRawList()
  else if (activeTab.value === 'transform') loadTransformList()
  else if (activeTab.value === 'retry') loadRetryList()
}

function handleTabChange() {
  loadData()
}

async function loadRawList() {
  rawLoading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.getRawLogs({ ...filter, page: rawPagination.page, pageSize: rawPagination.pageSize })
    rawList.value = []
    rawPagination.total = 0
  } catch {
    ElMessage.error('加载原始报文失败')
  } finally {
    rawLoading.value = false
  }
}

async function loadTransformList() {
  transformLoading.value = true
  try {
    // TODO: Replace with actual API call
    transformList.value = []
    transformPagination.total = 0
  } catch {
    ElMessage.error('加载转换日志失败')
  } finally {
    transformLoading.value = false
  }
}

async function loadRetryList() {
  retryLoading.value = true
  try {
    // TODO: Replace with actual API call
    retryList.value = []
    retryPagination.total = 0
  } catch {
    ElMessage.error('加载重试任务失败')
  } finally {
    retryLoading.value = false
  }
}

function viewRawContent(row: RawRecord) {
  currentRawContent.value = row.rawContent || '{}'
  rawContentDialogVisible.value = true
}

async function retryRaw(row: RawRecord) {
  try {
    // TODO: await api.retryRawRecord(row.id)
    ElMessage.success('重试已提交')
    loadRawList()
  } catch {
    ElMessage.error('重试失败')
  }
}

async function retrySingle(row: RetryRecord) {
  try {
    // TODO: await api.retryTask(row.id)
    ElMessage.success('重试已提交')
    loadRetryList()
  } catch {
    ElMessage.error('重试失败')
  }
}

function handleRetrySelectionChange(rows: RetryRecord[]) {
  retrySelectedRows.value = rows
}

async function batchRetry() {
  if (!retrySelectedRows.value.length) {
    ElMessage.warning('请先选择要重试的任务')
    return
  }
  try {
    // TODO: await api.batchRetry(retrySelectedRows.value.map(r => r.id))
    ElMessage.success(`已提交 ${retrySelectedRows.value.length} 个重试任务`)
    loadRetryList()
  } catch {
    ElMessage.error('批量重试失败')
  }
}

onMounted(() => {
  loadVendorList()
  loadRawList()
})
</script>

<style scoped>
.runtime-log {
  padding: 16px;
}
.filter-bar {
  margin-bottom: 8px;
}
.raw-content-pre {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 16px;
  max-height: 500px;
  overflow: auto;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
