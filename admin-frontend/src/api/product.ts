import request from './request'

// 获取产品列表
export const getProductList = (params: {
  page?: number
  per_page?: number
  sort?: string
  order?: string
  search?: string
  type?: string
  status?: string
  category?: number
  min_price?: number
  max_price?: number
  featured?: boolean
}) => {
  return request({
    url: '/products',
    method: 'get',
    params
  })
}

// 获取产品详情
export const getProductDetail = (id: number) => {
  return request({
    url: `/products/${id}`,
    method: 'get'
  })
}

// 创建产品
export const createProduct = (data: {
  name: string
  slug?: string
  sku: string
  type: string
  status: string
  featured?: boolean
  description?: string
  short_description?: string
  regular_price?: number
  sale_price?: number
  stock_quantity?: number
  categories?: number[]
  images?: Array<{
    image: string
    alt_text?: string
    is_featured?: boolean
  }>
}) => {
  return request({
    url: '/products',
    method: 'post',
    data
  })
}

// 更新产品
export const updateProduct = (id: number, data: {
  name?: string
  slug?: string
  sku?: string
  type?: string
  status?: string
  featured?: boolean
  description?: string
  short_description?: string
  regular_price?: number
  sale_price?: number
  stock_quantity?: number
  categories?: number[]
  images?: Array<{
    image: string
    alt_text?: string
    is_featured?: boolean
  }>
}) => {
  return request({
    url: `/products/${id}`,
    method: 'put',
    data
  })
}

// 删除产品
export const deleteProduct = (id: number) => {
  return request({
    url: `/products/${id}`,
    method: 'delete'
  })
}

// 批量处理产品
export const batchProducts = (data: {
  action: 'delete' | 'update' | 'trash' | 'restore'
  ids: number[]
  data?: any
}) => {
  return request({
    url: '/products/batch',
    method: 'post',
    data
  })
}

// 获取产品变体
export const getProductVariations = (productId: number) => {
  return request({
    url: `/products/${productId}/variations`,
    method: 'get'
  })
}

// 创建产品变体
export const createProductVariation = (productId: number, data: {
  sku: string
  regular_price?: number
  sale_price?: number
  stock_quantity?: number
  attributes: Array<{
    attribute_id: number
    value_id: number
  }>
}) => {
  return request({
    url: `/products/${productId}/variations`,
    method: 'post',
    data
  })
}

// 获取产品分类
export const getCategories = (params?: {
  page?: number
  per_page?: number
  parent?: number
  search?: string
}) => {
  return request({
    url: '/categories',
    method: 'get',
    params
  })
}

// 获取产品属性
export const getAttributes = () => {
  return request({
    url: '/attributes',
    method: 'get'
  })
}

// 获取属性值
export const getAttributeValues = (attributeId: number) => {
  return request({
    url: `/attributes/${attributeId}/values`,
    method: 'get'
  })
} 