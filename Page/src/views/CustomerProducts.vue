<template>
  <div class="customer-products-page">
    <!-- 顶部导航栏 -->
    <div class="page-header">
      <div class="breadcrumb">
        <div class="breadcrumb-item" @click="goBack">
          <el-icon class="icon"><ArrowLeft /></el-icon>
          <span>客户管理</span>
        </div>
        <span class="separator">/</span>
        <div class="breadcrumb-item active">
          <span>商品管理</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" @click="handleAddProductRelation" class="add-btn">
          <el-icon><Plus /></el-icon>
          <span>添加商品</span>
        </el-button>
      </div>
    </div>

    <!-- 客户信息卡片 -->
    <div class="customer-info-card" v-if="customer">
      <div class="customer-main">
        <div class="avatar">
          {{ customer.name?.charAt(0)?.toUpperCase() || 'C' }}
        </div>
        <div class="info-content">
          <div class="name-row">
            <h1 class="customer-name">{{ customer.name }}</h1>
            <el-tag :type="customer.is_active ? 'success' : 'danger'" class="status-tag">
              {{ customer.is_active ? '活跃' : '停用' }}
            </el-tag>
          </div>
          <div class="detail-row">
            <div class="detail-item">
              <el-icon><User /></el-icon>
              <span>{{ customer.contact_name || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <el-icon><Phone /></el-icon>
              <span>{{ customer.phone || '未设置' }}</span>
            </div>
            <div class="detail-item" v-if="customer.email">
              <el-icon><Message /></el-icon>
              <span>{{ customer.email }}</span>
            </div>
            <div class="detail-item" v-if="customer.address">
              <el-icon><Location /></el-icon>
              <span>{{ customer.address }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <el-icon><Goods /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ customerProducts.length }}</div>
          <div class="stat-label">关联商品</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ totalPrice.toFixed(2) }}</div>
          <div class="stat-label">总报价</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ activeProductsCount }}</div>
          <div class="stat-label">在售商品</div>
        </div>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="content-card">
      <div class="card-header">
        <h3 class="card-title">商品列表</h3>
        <div class="card-actions">
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索商品..." 
            clearable
            class="search-input"
            prefix-icon="Search"
          />
        </div>
      </div>
      
      <el-table 
        :data="filteredProducts" 
        class="product-table"
        v-loading="loading"
        stripe
        :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: 600 }"
      >
        <el-table-column prop="product_code" label="商品编码" width="140">
          <template #default="{ row }">
            <span class="code-tag">{{ row.product_code }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品名称" min-width="220">
          <template #default="{ row }">
            <div class="product-name-cell">
              <span class="name">{{ row.product_name }}</span>
              <span class="type-badge" v-if="row.product_type_display">
                {{ row.product_type_display }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="客户报价" width="160">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" size="small">
              {{ row.is_active ? '在售' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="关联时间" width="180">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="handleEditProductRelation(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="warning" link size="small" @click="handleViewPriceHistory(row)">
                <el-icon><Clock /></el-icon>
                历史
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteProductRelation(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="filteredProducts.length === 0 && !loading" description="暂无商品关联" class="empty-state">
        <el-button type="primary" @click="handleAddProductRelation">
          <el-icon><Plus /></el-icon>
          添加第一个商品
        </el-button>
      </el-empty>
    </div>

    <!-- 添加/编辑商品关联对话框 -->
    <el-dialog
      v-model="addProductDialogVisible"
      :title="productRelationDialogTitle"
      width="520px"
      class="product-dialog"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="productForm" 
        :rules="productRules" 
        ref="productFormRef" 
        label-width="90px"
        class="product-form"
      >
        <el-form-item label="选择商品" prop="product_id">
          <el-select 
            v-model="productForm.product_id" 
            placeholder="请选择商品" 
            style="width: 100%;" 
            filterable
            clearable
            class="product-select"
          >
            <el-option
              v-for="product in allProducts"
              :key="product.id"
              :label="`${product.code} - ${product.name}`"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="客户报价" prop="price">
          <div class="price-input-wrapper">
            <span class="currency">¥</span>
            <el-input-number 
              v-model="productForm.price" 
              :min="0" 
              :precision="2" 
              :step="0.1"
              controls-position="right"
              class="price-input"
            />
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <div class="switch-wrapper">
            <el-switch 
              v-model="productForm.is_active" 
              active-text="在售" 
              inactive-text="下架"
              inline-prompt
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addProductDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleSubmitProductRelation" :loading="productSubmitLoading" size="large">
            确认保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报价历史对话框 -->
    <el-dialog
      v-model="priceHistoryDialogVisible"
      title="报价历史记录"
      width="680px"
      class="history-dialog"
    >
      <div class="history-header" v-if="currentProduct">
        <div class="product-info">
          <div class="info-code">{{ currentProduct.product_code }}</div>
          <div class="info-name">{{ currentProduct.product_name }}</div>
        </div>
        <div class="info-price">
          <span class="label">当前报价</span>
          <span class="price">¥{{ currentProduct.price.toFixed(2) }}</span>
        </div>
      </div>
      <div class="history-content">
        <div class="timeline" v-if="priceHistories.length > 0">
          <div v-for="(item, index) in priceHistories" :key="index" class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="history-row">
                <span class="history-price">¥{{ item.price.toFixed(2) }}</span>
                <span class="history-date">{{ formatDate(item.created_at) }}</span>
              </div>
              <div class="history-meta">
                <span class="meta-item">
                  <el-icon><User /></el-icon>
                  {{ item.created_by_name || '系统' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无报价历史" class="empty-history" />
      </div>
      <template #footer>
        <el-button @click="priceHistoryDialogVisible = false" size="large">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  ArrowLeft, 
  User, 
  Phone, 
  Message, 
  Location, 
  Goods, 
  Money, 
  CircleCheck,
  Edit,
  Delete,
  Clock,
  Search
} from '@element-plus/icons-vue'
import { 
  getCustomerDetail,
  getCustomerProducts,
  createOrUpdateCustomerProduct,
  getCustomerPriceHistory,
  getProducts as fetchAllProducts
} from '@/api'

const route = useRoute()
const router = useRouter()

// 客户ID
const customerId = ref(null)
// 客户信息
const customer = ref(null)
// 客户商品列表
const customerProducts = ref([])
// 所有商品列表
const allProducts = ref([])
// 搜索关键词
const searchKeyword = ref('')
// 加载状态
const loading = ref(false)
const productSubmitLoading = ref(false)
// 对话框状态
const addProductDialogVisible = ref(false)
const priceHistoryDialogVisible = ref(false)
const productRelationDialogTitle = ref('添加商品')
// 当前操作的商品
const currentProduct = ref(null)
// 报价历史
const priceHistories = ref([])
// 商品关联表单
const productForm = reactive({
  id: '',
  product_id: '',
  price: 0,
  is_active: true
})
// 表单验证规则
const productRules = {
  product_id: [{ required: true, message: '请选择商品', trigger: 'change' }],
  price: [{ required: true, message: '请输入报价', trigger: 'blur' }]
}
// 表单引用
const productFormRef = ref(null)

// 计算属性
const totalPrice = computed(() => {
  return customerProducts.value.reduce((sum, item) => sum + (item.price || 0), 0)
})

const activeProductsCount = computed(() => {
  return customerProducts.value.filter(item => item.is_active).length
})

const filteredProducts = computed(() => {
  if (!searchKeyword.value) return customerProducts.value
  const keyword = searchKeyword.value.toLowerCase()
  return customerProducts.value.filter(item => 
    item.product_code?.toLowerCase().includes(keyword) ||
    item.product_name?.toLowerCase().includes(keyword)
  )
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 返回客户列表
const goBack = () => {
  router.push('/customers/list')
}

// 获取客户详情
const fetchCustomerDetail = async () => {
  try {
    const response = await getCustomerDetail(customerId.value)
    customer.value = response.data
  } catch (error) {
    ElMessage.error('获取客户信息失败')
    console.error(error)
  }
}

// 获取客户商品列表
const fetchCustomerProducts = async () => {
  loading.value = true
  try {
    const response = await getCustomerProducts(customerId.value)
    customerProducts.value = response.data.customer_products || []
  } catch (error) {
    ElMessage.error('获取客户商品列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 获取所有商品
const fetchProducts = async () => {
  try {
    const response = await fetchAllProducts({ page_size: 1000 })
    allProducts.value = response.data.products || []
  } catch (error) {
    ElMessage.error('获取商品列表失败')
    console.error(error)
  }
}

// 处理添加商品关联
const handleAddProductRelation = () => {
  productRelationDialogTitle.value = '添加商品'
  Object.assign(productForm, {
    id: '',
    product_id: '',
    price: 0,
    is_active: true
  })
  fetchProducts()
  addProductDialogVisible.value = true
}

// 处理编辑商品关联
const handleEditProductRelation = (row) => {
  productRelationDialogTitle.value = '编辑商品'
  Object.assign(productForm, {
    id: row.id,
    product_id: row.product_id,
    price: row.price,
    is_active: row.is_active
  })
  fetchProducts()
  addProductDialogVisible.value = true
}

// 处理删除商品关联
const handleDeleteProductRelation = (row) => {
  ElMessageBox.confirm(
    `确定要移除商品「${row.product_name}」的关联吗？`, 
    '提示', 
    {
      confirmButtonText: '确定移除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'confirm-btn-danger'
    }
  ).then(async () => {
    productSubmitLoading.value = true
    try {
      ElMessage.success('移除成功')
      fetchCustomerProducts()
    } catch (error) {
      ElMessage.error('移除失败')
      console.error(error)
    } finally {
      productSubmitLoading.value = false
    }
  }).catch(() => {})
}

// 处理提交商品关联
const handleSubmitProductRelation = async () => {
  if (!productFormRef.value) return
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      productSubmitLoading.value = true
      try {
        await createOrUpdateCustomerProduct(customerId.value, productForm)
        ElMessage.success('保存成功')
        addProductDialogVisible.value = false
        fetchCustomerProducts()
      } catch (error) {
        ElMessage.error(error?.response?.data?.error || '操作失败')
        console.error(error?.response?.data || error)
      } finally {
        productSubmitLoading.value = false
      }
    }
  })
}

// 处理查看报价历史
const handleViewPriceHistory = async (row) => {
  currentProduct.value = row
  try {
    const response = await getCustomerPriceHistory(customerId.value, row.product_id)
    priceHistories.value = (response.data.price_histories || []).sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    )
    priceHistoryDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取报价历史失败')
    console.error(error)
  }
}

// 初始化
onMounted(() => {
  customerId.value = route.params.id
  if (customerId.value) {
    fetchCustomerDetail()
    fetchCustomerProducts()
  } else {
    ElMessage.error('客户ID不存在')
    goBack()
  }
})
</script>

<style scoped>
.customer-products-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4f8 0%, #e8eef3 100%);
  padding: 24px 32px;
}

/* 顶部导航 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #64748b;
  font-size: 14px;
  transition: all 0.3s ease;
}

.breadcrumb-item:hover {
  color: #667eea;
}

.breadcrumb-item.active {
  color: #1e293b;
  font-weight: 600;
  cursor: default;
}

.breadcrumb-item .icon {
  font-size: 16px;
}

.separator {
  color: #cbd5e1;
  font-size: 14px;
}

.add-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 10px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.35);
  transition: all 0.3s ease;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45);
}

/* 客户信息卡片 */
.customer-info-card {
  background: white;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.customer-main {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
}

.info-content {
  flex: 1;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.customer-name {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.3px;
}

.status-tag {
  padding: 6px 14px;
  font-weight: 600;
  font-size: 13px;
  border-radius: 20px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
}

.detail-item .el-icon {
  color: #94a3b8;
  font-size: 16px;
}

/* 统计卡片 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
  font-weight: 500;
}

/* 内容卡片 */
.content-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid #f1f5f9;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.search-input {
  width: 260px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 6px 16px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1 inset;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #667eea inset;
}

/* 表格 */
.product-table {
  padding: 0 28px 28px;
}

.product-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.code-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #f1f5f9;
  color: #475569;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
}

.product-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.name {
  font-weight: 600;
  color: #1e293b;
}

.type-badge {
  padding: 2px 8px;
  background: #f0f9ff;
  color: #0369a1;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.price-text {
  font-weight: 700;
  color: #667eea;
  font-size: 16px;
}

.date-text {
  color: #64748b;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.action-buttons .el-button {
  font-weight: 500;
}

.empty-state {
  padding: 60px 0;
}

/* 对话框 */
.product-dialog :deep(.el-dialog) {
  border-radius: 16px;
}

.product-dialog :deep(.el-dialog__header) {
  padding: 24px 28px 8px;
}

.product-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.product-dialog :deep(.el-dialog__body) {
  padding: 16px 28px 8px;
}

.product-form {
  padding: 8px 0;
}

.product-select :deep(.el-select__wrapper) {
  border-radius: 10px;
}

.price-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.currency {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.price-input {
  flex: 1;
}

.price-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 6px 12px;
}

.switch-wrapper {
  padding: 4px 0;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 8px 28px 24px;
}

/* 历史记录对话框 */
.history-dialog :deep(.el-dialog) {
  border-radius: 16px;
}

.history-dialog :deep(.el-dialog__header) {
  padding: 24px 28px 0;
}

.history-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.history-dialog :deep(.el-dialog__body) {
  padding: 20px 28px 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e8eef3 100%);
  border-radius: 12px;
  margin-bottom: 20px;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-code {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  font-family: 'SF Mono', Monaco, monospace;
}

.info-name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.info-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.info-price .label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.info-price .price {
  font-size: 24px;
  font-weight: 800;
  color: #667eea;
}

.history-content {
  max-height: 400px;
  overflow-y: auto;
}

.timeline {
  padding: 8px 0;
}

.timeline-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #667eea;
  margin-top: 6px;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
}

.history-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.history-price {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.history-date {
  font-size: 13px;
  color: #64748b;
}

.history-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #64748b;
}

.meta-item .el-icon {
  font-size: 14px;
  color: #94a3b8;
}

.empty-history {
  padding: 40px 0;
}

.history-dialog :deep(.el-dialog__footer) {
  padding: 20px 28px 24px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .customer-products-page {
    padding: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>
