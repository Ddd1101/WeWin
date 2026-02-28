<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <el-form :model="profile" :rules="rules" ref="profileForm" label-width="120px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profile.username" disabled />
        </el-form-item>
        
        <el-form-item label="用户类型" prop="userType">
          <el-input v-model="profile.userType" disabled />
        </el-form-item>
        
        <el-form-item label="所属企业" prop="company">
          <el-input v-model="profile.company" disabled />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="profile.phone" placeholder="请输入联系电话" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profile.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="profile.realName" placeholder="请输入真实姓名" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">保存修改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="profile-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入旧密码" />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>
        
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitPassword">修改密码</el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentUser, updateProfile, changePassword } from '../api/index.js'

const profile = ref({
  username: '',
  userType: '',
  company: '',
  phone: '',
  email: '',
  realName: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = {
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const profileForm = ref(null)
const passwordFormRef = ref(null)

const submitForm = () => {
  profileForm.value.validate((valid) => {
    if (valid) {
      const updateData = {
        email: profile.value.email,
        phone: profile.value.phone
      }
      updateProfile(updateData)
        .then(response => {
          ElMessage.success('个人信息更新成功')
        })
        .catch(error => {
          ElMessage.error('更新失败：' + (error.response?.data?.error || '未知错误'))
        })
    } else {
      ElMessage.error('请检查输入信息')
      return false
    }
  })
}

const resetForm = () => {
  profileForm.value.resetFields()
}

const submitPassword = () => {
  passwordFormRef.value.validate((valid) => {
    if (valid) {
      const passwordData = {
        old_password: passwordForm.oldPassword,
        new_password: passwordForm.newPassword
      }
      changePassword(passwordData)
        .then(response => {
          ElMessage.success('密码修改成功')
          resetPasswordForm()
        })
        .catch(error => {
          ElMessage.error('修改失败：' + (error.response?.data?.error || '未知错误'))
        })
    } else {
      ElMessage.error('请检查输入信息')
      return false
    }
  })
}

const resetPasswordForm = () => {
  passwordFormRef.value.resetFields()
}

const loadUserInfo = () => {
  getCurrentUser()
    .then(response => {
      const userInfo = response.data
      profile.value = {
        username: userInfo.username,
        userType: userInfo.user_type_display,
        company: userInfo.company_name || '无',
        phone: userInfo.phone || '',
        email: userInfo.email || '',
        realName: userInfo.username
      }
    })
    .catch(error => {
      ElMessage.error('获取用户信息失败：' + (error.response?.data?.error || '未知错误'))
    })
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  max-width: 800px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>