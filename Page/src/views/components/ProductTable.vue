<template>
  <div>
    <ProductImageCell ref="imagePreviewRef" />

    <!-- 筛选区域 -->
    <div class="filter-container" :class="{ 'filter-mobile': isMobile }">
      <el-form :inline="!isMobile" class="demo-form-inline" :class="{ 'mobile-form': isMobile }">
        <el-form-item label="搜索">
          <el-input v-model="searchQuery" placeholder="搜索商品名称或货号" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="localFilter.is_active" placeholder="选择状态" :style="{ width: isMobile ? '100%' : '120px' }">
            <el-option label="全部" value="" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button @click="collapseAll">收起展开</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 桌面端表格 -->
    <el-table
      v-if="!isMobile"
      ref="tableRef"
      :data="filteredProducts"
      style="width: 100%"
      row-key="id"
      v-loading="loading"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column type="expand">
        <template #default="scope">
          <div v-if="scope.row.product_type === 'finished' && scope.row.finished" class="finished-details">
            <table class="detail-table" v-if="scope.row.finished.beads.length > 0">
              <thead>
                <tr>
                  <th colspan="9" class="detail-table-header">串珠（{{ scope.row.finished.beads.length }}种，共{{ calculateBeadsQuantity(scope.row.finished.beads) }}颗，小计 ¥{{ calculateBeadsTotal(scope.row.finished.beads).toFixed(2) }}）</th>
                </tr>
                <tr>
                  <th style="width:36px"></th>
                  <th style="width:80px">货号</th>
                  <th style="width:120px">SKU名称</th>
                  <th style="width:50px">数量</th>
                  <th style="width:80px">克价</th>
                  <th style="width:70px">单价</th>
                  <th style="width:60px">规格</th>
                  <th style="width:50px">品级</th>
                  <th style="width:80px">小计</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(bead, index) in scope.row.finished.beads" :key="index">
                  <td><img v-if="bead.bead_image_url" :src="bead.bead_image_url" class="detail-thumb" @click="imagePreviewRef.openPreview(bead.bead_image_url)" /></td>
                  <td>{{ bead.bead_code || '-' }}</td>
                  <td>{{ bead.sku?.name || bead.sku?.sku_name || bead.bead_name }}</td>
                  <td>{{ bead.quantity }}</td>
                  <td>¥{{ formatPrice(bead.bead_purchase_cost, 2) }}/g</td>
                  <td>¥{{ bead.bead_cost_price.toFixed(2) }}</td>
                  <td>{{ bead.bead_size ? bead.bead_size + 'mm' : '-' }}</td>
                  <td>{{ bead.bead_quality_level || '-' }}</td>
                  <td>¥{{ (bead.bead_cost_price * bead.quantity).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
            <table class="detail-table" v-if="scope.row.finished.accessories.length > 0">
              <thead>
                <tr>
                  <th colspan="6" class="detail-table-header">配件（{{ scope.row.finished.accessories.length }}种，共{{ calculateAccessoriesQuantity(scope.row.finished.accessories) }}个，小计 ¥{{ calculateAccessoriesTotal(scope.row.finished.accessories).toFixed(2) }}）</th>
                </tr>
                <tr>
                  <th style="width:36px"></th>
                  <th style="width:80px">货号</th>
                  <th style="width:120px">SKU名称</th>
                  <th style="width:50px">数量</th>
                  <th style="width:70px">单价</th>
                  <th style="width:80px">小计</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(acc, index) in scope.row.finished.accessories" :key="index">
                  <td><img v-if="acc.accessory_image_url" :src="acc.accessory_image_url" class="detail-thumb" @click="imagePreviewRef.openPreview(acc.accessory_image_url)" /></td>
                  <td>{{ acc.accessory_code || '-' }}</td>
                  <td>{{ acc.sku?.name || acc.sku?.sku_name || acc.accessory_name }}</td>
                  <td>{{ acc.quantity }}</td>
                  <td>¥{{ acc.accessory_cost_price.toFixed(2) }}</td>
                  <td>¥{{ (acc.accessory_cost_price * acc.quantity).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
            <div class="detail-summary">
              <span>工费: ¥{{ scope.row.finished.labor_cost.toFixed(2) }}</span>
              <span>弹性成本: ¥{{ scope.row.finished.elastic_cost.toFixed(2) }}</span>
            </div>
            <div v-if="scope.row.finished.cost_summary" class="cost-monitor">
              <span class="cost-monitor-item highest">历史最高: {{ formatCostMonitor(scope.row.finished.cost_summary.highest_cost) }}</span>
              <span class="cost-monitor-item current">当前成本: {{ formatCostMonitor(scope.row.finished.cost_summary.current_cost) }}</span>
              <span class="cost-monitor-item lowest">历史最低: {{ formatCostMonitor(scope.row.finished.cost_summary.lowest_cost) }}</span>
              <el-button link type="primary" size="small" @click="openCostHistory(scope.row)">成本历史</el-button>
            </div>
          </div>
          <div v-else-if="['bead', 'accessory', 'children_clothing'].includes(scope.row.product_type)" class="sku-details">
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
                <template #default="skuScope">{{ formatPrice(skuScope.row.weight, 2) }}g</template>
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
          <img
            v-if="scope.row.image_url"
            :src="scope.row.image_url"
            style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; cursor: pointer;"
            @click="imagePreviewRef.openPreview(scope.row.image_url)"
            alt="商品图片"
          />
          <span v-else style="color: #999">无图</span>
        </template>
      </el-table-column>
      <el-table-column prop="code" label="货号" width="180" sortable="custom" />
      <el-table-column prop="name" label="商品名称" min-width="120" />
      <el-table-column v-if="!props.hideProductType" prop="product_type_display" label="商品类型" width="120" />
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
          ¥{{ formatPrice(scope.row.product_type === 'finished' ? scope.row.cost_price : getListCost(scope.row)) }}
        </template>
      </el-table-column>
      <!-- 显示售卖价格 -->
      <el-table-column label="售卖价格" width="100">
        <template #default="scope">
          ¥{{ formatPrice(scope.row.product_type === 'finished' ? scope.row.selling_price : getDefaultSku(scope.row)?.selling_price) }}
        </template>
      </el-table-column>
      <!-- 显示利润率 -->
      <el-table-column v-if="props.products.some(p => p.product_type === 'finished')" label="利润率" width="90">
        <template #default="scope">
          <span v-if="scope.row.product_type === 'finished' && scope.row.selling_price > 0" :style="{ color: calculateProfitRate(scope.row, scope.row.finished) >= 30 ? '#10b981' : calculateProfitRate(scope.row, scope.row.finished) >= 15 ? '#f59e0b' : '#ef4444' }">
            {{ calculateProfitRate(scope.row, scope.row.finished) }}%
          </span>
          <span v-else style="color: #999">-</span>
        </template>
      </el-table-column>
      <!-- 显示利润值 -->
      <el-table-column v-if="props.products.some(p => p.product_type === 'finished')" label="利润" width="90">
        <template #default="scope">
          <span v-if="scope.row.product_type === 'finished'" :style="{ color: (scope.row.selling_price - scope.row.cost_price) >= 0 ? '#10b981' : '#ef4444' }">
            ¥{{ (scope.row.selling_price - scope.row.cost_price).toFixed(2) }}
          </span>
          <span v-else style="color: #999">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="location" label="库位" width="150" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="scope">
          {{ scope.row.created_at ? new Date(scope.row.created_at).toLocaleString('zh-CN') : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="scope">
          <el-button v-if="scope.row.product_type === 'finished'" size="small" type="warning" @click="openSimulate(scope.row)">模拟</el-button>
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 手机端卡片列表 -->
    <div v-if="isMobile" class="mobile-list" v-loading="loading">
      <div v-for="row in filteredProducts" :key="row.id" class="mobile-card">
        <div class="mobile-card-main" @click="toggleMobileExpand(row)">
          <div class="mobile-card-left">
            <img
              v-if="row.image_url"
              :src="row.image_url"
              class="mobile-card-img"
              @click.stop="imagePreviewRef.openPreview(row.image_url)"
              alt="商品图片"
            />
            <div v-else class="mobile-card-no-img">无图</div>
          </div>
          <div class="mobile-card-info">
            <div class="mobile-card-name">{{ row.name }}</div>
            <div class="mobile-card-code">{{ row.code }}</div>
            <div class="mobile-card-prices">
              <span class="mobile-price">成本: ¥{{ formatPrice(row.product_type === 'finished' ? row.cost_price : getListCost(row)) }}</span>
              <span class="mobile-price">售价: ¥{{ formatPrice(row.product_type === 'finished' ? row.selling_price : getDefaultSku(row)?.selling_price) }}</span>
            </div>
          </div>
          <div class="mobile-card-right">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
            <span class="mobile-expand-icon">{{ mobileExpandedIds.has(row.id) ? '▲' : '▼' }}</span>
          </div>
        </div>
        <!-- 手机端展开详情 -->
        <div v-if="mobileExpandedIds.has(row.id)" class="mobile-card-expand">
          <!-- 手串成品展开 -->
          <div v-if="row.product_type === 'finished' && row.finished" class="finished-details mobile-finished-details">
            <table class="detail-table mobile-detail-table" v-if="row.finished.beads.length > 0">
              <thead>
                <tr>
                  <th colspan="9" class="detail-table-header">串珠（{{ row.finished.beads.length }}种，共{{ calculateBeadsQuantity(row.finished.beads) }}颗，小计 ¥{{ calculateBeadsTotal(row.finished.beads).toFixed(2) }}）</th>
                </tr>
                <tr>
                  <th style="width:28px"></th>
                  <th style="width:80px">货号</th>
                  <th style="width:120px">SKU名称</th>
                  <th style="width:50px">数量</th>
                  <th style="width:80px">克价</th>
                  <th style="width:70px">单价</th>
                  <th style="width:60px">规格</th>
                  <th style="width:50px">品级</th>
                  <th style="width:80px">小计</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(bead, index) in row.finished.beads" :key="index">
                  <td><img v-if="bead.bead_image_url" :src="bead.bead_image_url" class="detail-thumb" @click="imagePreviewRef.openPreview(bead.bead_image_url)" /></td>
                  <td>{{ bead.bead_code || '-' }}</td>
                  <td>{{ bead.sku?.name || bead.sku?.sku_name || bead.bead_name }}</td>
                  <td>{{ bead.quantity }}</td>
                  <td>¥{{ formatPrice(bead.bead_purchase_cost, 2) }}/g</td>
                  <td>¥{{ bead.bead_cost_price.toFixed(2) }}</td>
                  <td>{{ bead.bead_size ? bead.bead_size + 'mm' : '-' }}</td>
                  <td>{{ bead.bead_quality_level || '-' }}</td>
                  <td>¥{{ (bead.bead_cost_price * bead.quantity).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
            <table class="detail-table mobile-detail-table" v-if="row.finished.accessories.length > 0">
              <thead>
                <tr>
                  <th colspan="6" class="detail-table-header">配件（{{ row.finished.accessories.length }}种，共{{ calculateAccessoriesQuantity(row.finished.accessories) }}个，小计 ¥{{ calculateAccessoriesTotal(row.finished.accessories).toFixed(2) }}）</th>
                </tr>
                <tr>
                  <th style="width:28px"></th>
                  <th style="width:80px">货号</th>
                  <th style="width:120px">SKU名称</th>
                  <th style="width:50px">数量</th>
                  <th style="width:70px">单价</th>
                  <th style="width:80px">小计</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(acc, index) in row.finished.accessories" :key="index">
                  <td><img v-if="acc.accessory_image_url" :src="acc.accessory_image_url" class="detail-thumb" @click="imagePreviewRef.openPreview(acc.accessory_image_url)" /></td>
                  <td>{{ acc.accessory_code || '-' }}</td>
                  <td>{{ acc.sku?.name || acc.sku?.sku_name || acc.accessory_name }}</td>
                  <td>{{ acc.quantity }}</td>
                  <td>¥{{ acc.accessory_cost_price.toFixed(2) }}</td>
                  <td>¥{{ (acc.accessory_cost_price * acc.quantity).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
            <div class="detail-summary">
              <span>工费: ¥{{ row.finished.labor_cost.toFixed(2) }}</span>
              <span>弹性成本: ¥{{ row.finished.elastic_cost.toFixed(2) }}</span>
            </div>
            <div v-if="row.finished.cost_summary" class="cost-monitor">
              <span class="cost-monitor-item highest">历史最高: {{ formatCostMonitor(row.finished.cost_summary.highest_cost) }}</span>
              <span class="cost-monitor-item current">当前成本: {{ formatCostMonitor(row.finished.cost_summary.current_cost) }}</span>
              <span class="cost-monitor-item lowest">历史最低: {{ formatCostMonitor(row.finished.cost_summary.lowest_cost) }}</span>
              <el-button link type="primary" size="small" @click="openCostHistory(row)">成本历史</el-button>
            </div>
          </div>
          <!-- 串珠/配件展开 -->
          <div v-else-if="['bead', 'accessory'].includes(row.product_type)" class="sku-details mobile-sku-details">
            <h4>SKU列表</h4>
            <div v-if="row.skus && row.skus.length > 0" class="mobile-sku-list">
              <div v-for="(sku, idx) in row.skus" :key="idx" class="mobile-sku-item">
                <div class="mobile-sku-row"><span class="mobile-sku-label">编码:</span> {{ sku.sku_code }}</div>
                <div class="mobile-sku-row"><span class="mobile-sku-label">名称:</span> {{ sku.sku_name || sku.name || '-' }}</div>
                <div class="mobile-sku-row"><span class="mobile-sku-label">规格:</span> {{ sku.size ? sku.size + 'mm' : '-' }}</div>
                <div class="mobile-sku-row"><span class="mobile-sku-label">成本:</span> ¥{{ formatPrice(sku.cost_price) }}</div>
                <div class="mobile-sku-row"><span class="mobile-sku-label">售价:</span> ¥{{ formatPrice(sku.selling_price) }}</div>
                <div v-if="row.product_type === 'bead'" class="mobile-sku-row"><span class="mobile-sku-label">克重:</span> {{ formatPrice(sku.weight, 2) }}g</div>
                <div class="mobile-sku-row"><span class="mobile-sku-label">品质:</span> {{ sku.quality_level || '-' }}</div>
                <el-tag v-if="sku.is_default" size="small" style="margin-top:4px">默认</el-tag>
              </div>
            </div>
            <el-empty v-else description="暂无SKU" :image-size="60" />
          </div>
          <div v-else class="mobile-no-detail">无明细</div>
          <!-- 操作按钮 -->
          <div class="mobile-card-actions">
            <el-button v-if="row.product_type === 'finished'" size="small" type="warning" @click="openSimulate(row)">模拟</el-button>
            <el-button size="small" @click="$emit('edit', row)">编辑</el-button>
            <el-button size="small" type="danger" @click="$emit('delete', row)">删除</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="filteredProducts.length === 0 && !loading" description="暂无数据" />

    <!-- 模拟克价对话框 -->
    <PriceSimulateDialog v-model="simulateVisible" :row="simulateRow" :is-mobile="isMobile" />

    <!-- 成本历史对话框 -->
    <FinishedCostHistoryDialog v-model="costHistoryVisible" :row="costHistoryRow" :is-mobile="isMobile" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import ProductImageCell from './ProductImageCell.vue'
import PriceSimulateDialog from './PriceSimulateDialog.vue'
import FinishedCostHistoryDialog from './FinishedCostHistoryDialog.vue'

const tableRef = ref(null)
const imagePreviewRef = ref(null)

// 手机端检测
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 手机端展开行控制
const mobileExpandedIds = ref(new Set())
const toggleMobileExpand = (row) => {
  if (mobileExpandedIds.value.has(row.id)) {
    mobileExpandedIds.value.delete(row.id)
  } else {
    mobileExpandedIds.value.add(row.id)
  }
  // 触发响应式更新
  mobileExpandedIds.value = new Set(mobileExpandedIds.value)
}

const collapseAll = () => {
  if (isMobile.value) {
    mobileExpandedIds.value = new Set()
    return
  }
  if (!tableRef.value) return
  filteredProducts.value.forEach(row => {
    tableRef.value.toggleRowExpansion(row, false)
  })
}

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
  },
  hideProductType: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'select-all', 'edit', 'delete', 'sort-change'])

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

// 童装列表成本取最低尺码成本，与成本表口径一致
const getListCost = (product) => {
  if (product.product_type === 'children_clothing') {
    const costs = (product.skus || []).map((sku) => Number(sku.cost_price))
    return costs.length ? Math.min(...costs) : 0
  }
  return getDefaultSku(product)?.cost_price
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

const handleSortChange = ({ prop, order }) => {
  emit('sort-change', { prop, order })
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

const formatCostMonitor = (value) => {
  if (value === null || value === undefined) return '—'
  return '¥' + Number(value).toFixed(2)
}

const calculateBeadsTotal = (beads) => {
  return beads.reduce((sum, bead) => sum + bead.bead_cost_price * bead.quantity, 0)
}

const calculateAccessoriesTotal = (accessories) => {
  return accessories.reduce((sum, acc) => sum + acc.accessory_cost_price * acc.quantity, 0)
}

const calculateBeadsQuantity = (beads) => {
  return beads.reduce((sum, bead) => sum + (Number(bead.quantity) || 0), 0)
}

const calculateAccessoriesQuantity = (accessories) => {
  return accessories.reduce((sum, acc) => sum + (Number(acc.quantity) || 0), 0)
}

const calculateTotalQuantity = (items = []) => {
  return items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0)
}

const calculateBeadQuantity = (finished) => {
  return calculateTotalQuantity(finished?.beads)
}

const calculateAccessoryQuantity = (finished) => {
  return calculateTotalQuantity(finished?.accessories)
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

const calculateProfitRate = (product, finished) => {
  const costPrice = product.cost_price || 0
  const sellingPrice = product.selling_price || 0
  if (sellingPrice <= 0) return 0
  return ((sellingPrice - costPrice) / sellingPrice * 100).toFixed(1)
}

// 模拟克价相关（弹窗由 PriceSimulateDialog 负责）
const simulateVisible = ref(false)
const simulateRow = ref(null)

const openSimulate = (row) => {
  simulateRow.value = row
  simulateVisible.value = true
}

// 成本历史相关（弹窗由 FinishedCostHistoryDialog 负责）
const costHistoryVisible = ref(false)
const costHistoryRow = ref(null)

const openCostHistory = (row) => {
  costHistoryRow.value = row
  costHistoryVisible.value = true
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
  padding: 12px 20px;
  overflow-x: auto;
}

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

.detail-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  vertical-align: middle;
}

.detail-summary {
  display: flex;
  gap: 24px;
  padding: 8px 10px;
  font-size: 14px;
  font-weight: 700;
  color: #303133;
  border-top: 2px solid #ebeef5;
}

.cost-monitor {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
  padding: 8px 10px;
  background: #f0f9ff;
  border-top: 1px dashed #d0e6f5;
}

.cost-monitor-item {
  font-size: 13px;
  font-weight: 700;
}

.cost-monitor-item.highest {
  color: #ef4444;
}

.cost-monitor-item.current {
  color: #303133;
}

.cost-monitor-item.lowest {
  color: #10b981;
}

.detail-total {
  font-weight: 700;
  color: #303133;
}

/* 手机端筛选区 */
.filter-mobile {
  padding: 12px;
}
.filter-mobile .mobile-form .el-form-item {
  margin-right: 0;
  margin-bottom: 8px;
  width: 100%;
}
.filter-mobile .mobile-form .el-form-item__content {
  width: 100%;
}
.filter-mobile .mobile-form .el-input,
.filter-mobile .mobile-form .el-select {
  width: 100% !important;
}

/* 手机端卡片列表 */
.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mobile-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}
.mobile-card-main {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  gap: 10px;
  cursor: pointer;
}
.mobile-card-left {
  flex-shrink: 0;
}
.mobile-card-img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
}
.mobile-card-no-img {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 6px;
  color: #999;
  font-size: 12px;
}
.mobile-card-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.mobile-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mobile-card-code {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
.mobile-card-prices {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  flex-wrap: wrap;
}
.mobile-price {
  font-size: 12px;
  color: #64748b;
}
.mobile-card-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.mobile-expand-icon {
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 2px;
}

/* 手机端展开详情 */
.mobile-card-expand {
  padding: 8px 12px 12px;
  border-top: 1px solid #ebeef5;
  background: #fafbfc;
}
.mobile-finished-details {
  padding: 0;
}
.mobile-detail-table {
  font-size: 12px;
}
.mobile-detail-table th,
.mobile-detail-table td {
  padding: 4px 6px;
  font-size: 12px;
}
.mobile-detail-table thead tr:nth-child(2) th {
  font-size: 11px;
}
.mobile-detail-table-header {
  font-size: 12px;
  padding: 6px !important;
}

/* 手机端SKU列表 */
.mobile-sku-details {
  padding: 0;
}
.mobile-sku-details h4 {
  font-size: 14px;
  margin-bottom: 8px;
}
.mobile-sku-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mobile-sku-item {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 13px;
}
.mobile-sku-row {
  padding: 2px 0;
  color: #606266;
}
.mobile-sku-label {
  color: #909399;
  margin-right: 4px;
}
.mobile-no-detail {
  color: #999;
  font-size: 13px;
  text-align: center;
  padding: 12px;
}
.mobile-card-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}
</style>
