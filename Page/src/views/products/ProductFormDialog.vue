<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    :width="isMobile ? '95%' : '780px'"
    class="product-dialog"
    @close="handleClose"
    :close-on-click-modal="false"
    :fullscreen="isMobile"
  >
    <el-form :model="form" :rules="rules" ref="formRef" :label-width="isMobile ? '80px' : '110px'">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12">
          <el-form-item label="货号" prop="code">
            <el-input v-model="form.code" placeholder="请输入货号" clearable />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item label="商品名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入商品名称" clearable />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12">
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
        <el-col :xs="24" :sm="12">
          <el-form-item label="状态" prop="is_active">
            <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <!-- SKU商品的采购/成本在SKU中维护 -->
        <el-col v-if="false && form.product_type === 'bead'" :span="12">
          <el-form-item label="采购成本(元/克)" prop="purchase_cost">
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
        <el-col v-if="form.product_type === 'finished'" :xs="24" :sm="12">
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
        <el-col v-if="form.product_type === 'finished'" :xs="24" :sm="12">
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
          <el-col :xs="24" :sm="12">
            <el-form-item label="工费">
              <el-input-number v-model="form.labor_cost" :min="0" :step="0.01" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="弹性成本">
              <el-input-number v-model="form.elastic_cost" :min="0" :step="0.01" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
      
      <el-row v-if="form.product_type === 'finished'" :gutter="20">
        <el-col :xs="24" :sm="12">
          <el-form-item label="库位">
            <el-input v-model="form.location" placeholder="请输入库位" clearable />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item label="供应商">
            <el-input v-model="form.supplier" placeholder="请输入供应商" clearable />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 童装特有字段 -->
      <el-row v-if="form.product_type === 'children_clothing'" :gutter="20">
        <el-col :xs="24" :sm="12">
          <el-form-item label="面料">
            <el-input v-model="form.fabric" placeholder="请输入面料" clearable />
          </el-form-item>
          <el-form-item label="尺码">
            <el-input v-model="form.size" placeholder="如 90/100/110 或 S/M/L" clearable />
          </el-form-item>
          <el-form-item label="颜色">
            <el-input v-model="form.color" placeholder="请输入颜色" clearable />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item label="季节">
            <el-select v-model="form.season" placeholder="选择季节" clearable style="width: 100%">
              <el-option label="春" value="spring" />
              <el-option label="夏" value="summer" />
              <el-option label="秋" value="autumn" />
              <el-option label="冬" value="winter" />
            </el-select>
          </el-form-item>
          <el-form-item label="性别">
            <el-select v-model="form.gender" placeholder="选择性别" clearable style="width: 100%">
              <el-option label="男童" value="boy" />
              <el-option label="女童" value="girl" />
              <el-option label="中性" value="unisex" />
            </el-select>
          </el-form-item>
          <el-form-item label="年龄段">
            <el-input v-model="form.age_range" placeholder="如 中童(4-6岁)" clearable />
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
          <div class="sku-card-header">
            <div class="sku-title">
              <span>SKU {{ index + 1 }}</span>
              <el-tag v-if="sku.is_default" type="success" size="small">默认</el-tag>
            </div>
            <div class="sku-actions">
              <el-button size="small" :type="sku.is_default ? 'success' : 'default'" @click="setDefaultSku(index)">
                设为默认
              </el-button>
              <el-button size="small" type="danger" plain @click="removeSku(index)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>

          <div class="sku-grid">
            <div class="sku-field span-2">
              <label>SKU编码</label>
              <el-input v-model="sku.sku_code" placeholder="如：PJ001-4MM-A" clearable />
            </div>
            <div class="sku-field span-2">
              <label>SKU名称</label>
              <el-input v-model="sku.sku_name" placeholder="如：4mm A级 / 银色小配件" clearable />
            </div>
            <div class="sku-field">
              <label>规格(mm)</label>
              <el-input-number v-model="sku.size" :min="0" :precision="0" controls-position="right" style="width:100%" />
            </div>
            <div class="sku-field">
              <label>品质等级</label>
              <el-input-number v-model="sku.quality_level" :min="1" :max="10" :precision="0" controls-position="right" style="width:100%" />
            </div>

            <div v-if="form.product_type === 'bead'" class="sku-field">
              <label>采购成本(元/克)</label>
              <el-input-number v-model="sku.purchase_cost" :min="0" :precision="2" controls-position="right" style="width:100%" />
            </div>
            <div class="sku-field">
              <label>{{ form.product_type === 'bead' ? '单颗成本(自动)' : '单件成本' }}</label>
              <el-input-number
                v-model="sku.cost_price"
                :min="0"
                :precision="2"
                controls-position="right"
                :disabled="form.product_type === 'bead'"
                style="width:100%"
              />
            </div>
            <div class="sku-field" v-if="form.product_type === 'bead'">
              <label>单颗克重(g)</label>
              <el-input-number v-model="sku.weight" :min="0" :precision="2" controls-position="right" style="width:100%" />
            </div>
            <div class="sku-field">
              <label>售卖价格</label>
              <el-input-number v-model="sku.selling_price" :min="0" :precision="2" controls-position="right" style="width:100%" />
            </div>

            <div class="sku-field">
              <label>材质</label>
              <el-input v-model="sku.material" placeholder="材质" clearable />
            </div>
            <div class="sku-field">
              <label>颜色</label>
              <el-input v-model="sku.color" placeholder="颜色" clearable />
            </div>
            <div class="sku-field">
              <label>库位</label>
              <el-input v-model="sku.location" placeholder="库位" clearable />
            </div>
            <div class="sku-field">
              <label>供应商</label>
              <el-input v-model="sku.supplier" placeholder="供应商" clearable />
            </div>

            <div class="sku-field span-full">
              <label>备注</label>
              <el-input v-model="sku.remark" type="textarea" :rows="2" placeholder="填写该SKU的特殊说明" />
            </div>
          </div>
        </div>
      </template>

      <!-- 成品组成 -->
      <FinishedComposition v-if="form.product_type === 'finished'" :form="form" :is-mobile="isMobile" />
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
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getProductTypes, createProduct, updateProduct } from '@/api'
import FinishedComposition from './FinishedComposition.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  productType: {
    type: String,
    default: ''
  },
  editData: {
    type: Object,
    default: null
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogTitle = computed(() => (props.editData ? '编辑商品' : '添加商品'))

// 商品类型
const productTypes = ref([])
const submitLoading = ref(false)
const formRef = ref(null)
const imageInputRef = ref(null)

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
  fabric: '',
  age_range: '',
  season: '',
  gender: '',
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

// 重置表单
const resetFormFields = () => {
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
    fabric: '',
    age_range: '',
    season: '',
    gender: '',
    image: null,
    imagePreview: '',
    image_url: '',
    remove_image: false,
    skus: []
  })
}

