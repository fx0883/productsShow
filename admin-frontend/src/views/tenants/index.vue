<template>
  <div class="tenants-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>租户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增租户
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="租户名称">
          <el-input v-model="searchForm.name" placeholder="请输入租户名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="suspended" />
            <el-option label="已删除" value="deleted" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tenantStore.tenantList" border v-loading="tenantStore.loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="租户名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="success" link @click="handleViewQuota(row)">
              <el-icon><Coin /></el-icon>配额
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 租户表单对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="tenantFormRef"
        :model="tenantForm"
        :rules="tenantFormRules"
        label-width="80px"
      >
        <el-form-item label="租户名称" prop="name">
          <el-input v-model="tenantForm.name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="tenantForm.status" placeholder="请选择状态">
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="suspended" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 配额对话框 -->
    <el-dialog
      title="租户配额"
      v-model="quotaDialogVisible"
      width="500px"
    >
      <el-form
        ref="quotaFormRef"
        :model="quotaForm"
        label-width="140px"
        v-loading="quotaLoading"
      >
        <el-form-item label="租户名称">
          <el-input v-model="currentTenantName" disabled />
        </el-form-item>
        <el-form-item label="最大用户数" prop="max_users">
          <el-input-number v-model="quotaForm.max_users" :min="1" />
        </el-form-item>
        <el-form-item label="最大管理员数" prop="max_admins">
          <el-input-number v-model="quotaForm.max_admins" :min="1" />
        </el-form-item>
        <el-form-item label="最大存储空间(MB)" prop="max_storage_mb">
          <el-input-number v-model="quotaForm.max_storage_mb" :min="1" />
        </el-form-item>
        <el-form-item label="最大产品数" prop="max_products">
          <el-input-number v-model="quotaForm.max_products" :min="1" />
        </el-form-item>
        <el-form-item label="已用存储空间(MB)">
          <el-input v-model="quotaForm.current_storage_used_mb" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="quotaDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateQuota">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Refresh, Edit, Delete, Coin } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { useTenantStore } from '../../stores/tenant'
import { getTenantQuota, updateTenantQuota } from '../../api/tenant'
import type { Tenant, TenantQuota } from '../../types/api'

const tenantStore = useTenantStore()

// 搜索表单
const searchForm = reactive({
  name: '',
  status: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add')
const dialogTitle = ref('新增租户')
const tenantFormRef = ref<FormInstance>()

// 租户表单
const tenantForm = reactive({
  name: '',
  status: 'active'
})

// 表单验证规则
const tenantFormRules = {
  name: [{ required: true, message: '请输入租户名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 配额对话框相关
const quotaDialogVisible = ref(false)
const quotaFormRef = ref<FormInstance>()
const quotaLoading = ref(false)
const currentTenantId = ref<number>(0)
const currentTenantName = ref('')

// 配额表单
const quotaForm = reactive<TenantQuota>({
  max_users: 10,
  max_admins: 2,
  max_storage_mb: 1024,
  max_products: 100,
  current_storage_used_mb: 0
})

// 初始化
onMounted(async () => {
  await fetchTenantList()
})

// 获取租户列表
const fetchTenantList = async () => {
  try {
    await tenantStore.fetchTenantList({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchForm.name,
      status: searchForm.status
    })
    // 设置总数（假设API返回了总数）
    total.value = 100 // TODO: 从API响应中获取实际总数
  } catch (error: any) {
    ElMessage.error(error.message || '获取租户列表失败')
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchTenantList()
}

// 重置搜索
const handleReset = () => {
  searchForm.name = ''
  searchForm.status = ''
  handleSearch()
}

// 分页相关方法
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchTenantList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchTenantList()
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'active':
      return 'success'
    case 'suspended':
      return 'warning'
    case 'deleted':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'active':
      return '活跃'
    case 'suspended':
      return '暂停'
    case 'deleted':
      return '已删除'
    default:
      return '未知'
  }
}

// 新增租户
const handleAdd = () => {
  dialogType.value = 'add'
  dialogTitle.value = '新增租户'
  dialogVisible.value = true
  Object.assign(tenantForm, {
    name: '',
    status: 'active'
  })
}

// 编辑租户
const handleEdit = (row: Tenant) => {
  dialogType.value = 'edit'
  dialogTitle.value = '编辑租户'
  dialogVisible.value = true
  Object.assign(tenantForm, {
    name: row.name,
    status: row.status
  })
  currentTenantId.value = row.id
}

// 查看配额
const handleViewQuota = async (row: Tenant) => {
  try {
    quotaLoading.value = true
    currentTenantId.value = row.id
    currentTenantName.value = row.name
    
    // 获取租户配额
    const quotaData = await getTenantQuota(row.id)
    Object.assign(quotaForm, quotaData)
    
    quotaDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取租户配额失败')
  } finally {
    quotaLoading.value = false
  }
}

// 更新配额
const handleUpdateQuota = async () => {
  try {
    quotaLoading.value = true
    await updateTenantQuota(currentTenantId.value, {
      max_users: quotaForm.max_users,
      max_admins: quotaForm.max_admins,
      max_storage_mb: quotaForm.max_storage_mb,
      max_products: quotaForm.max_products
    })
    
    ElMessage.success('更新配额成功')
    quotaDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '更新配额失败')
  } finally {
    quotaLoading.value = false
  }
}

// 删除租户
const handleDelete = (row: Tenant) => {
  ElMessageBox.confirm('确认删除该租户吗？这将删除租户下的所有数据！', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        // TODO: 实现删除逻辑
        ElMessage.success('删除成功')
        fetchTenantList()
      } catch (error: any) {
        ElMessage.error(error.message || '删除租户失败')
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 提交表单
const handleSubmit = async () => {
  if (!tenantFormRef.value) return

  try {
    await tenantFormRef.value.validate()
    
    if (dialogType.value === 'add') {
      // TODO: 实现添加租户逻辑
    } else {
      // TODO: 实现更新租户逻辑
    }
    
    ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
    dialogVisible.value = false
    fetchTenantList()
  } catch (error: any) {
    console.error('表单验证失败:', error)
    ElMessage.error(error.message || '提交失败')
  }
}

// 关闭对话框
const handleDialogClose = () => {
  if (tenantFormRef.value) {
    tenantFormRef.value.resetFields()
  }
}
</script>

<style scoped>
.tenants-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 