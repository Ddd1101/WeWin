<template>
  <div class="login-container">
    <div class="login-box">
      <h2>电商ERP管理系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="0">
        <el-form-item prop="username">
          <el-autocomplete
            v-model="loginForm.username"
            :fetch-suggestions="querySearch"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            clearable
            style="width: 100%"
            :trigger-on-focus="true"
          >
            <template #default="{ item }">
              <div class="history-item">
                {{ item.value }}
              </div>
            </template>
          </el-autocomplete>
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
const loginHistory = ref([])

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 从localStorage读取登录历史
const loadLoginHistory = () => {
  try {
    const history = localStorage.getItem('loginHistory')
    if (history) {
      loginHistory.value = JSON.parse(history)
    }
  } catch (error) {
    console.error('读取登录历史失败:', error)
  }
}

// 保存登录历史到localStorage
const saveLoginHistory = (username) => {
  try {
    // 移除已存在的同名账户
    let history = loginHistory.value.filter(item => item !== username)
    // 将新账户添加到最前面
    history.unshift(username)
    // 最多保存10个历史记录
    history = history.slice(0, 10)
    loginHistory.value = history
    localStorage.setItem('loginHistory', JSON.stringify(history))
  } catch (error) {
    console.error('保存登录历史失败:', error)
  }
}

// 自动补全查询函数
const querySearch = (queryString, cb) => {
  let results = []
  if (queryString) {
    results = loginHistory.value.filter(username => 
      username.toLowerCase().includes(queryString.toLowerCase())
    )
  } else {
    results = [...loginHistory.value]
  }
  // 转换为 el-autocomplete 需要的格式
  const formattedResults = results.map(username => ({ value: username }))
  cb(formattedResults)
}

// 页面加载时读取数据
onMounted(() => {
  loadLoginHistory()
  // 如果有历史记录，默认选中第一个
  if (loginHistory.value.length > 0) {
    loginForm.username = loginHistory.value[0]
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
        
        // 保存登录历史
        saveLoginHistory(loginForm.username)
        
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
.history-item {
  padding: 6px 12px;
  cursor: pointer;
}
.history-item:hover {
  background-color: #f5f7fa;
}
</style>
