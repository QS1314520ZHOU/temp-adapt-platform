<template>
  <div class="json-field-picker">
    <div class="picker-header">
      <el-input v-model="jsonInput" type="textarea" :rows="6" placeholder="粘贴 JSON 数据" />
      <el-button type="primary" @click="parseJson" :loading="parsing">解析</el-button>
    </div>

    <div v-if="treeData.length" class="picker-body">
      <div class="tree-panel">
        <div class="panel-title">数据结构 (点击选择字段)</div>
        <el-tree
          :data="treeData"
          :props="{ children: 'children', label: 'label' }"
          default-expand-all
          highlight-current
          @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <span class="node-key">{{ data.key }}</span>
              <span class="node-type">{{ data.type }}</span>
              <span v-if="data.value !== undefined" class="node-value">: {{ data.displayValue }}</span>
              <el-tag v-if="data.selected" size="small" type="success" closable @close="unselect(data)">
                已选
              </el-tag>
            </div>
          </template>
        </el-tree>
      </div>

      <div class="selected-panel">
        <div class="panel-title">已选字段</div>

        <div v-if="recordPath" class="path-info">
          <el-tag type="warning">记录路径: {{ recordPath }}</el-tag>
        </div>
        <div v-if="itemPath" class="path-info">
          <el-tag type="info">指标路径: {{ itemPath }}</el-tag>
        </div>

        <el-table :data="selectedFields" size="small" border>
          <el-table-column prop="jsonPath" label="JSON 路径" />
          <el-table-column label="目标字段" width="180">
            <template #default="{ row }">
              <el-input v-model="row.targetField" size="small" placeholder="如: patientId" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button type="danger" size="small" text @click="unselectField(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="selectedFields.length" class="actions">
          <el-button type="primary" @click="generateConfig">生成配置</el-button>
          <el-button @click="clearAll">清空</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

interface FieldNode {
  key: string
  path: string
  jsonPath: string
  type: string
  value: any
  displayValue: string
  selected: boolean
  children: FieldNode[]
  parent?: FieldNode
  isArrayItem?: boolean
}

interface SelectedField {
  jsonPath: string
  targetField: string
  nodeRef: FieldNode
}

const emit = defineEmits(['update:config'])

const jsonInput = ref('')
const parsing = ref(false)
const treeData = ref<FieldNode[]>([])
const selectedFields = ref<SelectedField[]>([])
const recordPath = ref('')
const itemPath = ref('')

function parseJson() {
  try {
    const data = JSON.parse(jsonInput.value)
    treeData.value = buildTree(data, '$', '$')
    selectedFields.value = []
    recordPath.value = ''
    itemPath.value = ''
    ElMessage.success('解析成功')
  } catch (e: any) {
    ElMessage.error('JSON 格式错误: ' + e.message)
  }
}

function buildTree(obj: any, path: string, jsonPath: string): FieldNode[] {
  if (obj === null || obj === undefined) {
    return []
  }

  if (Array.isArray(obj)) {
    return [{
      key: path.split('.').pop() || '[]',
      path,
      jsonPath: jsonPath + '[*]',
      type: `数组(${obj.length})`,
      value: obj,
      displayValue: `[${obj.length}项]`,
      selected: false,
      isArrayItem: true,
      children: obj.length > 0 ? buildTree(obj[0], path + '[0]', jsonPath + '[0]') : [],
    }]
  }

  if (typeof obj === 'object') {
    return Object.entries(obj).map(([key, val]) => {
      const newPath = path ? `${path}.${key}` : key
      const newJsonPath = `${jsonPath}.${key}`
      const node: FieldNode = {
        key,
        path: newPath,
        jsonPath: newJsonPath,
        type: getType(val),
        value: val,
        displayValue: getDisplayValue(val),
        selected: false,
        children: [],
      }
      node.children = buildTree(val, newPath, newJsonPath)
      return node
    })
  }

  return []
}

