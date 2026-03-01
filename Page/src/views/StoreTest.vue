<template>
  <div class="store-test">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>店铺测试页面</span>
        </div>
      </template>
      <div class="content">
        <el-form :model="testForm" label-width="120px" style="max-width: 800px;">
          <el-form-item label="选择店铺">
            <el-select v-model="testForm.storeId" placeholder="请选择要测试的店铺" style="width: 100%;" @change="handleStoreChange">
              <el-option 
                v-for="store in stores" 
                :key="store.id" 
                :label="store.name + ' (' + store.platform_display + ')'" 
                :value="store.id" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="testForm.startTime"
              type="datetime"
              placeholder="选择开始时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%;"
            />
          </el-form-item>
          
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="testForm.endTime"
              type="datetime"
              placeholder="选择结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%;"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleTest" :loading="testing">
              执行测试
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="response" class="response-section">
          <div class="response-header">
            <span>响应结果</span>
          </div>
          <pre class="json-display">{{ JSON.stringify(response, null, 2) }}</pre>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getStores, triggerDataPull } from '../api'

const stores = ref([])
const testing = ref(false)
const response = ref(null)

const testForm = ref({
  storeId: null,
  startTime: null,
  endTime: null
})

const fetchStores = async () => {
  try {
    const res = await getStores()
    stores.value = res.data.stores
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '获取店铺列表失败')
  }
}

const handleStoreChange = (storeId) => {
  const store = stores.value.find(s => s.id === storeId)
  if (store) {
    console.log('选择的店铺:', store)
  }
}

const handleTest = async () => {
  if (!testForm.value.storeId) {
    ElMessage.warning('请选择要测试的店铺')
    return
  }
  if (!testForm.value.startTime || !testForm.value.endTime) {
    ElMessage.warning('请选择开始时间和结束时间')
    return
  }

  testing.value = true
  response.value = null
  
  try {
    const res = await triggerDataPull(testForm.value.storeId, {
      start_time: testForm.value.startTime,
      end_time: testForm.value.endTime
    })
    response.value = res.data
    ElMessage.success('测试执行成功')
  } catch (error) {
    response.value = error.response?.data || { error: '测试执行失败' }
    ElMessage.error(error.response?.data?.error || '测试执行失败')
  } finally {
    testing.value = false
  }
}

const resetForm = () => {
  testForm.value = {
    storeId: null,
    startTime: null,
    endTime: null
  }
  response.value = null
}

onMounted(() => {
  fetchStores()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content {
  padding: 20px;
}

.response-section {
  margin-top: 30px;
  border-top: 1px solid #e6e6e6;
  padding-top: 20px;
}

.response-header {
  font-weight: 600;
  margin-bottom: 15px;
  color: #303133;
}

.json-display {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 500px;
  overflow-y: auto;
}
</style>
