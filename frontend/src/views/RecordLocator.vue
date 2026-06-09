<template>
  <div class="record-locator-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- 配置区域 -->
    <el-card shadow="never" class="config-card">
      <template #header>
        <span>主记录定位配置</span>
      </template>
      <el-form label-width="140px" style="max-width: 800px">
        <el-form-item label="记录路径类型">
          <el-radio-group v-model="pathType">
            <el-radio value="jsonpath">JsonPath</el-radio>
            <el-radio value="xpath">XPath</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="记录路径(recordPath)">
          <el-input v-model="recordPath" placeholder="如: $.data.records[*] 或 //record" />
          <div class="form-tip">用于从报文中提取主记录数组的表达式</div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 样例数据输入 -->
    <el-card shadow="never" class="sample-card">
      <template #header>
        <div class="card-header">
          <span>样例数据</span>
          <div class="header-actions">
            <el-button size="small" @click="formatInput">格式化</el-button>
            <el-button size="small" @click="clearInput">清空</el-button>
          </div>
        </div>
      </template>
      <el-input v-model="sampleData" type="textarea" :rows="14" placeholder="请粘贴JSON样例数据..." class="sample-textarea" />
    </el-card>

    <!-- 预览区域 -->
    <el-card shadow="never" class="preview-card">
      <template #header>
        <div class="card-header">
          <span>预览结果</span>
          <el-button type="primary" @click="handlePreview" :loading="previewing">
            <el-icon><View /></el-icon>
            预览
          </el-button>
        </div>
      </template>

      <!-- 提取统计 -->
      <div class="preview-stats" v-if="previewStats.total !== null">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="提取记录数">
            <el-tag :type="previewStats.total > 0 ? 'success' : 'danger'" size="large">
              {{ previewStats.total }} 条
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="记录路径">
            <code>{{ recordPath }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="数据格式">
            <el-tag>{{ previewStats.dataType }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 提取记录表格 -->
      <div class="preview-table" v-if="previewRecords.length > 0">
        <el-divider content-position="left">提取的记录（前10条）</el-divider>
        <el-table :data="previewRecords" stripe border size="small" max-height="400">
          <el-table-column type="index" label="序号" width="70" />
          <el-table-column v-for="col in previewColumns" :key="col" :prop="col" :label="col" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              {{ formatCellValue(row[col]) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 原始提取数据 -->
      <div class="raw-data" v-if="rawExtractedData.length > 0">
        <el-divider content-position="left">原始提取数据</el-divider>
        <el-collapse>
          <el-collapse-item title="查看原始JSON数据" name="raw">
            <pre class="raw-json">{{ JSON.stringify(rawExtractedData.slice(0, 5), null, 2) }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="previewStats.total === null && !previewing" description="请配置记录路径并点击预览" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// 厂家接口
interface Vendor {
  vendorCode: string
  vendorName: string
}

// 预览统计
interface PreviewStats {
  total: number | null
  dataType: string
}

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const loading = ref(false)
const pathType = ref('jsonpath')
const recordPath = ref('')
const sampleData = ref('')
const previewing = ref(false)

// 预览统计
const previewStats = reactive<PreviewStats>({
  total: null,
  dataType: '-'
})

// 预览记录
const previewRecords = ref<any[]>([])
const previewColumns = ref<string[]>([])
const rawExtractedData = ref<any[]>([])

// 格式化单元格值
const formatCellValue = (val: any): string => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

// 格式化输入
const formatInput = () => {
  if (!sampleData.value.trim()) return
  try {
    const parsed = JSON.parse(sampleData.value)
    sampleData.value = JSON.stringify(parsed, null, 2)
    ElMessage.success('格式化成功')
  } catch {
    ElMessage.warning('输入内容不是有效的JSON，无法格式化')
  }
}

// 清空输入
const clearInput = () => {
  sampleData.value = ''
  previewStats.total = null
  previewStats.dataType = '-'
  previewRecords.value = []
  previewColumns.value = []
  rawExtractedData.value = []
}

// 简单的JsonPath求值
const evaluateJsonPath = (data: any, path: string): any[] => {
  const results: any[] = []
  const cleaned = path.replace(/^\$\.?/, '')
  if (!cleaned) {
    results.push(data)
    return results
  }

  const parts = cleaned.split('.')

  const traverse = (current: any, remainingParts: string[]) => {
    if (remainingParts.length === 0) {
      results.push(current)
      return
    }

    const part = remainingParts[0]
    const rest = remainingParts.slice(1)

    // 处理数组标记 data[*] 或 data[0]
    const arrayMatch = part.match(/^(\w+)\[(\*|\d+)\]$/)
    if (arrayMatch) {
      const key = arrayMatch[1]
      const index = arrayMatch[2]
      const arr = current?.[key]
      if (Array.isArray(arr)) {
        if (index === '*') {
          arr.forEach((item) => traverse(item, rest))
        } else {
          traverse(arr[parseInt(index)], rest)
        }
      }
      return
    }

    // 通配符 *
    if (part === '*') {
      if (Array.isArray(current)) {
        current.forEach((item) => traverse(item, rest))
      } else if (typeof current === 'object' && current !== null) {
        Object.values(current).forEach((val) => traverse(val, rest))
      }
      return
    }

    if (current && typeof current === 'object') {
      traverse(current[part], rest)
    }
  }

  traverse(data, parts)
  return results
}

// 预览
const handlePreview = async () => {
  if (!sampleData.value.trim()) {
    ElMessage.warning('请先输入样例数据')
    return
  }
  if (!recordPath.value.trim()) {
    ElMessage.warning('请输入记录路径(recordPath)')
    return
  }

  previewing.value = true
  previewRecords.value = []
  previewColumns.value = []
  rawExtractedData.value = []

  try {
    const parsed = JSON.parse(sampleData.value)
    const records = evaluateJsonPath(parsed, recordPath.value)

    previewStats.total = records.length
    previewStats.dataType = 'JSON'

    if (records.length > 0) {
      rawExtractedData.value = records

      // 提取列名
      const columnSet = new Set<string>()
      records.forEach((record) => {
        if (typeof record === 'object' && record !== null && !Array.isArray(record)) {
          Object.keys(record).forEach((key) => columnSet.add(key))
        }
      })
      previewColumns.value = Array.from(columnSet)

      // 取前10条展示
      previewRecords.value = records.slice(0, 10)

      ElMessage.success(`成功提取 ${records.length} 条记录`)
    } else {
      ElMessage.warning('未提取到任何记录，请检查路径表达式')
    }
  } catch {
    ElMessage.error('数据解析失败，请检查JSON格式')
    previewStats.total = 0
  } finally {
    previewing.value = false
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
.record-locator-container {
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
  margin-bottom: 16px;

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}

.sample-card {
  margin-bottom: 16px;

  .sample-textarea {
    :deep(textarea) {
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 13px;
      line-height: 1.5;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.preview-card {
  .preview-stats {
    margin-bottom: 16px;
  }

  .preview-table {
    margin-bottom: 16px;
  }

  .raw-data {
    .raw-json {
      background-color: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 12px;
      line-height: 1.5;
      max-height: 300px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}
</style>