function getType(val: any): string {
  if (val === null) return 'null'
  if (Array.isArray(val)) return `数组(${val.length})`
  if (typeof val === 'object') return '对象'
  if (typeof val === 'string') return '字符串'
  if (typeof val === 'number') return '数字'
  if (typeof val === 'boolean') return '布尔'
  return typeof val
}

function getDisplayValue(val: any): string {
  if (val === null || val === undefined) return 'null'
  if (typeof val === 'string') return `"${val.length > 30 ? val.slice(0, 30) + '...' : val}"`
  if (typeof val === 'number' || typeof val === 'boolean') return String(val)
  if (Array.isArray(val)) return `[${val.length}项]`
  return '{...}'
}

function handleNodeClick(data: FieldNode) {
  // 如果是数组项，设置为记录路径或指标路径
  if (data.isArrayItem) {
    if (!recordPath.value) {
      recordPath.value = data.jsonPath
      data.selected = true
      ElMessage.success(`已设为记录路径: ${data.jsonPath}`)
    } else if (!itemPath.value && data.jsonPath.includes(recordPath.value.replace('[*]', ''))) {
      itemPath.value = data.jsonPath.replace(recordPath.value, '').replace(/^\./, '') || data.jsonPath
      data.selected = true
      ElMessage.success(`已设为指标路径: ${itemPath.value}`)
    }
    return
  }

  // 叶子节点或简单值，添加到选中字段
  if (data.type === '字符串' || data.type === '数字' || data.type === '布尔') {
    if (selectedFields.value.some(f => f.jsonPath === data.jsonPath)) {
      ElMessage.warning('该字段已选中')
      return
    }
    data.selected = true
    selectedFields.value.push({
      jsonPath: data.jsonPath,
      targetField: guessFieldName(data.key),
      nodeRef: data,
    })
    ElMessage.success(`已选中: ${data.jsonPath}`)
  }
}

function unselect(data: FieldNode) {
  data.selected = false
  selectedFields.value = selectedFields.value.filter(f => f.jsonPath !== data.jsonPath)
}

function unselectField(field: SelectedField) {
  field.nodeRef.selected = false
  selectedFields.value = selectedFields.value.filter(f => f !== field)
}

function clearAll() {
  selectedFields.value.forEach(f => f.nodeRef.selected = false)
  selectedFields.value = []
  recordPath.value = ''
  itemPath.value = ''
}

function guessFieldName(key: string): string {
  const map: Record<string, string> = {
    pid: 'patientId',
    patient_id: 'patientId',
    data_time: 'measureTime',
    measure_time: 'measureTime',
    inpno: 'admissionNo',
    admission_no: 'admissionNo',
    ward_id: 'wardCode',
    ward_code: 'wardCode',
    item_name: 'itemName',
    item_data: 'itemValue',
    name: 'name',
    value: 'value',
    code: 'code',
    type: 'type',
    time: 'time',
    date: 'date',
  }
  return map[key] || key
}

function generateConfig() {
  if (!recordPath.value) {
    ElMessage.warning('请先点击一个数组设为记录路径')
    return
  }

  const config = {
    recordPath: recordPath.value,
    itemPath: itemPath.value || undefined,
    fieldMappings: selectedFields.value.map(f => ({
      targetField: f.targetField,
      sourcePath: f.jsonPath,
    })),
  }

  emit('update:config', config)
  ElMessage.success('配置已生成')
}
</script>

<style scoped>
.json-field-picker {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
}

.picker-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.picker-header .el-button {
  align-self: flex-end;
}

.picker-body {
  display: flex;
  gap: 16px;
}

.tree-panel {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.selected-panel {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
}

.panel-title {
  font-weight: bold;
  margin-bottom: 12px;
  color: #303133;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.node-key {
  color: #409eff;
  font-weight: 500;
}

.node-type {
  color: #909399;
  font-size: 11px;
}

.node-value {
  color: #67c23a;
  font-size: 12px;
}

.path-info {
  margin-bottom: 8px;
}

.actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}
</style>
