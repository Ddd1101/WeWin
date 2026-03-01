<template>
  <div class="spreadsheet-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>在线表格编辑器</span>
          <div class="toolbar">
            <el-button type="primary" @click="exportData">
              <el-icon><Document /></el-icon>
              导出数据
            </el-button>
            <el-button type="success" @click="importData">
              <el-icon><FolderOpened /></el-icon>
              导入数据
            </el-button>
            <el-button type="warning" @click="clearSheet">
              <el-icon><Delete /></el-icon>
              清空表格
            </el-button>
          </div>
        </div>
      </template>
      <div ref="spreadsheetRef" class="spreadsheet-wrapper"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, FolderOpened, Delete } from '@element-plus/icons-vue'
import Spreadsheet from 'x-data-spreadsheet'
import 'x-data-spreadsheet/dist/xspreadsheet.css'

const spreadsheetRef = ref(null)
let xs = ref(null)

onMounted(() => {
  xs.value = new Spreadsheet(spreadsheetRef.value, {
    showToolbar: true,
    showGrid: true,
    showContextmenu: true,
    showBottomBar: true,
    mode: 'edit',
    view: {
      height: () => document.documentElement.clientHeight - 200,
      width: () => document.documentElement.clientWidth - 40,
    },
    row: {
      len: 100,
      height: 25,
    },
    col: {
      len: 26,
      width: 100,
      indexWidth: 60,
      minWidth: 100,
    },
  })

  xs.value.change((data) => {
    console.log('表格数据已更新', data)
  })

  xs.value.cellChanged((cell) => {
    console.log('单元格数据已更新', cell)
  })
})

onBeforeUnmount(() => {
  if (xs.value) {
    xs.value = null
  }
})

const exportData = () => {
  const data = xs.value.getData()
  const jsonData = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonData], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'spreadsheet-data.json'
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('数据导出成功！')
}

const importData = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result)
        xs.value.loadData(data)
        ElMessage.success('数据导入成功！')
      } catch (error) {
        ElMessage.error('数据格式错误，请检查导入有效的JSON文件')
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

const clearSheet = () => {
  xs.value.loadData({})
  ElMessage.info('表格已清空')
}
</script>

<style scoped>
.spreadsheet-container {
  padding: 20px;
  height: calc(100vh - 60px);
  box-sizing: border-box;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  display: flex;
  gap: 10px;
}

.spreadsheet-wrapper {
  height: calc(100vh - 200px);
  overflow: hidden;
}
</style>
