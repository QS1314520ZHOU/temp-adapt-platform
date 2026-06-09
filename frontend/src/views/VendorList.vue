<template>
  <div class="vendor-list-container">
    <!-- 顶部操作栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="searchKeyword" placeholder="搜索厂家编码/名称" clearable style="width: 250px" @clear="handleSearch">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增厂家
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 厂家列表表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredVendorList" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="vendorCode" label="厂家编码" width="120" />
        <el-table-column prop="vendorName" label="厂家名称" min-width="150" />
        <el-table-column prop="hospitalName" label="所属医院" min-width="150" />
        <el-table-column prop="accessType" label="接入方式" width="120">
          <template #default="{ row }">
            <el-tag>{{ getAccessTypeLabel(row.accessType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="厂家编码" prop="vendorCode">
          <el-input v-model="formData.vendorCode" placeholder="请输入厂家编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="厂家名称" prop="vendorName">
          <el-input v-model="formData.vendorName" placeholder="请输入厂家名称" />
        </el-form-item>
        <el-form-item label="医院编码" prop="hospitalCode">
          <el-input v-model="formData.hospitalCode" placeholder="请输入医院编码" />
        </el-form-item>
        <el-form-item label="医院名称" prop="hospitalName">
          <el-input v-model="formData.hospitalName" placeholder="请输入医院名称" />
        </el-form-item>
        <el-form-item label="接入方式" prop="accessType">
          <el-select v-model="formData.accessType" placeholder="请选择接入方式" style="width: 100%">
            <el-option label="HTTP推送" value="http_push" />
            <el-option label="HTTP拉取" value="http_pull" />
            <el-option label="数据库视图" value="db_view" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="联系信息" prop="contactInfo">
          <el-input v-model="formData.contactInfo" placeholder="请输入联系信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import request from '@/api/request'

// 厂家数据接口
interface Vendor {
  id?: number
  vendorCode: string
  vendorName: string
  hospitalCode: string
  hospitalName: string
  accessType: string
  description: string
  contactInfo: string
  enabled: boolean
}

// 搜索关键词
const searchKeyword = ref('')
const loading = ref(false)

// 厂家列表
const vendorList = ref<Vendor[]>([])

// 过滤后的厂家列表
const filteredVendorList = computed(() => {
  if (!searchKeyword.value) {
    return vendorList.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return vendorList.value.filter(
    (vendor) =>
      vendor.vendorCode.toLowerCase().includes(keyword) ||
      vendor.vendorName.toLowerCase().includes(keyword)
  )
})

// 获取接入方式标签
const getAccessTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    http_push: 'HTTP推送',
    http_pull: 'HTTP拉取',
    db_view: '数据库视图'
  }
  return labelMap[type] || type
}

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增厂家')
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单数据
const formData = reactive<Vendor>({
  vendorCode: '',
  vendorName: '',
  hospitalCode: '',
  hospitalName: '',
  accessType: '',
  description: '',
  contactInfo: '',
  enabled: true
})

// 表单验证规则
const formRules: FormRules = {
  vendorCode: [
    { required: true, message: '请输入厂家编码', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_-]+$/, message: '厂家编码只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  vendorName: [{ required: true, message: '请输入厂家名称', trigger: 'blur' }],
  hospitalCode: [{ required: true, message: '请输入医院编码', trigger: 'blur' }],
  hospitalName: [{ required: true, message: '请输入医院名称', trigger: 'blur' }],
  accessType: [{ required: true, message: '请选择接入方式', trigger: 'change' }]
}

// 搜索
const handleSearch = () => {
  // 实际可调用后端搜索接口
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增厂家'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: Vendor) => {
  dialogTitle.value = '编辑厂家'
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: Vendor) => {
  try {
    await ElMessageBox.confirm('确定要删除该厂家吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await request.delete(`/api/vendor/${row.vendorCode}`)
    ElMessage.success('删除成功')
    fetchVendorList()
  } catch {
    // 取消操作
  }
}

// 切换启用状态
const handleToggleEnabled = async (row: Vendor) => {
  try {
    await request.put(`/api/vendor/${row.vendorCode}/toggle`, { enabled: row.enabled })
    ElMessage.success(row.enabled ? '已启用' : '已停用')
  } catch {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const res = await request.post('/api/vendor', { ...formData })
        if (res.data.code === 0) {
          ElMessage.success(isEdit.value ? '更新成功' : '新增成功')
          dialogVisible.value = false
          fetchVendorList()
        } else {
          ElMessage.error(res.data.message || '操作失败')
        }
      } catch (e: any) {
        ElMessage.error(e.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    vendorCode: '',
    vendorName: '',
    hospitalCode: '',
    hospitalName: '',
    accessType: '',
    description: '',
    contactInfo: '',
    enabled: true
  })
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
    ElMessage.error('获取厂家列表失败')
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
.vendor-list-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 16px;

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .toolbar-left {
    display: flex;
    gap: 12px;
  }
}

.table-card {
  :deep(.el-table) {
    margin-top: 0;
  }
}
</style>
