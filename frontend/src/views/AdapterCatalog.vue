<template>
  <div class="adapter-catalog">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h2>适配器目录</h2>
        <span class="subtitle">选择一个内置模板，一键创建厂家配置</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索模板..."
          prefix-icon="Search"
          clearable
          style="width: 240px"
        />
      </div>
    </div>

    <!-- 标签筛选 -->
    <div class="tag-filter">
      <el-tag
        v-for="tag in allTags"
        :key="tag"
        :type="selectedTags.includes(tag) ? '' : 'info'"
        :effect="selectedTags.includes(tag) ? 'dark' : 'plain'"
        class="filter-tag"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </el-tag>
      <el-tag
        v-if="selectedTags.length > 0"
        type="warning"
        effect="plain"
        class="filter-tag"
        @click="selectedTags = []"
      >
        清除筛选
      </el-tag>
    </div>

    <!-- 模板卡片网格 -->
    <div class="card-grid" v-loading="loading">
      <div
        v-for="profile in filteredProfiles"
        :key="profile.profileCode"
        class="profile-card"
        :class="{ 'is-builtin': profile.isBuiltin }"
        @click="handleSelectProfile(profile)"
      >
        <div class="card-header">
          <div class="card-icon">
            <el-icon :size="32">
              <component :is="getIcon(profile)" />
            </el-icon>
          </div>
          <div class="card-builtin-badge" v-if="profile.isBuiltin">
            <el-tag size="small" type="success" effect="dark">内置</el-tag>
          </div>
          <div class="card-builtin-badge" v-else>
            <el-tag size="small" type="info" effect="plain">自定义</el-tag>
          </div>
        </div>

        <div class="card-body">
          <h3 class="card-title">{{ profile.profileName }}</h3>
          <p class="card-desc">{{ profile.description || '暂无描述' }}</p>
          <div class="card-tags">
            <el-tag
              v-for="tag in (profile.tags || []).slice(0, 4)"
              :key="tag"
              size="small"
              type="info"
              effect="plain"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="card-footer">
          <span class="access-type">{{ getAccessTypeLabel(profile.accessType) }}</span>
          <span class="rule-count">{{ (profile.itemRulesTemplate || []).length }} 条规则</span>
        </div>
      </div>
    </div>

    <!-- 应用模板弹窗 -->
    <el-dialog
      v-model="applyDialogVisible"
      title="应用适配器模板"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="applyFormRef" :model="applyForm" :rules="applyRules" label-width="100px">
        <el-form-item label="选择的模板">
          <el-tag type="primary" effect="dark">{{ selectedProfile?.profileName }}</el-tag>
        </el-form-item>
        <el-form-item label="厂家编码" prop="vendorCode">
          <el-input v-model="applyForm.vendorCode" placeholder="如: zhonglian_001" />
          <div class="form-tip">唯一标识，用于数据路由</div>
        </el-form-item>
        <el-form-item label="厂家名称" prop="vendorName">
          <el-input v-model="applyForm.vendorName" placeholder="如: 中联HIS-北京协和" />
        </el-form-item>
        <el-form-item label="医院编码">
          <el-input v-model="applyForm.hospitalCode" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleApply" :loading="applying">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 保存为模板弹窗 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="从厂家保存为适配器模板"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="saveFormRef" :model="saveForm" :rules="saveRules" label-width="100px">
        <el-form-item label="选择厂家" prop="vendorCode">
          <el-select v-model="saveForm.vendorCode" placeholder="请选择厂家" style="width: 100%">
            <el-option
              v-for="v in vendorList"
              :key="v.vendorCode"
              :label="v.vendorName"
              :value="v.vendorCode"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模板编码" prop="profileCode">
          <el-input v-model="saveForm.profileCode" placeholder="如: my_custom_his" />
        </el-form-item>
        <el-form-item label="模板名称" prop="profileName">
          <el-input v-model="saveForm.profileName" placeholder="如: 我的HIS系统" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="saveForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="saveForm.tagsStr" placeholder="用逗号分隔，如: JSON,自定义" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveFromVendor" :loading="saving">保存模板</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Connection,
  Document,
  SetUp,
  Setting,
  Promotion,
  Timer,
  OfficeBuilding,
  Box,
} from '@element-plus/icons-vue'
import { getAdapterProfiles, applyAdapterProfile, saveFromVendor } from '@/api/adapterProfile'
import { getVendors } from '@/api/vendor'

interface AdapterProfile {
  profileCode: string
  profileName: string
  description: string
  tags: string[]
  accessType: string
  isBuiltin: boolean
  itemRulesTemplate: any[]
}

const loading = ref(false)
const profiles = ref<AdapterProfile[]>([])
const searchText = ref('')
const selectedTags = ref<string[]>([])

// Apply dialog
const applyDialogVisible = ref(false)
const applying = ref(false)
const selectedProfile = ref<AdapterProfile | null>(null)
const applyFormRef = ref<FormInstance>()
const applyForm = ref({ vendorCode: '', vendorName: '', hospitalCode: '' })
const applyRules: FormRules = {
  vendorCode: [{ required: true, message: '请输入厂家编码', trigger: 'blur' }],
  vendorName: [{ required: true, message: '请输入厂家名称', trigger: 'blur' }],
}

