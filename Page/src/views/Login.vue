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
        <p><strong>测试账号：</strong></p>
        <p>管理员: admin / 123456</p>
        <p>店长: manager / 123456</p>
        <p>员工: staff / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'

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

const testAccounts = {
  admin: { password: '123456', role: 'superadmin' },
  manager: { password: '123456', role: 'admin' },
  staff: { password: '123456', role: 'user' }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const account = testAccounts[loginForm.username]
        if (account && account.password === loginForm.password) {
          const token = 'mock-token-' + Date.now()
          const userInfo = { username: loginForm.username, role: account.role }
          const currentStore = { id: 1, name: '旗舰店' }
          
          userStore.setToken(token)
          userStore.setUserInfo(userInfo)
          userStore.setCurrentStore(currentStore)
          
          ElMessage.success('登录成功')
          router.push('/')
        } else {
          ElMessage.error('用户名或密码错误')
        }
      } catch (error) {
        ElMessage.error('登录失败，请重试')
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
</style>