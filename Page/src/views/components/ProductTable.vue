<template>
  <div>
    <!-- 自定义图片预览 -->
    <div v-if="previewVisible" class="image-preview-overlay" @click="closePreview">
      <div class="image-preview-container" @click.stop>
        <div class="image-preview-toolbar">
          <button class="image-preview-btn" @click="zoomOut" title="缩小">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <button class="image-preview-btn" @click="zoomIn" title="放大">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <button class="image-preview-btn" @click="rotateLeft" title="逆时针旋转">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 4v6h6"></path>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
            </svg>
          </button>
          <button class="image-preview-btn" @click="rotateRight" title="顺时针旋转">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"></path>
              <path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"></path>
            </svg>
          </button>
          <button class="image-preview-btn image-preview-btn-reset" @click="resetTransform" title="重置">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"></path>
              <path d="M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
              <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
            </svg>
          </button>
          <button class="image-preview-close" @click="closePreview" title="关闭">×</button>
        </div>
        <div 
          class="image-preview-img-wrapper"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
          @touchstart="startDrag"
          @touchmove="onDrag"
          @touchend="stopDrag"
        >
          <img 
            :src="previewImage" 
            class="image-preview-img" 
            :style="imgStyle"
            alt="预览图片" 
          />
        </div>
      </div>
    </div>

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
                  <td><img v-if="bead.bead_image_url" :src="bead.bead_image_url" class="detail-thumb" @click="openPreview(bead.bead_image_url)" /></td>
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
                  <td><img v-if="acc.accessory_image_url" :src="acc.accessory_image_url" class="detail-thumb" @click="openPreview(acc.accessory_image_url)" /></td>
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
            @click="openPreview(scope.row.image_url)"
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
          ¥{{ formatPrice(scope.row.product_type === 'finished' ? scope.row.cost_price : getDefaultSku(scope.row)?.cost_price) }}
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
              @click.stop="openPreview(row.image_url)"
              alt="商品图片"
            />
            <div v-else class="mobile-card-no-img">无图</div>
          </div>
          <div class="mobile-card-info">
            <div class="mobile-card-name">{{ row.name }}</div>
            <div class="mobile-card-code">{{ row.code }}</div>
            <div class="mobile-card-prices">
              <span class="mobile-price">成本: ¥{{ formatPrice(row.product_type === 'finished' ? row.cost_price : getDefaultSku(row)?.cost_price) }}</span>
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
                  <td><img v-if="bead.bead_image_url" :src="bead.bead_image_url" class="detail-thumb" @click="openPreview(bead.bead_image_url)" /></td>
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
                  <td><img v-if="acc.accessory_image_url" :src="acc.accessory_image_url" class="detail-thumb" @click="openPreview(acc.accessory_image_url)" /></td>
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
    <el-dialog v-model="simulateVisible" title="克价模拟" :width="isMobile ? '95%' : '1200px'" :fullscreen="isMobile">
      <div v-if="simulateRow" class="simulate-content">
        <div class="simulate-info" :class="{ 'simulate-info-mobile': isMobile }">
          <span>货号: {{ simulateRow.code }}</span>
          <span>商品名称: {{ simulateRow.name }}</span>
          <span>售价: ¥{{ simulateRow.selling_price.toFixed(2) }}</span>
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
            <span>原成本: <b>¥{{ simulateOriginalCost.toFixed(2) }}</b></span>
            <span>新成本: <b :style="{ color: simulateNewCost > simulateOriginalCost ? '#ef4444' : '#10b981' }">¥{{ simulateNewCost.toFixed(2) }}</b></span>
            <span>成本变动: <b :style="{ color: simulateNewCost > simulateOriginalCost ? '#ef4444' : '#10b981' }">{{ simulateNewCost > simulateOriginalCost ? '+' : '' }}¥{{ (simulateNewCost - simulateOriginalCost).toFixed(2) }}</b></span>
          </div>
          <div class="summary-row">
            <span>原利润: <b>¥{{ (simulateRow.selling_price - simulateOriginalCost).toFixed(2) }}</b></span>
            <span>新利润: <b :style="{ color: (simulateRow.selling_price - simulateNewCost) >= 0 ? '#10b981' : '#ef4444' }">¥{{ (simulateRow.selling_price - simulateNewCost).toFixed(2) }}</b></span>
            <span>原利润率: <b>{{ simulateRow.selling_price > 0 ? ((simulateRow.selling_price - simulateOriginalCost) / simulateRow.selling_price * 100).toFixed(1) : 0 }}%</b></span>
            <span>新利润率: <b :style="{ color: simulateNewProfitRate >= 30 ? '#10b981' : simulateNewProfitRate >= 15 ? '#f59e0b' : '#ef4444' }">{{ simulateNewProfitRate }}%</b></span>
          </div>
        </div>
      </div>
      <template #footer>
        <div :class="{ 'simulate-footer-mobile': isMobile }">
          <el-button @click="resetSimulate">{{ isMobile ? '重置' : '重置' }}</el-button>
          <el-button type="primary" @click="simulateVisible = false">{{ isMobile ? '关闭' : '关闭' }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'

const tableRef = ref(null)

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

// 图片预览相关
const previewVisible = ref(false)
const previewImage = ref('')
const scale = ref(1)
const rotation = ref(0)
const positionX = ref(0)
const positionY = ref(0)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)