const initForm = () => {
  if (props.editData) {
    const product = props.editData
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
      size: product.bead?.size || product.accessory?.size || product.children_clothing?.size || '',
      color: product.bead?.color || product.accessory?.color || product.children_clothing?.color || '',
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
      fabric: product.children_clothing?.fabric || '',
      season: product.children_clothing?.season || '',
      gender: product.children_clothing?.gender || '',
      age_range: product.children_clothing?.age_range || '',
      image: null,
      imagePreview: '',
      image_url: product.image_url || '',
      remove_image: false,
      skus: (product.skus || []).map(sku => ({ ...sku, sku_name: sku.sku_name || sku.name }))
    })
  } else {
    resetFormFields()
    form.product_type = props.productType
    form.is_active = true
  }
}

watch(() => props.modelValue, (visible) => {
  if (visible) {
    initForm()
  }
})

const handleClose = () => {
  resetFormFields()
  formRef.value?.resetFields()
}

// 计算单颗成本
const calculateCostPrice = () => {
  if (form.product_type === 'bead') {
    const purchaseCost = Number(form.purchase_cost) || 0
    const weight = Number(form.weight) || 0
    form.cost_price = purchaseCost * weight
  }
}

// 串珠 SKU 单颗成本 = 采购成本(元/克) × 单颗克重
watch(
  () => form.skus,
  (skus) => {
    if (form.product_type !== 'bead') return
    skus.forEach((sku) => {
      const purchaseCost = Number(sku.purchase_cost) || 0
      const weight = Number(sku.weight) || 0
      sku.cost_price = Number((purchaseCost * weight).toFixed(2))
    })
  },
  { deep: true, immediate: true }
)

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
  
  if (file.size > 100 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 100MB')
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
        } else if (form.product_type === 'children_clothing') {
          data.fabric = form.fabric
          data.size = form.size
          data.color = form.color
          data.season = form.season
          data.gender = form.gender
          data.age_range = form.age_range
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
        emit('saved')
      } catch (error) {
        ElMessage.error(error?.response?.data?.error || '操作失败')
        console.error(error?.response?.data || error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchProductTypes()
})
</script>

<style scoped>
/* 对话框样式 */
.product-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.product-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
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
  border-color: #3b82f6;
  background: #eff6ff;
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

.sku-card {
  border: 1px solid #dbe4f0;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

.sku-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  margin-bottom: 14px;
  border-bottom: 1px dashed #cbd5e1;
}

.sku-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #334155;
}

.sku-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.sku-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px 16px;
}

.sku-field {
  min-width: 0;
}

.sku-field label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  line-height: 1;
}

.sku-field.span-2 {
  grid-column: span 2;
}

.sku-field.span-full {
  grid-column: 1 / -1;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .product-dialog :deep(.el-dialog__body) {
    padding: 12px;
    max-height: 80vh;
  }

  .sku-grid {
    grid-template-columns: 1fr;
  }

  .sku-field.span-2 {
    grid-column: 1;
  }
}

@media (max-width: 900px) and (min-width: 769px) {
  .sku-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .sku-field.span-2 {
    grid-column: 1 / -1;
  }
}
</style>
