<template>
  <div class="products-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>产品管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增产品
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="产品名称">
          <el-input v-model="searchForm.name" placeholder="请输入产品名称" clearable />
        </el-form-item>
        <el-form-item label="SKU">
          <el-input v-model="searchForm.sku" placeholder="请输入SKU" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="回收站" value="trash" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="请选择类型" clearable>
            <el-option label="简单产品" value="simple" />
            <el-option label="变体产品" value="variable" />
            <el-option label="组合产品" value="grouped" />
            <el-option label="外部产品" value="external" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="产品名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            {{ row.price ? `¥${row.price}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="80" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="success" link @click="handleView(row)">
              <el-icon><View /></el-icon>查看
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 产品表单对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productFormRules"
        label-width="100px"
      >
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-form-item label="产品名称" prop="name">
              <el-input v-model="productForm.name" placeholder="请输入产品名称" />
            </el-form-item>
            <el-form-item label="SKU" prop="sku">
              <el-input v-model="productForm.sku" placeholder="请输入SKU编码" />
            </el-form-item>
            <el-form-item label="类型" prop="type">
              <el-select v-model="productForm.type" placeholder="请选择产品类型">
                <el-option label="简单产品" value="simple" />
                <el-option label="变体产品" value="variable" />
                <el-option label="组合产品" value="grouped" />
                <el-option label="外部产品" value="external" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态" prop="status">
              <el-select v-model="productForm.status" placeholder="请选择产品状态">
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
                <el-option label="回收站" value="trash" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否精选">
              <el-switch v-model="productForm.featured" />
            </el-form-item>
            <el-form-item label="简短描述">
              <el-input v-model="productForm.short_description" type="textarea" rows="3" />
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="价格与库存" name="price">
            <el-form-item label="价格" prop="price">
              <el-input-number v-model="productForm.price" :precision="2" :min="0" />
            </el-form-item>
            <el-form-item label="原价">
              <el-input-number v-model="productForm.regular_price" :precision="2" :min="0" />
            </el-form-item>
            <el-form-item label="促销价">
              <el-input-number v-model="productForm.sale_price" :precision="2" :min="0" />
            </el-form-item>
            <el-form-item label="库存数量">
              <el-input-number v-model="productForm.stock_quantity" :min="0" :precision="0" />
            </el-form-item>
            <el-form-item label="库存状态">
              <el-select v-model="productForm.stock_status">
                <el-option label="有库存" value="instock" />
                <el-option label="缺货" value="outofstock" />
                <el-option label="预订" value="onbackorder" />
              </el-select>
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="详细描述" name="description">
            <el-form-item label="详细描述">
              <el-input v-model="productForm.description" type="textarea" rows="10" />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Refresh, Edit, Delete, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 模拟产品数据
const mockProducts = [
  {
    id: 1,
    name: '智能手机 X1',
    sku: 'PHN-X1-BLK',
    price: 2999.00,
    regular_price: 3299.00,
    sale_price: 2999.00,
    stock_quantity: 200,
    type: 'simple',
    status: 'published',
    featured: true,
    short_description: '高性能智能手机，6.5英寸全面屏，8GB+128GB',
    description: '这是一款高性能智能手机，采用6.5英寸全面屏设计，搭载高通骁龙处理器，8GB内存+128GB存储，4800万像素四摄，支持5G网络。',
    created_at: '2023-04-15 10:23:45'
  },
  {
    id: 2,
    name: '蓝牙耳机 B2',
    sku: 'AUD-B2-WHT',
    price: 399.00,
    regular_price: 499.00,
    sale_price: 399.00,
    stock_quantity: 350,
    type: 'simple',
    status: 'published',
    featured: false,
    short_description: '无线蓝牙耳机，降噪，续航20小时',
    description: '无线蓝牙耳机，支持主动降噪，单次充电可续航20小时，IPX5防水，支持触控操作。',
    created_at: '2023-04-16 14:30:22'
  },
  {
    id: 3,
    name: '智能手表 W3',
    sku: 'WCH-W3-SLV',
    price: 899.00,
    regular_price: 999.00,
    sale_price: 899.00,
    stock_quantity: 120,
    type: 'variable',
    status: 'published',
    featured: true,
    short_description: '智能手表，心率监测，多种运动模式',
    description: '智能手表，支持心率监测、血氧监测、睡眠监测，内置GPS，支持50+种运动模式，防水深度50米，续航时间7天。',
    created_at: '2023-04-17 09:15:33'
  },
  {
    id: 4,
    name: '笔记本电脑 L5',
    sku: 'LPT-L5-GRY',
    price: 5999.00,
    regular_price: 6299.00,
    sale_price: 5999.00,
    stock_quantity: 80,
    type: 'simple',
    status: 'published',
    featured: false,
    short_description: '15.6英寸笔记本，16GB内存，512GB SSD',
    description: '15.6英寸高清屏幕笔记本电脑，搭载最新一代处理器，16GB内存，512GB固态硬盘，独立显卡，轻薄金属机身，长续航。',
    created_at: '2023-04-18 16:45:11'
  },
  {
    id: 5,
    name: '平板电脑 T2',
    sku: 'TAB-T2-BLK',
    price: 1999.00,
    regular_price: 2199.00,
    sale_price: 1999.00,
    stock_quantity: 0,
    type: 'simple',
    status: 'draft',
    featured: false,
    short_description: '10.8英寸平板，8GB内存，128GB存储',
    description: '10.8英寸2K屏幕平板电脑，8GB内存，128GB存储，支持5G网络，搭载高性能处理器，支持手写笔，长达12小时续航。',
    created_at: '2023-04-19 11:20:45'
  }
];

