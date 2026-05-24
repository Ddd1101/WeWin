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
            <h4>成品组成明细</h4>
            
            <!-- 串珠列表 -->
            <div class="section" v-if="scope.row.finished.beads.length > 0">
              <h5>串珠</h5>
              <el-table :data="scope.row.finished.beads" size="small" style="width: 100%">
                <el-table-column label="缩略图" width="80">
                  <template #default="scope">
                    <el-image
                      v-if="scope.row.bead_image_url"
                      :src="scope.row.bead_image_url"
                      style="width: 40px; height: 40px"
                      fit="cover"
                      :preview-src-list="[scope.row.bead_image_url]"
                    />
                    <span v-else style="color: #999">无图</span>
                  </template>
                </el-table-column>
                <el-table-column prop="bead_name" label="名称" />
                <el-table-column label="单价(元/克)" width="100">
                  <template #default="scope">¥{{ scope.row.bead_cost_price.toFixed(2) }}</template>
                </el-table-column>
                <el-table-column label="单颗克重" width="90">
                  <template #default="scope">{{ scope.row.bead_weight?.toFixed(3) || '-' }}</template>
                </el-table-column>
                <el-table-column label="品质等级" width="80">
                  <template #default="scope">{{ scope.row.bead_quality_level || '-' }}</template>
                </el-table-column>
                <el-table-column label="备注" min-width="100">
                  <template #default="scope">{{ scope.row.bead_remark || '-' }}</template>
                </el-table-column>
                <el-table-column label="数量" width="80">
                  <template #default="scope">{{ scope.row.quantity }}</template>
                </el-table-column>
                <el-table-column label="小计" width="100">
                  <template #default="scope">
                    ¥{{ (scope.row.bead_cost_price * scope.row.quantity).toFixed(2) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <!-- 配件列表 -->
            <div class="section" v-if="scope.row.finished.accessories.length > 0">
              <h5>配件</h5>
              <el-table :data="scope.row.finished.accessories" size="small" style="width: 100%">
                <el-table-column label="缩略图" width="80">
                  <template #default="scope">
                    <el-image
                      v-if="scope.row.accessory_image_url"
                      :src="scope.row.accessory_image_url"
                      style="width: 40px; height: 40px"
                      fit="cover"
                      :preview-src-list="[scope.row.accessory_image_url]"
                    />
                    <span v-else style="color: #999">无图</span>
                  </template>
                </el-table-column>
                <el-table-column prop="accessory_name" label="名称" />
                <el-table-column label="单价" width="100">
                  <template #default="scope">¥{{ scope.row.accessory_cost_price.toFixed(2) }}</template>
                </el-table-column>
                <el-table-column label="数量" width="80">
                  <template #default="scope">{{ scope.row.quantity }}</template>
                </el-table-column>
                <el-table-column label="小计" width="100">
                  <template #default="scope">
                    ¥{{ (scope.row.accessory_cost_price * scope.row.quantity).toFixed(2) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <!-- 工费和弹性成本 -->
            <div class="section">
              <h5>其他成本</h5>
              <div class="cost-item">
                <span>工费：</span>
                <span class="amount">¥{{ scope.row.finished.labor_cost.toFixed(2) }}</span>
              </div>
              <div class="cost-item">
                <span>弹性成本：</span>
                <span class="amount">¥{{ scope.row.finished.elastic_cost.toFixed(2) }}</span>
              </div>
            </div>
            
            <!-- 总成本 -->
            <div class="total-cost">
              <span>总成本：</span>
              <span class="amount">¥{{ calculateTotalCost(scope.row.finished).toFixed(2) }}</span>
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
          ¥{{ formatPrice(getDefaultSku(scope.row)?.cost_price) }}
        </template>
      </el-table-column>
      <!-- 显示售卖价格 -->
      <el-table-column label="售卖价格" width="100">
        <template #default="scope">
          ¥{{ formatPrice(getDefaultSku(scope.row)?.selling_price) }}
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
.sku-details,
.finished-details {
  padding: 20px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.sku-details h4,
.finished-details h4 {
  margin: 0 0 15px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.finished-details h5 {
  margin: 20px 0 10px 0;
  color: #475569;
  font-size: 14px;
  border-left: 3px solid #667eea;
  padding-left: 8px;
}

.finished-details .section {
  margin-bottom: 15px;
}

.finished-details .cost-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: #64748b;
}

.finished-details .total-cost {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  font-size: 16px;
  font-weight: bold;
  color: #1e293b;
  border-top: 1px solid #e2e8f0;
  margin-top: 10px;
  padding-top: 15px;
}

.finished-details .amount {
  font-weight: bold;
  color: #667eea;
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
