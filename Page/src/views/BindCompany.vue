<template>
  <div class="bind-company-container">
    <div class="bind-company-box">
      <h2>绑定企业</h2>
      <el-tabs v-model="activeTab" class="bind-tabs">
        <el-tab-pane label="创建新企业" name="create">
          <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
            <el-form-item label="企业名称" prop="company_name">
              <el-input v-model="createForm.company_name" placeholder="请输入企业名称" />
            </el-form-item>
            <el-form-item label="企业地址" prop="company_address">
              <el-input v-model="createForm.company_address" placeholder="请输入企业地址" />
            </el-form-item>
            <el-form-item label="联系人姓名" prop="company_contact_name">
              <el-input v-model="createForm.company_contact_name" placeholder="请输入联系人姓名" />
            </el-form-item>
            <el-form-item label="联系人电话" prop="company_contact_phone">
              <el-input v-model="createForm.company_contact_phone" placeholder="请输入联系人电话" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleCreateCompany" :loading="loading" style="width: 100%">
                创建并绑定企业
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="加入已有企业" name="bind">
          <el-form :model="bindForm" :rules="bindRules" ref="bindFormRef" label-width="120px">
            <el-form-item label="企业编号" prop="company_code">
              <el-input v-model="bindForm.company_code" placeholder="请输入企业编号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleBindCompany" :loading="loading" style="width: 100%">
                加入企业
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div class="skip-link">
        <el-button type="text" @click="handleSkip">稍后绑定，先去首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('create')
const loading = ref(false)
const createFormRef = ref(null)
const bindFormRef = ref(null)

const createForm = ref({
  company_name: '',
  company_address: '',
  company_contact_name: '',
  company_contact_phone: ''
})

const bindForm = ref({
  company_code: ''
})

const createRules = ref({
  company_name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
})

const bindRules = ref({
  company_code: [{ required: true, message: '请输入企业编号', trigger: 'blur' }]
})

const handleCreateCompany = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const token = localStorage.getItem('token')
        const response = await fetch('http://localhost:8000/api/account/create-and-bind-company/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(createForm.value)
        })
        
        const result = await response.json()
        
        if (response.ok) {
          ElMessage.success('企业创建成功，您已成为该企业管理员！')
          userStore.setUserInfo(result)
          ElMessage.info(`您的企业编号是：${result.company_code}，请妥善保管！`)
          setTimeout(() => {
            router.push('/')
          }, 2000)
        } else {
          ElMessage.error(result.error || '创建企业失败')
        }
      } catch (error) {
        ElMessage.error('创建企业失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleBindCompany = async () => {
  if (!bindFormRef.value) return
  
  await bindFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const token = localStorage.getItem('token')
        const response = await fetch('http://localhost:8000/api/account/bind-existing-company/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(bindForm.value)
        })
        
        const result = await response.json()
        
        if (response.ok) {
          ElMessage.success('成功加入企业！')
          userStore.setUserInfo(result)
          setTimeout(() => {
            router.push('/')
          }, 1000)
        } else {
          ElMessage.error(result.error || '加入企业失败')
        }
      } catch (error) {
        ElMessage.error('加入企业失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleSkip = () => {
  router.push('/')
}

onMounted(() => {
  const user = userStore.user
  if (user && user.company_id) {
    ElMessage.info('您已经绑定了企业')
    router.push('/')
  }
})
</script>

<style scoped>
.bind-company-container {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.bind-company-box {
  width: 500px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.bind-company-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.bind-tabs {
  margin-bottom: 20px;
}

.skip-link {
  text-align: center;
  margin-top: 20px;
}
</style>