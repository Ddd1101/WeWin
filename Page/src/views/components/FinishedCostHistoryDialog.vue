<template>
  <el-dialog v-model="dialogVisible" title="成本历史" :width="isMobile ? '95%' : '880px'" :fullscreen="isMobile">
    <div v-loading="loading">
      <div v-if="row" class="history-info">
        <span>货号: {{ row.code }}</span>
        <span>商品名称: {{ row.name }}</span>
        <span>当前成本: <b>¥{{ formatPrice(row.cost_price) }}</b></span>
      </div>

      <el-empty v-if="!loading && history.length === 0" description="暂无成本历史" />

      <div v-else class="history-list">
        <div v-for="(h, index) in history" :key="h.id" class="history-item">
          <div class="history-header">
            <span class="history-time">{{ formatTime(h.created_at) }}</span>
            <span class="history-cost">¥{{ formatPrice(h.cost_price) }}</span>
            <span v-if="index > 0" class="history-delta" :class="deltaClass(index)">{{ deltaText(index) }}</span>
            <el-tag v-if="index === history.length - 1" size="small" type="success">当前</el-tag>
          </div>
          <div class="history-breakdown">
            <span>串珠: ¥{{ formatPrice(h.bead_cost) }}</span>
            <span>配件: ¥{{ formatPrice(h.accessory_cost) }}</span>
            <span>工费: ¥{{ formatPrice(h.labor_cost) }}</span>
            <span>弹性: ¥{{ formatPrice(h.elastic_cost) }}</span>
          </div>
          <div class="history-meta">
            <span v-if="h.trigger_reason">触发: {{ h.trigger_reason }}</span>
            <span v-if="h.created_by_name">操作人: {{ h.created_by_name }}</span>
          </div>

          <el-collapse v-if="hasBom(h)" class="history-bom">
            <el-collapse-item title="查看当时组成明细" name="bom">
              <div v-if="h.bom_snapshot.beads && h.bom_snapshot.beads.length" class="bom-section">
                <div class="bom-title">串珠</div>
                <div v-for="(b, bi) in h.bom_snapshot.beads" :key="'b' + bi" class="bom-row">
                  {{ b.code }}{{ b.sku_code ? ' / ' + b.sku_code : '' }} × {{ b.quantity }} = ¥{{ formatPrice(b.subtotal) }}（单价 ¥{{ formatPrice(b.unit_cost) }}）
                </div>
              </div>
              <div v-if="h.bom_snapshot.accessories && h.bom_snapshot.accessories.length" class="bom-section">
                <div class="bom-title">配件</div>
                <div v-for="(a, ai) in h.bom_snapshot.accessories" :key="'a' + ai" class="bom-row">
                  {{ a.code }}{{ a.sku_code ? ' / ' + a.sku_code : '' }} × {{ a.quantity }} = ¥{{ formatPrice(a.subtotal) }}（单价 ¥{{ formatPrice(a.unit_cost) }}）
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
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

const loadHistory = async () => {
  if (!props.row) return
  loading.value = true
  try {
    const res = await getFinishedCostHistory(props.row.id)
    history.value = res.data?.cost_history || []
  } catch (e) {
    history.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (val) => {
  if (val) loadHistory()
})

const formatPrice = (v) => {
  const n = Number(v) || 0
  return n.toFixed(2)
}

const formatTime = (iso) => {
  return iso ? new Date(iso).toLocaleString('zh-CN') : '-'
}

const deltaText = (index) => {
  if (index <= 0) return ''
  const d = Number(history.value[index].cost_price) - Number(history.value[index - 1].cost_price)
  return (d >= 0 ? '+' : '') + d.toFixed(2)
}

const deltaClass = (index) => {
  if (index <= 0) return ''
  const d = Number(history.value[index].cost_price) - Number(history.value[index - 1].cost_price)
  return d > 0 ? 'up' : d < 0 ? 'down' : 'flat'
}

const hasBom = (h) => {
  const b = h.bom_snapshot
  return b && ((b.beads && b.beads.length) || (b.accessories && b.accessories.length))
}
</script>

<style scoped>
.history-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 24px;
  padding: 10px 12px;
  margin-bottom: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 13px;
  color: #606266;
}

.history-info b {
  color: #303133;
}

.history-list {
  max-height: 60vh;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.history-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.history-time {
  color: #909399;
  font-size: 13px;
}

.history-cost {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.history-delta {
  font-size: 13px;
  font-weight: 700;
}

.history-delta.up {
  color: #ef4444;
}

.history-delta.down {
  color: #10b981;
}

.history-delta.flat {
  color: #909399;
}

.history-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 18px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.history-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 18px;
  font-size: 12px;
  color: #909399;
}

.history-bom {
  margin-top: 8px;
  border-top: 1px dashed #ebeef5;
}

.bom-section {
  margin-bottom: 8px;
}

.bom-title {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.bom-row {
  font-size: 12px;
  color: #606266;
  padding: 2px 0;
}
</style>
