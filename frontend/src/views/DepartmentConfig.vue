<template>
  <div class="department-config-container">
    <!-- 顶部选择厂家 -->
    <el-card shadow="never" class="selector-card">
      <div class="selector-row">
        <span class="selector-label">选择厂家：</span>
        <el-select v-model="selectedVendor" placeholder="请选择厂家" style="width: 300px" @change="handleVendorChange">
          <el-option v-for="vendor in vendorList" :key="vendor.vendorCode" :label="vendor.vendorName" :value="vendor.vendorCode" />
        </el-select>
      </div>
    </el-card>

    <!-- 科室列表 -->
    <el-card shadow="never" class="table-card" v-if="selectedVendor">
      <template #header>
        <div class="card-header">
          <span>科室/病区列表</span>
          <div>
            <el-button type="primary" @click="openAddDialog">新增科室</el-button>
            <el-button type="success" @click="openBatchImportDialog">批量导入</el-button>
            <el-button type="primary" link @click="fetchDepartments">刷新</el-button>
          </div>
        </div>
      </template>
      <el-table :data="departments" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="wardCode" label="病区编码" width="110" />
        <el-table-column prop="wardName" label="病区名称" width="120" />
        <el-table-column prop="hisDeptCode" label="HIS科室编码" width="120" />
        <el-table-column prop="hisDeptName" label="HIS科室名称" width="120" />
        <el-table-column prop="hisWardCode" label="HIS病区编码" width="120" />
        <el-table-column prop="hisWardName" label="HIS病区名称" width="120" />
        <el-table-column label="床位范围" width="120">
          <template #default="{ row }">
            {{ row.bedRangeStart && row.bedRangeEnd ? `${row.bedRangeStart}~${row.bedRangeEnd}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" size="small" @change="handleToggle(row, 'enabled')" />
          </template>
        </el-table-column>
        <el-table-column prop="syncEnabled" label="同步" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.syncEnabled" size="small" @change="handleToggle(row, 'syncEnabled')" />
          </template>
        </el-table-column>
        <el-table-column prop="callbackEnabled" label="回传" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.callbackEnabled" size="small" @change="handleToggle(row, 'callbackEnabled')" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该科室？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchDepartments"
          @current-change="fetchDepartments"
        />
      </div>
    </el-card>

    <!-- 未选择厂家时的提示 -->
    <el-card shadow="never" class="empty-card" v-else>
      <el-empty description="请先选择厂家" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑科室' : '新增科室'" width="650px" destroy-on-close>
      <el-form ref="deptFormRef" :model="deptForm" :rules="deptRules" label-width="130px">
        <el-form-item label="厂家编码">
          <el-input :model-value="selectedVendor" disabled />
        </el-form-item>
        <el-form-item label="病区编码" prop="wardCode">
          <el-input v-model="deptForm.wardCode" placeholder="请输入病区编码" />
        </el-form-item>
        <el-form-item label="病区名称" prop="wardName">
          <el-input v-model="deptForm.wardName" placeholder="请输入病区名称" />
        </el-form-item>
        <el-form-item label="医院编码">
          <el-input v-model="deptForm.hospitalCode" placeholder="请输入医院编码" />
        </el-form-item>
        <el-form-item label="HIS科室编码">
          <el-input v-model="deptForm.hisDeptCode" placeholder="HIS系统科室编码" />
          <div class="form-tip">HIS系统科室编码</div>
        </el-form-item>
        <el-form-item label="HIS科室名称">
          <el-input v-model="deptForm.hisDeptName" placeholder="HIS系统科室名称" />
          <div class="form-tip">HIS系统科室名称</div>
        </el-form-item>
        <el-form-item label="HIS病区编码">
          <el-input v-model="deptForm.hisWardCode" placeholder="HIS系统病区编码" />
          <div class="form-tip">HIS系统病区编码</div>
        </el-form-item>
        <el-form-item label="HIS病区名称">
          <el-input v-model="deptForm.hisWardName" placeholder="HIS系统病区名称" />
          <div class="form-tip">HIS系统病区名称</div>
        </el-form-item>
        <el-form-item label="床位起始号">
          <el-input v-model="deptForm.bedRangeStart" placeholder="如: 01" />
          <div class="form-tip">床位范围，如 01~20</div>
        </el-form-item>
        <el-form-item label="床位结束号">
          <el-input v-model="deptForm.bedRangeEnd" placeholder="如: 20" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="deptForm.enabled" />
        </el-form-item>
        <el-form-item label="同步启用">
          <el-switch v-model="deptForm.syncEnabled" />
        </el-form-item>
        <el-form-item label="回传启用">
          <el-switch v-model="deptForm.callbackEnabled" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="deptForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDept" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="batchDialogVisible" title="批量导入科室" width="650px" destroy-on-close>
      <el-alert title="请输入JSON数组格式的科室数据" type="info" :closable="false" style="margin-bottom: 16px" />
      <el-input
        v-model="batchImportData"
        type="textarea"
        :rows="12"
        placeholder='[{"wardCode":"W001","wardName":"内科一病区","hisDeptCode":"D001","hisDeptName":"内科"}]'
      />
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchImport" :loading="batchImporting">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import request from '@/api/request'

// 厂家接口
interface Vendor {
  vendorCode: string
  vendorName: string
}

// 科室接口
interface Department {
  id?: number
  vendorCode: string
  wardCode: string
  wardName: string
  hospitalCode: string
  hisDeptCode: string
  hisDeptName: string
  hisWardCode: string
  hisWardName: string
  bedRangeStart: string
  bedRangeEnd: string
  enabled: boolean
  syncEnabled: boolean
  callbackEnabled: boolean
  remark: string
}

// 厂家列表
const vendorList = ref<Vendor[]>([])
const selectedVendor = ref('')
const loading = ref(false)
const saving = ref(false)
const batchImporting = ref(false)

// 科室列表
const departments = ref<Department[]>([])
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 弹窗
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

// 表单
const deptFormRef = ref<FormInstance>()
const defaultDeptForm = (): Department => ({
  vendorCode: '',
  wardCode: '',
  wardName: '',
  hospitalCode: '',
  hisDeptCode: '',
  hisDeptName: '',
  hisWardCode: '',
  hisWardName: '',
  bedRangeStart: '',
  bedRangeEnd: '',
  enabled: true,
  syncEnabled: true,
  callbackEnabled: true,
  remark: ''
})

const deptForm = reactive<Department>(defaultDeptForm())

const deptRules: FormRules = {
  wardCode: [{ required: true, message: '请输入病区编码', trigger: 'blur' }],
  wardName: [{ required: true, message: '请输入病区名称', trigger: 'blur' }]
}

// 批量导入
const batchDialogVisible = ref(false)
const batchImportData = ref('')

// 获取厂家列表
const fetchVendorList = async () => {
  try {
    const res = await request.get('/api/vendor/list')
    vendorList.value = res.data?.data || res.data || []
  } catch {
    vendorList.value = []
  }
}

// 厂家切换
const handleVendorChange = (vendorCode: string) => {
  if (vendorCode) {
    pagination.page = 1
    fetchDepartments()
  }
}

// 获取科室列表
const fetchDepartments = async () => {
  if (!selectedVendor.value) return
  loading.value = true
  try {
    const res = await request.get('/api/department/list', {
      params: {
        vendorCode: selectedVendor.value,
        page: pagination.page,
        page_size: pagination.pageSize
      }
    })
    const data = res.data?.data || res.data
    departments.value = data?.items || data?.list || []
    pagination.total = data?.total || 0
  } catch {
    departments.value = []
  } finally {
    loading.value = false
  }
}

// 打开新增弹窗
const openAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  Object.assign(deptForm, defaultDeptForm())
  dialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (row: Department) => {
  isEditing.value = true
  editingId.value = row.id ?? null
  Object.assign(deptForm, row)
  dialogVisible.value = true
}

// 保存科室
const handleSaveDept = async () => {
  if (!deptFormRef.value) return
  await deptFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const payload = { ...deptForm, vendorCode: selectedVendor.value }
        if (isEditing.value && editingId.value) {
          await request.put(`/api/department/${editingId.value}`, payload)
          ElMessage.success('更新成功')
        } else {
          await request.post('/api/department', payload)
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        fetchDepartments()
      } catch {
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 删除科室
const handleDelete = async (row: Department) => {
  try {
    await request.delete(`/api/department/${row.id}`)
    ElMessage.success('删除成功')
    fetchDepartments()
  } catch {
    ElMessage.error('删除失败')
  }
}

// 切换状态
const handleToggle = async (row: Department, field: string) => {
  try {
    await request.put(`/api/department/${row.id}`, { [field]: row[field as keyof Department] })
    ElMessage.success('更新成功')
  } catch {
    // 回滚
    row[field as keyof Department] = !row[field as keyof Department] as any
    ElMessage.error('更新失败')
  }
}

// 打开批量导入弹窗
const openBatchImportDialog = () => {
  batchImportData.value = ''
  batchDialogVisible.value = true
}

// 批量导入
const handleBatchImport = async () => {
  let parsed: Department[]
  try {
    parsed = JSON.parse(batchImportData.value)
    if (!Array.isArray(parsed)) {
      ElMessage.error('请输入JSON数组格式')
      return
    }
  } catch {
    ElMessage.error('JSON格式错误，请检查输入')
    return
  }

  batchImporting.value = true
  try {
    await request.post('/api/department/batch', {
      vendorCode: selectedVendor.value,
      departments: parsed
    })
    ElMessage.success(`成功导入 ${parsed.length} 条记录`)
    batchDialogVisible.value = false
    fetchDepartments()
  } catch {
    ElMessage.error('批量导入失败')
  } finally {
    batchImporting.value = false
  }
}

// 初始化
onMounted(() => {
  fetchVendorList()
})
</script>

<style scoped lang="scss">
.department-config-container {
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

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.empty-card {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
