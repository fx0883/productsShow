// API响应类型
export interface ApiResponse<T> {
  status: string
  data: T
  message?: string
  pagination?: {
    page: number
    per_page: number
    total_pages: number
    total_items: number
  }
}

// 用户相关类型
export interface UserInfo {
  id: number
  username: string
  email: string
  is_admin: boolean
  is_member: boolean
  is_super_admin: boolean
  phone?: string
  nick_name?: string
  tenant?: {
    id: number
    name: string
  }
}

export interface LoginResponse {
  token: string
  refresh_token: string
  user: UserInfo
  expires_in: number
}

// 租户相关类型
export interface Tenant {
  id: number
  name: string
  status: string
  created_at: string
  updated_at: string
}

export interface TenantQuota {
  max_users: number
  max_admins: number
  max_storage_mb: number
  max_products: number
  current_storage_used_mb: number
} 