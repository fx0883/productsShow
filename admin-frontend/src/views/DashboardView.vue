<template>
  <div class="dashboard-container">
    <h1>仪表盘</h1>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>产品统计</span>
              <el-button type="text" @click="$router.push('/products')">查看详情</el-button>
            </div>
          </template>
          <div class="card-content">
            <el-statistic title="总产品数" :value="statistics.totalProducts" />
            <div class="stat-details">
              <div class="stat-item">
                <span>已发布</span>
                <el-tag type="success">{{ statistics.publishedProducts }}</el-tag>
              </div>
              <div class="stat-item">
                <span>草稿</span>
                <el-tag type="info">{{ statistics.draftProducts }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>用户统计</span>
              <el-button type="text" @click="$router.push('/users')">查看详情</el-button>
            </div>
          </template>
          <div class="card-content">
            <el-statistic title="总用户数" :value="statistics.totalUsers" />
            <div class="stat-details">
              <div class="stat-item">
                <span>管理员</span>
                <el-tag type="warning">{{ statistics.adminUsers }}</el-tag>
              </div>
              <div class="stat-item">
                <span>普通用户</span>
                <el-tag type="info">{{ statistics.regularUsers }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="card-content">
            <el-statistic title="系统运行时间" value="30天" />
            <div class="stat-details">
              <div class="stat-item">
                <span>CPU使用率</span>
                <el-progress :percentage="statistics.cpuUsage" />
              </div>
              <div class="stat-item">
                <span>内存使用率</span>
                <el-progress :percentage="statistics.memoryUsage" :color="memoryProgressColor" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/products?action=add')">
              添加产品
            </el-button>
            <el-button type="success" @click="$router.push('/users?action=add')">
              添加用户
            </el-button>
            <el-button @click="$router.push('/profile')">
              修改个人信息
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 模拟统计数据
const statistics = ref({
  totalProducts: 26,
  publishedProducts: 18,
  draftProducts: 8,
  totalUsers: 12,
  adminUsers: 3,
  regularUsers: 9,
  cpuUsage: 35,
  memoryUsage: 68
})

// 内存使用颜色
const memoryProgressColor = computed(() => {
  const memUsage = statistics.value.memoryUsage
  if (memUsage < 50) return '#67c23a'
  if (memUsage < 80) return '#e6a23c'
  return '#f56c6c'
})

// 模拟最近活动
const recentActivities = ref([
  {
    content: '管理员 admin 添加了新产品 "智能手表 W3"',
    time: '2023-07-18 14:30',
    type: 'primary'
  },
  {
    content: '用户 user1 更新了自己的个人信息',
    time: '2023-07-18 13:25',
    type: 'info'
  },
  {
    content: '管理员 admin 删除了产品 "过时产品"',
    time: '2023-07-18 11:40',
    type: 'danger'
  },
  {
    content: '管理员 admin2 添加了新用户 "市场部门"',
    time: '2023-07-18 10:15',
    type: 'success'
  },
  {
    content: '系统自动备份完成',
    time: '2023-07-18 01:00',
    type: 'info'
  }
])
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-actions .el-button {
  margin-left: 0;
}
</style> 