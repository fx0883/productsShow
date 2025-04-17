import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getTenantList, getTenantInfo, switchTenant } from '../api/tenant'
import type { Tenant, TenantQuota } from '../types/api'

export const useTenantStore = defineStore('tenant', () => {
  // 状态
  const currentTenant = ref<Tenant | null>(null)
  const tenantList = ref<Tenant[]>([])
  const loading = ref<boolean>(false)

  // 获取租户列表
  const fetchTenantList = async (params = {}) => {
    try {
      loading.value = true
      const data = await getTenantList(params)
      tenantList.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  // 获取租户详情
  const fetchTenantInfo = async (id: number) => {
    try {
      loading.value = true
      const data = await getTenantInfo(id)
      return data
    } finally {
      loading.value = false
    }
  }

  // 切换当前租户
  const switchCurrentTenant = async (id: number) => {
    try {
      loading.value = true
      await switchTenant(id)
      // 切换成功后，获取新租户信息
      const tenantInfo = await getTenantInfo(id)
      currentTenant.value = tenantInfo
      return tenantInfo
    } finally {
      loading.value = false
    }
  }

  // 设置当前租户
  const setCurrentTenant = (tenant: Tenant) => {
    currentTenant.value = tenant
  }

  return {
    currentTenant,
    tenantList,
    loading,
    fetchTenantList,
    fetchTenantInfo,
    switchCurrentTenant,
    setCurrentTenant
  }
}) 