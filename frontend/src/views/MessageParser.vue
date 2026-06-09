<template>
  <div class="message-parser-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- 主体区域 -->
    <el-row :gutter="16" class="main-content">
      <!-- 左侧：报文输入 -->
      <el-col :span="12">
        <el-card shadow="never" class="input-card">
          <template #header>
            <div class="card-header">
              <span>样例报文</span>
              <div class="header-actions">
                <el-button size="small" @click="formatInput">格式化</el-button>
                <el-button size="small" @click="clearInput">清空</el-button>
              </div>
            </div>
          </template>
          <el-input v-model="inputData" type="textarea" :rows="22" placeholder="请粘贴JSON或XML样例报文..." class="input-textarea" />
        </el-card>
      </el-col>

      <!-- 右侧：JSON树形查看器 -->
      <el-col :span="12">
        <el-card shadow="never" class="tree-card">
          <template #header>
            <div class="card-header">
              <span>报文结构</span>
              <el-tag size="small" v-if="dataType">{{ dataType }}</el-tag>
            </div>
          </template>
          <div class="tree-viewer" v-if="parsedData">
            <JsonTreeNode :data="parsedData" :key-name="''" :depth="0" />
          </div>
          <el-empty v-else description="请输入报文数据" :image-size="80" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部：JsonPath/XPath测试 -->
    <el-card shadow="never" class="path-test-card">
      <template #header>
        <span>路径测试</span>
      </template>
      <el-row :gutter="16" align="middle">
        <el-col :span="16">
          <el-input v-model="pathExpression" placeholder="请输入JsonPath或XPath表达式，如: $.data.records[*].temperature">
            <template #prepend>
              <el-select v-model="pathType" style="width: 120px">
                <el-option label="JsonPath" value="jsonpath" />
                <el-option label="XPath" value="xpath" />
              </el-select>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="testPath" :loading="testing">测试</el-button>
        </el-col>
        <el-col :span="4">
          <span class="match-count" v-if="matchCount !== null">
            匹配结果：<el-tag :type="matchCount > 0 ? 'success' : 'danger'">{{ matchCount }} 条</el-tag>
          </span>
        </el-col>
      </el-row>

      <!-- 匹配结果 -->
      <div class="match-results" v-if="matchResults.length > 0">
        <el-divider content-position="left">匹配结果</el-divider>
        <el-table :data="matchResults" stripe size="small" max-height="300">
          <el-table-column type="index" label="序号" width="70" />
          <el-table-column prop="path" label="路径" min-width="250" show-overflow-tooltip />
          <el-table-column prop="value" label="值" min-width="350" show-overflow-tooltip />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// --- 递归JSON树节点组件 ---
const JsonTreeNode = {
  name: 'JsonTreeNode',
  props: {
    data: { type: [Object, Array, String, Number, Boolean, null], default: null },
    keyName: { type: String, default: '' },
    depth: { type: Number, default: 0 }
  },
  setup(props: { data: any; keyName: string; depth: number }) {
    const expanded = ref(props.depth < 3)

    const isObject = computed(() => props.data !== null && typeof props.data === 'object' && !Array.isArray(props.data))
    const isArray = computed(() => Array.isArray(props.data))
    const isExpandable = computed(() => isObject.value || isArray.value)

    const toggleExpand = () => {
      if (isExpandable.value) {
        expanded.value = !expanded.value
      }
    }

    const getValueType = (val: any) => {
      if (val === null || val === undefined) return 'null'
      if (typeof val === 'string') return 'string'
      if (typeof val === 'number') return 'number'
      if (typeof val === 'boolean') return 'boolean'
      if (Array.isArray(val)) return 'array'
      return 'object'
    }

    return () => {
      const indent = props.depth * 20

      if (isExpandable.value) {
        const entries = isArray.value
          ? props.data.map((item: any, idx: number) => [idx, item])
          : Object.entries(props.data)
        const bracket = isArray.value ? ['[', ']'] : ['{', '}']
        const summary = isArray.value
          ? `Array(${props.data.length})`
          : `${Object.keys(props.data).length} properties`

        return h('div', { class: 'json-node' }, [
          h('div', {
            class: 'json-line expandable',
            style: { paddingLeft: `${indent}px` },
            onClick: toggleExpand
          }, [
            h('span', { class: 'json-arrow' }, expanded.value ? '▼' : '▶'),
            props.keyName !== '' ? h('span', { class: 'json-key' }, `"${props.keyName}"`) : null,
            props.keyName !== '' ? h('span', { class: 'json-colon' }, ': ') : null,
            h('span', { class: 'json-bracket' }, bracket[0]),
            !expanded.value ? h('span', { class: 'json-summary' }, ` ${summary} `) : null,
            !expanded.value ? h('span', { class: 'json-bracket' }, bracket[1]) : null,
          ]),
          expanded.value ? h('div', { class: 'json-children' },
            entries.map(([key, value]: [any, any]) =>
              h(JsonTreeNode, { data: value, keyName: String(key), depth: props.depth + 1, key })
            )
          ) : null,
          expanded.value ? h('div', {
            class: 'json-line',
            style: { paddingLeft: `${indent}px` }
          }, [
            h('span', { class: 'json-bracket' }, bracket[1])
          ]) : null
        ])
      } else {
        const valueType = getValueType(props.data)
        const displayValue = props.data === null ? 'null'
          : typeof props.data === 'string' ? `"${props.data}"`
          : String(props.data)

        return h('div', {
          class: 'json-line leaf',
          style: { paddingLeft: `${indent}px` }
        }, [
          props.keyName !== '' ? h('span', { class: 'json-key' }, `"${props.keyName}"`) : null,
          props.keyName !== '' ? h('span', { class: 'json-colon' }, ': ') : null,
          h('span', { class: `json-value json-value-${valueType}` }, displayValue)
        ])
      }
    }
  }
}

