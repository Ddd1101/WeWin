<template>
  <div class="products">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="handleAddProduct">添加商品</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="串珠" name="bead">
          <div class="filter-container">
            <el-form :inline="true" :model="filterForm" class="demo-form-inline">
              <el-form-item label="状态">
                <el-select v-model="filterForm.is_active" placeholder="选择状态" style="width: 120px">
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
          
          <el-table :data="products" style="width: 100%" row-key="id">
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
            <el-table-column prop="cost_price" label="成本价格" width="100" />
            <el-table-column prop="selling_price" label="售卖价格" width="100" />
            <el-table-column prop="location" label="库位" width="120" />
            <el-table-column prop="supplier" label="供应商" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                  {{ scope.row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="handleEditProduct(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteProduct(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
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
        </el-tab-pane>
        
        <el-tab-pane label="手串成品" name="finished">
          <div class="filter-container">
            <el-form :inline="true" :model="filterForm" class="demo-form-inline">
              <el-form-item label="状态">
                <el-select v-model="filterForm.is_active" placeholder="选择状态" style="width: 120px">
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
          
          <el-table :data="products" style="width: 100%" row-key="id">
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
            <el-table-column prop="cost_price" label="成本价格" width="100" />
            <el-table-column prop="selling_price" label="售卖价格" width="100" />
            <el-table-column prop="location" label="库位" width="120" />
            <el-table-column prop="supplier" label="供应商" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                  {{ scope.row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="handleEditProduct(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteProduct(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
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
        </el-tab-pane>
        
        <el-tab-pane label="手串配件" name="accessory">
          <div class="filter-container">
            <el-form :inline="true" :model="filterForm" class="demo-form-inline">
              <el-form-item label="状态">
                <el-select v-model="filterForm.is_active" placeholder="选择状态" style="width: 120px">
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
          
          <el-table :data="products" style="width: 100%" row-key="id">
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
            <el-table-column prop="cost_price" label="成本价格" width="100" />
            <el-table-column prop="selling_price" label="售卖价格" width="100" />
            <el-table-column prop="location" label="库位" width="120" />
            <el-table-column prop="supplier" label="供应商" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                  {{ scope.row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="handleEditProduct(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteProduct(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
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
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 添加/编辑商品对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="货号" prop="code">
          <el-input v-model="form.code" placeholder="请输入货号" />
        </el-form-item>
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
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
        <el-form-item label="成本价格" prop="cost_price">
          <el-input-number v-model="form.cost_price" :min="0" :step="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="售卖价格" prop="selling_price">
          <el-input-number v-model="form.selling_price" :min="0" :step="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="库位">
          <el-input v-model="form.location" placeholder="请输入库位" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="form.supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="商品图片">
          <div class="image-upload-container">
            <div
              v-if="!form.imagePreview && !form.image_url"
              class="image-uploader"
              @click="triggerImageUpload"
            >
              <el-icon class="image-uploader-icon"><Plus /></el-icon>
            </div>
            <div v-else class="image-preview">
              <el-image
                :src="form.imagePreview || form.image_url"
                style="width: 100px; height: 100px"
                fit="cover"
                :preview-src-list="[form.imagePreview || form.image_url]"
              />
              <el-button
                size="small"
                type="danger"
                @click="handleRemoveImage"
                style="margin-top: 8px"
              >
                删除图片
              </el-button>
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
        <template v-if="form.product_type === 'bead'">
          <el-form-item label="材质">
            <el-input v-model="form.material" placeholder="请输入材质" />
          </el-form-item>
          <el-form-item label="尺寸">
            <el-input v-model="form.size" placeholder="请输入尺寸" />
          </el-form-item>
          <el-form-item label="颜色">
            <el-input v-model="form.color" placeholder="请输入颜色" />
          </el-form-item>
          <el-form-item label="单颗克重">
            <el-input-number v-model="form.weight" :min="0" :step="0.01" :precision="3" />
          </el-form-item>
          <el-form-item label="品质等级(1-10)">
            <el-input-number v-model="form.quality_level" :min="1" :max="10" :step="1" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </template>

        <!-- 配件特有属性 -->
        <template v-if="form.product_type === 'accessory'">
          <el-form-item label="材质">
            <el-input v-model="form.material" placeholder="请输入材质" />
          </el-form-item>
          <el-form-item label="尺寸">
            <el-input v-model="form.size" placeholder="请输入尺寸" />
          </el-form-item>
          <el-form-item label="颜色">
            <el-input v-model="form.color" placeholder="请输入颜色" />
          </el-form-item>
        </template>

        <!-- 成品特有属性 -->
        <template v-if="form.product_type === 'finished'">
          <el-form-item label="工费">
            <el-input-number v-model="form.labor_cost" :min="0" :step="0.01" :precision="2" />
          </el-form-item>
          <el-form-item label="弹性成本">
            <el-input-number v-model="form.elastic_cost" :min="0" :step="0.01" :precision="2" />
          </el-form-item>
          <el-form-item label="串珠组成">
            <el-button type="primary" size="small" @click="handleAddBead">添加串珠</el-button>
            <el-table :data="form.beads" style="width: 100%; margin-top: 10px">
              <el-table-column prop="bead_name" label="串珠名称" />
              <el-table-column prop="quantity" label="数量">
                <template #default="scope">
                  <el-input-number v-model="scope.row.quantity" :min="1" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="scope">
                  <el-button size="small" type="danger" @click="form.beads.splice(scope.$index, 1)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>
          <el-form-item label="配件组成">
            <el-button type="primary" size="small" @click="handleAddAccessory">添加配件</el-button>
            <el-table :data="form.accessories" style="width: 100%; margin-top: 10px">
              <el-table-column prop="accessory_name" label="配件名称" />
              <el-table-column prop="quantity" label="数量">
                <template #default="scope">
                  <el-input-number v-model="scope.row.quantity" :min="1" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="scope">
                  <el-button size="small" type="danger" @click="form.accessories.splice(scope.$index, 1)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 选择串珠对话框 -->
    <el-dialog
      v-model="beadDialogVisible"
      title="选择串珠"
      width="500px"
    >
      <el-input v-model="beadSearch" placeholder="搜索串珠" style="margin-bottom: 15px" />
      <el-table :data="filteredBeads" style="width: 100%">
        <el-table-column prop="code" label="货号" width="120" />
        <el-table-column prop="name" label="串珠名称" />
        <el-table-column prop="cost_price" label="成本价格" width="100" />
        <el-table-column label="操作" width="80">
          <template #default="scope">
            <el-button size="small" type="primary" @click="handleSelectBead(scope.row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="beadDialogVisible = false">取消</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 选择配件对话框 -->
    <el-dialog
      v-model="accessoryDialogVisible"
      title="选择配件"
      width="500px"
    >
      <el-input v-model="accessorySearch" placeholder="搜索配件" style="margin-bottom: 15px" />
      <el-table :data="filteredAccessories" style="width: 100%">
        <el-table-column prop="code" label="货号" width="120" />
        <el-table-column prop="name" label="配件名称" />
        <el-table-column prop="cost_price" label="成本价格" width="100" />
        <el-table-column label="操作" width="80">
          <template #default="scope">
            <el-button size="small" type="primary" @click="handleSelectAccessory(scope.row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="accessoryDialogVisible = false">取消</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getProductTypes, getProducts, createProduct, updateProduct, deleteProduct, getProductDetail, getAccessories, getBeads } from '@/api'

// 商品类型
const productTypes = ref([])
// 商品列表
const products = ref([])
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
    acc.code.includes(accessorySearch.value) || 
    acc.name.includes(accessorySearch.value)
  )
})
// 筛选后的串珠列表
const filteredBeads = computed(() => {
  if (!beadSearch.value) {
    return beads.value
  }
  return beads.value.filter(bead => 
    bead.code.includes(beadSearch.value) || 
    bead.name.includes(beadSearch.value)
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
  cost_price: 0,
  selling_price: 0,
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
  remove_image: false
})
// 表单验证规则
const rules = {
  code: [{ required: true, message: '请输入货号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  product_type: [{ required: true, message: '请选择商品类型', trigger: 'change' }],
  cost_price: [{ required: true, message: '请输入成本价格', trigger: 'blur' }],
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
const activeTab = ref('bead')

// 获取商品类型
const fetchProductTypes = async () => {
  try {
    const response = await getProductTypes()
    productTypes.value = response.data.product_types
  } catch (error) {
    ElMessage.error('获取商品类型失败')
    console.error(error)
  }
}

// 获取商品列表
const fetchProducts = async () => {
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
  }
}

// 监听标签页切换
const handleTabChange = () => {
  pagination.currentPage = 1
  filterForm.is_active = ''
  fetchProducts()
}

// 获取配件列表
const fetchAccessories = async () => {
  try {
    const response = await getAccessories()
    accessories.value = response.data.accessories
  } catch (error) {
    ElMessage.error('获取配件列表失败')
    console.error(error)
  }
}

// 获取串珠列表
const fetchBeads = async () => {
  try {
    const response = await getBeads()
    beads.value = response.data.beads
  } catch (error) {
    ElMessage.error('获取串珠列表失败')
    console.error(error)
  }
}

// 处理筛选
const handleFilter = () => {
  pagination.currentPage = 1
  fetchProducts()
}

// 重置筛选
const resetFilter = () => {
  filterForm.is_active = ''
  pagination.currentPage = 1
  fetchProducts()
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
  Object.assign(form, {
    id: '',
    code: '',
    name: '',
    product_type: activeTab.value, // 默认使用当前标签页的商品类型
    cost_price: 0,
    selling_price: 0,
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
    remove_image: false
  })
  dialogVisible.value = true
}

// 触发图片上传
const triggerImageUpload = () => {
  // 重置输入框值，允许重复选择同一文件
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
  // 验证文件类型
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 PNG、JPEG、GIF 和 WEBP 格式的图片')
    return
  }
  
  // 验证文件大小 (最大 5MB)
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  form.image = file
  form.remove_image = false
  
  // 生成预览
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
      cost_price: product.cost_price,
      selling_price: product.selling_price,
      location: product.location,
      supplier: product.supplier,
      material: product.bead?.material || product.accessory?.material || '',
      size: product.bead?.size || product.accessory?.size || '',
      color: product.bead?.color || product.accessory?.color || '',
      weight: product.bead?.weight || 0,
      quality_level: product.bead?.quality_level || 5,
      remark: product.bead?.remark || '',
      beads: product.finished?.beads || [],
      accessories: product.finished?.accessories || [],
      labor_cost: product.finished?.labor_cost || 0,
      elastic_cost: product.finished?.elastic_cost || 0,
      image: null,
      imagePreview: '',
      image_url: product.image_url || '',
      remove_image: false
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
    try {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      fetchProducts()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
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
  // 检查是否已经添加过该串珠
  const existing = form.beads.find(item => item.bead_id === bead.id)
  if (existing) {
    ElMessage.warning('该串珠已经添加过了')
    return
  }
  form.beads.push({
    bead_id: bead.id,
    bead_code: bead.code,
    bead_name: bead.name,
    quantity: 1
  })
  beadDialogVisible.value = false
}

// 处理添加配件
const handleAddAccessory = () => {
  fetchAccessories()
  accessoryDialogVisible.value = true
}

// 处理选择配件
const handleSelectAccessory = (accessory) => {
  // 检查是否已经添加过该配件
  const existing = form.accessories.find(item => item.accessory_id === accessory.id)
  if (existing) {
    ElMessage.warning('该配件已经添加过了')
    return
  }
  form.accessories.push({
    accessory_id: accessory.id,
    accessory_code: accessory.code,
    accessory_name: accessory.name,
    quantity: 1
  })
  accessoryDialogVisible.value = false
}

// 计算成品总成本
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

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          code: form.code,
          name: form.name,
          product_type: form.product_type,
          cost_price: form.cost_price,
          selling_price: form.selling_price,
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
        } else if (form.product_type === 'accessory') {
          data.material = form.material
          data.size = form.size
          data.color = form.color
        } else if (form.product_type === 'finished') {
          data.beads = form.beads
          data.accessories = form.accessories
          data.labor_cost = form.labor_cost
          data.elastic_cost = form.elastic_cost
        }

        // 处理图片
        if (form.image) {
          data.image = form.image
        }
        if (form.id && form.remove_image) {
          data.remove_image = true
        }

        if (form.id) {
          // 编辑商品
          await updateProduct(form.id, data)
          ElMessage.success('更新成功')
        } else {
          // 添加商品
          await createProduct(data)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchProducts()
      } catch (error) {
        ElMessage.error('操作失败')
        console.error(error)
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  width: 100%;
}

.image-upload-container {
  width: 100%;
}

.image-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 100px;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-uploader:hover {
  border-color: var(--el-color-primary);
}

.image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.image-preview {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* 成品详情样式 */
.finished-details {
  padding: 20px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.finished-details h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.finished-details h5 {
  margin: 20px 0 10px 0;
  color: #606266;
  font-size: 14px;
  border-left: 3px solid #409eff;
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
  color: #606266;
}

.finished-details .total-cost {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-top: 1px solid #dcdfe6;
  margin-top: 10px;
  padding-top: 15px;
}

.finished-details .amount {
  font-weight: bold;
  color: #409eff;
}
</style>
