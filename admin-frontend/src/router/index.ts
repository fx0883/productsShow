import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 添加日志工具函数
const logger = {
  log: (message: string, data?: any) => {
    const timestamp = new Date().toISOString();
    if (data) {
      console.log(`[Router ${timestamp}] ${message}`, data);
    } else {
      console.log(`[Router ${timestamp}] ${message}`);
    }
  },
  error: (message: string, error?: any) => {
    const timestamp = new Date().toISOString();
    if (error) {
      console.error(`[Router Error ${timestamp}] ${message}`, error);
    } else {
      console.error(`[Router Error ${timestamp}] ${message}`);
    }
  },
  warn: (message: string, data?: any) => {
    const timestamp = new Date().toISOString();
    if (data) {
      console.warn(`[Router Warning ${timestamp}] ${message}`, data);
    } else {
      console.warn(`[Router Warning ${timestamp}] ${message}`);
    }
  },
  time: (label: string) => {
    console.time(`[Router Time] ${label}`);
  },
  timeEnd: (label: string) => {
    console.timeEnd(`[Router Time] ${label}`);
  }
};

// 封装异步组件加载，添加错误处理
const asyncComponent = (importFn: () => Promise<any>, name: string) => {
  return () => {
    logger.time(`加载组件: ${name}`);
    return importFn().then(comp => {
      logger.timeEnd(`加载组件: ${name}`);
      logger.log(`组件 ${name} 加载成功`);
      return comp;
    }).catch(err => {
      logger.error(`组件 ${name} 加载失败`, err);
      throw err;
    });
  };
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: asyncComponent(() => import('@/views/LoginView.vue'), 'LoginView'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: asyncComponent(() => import('@/views/HomeView.vue'), 'HomeView'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: asyncComponent(() => import('@/views/DashboardView.vue'), 'DashboardView'),
      meta: { requiresAuth: true }
    },
    {
      path: '/products',
      name: 'products',
      component: asyncComponent(() => import('@/views/ProductsView.vue'), 'ProductsView'),
      meta: { requiresAuth: true, permissions: ['products.view'] }
    },
    {
      path: '/users',
      name: 'users',
      component: asyncComponent(() => import('@/views/UsersView.vue'), 'UsersView'),
      meta: { requiresAuth: true, permissions: ['users.manage'] }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: asyncComponent(() => import('@/views/NotFoundView.vue'), 'NotFoundView')
    }
  ]
})

router.beforeEach((to, from, next) => {
  const startTime = performance.now();
  logger.log(`导航请求: 从 "${from.fullPath}" 到 "${to.fullPath}"`);
  logger.log(`目标路由信息:`, {
    name: to.name,
    path: to.path,
    params: to.params,
    query: to.query,
    meta: to.meta
  });
  
  const userStore = useUserStore()
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth !== false) {
    logger.log(`路由 "${to.path}" 需要认证`);
    
    // 如果用户未登录，重定向到登录页面
    if (!userStore.isLoggedIn()) {
      logger.log(`用户未登录，重定向到登录页面`);
      next({ name: 'login', query: { redirect: to.fullPath } });
      return;
    }
    
    logger.log(`用户已登录，检查权限`);
    
    // 检查权限
    const requiredPermissions = to.meta.permissions as string[] | undefined;
    if (requiredPermissions && requiredPermissions.length > 0) {
      logger.log(`路由 "${to.path}" 需要权限:`, requiredPermissions);
      
      const hasPermission = requiredPermissions.every(permission => 
        userStore.hasPermission(permission)
      );
      
      if (!hasPermission) {
        logger.log(`用户缺少所需权限，重定向到仪表板`);
        next({ name: 'dashboard' });
        return;
      }
      
      logger.log(`用户拥有所需权限`);
    }
  } else {
    logger.log(`路由 "${to.path}" 不需要认证`);
  }
  
  // 如果用户已登录并尝试访问登录页面，重定向到首页
  if (to.name === 'login' && userStore.isLoggedIn()) {
    logger.log(`已登录用户尝试访问登录页面，重定向到仪表板`);
    next({ name: 'dashboard' });
    return;
  }
  
  logger.log(`允许导航到 "${to.path}"`);
  
  // 记录路由处理耗时
  const endTime = performance.now();
  logger.log(`路由守卫处理时间: ${Math.round(endTime - startTime)}ms`);
  
  next();
})

router.afterEach((to, from) => {
  logger.log(`导航完成: 从 "${from.fullPath}" 到 "${to.fullPath}"`);
  
  // 检查并记录 URL 中的参数
  if (Object.keys(to.query).length > 0) {
    logger.log(`URL查询参数:`, to.query);
  }
  if (Object.keys(to.params).length > 0) {
    logger.log(`URL路径参数:`, to.params);
  }
  
  // 记录页面导航耗时
  if (window.performance) {
    const navTiming = window.performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navTiming) {
      logger.log(`页面加载性能:`, {
        domComplete: Math.round(navTiming.domComplete),
        loadEventEnd: Math.round(navTiming.loadEventEnd),
        domContentLoadedEventEnd: Math.round(navTiming.domContentLoadedEventEnd),
        duration: Math.round(navTiming.duration)
      });
    }
  }
})

router.onError((error) => {
  logger.error(`路由错误:`, error);
  
  // 添加更详细的错误信息
  if (error instanceof Error) {
    logger.error('错误堆栈:', error.stack);
    
    // 尝试诊断常见错误
    if (error.message.includes('Failed to fetch dynamically imported module')) {
      logger.error('组件加载失败，可能是网络问题或文件不存在');
    } else if (error.message.includes('Cannot find module')) {
      logger.error('模块未找到，请检查导入路径是否正确');
    } else if (error.message.includes('Unexpected token')) {
      logger.error('代码语法错误，请检查组件代码');
    }
  }
})

export default router