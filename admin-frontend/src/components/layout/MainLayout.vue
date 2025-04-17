<template>
  <div class="main-layout">
    <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="logo">
        <h2 v-if="!isSidebarCollapsed">后台管理系统</h2>
        <h2 v-else>A</h2>
      </div>
      <div class="menu">
        <router-link 
          v-for="menu in menus" 
          :key="menu.path" 
          :to="menu.path"
          class="menu-item"
          :class="{ active: currentPath.startsWith(menu.path) }"
        >
          <i :class="menu.icon"></i>
          <span v-if="!isSidebarCollapsed">{{ menu.title }}</span>
        </router-link>
      </div>
    </aside>
    
    <div class="main-content">
      <header class="top-header">
        <div class="header-left">
          <button class="toggle-btn" @click="toggleSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <div class="breadcrumb">{{ currentRoute?.meta?.title || '首页' }}</div>
        </div>
        <div class="header-right">
          <div class="user-dropdown" @click="showUserMenu = !showUserMenu">
            <div class="avatar">
              <img :src="userAvatar" alt="User Avatar">
            </div>
            <span>{{ userStore.userInfo?.username || '用户' }}</span>
            <i class="fas fa-chevron-down"></i>
            
            <div class="dropdown-menu" v-if="showUserMenu">
              <div class="dropdown-item" @click="goToProfile">
                <i class="fas fa-user"></i> 个人信息
              </div>
              <div class="dropdown-item" @click="logout">
                <i class="fas fa-sign-out-alt"></i> 退出登录
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <main class="content">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const isSidebarCollapsed = ref(false)
const showUserMenu = ref(false)

// 菜单项
const menus = ref([
  { title: '仪表盘', path: '/dashboard', icon: 'fas fa-tachometer-alt' },
  { title: '产品管理', path: '/products', icon: 'fas fa-box' },
  { title: '订单管理', path: '/orders', icon: 'fas fa-shopping-cart' },
  { title: '用户管理', path: '/users', icon: 'fas fa-users' },
  { title: '系统设置', path: '/settings', icon: 'fas fa-cog' },
])

const currentRoute = computed(() => route)
const currentPath = computed(() => route.path)

const userAvatar = computed(() => {
  return userStore.userInfo?.avatar || 'https://via.placeholder.com/40'
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarState', isSidebarCollapsed.value ? 'collapsed' : 'expanded')
}

const goToProfile = () => {
  showUserMenu.value = false
  router.push('/profile')
}

const logout = () => {
  showUserMenu.value = false
  userStore.logout()
}

// 点击外部区域关闭用户菜单
const closeUserMenu = (e: MouseEvent) => {
  const dropdown = document.querySelector('.user-dropdown')
  if (dropdown && !dropdown.contains(e.target as Node) && showUserMenu.value) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  // 从本地存储中恢复侧边栏状态
  const savedState = localStorage.getItem('sidebarState')
  if (savedState) {
    isSidebarCollapsed.value = savedState === 'collapsed'
  }
  
  // 添加点击外部关闭事件
  document.addEventListener('click', closeUserMenu)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeUserMenu)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 70px;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.menu {
  padding: 20px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s;
}

.menu-item i {
  font-size: 18px;
  width: 30px;
}

.menu-item span {
  margin-left: 10px;
}

.menu-item:hover, .menu-item.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.top-header {
  height: 64px;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  margin-right: 15px;
  color: #555;
}

.breadcrumb {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
}

.user-dropdown:hover {
  background-color: #f9f9f9;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-dropdown i {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 160px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  z-index: 100;
  margin-top: 5px;
}

.dropdown-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  color: #333;
}

.dropdown-item i {
  margin-right: 8px;
  color: #666;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.content {
  flex: 1;
  padding: 20px;
  background-color: #f5f7f9;
  overflow-y: auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .sidebar {
    width: 70px;
  }
  
  .sidebar:not(.collapsed) {
    width: 250px;
    position: absolute;
    z-index: 1000;
    height: 100vh;
  }
}
</style> 