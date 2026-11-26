<template>
  <el-dialog v-model="dialogVisible" title="克价模拟" :width="isMobile ? '95%' : '1200px'" :fullscreen="isMobile">
    <div v-if="row" class="simulate-content">
      <div class="simulate-info" :class="{ 'simulate-info-mobile': isMobile }">
        <span>货号: {{ row.code }}</span>
        <span>商品名称: {{ row.name }}</span>
        <span>售价: ¥{{ row.selling_price.toFixed(2) }}</span>
      </div>

      <!-- 桌面端：表格布局 -->
      <template v-if="!isMobile">
        <table class="detail-table simulate-table" v-if="simulateBeads.length > 0">
          <thead>
            <tr>
              <th colspan="9" class="detail-table-header">串珠（{{ simulateBeads.length }}种，共{{ calculateBeadsQuantity(simulateBeads) }}颗）</th>
            </tr>
            <tr>
              <th style="width:140px">SKU名称</th>
              <th style="width:50px">数量</th>
              <th style="width:60px">克重</th>
              <th style="width:80px">原克价</th>
              <th style="width:140px">新克价(元/克)</th>
              <th style="width:70px">原单价</th>
              <th style="width:70px">新单价</th>
              <th style="width:70px">原小计</th>
              <th style="width:70px">新小计</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(bead, index) in simulateBeads" :key="'b'+index">
              <td class="simulate-text">{{ bead.sku?.name || bead.sku?.sku_name || bead.bead_name }}</td>
              <td>{{ bead.quantity }}</td>
              <td>{{ bead.bead_weight ? bead.bead_weight.toFixed(2) + 'g' : '-' }}</td>
              <td>¥{{ formatPrice(bead.bead_purchase_cost, 2) }}</td>
              <td>
                <el-input-number v-model="bead.newPurchaseCost" :min="0" :step="0.01" :precision="2" :controls="false" size="small" class="simulate-input" />
              </td>
              <td>¥{{ bead.bead_cost_price.toFixed(2) }}</td>
              <td>¥{{ (bead.newPurchaseCost * (bead.bead_weight || 0)).toFixed(2) }}</td>
              <td>¥{{ (bead.bead_cost_price * bead.quantity).toFixed(2) }}</td>
              <td>¥{{ (bead.newPurchaseCost * (bead.bead_weight || 0) * bead.quantity).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
        <table class="detail-table simulate-table" v-if="simulateAccessories.length > 0">
          <thead>
            <tr>
              <th colspan="7" class="detail-table-header">配件（{{ simulateAccessories.length }}种，共{{ calculateAccessoriesQuantity(simulateAccessories) }}个）</th>
            </tr>
            <tr>
              <th style="width:140px">SKU名称</th>
              <th style="width:50px">数量</th>
              <th style="width:80px">原单价</th>
              <th style="width:130px">新单价</th>
              <th style="width:70px">原小计</th>
              <th style="width:70px">新小计</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(acc, index) in simulateAccessories" :key="'a'+index">
              <td class="simulate-text">{{ acc.sku?.name || acc.sku?.sku_name || acc.accessory_name }}</td>
              <td>{{ acc.quantity }}</td>
              <td>¥{{ acc.accessory_cost_price.toFixed(2) }}</td>
              <td>
                <el-input-number v-model="acc.newCostPrice" :min="0" :step="0.01" :precision="2" :controls="false" size="small" class="simulate-input" />
              </td>
              <td>¥{{ (acc.accessory_cost_price * acc.quantity).toFixed(2) }}</td>
              <td>¥{{ (acc.newCostPrice * acc.quantity).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- 手机端：卡片式布局 -->
      <template v-else>
        <div v-if="simulateBeads.length > 0" class="simulate-mobile-section">
          <div class="simulate-mobile-title">串珠（{{ simulateBeads.length }}种，共{{ calculateBeadsQuantity(simulateBeads) }}颗）</div>
          <div v-for="(bead, index) in simulateBeads" :key="'mb'+index" class="simulate-mobile-card">
            <div class="simulate-mobile-card-header">{{ bead.sku?.name || bead.sku?.sku_name || bead.bead_name }}</div>
            <div class="simulate-mobile-grid">
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">数量</span>
                <span>{{ bead.quantity }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">克重</span>
                <span>{{ bead.bead_weight ? bead.bead_weight.toFixed(2) + 'g' : '-' }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">原克价</span>
                <span>¥{{ formatPrice(bead.bead_purchase_cost, 2) }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">新克价</span>
                <el-input-number v-model="bead.newPurchaseCost" :min="0" :step="0.01" :precision="2" :controls="false" size="small" class="simulate-input-mobile" />
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">原单价</span>
                <span>¥{{ bead.bead_cost_price.toFixed(2) }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">新单价</span>
                <span>¥{{ (bead.newPurchaseCost * (bead.bead_weight || 0)).toFixed(2) }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">原小计</span>
                <span>¥{{ (bead.bead_cost_price * bead.quantity).toFixed(2) }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">新小计</span>
                <span :style="{ color: (bead.newPurchaseCost * (bead.bead_weight || 0) * bead.quantity) > (bead.bead_cost_price * bead.quantity) ? '#ef4444' : '#10b981' }">¥{{ (bead.newPurchaseCost * (bead.bead_weight || 0) * bead.quantity).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="simulateAccessories.length > 0" class="simulate-mobile-section">
          <div class="simulate-mobile-title">配件（{{ simulateAccessories.length }}种，共{{ calculateAccessoriesQuantity(simulateAccessories) }}个）</div>
          <div v-for="(acc, index) in simulateAccessories" :key="'ma'+index" class="simulate-mobile-card">
            <div class="simulate-mobile-card-header">{{ acc.sku?.name || acc.sku?.sku_name || acc.accessory_name }}</div>
            <div class="simulate-mobile-grid">
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">数量</span>
                <span>{{ acc.quantity }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">原单价</span>
                <span>¥{{ acc.accessory_cost_price.toFixed(2) }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">新单价</span>
                <el-input-number v-model="acc.newCostPrice" :min="0" :step="0.01" :precision="2" :controls="false" size="small" class="simulate-input-mobile" />
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">原小计</span>
                <span>¥{{ (acc.accessory_cost_price * acc.quantity).toFixed(2) }}</span>
              </div>
              <div class="simulate-mobile-row">
                <span class="simulate-mobile-label">新小计</span>
                <span :style="{ color: (acc.newCostPrice * acc.quantity) > (acc.accessory_cost_price * acc.quantity) ? '#ef4444' : '#10b981' }">¥{{ (acc.newCostPrice * acc.quantity).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div class="simulate-summary" :class="{ 'simulate-summary-mobile': isMobile }">
        <div class="summary-row">
          <span>原测算成本: <b>¥{{ simulateOriginalCost.toFixed(2) }}</b></span>
          <span>新测算成本: <b :style="{ color: simulateNewCost > simulateOriginalCost ? '#ef4444' : '#10b981' }">¥{{ simulateNewCost.toFixed(2) }}</b></span>
          <span>成本变动: <b :style="{ color: simulateNewCost > simulateOriginalCost ? '#ef4444' : '#10b981' }">{{ simulateNewCost > simulateOriginalCost ? '+' : '' }}¥{{ (simulateNewCost - simulateOriginalCost).toFixed(2) }}</b></span>
        </div>
        <div class="summary-row">
          <span>测算原利润: <b>¥{{ (row.selling_price - simulateOriginalCost).toFixed(2) }}</b></span>
          <span>测算新利润: <b :style="{ color: (row.selling_price - simulateNewCost) >= 0 ? '#10b981' : '#ef4444' }">¥{{ (row.selling_price - simulateNewCost).toFixed(2) }}</b></span>
          <span>原利润率: <b>{{ row.selling_price > 0 ? ((row.selling_price - simulateOriginalCost) / row.selling_price * 100).toFixed(1) : 0 }}%</b></span>
          <span>新利润率: <b :style="{ color: simulateNewProfitRate >= 30 ? '#10b981' : simulateNewProfitRate >= 15 ? '#f59e0b' : '#ef4444' }">{{ simulateNewProfitRate }}%</b></span>
        </div>
      </div>
    </div>
    <el-alert v-if="row?.finished?.cost_mode === 'manual'" type="info" :closable="false" :title="`本模拟仅测算组成成本，独立采用成本 ¥${Number(row.cost_price).toFixed(2)} 不变；测算利润不代表当前实际采用成本下的利润。`" />
    <template #footer>
      <div :class="{ 'simulate-footer-mobile': isMobile }">
        <el-button @click="resetSimulate">重置</el-button>
        <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

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

const simulateBeads = ref([])
const simulateAccessories = ref([])

watch(() => props.row, (row) => {
  if (row) {
    simulateBeads.value = (row.finished?.beads || []).map(b => ({
      ...b,
      newPurchaseCost: b.bead_purchase_cost || 0
    }))
    simulateAccessories.value = (row.finished?.accessories || []).map(a => ({
      ...a,
      newCostPrice: a.accessory_cost_price || 0
    }))
  }
}, { immediate: true })

const resetSimulate = () => {
  simulateBeads.value.forEach(b => {
    b.newPurchaseCost = b.bead_purchase_cost || 0
  })
  simulateAccessories.value.forEach(a => {
    a.newCostPrice = a.accessory_cost_price || 0
  })
}

const formatPrice = (value, digits = 2) => {
  const num = Number(value) || 0
  return num.toFixed(digits)
}

const calculateBeadsQuantity = (beads) => {
  return beads.reduce((sum, bead) => sum + (Number(bead.quantity) || 0), 0)
}

const calculateAccessoriesQuantity = (accessories) => {
  return accessories.reduce((sum, acc) => sum + (Number(acc.quantity) || 0), 0)
}

const simulateOriginalCost = computed(() => {
  if (!props.row?.finished) return 0
  const f = props.row.finished
  let total = 0
  f.beads.forEach(b => { total += b.bead_cost_price * b.quantity })
  f.accessories.forEach(a => { total += a.accessory_cost_price * a.quantity })
  total += f.labor_cost + f.elastic_cost
  return total
})

const simulateNewCost = computed(() => {
  if (!props.row?.finished) return 0
  const f = props.row.finished
  let total = 0
  simulateBeads.value.forEach(b => {
    total += (b.newPurchaseCost * (b.bead_weight || 0)) * b.quantity
  })
  simulateAccessories.value.forEach(a => {
    total += a.newCostPrice * a.quantity
  })
  total += f.labor_cost + f.elastic_cost
  return total
})

const simulateNewProfitRate = computed(() => {
  if (!props.row || props.row.selling_price <= 0) return '0.0'
  return ((props.row.selling_price - simulateNewCost.value) / props.row.selling_price * 100).toFixed(1)
})
</script>

<style scoped>
.detail-table {
  table-layout: fixed;
  border-collapse: collapse;
  margin-bottom: 12px;
  font-size: 13px;
}

.detail-table th,
.detail-table td {
  padding: 6px 10px;
  border-bottom: 1px solid #ebeef5;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail-table thead tr:nth-child(2) th {
  background: #f5f7fa;
  color: #909399;
  font-weight: 600;
  font-size: 12px;
  text-align: left;
}

.detail-table-header {
  background: #f5f7fa;
  color: #303133;
  font-weight: 700;
  font-size: 13px;
  text-align: left;
  padding: 8px 10px !important;
}

.detail-table tbody tr:hover {
  background: #f5f7fa;
}

.simulate-content {
  padding: 0 4px;
}

.simulate-info {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #606266;
}

.simulate-info-mobile {
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  background: #fafafa;
  border-radius: 6px;
  padding: 10px 12px;
  margin-bottom: 12px;
}

.simulate-info-mobile span {
  word-break: break-all;
}

.simulate-table {
  font-size: 13px;
  table-layout: fixed;
  width: 100%;
}

.simulate-table th,
.simulate-table td {
  padding: 8px 6px;
  text-align: center;
  vertical-align: middle;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.simulate-table .simulate-text {
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.simulate-input {
  width: 100%;
  min-width: 0;
}

.simulate-input :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

/* 手机端卡片式布局 */
.simulate-mobile-section {
  margin-bottom: 14px;
}

.simulate-mobile-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 6px 6px 0 0;
}

.simulate-mobile-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-top: none;
  padding: 10px 12px;
  margin-bottom: 8px;
}

.simulate-mobile-card:last-child {
  border-radius: 0 0 6px 6px;
}

.simulate-mobile-card-header {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px dashed #ebeef5;
  word-break: break-all;
}

.simulate-mobile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 12px;
}

.simulate-mobile-row {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #606266;
}

.simulate-mobile-row:nth-child(4),
.simulate-mobile-row:nth-child(8) {
  grid-column: 1 / -1;
}

.simulate-mobile-label {
  color: #909399;
  margin-right: 8px;
  min-width: 44px;
  flex-shrink: 0;
}

.simulate-input-mobile {
  flex: 1;
  min-width: 0;
}

.simulate-input-mobile :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

.simulate-summary {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  gap: 32px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.summary-row:last-child {
  margin-bottom: 0;
}

.summary-row b {
  color: #303133;
}

.simulate-summary-mobile {
  padding: 10px 12px;
  margin-top: 12px;
}

.simulate-summary-mobile .summary-row {
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 12px;
}

.simulate-footer-mobile {
  display: flex;
  gap: 10px;
}

.simulate-footer-mobile .el-button {
  flex: 1;
}
</style>
