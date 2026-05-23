<template>
  <div class="products">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">商品管理</span>
          <div class="header-actions">
            <el-button v-if="selectedIds.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedIds.length }})
            </el-button>
            <el-button type="primary" @click="handleAddProduct">
              <el-icon><Plus /></el-icon>
              添加商品
            </el-button>
          </div>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="product-tabs">
        <el-tab-pane label="手串成品" name="finished">
          <template #label>
            <span class="tab-label">
              <el-icon><Grid /></el-icon>
              手串成品
            </span>
          </template>
          <ProductTable
            :products="products"
            :loading="loading"
            :selected-ids="selectedIds"
            @select="handleSelect"
            @select-all="handleSelectAll"
            @edit="handleEditProduct"
            @delete="handleDeleteProduct"
          />
        </el-tab-pane>
        
        <el-tab-pane label="串珠" name="bead">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleCheck /></el-icon>
              串珠
            </span>
          </template>
          <ProductTable
            :products="products"
            :loading="loading"
            :selected-ids="selectedIds"
            @select="handleSelect"
            @select-all="handleSelectAll"
            @edit="handleEditProduct"
            @delete="handleDeleteProduct"
          />
        </el-tab-pane>
        
        <el-tab-pane label="手串配件" name="accessory">
          <template #label>
            <span class="tab-label">
              <el-icon><Box /></el-icon>
              手串配件
            </span>
          </template>
          <ProductTable
            :products="products"
            :loading="loading"
            :selected-ids="selectedIds"
            @select="handleSelect"
            @select-all="handleSelectAll"
            @edit="handleEditProduct"
            @delete="handleDeleteProduct"
          />
        </el-tab-pane>
      </el-tabs>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑商品对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="780px"
      class="product-dialog"
      @close="resetForm"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="货号" prop="code">
              <el-input v-model="form.code" placeholder="请输入货号" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入商品名称" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品类型" prop="product_type">
              <el-select v-model="form.product_type" placeholder="选择商品类型" style="width: 100%">
                <el-option 
                  v-for="type in productTypes" 
                  :key="type.value" 
                  :label="type.label" 
                  :value="type.value" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="is_active">
              <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <!-- SKU商品的采购/成本在SKU中维护 -->
          <el-col v-if="false && form.product_type === 'bead'" :span="12">
            <el-form-item label="采购成本" prop="purchase_cost">
              <div class="purchase-cost-container">
                <el-input-number 
                  v-model="form.purchase_cost" 
                  :min="0" 
                  :step="0.01" 
                  :precision="4" 
                  style="width: 140px" 
                  @change="calculateCostPrice"
                />
                <span class="unit-text">元/克</span>
              </div>
            </el-form-item>
          </el-col>
          <!-- 配件和成品显示成本价格 -->
          <el-col v-if="form.product_type === 'finished'" :span="12">
            <el-form-item label="成本价格" prop="cost_price">
              <el-input-number 
                v-model="form.cost_price" 
                :min="0" 
                :step="0.01" 
                :precision="2" 
                :disabled="form.product_type === 'finished'"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <!-- 单颗成本归入SKU -->
          <el-col v-if="false && form.product_type === 'bead'" :span="12">
            <el-form-item label="单颗成本">
              <el-input-number 
                v-model="form.cost_price" 
                :min="0" 
                :step="0.01" 
                :precision="2" 
                disabled
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <!-- 串珠/配件售价归入SKU，成品保留售价 -->
          <el-col v-if="form.product_type === 'finished'" :span="12">
            <el-form-item label="售卖价格" prop="selling_price">
              <el-input-number v-model="form.selling_price" :min="0" :step="0.01" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <!-- 串珠的售卖价格单独一行 -->
        <el-row v-if="false && form.product_type === 'bead'" :gutter="20">
          <el-col :span="24">
            <el-form-item label="售卖价格" prop="selling_price">
              <el-input-number v-model="form.selling_price" :min="0" :step="0.01" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 成品特有价格字段 -->
        <template v-if="form.product_type === 'finished'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="工费">
                <el-input-number v-model="form.labor_cost" :min="0" :step="0.01" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="弹性成本">
                <el-input-number v-model="form.elastic_cost" :min="0" :step="0.01" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </template>
        
        <el-row v-if="form.product_type === 'finished'" :gutter="20">
          <el-col :span="12">
            <el-form-item label="库位">
              <el-input v-model="form.location" placeholder="请输入库位" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-input v-model="form.supplier" placeholder="请输入供应商" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="商品图片">
          <div class="image-upload-container">
            <div
              v-if="!form.imagePreview && !form.image_url"
              class="image-uploader"
              @click="triggerImageUpload"
            >
              <el-icon class="image-uploader-icon"><Plus /></el-icon>
              <span>上传图片</span>
            </div>
            <div v-else class="image-preview-wrapper">
              <el-image
                :src="form.imagePreview || form.image_url"
                style="width: 120px; height: 120px"
                fit="cover"
                :preview-src-list="[form.imagePreview || form.image_url]"
                class="preview-image"
              />
              <div class="image-actions">
                <el-button
                  size="small"
                  type="danger"
                  @click="handleRemoveImage"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
            <input
              ref="imageInputRef"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              style="display: none"
              @change="handleImageSelect"
            />
          </div>
        </el-form-item>
        
        <!-- 串珠特有属性 -->
        <template v-if="false && form.product_type === 'bead'">
          <el-divider content-position="left">串珠属性</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="材质">
                <el-input v-model="form.material" placeholder="请输入材质" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="规格">
                <div class="size-input-container">
                  <el-input-number v-model="form.size" :min="1" :step="1" :precision="0" style="width: 100%" placeholder="请输入规格" />
                  <span class="unit-text">mm</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="颜色">
                <el-input v-model="form.color" placeholder="请输入颜色" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="单颗克重">
                <el-input-number v-model="form.weight" :min="0" :step="0.01" :precision="3" style="width: 100%" @change="calculateCostPrice" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="品质等级">
                <el-input-number 
                  v-model="form.quality_level" 
                  :min="1" 
                  :max="10" 
                  :step="1" 
                  :precision="0" 
                  style="width: 100%" 
                  placeholder="请输入品质等级(1-10)" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </template>

        <!-- 配件特有属性 -->
        <template v-if="false && form.product_type === 'accessory'">
          <el-divider content-position="left">配件属性</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="材质">
                <el-input v-model="form.material" placeholder="请输入材质" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="规格">
                <div class="size-input-container">
                  <el-input-number v-model="form.size" :min="1" :step="1" :precision="0" style="width: 100%" placeholder="请输入规格" />
                  <span class="unit-text">mm</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="颜色">
                <el-input v-model="form.color" placeholder="请输入颜色" clearable />
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <!-- SKU选项 -->
        <template v-if="form.product_type === 'bead' || form.product_type === 'accessory'">
          <el-divider content-position="left">SKU选项</el-divider>
          <el-alert type="info" :closable="false" show-icon style="margin-bottom: 12px">
            <template #title>同一货号下可维护多个规格/成本/克重/品质不同的 SKU，成品组合时会选择具体 SKU。</template>
          </el-alert>
          <el-button type="primary" size="small" @click="handleAddSku" style="margin-bottom: 12px">
            <el-icon><Plus /></el-icon> 添加SKU
          </el-button>
          <div v-for="(sku, index) in form.skus" :key="index" class="sku-card">
            <el-row :gutter="12">
              <el-col :span="6"><el-input v-model="sku.sku_code" placeholder="SKU编码" /></el-col>
              <el-col :span="6"><el-input v-model="sku.sku_name" placeholder="SKU名称" /></el-col>
              <el-col :span="4"><el-input-number v-model="sku.size" :min="0" :precision="0" placeholder="规格" style="width:100%" /></el-col>
              <el-col :span="4"><el-input-number v-model="sku.cost_price" :min="0" :precision="2" placeholder="单颗/件成本" style="width:100%" /></el-col>
              <el-col :span="4" class="sku-actions">
                <el-switch v-model="sku.is_default" active-text="默认" @change="() => setDefaultSku(index)" />
                <el-button type="danger" text @click="removeSku(index)"><el-icon><Delete /></el-icon></el-button>
              </el-col>
            </el-row>
            <el-row :gutter="12" style="margin-top: 10px">
              <el-col :span="5"><el-input v-model="sku.material" placeholder="材质" /></el-col>
              <el-col :span="5"><el-input v-model="sku.color" placeholder="颜色" /></el-col>
              <el-col :span="5"><el-input-number v-model="sku.purchase_cost" :min="0" :precision="4" placeholder="采购成本" style="width:100%" /></el-col>
              <el-col :span="5"><el-input-number v-model="sku.weight" :min="0" :precision="3" placeholder="克重" style="width:100%" /></el-col>
              <el-col :span="4"><el-input-number v-model="sku.quality_level" :min="1" :max="10" :precision="0" placeholder="品质" style="width:100%" /></el-col>
            </el-row>
            <el-row :gutter="12" style="margin-top: 10px">
              <el-col :span="6"><el-input-number v-model="sku.selling_price" :min="0" :precision="2" placeholder="售价" style="width:100%" /></el-col>
              <el-col :span="6"><el-input v-model="sku.location" placeholder="库位" /></el-col>
              <el-col :span="6"><el-input v-model="sku.supplier" placeholder="供应商" /></el-col>
              <el-col :span="6"><el-input v-model="sku.remark" placeholder="备注" /></el-col>
            </el-row>
          </div>
        </template>

        <!-- 成品特有属性 -->
        <template v-if="form.product_type === 'finished'">
          <el-divider content-position="left">成品组成</el-divider>
          <div class="cost-summary" v-if="form.beads.length > 0 || form.accessories.length > 0">
            <div class="cost-item">
              <span class="label">串珠成本：</span>
              <span class="value">¥{{ beadsCost.toFixed(2) }}</span>
            </div>
            <div class="cost-item">
              <span class="label">配件成本：</span>
              <span class="value">¥{{ accessoriesCost.toFixed(2) }}</span>
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
                    <img
                      v-if="bead.image_url || bead.bead_image_url"
                      :src="bead.image_url || bead.bead_image_url"
                      class="selected-item-image"
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
                    <img
                      v-if="acc.image_url || acc.accessory_image_url"
                      :src="acc.image_url || acc.accessory_image_url"
                      class="selected-item-image"
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
        </template>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 选择串珠对话框 -->
    <el-dialog
      v-model="beadDialogVisible"
      title="选择串珠"
      width="900px"
      class="selection-dialog"
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
              <span v-if="bead.weight" class="product-weight">{{ bead.weight?.toFixed(3) }}g</span>
            </div>
            <div class="product-badges">
              <span class="badge quality-badge">{{ bead.skus?.length || 0 }} 个SKU</span>
            </div>
            <el-select v-if="bead.skus?.length" v-model="bead.selectedSku" value-key="id" placeholder="选择SKU" style="width:100%; margin-top:8px" @click.stop>
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
      width="900px"
      class="selection-dialog"
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
            <el-select v-if="accessory.skus?.length" v-model="accessory.selectedSku" value-key="id" placeholder="选择SKU" style="width:100%; margin-top:8px" @click.stop>
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
import { ref, reactive, onMounted, computed, defineAsyncComponent, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Picture, Document, Grid, CircleCheck, Box, Delete, Check } from '@element-plus/icons-vue'
import { getProductTypes, getProducts, createProduct, updateProduct, deleteProduct, getProductDetail, getAccessories, getBeads } from '@/api'

