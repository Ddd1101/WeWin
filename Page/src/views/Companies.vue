<template>
  <div class="companies-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>企业管理</span>
          <div class="header-actions">
            <el-button 
              type="primary" 
              @click="openAddCompanyDialog"
              :disabled="selectedCompanies.length > 0"
            >
              <el-icon><Plus /></el-icon>
              新增企业
            </el-button>
            <el-button 
              type="success" 
              @click="batchActivateCompanies"
              :disabled="selectedCompanies.length === 0"
            >
              <el-icon><Check /></el-icon>
              批量启用
            </el-button>
            <el-button 
              type="danger" 
              @click="batchDeactivateCompanies"
              :disabled="selectedCompanies.length === 0"
            >
              <el-icon><Close /></el-icon>
              批量禁用
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="companies" 
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="企业名称" />
        <el-table-column prop="code" label="企业编号" />
        <el-table-column prop="address" label="企业地址" />
        <el-table-column prop="contact_name" label="联系人" />
        <el-table-column prop="contact_phone" label="联系电话" />
        <el-table-column label="创建时间">
          <template #default="scope">
            <el-tooltip 
              :content="new Date(scope.row.created_at).toLocaleString('zh-CN', { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit', 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
              })" 
              placement="top"
            >
              <span>{{ new Date(scope.row.created_at).toLocaleString('zh-CN', { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit', 
                hour: '2-digit', 
                minute: '2-digit' 
              }) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.is_active" 
              @change="updateCompanyStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="openEditCompanyDialog(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteCompany(scope.row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
            <el-button size="small" @click="viewCompanyUsers(scope.row.id)">
              <el-icon><User /></el-icon>
              查看用户
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 新增/编辑企业对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="企业名称" required>
          <el-input v-model="form.name" placeholder="请输入企业名称" />
        </el-form-item>
        <el-form-item label="企业地址">
          <el-input v-model="form.address" placeholder="请输入企业地址" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_name" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCompany">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 企业用户列表对话框 -->
    <el-dialog
      v-model="usersDialogVisible"
      title="企业用户列表"
      width="800px"
    >
      <el-table :data="companyUsers" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="user_type_display" label="用户类型" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="is_active" label="是否激活">
          <template #default="scope">
            <el-switch v-model="scope.row.is_active" @change="updateUserStatus(scope.row.id, scope.row.is_active)" />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, User, OfficeBuilding, Check, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCompanies, createCompany, updateCompany, deleteCompany as deleteCompanyApi, getCompanyUsers, batchUpdateCompanyStatus } from '../api'

const companies = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 选中的企业
const selectedCompanies = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新增企业')
const form = ref({
  name: '',
  address: '',
  contact_name: '',
  contact_phone: ''
})

const usersDialogVisible = ref(false)
const companyUsers = ref([])

const loadCompanies = async () => {
  try {
    const response = await getCompanies()
    companies.value = response.data.companies
    total.value = response.data.companies.length
  } catch (error) {
    ElMessage.error('获取企业列表失败')
  }
}

const openAddCompanyDialog = () => {
  dialogTitle.value = '新增企业'
  form.value = {
    name: '',
    code: '',
    address: '',
    contact_name: '',
    contact_phone: ''
  }
  dialogVisible.value = true
}

const openEditCompanyDialog = (company) => {
  dialogTitle.value = '编辑企业'
  form.value = {
    id: company.id,
    name: company.name,
    address: company.address,
    contact_name: company.contact_name,
    contact_phone: company.contact_phone
  }
  dialogVisible.value = true
}

const saveCompany = async () => {
  try {
    if (form.value.id) {
      // 编辑企业
      await updateCompany(form.value)
      ElMessage.success('企业信息更新成功')
    } else {
      // 新增企业
      await createCompany(form.value)
      ElMessage.success('企业创建成功')
    }
    dialogVisible.value = false
    loadCompanies()
  } catch (error) {
    console.log('Save company error:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error('操作失败: ' + error.response.data.error)
    } else {
      ElMessage.error('操作失败')
    }
  }
}

const deleteCompany = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该企业吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteCompanyApi(id)
    ElMessage.success('企业删除成功')
    loadCompanies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewCompanyUsers = async (companyId) => {
  try {
    const response = await getCompanyUsers(companyId)
    companyUsers.value = response.data.users
    usersDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取企业用户失败')
  }
}

const updateUserStatus = async (userId, isActive) => {
  try {
    // 调用更新用户状态的API
    await updateUserStatusApi(userId, isActive)
    ElMessage.success('用户状态更新成功')
  } catch (error) {
    ElMessage.error('更新用户状态失败')
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadCompanies()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  loadCompanies()
}

// 处理选择事件
const handleSelectionChange = (val) => {
  selectedCompanies.value = val
}

// 单个企业状态更新
const updateCompanyStatus = async (company) => {
  try {
    await updateCompany(company)
    ElMessage.success(`企业${company.is_active ? '启用' : '禁用'}成功`)
  } catch (error) {
    ElMessage.error('操作失败')
    // 恢复原来的状态
    company.is_active = !company.is_active
  }
}

// 批量启用企业
const batchActivateCompanies = async () => {
  try {
    await ElMessageBox.confirm('确定要批量启用选中的企业吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const companyIds = selectedCompanies.value.map(company => company.id)
    await batchUpdateCompanyStatus(companyIds, true)
    ElMessage.success('批量启用成功')
    loadCompanies()
    selectedCompanies.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量启用失败')
    }
  }
}

// 批量禁用企业
const batchDeactivateCompanies = async () => {
  try {
    await ElMessageBox.confirm('确定要批量禁用选中的企业吗？禁用后，企业下的非管理员用户将被禁用。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const companyIds = selectedCompanies.value.map(company => company.id)
    await batchUpdateCompanyStatus(companyIds, false)
    ElMessage.success('批量禁用成功')
    loadCompanies()
    selectedCompanies.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量禁用失败')
    }
  }
}

onMounted(() => {
  loadCompanies()
})
</script>

<style scoped>
.companies-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>