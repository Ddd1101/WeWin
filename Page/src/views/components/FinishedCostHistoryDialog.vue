<template>
  <el-dialog
    v-model="dialogVisible"
    class="cost-history-dialog"
    :width="isMobile ? '96%' : '1000px'"
    :fullscreen="isMobile"
    destroy-on-close
  >
    <template #header>
      <div class="dialog-head">
        <div class="dialog-head-main">
          <div class="dialog-title">成本历史</div>
          <div v-if="row" class="dialog-sub">
            <span class="code">{{ row.code }}</span>
            <span class="divider">·</span>
            <span>{{ row.name }}</span>
          </div>
        </div>
        <el-tag v-if="history.length" size="small" effect="plain" round>{{ history.length }} 次快照</el-tag>
      </div>
    </template>

    <div v-loading="loading" class="ch-body">
      <template v-if="!loading && history.length">
        <!-- 概览 -->
        <section class="overview">
          <div class="overview-main">
            <div class="overview-label">当前成本</div>
            <div class="overview-value">¥{{ formatPrice(stats.current) }}</div>
            <div class="overview-delta" :class="deltaClass(stats.delta)">
              <template v-if="stats.delta !== null">
                较上次 <b>{{ formatSigned(stats.delta) }}</b>
              </template>
              <template v-else>首条快照</template>
            </div>
          </div>
          <div class="stat-grid">
            <div class="stat-card">
              <span class="stat-label">历史最高</span>
              <b class="stat-value up">¥{{ formatPrice(stats.highest) }}</b>
            </div>
            <div class="stat-card">
              <span class="stat-label">历史最低</span>
              <b class="stat-value down">¥{{ formatPrice(stats.lowest) }}</b>
            </div>
            <div class="stat-card">
              <span class="stat-label">平均成本</span>
              <b class="stat-value">¥{{ formatPrice(stats.avg) }}</b>
            </div>
            <div class="stat-card">
              <span class="stat-label">快照数量</span>
              <b class="stat-value">{{ stats.count }} 次</b>
            </div>
          </div>
        </section>

        <!-- 走势 -->
        <section v-if="chart && history.length > 1" class="trend-card">
          <div class="section-head">
            <div>
              <div class="section-title">成本走势</div>
              <div class="section-sub">按快照时间顺序展示</div>
            </div>
            <span class="section-tag">¥{{ formatPrice(stats.lowest) }} ~ ¥{{ formatPrice(stats.highest) }}</span>
          </div>
          <div class="chart-wrap" @mouseleave="hoverIndex = -1">
            <svg class="chart-svg" viewBox="0 0 720 220" role="img" aria-label="成本走势图">
              <defs>
                <linearGradient id="costArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#2563eb" stop-opacity="0.18" />
                  <stop offset="100%" stop-color="#2563eb" stop-opacity="0" />
                </linearGradient>
              </defs>
              <g>
                <line
                  v-for="(g, gi) in chart.grid"
                  :key="'grid' + gi"
                  :x1="chart.padX"
                  :x2="chart.width - chart.padX"
                  :y1="g.y"
                  :y2="g.y"
                  stroke="#eef2f7"
                  stroke-dasharray="4 4"
                />
                <text
                  v-for="(g, gi) in chart.grid"
                  :key="'grid-label' + gi"
                  x="8"
                  :y="g.y + 4"
                  fill="#94a3b8"
                  font-size="11"
                >¥{{ formatPrice(g.value) }}</text>
              </g>
              <path :d="chart.area" fill="url(#costArea)" />
              <polyline
                :points="chart.line"
                fill="none"
                stroke="#2563eb"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <g v-for="(p, pi) in chart.points" :key="'point' + p.id">
                <circle :cx="p.x" :cy="p.y" r="4" fill="#fff" stroke="#2563eb" stroke-width="2" />
                <circle
                  :cx="p.x"
                  :cy="p.y"
                  r="14"
                  fill="transparent"
                  class="chart-hit"
                  @mouseenter="hoverIndex = pi"
                />
              </g>
              <text
                v-for="(p, pi) in chart.labels"
                :key="'x-label' + pi"
                :x="p.x"
                y="212"
                text-anchor="middle"
                fill="#94a3b8"
                font-size="11"
              >{{ formatShortDate(p.created_at) }}</text>
            </svg>
            <div v-if="hoverPoint" class="chart-tip" :style="tipStyle">
              <div class="tip-date">{{ formatTime(hoverPoint.created_at) }}</div>
              <div class="tip-cost">¥{{ formatPrice(hoverPoint.cost_price) }}</div>
              <div v-if="hoverPoint.trigger_reason" class="tip-reason">{{ hoverPoint.trigger_reason }}</div>
            </div>
          </div>
        </section>

        <!-- 筛选 -->
        <section class="filter-bar">
          <span class="filter-title">筛选记录</span>
          <el-select v-model="rangeFilter" size="small" class="filter-select">
            <el-option label="全部时间" value="all" />
            <el-option label="近 30 天" value="30" />
            <el-option label="近 90 天" value="90" />
            <el-option label="近一年" value="365" />
          </el-select>
          <el-select v-model="typeFilter" size="small" class="filter-select">
            <el-option label="全部类型" value="all" />
            <el-option label="物料变动" value="material" />
            <el-option label="初始化快照" value="init" />
            <el-option label="手工调整" value="manual" />
            <el-option label="其他" value="other" />
          </el-select>
          <el-checkbox v-model="onlyChanged" size="small">只看有变化</el-checkbox>
          <span class="filter-count">{{ filteredHistory.length }} / {{ history.length }} 条</span>
        </section>
      </template>

      <div v-if="loadError && !loading" class="load-error">
        <el-alert :title="loadError" type="error" :closable="false" show-icon />
        <el-button size="small" @click="loadHistory">重新加载</el-button>
      </div>
      <el-empty
        v-else-if="!loading && history.length === 0"
        description="暂无成本历史"
      />
      <div v-else-if="!loading && filteredHistory.length === 0" class="filter-empty">
        <div class="filter-empty-title">没有符合筛选条件的记录</div>
        <div class="filter-empty-sub">试试切换时间范围或取消“只看有变化”</div>
        <el-button size="small" @click="resetFilters">重置筛选</el-button>
      </div>
      <div v-else-if="!loading" class="timeline">
        <article
          v-for="item in filteredHistory"
          :key="item.id"
          class="timeline-item"
          :class="[deltaClass(item._delta), { current: item._isCurrent }]"
        >
          <div class="timeline-axis">
            <span class="timeline-dot"></span>
            <span class="timeline-line"></span>
          </div>
          <div class="timeline-card">
            <div class="card-head">
              <div class="card-time">
                <span class="date">{{ formatDate(item.created_at) }}</span>
                <span class="clock">{{ formatClock(item.created_at) }}</span>
              </div>
              <div class="card-cost-wrap">
                <span class="card-cost">¥{{ formatPrice(item.cost_price) }}</span>
                <span
                  v-if="item._delta !== null"
                  class="delta-pill"
                  :class="deltaClass(item._delta)"
                >{{ formatSigned(item._delta) }}</span>
                <span v-if="item._isCurrent" class="current-tag">当前</span>
              </div>
            </div>

            <div class="trigger-row">
              <span class="trigger-label">触发</span>
              <span class="trigger-text">{{ item.trigger_reason || '—' }}</span>
              <span v-if="item.created_by_name" class="operator">操作人 {{ item.created_by_name }}</span>
            </div>

            <div class="stack-bar">
              <span
                v-for="c in item._composition"
                :key="c.key"
                class="stack-seg"
                :style="{ width: c.pct + '%', background: c.color }"
                :title="`${c.label} ¥${formatPrice(c.value)}`"
              ></span>
            </div>
            <div class="comp-legend">
              <span v-for="c in item._composition" :key="c.key" class="comp-item">
                <i class="comp-dot" :style="{ background: c.color }"></i>{{ c.label }} ¥{{ formatPrice(c.value) }}
              </span>
            </div>

            <button
              v-if="hasBom(item)"
              type="button"
              class="bom-toggle"
              @click="toggleBom(item.id)"
            >
              <span>查看当时组成明细</span>
              <span class="bom-toggle-action">
                {{ expandedBoms[item.id] ? '收起' : '展开' }}
                <span class="chevron" :class="{ open: expandedBoms[item.id] }">›</span>
              </span>
            </button>
            <div v-if="expandedBoms[item.id] && hasBom(item)" class="bom-panel">
              <div v-for="group in bomGroups(item)" :key="group.key" class="bom-group">
                <div class="bom-group-title">
                  <i class="comp-dot" :style="{ background: group.color }"></i>
                  {{ group.label }}
                  <span class="muted">{{ group.items.length }} 项</span>
                </div>
                <div class="bom-table">
                  <div class="bom-row bom-row-head">
                    <span>货号 / SKU</span>
                    <span>数量</span>
                    <span>单价</span>
                    <span>小计</span>
                  </div>
                  <div v-for="(b, bi) in group.items" :key="bi" class="bom-row">
                    <span class="bom-name">{{ b.code }}{{ b.sku_code ? ' / ' + b.sku_code : '' }}</span>
                    <span>× {{ b.quantity }}</span>
                    <span>¥{{ formatPrice(b.unit_cost) }}</span>
                    <span class="bom-subtotal">¥{{ formatPrice(b.subtotal) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <span v-if="stats" class="footer-note">
          共 {{ stats.count }} 条快照 · 当前成本 ¥{{ formatPrice(stats.current) }}
        </span>
        <span v-else class="footer-note">成本变化后会自动生成快照</span>
        <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getFinishedCostHistory } from '../../api/store'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  row: {
    type: Object,
    default: null
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const history = ref([])
const loading = ref(false)
const loadError = ref('')

const rangeFilter = ref('all')
const typeFilter = ref('all')
const onlyChanged = ref(false)
const expandedBoms = ref({})
const hoverIndex = ref(-1)

const CHART = { width: 720, height: 220, padX: 44, padTop: 24, padBottom: 34 }

const loadHistory = async () => {
  if (!props.row) return
  loading.value = true
  loadError.value = ''
  try {
    const res = await getFinishedCostHistory(props.row.id)
    const list = res.data?.cost_history || []
    history.value = [...list].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  } catch (e) {
    history.value = []
    loadError.value = '成本历史加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (val) => {
  if (!val) return
  rangeFilter.value = 'all'
  typeFilter.value = 'all'
  onlyChanged.value = false
  expandedBoms.value = {}
  hoverIndex.value = -1
  loadHistory()
})

const formatPrice = (v) => {
  const n = Number(v) || 0
  return n.toFixed(2)
}

const formatTime = (iso) => {
  return iso ? new Date(iso).toLocaleString('zh-CN') : '-'
}

const formatDate = (iso) => {
  return iso
    ? new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
    : '-'
}

const formatClock = (iso) => {
  return iso
    ? new Date(iso).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    : ''
}

const formatShortDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

const formatSigned = (v) => {
  if (v === null || v === undefined) return ''
  const n = Number(v)
  return `${n > 0 ? '+' : ''}${n.toFixed(2)}`
}

const deltaClass = (v) => {
  if (v === null || v === undefined) return ''
  return Number(v) > 0 ? 'up' : Number(v) < 0 ? 'down' : 'flat'
}

const classifyTrigger = (reason = '') => {
  if (reason.includes('串珠') || reason.includes('配件') || reason.includes('SKU')) return 'material'
  if (reason.includes('初始化')) return 'init'
  if (reason.includes('核算') || reason.includes('调整') || reason.includes('手工')) return 'manual'
  return 'other'
}

const compositionOf = (h) => {
  const items = [
    { key: 'bead', label: '串珠', value: Number(h.bead_cost) || 0, color: '#3b82f6' },
    { key: 'accessory', label: '配件', value: Number(h.accessory_cost) || 0, color: '#8b5cf6' },
    { key: 'labor', label: '工费', value: Number(h.labor_cost) || 0, color: '#f59e0b' },
    { key: 'elastic', label: '弹性', value: Number(h.elastic_cost) || 0, color: '#14b8a6' }
  ]
  const total = items.reduce((sum, item) => sum + item.value, 0)
  return items.map((item) => ({
    ...item,
    pct: total > 0 ? (item.value / total) * 100 : 0
  }))
}

const enrichedHistory = computed(() => history.value.map((h, index) => {
  const cost = Number(h.cost_price) || 0
  const prev = index > 0 ? Number(history.value[index - 1].cost_price) || 0 : null
  return {
    ...h,
    _cost: cost,
    _index: index,
    _delta: prev === null ? null : cost - prev,
    _isCurrent: index === history.value.length - 1,
    _type: classifyTrigger(h.trigger_reason),
    _composition: compositionOf(h)
  }
}))

const stats = computed(() => {
  if (!enrichedHistory.value.length) return null
  const costs = enrichedHistory.value.map((h) => h._cost)
  const current = costs[costs.length - 1]
  return {
    current,
    delta: costs.length > 1 ? current - costs[costs.length - 2] : null,
    highest: Math.max(...costs),
    lowest: Math.min(...costs),
    avg: costs.reduce((sum, v) => sum + v, 0) / costs.length,
    count: costs.length
  }
})

const filteredHistory = computed(() => {
  const now = Date.now()
  return [...enrichedHistory.value].reverse().filter((item) => {
    if (rangeFilter.value !== 'all') {
      const days = Number(rangeFilter.value)
      const time = new Date(item.created_at).getTime()
      if (!Number.isNaN(time) && now - time > days * 24 * 60 * 60 * 1000) return false
    }
    if (typeFilter.value !== 'all' && item._type !== typeFilter.value) return false
    if (onlyChanged.value && !item._delta) return false
    return true
  })
})

const chart = computed(() => {
  const items = enrichedHistory.value
  if (!items.length) return null
  const values = items.map((item) => item._cost)
  let min = Math.min(...values)
  let max = Math.max(...values)
  if (max === min) {
    max = min + 1
    min = Math.max(0, min - 1)
  }
  const innerW = CHART.width - CHART.padX * 2
  const innerH = CHART.height - CHART.padTop - CHART.padBottom
  const points = items.map((item, index) => ({
    ...item,
    x: items.length === 1 ? CHART.width / 2 : CHART.padX + (innerW * index) / (items.length - 1),
    y: CHART.padTop + (1 - (item._cost - min) / (max - min)) * innerH
  }))
  const baseline = CHART.height - CHART.padBottom
  const area = `M ${points[0].x} ${baseline} L ${points.map((p) => `${p.x} ${p.y}`).join(' L ')} L ${points[points.length - 1].x} ${baseline} Z`
  const grid = [0, 0.25, 0.5, 0.75, 1].map((ratio) => ({
    y: CHART.padTop + innerH * ratio,
    value: max - (max - min) * ratio
  }))
  const labels = points.filter((p, index) => {
    if (points.length <= 6) return true
    return index === 0 || index === points.length - 1 || index === Math.floor((points.length - 1) / 2)
  })
  return {
    width: CHART.width,
    padX: CHART.padX,
    points,
    line: points.map((p) => `${p.x},${p.y}`).join(' '),
    area,
    grid,
    labels
  }
})

const hoverPoint = computed(() => {
  if (hoverIndex.value < 0 || !chart.value) return null
  return chart.value.points[hoverIndex.value] || null
})

const tipStyle = computed(() => {
  if (!hoverPoint.value) return {}
  const left = Math.min(88, Math.max(12, (hoverPoint.value.x / CHART.width) * 100))
  return {
    left: `${left}%`,
    top: `${(hoverPoint.value.y / CHART.height) * 100}%`
  }
})

const hasBom = (h) => {
  const b = h.bom_snapshot
  return b && ((b.beads && b.beads.length) || (b.accessories && b.accessories.length))
}

const bomGroups = (h) => {
  const b = h.bom_snapshot || {}
  return [
    { key: 'beads', label: '串珠', color: '#3b82f6', items: b.beads || [] },
    { key: 'accessories', label: '配件', color: '#8b5cf6', items: b.accessories || [] }
  ].filter((group) => group.items.length > 0)
}

const toggleBom = (id) => {
  expandedBoms.value = { ...expandedBoms.value, [id]: !expandedBoms.value[id] }
}

const resetFilters = () => {
  rangeFilter.value = 'all'
  typeFilter.value = 'all'
  onlyChanged.value = false
}
</script>

<style scoped>
.cost-history-dialog {
  --ch-text: #0f172a;
  --ch-muted: #64748b;
  --ch-border: #e2e8f0;
  --ch-soft: #f8fafc;
  --ch-primary: #2563eb;
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  margin: 0;
  padding: 20px 24px 0;
}

:deep(.el-dialog__headerbtn) {
  top: 18px;
  right: 18px;
}

:deep(.el-dialog__body) {
  padding: 16px 24px 4px;
  max-height: 72vh;
  overflow-y: auto;
  color: var(--ch-text);
}

:deep(.el-dialog__footer) {
  padding: 12px 24px 18px;
  border-top: 1px solid #eef2f7;
}

.dialog-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-right: 28px;
}

.dialog-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.dialog-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 5px;
  font-size: 13px;
  color: var(--ch-muted);
}

