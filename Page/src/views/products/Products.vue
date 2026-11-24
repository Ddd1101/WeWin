<template>
  <div class="products">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">商品管理</span>
          <div class="header-actions">
            <el-button v-if="selectedIds.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedIds.length }})
            </el-button>
            <el-button
              v-if="activeTab === 'finished'"
              type="success"
              @click="handleExportProducts"
              :loading="exportLoading"
            >
              <el-icon><Download /></el-icon>
              导出明细
            </el-button>
            <el-button v-if="activeTab !== 'children_clothing_costs'" type="primary" @click="handleAddProduct">
              <el-icon><Plus /></el-icon>
              添加商品
            </el-button>
          </div>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="product-tabs">
        <el-tab-pane label="手串成品" name="finished">
          <template #label>
            <span class="tab-label">
              <el-icon><Grid /></el-icon>
              手串成品
            </span>
          </template>
        </el-tab-pane>

        <el-tab-pane label="串珠" name="bead">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleCheck /></el-icon>
              串珠
            </span>
          </template>
        </el-tab-pane>

        <el-tab-pane label="手串配件" name="accessory">
          <template #label>
            <span class="tab-label">
              <el-icon><Box /></el-icon>
              手串配件
            </span>
          </template>
        </el-tab-pane>

        <el-tab-pane label="童装" name="children_clothing">
          <template #label>
            <span class="tab-label">
              <el-icon><ShoppingBag /></el-icon>
              童装
            </span>
          </template>
        </el-tab-pane>

        <el-tab-pane label="童装成本表" name="children_clothing_costs">
          <template #label>
            <span class="tab-label">
              <el-icon><Coin /></el-icon>
              童装成本表
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <ChildrenClothingCosts v-if="activeTab === 'children_clothing_costs'" />

      <template v-else>
        <ProductTable
          :key="activeTab"
          :products="products"
          :loading="loading"
          :selected-ids="selectedIds"
          :hide-product-type="activeTab === 'finished'"
          @select="handleSelect"
          @select-all="handleSelectAll"
          @edit="handleEditProduct"
          @delete="handleDeleteProduct"
          @sort-change="handleSortChange"
        />

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :layout="isMobile ? 'total, prev, pager, next' : 'total, sizes, prev, pager, next, jumper'"
            :total="pagination.total"
            :small="isMobile"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </template>
    </el-card>
    
    <ProductFormDialog
      v-model="dialogVisible"
      :product-type="addProductType"
      :edit-data="editData"
      :is-mobile="isMobile"
      @saved="fetchProducts"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, defineAsyncComponent, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Grid, CircleCheck, Box, ShoppingBag, Coin, Download } from '@element-plus/icons-vue'
import { getProducts, deleteProduct, getProductDetail } from '@/api'
import { exportFinishedProducts } from '@/utils/exportProducts'
import ProductFormDialog from './ProductFormDialog.vue'

// 产品表格组件
const ProductTable = defineAsyncComponent(() => import('../components/ProductTable.vue'))
// 童装成本表组件
const ChildrenClothingCosts = defineAsyncComponent(() => import('../ChildrenClothingCosts.vue'))

// 手机端检测
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 商品列表
const products = ref([])
// 选中的ID
const selectedIds = ref([])
// 加载状态
const loading = ref(false)
const submitLoading = ref(false)
const exportLoading = ref(false)
// 筛选表单
const filterForm = reactive({
  product_type: '',
  is_active: ''
})
// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 50,
  total: 0
})
// 对话框状态
const dialogVisible = ref(false)
const editData = ref(null)
const addProductType = ref('')
// 当前选中的标签页
const activeTab = ref('finished')
// 排序状态
const sortState = reactive({
  prop: '',
  order: ''
})

// 获取商品列表
const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    // 使用当前标签页作为商品类型筛选
    params.product_type = activeTab.value
    if (filterForm.is_active !== '') {
      params.is_active = filterForm.is_active
    }
    // 排序参数
    if (sortState.prop && sortState.order) {
      const prefix = sortState.order === 'descending' ? '-' : ''
      params.ordering = `${prefix}${sortState.prop}`
    }
    const response = await getProducts(params)
    products.value = response.data.products
    pagination.total = response.data.total_count
  } catch (error) {
    ElMessage.error('获取商品列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 导出成品明细
const handleExportProducts = async () => {
  exportLoading.value = true
  try {
    // 获取全量成品数据（不分页）
    const allProducts = []
    let page = 1
    const pageSize = 200
    while (true) {
      const response = await getProducts({
        product_type: 'finished',
        page,
        page_size: pageSize
      })
      allProducts.push(...response.data.products)
      if (allProducts.length >= response.data.total_count) break
      page++
    }
    if (allProducts.length === 0) {
      ElMessage.warning('没有可导出的成品数据')
      return
    }
    exportFinishedProducts(allProducts)
    ElMessage.success(`成功导出 ${allProducts.length} 个成品明细`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

// 监听标签页切换
const handleTabChange = () => {
  selectedIds.value = []
  pagination.currentPage = 1
  filterForm.is_active = ''
  sortState.prop = ''
  sortState.order = ''
  // 童装成本表不使用商品列表数据
  if (activeTab.value === 'children_clothing_costs') return
  fetchProducts()
}

// 处理排序变化
const handleSortChange = ({ prop, order }) => {
  sortState.prop = prop
  sortState.order = order
  pagination.currentPage = 1
  fetchProducts()
}

// 处理选择
const handleSelect = (id, checked) => {
  if (checked) {
    selectedIds.value.push(id)
  } else {
    const index = selectedIds.value.indexOf(id)
    if (index > -1) {
      selectedIds.value.splice(index, 1)
    }
  }
}

// 处理全选
const handleSelectAll = (ids) => {
  selectedIds.value = ids
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchProducts()
}

// 处理分页页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  fetchProducts()
}

// 处理添加商品
const handleAddProduct = () => {
  editData.value = null
  addProductType.value = activeTab.value
  dialogVisible.value = true
}

// 处理编辑商品
const handleEditProduct = async (row) => {
  try {
    const response = await getProductDetail(row.id)
    editData.value = response.data
    addProductType.value = ''
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取商品详情失败')
    console.error(error)
  }
}

// 处理删除商品
const handleDeleteProduct = (row) => {
  ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    submitLoading.value = true
    try {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      fetchProducts()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

// 批量删除
const handleBatchDelete = () => {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 个商品吗？`, '批量删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    submitLoading.value = true
    try {
      for (const id of selectedIds.value) {
        await deleteProduct(id)
      }
      ElMessage.success('批量删除成功')
      selectedIds.value = []
      fetchProducts()
    } catch (error) {
      ElMessage.error('批量删除失败')
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

// 初始化
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products {
  min-height: 100vh;
  background: linear-gradient(180deg, #f7f9fc 0%, #f0f4f8 100%);
  padding: 0;
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  border: none;
  margin: 24px 40px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.product-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.product-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 500;
}

.tab-label .el-icon {
  font-size: 18px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .products {
    padding: 0;
  }

  .main-card {
    margin: 8px;
    border-radius: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .tab-label {
    font-size: 13px;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
  }
}
</style>
