<template>
  <div class="customers-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">客户管理</h1>
        <p class="page-subtitle">管理和维护您的客户信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" @click="handleAddCustomer" class="add-btn">
          <el-icon><Plus /></el-icon>
          <span>新建客户</span>
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pagination.total }}</div>
          <div class="stat-label">全部客户</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ activeCount }}</div>
          <div class="stat-label">活跃客户</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ customers.length }}</div>
          <div class="stat-label">当前页面</div>
        </div>
      </div>
    </div>

    <!-- 主内容卡片 -->
    <div class="content-card">
      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <div class="filter-left">
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索客户名称、电话或联系人..." 
            clearable
            class="search-input"
            prefix-icon="Search"
            @keyup.enter="fetchCustomers"
          />
          <el-select 
            v-model="filterForm.is_active" 
            placeholder="状态筛选" 
            clearable
            class="status-select"
            @change="fetchCustomers"
          >
            <el-option label="全部" value="" />
            <el-option label="活跃" :value="true" />
            <el-option label="停用" :value="false" />
          </el-select>
          <el-button type="primary" @click="fetchCustomers" class="search-btn">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </div>
      </div>

      <!-- 客户列表 -->
      <el-table 
        :data="customers" 
        class="customer-table"
        v-loading="loading"
        stripe
        :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: 600 }"
      >
        <el-table-column prop="name" label="客户名称" width="200">
          <template #default="{ row }">
            <div class="name-cell">
              <div class="avatar-small">
                {{ row.name?.charAt(0)?.toUpperCase() || 'C' }}
              </div>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contact_name" label="联系人" width="120">
          <template #default="{ row }">
            <span class="text-gray">{{ row.contact_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="150">
          <template #default="{ row }">
            <span class="text-gray">{{ row.phone || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="200">
          <template #default="{ row }">
            <span class="text-gray">{{ row.email || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="text-gray">{{ row.address || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" size="small">
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120">
          <template #default="{ row }">
            <span class="text-gray">{{ row.created_by_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="handleViewDetail(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button type="primary" link size="small" @click="handleEditCustomer(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="success" link size="small" @click="handleProductRelation(row)">
                <el-icon><Goods /></el-icon>
                商品
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteCustomer(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="pagination.total > 0">
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

      <!-- 空状态 -->
      <el-empty v-if="customers.length === 0 && !loading" description="暂无客户" class="empty-state">
        <el-button type="primary" @click="handleAddCustomer">
          <el-icon><Plus /></el-icon>
          添加第一个客户
        </el-button>
      </el-empty>
    </div>
    
    <!-- 添加/编辑客户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="560px"
      class="customer-dialog"
      @close="resetForm"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" class="customer-form">
        <el-form-item label="客户名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入客户名称" class="form-input" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_name">
              <el-input v-model="form.contact_name" placeholder="请输入联系人" class="form-input" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入联系电话" class="form-input" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" class="form-input" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="请输入地址" class="form-textarea" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" class="form-textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <div class="switch-wrapper">
            <el-switch v-model="form.is_active" active-text="活跃" inactive-text="停用" inline-prompt />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading" size="large">
            确认保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 客户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="客户详情"
      width="680px"
      class="detail-dialog"
    >
      <div class="detail-header" v-if="currentCustomer">
        <div class="detail-avatar">
          {{ currentCustomer.name?.charAt(0)?.toUpperCase() || 'C' }}
        </div>
        <div class="detail-info">
          <h2 class="detail-name">{{ currentCustomer.name }}</h2>
          <el-tag :type="currentCustomer.is_active ? 'success' : 'info'" effect="light" size="small">
            {{ currentCustomer.is_active ? '活跃' : '停用' }}
          </el-tag>
        </div>
      </div>
      <div class="detail-content">
        <el-descriptions :column="2" border v-if="currentCustomer" class="detail-descriptions">
          <el-descriptions-item label="联系人">
            <span class="desc-text">{{ currentCustomer.contact_name || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            <span class="desc-text">{{ currentCustomer.phone || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱" :span="2">
            <span class="desc-text">{{ currentCustomer.email || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">
            <span class="desc-text">{{ currentCustomer.address || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            <span class="desc-text">{{ currentCustomer.remark || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="所属企业">
            <span class="desc-text">{{ currentCustomer.company_name || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            <span class="desc-text">{{ currentCustomer.created_by_name || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            <span class="desc-text">{{ formatDate(currentCustomer.created_at) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            <span class="desc-text">{{ formatDate(currentCustomer.updated_at) }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <div class="detail-footer">
          <el-button @click="detailDialogVisible = false" size="large">关闭</el-button>
          <el-button type="primary" @click="handleEditFromDetail" size="large" v-if="currentCustomer">
            <el-icon><Edit /></el-icon>
            编辑客户
          </el-button>
          <el-button type="success" @click="handleProductRelation(currentCustomer)" size="large" v-if="currentCustomer">
            <el-icon><Goods /></el-icon>
            商品管理
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, User, CircleCheck, UserFilled, View, Edit, Delete, Goods } from '@element-plus/icons-vue'
import { 
  getCustomers, 
  createCustomer, 
  updateCustomer, 
  deleteCustomer, 
  getCustomerDetail
} from '@/api'

const router = useRouter()

// 客户列表
const customers = ref([])
// 加载状态
const loading = ref(false)
const submitLoading = ref(false)
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
const dialogTitle = ref('新建客户')
// 当前操作的客户
const currentCustomer = ref(null)
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
// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }]
}
// 表单引用
const formRef = ref(null)

// 计算属性
const activeCount = computed(() => {
  return customers.value.filter(item => item.is_active).length
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
    customers.value = response.data.customers || []
    pagination.total = response.data.total_count || 0
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
  dialogTitle.value = '新建客户'
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

// 从详情页编辑客户
const handleEditFromDetail = () => {
  detailDialogVisible.value = false
  handleEditCustomer(currentCustomer.value)
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
  ElMessageBox.confirm(
    `确定要删除客户「${row.name}」吗？`, 
    '提示', 
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'confirm-btn-danger'
    }
  ).then(async () => {
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
const handleProductRelation = (row) => {
  if (detailDialogVisible.value) {
    detailDialogVisible.value = false
  }
  router.push(`/customers/${row.id}/products`)
}

// 初始化
onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.customers-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4f8 0%, #e8eef3 100%);
  padding: 24px 32px;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -0.5px;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
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
  padding: 24px 28px;
  overflow: hidden;
}

/* 筛选部分 */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 320px;
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

.status-select {
  width: 140px;
}

.status-select :deep(.el-select__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}

.search-btn {
  border-radius: 10px;
  font-weight: 600;
}

/* 表格 */
.customer-table {
  width: 100%;
}

.customer-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}

.name-text {
  font-weight: 600;
  color: #1e293b;
}

.text-gray {
  color: #64748b;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.action-buttons .el-button {
  font-weight: 500;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding-top: 24px;
}

/* 空状态 */
.empty-state {
  padding: 60px 0;
}

/* 对话框 */
.customer-dialog :deep(.el-dialog),
.detail-dialog :deep(.el-dialog) {
  border-radius: 16px;
}

.customer-dialog :deep(.el-dialog__header),
.detail-dialog :deep(.el-dialog__header) {
  padding: 24px 28px 8px;
}

.customer-dialog :deep(.el-dialog__title),
.detail-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.customer-dialog :deep(.el-dialog__body),
.detail-dialog :deep(.el-dialog__body) {
  padding: 16px 28px 8px;
}

.customer-form {
  padding: 8px 0;
}

.form-input :deep(.el-input__wrapper),
.form-textarea :deep(.el-textarea__inner) {
  border-radius: 10px;
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

/* 详情对话框 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 20px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e8eef3 100%);
  border-radius: 12px;
  margin-bottom: 24px;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 26px;
  font-weight: 800;
}

.detail-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-name {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #1e293b;
}

.detail-content {
  padding: 4px 0;
}

.detail-descriptions :deep(.el-descriptions__header .el-descriptions__cell) {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
}

.detail-descriptions :deep(.el-descriptions__label) {
  color: #64748b;
  font-weight: 600;
}

.desc-text {
  color: #1e293b;
}

.detail-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 8px 28px 24px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .customers-page {
    padding: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>
