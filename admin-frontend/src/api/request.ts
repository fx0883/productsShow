import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // 后端API基础URL
  timeout: 15000 // 请求超时时间
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    
    // 如果有token则添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 处理API响应格式
    const { data } = response
    // 后端API返回格式：{ status: 'success', data: any, message: string }
    if (data.status === 'success') {
      // 直接返回data字段的内容，而不是整个响应对象
      return data.data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  (error) => {
    // 处理HTTP错误
    if (error.response) {
      const { status } = error.response
      
      switch (status) {
        case 400:
          ElMessage.error('请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请重新登录')
          // 清除token
          localStorage.removeItem('token')
          // 跳转到登录页
          router.push('/')
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(`连接错误 ${status}`)
      }
    } else {
      ElMessage.error('网络连接异常')
    }
    
    return Promise.reject(error)
  }
)

export default request 