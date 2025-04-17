<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
            </div>
          </template>
          <div class="user-info">
            <el-avatar :size="100" :icon="UserFilled" class="avatar" />
            <h3>{{ userStore.userInfo?.username || '用户名' }}</h3>
            <p>{{ userStore.userInfo?.email || '邮箱' }}</p>
            <el-tag v-if="userStore.userInfo?.is_super_admin">超级管理员</el-tag>
            <el-tag v-else-if="userStore.userInfo?.is_admin" type="success">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
            <p v-if="userStore.userInfo?.tenant">
              <span>所属租户: </span>
              <el-tag type="warning">{{ userStore.userInfo.tenant.name }}</el-tag>
            </p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>编辑个人信息</span>
            </div>
          </template>
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            v-loading="loading"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item label="昵称" prop="nick_name">
              <el-input v-model="profileForm.nick_name" />
            </el-form-item>
            <el-form-item label="语言偏好" prop="preferred_language">
              <el-select v-model="profileForm.preferred_language">
                <el-option label="中文" value="zh-cn" />
                <el-option label="英文" value="en-us" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>修改密码</span>
            </div>
          </template>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
            v-loading="passwordLoading"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '../../stores/user'
import { updateCurrentUser, changePassword } from '../../api/user'

const userStore = useUserStore()
const loading = ref(false)
const passwordLoading = ref(false)
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
  nick_name: '',
  preferred_language: 'zh-cn'
})

// 修改密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const profileRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 密码验证规则
const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 初始化用户信息
onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.getUserInfo()
  }
  
  if (userStore.userInfo) {
    Object.assign(profileForm, {
      username: userStore.userInfo.username || '',
      email: userStore.userInfo.email || '',
      phone: userStore.userInfo.phone || '',
      nick_name: userStore.userInfo.nick_name || '',
      preferred_language: 'zh-cn' // 默认中文
    })
  }
})

// 更新个人信息
const handleUpdateProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    loading.value = true
    
    await updateCurrentUser({
      username: profileForm.username,
      email: profileForm.email,
      phone: profileForm.phone,
      nick_name: profileForm.nick_name,
      preferred_language: profileForm.preferred_language
    })
    
    ElMessage.success('个人信息更新成功')
    // 重新获取用户信息
    await userStore.getUserInfo()
  } catch (error: any) {
    ElMessage.error(error.message || '更新个人信息失败')
  } finally {
    loading.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    
    ElMessage.success('密码修改成功')
    // 重置表单
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    passwordFormRef.value.resetFields()
  } catch (error: any) {
    ElMessage.error(error.message || '修改密码失败')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.avatar {
  margin-bottom: 10px;
}
</style>