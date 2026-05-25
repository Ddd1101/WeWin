<template>
  <div>
    <!-- 筛选区域 -->
    <div class="filter-container">
      <el-form :inline="true" class="demo-form-inline">
        <el-form-item label="搜索">
          <el-input v-model="searchQuery" placeholder="搜索商品名称或货号" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="localFilter.is_active" placeholder="选择状态" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格 -->
    <el-table 
      :data="filteredProducts" 
      style="width: 100%" 
      row-key="id"
      v-loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column type="expand">
        <template #default="scope">
          <div v-if="scope.row.product_type === 'finished' && scope.row.finished" class="finished-details">
            <div class="details-header">
              <div class="header-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="header-title">
                <h4>成品组成明细</h4>
              </div>
            </div>
            
            <div class="details-content">
              <!-- 串珠列表 -->
              <div class="section" v-if="scope.row.finished.beads.length > 0">
                <div class="section-header">
                  <div class="section-title">
                    <span class="section-icon">💎</span>
                    <h5>串珠</h5>
                    <span class="count-badge">{{ scope.row.finished.beads.length }}</span>
                  </div>
                  <div class="section-summary">
                    小计：<span class="summary-amount">¥{{ calculateBeadsTotal(scope.row.finished.beads).toFixed(2) }}</span>
                  </div>
                </div>
                <div class="item-list">
                  <div v-for="(bead, index) in scope.row.finished.beads" :key="index" class="item-card">
                    <div class="item-image">
                      <el-image
                        v-if="bead.bead_image_url"
                        :src="bead.bead_image_url"
                        style="width: 60px; height: 60px"
                        fit="cover"
                        :preview-src-list="[bead.bead_image_url]"
                      />
                      <div v-else class="image-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                          <path d="M21 15L16 10L5 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </div>
                    </div>
                    <div class="item-info">
                      <div class="all-tags">
                        <span v-if="bead.bead_code" class="item-tag code-tag">货号: {{ bead.bead_code }}</span>
                        <span class="item-tag name-tag">品名: {{ bead.bead_name }}</span>
                        <span class="item-tag quality-tag" v-if="bead.bead_quality_level">品级: {{ bead.bead_quality_level }}</span>
                        <span class="item-tag spec-tag" v-if="bead.bead_size">规格: {{ bead.bead_size }}mm</span>
                        <span class="item-tag price-tag" v-if="bead.bead_purchase_cost">采购：¥{{ bead.bead_purchase_cost.toFixed(2) }}/g</span>
                      </div>
                      <div class="item-remark" v-if="bead.bead_remark">{{ bead.bead_remark }}</div>
                    </div>
                    <div class="item-quantity">
                      <span class="qty-label">数量</span>
                      <span class="qty-value">{{ bead.quantity }}</span>
                    </div>
                    <div class="item-price">
                      <div class="price-unit">¥{{ bead.bead_cost_price.toFixed(2) }}/颗</div>
                      <div class="price-total">¥{{ (bead.bead_cost_price * bead.quantity).toFixed(2) }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 配件列表 -->
              <div class="section" v-if="scope.row.finished.accessories.length > 0">
                <div class="section-header">
                  <div class="section-title">
                    <span class="section-icon">🔗</span>
                    <h5>配件</h5>
                    <span class="count-badge">{{ scope.row.finished.accessories.length }}</span>
                  </div>
                  <div class="section-summary">
                    小计：<span class="summary-amount">¥{{ calculateAccessoriesTotal(scope.row.finished.accessories).toFixed(2) }}</span>
                  </div>
                </div>
                <div class="item-list">
                  <div v-for="(acc, index) in scope.row.finished.accessories" :key="index" class="item-card">
                    <div class="item-image">
                      <el-image
                        v-if="acc.accessory_image_url"
                        :src="acc.accessory_image_url"
                        style="width: 60px; height: 60px"
                        fit="cover"
                        :preview-src-list="[acc.accessory_image_url]"
                      />
                      <div v-else class="image-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                          <path d="M21 15L16 10L5 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </div>
                    </div>
                    <div class="item-info">
                      <div class="all-tags">
                        <span v-if="acc.accessory_code" class="item-tag code-tag">货号: {{ acc.accessory_code }}</span>
                        <span class="item-tag name-tag">品名: {{ acc.accessory_name }}</span>
                      </div>
                    </div>
                    <div class="item-quantity">
                      <span class="qty-label">数量</span>
                      <span class="qty-value">{{ acc.quantity }}</span>
                    </div>
                    <div class="item-price">
                      <div class="price-unit">¥{{ acc.accessory_cost_price.toFixed(2) }}/件</div>
                      <div class="price-total">¥{{ (acc.accessory_cost_price * acc.quantity).toFixed(2) }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 工费和弹性成本 -->
              <div class="section costs-section">
                <div class="section-header">
                  <div class="section-title">
                    <span class="section-icon">⚙️</span>
                    <h5>其他成本</h5>
                  </div>
                </div>
                <div class="costs-grid">
                  <div class="cost-card">
                    <div class="cost-icon">👷</div>
                    <div class="cost-info">
                      <div class="cost-label">工费</div>
                      <div class="cost-value">¥{{ scope.row.finished.labor_cost.toFixed(2) }}</div>
                    </div>
                  </div>
                  <div class="cost-card">
                    <div class="cost-icon">📦</div>
                    <div class="cost-info">
                      <div class="cost-label">弹性成本</div>
                      <div class="cost-value">¥{{ scope.row.finished.elastic_cost.toFixed(2) }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 总成本 -->
              <div class="total-section">
                <div class="total-divider"></div>
                <div class="total-content">
                  <div class="total-label">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 1V23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      <path d="M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6313 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6313 13.6815 18 14.5717 18 15.5C18 16.4283 17.6313 17.3185 16.9749 17.9749C16.3185 18.6313 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    总成本
                  </div>
                  <div class="total-value">¥{{ calculateTotalCost(scope.row.finished).toFixed(2) }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="['bead', 'accessory'].includes(scope.row.product_type)" class="sku-details">
            <h4>SKU列表</h4>
            <el-table v-if="scope.row.skus && scope.row.skus.length > 0" :data="scope.row.skus" size="small" style="width: 100%">
              <el-table-column prop="sku_code" label="SKU编码" min-width="120" />
              <el-table-column label="SKU名称" min-width="120">
                <template #default="skuScope">{{ skuScope.row.sku_name || skuScope.row.name || '-' }}</template>
              </el-table-column>
              <el-table-column prop="material" label="材质" width="100" />
              <el-table-column label="规格(mm)" width="100">
                <template #default="skuScope">{{ skuScope.row.size || '-' }}</template>
              </el-table-column>
              <el-table-column prop="color" label="颜色" width="100" />
              <el-table-column label="采购成本(元/克)" width="110">
                <template #default="skuScope">¥{{ formatPrice(skuScope.row.purchase_cost, 2) }}</template>
              </el-table-column>
              <el-table-column label="成本" width="100">
                <template #default="skuScope">¥{{ formatPrice(skuScope.row.cost_price) }}</template>
              </el-table-column>
              <el-table-column v-if="scope.row.product_type === 'bead'" label="克重" width="90">
                <template #default="skuScope">{{ formatPrice(skuScope.row.weight, 3) }}g</template>
              </el-table-column>
              <el-table-column label="品质" width="80">
                <template #default="skuScope">{{ skuScope.row.quality_level || '-' }}</template>
              </el-table-column>
              <el-table-column label="售价" width="100">
                <template #default="skuScope">¥{{ formatPrice(skuScope.row.selling_price) }}</template>
              </el-table-column>
              <el-table-column prop="location" label="库位" width="100" />
              <el-table-column prop="supplier" label="供应商" width="120" />
              <el-table-column label="默认" width="80">
                <template #default="skuScope"><el-tag v-if="skuScope.row.is_default" size="small">默认</el-tag></template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="120" />
            </el-table>
            <el-empty v-else description="暂无SKU" />
          </div>
          <div v-else>无明细</div>
        </template>
      </el-table-column>
      <el-table-column label="图片" width="80">
        <template #default="scope">
          <el-image
            v-if="scope.row.image_url"
            :src="scope.row.image_url"
            style="width: 50px; height: 50px"
            fit="cover"
            :preview-src-list="[scope.row.image_url]"
          />
          <span v-else style="color: #999">无图</span>
        </template>
      </el-table-column>
      <el-table-column prop="code" label="货号" width="180" />
      <el-table-column prop="name" label="商品名称" />
      <el-table-column prop="product_type_display" label="商品类型" width="120" />
      <!-- 配件和串珠显示规格 -->
      <el-table-column v-if="props.products.some(p => p.product_type === 'accessory' || p.product_type === 'bead')" label="规格(mm)" width="100">
        <template #default="scope">
          {{ getDefaultSku(scope.row)?.size || '-' }}
        </template>
      </el-table-column>
      <!-- 串珠显示品质等级 -->
      <el-table-column v-if="props.products.some(p => p.product_type === 'bead')" label="品质等级" width="100">
        <template #default="scope">
          {{ getDefaultSku(scope.row)?.quality_level || '-' }}
        </template>
      </el-table-column>
      <!-- 只对串珠显示采购成本 -->
      <el-table-column v-if="props.products.some(p => p.product_type === 'bead')" label="采购成本(元/克)" width="130">
        <template #default="scope">
          {{ scope.row.product_type === 'bead' ? '¥' + formatPrice(getDefaultSku(scope.row)?.purchase_cost, 2) : '-' }}
        </template>
      </el-table-column>
      <!-- 显示成本价格 -->
      <el-table-column label="成本价格" width="100">
        <template #default="scope">
          ¥{{ formatPrice(scope.row.product_type === 'finished' ? scope.row.cost_price : getDefaultSku(scope.row)?.cost_price) }}
        </template>
      </el-table-column>
      <!-- 显示售卖价格 -->
      <el-table-column label="售卖价格" width="100">
        <template #default="scope">
          ¥{{ formatPrice(scope.row.product_type === 'finished' ? scope.row.selling_price : getDefaultSku(scope.row)?.selling_price) }}
        </template>
      </el-table-column>
      <el-table-column prop="location" label="库位" width="120" />
      <el-table-column prop="supplier" label="供应商" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 空状态 -->
    <el-empty v-if="filteredProducts.length === 0 && !loading" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
  products: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  selectedIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select', 'select-all', 'edit', 'delete'])

const searchQuery = ref('')
const localFilter = ref({
  is_active: ''
})

// 获取默认SKU的工具函数
const getDefaultSku = (product) => {
  if (!product.skus || product.skus.length === 0) {
    return null
  }
  // 首先找 is_default 为 true 的
  let defaultSku = product.skus.find(sku => sku.is_default)
  // 如果没有找到，就用第一个
  if (!defaultSku) {
    defaultSku = product.skus[0]
  }
  return defaultSku
}

// 过滤后的产品列表
const filteredProducts = computed(() => {
  let result = props.products
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.code?.toLowerCase().includes(query) || 
      p.name?.toLowerCase().includes(query)
    )
  }
  
  // 状态过滤
  if (localFilter.value.is_active !== '') {
    result = result.filter(p => p.is_active === localFilter.value.is_active)
  }
  
  return result
})

const handleFilter = () => {
  // 父组件已处理分页，这里可以通知更新
}

const resetFilter = () => {
  searchQuery.value = ''
  localFilter.value.is_active = ''
}

const handleSelectionChange = (selection) => {
  const ids = selection.map(item => item.id)
  if (ids.length === 0) {
    emit('select-all', [])
  } else {
    emit('select-all', ids)
  }
}

const handleEdit = (row) => {
  emit('edit', row)
}

const handleDelete = (row) => {
  emit('delete', row)
}

const formatPrice = (value, digits = 2) => {
  const num = Number(value) || 0
  return num.toFixed(digits)
}

const calculateBeadsTotal = (beads) => {
  return beads.reduce((sum, bead) => sum + bead.bead_cost_price * bead.quantity, 0)
}

const calculateAccessoriesTotal = (accessories) => {
  return accessories.reduce((sum, acc) => sum + acc.accessory_cost_price * acc.quantity, 0)
}

const calculateTotalCost = (finished) => {
  let total = 0
  // 计算串珠成本
  finished.beads.forEach((bead) => {
    total += bead.bead_cost_price * bead.quantity
  })
  // 计算配件成本
  finished.accessories.forEach((acc) => {
    total += acc.accessory_cost_price * acc.quantity
  })
  // 加上工费和弹性成本
  total += finished.labor_cost
  total += finished.elastic_cost
  return total
}
</script>

<style scoped>
.filter-container {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

/* 展开详情样式 */
.sku-details {
  padding: 20px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.sku-details h4 {
  margin: 0 0 15px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.finished-details {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  overflow: hidden;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.details-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.header-icon svg {
  width: 24px;
  height: 24px;
}

.header-title h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.header-title p {
  margin: 4px 0 0 0;
  font-size: 13px;
  opacity: 0.9;
}

.details-content {
  padding: 24px;
}

.finished-details .section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 20px;
}

.section-title h5 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 12px;
}

.section-summary {
  font-size: 14px;
  color: #64748b;
}

.summary-amount {
  font-weight: 700;
  color: #667eea;
  font-size: 16px;
  margin-left: 4px;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  display: grid;
  grid-template-columns: 76px 1fr 100px 120px;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  border: 1px solid #f1f5f9;
}

.item-card:hover {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.12);
  transform: translateY(-2px);
  border-color: #e0e7ff;
}

.item-image {
  position: relative;
}

.item-image .el-image {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.image-placeholder {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.image-placeholder svg {
  width: 28px;
  height: 28px;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.all-tags {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding-bottom: 4px;
}

.all-tags::-webkit-scrollbar {
  height: 4px;
}

.all-tags::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.item-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.item-tag.code-tag {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #4338ca;
}

.item-tag.name-tag {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.item-tag.quality-tag {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.item-tag.spec-tag {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #0369a1;
}

.item-tag.price-tag {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
}

.item-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}



.item-remark {
  font-size: 12px;
  color: #94a3b8;
  font-style: italic;
}

.item-quantity {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.qty-label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.qty-value {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.item-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.price-unit {
  font-size: 12px;
  color: #64748b;
}

.price-total {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.costs-section .section-header {
  border-bottom: none;
  margin-bottom: 12px;
  padding-bottom: 0;
}

.costs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.cost-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f5f9;
  transition: all 0.2s ease;
}

.cost-card:hover {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.12);
  transform: translateY(-2px);
}

.cost-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
}

.cost-info {
  flex: 1;
}

.cost-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.cost-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.total-section {
  margin-top: 8px;
}

.total-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, #cbd5e1 50%, transparent 100%);
  margin-bottom: 20px;
}

.total-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.total-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.total-label svg {
  width: 24px;
  height: 24px;
}

.total-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .item-card {
    grid-template-columns: 60px 1fr;
    grid-template-rows: auto auto auto;
    gap: 12px;
  }
  
  .item-image {
    grid-row: 1 / 4;
  }
  
  .item-info {
    grid-column: 2;
    grid-row: 1;
  }
  
  .item-quantity {
    grid-column: 2;
    grid-row: 2;
    align-items: flex-start;
  }
  
  .item-price {
    grid-column: 2;
    grid-row: 3;
    align-items: flex-start;
  }
  
  .costs-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
/* Element Plus 图片预览全局样式 - 必须确保在最上层 */
body > .el-image-viewer__wrapper {
  z-index: 99999 !important;
}

/* 确保预览容器在最上层，内部元素保持相对层级 */
.el-image-viewer__wrapper {
  z-index: 99999 !important;
}

/* 调整遮罩层透明度，让它不那么暗 */
.el-image-viewer__mask {
  background-color: rgba(0, 0, 0, 0.5) !important;
}

/* 防止表格元素创建层叠上下文影响预览 */
.el-table,
.el-table__body-wrapper,
.el-table__body,
.el-table__cell,
.el-table__row {
  position: static !important;
}

/* 只对必要的元素保持相对定位，但降低z-index */
.el-table__header-wrapper {
  position: relative;
  z-index: 1;
}

.el-table__fixed,
.el-table__fixed-right {
  z-index: 2 !important;
}
</style>
