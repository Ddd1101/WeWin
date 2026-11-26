<template>
  <div class="response-section">
    <div class="response-header">
      <span>请求链接</span>
    </div>
    <div v-if="logs && logs.length > 0" class="request-logs">
      <el-collapse v-model="activeRequestLogs">
        <el-collapse-item
          v-for="(log, index) in logs"
          :key="index"
          :name="index"
        >
          <template #title>
            <span class="request-title">
            请求 {{ index + 1 }}: {{ log.url }}</span>
          </template>
          <div class="request-detail">
            <div class="request-info">
              <span><span class="label">方法:</span> {{ log.method }}</span>
              <span v-if="log.status_code"><span class="label">状态码:</span> {{ log.status_code }}</span>
            </div>
            <div class="request-params">
              <div class="label">请求参数:</div>
              <pre class="json-display">{{ JSON.stringify(log.params, null, 2) }}</pre>
            </div>
            <div v-if="log.response" class="request-response">
              <div class="label">响应结果:</div>
              <pre class="json-display">{{ JSON.stringify(log.response, null, 2) }}</pre>
            </div>
            <div v-if="log.error" class="request-error">
              <div class="label">错误信息:</div>
              <pre class="json-display">{{ log.error }}</pre>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    <div v-else class="no-request-logs">
      <el-empty description="暂无请求日志" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  logs: {
    type: Array,
    default: () => []
  }
})

const activeRequestLogs = ref([])
</script>

<style scoped>
.response-section {
  margin-top: 30px;
  border-top: 1px solid #e6e6e6;
  padding-top: 20px;
}

.response-header {
  font-weight: 600;
  margin-bottom: 15px;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.request-logs {
  margin-bottom: 20px;
}

.request-title {
  font-weight: 500;
  color: #409eff;
}

.request-detail {
  padding: 15px;
  background-color: #fafafa;
  border-radius: 4px;
}

.request-info {
  margin-bottom: 15px;
  display: flex;
  gap: 20px;
}

.request-info .label {
  font-weight: 600;
  color: #606266;
  margin-right: 5px;
}

.request-params,
.request-response,
.request-error {
  margin-bottom: 15px;
}

.request-params .label,
.request-response .label,
.request-error .label {
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  display: block;
}

.json-display {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  margin: 0;
}

.no-request-logs {
  padding: 40px 0;
}
</style>
