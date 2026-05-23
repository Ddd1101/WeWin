<template>
  <div class="customers">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">客户管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddCustomer">
              <el-icon><Plus /></el-icon>
              添加客户
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-input v-model="searchKeyword" placeholder="搜索客户名称、电话或联系人..." clearable style="width: 300px; margin-right: 12px;">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterForm.is_active" placeholder="状态筛选" clearable style="width: 150px;">
          <el-option label="全部" value="" />
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
        <el-button type="primary" @click="fetchCustomers">查询</el-button>
      </div>

      <!-- 客户列表 -->
      <el-table :data="customers" style="width: 100%; margin-top: 16px;" v-loading="loading">
        <el-table-column prop="name" label="客户名称" width="180" />
        <el-table-column prop="contact_name" label="联系人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewDetail(row)">详情</el-button>
            <el-button size="small" type="primary" @click="handleEditCustomer(row)">编辑</el-button>
            <el-button size="small" type="success" @click="handleProductRelation(row)">商品关联</el-button>
            <el-button size="small" type="danger" @click="handleDeleteCustomer(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑客户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      class="customer-dialog"
      @close="resetForm"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="客户名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_name">
              <el-input v-model="form.contact_name" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 客户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="客户详情"
      width="700px"
      class="detail-dialog"
    >
      <el-descriptions :column="2" border v-if="currentCustomer">
        <el-descriptions-item label="客户名称">{{ currentCustomer.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentCustomer.is_active ? 'success' : 'danger'">
            {{ currentCustomer.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentCustomer.contact_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentCustomer.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱" :span="2">{{ currentCustomer.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentCustomer.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentCustomer.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属企业">{{ currentCustomer.company_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ currentCustomer.created_by_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentCustomer.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(currentCustomer.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 商品关联管理对话框 -->
    <el-dialog
      v-model="productDialogVisible"
      title="商品关联管理"
      width="900px"
      class="product-dialog"
    >
      <div class="product-header">
        <el-button type="primary" size="small" @click="handleAddProductRelation">
          <el-icon><Plus /></el-icon>
          添加商品
        </el-button>
      </div>
      <el-table :data="customerProducts" style="width: 100%; margin-top: 16px;">
        <el-table-column prop="product_code" label="商品编码" width="120" />
        <el-table-column prop="product_name" label="商品名称" width="180" />
        <el-table-column prop="product_type_display" label="商品类型" width="100" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEditProductRelation(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleViewPriceHistory(row)">报价历史</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 添加/编辑商品关联对话框 -->
    <el-dialog
      v-model="addProductDialogVisible"
      :title="productRelationDialogTitle"
      width="500px"
      class="add-product-dialog"
    >
      <el-form :model="productForm" :rules="productRules" ref="productFormRef" label-width="100px">
        <el-form-item label="选择商品" prop="product_id">
          <el-select v-model="productForm.product_id" placeholder="请选择商品" style="width: 100%;" filterable>
            <el-option
              v-for="product in allProducts"
              :key="product.id"
              :label="`${product.code} - ${product.name}`"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="productForm.price" :min="0" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="productForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addProductDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitProductRelation" :loading="productSubmitLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报价历史对话框 -->
    <el-dialog
      v-model="priceHistoryDialogVisible"
      title="报价历史"
      width="600px"
      class="price-history-dialog"
    >
      <el-table :data="priceHistories" style="width: 100%;">
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { 
  getCustomers, 
  createCustomer, 
  updateCustomer, 
  deleteCustomer, 
  getCustomerDetail,
  getCustomerProducts,
  createOrUpdateCustomerProduct,
  getCustomerPriceHistory,
  getProducts as fetchAllProducts
} from '@/api'

// 客户列表
const customers = ref([])
// 加载状态
const loading = ref(false)
const submitLoading = ref(false)
const productSubmitLoading = ref(false)
// 搜索关键词
const searchKeyword = ref('')
// 筛选表单
const filterForm = reactive({
  is_active: ''
})
// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})
// 对话框状态
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const productDialogVisible = ref(false)
const addProductDialogVisible = ref(false)
const priceHistoryDialogVisible = ref(false)
const dialogTitle = ref('添加客户')
const productRelationDialogTitle = ref('添加商品关联')
// 当前操作的客户
const currentCustomer = ref(null)
const currentCustomerId = ref(null)
// 客户商品列表
const customerProducts = ref([])
// 所有商品列表
const allProducts = ref([])
// 报价历史
const priceHistories = ref([])
// 表单数据
const form = reactive({
  id: '',
  name: '',
  contact_name: '',
  phone: '',
  email: '',
  address: '',
  remark: '',
  is_active: true
})
// 商品关联表单
const productForm = reactive({
  id: '',
  product_id: '',
  price: 0,
  is_active: true
})
// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }]
}
const productRules = {
  product_id: [{ required: true, message: '请选择商品', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }]
}
// 表单引用
const formRef = ref(null)
const productFormRef = ref(null)

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取客户列表
const fetchCustomers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    if (filterForm.is_active !== '') {
      params.is_active = filterForm.is_active
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const response = await getCustomers(params)
    customers.value = response.data.customers
    pagination.total = response.data.total_count
  } catch (error) {
    ElMessage.error('获取客户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchCustomers()
}

// 处理分页页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  fetchCustomers()
}

// 处理添加客户
const handleAddCustomer = () => {
  dialogTitle.value = '添加客户'
  resetForm()
  form.is_active = true
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: '',
    name: '',
    contact_name: '',
    phone: '',
    email: '',
    address: '',
    remark: '',
    is_active: true
  })
  formRef.value?.resetFields()
}

// 处理编辑客户
const handleEditCustomer = async (row) => {
  dialogTitle.value = '编辑客户'
  try {
    const response = await getCustomerDetail(row.id)
    const customer = response.data
    Object.assign(form, {
      id: customer.id,
      name: customer.name,
      contact_name: customer.contact_name,
      phone: customer.phone,
      email: customer.email,
      address: customer.address,
      remark: customer.remark,
      is_active: customer.is_active
    })
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取客户详情失败')
    console.error(error)
  }
}

// 处理查看详情
const handleViewDetail = async (row) => {
  try {
    const response = await getCustomerDetail(row.id)
    currentCustomer.value = response.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取客户详情失败')
    console.error(error)
  }
}

// 处理删除客户
const handleDeleteCustomer = (row) => {
  ElMessageBox.confirm('确定要删除这个客户吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    submitLoading.value = true
    try {
      await deleteCustomer(row.id)
      ElMessage.success('删除成功')
      fetchCustomers()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (form.id) {
          await updateCustomer(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createCustomer(form)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchCustomers()
      } catch (error) {
        ElMessage.error(error?.response?.data?.error || '操作失败')
        console.error(error?.response?.data || error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 处理商品关联
const handleProductRelation = async (row) => {
  currentCustomerId.value = row.id
  currentCustomer.value = row
  await fetchCustomerProducts()
  productDialogVisible.value = true
}

// 获取客户商品列表
const fetchCustomerProducts = async () => {
  try {
    const response = await getCustomerProducts(currentCustomerId.value)
    customerProducts.value = response.data.customer_products
  } catch (error) {
    ElMessage.error('获取客户商品列表失败')
    console.error(error)
  }
}

// 获取所有商品
const fetchProducts = async () => {
  try {
    const response = await fetchAllProducts({ page_size: 1000 })
    allProducts.value = response.data.products
  } catch (error) {
    ElMessage.error('获取商品列表失败')
    console.error(error)
  }
}

// 处理添加商品关联
const handleAddProductRelation = () => {
  productRelationDialogTitle.value = '添加商品关联'
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
  productRelationDialogTitle.value = '编辑商品关联'
  Object.assign(productForm, {
    id: row.id,
    product_id: row.product_id,
    price: row.price,
    is_active: row.is_active
  })
  fetchProducts()
  addProductDialogVisible.value = true
}

// 处理提交商品关联
const handleSubmitProductRelation = async () => {
  if (!productFormRef.value) return
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      productSubmitLoading.value = true
      try {
        await createOrUpdateCustomerProduct(currentCustomerId.value, productForm)
        ElMessage.success('操作成功')
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
  try {
    const response = await getCustomerPriceHistory(currentCustomerId.value, row.product_id)
    priceHistories.value = response.data.price_histories
    priceHistoryDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取报价历史失败')
    console.error(error)
  }
}

// 初始化
onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.customers {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 24px;
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-section {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.product-header {
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
