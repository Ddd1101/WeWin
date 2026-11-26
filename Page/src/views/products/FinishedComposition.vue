<template>
  <div>
    <!-- 成品组成 -->
    <el-divider content-position="left">成品组成</el-divider>
    <div class="cost-summary" v-if="form.beads.length > 0 || form.accessories.length > 0">
      <div class="cost-item">
        <span class="label">串珠数量：</span>
        <span class="value">{{ form.beads.reduce((sum, b) => sum + (b.quantity || 0), 0) }}颗（{{ form.beads.length }}种）</span>
      </div>
      <div class="cost-item">
        <span class="label">配件数量：</span>
        <span class="value">{{ form.accessories.reduce((sum, a) => sum + (a.quantity || 0), 0) }}个（{{ form.accessories.length }}种）</span>
      </div>
      <div class="cost-item">
        <span class="label">工费：</span>
        <span class="value">¥{{ form.labor_cost.toFixed(2) }}</span>
      </div>
      <div class="cost-item">
        <span class="label">弹性成本：</span>
        <span class="value">¥{{ form.elastic_cost.toFixed(2) }}</span>
      </div>
      <div class="cost-item total">
        <span class="label">总成本：</span>
        <span class="value">¥{{ totalCost.toFixed(2) }}</span>
      </div>
      <div v-if="form.selling_price > 0" class="cost-item profit">
        <span class="label">利润：</span>
        <span class="value">¥{{ profit.toFixed(2) }} ({{ profitRate.toFixed(1) }}%)</span>
      </div>
    </div>
    <el-divider content-position="left" style="margin: 15px 0;">串珠组成</el-divider>
    <div class="composition-section">
      <el-button type="primary" size="default" @click="handleAddBead" class="add-btn">
        <el-icon><Plus /></el-icon>
        添加串珠
      </el-button>
      <div class="selected-items" v-if="form.beads.length > 0">
        <div v-for="(bead, index) in form.beads" :key="index" class="item-card">
          <div class="item-main">
            <div class="selected-item-image-wrapper">
              <el-image
                v-if="bead.image_url || bead.bead_image_url"
                :src="bead.image_url || bead.bead_image_url"
                class="selected-item-image"
                fit="cover"
                :preview-src-list="[bead.image_url || bead.bead_image_url]"
                :initial-index="0"
                preview-teleported
                :alt="bead.bead_name"
              />
              <div v-else class="selected-item-no-image">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
            <div class="item-info">
              <span class="item-name">{{ bead.bead_name }}</span>
              <span class="item-code">{{ bead.bead_code }}</span>
              <span class="item-price">{{ skuLabel(bead) }}</span>
              <span class="item-price">单价: ¥{{ safePrice(bead.cost_price) }}</span>
            </div>
          </div>
          <div class="item-controls">
            <span class="label">数量:</span>
            <el-input-number 
              v-model="bead.quantity" 
              :min="1" 
              size="small" 
              style="width: 90px;"
            />
            <span class="item-subtotal">小计: ¥{{ safePrice(safeCalculate(bead.cost_price, bead.quantity)) }}</span>
            <el-button 
              size="small" 
              type="danger" 
              text 
              @click="form.beads.splice(index, 1)"
              class="delete-btn"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
      <div v-else class="empty-hint">
        <el-icon><CirclePlus /></el-icon>
        <span>点击上方按钮添加串珠</span>
      </div>
    </div>
    
    <el-divider content-position="left" style="margin: 20px 0;">配件组成</el-divider>
    <div class="composition-section">
      <el-button type="primary" size="default" @click="handleAddAccessory" class="add-btn">
        <el-icon><Plus /></el-icon>
        添加配件
      </el-button>
      <div class="selected-items" v-if="form.accessories.length > 0">
        <div v-for="(acc, index) in form.accessories" :key="index" class="item-card">
          <div class="item-main">
            <div class="selected-item-image-wrapper">
              <el-image
                v-if="acc.image_url || acc.accessory_image_url"
                :src="acc.image_url || acc.accessory_image_url"
                class="selected-item-image"
                fit="cover"
                :preview-src-list="[acc.image_url || acc.accessory_image_url]"
                :initial-index="0"
                preview-teleported
                :alt="acc.accessory_name"
              />
              <div v-else class="selected-item-no-image">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
            <div class="item-info">
              <span class="item-name">{{ acc.accessory_name }}</span>
              <span class="item-code">{{ acc.accessory_code }}</span>
              <span class="item-price">{{ skuLabel(acc) }}</span>
              <span class="item-price">单价: ¥{{ safePrice(acc.cost_price) }}</span>
            </div>
          </div>
          <div class="item-controls">
            <span class="label">数量:</span>
            <el-input-number 
              v-model="acc.quantity" 
              :min="1" 
              size="small" 
              style="width: 90px;"
            />
            <span class="item-subtotal">小计: ¥{{ safePrice(safeCalculate(acc.cost_price, acc.quantity)) }}</span>
            <el-button 
              size="small" 
              type="danger" 
              text 
              @click="form.accessories.splice(index, 1)"
              class="delete-btn"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
      <div v-else class="empty-hint">
        <el-icon><CirclePlus /></el-icon>
        <span>点击上方按钮添加配件</span>
      </div>
    </div>

    <!-- 选择串珠对话框 -->
    <el-dialog
      v-model="beadDialogVisible"
      title="选择串珠"
      :width="isMobile ? '95%' : '900px'"
      class="selection-dialog"
      :fullscreen="isMobile"
    >
      <div class="dialog-search-wrapper">
        <el-input v-model="beadSearch" placeholder="搜索串珠名称或货号..." class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="cards-container">
        <div 
          v-for="bead in filteredBeads" 
          :key="bead.id"
          class="product-card"
        >
          <div class="card-image-wrapper">
            <img
              v-if="bead.image_url"
              :src="bead.image_url"
              class="product-image"
              @click.stop="() => { 
                const viewer = document.createElement('div');
                viewer.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:99999;cursor:zoom-out;';
                viewer.onclick = () => viewer.remove();
                const img = document.createElement('img');
                img.src = bead.image_url;
                img.style.cssText = 'max-width:90%;max-height:90%;object-fit:contain;';
                viewer.appendChild(img);
                document.body.appendChild(viewer);
              }"
            />
            <div v-else class="no-image">
              <el-icon><Picture /></el-icon>
            </div>
          </div>
          <div class="card-content">
            <div class="product-code">{{ bead.code }}</div>
            <h4 class="product-name">{{ bead.name }}</h4>
            <div class="product-meta">
              <span class="product-price">¥{{ bead.cost_price.toFixed(2) }}/g</span>
              <span v-if="bead.weight" class="product-weight">{{ bead.weight?.toFixed(2) }}g</span>
            </div>
            <div class="product-badges">
              <span class="badge quality-badge">{{ bead.skus?.length || 0 }} 个SKU</span>
            </div>
            <el-select
              v-if="bead.skus?.length"
              v-model="bead.selectedSku"
              value-key="id"
              placeholder="选择SKU"
              style="width:100%; margin-top:8px"
              :teleported="false"
              @click.stop
            >
              <el-option v-for="sku in bead.skus" :key="sku.id" :label="skuLabel(sku) || sku.sku_code" :value="sku" />
            </el-select>
          </div>
          <div class="card-actions">
            <el-button type="primary" size="small" class="select-card-btn" @click.stop="handleSelectBead(bead)">
              <el-icon><Check /></el-icon>
              选择
            </el-button>
          </div>
        </div>
        
        <div v-if="filteredBeads.length === 0" class="empty-state">
          <el-icon class="empty-icon"><Document /></el-icon>
          <p>暂无相关串珠</p>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button @click="beadDialogVisible = false">取消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择配件对话框 -->
    <el-dialog
      v-model="accessoryDialogVisible"
      title="选择配件"
      :width="isMobile ? '95%' : '900px'"
      class="selection-dialog"
      :fullscreen="isMobile"
    >
      <div class="dialog-search-wrapper">
        <el-input v-model="accessorySearch" placeholder="搜索配件名称或货号..." class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="cards-container">
        <div 
          v-for="accessory in filteredAccessories" 
          :key="accessory.id"
          class="product-card"
        >
          <div class="card-image-wrapper">
            <img
              v-if="accessory.image_url"
              :src="accessory.image_url"
              class="product-image"
              @click.stop="() => { 
                const viewer = document.createElement('div');
                viewer.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:99999;cursor:zoom-out;';
                viewer.onclick = () => viewer.remove();
                const img = document.createElement('img');
                img.src = accessory.image_url;
                img.style.cssText = 'max-width:90%;max-height:90%;object-fit:contain;';
                viewer.appendChild(img);
                document.body.appendChild(viewer);
              }"
            />
            <div v-else class="no-image">
              <el-icon><Picture /></el-icon>
            </div>
          </div>
          <div class="card-content">
            <div class="product-code">{{ accessory.code }}</div>
            <h4 class="product-name">{{ accessory.name }}</h4>
            <div class="product-meta">
              <span class="product-price">¥{{ accessory.cost_price.toFixed(2) }}</span>
            </div>
            <div class="product-badges"><span class="badge quality-badge">{{ accessory.skus?.length || 0 }} 个SKU</span></div>
            <el-select
              v-if="accessory.skus?.length"
              v-model="accessory.selectedSku"
              value-key="id"
              placeholder="选择SKU"
              style="width:100%; margin-top:8px"
              :teleported="false"
              @click.stop
            >
              <el-option v-for="sku in accessory.skus" :key="sku.id" :label="skuLabel(sku) || sku.sku_code" :value="sku" />
            </el-select>
          </div>
          <div class="card-actions">
            <el-button type="primary" size="small" class="select-card-btn" @click.stop="handleSelectAccessory(accessory)">
              <el-icon><Check /></el-icon>
              选择
            </el-button>
          </div>
        </div>
        
        <div v-if="filteredAccessories.length === 0" class="empty-state">
          <el-icon class="empty-icon"><Document /></el-icon>
          <p>暂无相关配件</p>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer-custom">
          <el-button @click="accessoryDialogVisible = false">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Picture, Document, Check, CirclePlus, Delete } from '@element-plus/icons-vue'