// 搜索表单
const searchForm = reactive({
  name: '',
  sku: '',
  status: '',
  type: ''
})

// 表格数据
const tableData = ref(mockProducts)
const loading = ref(false)
const submitLoading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(mockProducts.length)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add')
const dialogTitle = ref('新增产品')
const productFormRef = ref<FormInstance>()
const activeTab = ref('basic')

// 产品表单
const productForm = reactive({
  id: 0,
  name: '',
  sku: '',
  price: 0,
  regular_price: 0,
  sale_price: 0,
  stock_quantity: 0,
  type: 'simple',
  status: 'draft',
  featured: false,
  stock_status: 'instock',
  short_description: '',
  description: ''
})

// 表单验证规则
const productFormRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  sku: [{ required: true, message: '请输入SKU编码', trigger: 'blur' }],
  type: [{ required: true, message: '请选择产品类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择产品状态', trigger: 'change' }],
  price: [{ required: true, message: '请输入产品价格', trigger: 'blur' }]
})

// 初始化
onMounted(() => {
  fetchProductList()
})

// 获取产品列表（模拟）
const fetchProductList = () => {
  loading.value = true
  
  setTimeout(() => {
    // 筛选条件
    let filteredData = [...mockProducts]
    
    if (searchForm.name) {
      filteredData = filteredData.filter(item => 
        item.name.toLowerCase().includes(searchForm.name.toLowerCase())
      )
    }
    
    if (searchForm.sku) {
      filteredData = filteredData.filter(item => 
        item.sku.toLowerCase().includes(searchForm.sku.toLowerCase())
      )
    }
    
    if (searchForm.status) {
      filteredData = filteredData.filter(item => item.status === searchForm.status)
    }
    
    if (searchForm.type) {
      filteredData = filteredData.filter(item => item.type === searchForm.type)
    }
    
    // 分页处理
    total.value = filteredData.length
    const startIdx = (currentPage.value - 1) * pageSize.value
    const endIdx = startIdx + pageSize.value
    tableData.value = filteredData.slice(startIdx, endIdx)
    
    loading.value = false
  }, 500)
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchProductList()
}

// 重置搜索
const handleReset = () => {
  searchForm.name = ''
  searchForm.sku = ''
  searchForm.status = ''
  searchForm.type = ''
  handleSearch()
}

// 分页方法
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchProductList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchProductList()
}

// 新增产品
const handleAdd = () => {
  dialogType.value = 'add'
  dialogTitle.value = '新增产品'
  dialogVisible.value = true
  activeTab.value = 'basic'
  
  // 重置表单
  Object.assign(productForm, {
    id: 0,
    name: '',
    sku: '',
    price: 0,
    regular_price: 0,
    sale_price: 0,
    stock_quantity: 0,
    type: 'simple',
    status: 'draft',
    featured: false,
    stock_status: 'instock',
    short_description: '',
    description: ''
  })
}

// 编辑产品
const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  dialogTitle.value = '编辑产品'
  dialogVisible.value = true
  activeTab.value = 'basic'
  
  // 填充表单
  Object.assign(productForm, { ...row })
}

// 查看产品
const handleView = (row: any) => {
  ElMessageBox.alert(`
    <h3>${row.name}</h3>
    <p><strong>SKU:</strong> ${row.sku}</p>
    <p><strong>价格:</strong> ¥${row.price}</p>
    <p><strong>库存:</strong> ${row.stock_quantity}</p>
    <p><strong>描述:</strong> ${row.short_description}</p>
    <p>${row.description}</p>
  `, '产品详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '关闭'
  })
}

// 删除产品
const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该产品吗？该操作不可恢复！', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 模拟删除
    const index = mockProducts.findIndex(item => item.id === row.id)
    if (index !== -1) {
      mockProducts.splice(index, 1)
      ElMessage.success('删除成功')
      fetchProductList()
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!productFormRef.value) return
  
  try {
    await productFormRef.value.validate()
    submitLoading.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (dialogType.value === 'add') {
      // 模拟新增
      const newProduct = {
        ...productForm,
        id: mockProducts.length + 1,
        created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
      }
      mockProducts.push(newProduct)
      ElMessage.success('添加产品成功')
    } else {
      // 模拟编辑
      const index = mockProducts.findIndex(item => item.id === productForm.id)
      if (index !== -1) {
        mockProducts[index] = { ...mockProducts[index], ...productForm }
        ElMessage.success('更新产品成功')
      }
    }
    
    dialogVisible.value = false
    fetchProductList()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  if (productFormRef.value) {
    productFormRef.value.resetFields()
  }
}

// 辅助函数 - 获取类型标签样式
const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    simple: '',
    variable: 'success',
    grouped: 'warning',
    external: 'info'
  }
  return map[type] || ''
}

// 辅助函数 - 获取类型显示文本
const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    simple: '简单产品',
    variable: '变体产品',
    grouped: '组合产品',
    external: '外部产品'
  }
  return map[type] || type
}

// 辅助函数 - 获取状态标签样式
const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    published: 'success',
    draft: 'info',
    trash: 'danger'
  }
  return map[status] || ''
}

// 辅助函数 - 获取状态显示文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    published: '已发布',
    draft: '草稿',
    trash: '回收站'
  }
  return map[status] || status
}
</script>

<style scoped>
.products-container {
  min-height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 