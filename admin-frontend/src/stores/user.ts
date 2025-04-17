import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 添加日志工具函数
const logger = {
  log: (message: string, data?: any) => {
    const timestamp = new Date().toISOString();
    if (data) {
      console.log(`[UserStore ${timestamp}] ${message}`, data);
    } else {
      console.log(`[UserStore ${timestamp}] ${message}`);
    }
  },
  error: (message: string, error?: any) => {
    const timestamp = new Date().toISOString();
    if (error) {
      console.error(`[UserStore Error ${timestamp}] ${message}`, error);
    } else {
      console.error(`[UserStore Error ${timestamp}] ${message}`);
    }
  }
};

export interface UserInfo {
  id: number
  username: string
  avatar?: string
  email?: string
  role: string
  permissions: string[]
  is_admin?: boolean
  is_super_admin?: boolean
  tenant?: any
  phone?: string
  nick_name?: string
}

export const useUserStore = defineStore('user', () => {
  const router = useRouter()
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  logger.log('初始化用户存储', { hasToken: !!token.value });

  // 登录
  const login = async (username: string, password: string) => {
    logger.log(`尝试用户登录: ${username}`);
    try {
      isLoading.value = true
      
      // 这里应该是实际的API调用，现在仅用模拟数据
      // const response = await fetch('/api/login', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({ username, password }),
      // })
      // const data = await response.json()
      
      // 模拟登录成功
      logger.log('模拟API延迟...');
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 模拟数据
      const mockToken = 'mock-jwt-token-' + Math.random().toString(36).substring(2)
      const mockUserInfo: UserInfo = {
        id: 1,
        username,
        avatar: 'https://via.placeholder.com/150',
        email: username + '@example.com',
        role: 'admin',
        permissions: ['read', 'write', 'delete', 'products.view', 'users.manage'],
        is_admin: true,
        is_super_admin: username === 'admin',
        phone: '13800138000',
        nick_name: username
      }
      
      logger.log('登录成功，存储用户信息', { username, role: mockUserInfo.role });
      
      // 存储登录信息
      token.value = mockToken
      userInfo.value = mockUserInfo
      localStorage.setItem('token', mockToken)
      
      ElMessage.success('登录成功')
      router.push('/')
      
      return true
    } catch (error) {
      logger.error('登录失败', error);
      console.error('登录失败:', error)
      ElMessage.error('登录失败，请检查用户名和密码')
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 退出登录
  const logout = () => {
    logger.log('用户退出登录');
    token.value = null
    userInfo.value = null
    localStorage.removeItem('token')
    router.push('/login')
    ElMessage.success('退出登录成功')
  }

  // 获取用户信息 - 添加这个缺失的方法
  const getUserInfo = async () => {
    logger.log('尝试获取用户信息', { hasToken: !!token.value });
    return await fetchUserInfo();
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    logger.log('尝试获取用户信息', { hasToken: !!token.value });
    if (!token.value) {
      logger.log('获取用户信息失败: 没有令牌');
      return null;
    }
    
    try {
      isLoading.value = true
      
      // 这里应该是实际的API调用，现在仅用模拟数据
      // const response = await fetch('/api/user/info', {
      //   headers: {
      //     'Authorization': `Bearer ${token.value}`
      //   }
      // })
      // const data = await response.json()
      
      // 模拟获取用户信息
      logger.log('模拟API延迟...');
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 模拟数据
      userInfo.value = {
        id: 1,
        username: 'admin',
        avatar: 'https://via.placeholder.com/150',
        email: 'admin@example.com',
        role: 'admin',
        permissions: ['read', 'write', 'delete', 'products.view', 'users.manage'],
        is_admin: true,
        is_super_admin: true,
        phone: '13800138000',
        nick_name: 'Admin User',
        tenant: {
          id: 1,
          name: '默认租户'
        }
      }
      
      logger.log('获取用户信息成功', userInfo.value);
      return userInfo.value
    } catch (error) {
      logger.error('获取用户信息失败', error);
      console.error('获取用户信息失败:', error)
      token.value = null
      localStorage.removeItem('token')
      return null
    } finally {
      isLoading.value = false
    }
  }

  // 检查是否已登录
  const isLoggedIn = () => {
    const loggedIn = !!token.value;
    logger.log(`检查用户是否已登录: ${loggedIn}`);
    return loggedIn;
  }

  // 检查是否有特定权限
  const hasPermission = (permission: string) => {
    const has = userInfo.value?.permissions.includes(permission) || false;
    logger.log(`检查权限 [${permission}]: ${has}`, { 
      permissions: userInfo.value?.permissions || [] 
    });
    return has;
  }

  // 检查是否为管理员
  const isAdmin = () => {
    const admin = userInfo.value?.is_admin || false;
    logger.log(`检查是否为管理员: ${admin}`);
    return admin;
  }

  // 检查是否为超级管理员
  const isSuperAdmin = () => {
    const superAdmin = userInfo.value?.is_super_admin || false;
    logger.log(`检查是否为超级管理员: ${superAdmin}`);
    return superAdmin;
  }

  return {
    token,
    userInfo,
    isLoading,
    login,
    logout,
    fetchUserInfo,
    getUserInfo,
    isLoggedIn,
    hasPermission,
    isAdmin,
    isSuperAdmin
  }
}) 