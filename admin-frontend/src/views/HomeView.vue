<template>
  <div class="home-container">
    <MainLayout>
      <h1>欢迎使用产品管理系统</h1>
      <p>这是一个基于Vue 3 + TypeScript的示例项目</p>
    </MainLayout>
  </div>
</template>

<script setup lang="ts">
import MainLayout from '@/components/layout/MainLayout.vue'
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}
</style> 