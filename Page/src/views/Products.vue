<template>
  <div class="products">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="handleAddProduct">添加商品</el-button>
        </div>
      </template>
      
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="商品类型">
            <el-select v-model="filterForm.product_type" placeholder="选择商品类型">
              <el-option label="全部" value="" />
              <el-option 
                v-for="type in productTypes" 
                :key="type.value" 
                :label="type.label" 
                :value="type.value" 
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.is_active" placeholder="选择状态">
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
      
      <el-table :data="products" style="width: 100%">
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
          <el-select v-model="form.product_type" placeholder="选择商品类型">
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
  beads: [],
  accessories: []
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
// 配件搜索
const accessorySearch = ref('')
// 串珠搜索
const beadSearch = ref('')

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
    if (filterForm.product_type) {
      params.product_type = filterForm.product_type
    }
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
  filterForm.product_type = ''
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
    product_type: '',
    cost_price: 0,
    selling_price: 0,
    location: '',
    supplier: '',
    material: '',
    size: '',
    color: '',
    beads: [],
    accessories: []
  })
  dialogVisible.value = true
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
      beads: product.finished?.beads || [],
      accessories: product.finished?.accessories || []
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
        } else if (form.product_type === 'accessory') {
          data.material = form.material
          data.size = form.size
          data.color = form.color
        } else if (form.product_type === 'finished') {
          data.beads = form.beads
          data.accessories = form.accessories
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
  display: flex;
  justify-content: flex-end;
}
</style>