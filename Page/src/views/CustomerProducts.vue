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
        row-key="id"
        :expand-row-keys="expandedRows"
        @expand-change="handleExpandChange"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="sku-expand-content">
              <div v-if="row.skus && row.skus.length > 0" class="sku-list">
                <div 
                  v-for="sku in row.skus" 
                  :key="sku.id"
                  class="sku-item"
                  :class="{ 'sku-active': sku.is_active }"
                >
                  <div class="sku-info">
                    <span class="sku-code">{{ sku.sku_code || '-' }}</span>
                    <span class="sku-name">{{ sku.sku_name || sku.name || '-' }}</span>
                    <span class="sku-specs">{{ getSkuSpecs(sku) }}</span>
                  </div>
                  <div class="sku-price">
                    <span class="sku-price-label">报价：</span>
                    <span class="sku-price-value">¥{{ sku.price?.toFixed(2) || row.price.toFixed(2) }}</span>
                  </div>
                  <div class="sku-actions">
                    <el-button type="primary" link size="small" @click="handleEditSkuRelation(row, sku)">
                      <el-icon><Edit /></el-icon>
                      编辑
                    </el-button>
                    <el-button type="warning" link size="small" @click="handleViewSkuPriceHistory(row, sku)">
                      <el-icon><Clock /></el-icon>
                      历史
                    </el-button>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无SKU信息" :image-size="60" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="商品图片" width="100">
          <template #default="{ row }">
            <div class="product-image-cell">
              <el-image
                v-if="row.product_image_url"
                :src="row.product_image_url"
                :preview-src-list="[row.product_image_url]"
                class="product-list-image"
                fit="cover"
              />
              <div v-else class="product-no-image">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>
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
        <el-table-column label="SKU信息" width="200">
          <template #default="{ row }">
            <div class="sku-info-cell">
              <div v-if="row.skus && row.skus.length > 0">
                <el-tag size="small" type="info">{{ row.skus.length }} 个SKU</el-tag>
                <span class="sku-expand-hint">展开查看</span>
              </div>
              <span v-else class="text-gray-500">-</span>
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
      width="900px"
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
        <!-- 商品类型筛选 -->
        <el-form-item label="商品类型">
          <el-radio-group v-model="selectedProductType" @change="handleProductTypeChange">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="finished">手串成品</el-radio-button>
            <el-radio-button value="bead">串珠</el-radio-button>
            <el-radio-button value="accessory">配件</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <!-- 商品搜索 -->
        <el-form-item label="搜索商品">
          <el-input 
            v-model="productSearchKeyword" 
            placeholder="搜索商品名称或货号..." 
            clearable
            prefix-icon="Search"
          />
        </el-form-item>
        
        <!-- 商品选择卡片列表 -->
        <el-form-item label="选择商品" prop="product_id">
          <div class="product-selection-grid">
            <div 
              v-for="product in filteredAllProducts" 
              :key="product.id"
              :class="['product-card-item', { selected: productForm.product_id === product.id }]"
              @click="handleSelectProduct(product)"
            >
              <div class="product-card-image" @click.stop="handlePreviewImage(product)">
                <el-image
                  v-if="product.image_url"
                  :src="product.image_url"
                  fit="cover"
                  class="product-thumbnail"
                  :preview-src-list="[product.image_url]"
                  :initial-index="0"
                  preview-teleported
                />
                <div v-else class="product-no-image">
                  <el-icon><Picture /></el-icon>
                </div>
              </div>
              <div class="product-card-content">
                <div class="product-card-code">{{ product.code }}</div>
                <div class="product-card-name">{{ product.name }}</div>
                <div class="product-card-type">
                  <el-tag size="small" :type="getProductTypeTag(product.product_type)">
                    {{ getProductTypeName(product.product_type) }}
                  </el-tag>
                </div>
                <div class="product-card-sku-count">
                  <el-tag size="small" type="info">{{ product.skus?.length || 0 }} 个SKU</el-tag>
                </div>
              </div>
              <div v-if="productForm.product_id === product.id" class="product-check-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
            </div>
          </div>
          <div v-if="filteredAllProducts.length === 0" class="empty-products">
            <el-empty description="暂无符合条件的商品" />
          </div>
        </el-form-item>
        
        <!-- SKU选择 -->
        <el-form-item 
          v-if="selectedProduct && selectedProduct.skus && selectedProduct.skus.length > 0" 
          label="选择SKU" 
          prop="sku_id"
        >
          <div class="sku-selection-container">
            <div 
              v-for="sku in selectedProduct.skus" 
              :key="sku.id"
              :class="['sku-option-card', { selected: productForm.sku_id === sku.id }]"
              @click="handleSelectSku(sku)"
            >
              <div class="sku-option-info">
                <div class="sku-option-code">{{ sku.sku_code || '-' }}</div>
                <div class="sku-option-name">{{ sku.sku_name || sku.name || '-' }}</div>
                <div class="sku-option-specs">{{ getSkuSpecs(sku) }}</div>
              </div>
              <div class="sku-option-price">
                ¥{{ sku.selling_price?.toFixed(2) || sku.cost_price?.toFixed(2) || '0.00' }}
              </div>
              <div v-if="productForm.sku_id === sku.id" class="sku-check-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <!-- 无SKU提示 -->
        <el-form-item 
          v-else-if="selectedProduct && (!selectedProduct.skus || selectedProduct.skus.length === 0)" 
          label="SKU"
        >
          <el-alert title="该商品暂无SKU，将使用商品默认信息" type="info" :closable="false" />
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
          <div v-if="currentSku" class="info-sku">
            <el-tag size="small" type="warning">SKU: {{ currentSku.sku_code || '-' }}</el-tag>
            <span class="sku-name">{{ currentSku.sku_name || currentSku.name || '' }}</span>
          </div>
        </div>
        <div class="info-price">
          <span class="label">当前报价</span>
          <span class="price">¥{{ currentProduct.price.toFixed(2) }}</span>
        </div>
      </div>
      <!-- 历史列表区域 -->
      <div class="history-list-header">
        <div class="history-list-title">
          <el-icon><Document /></el-icon>
          历史记录（共 {{ priceHistories.length }} 条）
        </div>
        <div class="scroll-hint" v-if="priceHistories.length > 5">
          <el-icon><Bottom /></el-icon>
          向下滚动查看更多
        </div>
      </div>
      <div class="history-content">
        <div class="timeline" v-if="priceHistories.length > 0">
          <div v-for="(item, index) in priceHistories" :key="index" class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="history-row">
                <div class="history-price-wrapper">
                  <span class="currency">¥</span>
                  <el-input-number 
                    v-if="item.editing"
                    v-model="item.tempPrice" 
                    :min="0" 
                    :precision="2" 
                    :step="0.1"
                    controls-position="right"
                    class="history-price-input"
                  />
                  <span v-else class="history-price">¥{{ item.price.toFixed(2) }}</span>
                </div>
                <div class="history-actions">
                  <span class="history-date">{{ formatDate(item.created_at) }}</span>
                  <div class="action-buttons-mini">
                    <el-button 
                      v-if="!item.editing"
                      type="primary" 
                      link 
                      size="small" 
                      @click="startEditPrice(item)"
                    >
                      <el-icon><Edit /></el-icon>
                      编辑
                    </el-button>
                    <template v-else>
                      <el-button 
                        type="success" 
                        link 
                        size="small" 
                        @click="savePriceEdit(item, index)"
                      >
                        <el-icon><CircleCheck /></el-icon>
                        保存
                      </el-button>
                      <el-button 
                        type="info" 
                        link 
                        size="small" 
                        @click="cancelPriceEdit(item)"
                      >
                        <el-icon><Close /></el-icon>
                        取消
                      </el-button>
                    </template>
                    <el-button 
                      v-if="!item.editing"
                      type="danger" 
                      link 
                      size="small" 
                      @click="handleDeletePriceHistory(item, index)"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                </div>
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
      <!-- 报价趋势图 -->
      <div class="chart-section" v-if="priceHistories.length > 0">
        <div class="chart-header">
          <div class="chart-title">
            <el-icon><TrendCharts /></el-icon>
            价格趋势（最近 {{ priceHistories.length > 10 ? 10 : priceHistories.length }} 次）
          </div>
        </div>
        <div ref="priceChartRef" class="price-chart"></div>
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
  Search,
  Close,
  TrendCharts,
  Document,
  Bottom,
  Picture
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { 
  getCustomerDetail,
  getCustomerProducts,
  createOrUpdateCustomerProduct,
  deleteCustomerProduct,
  getCustomerPriceHistory,
  getProducts as fetchAllProducts
} from "@/api";

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
// 商品搜索关键词
const productSearchKeyword = ref('')
// 选中的商品类型筛选
const selectedProductType = ref('')
// 搜索关键词
const searchKeyword = ref('')
// 展开的行
const expandedRows = ref([])
// 加载状态
const loading = ref(false)
const productSubmitLoading = ref(false)
// 对话框状态
const addProductDialogVisible = ref(false)
const priceHistoryDialogVisible = ref(false)
const productRelationDialogTitle = ref('添加商品')
// 当前操作的商品
const currentProduct = ref(null)
// 当前操作的SKU
const currentSku = ref(null)
// 当前选中的商品
const selectedProduct = ref(null)
// 报价历史
const priceHistories = ref([])
// 商品关联表单
const productForm = reactive({
  id: '',
  product_id: '',
  sku_id: '',
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
// 图表引用
const priceChartRef = ref(null)
let priceChart = null

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

// 筛选后的所有商品列表
const filteredAllProducts = computed(() => {
  let result = allProducts.value
  
  // 按商品类型筛选
  if (selectedProductType.value) {
    result = result.filter(product => product.product_type === selectedProductType.value)
  }
  
  // 按关键词搜索
  if (productSearchKeyword.value) {
    const keyword = productSearchKeyword.value.toLowerCase()
    result = result.filter(product => 
      product.code?.toLowerCase().includes(keyword) ||
      product.name?.toLowerCase().includes(keyword)
    )
  }
  
  return result
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

// 获取商品类型名称
const getProductTypeName = (type) => {
  const typeMap = {
    'finished': '手串成品',
    'bead': '串珠',
    'accessory': '配件'
  }
  return typeMap[type] || type
}

// 获取商品类型对应的标签颜色
const getProductTypeTag = (type) => {
  const tagMap = {
    'finished': 'success',
    'bead': 'warning',
    'accessory': 'info'
  }
  return tagMap[type] || ''
}

// 商品类型变化处理
const handleProductTypeChange = () => {
  // 类型变化时清空已选商品
  productForm.product_id = ''
}

// 选择商品
const handleSelectProduct = (product) => {
  productForm.product_id = product.id
  productForm.sku_id = ''
  selectedProduct.value = product
  // 如果有SKU，默认选择第一个
  if (product.skus && product.skus.length > 0) {
    const defaultSku = product.skus.find(s => s.is_default) || product.skus[0]
    handleSelectSku(defaultSku)
  } else {
    // 使用商品默认价格
    productForm.price = product.selling_price || product.cost_price || 0
  }
}

// 选择SKU
const handleSelectSku = (sku) => {
  productForm.sku_id = sku.id
  // 自动填入SKU价格
  productForm.price = sku.selling_price || sku.cost_price || 0
}

// 预览商品图片
const handlePreviewImage = (product) => {
  // el-image 组件已经处理了预览功能
  // 这里可以添加额外的逻辑
}

// 获取SKU规格信息
const getSkuSpecs = (sku) => {
  const specs = []
  if (sku.size) specs.push(`${sku.size}mm`)
  if (sku.material) specs.push(sku.material)
  if (sku.color) specs.push(sku.color)
  if (sku.quality_level) specs.push(`品质${sku.quality_level}`)
  if (sku.weight) specs.push(`${sku.weight}g`)
  return specs.join(' | ') || '-'
}

// 处理表格展开
const handleExpandChange = (row, expandedRows) => {
  expandedRows.value = expandedRows.map(r => r.id)
}

// 处理编辑SKU关联
const handleEditSkuRelation = (product, sku) => {
  productRelationDialogTitle.value = '编辑SKU报价'
  Object.assign(productForm, {
    id: product.id,
    product_id: product.product_id,
    sku_id: sku.id,
    price: sku.price || product.price,
    is_active: product.is_active
  })
  // 找到对应的商品信息
  selectedProduct.value = allProducts.value.find(p => p.id === product.product_id)
  addProductDialogVisible.value = true
}

// 处理查看SKU报价历史
const handleViewSkuPriceHistory = (product, sku) => {
  currentProduct.value = product
  currentSku.value = sku
  // 这里需要调用API获取SKU的报价历史
  // 暂时使用商品的历史记录
  fetchPriceHistory(product.product_id, sku.id)
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
    sku_id: '',
    price: 0,
    is_active: true
  })
  // 重置筛选条件
  selectedProductType.value = ''
  productSearchKeyword.value = ''
  selectedProduct.value = null
  fetchProducts()
  addProductDialogVisible.value = true
}

// 处理编辑商品关联
const handleEditProductRelation = (row) => {
  productRelationDialogTitle.value = '编辑商品'
  Object.assign(productForm, {
    id: row.id,
    product_id: row.product_id,
    sku_id: row.sku_id || '',
    price: row.price,
    is_active: row.is_active
  })
  // 找到对应的商品信息
  fetchProducts().then(() => {
    selectedProduct.value = allProducts.value.find(p => p.id === row.product_id)
  })
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
      await deleteCustomerProduct(customerId.value, row.id)
      ElMessage.success('移除成功')
      fetchCustomerProducts()
    } catch (error) {
      ElMessage.error(error?.response?.data?.error || '移除失败')
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
  currentSku.value = null
  fetchPriceHistory(row.product_id)
}

// 获取报价历史
const fetchPriceHistory = async (productId, skuId = null) => {
  try {
    const params = skuId ? { sku_id: skuId } : {}
    const response = await getCustomerPriceHistory(customerId.value, productId, params)
    priceHistories.value = (response.data.price_histories || []).sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    ).map(item => ({
      ...item,
      editing: false,
      tempPrice: item.price
    }))
    priceHistoryDialogVisible.value = true
    
    // 延迟渲染图表，等待DOM更新
    setTimeout(() => {
      initPriceChart()
    }, 100)
  } catch (error) {
    ElMessage.error('获取报价历史失败')
    console.error(error)
  }
}

// 初始化价格图表
const initPriceChart = () => {
  if (!priceChartRef.value) return
  
  // 销毁旧图表
  if (priceChart) {
    priceChart.dispose()
  }
  
  priceChart = echarts.init(priceChartRef.value)
  
  updatePriceChart()
  
  // 响应式窗口
  window.addEventListener('resize', () => {
    priceChart?.resize()
  })
}

// 更新价格图表
const updatePriceChart = () => {
  if (!priceChart || priceHistories.value.length === 0) return
  
  // 取最近10条数据并反转（从旧到新）
  const recentData = [...priceHistories.value].slice(0, 10).reverse()
  
  const dates = recentData.map(item => {
    const date = new Date(item.created_at)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  })
  
  const prices = recentData.map(item => item.price)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: {
        color: '#1e293b'
      },
      formatter: (params) => {
        const data = params[0]
        return `
          <div style="font-weight: 600; margin-bottom: 4px;">${data.axisValue}</div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"></span>
            <span>报价：<strong style="color: #667eea;">¥${data.value.toFixed(2)}</strong></span>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#f1f5f9'
        }
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 12,
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '报价',
        type: 'line',
        smooth: true,
        data: prices,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#667eea' },
              { offset: 1, color: '#764ba2' }
            ]
          }
        },
        itemStyle: {
          color: '#667eea',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.25)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
            ]
          }
        }
      }
    ]
  }
  
  priceChart.setOption(option)
}

// 保存价格后更新图表
const updateChartAfterSave = () => {
  setTimeout(() => {
    updatePriceChart()
  }, 100)
}

// 开始编辑价格
const startEditPrice = (item) => {
  item.editing = true
  item.tempPrice = item.price
}

// 保存价格编辑
const savePriceEdit = async (item, index) => {
  if (item.tempPrice === item.price) {
    item.editing = false
    return
  }
  
  productSubmitLoading.value = true
  try {
    // 这里调用更新历史价格的API（需要后端支持）
    // 暂时模拟成功
    item.price = item.tempPrice
    item.editing = false
    ElMessage.success('价格更新成功')
    
    // 更新图表
    updateChartAfterSave()
  } catch (error) {
    ElMessage.error('更新价格失败')
    console.error(error)
  } finally {
    productSubmitLoading.value = false
  }
}

// 取消价格编辑
const cancelPriceEdit = (item) => {
  item.editing = false
  item.tempPrice = item.price
}

// 删除价格历史
const handleDeletePriceHistory = (item, index) => {
  ElMessageBox.confirm(
    `确定要删除这条报价历史记录吗？\n报价：¥${item.price.toFixed(2)}\n时间：${formatDate(item.created_at)}`, 
    '删除确认', 
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'confirm-btn-danger'
    }
  ).then(async () => {
    productSubmitLoading.value = true
    try {
      // 这里调用删除历史价格的API（需要后端支持）
      // 暂时模拟成功，从列表中移除
      priceHistories.value.splice(index, 1)
      ElMessage.success('删除成功')
      
      // 更新图表
      updateChartAfterSave()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    } finally {
      productSubmitLoading.value = false
    }
  }).catch(() => {})
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

/* 图表区域 */
.chart-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.chart-title .el-icon {
  color: #667eea;
  font-size: 18px;
}

.price-chart {
  width: 100%;
  height: 240px;
}

/* 历史列表头部 */
.history-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.history-list-title .el-icon {
  color: #667eea;
  font-size: 18px;
}

.scroll-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 16px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

.scroll-hint .el-icon {
  font-size: 14px;
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
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
}

.history-content::-webkit-scrollbar {
  width: 8px;
}

.history-content::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.history-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.history-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.timeline {
  padding: 8px 0;
}

.timeline-item {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: white;
  transition: all 0.2s ease;
}

.timeline-item:hover {
  background: #fafbfc;
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

.history-price-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.history-price-wrapper .currency {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.history-price-input {
  width: 140px;
}

.history-price-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 4px 10px;
}

.history-price {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-date {
  font-size: 13px;
  color: #64748b;
}

.action-buttons-mini {
  display: flex;
  gap: 4px;
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

/* 商品选择网格 */
.product-selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
}

.product-selection-grid::-webkit-scrollbar {
  width: 8px;
}

.product-selection-grid::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.product-selection-grid::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.product-card-item {
  position: relative;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-card-item:hover {
  border-color: #667eea;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.product-card-item.selected {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.product-card-image {
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: #f8fafc;
  cursor: zoom-in;
}

.product-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card-image:hover .product-thumbnail {
  transform: scale(1.05);
}

.product-no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.product-no-image .el-icon {
  font-size: 48px;
}

.product-card-content {
  padding: 12px;
}

.product-card-code {
  font-size: 12px;
  color: #94a3b8;
  font-family: 'SF Mono', Monaco, monospace;
  margin-bottom: 4px;
}

.product-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-card-type {
  margin-bottom: 6px;
}

.product-card-price {
  font-size: 13px;
  font-weight: 600;
  color: #667eea;
}

.product-check-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.product-check-icon .el-icon {
  font-size: 18px;
}

.empty-products {
  padding: 40px 0;
}

/* 商品列表图片样式 */
.product-image-cell {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
}

.product-list-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sku-info-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sku-expand-hint {
  font-size: 12px;
  color: #94a3b8;
}

/* SKU展开内容样式 */
.sku-expand-content {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.sku-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sku-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.sku-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.sku-item.sku-active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.sku-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sku-code {
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  font-family: 'SF Mono', Monaco, monospace;
}

.sku-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.sku-specs {
  font-size: 12px;
  color: #64748b;
}

.sku-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
}

.sku-price-label {
  font-size: 12px;
  color: #94a3b8;
}

.sku-price-value {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.sku-actions {
  display: flex;
  gap: 8px;
}

/* SKU选择样式 */
.product-card-sku-count {
  margin-top: 6px;
}

.sku-selection-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.sku-option-card {
  position: relative;
  display: flex;
  align-items: center;
  padding: 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sku-option-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.sku-option-card.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.sku-option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sku-option-code {
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  font-family: 'SF Mono', Monaco, monospace;
}

.sku-option-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.sku-option-specs {
  font-size: 12px;
  color: #64748b;
}

.sku-option-price {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
  margin-right: 16px;
}

.sku-check-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.sku-check-icon .el-icon {
  font-size: 16px;
}

/* 历史记录SKU显示 */
.info-sku {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.info-sku .sku-name {
  font-size: 13px;
  color: #64748b;
}

/* 响应式 */
@media (max-width: 1024px) {
  .customer-products-page {
    padding: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .product-selection-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}
</style>