import { getBeads, getAccessories } from '@/api'

const props = defineProps({
  form: {
    type: Object,
    required: true
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

// 配件列表
const accessories = ref([])
// 串珠列表
const beads = ref([])
// 筛选后的配件列表
const filteredAccessories = computed(() => {
  if (!accessorySearch.value) {
    return accessories.value
  }
  return accessories.value.filter(acc => 
    acc.code.toLowerCase().includes(accessorySearch.value.toLowerCase()) || 
    acc.name.toLowerCase().includes(accessorySearch.value.toLowerCase())
  )
})
// 筛选后的串珠列表
const filteredBeads = computed(() => {
  if (!beadSearch.value) {
    return beads.value
  }
  return beads.value.filter(bead => 
    bead.code.toLowerCase().includes(beadSearch.value.toLowerCase()) || 
    bead.name.toLowerCase().includes(beadSearch.value.toLowerCase())
  )
})
const beadDialogVisible = ref(false)
const accessoryDialogVisible = ref(false)
// 配件搜索
const accessorySearch = ref('')
// 串珠搜索
const beadSearch = ref('')

// 计算串珠成本
const beadsCost = computed(() => {
  return props.form.beads.reduce((sum, bead) => {
    // 优先使用已保存的 cost_price，如果没有则尝试从列表中查找
    let costPrice = bead.cost_price
    if (!costPrice || costPrice === 0) {
      const beadData = beads.value.find(b => b.id === bead.bead_id)
      if (beadData) {
        costPrice = beadData.cost_price
      }
    }
    return sum + safeCalculate(costPrice, bead.quantity)
  }, 0)
})

// 计算配件成本
const accessoriesCost = computed(() => {
  return props.form.accessories.reduce((sum, acc) => {
    // 优先使用已保存的 cost_price，如果没有则尝试从列表中查找
    let costPrice = acc.cost_price
    if (!costPrice || costPrice === 0) {
      const accData = accessories.value.find(a => a.id === acc.accessory_id)
      if (accData) {
        costPrice = accData.cost_price
      }
    }
    return sum + safeCalculate(costPrice, acc.quantity)
  }, 0)
})

// 计算总成本
const totalCost = computed(() => {
  return beadsCost.value + accessoriesCost.value + props.form.labor_cost + props.form.elastic_cost
})

// 计算利润
const profit = computed(() => {
  return props.form.selling_price - totalCost.value
})

// 计算利润率
const profitRate = computed(() => {
  if (props.form.selling_price <= 0) return 0
  return (profit.value / props.form.selling_price) * 100
})

// 安全计算函数，防止NaN
const safeCalculate = (num1, num2) => {
  const n1 = Number(num1) || 0
  const n2 = Number(num2) || 0
  return n1 * n2
}

// 安全显示价格
const safePrice = (price) => {
  const num = Number(price) || 0
  return num.toFixed(2)
}

// 监听成品组成变化，自动计算成本价格
watch([
  () => props.form.beads,
  () => props.form.labor_cost,
  () => props.form.elastic_cost,
  () => props.form.accessories
], () => {
  if (props.form.product_type === 'finished') {
    props.form.cost_price = totalCost.value
  }
}, { deep: true, immediate: true })

// 获取配件列表
const fetchAccessories = async () => {
  try {
    const response = await getAccessories()
    accessories.value = response.data.accessories.map(acc => ({ ...acc, selectedSku: acc.skus?.find(s => s.is_default) || acc.skus?.[0] }))
  } catch (error) {
    ElMessage.error('获取配件列表失败')
    console.error(error)
  }
}

// 获取串珠列表
const fetchBeads = async () => {
  try {
    const response = await getBeads()
    beads.value = response.data.beads.map(bead => ({ ...bead, selectedSku: bead.skus?.find(s => s.is_default) || bead.skus?.[0] }))
  } catch (error) {
    ElMessage.error('获取串珠列表失败')
    console.error(error)
  }
}

// 处理添加串珠
const handleAddBead = () => {
  fetchBeads()
  beadDialogVisible.value = true
}

// 处理选择串珠
const handleSelectBead = (bead) => {
  const sku = bead.selectedSku || bead.skus?.find(s => s.is_default) || bead.skus?.[0] || {}
  const existing = props.form.beads.find(item => item.bead_id === bead.id && item.sku_id === sku.id)
  if (existing) {
    ElMessage.warning('该串珠SKU已经添加过了')
    return
  }
  props.form.beads.push({
    bead_id: bead.id,
    sku_id: sku.id,
    sku,
    bead_code: bead.code,
    bead_name: bead.name,
    cost_price: sku.cost_price ?? bead.cost_price,
    image_url: bead.image_url,
    bead_image_url: bead.image_url,
    quantity: 1
  })
  beadDialogVisible.value = false
}

const skuLabel = (item, prefix = '') => {
  const sku = item.sku || item
  const parts = [sku.sku_name || sku.name, sku.size ? `${sku.size}mm` : '', sku.weight ? `${Number(sku.weight).toFixed(2)}g` : '']
  // 添加采购成本或成本价格信息
  if (sku.purchase_cost !== undefined && sku.purchase_cost !== null && sku.purchase_cost !== '') {
    parts.push(`${Number(sku.purchase_cost).toFixed(2)}元/g`)
  }
  if (sku.cost_price !== undefined && sku.cost_price !== null && sku.cost_price !== '') {
    parts.push(`${Number(sku.cost_price).toFixed(2)}元`)
  }
  return `${prefix}${parts.filter(Boolean).join(' / ')}`
}

const handleAddAccessory = () => {
  fetchAccessories()
  accessoryDialogVisible.value = true
}

// 处理选择配件
const handleSelectAccessory = (accessory) => {
  const sku = accessory.selectedSku || accessory.skus?.find(s => s.is_default) || accessory.skus?.[0] || {}
  const existing = props.form.accessories.find(item => item.accessory_id === accessory.id && item.sku_id === sku.id)
  if (existing) {
    ElMessage.warning('该配件SKU已经添加过了')
    return
  }
  props.form.accessories.push({
    accessory_id: accessory.id,
    sku_id: sku.id,
    sku,
    accessory_code: accessory.code,
    accessory_name: accessory.name,
    cost_price: sku.cost_price ?? accessory.cost_price,
    image_url: accessory.image_url,
    accessory_image_url: accessory.image_url,
    quantity: 1
  })
  accessoryDialogVisible.value = false
}
</script>

<style scoped>
.cost-summary {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #e0e7ff;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}

.cost-item .label {
  color: #64748b;
}

.cost-item .value {
  font-weight: 600;
  color: #334155;
}

.cost-item.total {
  padding-top: 12px;
  margin-top: 8px;
  border-top: 1px dashed #cbd5e1;
  font-size: 16px;
}

.cost-item.total .value {
  color: #3b82f6;
  font-size: 18px;
}

.cost-item.profit .value {
  color: #10b981;
}

/* 组成区域样式 */
.composition-section {
  margin-bottom: 8px;
}

.add-btn {
  margin-bottom: 12px;
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #94a3b8;
  gap: 8px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px dashed #cbd5e1;
}

.empty-hint .el-icon {
  font-size: 32px;
}

.selected-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.item-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #fafbff 0%, #f8fafc 100%);
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
  width: 100%;
}

.item-card:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.item-main {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.selected-item-image-wrapper {
  width: 64px;
  height: 64px;
  flex: 0 0 64px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}

.selected-item-image {
  width: 100%;
  height: 100%;
  display: block;
  cursor: zoom-in;
}

.selected-item-image :deep(img) {
  object-fit: cover;
}

.selected-item-no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.selected-item-no-image .el-icon {
  font-size: 24px;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.item-name {
  font-size: 15px;
  color: #374151;
  font-weight: 600;
}

.item-code {
  font-size: 12px;
  color: #94a3b8;
}

.item-price {
  font-size: 13px;
  color: #64748b;
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.item-controls .label {
  font-size: 13px;
  color: #64748b;
  white-space: nowrap;
}

.item-subtotal {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
  background: #eff6ff;
  padding: 4px 10px;
  border-radius: 6px;
}

.delete-btn {
  margin-left: auto;
  padding: 4px 8px;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #fee2e2;
}

/* 选择对话框样式 */
.selection-dialog {
  --dialog-bg: #ffffff;
  --primary-gradient: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  --card-bg: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --hover-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.selection-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.selection-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  padding: 24px 24px 20px;
  margin: 0;
}

.selection-dialog :deep(.el-dialog__title) {
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.selection-dialog :deep(.el-dialog__headerbtn) {
  top: 24px;
}

.selection-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #ffffff;
  font-size: 20px;
}

.dialog-search-wrapper {
  margin-bottom: 24px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
  padding: 0 16px;
  transition: all 0.2s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1 inset;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #3b82f6 inset;
}

/* 卡片容器 */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
  padding: 4px;
}

.cards-container::-webkit-scrollbar {
  width: 8px;
}

.cards-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.cards-container::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 4px;
}

/* 产品卡片 */
.product-card {
  position: relative;
  background: #ffffff;
  border-radius: 14px;
  overflow: visible;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

.product-card:has(.el-select__wrapper.is-focused),
.product-card:has(.el-select-dropdown) {
  z-index: 5;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.15);
  border-color: #3b82f6;
}

.product-card:hover .card-image-wrapper {
  transform: scale(1.02);
}

/* 卡片图片 */
.card-image-wrapper {
  position: relative;
  width: 100%;
  min-height: 160px;
  max-height: 220px;
  border-radius: 14px 14px 0 0;
  overflow: hidden;
  transition: transform 0.4s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 10px;
  box-sizing: border-box;
}

.product-image {
  max-width: 100%;
  max-height: 200px;
  width: auto;
  height: auto;
  display: block;
  cursor: zoom-in;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  color: #94a3b8;
}

.no-image .el-icon {
  font-size: 48px;
}

/* 卡片内容 */
.card-content {
  padding: 16px;
}

.product-code {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.product-price {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.product-weight {
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.product-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 20px;
  letter-spacing: 0.3px;
}

.quality-badge {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

/* 卡片操作区 */
.card-actions {
  padding: 0 16px 16px;
  display: flex;
  justify-content: flex-end;
}

.select-card-btn {
  width: 100%;
  border-radius: 10px;
  font-weight: 600;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
  color: white;
  height: 40px;
  transition: all 0.2s ease;
}

.select-card-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #94a3b8;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cbd5e1;
  margin-bottom: 12px;
}

.empty-state-icon .el-icon {
  font-size: 40px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 对话框底部 */
.dialog-footer-custom {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

.selection-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  background-color: #f8fafc;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .cost-summary {
    padding: 10px;
  }

  .cost-item {
    font-size: 13px;
  }

  .cost-item.total .value {
    font-size: 16px;
  }

  .item-card {
    padding: 10px 12px;
  }

  .item-controls {
    flex-wrap: wrap;
    gap: 8px;
  }

  .item-subtotal {
    font-size: 13px;
  }

  .cards-container {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
  }

  .card-image-wrapper {
    min-height: 100px;
    max-height: 150px;
  }

  .product-name {
    font-size: 13px;
  }

  .product-price {
    font-size: 15px;
  }

  .selection-dialog :deep(.el-dialog__body) {
    padding: 12px;
  }
}
</style>
