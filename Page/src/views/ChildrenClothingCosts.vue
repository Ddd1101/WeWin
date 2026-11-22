<template>
  <div class="costs-page">
    <div class="toolbar">
      <h2>童装成本表</h2>
      <div class="toolbar-actions">
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        <el-button @click="reload">刷新</el-button>
      </div>
    </div>
    <p class="hint">行=货号，列=尺码；货号/名称只读，供应商与各尺码成本可直接编辑。清空某尺码单元格表示删除该尺码。</p>
    <HotTable v-if="loaded" ref="hotTableRef" :settings="hotSettings" />
    <div v-else class="loading">加载中...</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { HotTable } from '@handsontable/vue3'
import { registerAllModules } from 'handsontable/registry'
import { ElMessage } from 'element-plus'
import 'handsontable/styles/handsontable.min.css'
import 'handsontable/styles/ht-theme-main.min.css'
import { getChildrenClothingCosts, saveChildrenClothingCosts } from '@/api'

registerAllModules()

const hotTableRef = ref(null)
const rows = ref([])
const sizeColumns = ref([])
const saving = ref(false)
const loaded = ref(false)

const hotSettings = reactive({
  licenseKey: 'non-commercial-and-evaluation',
  data: [],
  colHeaders: [],
  rowHeaders: true,
  columns: [],
  height: 600,
  width: '100%',
  manualColumnResize: true,
  stretchH: 'none',
  contextMenu: true,
  dropdownMenu: true,
  filters: true,
  search: true,
  columnSorting: true,
  manualRowResize: true,
  manualColumnMove: true,
  manualRowMove: true,
  hiddenColumns: true,
  fixedColumnsLeft: 3,
  fillHandle: true,
  comments: true,
})

function buildData() {
  return rows.value.map((r) => {
    const row = [r.code, r.name, r.supplier]
    for (const size of sizeColumns.value) {
      row.push(r.costs[size] ?? null)
    }
    return row
  })
}

function buildColHeaders() {
  return ['货号', '名称', '供应商', ...sizeColumns.value]
}

function buildColumns() {
  return [
    { data: 0, readOnly: true, width: 110 },
    { data: 1, readOnly: true, width: 160 },
    { data: 2, type: 'text', width: 140 },
    ...sizeColumns.value.map(() => ({
      type: 'numeric',
      numericFormat: { pattern: '0.00' },
      width: 80,
    })),
  ]
}

async function loadData() {
  const res = await getChildrenClothingCosts()
  rows.value = res.data.rows || []
  sizeColumns.value = res.data.columns || []
  hotSettings.data = buildData()
  hotSettings.colHeaders = buildColHeaders()
  hotSettings.columns = buildColumns()
  loaded.value = true
}

async function reload() {
  loaded.value = false
  try {
    await loadData()
  } catch (e) {
    loaded.value = true
    ElMessage.error(e.response?.data?.error || '加载失败')
  }
}

async function handleSave() {
  const currentData = hotSettings.data
  const payload = rows.value.map((r, idx) => {
    const row = currentData[idx] || []
    const costs = {}
    sizeColumns.value.forEach((size, i) => {
      const v = row[3 + i]
      if (v !== null && v !== undefined && v !== '') {
        costs[size] = v
      }
    })
    return { id: r.id, supplier: row[2] || '', costs }
  })

  saving.value = true
  try {
    const res = await saveChildrenClothingCosts(payload)
    ElMessage.success(res.data.message || '保存成功')
    await reload()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    await loadData()
  } catch (e) {
    loaded.value = true
    ElMessage.error(e.response?.data?.error || '加载失败')
  }
})
</script>

<style scoped>
.costs-page {
  padding: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.toolbar h2 {
  margin: 0;
  font-size: 20px;
}
.hint {
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}
.loading {
  padding: 40px;
  text-align: center;
  color: #909399;
}
</style>
