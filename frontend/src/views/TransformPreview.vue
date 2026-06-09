<template>
  <div class="transform-preview">
    <el-card shadow="never">
      <template #header>
        <span>转换预览</span>
      </template>

      <div class="preview-layout">
        <!-- 左侧输入区 -->
        <div class="preview-left">
          <el-form label-width="80px">
            <el-form-item label="厂商">
              <el-select v-model="selectedVendor" placeholder="请选择厂商" style="width: 100%">
                <el-option
                  v-for="v in vendorList"
                  :key="v.code"
                  :label="v.name"
                  :value="v.code"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="原始数据">
              <el-input
                v-model="rawData"
                type="textarea"
                :rows="18"
                placeholder="粘贴原始报文JSON数据"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doTransform" :loading="loading">
                转换预览
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧结果区 -->
        <div class="preview-right">
          <template v-if="showResult">
            <!-- 汇总信息 -->
            <div class="summary-bar">
              <el-row :gutter="16">
                <el-col :span="6">
                  <el-statistic title="总数" :value="summary.total" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="成功">
                    <template #default>
                      <span style="color: #67c23a">{{ summary.success }}</span>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="6">
                  <el-statistic title="失败">
                    <template #default>
                      <span style="color: #f56c6c">{{ summary.fail }}</span>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="6">
                  <el-statistic title="未识别">
                    <template #default>
                      <span style="color: #e6a23c">{{ summary.unmatched }}</span>
                    </template>
                  </el-statistic>
                </el-col>
              </el-row>
            </div>

            <el-divider />

            <!-- 结果 Tabs -->
            <el-tabs v-model="activeTab">
              <el-tab-pane label="标准数据" name="standard">
                <el-collapse v-if="standardRecords.length">
                  <el-collapse-item
                    v-for="(record, idx) in standardRecords"
                    :key="idx"
                    :title="`记录 ${idx + 1} — 患者: ${record.patientId} | 就诊: ${record.visitNo} | 时间: ${record.recordTime}`"
                    :name="idx"
                  >
                    <el-table :data="record.items" border size="small">
                      <el-table-column prop="code" label="编码" width="120" />
                      <el-table-column prop="name" label="名称" width="140" />
                      <el-table-column prop="value" label="值" min-width="120" />
                      <el-table-column prop="unit" label="单位" width="80" />
                    </el-table>
                  </el-collapse-item>
                </el-collapse>
                <el-empty v-else description="暂无标准数据" />
              </el-tab-pane>

              <el-tab-pane label="未识别指标" name="unmatched">
                <el-table v-if="unmatchedItems.length" :data="unmatchedItems" border size="small">
                  <el-table-column
                    v-for="col in unmatchedColumns"
                    :key="col.prop"
                    :prop="col.prop"
                    :label="col.label"
                    :width="col.width"
                    show-overflow-tooltip
                  />
                </el-table>
                <el-empty v-else description="暂无未识别指标" />
              </el-tab-pane>
            </el-tabs>
          </template>
          <el-empty v-else description="请在左侧输入数据并点击转换预览" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

interface VendorOption {
  code: string
  name: string
}

interface StandardItem {
  code: string
  name: string
  value: string
  unit: string
}

interface StandardRecord {
  patientId: string
  visitNo: string
  recordTime: string
  items: StandardItem[]
}

interface TransformResult {
  summary: {
    total: number
    success: number
    fail: number
    unmatched: number
  }
  standardRecords: StandardRecord[]
  unmatchedItems: Record<string, any>[]
}

const loading = ref(false)
const selectedVendor = ref('')
const rawData = ref('')
const vendorList = ref<VendorOption[]>([])

const transformResult = ref<TransformResult | null>(null)
const activeTab = ref('standard')

const showResult = computed(() => transformResult.value !== null)

const summary = computed(() => transformResult.value?.summary || { total: 0, success: 0, fail: 0, unmatched: 0 })
const standardRecords = computed(() => transformResult.value?.standardRecords || [])
const unmatchedItems = computed(() => transformResult.value?.unmatchedItems || [])

const unmatchedColumns = computed(() => {
  if (!unmatchedItems.value.length) return []
  const keys = Object.keys(unmatchedItems.value[0])
  return keys.map((key) => ({
    prop: key,
    label: key,
    width: key.length > 10 ? 180 : 120
  }))
})

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

async function doTransform() {
  if (!selectedVendor.value) {
    ElMessage.warning('请选择厂商')
    return
  }
  if (!rawData.value.trim()) {
    ElMessage.warning('请输入原始数据')
    return
  }
  let parsedData: any
  try {
    parsedData = JSON.parse(rawData.value)
  } catch {
    ElMessage.error('JSON格式错误')
    return
  }
  loading.value = true
  try {
    // TODO: Replace with actual API call
    // const res = await api.transformPreview(selectedVendor.value, parsedData)
    transformResult.value = {
      summary: { total: 0, success: 0, fail: 0, unmatched: 0 },
      standardRecords: [],
      unmatchedItems: []
    }
  } catch {
    ElMessage.error('转换预览失败')
    transformResult.value = null
  } finally {
    loading.value = false
  }
}

function clearAll() {
  rawData.value = ''
  transformResult.value = null
  activeTab.value = 'standard'
}

onMounted(() => {
  loadVendorList()
})
</script>

<style scoped>
.transform-preview {
  padding: 16px;
}
.preview-layout {
  display: flex;
  gap: 20px;
}
.preview-left {
  width: 420px;
  flex-shrink: 0;
}
.preview-right {
  flex: 1;
  min-width: 0;
}
.summary-bar {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}
</style>
