<template>
  <div class="stores">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>店铺管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            创建店铺
          </el-button>
        </div>
      </template>

      <el-table :data="stores" style="width: 100%" v-loading="loading" row-key="id">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <div class="expand-column">
                <div class="expand-item">
                  <span class="expand-label">联系人：</span>
                  <span class="expand-value">{{ row.contact_name || '-' }}</span>
                </div>
                <div v-if="row.shop_url" class="expand-item">
                  <span class="expand-label">店铺链接：</span>
                  <a :href="row.shop_url" target="_blank" class="expand-link">{{ row.shop_url }}</a>
                </div>
                <div class="expand-item">
                  <span class="expand-label">App Key：</span>
                  <span class="expand-value">{{ row.api_config?.app_key || '-' }}</span>
                </div>
              </div>
              <div class="expand-column">
                <div class="expand-item">
                  <span class="expand-label">联系电话：</span>
                  <span class="expand-value">{{ row.contact_phone || '-' }}</span>
                </div>
                <div v-if="row.description" class="expand-item">
                  <span class="expand-label">店铺描述：</span>
                  <span class="expand-value">{{ row.description }}</span>
                </div>
                <div class="expand-item">
                  <span class="expand-label">Access Token：</span>
                  <span class="expand-value">{{ row.api_config?.has_access_token ? '已配置' : '未配置' }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="店铺名称" min-width="150" />
        <el-table-column prop="platform_display" label="电商平台" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getPlatformTagType(row.platform)">{{ row.platform_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_display" label="店铺品类" min-width="120" />
        <el-table-column prop="company_name" label="所属企业" min-width="150" />
        <el-table-column label="店铺管理员" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="manager in row.managers" :key="manager.id" size="small" style="margin-right: 4px; margin-bottom: 4px;">
              {{ manager.real_name || manager.username }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="300">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button link type="success" size="small" @click="openApiConfigDialog(row)">
              API配置
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑店铺' : '创建店铺'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="店铺名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入店铺名称" />
        </el-form-item>
        <el-form-item label="电商平台" prop="platform">
          <el-select v-model="form.platform" placeholder="请选择电商平台" style="width: 100%">
            <el-option v-for="platform in platforms" :key="platform.value" :label="platform.label" :value="platform.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺品类" prop="category">
          <el-select v-model="form.category" placeholder="请选择店铺品类" style="width: 100%">
            <el-option v-for="category in categories" :key="category.value" :label="category.label" :value="category.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入店铺描述" />
        </el-form-item>
        <el-form-item label="店铺链接" prop="shop_url">
          <el-input v-model="form.shop_url" placeholder="请输入店铺链接" />
        </el-form-item>
        <el-form-item label="联系人姓名" prop="contact_name">
          <el-input v-model="form.contact_name" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="店铺管理员" prop="manager_ids">
          <el-select v-model="form.manager_ids" multiple placeholder="请选择店铺管理员" style="width: 100%">
            <el-option v-for="user in companyUsers" :key="user.id" :label="user.real_name || user.username" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="isEdit">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="apiConfigDialogVisible"
      title="API配置"
      width="600px"
      @close="resetApiConfigForm"
    >
      <el-form :model="apiConfigForm" ref="apiConfigFormRef" label-width="120px">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <template #default>
            请填写平台API相关配置信息，用于从电商平台后台拉取订单数据。
          </template>
        </el-alert>
        <el-form-item label="店铺名称">
          <el-input v-model="currentStore.name" disabled />
        </el-form-item>
        <el-form-item label="电商平台">
          <el-tag>{{ currentStore.platform_display }}</el-tag>
        </el-form-item>
        <el-form-item label="App Key">
          <el-input v-model="apiConfigForm.app_key" placeholder="请输入App Key" show-password />
        </el-form-item>
        <el-form-item label="App Secret">
          <el-input v-model="apiConfigForm.app_secret" placeholder="请输入App Secret" show-password />
        </el-form-item>
        <el-form-item label="Access Token">
          <el-input v-model="apiConfigForm.access_token" type="textarea" :rows="2" placeholder="请输入Access Token" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="apiConfigForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="apiConfigDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveApiConfig" :loading="apiConfigSubmitLoading">
          保存配置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getPlatforms, getCategories, getStores, createStore, updateStore, deleteStore, getUsers,
  getStoreApiConfig, createOrUpdateStoreApiConfig 
} from '../api'

const stores = ref([])
const platforms = ref([])
const categories = ref([])
const companyUsers = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const apiConfigDialogVisible = ref(false)
const apiConfigSubmitLoading = ref(false)
const apiConfigFormRef = ref(null)
const currentStore = ref({})

const form = ref({
  name: '',
  platform: '',
  category: '',
  description: '',
  shop_url: '',
  contact_name: '',
  contact_phone: '',
  manager_ids: [],
  is_active: true
})

const apiConfigForm = ref({
  app_key: '',
  app_secret: '',
  access_token: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  platform: [{ required: true, message: '请选择电商平台', trigger: 'change' }],
  category: [{ required: true, message: '请选择店铺品类', trigger: 'change' }]
}

const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')

const getPlatformTagType = (platform) => {
  const typeMap = {
    'taobao': 'danger',
    'tmall': 'warning',
    'jd': 'primary',
    'pdd': 'success',
    'douyin': 'info',
    'kuaishou': '',
    '1688': 'primary',
    'xiaohongshu': 'danger',
    'wechat': 'success',
    'other': 'info'
  }
  return typeMap[platform] || ''
}

const fetchStores = async () => {
  loading.value = true
  try {
    const response = await getStores()
    console.log('获取店铺列表响应:', response)
    stores.value = response.data.stores
    console.log('店铺数据:', stores.value)
  } catch (error) {
    console.error('获取店铺列表失败:', error)
    ElMessage.error(error.response?.data?.error || '获取店铺列表失败')
  } finally {
    loading.value = false
  }
}

const fetchPlatforms = async () => {
  try {
    const response = await getPlatforms()
    platforms.value = response.data.platforms
  } catch (error) {
    console.error('获取平台列表失败:', error)
    ElMessage.error(error.response?.data?.error || '获取平台列表失败')
  }
}

const fetchCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response.data.categories
  } catch (error) {
    console.error('获取品类列表失败:', error)
    ElMessage.error(error.response?.data?.error || '获取品类列表失败')
  }
}

