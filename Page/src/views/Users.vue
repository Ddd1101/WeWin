<template>
  <div class="users">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleRefresh">刷新</el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="用户名">
            <el-input v-model="filterForm.username" placeholder="请输入用户名" clearable />
          </el-form-item>
          <el-form-item label="姓名">
            <el-input v-model="filterForm.realName" placeholder="请输入真实姓名" clearable />
          </el-form-item>
          <el-form-item label="用户类型">
            <el-select v-model="filterForm.userType" placeholder="请选择用户类型" clearable>
              <el-option label="网站超级管理员" value="super_admin" />
              <el-option label="网站管理员" value="site_admin" />
              <el-option label="企业负责人" value="enterprise_leader" />
              <el-option label="企业用户管理员" value="enterprise_admin" />
              <el-option label="企业用户普通账户" value="enterprise_user" />
              <el-option label="临时账户" value="temporary" />
            </el-select>
          </el-form-item>
          <el-form-item label="企业">
            <el-input v-model="filterForm.company" placeholder="请输入企业名称或编号" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
              <el-option label="激活" value="true" />
              <el-option label="禁用" value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">筛选</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="filteredUsers" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="real_name" label="姓名" width="120">
          <template #default="{ row }">
            {{ row.real_name || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column prop="user_type_display" label="用户类型" width="180" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column prop="company_name" label="企业名称" width="180" />
        <el-table-column prop="company_code" label="企业编号" width="120" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            <el-tooltip :content="new Date(row.date_joined).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })" placement="top">
              <span>{{ new Date(row.date_joined).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

const users = ref([])
const loading = ref(false)

// 筛选表单
const filterForm = ref({
  username: '',
  realName: '',
  userType: '',
  company: '',
  status: ''
})

// 筛选后的用户列表
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    // 用户名筛选
    if (filterForm.value.username && !user.username.toLowerCase().includes(filterForm.value.username.toLowerCase())) {
      return false
    }
    
    // 真实姓名筛选
    if (filterForm.value.realName) {
      const realNameFilter = filterForm.value.realName.toLowerCase()
      const realName = (user.real_name || '').toLowerCase()
      if (!realName.includes(realNameFilter)) {
        return false
      }
    }
    
    // 用户类型筛选
    if (filterForm.value.userType && user.user_type !== filterForm.value.userType) {
      return false
    }
    
    // 企业筛选
    if (filterForm.value.company) {
      const companyFilter = filterForm.value.company.toLowerCase()
      const companyName = (user.company_name || '').toLowerCase()
      const companyCode = (user.company_code || '').toLowerCase()
      if (!companyName.includes(companyFilter) && !companyCode.includes(companyFilter)) {
        return false
      }
    }
    
    // 状态筛选
    if (filterForm.value.status !== '') {
      const statusFilter = filterForm.value.status === 'true'
      if (user.is_active !== statusFilter) {
        return false
      }
    }
    
    return true
  })
})

const loadUsers = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:8000/api/account/users/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    const data = await response.json()
    
    if (response.ok) {
      users.value = data.users
    } else {
      ElMessage.error(data.error || '加载用户失败')
    }
  } catch (error) {
    ElMessage.error('加载用户失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadUsers()
}

// 处理筛选
const handleFilter = () => {
  // 筛选逻辑由computed属性处理
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    username: '',
    realName: '',
    userType: '',
    company: '',
    status: ''
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.filter-form {
  width: 100%;
}

.filter-form .el-form-item {
  margin-right: 15px;
}

.filter-form .el-input,
.filter-form .el-select {
  min-width: 180px;
}
</style>