import request from './request'
import type { Tenant, TenantQuota } from '../types/api'

// 获取租户列表
export const getTenantList = (params: {
  page?: number
  per_page?: number
  search?: string
  status?: string
}): Promise<Tenant[]> => {
  return request({
    url: '/common/tenants/',
    method: 'get',
    params
  })
}

// 获取单个租户信息
export const getTenantInfo = (id: number): Promise<Tenant> => {
  return request({
    url: `/common/tenants/${id}/`,
    method: 'get'
  })
}

// 创建租户
export const createTenant = (data: {
  name: string
  status?: string
}): Promise<Tenant> => {
  return request({
    url: '/common/tenants/',
    method: 'post',
    data
  })
}

// 更新租户
export const updateTenant = (id: number, data: {
  name?: string
  status?: string
}): Promise<Tenant> => {
  return request({
    url: `/common/tenants/${id}/`,
    method: 'put',
    data
  })
}

// 删除租户
export const deleteTenant = (id: number): Promise<void> => {
  return request({
    url: `/common/tenants/${id}/`,
    method: 'delete'
  })
}

// 获取租户配额
export const getTenantQuota = (tenantId: number): Promise<TenantQuota> => {
  return request({
    url: `/common/tenants/${tenantId}/quota/`,
    method: 'get'
  })
}

// 更新租户配额
export const updateTenantQuota = (tenantId: number, data: {
  max_users?: number
  max_admins?: number
  max_storage_mb?: number
  max_products?: number
}): Promise<TenantQuota> => {
  return request({
    url: `/common/tenants/${tenantId}/quota/`,
    method: 'put',
    data
  })
}

// 获取租户下的用户列表
export const getTenantUsers = (tenantId: number, params: {
  page?: number
  per_page?: number
  search?: string
  role?: string
}): Promise<any> => {
  return request({
    url: `/common/tenants/${tenantId}/users/`,
    method: 'get',
    params
  })
}

// 切换当前租户
export const switchTenant = (tenantId: number): Promise<{ message: string }> => {
  return request({
    url: '/common/tenants/switch/',
    method: 'post',
    data: { tenant_id: tenantId }
  })
} 