const fetchCompanyUsers = async () => {
  try {
    const response = await getUsers()
    companyUsers.value = response.data.users.filter(u => u.company_id === userInfo.company_id)
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    name: row.name,
    platform: row.platform,
    category: row.category,
    description: row.description,
    shop_url: row.shop_url,
    contact_name: row.contact_name,
    contact_phone: row.contact_phone,
    manager_ids: row.managers.map(m => m.id),
    is_active: row.is_active
  }
  dialogVisible.value = true
}

const resetForm = () => {
  form.value = {
    name: '',
    platform: '',
    category: '',
    description: '',
    shop_url: '',
    contact_name: '',
    contact_phone: '',
    manager_ids: [],
    is_active: true
  }
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateStore(form.value)
          ElMessage.success('更新店铺成功')
        } else {
          await createStore(form.value)
          ElMessage.success('创建店铺成功')
        }
        dialogVisible.value = false
        fetchStores()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || (isEdit.value ? '更新店铺失败' : '创建店铺失败'))
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个店铺吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteStore(row.id)
    ElMessage.success('删除店铺成功')
    fetchStores()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '删除店铺失败')
    }
  }
}

const openApiConfigDialog = async (row) => {
  currentStore.value = row
  apiConfigDialogVisible.value = true
  await fetchApiConfig(row.id)
}

const fetchApiConfig = async (storeId) => {
  try {
    const response = await getStoreApiConfig(storeId)
    if (response.data.config) {
      apiConfigForm.value = {
        app_key: response.data.config.app_key || '',
        app_secret: response.data.config.app_secret || '',
        access_token: response.data.config.access_token || '',
        is_active: response.data.config.is_active !== false
      }
    } else {
      resetApiConfigForm()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '获取API配置失败')
  }
}

const resetApiConfigForm = () => {
  apiConfigForm.value = {
    app_key: '',
    app_secret: '',
    access_token: '',
    is_active: true
  }
  if (apiConfigFormRef.value) {
    apiConfigFormRef.value.clearValidate()
  }
}

const handleSaveApiConfig = async () => {
  apiConfigSubmitLoading.value = true
  try {
    await createOrUpdateStoreApiConfig(currentStore.value.id, apiConfigForm.value)
    ElMessage.success('保存API配置成功')
    apiConfigDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '保存API配置失败')
  } finally {
    apiConfigSubmitLoading.value = false
  }
}

onMounted(() => {
  fetchStores()
  fetchPlatforms()
  fetchCategories()
  fetchCompanyUsers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expand-content {
  padding: 20px;
  display: flex;
  gap: 40px;
}

.expand-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.expand-item {
  display: flex;
  align-items: flex-start;
}

.expand-label {
  font-weight: 600;
  color: #606266;
  min-width: 100px;
  flex-shrink: 0;
}

.expand-value {
  color: #303133;
  word-break: break-all;
}

.expand-link {
  color: #409eff;
  text-decoration: none;
  word-break: break-all;
}

.expand-link:hover {
  text-decoration: underline;
}
</style>
