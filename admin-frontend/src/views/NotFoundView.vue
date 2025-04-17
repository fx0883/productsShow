<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>您访问的页面不存在或已被删除</p>
      <p class="path-info">请求路径: {{ $route.fullPath }}</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// 添加日志记录
const logDetails = () => {
  console.log(`[NotFound ${new Date().toISOString()}] 访问了不存在的页面: ${route.fullPath}`);
  console.log(`[NotFound ${new Date().toISOString()}] 路由信息:`, {
    path: route.path,
    fullPath: route.fullPath,
    name: route.name,
    params: route.params,
    query: route.query,
    hash: route.hash,
    meta: route.meta
  });
};

const goHome = () => {
  console.log(`[NotFound ${new Date().toISOString()}] 用户从404页面返回首页`);
  router.push('/');
};

onMounted(() => {
  logDetails();
});
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.not-found-content {
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 72px;
  color: #409eff;
  margin: 0;
  line-height: 1.2;
}

h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 20px;
}

p {
  color: #606266;
  margin-bottom: 20px;
}

.path-info {
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
  word-break: break-all;
}
</style> 