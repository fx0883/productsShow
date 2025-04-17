<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增用户
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
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

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
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

    <!-- 用户表单对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="userForm.status"
            :active-value="'active'"
            :inactive-value="'inactive'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser } from '../../api/user'
import { useUserStore } from '../../stores/user'
import type { UserInfo } from '../../types/api'

const userStore = useUserStore()

// 搜索表单
const searchForm = reactive({
  username: '',
  role: ''
})

// 表格数据
const tableData = ref<UserInfo[]>([])
const loading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add')
const dialogTitle = ref('新增用户')
const userFormRef = ref<FormInstance>()

// 用户表单
const userForm = reactive({
  username: '',
  email: '',
  password: '',
  role: '',
  status: 'active'
})

// 表单验证规则
const userFormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

// 在现有变量后添加
const currentUserId = ref<number>(0)

// 初始化
onMounted(async () => {
  await fetchUserList()
})

// 获取用户列表
const fetchUserList = async () => {
  try {
    loading.value = true
    const data = await getUserList({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchForm.username,
      role: searchForm.role
    })
    tableData.value = data
    // 设置总数（假设API返回了总数）
    total.value = 100 // TODO: 从API响应中获取实际总数
  } catch (error: any) {
    ElMessage.error(error.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 修改搜索方法
const handleSearch = () => {
  currentPage.value = 1
  fetchUserList()
}

// 重置搜索
const handleReset = () => {
  searchForm.username = ''
  searchForm.role = ''
  handleSearch()
}

// 分页相关方法
const handleSizeChange = (val: number) => {
  pageSize.value = val
  handleSearch()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  handleSearch()
}

// 新增用户
const handleAdd = () => {
  dialogType.value = 'add'
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
  Object.assign(userForm, {
    username: '',
    email: '',
    password: '',
    role: '',
    status: 'active'
  })
}

// 编辑用户
const handleEdit = (row: UserInfo) => {
  dialogType.value = 'edit'
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
  currentUserId.value = row.id
  Object.assign(userForm, {
    username: row.username,
    email: row.email,
    password: '',
    role: row.is_admin ? 'admin' : 'user',
    status: 'active',
    phone: row.phone || ''
  })
}

// 删除用户
const handleDelete = (row: UserInfo) => {
  ElMessageBox.confirm('确认删除该用户吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        loading.value = true
        await deleteUser(row.id)
        ElMessage.success('删除成功')
        fetchUserList()
      } catch (error: any) {
        ElMessage.error(error.message || '删除用户失败')
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return

  try {
    await userFormRef.value.validate()
    loading.value = true
    
    if (dialogType.value === 'add') {
      await createUser({
        username: userForm.username,
        email: userForm.email,
        password: userForm.password,
        is_admin: userForm.role === 'admin',
        is_member: userForm.role === 'user',
        phone: userForm.phone
      })
    } else {
      await updateUser(currentUserId.value, {
        username: userForm.username,
        email: userForm.email,
        is_admin: userForm.role === 'admin',
        is_member: userForm.role === 'user',
        phone: userForm.phone
      })
    }
    
    ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
    dialogVisible.value = false
    fetchUserList()
  } catch (error: any) {
    console.error('表单验证失败:', error)
    ElMessage.error(error.message || '提交失败')
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}
</script>

<style scoped>
.users-container {
  min-height: 100%;
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