// Save dialog
const saveDialogVisible = ref(false)
const saving = ref(false)
const saveFormRef = ref<FormInstance>()
const vendorList = ref<any[]>([])
const saveForm = ref({ vendorCode: '', profileCode: '', profileName: '', description: '', tagsStr: '' })
const saveRules: FormRules = {
  vendorCode: [{ required: true, message: '请选择厂家', trigger: 'change' }],
  profileCode: [{ required: true, message: '请输入模板编码', trigger: 'blur' }],
  profileName: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
}

const accessTypeLabels: Record<string, string> = {
  http_push: 'HTTP Push',
  http_pull: 'HTTP Pull',
  soap_push: 'SOAP Push',
  db_view: '数据库视图',
}

const allTags = computed(() => {
  const tagSet = new Set<string>()
  profiles.value.forEach(p => (p.tags || []).forEach(t => tagSet.add(t)))
  return Array.from(tagSet).sort()
})

const filteredProfiles = computed(() => {
  let result = profiles.value
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    result = result.filter(p =>
      p.profileName.toLowerCase().includes(q) ||
      (p.description || '').toLowerCase().includes(q) ||
      (p.tags || []).some(t => t.toLowerCase().includes(q))
    )
  }
  if (selectedTags.value.length > 0) {
    result = result.filter(p =>
      selectedTags.value.some(t => (p.tags || []).includes(t))
    )
  }
  return result
})

function getIcon(profile: AdapterProfile) {
  if (profile.accessType === 'soap_push') return Connection
  if (profile.accessType === 'http_pull') return Timer
  if (profile.accessType === 'db_view') return Document
  return Box
}

function getAccessTypeLabel(type: string) {
  return accessTypeLabels[type] || type
}

function toggleTag(tag: string) {
  const idx = selectedTags.value.indexOf(tag)
  if (idx >= 0) selectedTags.value.splice(idx, 1)
  else selectedTags.value.push(tag)
}

async function fetchProfiles() {
  loading.value = true
  try {
    const res = await getAdapterProfiles()
    profiles.value = res.data?.data || res.data || []
  } catch {
    ElMessage.error('获取适配器模板失败')
  } finally {
    loading.value = false
  }
}

function handleSelectProfile(profile: AdapterProfile) {
  selectedProfile.value = profile
  applyForm.value = { vendorCode: '', vendorName: '', hospitalCode: '' }
  applyDialogVisible.value = true
}

async function handleApply() {
  if (!applyFormRef.value) return
  await applyFormRef.value.validate(async (valid) => {
    if (!valid) return
    applying.value = true
    try {
      const res = await applyAdapterProfile({
        profileCode: selectedProfile.value!.profileCode,
        ...applyForm.value,
      })
      ElMessage.success(res.data?.data?.summary || '创建成功')
      applyDialogVisible.value = false
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.message || '创建失败')
    } finally {
      applying.value = false
    }
  })
}

async function fetchVendorList() {
  try {
    const res = await getVendors()
    vendorList.value = res.data?.data || res.data || []
  } catch {
    vendorList.value = []
  }
}

function openSaveDialog() {
  saveForm.value = { vendorCode: '', profileCode: '', profileName: '', description: '', tagsStr: '' }
  fetchVendorList()
  saveDialogVisible.value = true
}

async function handleSaveFromVendor() {
  if (!saveFormRef.value) return
  await saveFormRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const tags = saveForm.value.tagsStr
        ? saveForm.value.tagsStr.split(',').map(t => t.trim()).filter(Boolean)
        : []
      await saveFromVendor({
        vendorCode: saveForm.value.vendorCode,
        profileCode: saveForm.value.profileCode,
        profileName: saveForm.value.profileName,
        description: saveForm.value.description,
        tags,
      })
      ElMessage.success('保存模板成功')
      saveDialogVisible.value = false
      fetchProfiles()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.message || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

// Expose openSaveDialog for parent use
defineExpose({ openSaveDialog })

onMounted(() => {
  fetchProfiles()
})
</script>

<style scoped lang="scss">
.adapter-catalog {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  .header-left {
    h2 {
      font-size: 20px;
      color: #303133;
      margin: 0;
    }
    .subtitle {
      font-size: 13px;
      color: #909399;
      margin-top: 4px;
      display: block;
    }
  }
}

.tag-filter {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .filter-tag {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      opacity: 0.8;
    }
  }
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.profile-card {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;

  &:hover {
    border-color: #409eff;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
    transform: translateY(-2px);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;

    .card-icon {
      width: 48px;
      height: 48px;
      border-radius: 8px;
      background: #ecf5ff;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #409eff;
    }
  }

  .card-body {
    flex: 1;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .card-desc {
      font-size: 13px;
      color: #909399;
      line-height: 1.5;
      margin: 0 0 12px 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .card-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;

      .tag-item {
        font-size: 11px;
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;
    font-size: 12px;
    color: #909399;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
