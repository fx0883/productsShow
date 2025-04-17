<template>
  <div class="dashboard-container">
    <el-container class="dashboard-layout">
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <h2>产品展示系统</h2>
        </div>
        <el-menu
          router
          :default-active="currentPath"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/users" v-if="userStore.isAdmin()">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/tenants" v-if="userStore.isSuperAdmin()">
            <el-icon><OfficeBuilding /></el-icon>
            <span>租户管理</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/profile">
            <el-icon><Setting /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="route.path.includes('/users')">用户管理</el-breadcrumb-item>
              <el-breadcrumb-item v-if="route.path.includes('/tenants')">租户管理</el-breadcrumb-item>
              <el-breadcrumb-item v-if="route.path.includes('/profile')">个人信息</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="user-dropdown">
                {{ userStore.userInfo?.username }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, User, OfficeBuilding, Setting, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 当前路径
const currentPath = computed(() => route.path)

// 初始化
onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.getUserInfo()
  }
})

// 下拉菜单点击事件
const handleCommand = (command: string) => {
  if (command === 'profile') {
    router.push('/dashboard/profile')
  } else if (command === 'logout') {
    userStore.logout()
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.dashboard-layout {
  height: 100%;
}

.sidebar {
  background-color: #304156;
  color: #fff;
  height: 100%;
}

.logo {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  background-color: #263445;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-content {
  background-color: #f0f2f5;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 0;
}
</style>