// --- 主逻辑 ---

// 厂家接口
interface Vendor {
  vendorCode: string
  vendorName: string
}

// 匹配结果接口
interface MatchResult {
  path: string
  value: string
}

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const inputData = ref('')
const loading = ref(false)
const pathType = ref('jsonpath')
const pathExpression = ref('')
const testing = ref(false)
const matchCount = ref<number | null>(null)
const matchResults = ref<MatchResult[]>([])

// 检测数据类型
const dataType = computed(() => {
  if (!inputData.value.trim()) return ''
  const trimmed = inputData.value.trim()
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      JSON.parse(trimmed)
      return 'JSON'
    } catch {
      // not valid JSON
    }
  }
  if (trimmed.startsWith('<')) {
    return 'XML'
  }
  return ''
})

// 解析数据
const parsedData = computed(() => {
  if (!inputData.value.trim()) return null
  const trimmed = inputData.value.trim()
  try {
    return JSON.parse(trimmed)
  } catch {
    return null
  }
})

// 格式化输入
const formatInput = () => {
  if (!inputData.value.trim()) return
  try {
    const parsed = JSON.parse(inputData.value)
    inputData.value = JSON.stringify(parsed, null, 2)
    ElMessage.success('格式化成功')
  } catch {
    ElMessage.warning('输入内容不是有效的JSON，无法格式化')
  }
}

// 清空输入
const clearInput = () => {
  inputData.value = ''
  matchResults.value = []
  matchCount.value = null
  pathExpression.value = ''
}

// 简单的JsonPath求值（支持基础语法）
const evaluateJsonPath = (data: any, path: string): any[] => {
  const results: any[] = []

  // 去掉开头的 $
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

    // 处理数组通配符 data[*]
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

    // 处理通配符
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

// 测试路径
const testPath = () => {
  if (!inputData.value.trim()) {
    ElMessage.warning('请先输入样例报文')
    return
  }
  if (!pathExpression.value.trim()) {
    ElMessage.warning('请输入路径表达式')
    return
  }

  testing.value = true
  matchResults.value = []
  matchCount.value = null

  try {
    const parsed = JSON.parse(inputData.value)

    if (pathType.value === 'jsonpath') {
      const values = evaluateJsonPath(parsed, pathExpression.value)
      matchCount.value = values.length
      matchResults.value = values.map((val, idx) => ({
        path: `${pathExpression.value}[${idx}]`,
        value: typeof val === 'object' ? JSON.stringify(val) : String(val)
      }))
    } else {
      // XPath暂不支持，给出提示
      ElMessage.info('XPath解析暂不支持JSON数据，请使用JsonPath')
      matchCount.value = 0
    }
  } catch {
    ElMessage.error('报文解析失败，请检查格式是否正确')
    matchCount.value = 0
  } finally {
    testing.value = false
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
.message-parser-container {
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

.main-content {
  margin-bottom: 16px;
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

.input-card {
  height: 100%;

  .input-textarea {
    :deep(textarea) {
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 13px;
      line-height: 1.5;
    }
  }
}

.tree-card {
  height: 100%;

  .tree-viewer {
    max-height: 500px;
    overflow-y: auto;
    padding: 8px 0;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
    line-height: 1.8;
  }
}

.path-test-card {
  .match-count {
    font-size: 14px;
    color: #606266;
    white-space: nowrap;
  }

  .match-results {
    margin-top: 16px;
  }
}

:deep(.json-node) {
  .json-line {
    white-space: nowrap;

    &.expandable {
      cursor: pointer;

      &:hover {
        background-color: #f5f7fa;
      }
    }
  }

  .json-arrow {
    display: inline-block;
    width: 16px;
    font-size: 10px;
    color: #909399;
    user-select: none;
  }

  .json-key {
    color: #881391;
  }

  .json-colon {
    color: #333;
  }

  .json-bracket {
    color: #333;
  }

  .json-summary {
    color: #909399;
    font-style: italic;
    font-size: 12px;
  }

  .json-value {
    &.json-value-string {
      color: #1a7f37;
    }

    &.json-value-number {
      color: #0550ae;
    }

    &.json-value-boolean {
      color: #cf222e;
    }

    &.json-value-null {
      color: #909399;
      font-style: italic;
    }
  }

  .json-children {
    border-left: 1px dashed #dcdfe6;
    margin-left: 8px;
  }
}
</style>
