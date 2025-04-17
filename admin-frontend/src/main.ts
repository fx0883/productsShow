import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import './style.css'
import App from './App.vue'

// 添加全局错误处理
const handleError = (error: any, instance: any, info: string) => {
  console.error(`[Global Error ${new Date().toISOString()}] 错误信息:`, error);
  console.error(`[Global Error ${new Date().toISOString()}] 组件:`, instance);
  console.error(`[Global Error ${new Date().toISOString()}] 信息:`, info);
};

// 添加性能检测
const reportPerformance = () => {
  if (window.performance) {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    console.log(`[Performance ${new Date().toISOString()}] 页面加载时间: ${pageLoadTime}ms`);
    
    // 输出资源加载时间
    console.log(`[Performance ${new Date().toISOString()}] 资源加载详情:`);
    window.performance.getEntriesByType('resource').forEach(resource => {
      const resourcePerf = resource as PerformanceResourceTiming;
      console.log(`[Resource ${new Date().toISOString()}] ${resourcePerf.name} - 加载时间: ${Math.round(resourcePerf.duration)}ms`);
    });
  }
};

// 等待页面完全加载后执行性能报告
window.addEventListener('load', reportPerformance);

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局错误处理
app.config.errorHandler = handleError;

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