// 产品表格组件
const ProductTable = defineAsyncComponent(() => import('./components/ProductTable.vue'))

// 商品类型
const productTypes = ref([])
// 商品列表
const products = ref([])
// 配件列表
const accessories = ref([])
// 串珠列表
const beads = ref([])
// 选中的ID
const selectedIds = ref([])
// 加载状态
const loading = ref(false)
const submitLoading = ref(false)
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
// 筛选表单
const filterForm = reactive({
  product_type: '',
  is_active: ''
})
// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})
// 对话框状态
const dialogVisible = ref(false)
const beadDialogVisible = ref(false)
const accessoryDialogVisible = ref(false)
const dialogTitle = ref('添加商品')
// 表单数据
const form = reactive({
  id: '',
  code: '',
  name: '',
  product_type: '',
  purchase_cost: 0,
  cost_price: 0,
  selling_price: 0,
  is_active: true,
  location: '',
  supplier: '',
  material: '',
  size: '',
  color: '',
  weight: 0,
  quality_level: 5,
  remark: '',
  beads: [],
  accessories: [],
  labor_cost: 0,
  elastic_cost: 0,
  image: null,
  imagePreview: '',
  image_url: '',
  remove_image: false,
  skus: []
})
// 表单验证规则
const rules = {
  code: [{ required: true, message: '请输入货号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  product_type: [{ required: true, message: '请选择商品类型', trigger: 'change' }],
  purchase_cost: [
    { 
      required: true, 
      message: '请输入采购成本', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.product_type === 'bead') {
          if (value === null || value === undefined || value === '') {
            callback(new Error('请输入采购成本'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      }
    }
  ],
  cost_price: [
    { 
      required: true, 
      message: '请输入成本价格', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.product_type === 'finished') {
          callback()
        } else if (form.product_type === 'bead') {
          callback()
        } else if (value === null || value === undefined || value === '') {
          callback(new Error('请输入成本价格'))
        } else {
          callback()
        }
      }
    }
  ],
  selling_price: [{ required: true, message: '请输入售卖价格', trigger: 'blur' }]
}
// 表单引用
const formRef = ref(null)
// 图片上传输入框引用
const imageInputRef = ref(null)
// 配件搜索
const accessorySearch = ref('')
// 串珠搜索
const beadSearch = ref('')
// 当前选中的标签页
const activeTab = ref('finished')

// 计算串珠成本
const beadsCost = computed(() => {
  return form.beads.reduce((sum, bead) => {
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
  return form.accessories.reduce((sum, acc) => {
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
  return beadsCost.value + accessoriesCost.value + form.labor_cost + form.elastic_cost
})

// 计算利润
const profit = computed(() => {
  return form.selling_price - totalCost.value
})

// 计算利润率
const profitRate = computed(() => {
  if (form.selling_price <= 0) return 0
  return (profit.value / form.selling_price) * 100
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

// 计算单颗成本
const calculateCostPrice = () => {
  if (form.product_type === 'bead') {
    const purchaseCost = Number(form.purchase_cost) || 0
    const weight = Number(form.weight) || 0
    form.cost_price = purchaseCost * weight
  }
}

// 监听成品组成变化，自动计算成本价格
watch([
  () => form.beads,
  () => form.labor_cost,
  () => form.elastic_cost,
  () => form.accessories
], () => {
  if (form.product_type === 'finished') {
    form.cost_price = totalCost.value
  }
}, { deep: true, immediate: true })

// 获取商品类型
const fetchProductTypes = async () => {
  try {
    const response = await getProductTypes()
    productTypes.value = response.data.product_types
  } catch (error) {
    ElMessage.error('获取商品类型失败')
    console.error(error?.response?.data || error)
  }
}

// 获取商品列表
const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    // 使用当前标签页作为商品类型筛选
    params.product_type = activeTab.value
    if (filterForm.is_active !== '') {
      params.is_active = filterForm.is_active
    }
    const response = await getProducts(params)
    products.value = response.data.products
    pagination.total = response.data.total_count
  } catch (error) {
    ElMessage.error('获取商品列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 监听标签页切换
const handleTabChange = () => {
  selectedIds.value = []
  pagination.currentPage = 1
  filterForm.is_active = ''
  fetchProducts()
}

// 处理选择
const handleSelect = (id, checked) => {
  if (checked) {
    selectedIds.value.push(id)
  } else {
    const index = selectedIds.value.indexOf(id)
    if (index > -1) {
      selectedIds.value.splice(index, 1)
    }
  }
}

// 处理全选
const handleSelectAll = (ids) => {
  selectedIds.value = ids
}

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

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchProducts()
}

// 处理分页页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  fetchProducts()
}

// 处理添加商品
const handleAddProduct = () => {
  dialogTitle.value = '添加商品'
  resetForm()
  form.product_type = activeTab.value
  form.is_active = true
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: '',
    code: '',
    name: '',
    product_type: '',
    purchase_cost: 0,
    cost_price: 0,
    selling_price: 0,
    is_active: true,
    location: '',
    supplier: '',
    material: '',
    size: '',
    color: '',
    weight: 0,
    quality_level: 5,
    remark: '',
    beads: [],
    accessories: [],
    labor_cost: 0,
    elastic_cost: 0,
    image: null,
    imagePreview: '',
    image_url: '',
    remove_image: false,
    skus: []
  })
  formRef.value?.resetFields()
}

// 触发图片上传
const triggerImageUpload = () => {
  if (imageInputRef.value) {
    imageInputRef.value.value = ''
    imageInputRef.value.click()
  }
}

// 处理图片选择
const handleImageSelect = (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  const file = files[0]
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 PNG、JPEG、GIF 和 WEBP 格式的图片')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  form.image = file
  form.remove_image = false
  
  const reader = new FileReader()
  reader.onload = (e) => {
    form.imagePreview = e.target.result
  }
  reader.readAsDataURL(file)
}

// 处理删除图片
const handleRemoveImage = () => {
  form.image = null
  form.imagePreview = ''
  form.image_url = ''
  form.remove_image = true
}

// 处理编辑商品
const handleEditProduct = async (row) => {
  dialogTitle.value = '编辑商品'
  try {
    const response = await getProductDetail(row.id)
    const product = response.data
    Object.assign(form, {
      id: product.id,
      code: product.code,
      name: product.name,
      product_type: product.product_type,
      purchase_cost: product.purchase_cost || 0,
      cost_price: product.cost_price,
      selling_price: product.selling_price,
      is_active: product.is_active,
      location: product.location,
      supplier: product.supplier,
      material: product.bead?.material || product.accessory?.material || '',
      size: product.bead?.size || product.accessory?.size || '',
      color: product.bead?.color || product.accessory?.color || '',
      weight: product.bead?.weight || 0,
      quality_level: product.bead?.quality_level || 5,
      remark: product.bead?.remark || '',
      beads: (product.finished?.beads || []).map(bead => ({
        ...bead,
        sku: bead.sku || {
          sku_name: bead.sku_name || '',
          name: bead.sku_name || '',
          size: bead.bead_size || bead.size,
          weight: bead.bead_weight,
          quality_level: bead.bead_quality_level,
          remark: bead.bead_remark,
          cost_price: bead.bead_cost_price
        },
        sku_id: bead.sku_id,
        cost_price: bead.bead_cost_price,
        image_url: bead.bead_image_url
      })),
      accessories: (product.finished?.accessories || []).map(acc => ({
        ...acc,
        sku: acc.sku || {
          sku_name: acc.sku_name || '',
          name: acc.sku_name || '',
          size: acc.accessory_size || acc.size,
          cost_price: acc.accessory_cost_price
        },
        sku_id: acc.sku_id,
        cost_price: acc.accessory_cost_price,
        image_url: acc.accessory_image_url
      })),
      labor_cost: product.finished?.labor_cost || 0,
      elastic_cost: product.finished?.elastic_cost || 0,
      image: null,
      imagePreview: '',
      image_url: product.image_url || '',
      remove_image: false,
      skus: (product.skus || []).map(sku => ({ ...sku, sku_name: sku.sku_name || sku.name }))
    })
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取商品详情失败')
    console.error(error)
  }
}

// 处理删除商品
const handleDeleteProduct = (row) => {
  ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    submitLoading.value = true
    try {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      fetchProducts()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

// 批量删除
const handleBatchDelete = () => {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 个商品吗？`, '批量删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    submitLoading.value = true
    try {
      for (const id of selectedIds.value) {
        await deleteProduct(id)
      }
      ElMessage.success('批量删除成功')
      selectedIds.value = []
      fetchProducts()
    } catch (error) {
      ElMessage.error('批量删除失败')
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

// 处理添加串珠
const handleAddBead = () => {
  fetchBeads()
  beadDialogVisible.value = true
}

// 处理选择串珠
const handleSelectBead = (bead) => {
  const sku = bead.selectedSku || bead.skus?.find(s => s.is_default) || bead.skus?.[0] || {}
  const existing = form.beads.find(item => item.bead_id === bead.id && item.sku_id === sku.id)
  if (existing) {
    ElMessage.warning('该串珠SKU已经添加过了')
    return
  }
  form.beads.push({
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

// 处理添加配件
const ensureDefaultSku = () => {
  if (!['bead', 'accessory'].includes(form.product_type)) return
  if (form.skus.length === 0) {
    form.skus.push({
      sku_code: `${form.code || 'SKU'}-默认`,
      sku_name: '默认SKU',
      selling_price: form.selling_price,
      location: form.location,
      supplier: form.supplier,
      material: form.material,
      size: form.size,
      color: form.color,
      purchase_cost: form.purchase_cost,
      cost_price: form.cost_price,
      weight: form.weight,
      quality_level: form.quality_level,
      remark: form.remark,
      is_default: true,
      is_active: true
    })
  }
}

const handleAddSku = () => {
  form.skus.push({
    sku_code: `${form.code || 'SKU'}-${form.skus.length + 1}`,
    sku_name: '', selling_price: form.selling_price, location: form.location, supplier: form.supplier, material: form.material, size: form.size, color: form.color,
    purchase_cost: form.purchase_cost, cost_price: form.cost_price, weight: form.weight,
    quality_level: form.quality_level, remark: '', is_default: form.skus.length === 0, is_active: true
  })
}

const removeSku = (index) => {
  form.skus.splice(index, 1)
  if (form.skus.length && !form.skus.some(s => s.is_default)) form.skus[0].is_default = true
}

const setDefaultSku = (index) => {
  form.skus.forEach((sku, i) => { sku.is_default = i === index })
}

const skuLabel = (item, prefix = '') => {
  const sku = item.sku || item
  const parts = [sku.sku_name || sku.name, sku.size ? `${sku.size}mm` : '', sku.weight ? `${Number(sku.weight).toFixed(3)}g` : '', sku.quality_level ? `品质${sku.quality_level}` : ''].filter(Boolean)
  return `${prefix}${parts.join(' / ')}`
}


const handleAddAccessory = () => {
  fetchAccessories()
  accessoryDialogVisible.value = true
}

// 处理选择配件
const handleSelectAccessory = (accessory) => {
  const sku = accessory.selectedSku || accessory.skus?.find(s => s.is_default) || accessory.skus?.[0] || {}
  const existing = form.accessories.find(item => item.accessory_id === accessory.id && item.sku_id === sku.id)
  if (existing) {
    ElMessage.warning('该配件SKU已经添加过了')
    return
  }
  form.accessories.push({
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

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const data = {
          code: form.code,
          name: form.name,
          product_type: form.product_type,
          purchase_cost: form.purchase_cost,
          cost_price: form.cost_price,
          selling_price: form.selling_price,
          is_active: form.is_active,
          location: form.location,
          supplier: form.supplier
        }

        if (form.product_type === 'bead') {
          data.material = form.material
          data.size = form.size
          data.color = form.color
          data.weight = form.weight
          data.quality_level = form.quality_level
          data.remark = form.remark
          data.skus = form.skus
        } else if (form.product_type === 'accessory') {
          data.material = form.material
          data.size = form.size
          data.color = form.color
          data.skus = form.skus
        } else if (form.product_type === 'finished') {
          data.beads = form.beads
          data.accessories = form.accessories
          data.labor_cost = form.labor_cost
          data.elastic_cost = form.elastic_cost
        }

        if (form.image) {
          data.image = form.image
        }
        if (form.id && form.remove_image) {
          data.remove_image = true
        }

        if (form.id) {
          await updateProduct(form.id, data)
          ElMessage.success('更新成功')
        } else {
          await createProduct(data)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchProducts()
      } catch (error) {
        ElMessage.error(error?.response?.data?.error || '操作失败')
        console.error(error?.response?.data || error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 初始化
onMounted(() => {
  fetchProductTypes()
  fetchProducts()
})
</script>

<style scoped>
.products {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 24px;
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.product-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.product-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 500;
}

.tab-label .el-icon {
  font-size: 18px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 对话框样式 */
.product-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.product-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  margin: 0;
}

.product-dialog :deep(.el-dialog__title) {
  color: #ffffff;
  font-weight: 600;
}

.product-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #ffffff;
}

.product-dialog :deep(.el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

/* 表单间距优化 */
.product-dialog :deep(.el-form-item) {
  margin-bottom: 18px;
}

.product-dialog :deep(.el-divider--left) {
  margin: 20px 0;
}

.purchase-cost-container,
.size-input-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.unit-text {
  font-size: 14px;
  color: #64748b;
  white-space: nowrap;
}

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
  color: #667eea;
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
  object-fit: cover;
  display: block;
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
  color: #667eea;
  background: #f0f4ff;
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

.image-upload-container {
  width: 100%;
}

.image-uploader {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  cursor: pointer;
  width: 120px;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  background: #f8fafc;
}

.image-uploader:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.image-uploader-icon {
  font-size: 32px;
  color: #94a3b8;
}

.image-uploader span {
  font-size: 14px;
  color: #64748b;
}

.image-preview-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.preview-image {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-actions {
  display: flex;
  gap: 8px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 选择对话框样式 */
.selection-dialog {
  --dialog-bg: #ffffff;
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --card-bg: #ffffff;
  --text-primary: #1a1a2e;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --hover-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.selection-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.selection-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0 16px;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(102, 126, 234, 0.15);
}

/* 卡片容器 */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  max-height: 450px;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

/* 产品卡片 */
.product-card {
  position: relative;
  background: var(--card-bg);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
}

.product-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
  border-color: #667eea;
}

.product-card:hover .card-image-wrapper {
  transform: scale(1.05);
}

/* 卡片图片 */
.card-image-wrapper {
  position: relative;
  width: 100%;
  min-height: 160px;
  max-height: 220px;
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
  color: var(--text-primary);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.product-weight {
  font-size: 13px;
  color: var(--text-secondary);
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
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 15px;
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
  .products {
    padding: 12px;
  }
  
  .cards-container {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
  
  .card-image-wrapper {
    height: 120px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
}
.sku-card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 12px;
  background: #f8fafc;
}
.sku-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

</style>