.dialog-sub .code {
  font-weight: 600;
  color: #334155;
}

.dialog-sub .divider {
  color: #cbd5e1;
}

.ch-body {
  min-height: 180px;
}

.overview {
  display: grid;
  grid-template-columns: minmax(180px, 0.9fr) 2fr;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e8eef7;
  border-radius: 14px;
  background:
    radial-gradient(circle at 0% 0%, rgba(37, 99, 235, 0.08), transparent 42%),
    linear-gradient(180deg, #fbfdff, #ffffff);
}

.overview-label {
  font-size: 13px;
  color: var(--ch-muted);
}

.overview-value {
  margin-top: 6px;
  font-size: 32px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.5px;
  font-variant-numeric: tabular-nums;
}

.overview-delta {
  margin-top: 8px;
  font-size: 12px;
  color: var(--ch-muted);
}

.overview-delta b {
  font-variant-numeric: tabular-nums;
}

.overview-delta.up b {
  color: #ef4444;
}

.overview-delta.down b {
  color: #10b981;
}

.overview-delta.flat b {
  color: #64748b;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border: 1px solid #eef2f7;
  border-radius: 10px;
  background: #fff;
}

.stat-label {
  font-size: 12px;
  color: var(--ch-muted);
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stat-value.up {
  color: #ef4444;
}

.stat-value.down {
  color: #10b981;
}

.trend-card {
  margin-top: 14px;
  padding: 16px 18px 6px;
  border: 1px solid #eef2f7;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fafc, #ffffff);
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 4px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
}

.section-sub {
  margin-top: 3px;
  font-size: 12px;
  color: var(--ch-muted);
}

.section-tag {
  padding: 4px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #fff;
  font-size: 12px;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

.chart-wrap {
  position: relative;
  margin-top: 4px;
}

.chart-svg {
  width: 100%;
  height: auto;
  display: block;
  overflow: visible;
}

.chart-hit {
  cursor: crosshair;
}

.chart-tip {
  position: absolute;
  z-index: 2;
  transform: translate(-50%, -110%);
  min-width: 140px;
  max-width: 280px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #0f172a;
  color: #fff;
  font-size: 12px;
  line-height: 1.5;
  pointer-events: none;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.2);
}

.tip-date {
  color: #cbd5e1;
}

.tip-cost {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.tip-reason {
  margin-top: 2px;
  color: #cbd5e1;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin: 16px 0 12px;
  padding: 10px 12px;
  border: 1px solid #eef2f7;
  border-radius: 10px;
  background: #fff;
}

.filter-title {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.filter-select {
  width: 122px;
}

.filter-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--ch-muted);
  font-variant-numeric: tabular-nums;
}

.timeline {
  padding: 2px 0 4px;
}

.timeline-item {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 12px;
}

.timeline-axis {
  position: relative;
  display: flex;
  justify-content: center;
}

.timeline-dot {
  position: relative;
  z-index: 1;
  width: 10px;
  height: 10px;
  margin-top: 24px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #cbd5e1;
  box-shadow: 0 0 0 2px #e2e8f0;
}

.timeline-item.up .timeline-dot {
  background: #ef4444;
  box-shadow: 0 0 0 2px #fee2e2;
}

.timeline-item.down .timeline-dot {
  background: #10b981;
  box-shadow: 0 0 0 2px #d1fae5;
}

.timeline-item.current .timeline-dot {
  background: var(--ch-primary);
  box-shadow: 0 0 0 3px #dbeafe;
}

.timeline-line {
  position: absolute;
  top: 34px;
  bottom: -10px;
  width: 2px;
  background: #eef2f7;
}

.timeline-item:last-child .timeline-line {
  display: none;
}

.timeline-card {
  margin-bottom: 14px;
  padding: 14px 16px;
  border: 1px solid #e8eef7;
  border-radius: 12px;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.timeline-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.timeline-item.current .timeline-card {
  border-color: #bfdbfe;
  background: linear-gradient(180deg, #f8fbff, #ffffff);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.08);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.card-time {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.card-time .date {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.card-time .clock {
  font-size: 12px;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
}

.card-cost-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-cost {
  font-size: 20px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.delta-pill {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.delta-pill.up {
  background: #fef2f2;
  color: #dc2626;
}

.delta-pill.down {
  background: #ecfdf5;
  color: #059669;
}

.delta-pill.flat {
  background: #f1f5f9;
  color: #64748b;
}

.current-tag {
  padding: 2px 8px;
  border-radius: 999px;
  background: #eff6ff;
  color: var(--ch-primary);
  font-size: 12px;
  font-weight: 600;
}

.trigger-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px 8px;
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.6;
}

.trigger-label {
  flex: 0 0 auto;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #64748b;
}

.trigger-text {
  flex: 1 1 240px;
  color: #475569;
  word-break: break-word;
}

.operator {
  color: #94a3b8;
}

.stack-bar {
  display: flex;
  height: 8px;
  margin: 12px 0 8px;
  border-radius: 999px;
  overflow: hidden;
  background: #f1f5f9;
}

.stack-seg {
  height: 100%;
  transition: width 0.3s ease;
}

.comp-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  font-size: 12px;
  color: var(--ch-muted);
  font-variant-numeric: tabular-nums;
}

.comp-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.comp-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.bom-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 12px;
  padding: 10px 0 0;
  border: 0;
  border-top: 1px dashed #e2e8f0;
  background: transparent;
  color: var(--ch-primary);
  font-size: 12px;
  cursor: pointer;
}

.bom-toggle-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
}

.chevron {
  display: inline-block;
  font-size: 16px;
  line-height: 1;
  transition: transform 0.2s ease;
}

.chevron.open {
  transform: rotate(90deg);
}

.bom-panel {
  margin-top: 10px;
  padding: 12px;
  border: 1px solid #eef2f7;
  border-radius: 10px;
  background: var(--ch-soft);
}

.bom-group + .bom-group {
  margin-top: 14px;
}

.bom-group-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
}

.bom-group-title .muted {
  font-weight: 400;
}

.bom-table {
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.bom-row {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) 52px 76px 86px;
  gap: 8px;
  align-items: center;
  padding: 7px 10px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 12px;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

.bom-row:last-child {
  border-bottom: 0;
}

.bom-row-head {
  background: #f8fafc;
  font-size: 11px;
  color: #94a3b8;
}

.bom-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bom-subtotal {
  font-weight: 600;
  color: #0f172a;
}

.muted {
  color: #94a3b8;
}

.filter-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px 0;
  text-align: center;
}

.filter-empty-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.filter-empty-sub {
  font-size: 12px;
  color: var(--ch-muted);
}

.load-error {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  padding: 16px 0;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.footer-note {
  font-size: 12px;
  color: var(--ch-muted);
  font-variant-numeric: tabular-nums;
}

@media (max-width: 768px) {
  :deep(.el-dialog__header) {
    padding: 16px 16px 0;
  }

  :deep(.el-dialog__body) {
    max-height: none;
    padding: 12px 14px 4px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 16px 14px;
  }

  .dialog-title {
    font-size: 18px;
  }

  .overview {
    grid-template-columns: 1fr;
    padding: 14px;
  }

  .overview-value {
    font-size: 28px;
  }

  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .trend-card {
    padding: 14px 12px 4px;
  }

  .filter-bar {
    gap: 8px;
  }

  .filter-select {
    flex: 1 1 120px;
    width: auto;
  }

  .filter-count {
    width: 100%;
    margin-left: 0;
  }

  .timeline {
    padding-left: 0;
  }

  .timeline-item {
    grid-template-columns: 14px minmax(0, 1fr);
    gap: 8px;
  }

  .timeline-card {
    padding: 12px;
  }

  .card-head {
    flex-direction: column;
    gap: 6px;
  }

  .card-cost {
    font-size: 18px;
  }

  .bom-row {
    grid-template-columns: minmax(0, 1.4fr) 40px 62px 72px;
    gap: 6px;
    padding: 6px 8px;
    font-size: 11px;
  }

  .dialog-footer {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .dialog-footer .el-button {
    width: 100%;
  }
}
</style>
