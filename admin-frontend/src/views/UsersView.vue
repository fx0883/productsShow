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
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
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

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column label="角色">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="success">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" />
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
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
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
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 模拟用户数据
const mockUsers = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    phone: '13800138000',
    is_admin: true,
    is_member: false,
    date_joined: '2023-07-01 10:00:00',
    last_login: '2023-07-18 09:45:12'
  },
  {
    id: 2,
    username: 'user1',
    email: 'user1@example.com',
    phone: '13900139000',
    is_admin: false,
    is_member: true,
    date_joined: '2023-07-05 14:30:00',
    last_login: '2023-07-17 16:20:35'
  },
  {
    id: 3,
    username: 'manager',
    email: 'manager@example.com',
    phone: '13700137000',
    is_admin: true,
    is_member: false,
    date_joined: '2023-07-10 09:15:00',
    last_login: '2023-07-18 11:30:22'
  }
]

// 搜索表单
const searchForm = reactive({
  username: '',
  role: ''
})

// 表格数据
const tableData = ref(mockUsers)
const loading = ref(false)
const submitLoading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(mockUsers.length)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add')
const dialogTitle = ref('新增用户')
const userFormRef = ref<FormInstance>()
const currentUserId = ref(0)

// 用户表单
const userForm = reactive({
  username: '',
  email: '',
  password: '',
  phone: '',
  role: ''
})

// 表单验证规则
const userFormRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
})

// 初始化
onMounted(() => {
  fetchUserList()
})

// 获取用户列表（模拟）
const fetchUserList = () => {
  loading.value = true
  
  setTimeout(() => {
    // 筛选条件
    let filteredData = [...mockUsers]
    
    if (searchForm.username) {
      filteredData = filteredData.filter(item => 
        item.username.toLowerCase().includes(searchForm.username.toLowerCase())
      )
    }
    
    if (searchForm.role) {
      if (searchForm.role === 'admin') {
        filteredData = filteredData.filter(item => item.is_admin)
      } else {
        filteredData = filteredData.filter(item => !item.is_admin)
      }
    }
    
    // 分页处理
    total.value = filteredData.length
    const startIdx = (currentPage.value - 1) * pageSize.value
    const endIdx = startIdx + pageSize.value
    tableData.value = filteredData.slice(startIdx, endIdx)
    
    loading.value = false
  }, 500)
}

// 搜索
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

// 分页方法
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchUserList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchUserList()
}

// 新增用户
const handleAdd = () => {
  dialogType.value = 'add'
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
  
  // 重置表单
  Object.assign(userForm, {
    username: '',
    email: '',
    password: '',
    phone: '',
    role: ''
  })
}

// 编辑用户
const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
  currentUserId.value = row.id
  
  // 填充表单
  Object.assign(userForm, {
    username: row.username,
    email: row.email,
    phone: row.phone || '',
    role: row.is_admin ? 'admin' : 'user'
  })
}

// 删除用户
const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该用户吗？该操作不可恢复！', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 模拟删除
    const index = mockUsers.findIndex(item => item.id === row.id)
    if (index !== -1) {
      mockUsers.splice(index, 1)
      ElMessage.success('删除成功')
      fetchUserList()
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    submitLoading.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (dialogType.value === 'add') {
      // 模拟新增
      const newUser = {
        id: mockUsers.length + 1,
        username: userForm.username,
        email: userForm.email,
        phone: userForm.phone,
        is_admin: userForm.role === 'admin',
        is_member: userForm.role === 'user',
        date_joined: new Date().toISOString().replace('T', ' ').substring(0, 19),
        last_login: null
      }
      mockUsers.push(newUser)
      ElMessage.success('添加用户成功')
    } else {
      // 模拟编辑
      const index = mockUsers.findIndex(item => item.id === currentUserId.value)
      if (index !== -1) {
        mockUsers[index] = {
          ...mockUsers[index],
          username: userForm.username,
          email: userForm.email,
          phone: userForm.phone,
          is_admin: userForm.role === 'admin',
          is_member: userForm.role === 'user'
        }
        ElMessage.success('更新用户成功')
      }
    }
    
    dialogVisible.value = false
    fetchUserList()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitLoading.value = false
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