const imgStyle = computed(() => {
  return {
    transform: `translate(${positionX.value}px, ${positionY.value}px) scale(${scale.value}) rotate(${rotation.value}deg)`,
    transition: isDragging.value ? 'none' : 'transform 0.2s ease-out'
  }
})

const openPreview = (imageUrl) => {
  previewImage.value = imageUrl
  previewVisible.value = true
  scale.value = 1
  rotation.value = 0
  positionX.value = 0
  positionY.value = 0
  isDragging.value = false
  document.body.style.overflow = 'hidden'
}

const closePreview = () => {
  previewVisible.value = false
  previewImage.value = ''
  scale.value = 1
  rotation.value = 0
  positionX.value = 0
  positionY.value = 0
  isDragging.value = false
  document.body.style.overflow = ''
}

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.25, 5)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.25, 0.25)
}

const rotateLeft = () => {
  rotation.value -= 90
}

const rotateRight = () => {
  rotation.value += 90
}

const resetTransform = () => {
  scale.value = 1
  rotation.value = 0
  positionX.value = 0
  positionY.value = 0
}

// 拖动功能
const startDrag = (e) => {
  if (scale.value <= 1) return
  
  isDragging.value = true
  const clientX = e.clientX || e.touches?.[0]?.clientX
  const clientY = e.clientY || e.touches?.[0]?.clientY
  startX.value = clientX - positionX.value
  startY.value = clientY - positionY.value
}

const onDrag = (e) => {
  if (!isDragging.value || scale.value <= 1) return
  
  e.preventDefault()
  const clientX = e.clientX || e.touches?.[0]?.clientX
  const clientY = e.clientY || e.touches?.[0]?.clientY
  positionX.value = clientX - startX.value
  positionY.value = clientY - startY.value
}

const stopDrag = () => {
  isDragging.value = false
}

// ESC键关闭预览
document.addEventListener('keydown', (e) => {
  if (!previewVisible.value) return
  
  if (e.key === 'Escape') {
    closePreview()
  } else if (e.key === '+' || e.key === '=') {
    zoomIn()
  } else if (e.key === '-') {
    zoomOut()
  } else if (e.key === 'ArrowLeft') {
    rotateLeft()
  } else if (e.key === 'ArrowRight') {
    rotateRight()
  } else if (e.key.toLowerCase() === 'r') {
    resetTransform()
  }
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

// 模拟克价相关
const simulateVisible = ref(false)
const simulateRow = ref(null)
const simulateBeads = ref([])
const simulateAccessories = ref([])

const openSimulate = (row) => {
  simulateRow.value = row
  simulateBeads.value = (row.finished?.beads || []).map(b => ({
    ...b,
    newPurchaseCost: b.bead_purchase_cost || 0
  }))
  simulateAccessories.value = (row.finished?.accessories || []).map(a => ({
    ...a,
    newCostPrice: a.accessory_cost_price || 0
  }))
  simulateVisible.value = true
}

const resetSimulate = () => {
  simulateBeads.value.forEach(b => {
    b.newPurchaseCost = b.bead_purchase_cost || 0
  })
  simulateAccessories.value.forEach(a => {
    a.newCostPrice = a.accessory_cost_price || 0
  })
}

const simulateOriginalCost = computed(() => {
  if (!simulateRow.value?.finished) return 0
  const f = simulateRow.value.finished
  let total = 0
  f.beads.forEach(b => { total += b.bead_cost_price * b.quantity })
  f.accessories.forEach(a => { total += a.accessory_cost_price * a.quantity })
  total += f.labor_cost + f.elastic_cost
  return total
})

const simulateNewCost = computed(() => {
  if (!simulateRow.value?.finished) return 0
  const f = simulateRow.value.finished
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
  if (!simulateRow.value || simulateRow.value.selling_price <= 0) return '0.0'
  return ((simulateRow.value.selling_price - simulateNewCost.value) / simulateRow.value.selling_price * 100).toFixed(1)
})
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

<style>
/* 自定义图片预览样式 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  animation: fadeIn 0.2s ease-out;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.image-preview-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.image-preview-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  background: rgba(0, 0, 0, 0.6);
  padding: 12px 20px;
  border-radius: 50px;
  backdrop-filter: blur(10px);
}

.image-preview-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.image-preview-btn svg {
  width: 20px;
  height: 20px;
}

.image-preview-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.image-preview-btn:active {
  transform: scale(0.95);
}

.image-preview-btn-reset {
  margin-right: 8px;
}

.image-preview-close {
  width: 44px;
  height: 44px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  line-height: 1;
}

.image-preview-close:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.image-preview-img-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 90vw;
  max-height: 75vh;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.image-preview-img-wrapper:active {
  cursor: grabbing;
}

.image-preview-img {
  max-width: 100%;
  max-height: 75vh;
  border-radius: 8px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
  object-fit: contain;
  pointer-events: none;
}
</style>
