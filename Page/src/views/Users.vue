<template>
  <div class="users-container">
    <div class="users-header">
      <h2>用户管理</h2>
      <div class="header-buttons">
        <el-button 
          type="success" 
          @click="batchActivate"
          :disabled="selectedUsers.length === 0"
        >
          批量激活
        </el-button>
        <el-button 
          type="danger" 
          @click="batchDeactivate"
          :disabled="selectedUsers.length === 0"
        >
          批量禁用
        </el-button>
        <el-button type="primary" @click="handleRefresh">刷新</el-button>
      </div>
    </div>
    
    <!-- 筛选条件 -->
    <div class="filter-container">
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
    
    <!-- 用户表格 -->
    <el-table
      :data="filteredUsers"
      v-loading="loading"
      stripe
      style="width: 100%"
      :max-height="800"
      @selection-change="handleSelectionChange"
      row-key="id"
    >
      <!-- 展开行 -->
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="user-details">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="邮箱">{{ row.email || '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="电话">{{ row.phone || '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="企业编号">{{ row.company_code || '无' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">
                <el-tooltip 
                  :content="new Date(row.date_joined).toLocaleString('zh-CN', { 
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit', 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit' 
                  })" 
                  placement="top"
                >
                  <span>{{ new Date(row.date_joined).toLocaleString('zh-CN', { 
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit', 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  }) }}</span>
                </el-tooltip>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </template>
      </el-table-column>
      
      <!-- 表格列 -->
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" fixed="left" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="real_name" label="姓名" width="120">
        <template #default="{ row }">
          {{ row.real_name || '未设置' }}
        </template>
      </el-table-column>
      <el-table-column label="用户类型" width="200">
        <template #default="{ row }">
          <el-select 
            v-model="row.user_type" 
            @change="(value) => changeUserType({...row, user_type: value})" 
            size="small" 
            style="width: 100%;"
            :disabled="!(row.user_type === 'temporary' || row.user_type === 'site_admin')"
          >
            <el-option label="网站超级管理员" value="super_admin" />
            <el-option label="网站管理员" value="site_admin" />
            <el-option label="企业负责人" value="enterprise_leader" />
            <el-option label="企业用户管理员" value="enterprise_admin" />
            <el-option label="企业用户普通账户" value="enterprise_user" />
            <el-option label="临时账户" value="temporary" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="company_name" label="企业名称" min-width="180" />
      <el-table-column label="状态" width="180" fixed="right">
        <template #default="{ row }">
          <el-select 
            v-model="row.is_active" 
            @change="(value) => toggleUserStatus({...row, is_active: value})" 
            size="small" 
            style="width: 100%;"
            :disabled="row.user_type === 'super_admin' || (row.company_is_active !== undefined && row.company_is_active !== null && !row.company_is_active)"
          >
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElTable, ElTableColumn, ElButton, ElInput, ElForm, ElFormItem, ElSelect, ElOption, ElDescriptions, ElDescriptionsItem, ElTooltip } from 'element-plus'

// API 基础 URL - 根据当前访问的主机自动选择
const getApiBaseUrl = () => {
  const currentHost = window.location.hostname;
  // 本地开发环境
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return "http://localhost:8000";
  }
  // 局域网环境 - 使用服务器IP
  return "http://192.168.1.14:8000";
};
const API_BASE_URL = getApiBaseUrl();

// 响应式数据
const users = ref([])
const loading = ref(false)
const selectedUsers = ref([])

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
    if (filterForm.value.status && filterForm.value.status !== '') {
      const statusFilter = filterForm.value.status === 'true'
      if (user.is_active !== statusFilter) {
        return false
      }
    }
    
    return true
  })
})

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE_URL}/api/account/users/`, {
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

// 刷新用户列表
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

// 变更用户类型
const changeUserType = async (user) => {
  try {
    // 从原始用户列表中获取当前用户的原始类型
    const originalUser = users.value.find(u => u.id === user.id)
    const originalUserType = originalUser ? originalUser.user_type : user.user_type
    const newUserType = user.user_type
    
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE_URL}/api/account/users/${user.id}/update-type/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_type: newUserType })
    })

    const data = await response.json()

    if (response.ok) {
      ElMessage.success('用户类型变更成功')
      loadUsers()
    } else {
      ElMessage.error(data.error || '变更失败')
      // 恢复原来的用户类型
      const userIndex = users.value.findIndex(u => u.id === user.id)
      if (userIndex !== -1) {
        users.value[userIndex].user_type = originalUserType
      }
    }
  } catch (error) {
    ElMessage.error('变更失败，请重试')
    // 重新加载用户列表以确保数据一致性
    loadUsers()
  }
}

// 切换用户状态
const toggleUserStatus = async (user) => {
  try {
    // 从原始用户列表中获取当前用户的原始状态
    const originalUser = users.value.find(u => u.id === user.id)
    const originalStatus = originalUser ? originalUser.is_active : user.is_active
    const newStatus = user.is_active
    
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE_URL}/api/account/users/${user.id}/status/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_active: newStatus })
    })

    const data = await response.json()

    if (response.ok) {
      ElMessage.success(`${newStatus ? '激活' : '禁用'}成功`)
      loadUsers()
    } else {
      ElMessage.error(data.error || '操作失败')
      // 恢复原来的状态
      const userIndex = users.value.findIndex(u => u.id === user.id)
      if (userIndex !== -1) {
        users.value[userIndex].is_active = originalStatus
      }
    }
  } catch (error) {
    ElMessage.error('操作失败，请重试')
    // 重新加载用户列表以确保数据一致性
    loadUsers()
  }
}

// 处理选择变更
const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

// 批量操作的公共函数
const batchUpdateUsers = async (isActive, actionText) => {
  try {
    const token = localStorage.getItem('token')
    
    // 过滤掉超级管理员
    const usersToUpdate = selectedUsers.value.filter(u => u.user_type !== 'super_admin')
    
    if (usersToUpdate.length === 0) {
      ElMessage.warning(`没有可${actionText}的用户（超级管理员不能被批量操作）`)
      return
    }

    await ElMessageBox.confirm(`确定要批量${actionText}选中的 ${usersToUpdate.length} 个用户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const promises = usersToUpdate.map(user => 
      fetch(`${API_BASE_URL}/api/account/users/${user.id}/status/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: isActive })
      }).then(response => response.ok)
    )

    const results = await Promise.all(promises)
    const successCount = results.filter(r => r).length
    const failCount = results.length - successCount

    if (successCount > 0) {
      ElMessage.success(`批量${actionText}成功 ${successCount} 个用户${failCount > 0 ? `，${failCount} 个用户${actionText}失败` : ''}`)
    }
    if (failCount > 0 && successCount === 0) {
      ElMessage.error(`批量${actionText}失败`)
    }
    
    loadUsers()
    selectedUsers.value = []
  } catch (error) {
    console.error('批量操作错误:', error)
    if (error !== 'cancel') {
      ElMessage.error(`批量${actionText}失败，请重试`)
    }
  }
}

// 批量激活
const batchActivate = () => {
  batchUpdateUsers(true, '激活')
}

// 批量禁用
const batchDeactivate = () => {
  batchUpdateUsers(false, '禁用')
}

// 页面挂载时加载用户列表
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.users-header h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.filter-container {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-form {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-form .el-form-item {
  margin-right: 0;
  margin-bottom: 10px;
  flex: 1 1 200px;
}

.filter-form .el-input,
.filter-form .el-select {
  width: 100%;
}

.filter-form .el-button {
  margin-top: 25px;
  flex: 0 0 auto;
}

@media (max-width: 768px) {
  .filter-form .el-form-item {
    flex: 1 1 100%;
  }
  
  .filter-form .el-button {
    margin-top: 10px;
  }
}

.user-details {
  padding: 10px 0;
}

.el-table {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-table__expanded-cell {
  background-color: #f9fafc !important;
}
</style>