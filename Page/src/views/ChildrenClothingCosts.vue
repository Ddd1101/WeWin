<template>
  <div class="costs-page">
    <div class="sheet-head">
      <div class="head-main">
        <span class="eyebrow">CHILDRENSWEAR · COST MATRIX</span>
        <div class="title-row">
          <h2>童装成本表</h2>
          <span class="sync-state" :class="dirty ? 'is-dirty' : 'is-clean'">
            <i class="dot"></i>
            {{ dirty ? '有未保存修改' : '已同步' }}
          </span>
        </div>
        <div class="meta-row">
          <span><b>{{ rows.length }}</b> 个货号</span>
          <span class="sep">/</span>
          <span><b>{{ sizeColumns.length }}</b> 个尺码</span>
          <span class="sep">/</span>
          <span><b>{{ supplierCount }}</b> 家供应商</span>
        </div>
      </div>
      <div class="head-actions">
        <el-button :icon="Refresh" :disabled="saving" @click="reload">刷新</el-button>
        <el-button type="primary" :icon="Check" :loading="saving" @click="handleSave">
          保存更改
        </el-button>
      </div>
    </div>

    <div class="hint">
      <el-icon><InfoFilled /></el-icon>
      <span>行 = 货号，列 = 尺码。货号与名称只读，供应商及各尺码成本可直接编辑；清空某个尺码单元格即删除该尺码。</span>
    </div>

    <div v-if="loaded" class="sheet-wrap">
      <HotTable ref="hotTableRef" :settings="hotSettings" />
    </div>
    <div v-else class="sheet-skeleton" aria-busy="true">
      <div class="skeleton-head"></div>
      <div v-for="n in 7" :key="n" class="skeleton-row"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { HotTable } from '@handsontable/vue3'
import { registerAllModules } from 'handsontable/registry'
import { ElMessage } from 'element-plus'
import { Check, Refresh, InfoFilled } from '@element-plus/icons-vue'
import 'handsontable/styles/handsontable.min.css'
import 'handsontable/styles/ht-theme-main.min.css'
import { getChildrenClothingCosts, saveChildrenClothingCosts } from '@/api'

registerAllModules()

const hotTableRef = ref(null)
const rows = ref([])
const sizeColumns = ref([])
const saving = ref(false)
const loaded = ref(false)
const dirty = ref(false)

// 加载数据时忽略 Handsontable 自身触发的变更回调
let suspendTrack = false

const supplierCount = computed(() => {
  const set = new Set()
  for (const r of rows.value) {
    const name = (r.supplier || '').trim()
    if (name) set.add(name)
  }
  return set.size
})

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
  afterChange: (changes) => {
    if (!suspendTrack && changes && changes.length > 0) {
      dirty.value = true
    }
  },
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
  suspendTrack = true
  rows.value = res.data.rows || []
  sizeColumns.value = res.data.columns || []
  hotSettings.data = buildData()
  hotSettings.colHeaders = buildColHeaders()
  hotSettings.columns = buildColumns()
  loaded.value = true
  await nextTick()
  dirty.value = false
  suspendTrack = false
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
    dirty.value = false
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
  --ink: #1e293b;
  --muted: #64748b;
  --line: #e2e8f0;
  --accent: #0f766e;
  --accent-soft: #ecfdf5;
  padding: 2px 2px 8px;
  color: var(--ink);
  animation: rise 0.35s ease both;
}

/* 头部 */
.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--line);
}

.eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.18em;
  color: var(--muted);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.title-row h2 {
  position: relative;
  margin: 0;
  padding-left: 12px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.2;
  color: var(--ink);
}

.title-row h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 3px;
  height: 20px;
  border-radius: 2px;
  background: var(--accent);
  transform: translateY(-50%);
}

.sync-state {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  background: #f1f5f9;
  color: var(--muted);
}

.sync-state.is-dirty {
  background: #fff7ed;
  color: #b45309;
}

.sync-state .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.sync-state.is-dirty .dot {
  animation: pulse 1.6s ease-in-out infinite;
}

.meta-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 10px;
  font-size: 13px;
  color: var(--muted);
}

.meta-row b {
  font-family: ui-monospace, "SF Mono", Consolas, monospace;
  font-size: 16px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
}

.meta-row .sep {
  color: #cbd5e1;
}

.head-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.head-actions :deep(.el-button--primary) {
  --el-button-bg-color: var(--accent);
  --el-button-border-color: var(--accent);
  --el-button-hover-bg-color: #0d9488;
  --el-button-hover-border-color: #0d9488;
  --el-button-active-bg-color: #115e59;
  --el-button-active-border-color: #115e59;
}

/* 提示条 */
.hint {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 14px 0;
  padding: 10px 14px;
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: #f8fafc;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--muted);
}

.hint .el-icon {
  margin-top: 2px;
  color: var(--accent);
  flex-shrink: 0;
}

/* 表格容器 */
.sheet-wrap {
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 12px 28px -18px rgba(15, 23, 42, 0.28);
  animation: rise 0.4s ease both;
}

.sheet-wrap :deep(.handsontable) {
  --ht-accent-color: #0f766e;
  --ht-background-secondary-color: #f8fafc;
  --ht-border-color: #e2e8f0;
  --ht-foreground-color: #1e293b;
  --ht-read-only-color: #94a3b8;
  font-family: ui-monospace, "SF Mono", Consolas, "PingFang SC", "Microsoft YaHei", monospace;
  font-size: 13px;
  color: var(--ink);
}

.sheet-wrap :deep(.handsontable th) {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.sheet-wrap :deep(.handsontable td) {
  border-color: #eef2f7;
  font-variant-numeric: tabular-nums;
}

.sheet-wrap :deep(.handsontable td.htDimmed) {
  background: #fbfcfe;
  color: #94a3b8;
}

/* 加载骨架 */
.sheet-skeleton {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.skeleton-head,
.skeleton-row {
  border-radius: 8px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e8eef5 37%, #f1f5f9 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}

.skeleton-head {
  height: 38px;
  margin-bottom: 10px;
}

.skeleton-row {
  height: 34px;
  margin-bottom: 8px;
}

.skeleton-row:last-child {
  margin-bottom: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .sheet-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .title-row h2 {
    font-size: 19px;
  }

  .head-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .hint {
    font-size: 12px;
  }
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: 0 0;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}

@media (prefers-reduced-motion: reduce) {
  .costs-page,
  .sheet-wrap,
  .skeleton-head,
  .skeleton-row,
  .sync-state.is-dirty .dot {
    animation: none;
  }
}
</style>
