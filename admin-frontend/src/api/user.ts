import request from './request'
import type { UserInfo, LoginResponse } from '../types/api'

// 用户登录
export const login = (data: {
  username: string
  password: string
}): Promise<LoginResponse> => {
  return request({
    url: '/users/login/',
    method: 'post',
    data
  })
}

// 刷新令牌
export const refreshToken = (data: {
  refresh_token: string
}): Promise<{ token: string; refresh_token: string; expires_in: number }> => {
  return request({
    url: '/users/token/refresh/',
    method: 'post',
    data
  })
}

// 获取用户列表
export const getUserList = (params: {
  page?: number
  per_page?: number
  search?: string
  role?: string
}): Promise<UserInfo[]> => {
  return request({
    url: '/users/',
    method: 'get',
    params
  })
}

// 获取单个用户信息
export const getUserInfo = (id: number): Promise<UserInfo> => {
  return request({
    url: `/users/${id}/`,
    method: 'get'
  })
}

// 创建用户
export const createUser = (data: {
  username: string
  email: string
  password: string
  is_admin?: boolean
  is_member?: boolean
  phone?: string
  nick_name?: string
}): Promise<UserInfo> => {
  return request({
    url: '/users/',
    method: 'post',
    data
  })
}

// 更新用户
export const updateUser = (id: number, data: {
  username?: string
  email?: string
  password?: string
  is_admin?: boolean
  is_member?: boolean
  phone?: string
  nick_name?: string
}): Promise<UserInfo> => {
  return request({
    url: `/users/${id}/`,
    method: 'put',
    data
  })
}

// 删除用户
export const deleteUser = (id: number): Promise<void> => {
  return request({
    url: `/users/${id}/`,
    method: 'delete'
  })
}

// 获取当前用户信息
export const getCurrentUser = (): Promise<UserInfo> => {
  return request({
    url: '/users/profile/',
    method: 'get'
  })
}

// 更新当前用户信息
export const updateCurrentUser = (data: {
  username?: string
  email?: string
  password?: string
  phone?: string
  nick_name?: string
  preferred_language?: string
}): Promise<UserInfo> => {
  return request({
    url: '/users/profile/',
    method: 'put',
    data
  })
}

// 修改密码
export const changePassword = (data: {
  old_password: string
  new_password: string
}): Promise<{ message: string }> => {
  return request({
    url: '/users/change-password/',
    method: 'post',
    data
  })
}

// 登出
export const logout = (): Promise<void> => {
  return request({
    url: '/users/logout/',
    method: 'post'
  })
} 