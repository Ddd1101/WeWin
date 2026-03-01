<template>
  <div class="login-container">
    <div class="login-box">
      <h2>电商ERP管理系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="account-hint">
        <p><strong>默认账号：</strong></p>
        <p>网站超级管理员: superadmin / superadmin123</p>
      </div>
      <div class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'
import { login } from '../api/index.js'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 页面加载时从localStorage读取保存的用户名
onMounted(() => {
  const savedUsername = localStorage.getItem('lastLoginUsername')
  if (savedUsername) {
    loginForm.username = savedUsername
  }
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        console.log('Attempting to login with:', loginForm.username)
        const response = await login(loginForm.username, loginForm.password)
        
        console.log('Login response:', response)
        const data = response.data
        
        // 保存用户名到localStorage
        localStorage.setItem('lastLoginUsername', loginForm.username)
        
        userStore.setToken(data.token)
        userStore.setUserInfo(data.user)
        
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        console.log('Login error:', error)
        if (error.response) {
          // 服务器返回了错误响应
          console.log('Error response status:', error.response.status)
          console.log('Error response data:', error.response.data)
          const errorMessage = error.response.data?.error || '登录失败，请重试'
          console.log('Error message:', errorMessage)
          if (errorMessage.includes('账户已被禁用')) {
            ElMessage.error('账户已被禁用，请联系管理员')
          } else {
            ElMessage.error(errorMessage)
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应
          console.log('Error request:', error.request)
          ElMessage.error('网络错误，请检查网络连接')
        } else {
          // 请求配置出错
          console.log('Error message:', error.message)
          ElMessage.error('登录失败，请重试')
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}
.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
.login-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}
.account-hint {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}
.account-hint p {
  margin: 5px 0;
}
.register-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}
.register-link a {
  color: #409eff;
  text-decoration: none;
}
.register-link a:hover {
  text-decoration: underline;
}
</style>
