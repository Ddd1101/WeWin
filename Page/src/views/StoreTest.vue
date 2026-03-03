<template>
  <div class="store-test">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>店铺测试页面</span>
        </div>
      </template>
      <div class="content">
        <el-form :model="testForm" label-width="120px" style="max-width: 800px;">
          <el-form-item label="选择店铺">
            <el-select v-model="testForm.storeId" placeholder="请选择要测试的店铺" style="width: 100%;" @change="handleStoreChange">
              <el-option 
                v-for="store in stores" 
                :key="store.id" 
                :label="store.name + ' (' + store.platform_display + ')'" 
                :value="store.id" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="testForm.startTime"
              type="datetime"
              placeholder="选择开始时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%;"
            />
          </el-form-item>
          
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="testForm.endTime"
              type="datetime"
              placeholder="选择结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%;"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleTest" :loading="testing">
              执行测试
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="response" class="response-section">
          <div class="response-header">
            <span>请求链接</span>
          </div>
          <div v-if="response.request_logs && response.request_logs.length > 0" class="request-logs">
            <el-collapse v-model="activeRequestLogs">
              <el-collapse-item 
                v-for="(log, index) in response.request_logs" 
                :key="index"
                :name="index"
              >
                <template #title>
                  <span class="request-title">
                  请求 {{ index + 1 }}: {{ log.url }}</span>
                </template>
                <div class="request-detail">
                  <div class="request-info">
                    <span><span class="label">方法:</span> {{ log.method }}</span>
                    <span v-if="log.status_code"><span class="label">状态码:</span> {{ log.status_code }}</span>
                  </div>
                  <div class="request-params">
                    <div class="label">请求参数:</div>
                    <pre class="json-display">{{ JSON.stringify(log.params, null, 2) }}</pre>
                  </div>
                  <div v-if="log.response" class="request-response">
                    <div class="label">响应结果:</div>
                    <pre class="json-display">{{ JSON.stringify(log.response, null, 2) }}</pre>
                  </div>
                  <div v-if="log.error" class="request-error">
                    <div class="label">错误信息:</div>
                    <pre class="json-display">{{ log.error }}</pre>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
          <div v-else class="no-request-logs">
            <el-empty description="暂无请求日志" />
          </div>
        </div>
        
        <div v-if="allOrders.length > 0" class="response-section">
          <div class="response-header">
            <span>订单可视化 ({{ allOrders.length }} 个订单)</span>
          </div>
          <div class="orders-list">
            <el-card v-for="(order, orderIndex) in allOrders" :key="orderIndex" class="order-card">
              <template #header>
                <div class="order-header">
                  <span class="order-id clickable" @click="handleOrderClick(order)">订单号: {{ order.baseInfo?.idOfStr || order.baseInfo?.id || '-' }}</span>
                  <el-tag :type="getOrderStatusType(order.baseInfo?.status)">{{ order.baseInfo?.status || '-' }}</el-tag>
                </div>
              </template>
              <div class="order-content">
                <!-- 买家信息 -->
                <div v-if="order.baseInfo?.buyerContact" class="order-section">
                  <div class="section-title">买家信息</div>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">买家账号:</span>
                      <span class="info-value">{{ order.baseInfo?.buyerLoginId || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">买家姓名:</span>
                      <span class="info-value">{{ order.baseInfo.buyerContact.name || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">公司名称:</span>
                      <span class="info-value">{{ order.baseInfo.buyerContact.companyName || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">电话:</span>
                      <span class="info-value">{{ order.baseInfo.buyerContact.phone || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">手机:</span>
                      <span class="info-value">{{ order.baseInfo.buyerContact.mobile || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">旺旺:</span>
                      <span class="info-value">{{ order.baseInfo.buyerContact.imInPlatform || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- 收货信息 (receiverInfo) -->
                <div v-if="order.baseInfo?.receiverInfo" class="order-section">
                  <div class="section-title">收货信息</div>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">收货人:</span>
                      <span class="info-value">{{ order.baseInfo.receiverInfo.toFullName || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">电话:</span>
                      <span class="info-value">{{ order.baseInfo.receiverInfo.toPhone || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">手机:</span>
                      <span class="info-value">{{ order.baseInfo.receiverInfo.toMobile || '-' }}</span>
                    </div>
                    <div class="info-item full-width">
                      <span class="info-label">地址:</span>
                      <span class="info-value">{{ order.baseInfo.receiverInfo.toArea || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- 收货信息 (receiveAddressInfo - 兼容旧格式) -->
                <div v-else-if="order.baseInfo?.receiveAddressInfo" class="order-section">
                  <div class="section-title">收货信息</div>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">收货人:</span>
                      <span class="info-value">{{ order.baseInfo.receiveAddressInfo.fullName || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">电话:</span>
                      <span class="info-value">{{ order.baseInfo.receiveAddressInfo.phone || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">手机:</span>
                      <span class="info-value">{{ order.baseInfo.receiveAddressInfo.mobile || '-' }}</span>
                    </div>
                    <div class="info-item full-width">
                      <span class="info-label">地址:</span>
                      <span class="info-value">
                        {{ order.baseInfo.receiveAddressInfo.province || '' }}
                        {{ order.baseInfo.receiveAddressInfo.city || '' }}
                        {{ order.baseInfo.receiveAddressInfo.area || '' }}
                        {{ order.baseInfo.receiveAddressInfo.address || '' }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 基本信息 -->
                <div class="order-section">
                  <div class="section-title">基本信息</div>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">买家:</span>
                      <span class="info-value">{{ order.baseInfo?.buyerLoginId || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">创建时间:</span>
                      <span class="info-value">{{ formatTime(order.baseInfo?.createTime) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">付款时间:</span>
                      <span class="info-value">{{ formatTime(order.baseInfo?.payTime) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">折扣前金额:</span>
                      <span class="info-value original-price">¥{{ ((order.baseInfo?.totalAmount || 0) + (order.baseInfo?.discount || 0)).toFixed(2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">折扣金额:</span>
                      <span class="info-value discount-price">-¥{{ (order.baseInfo?.discount || 0).toFixed(2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">订单金额:</span>
                      <span class="info-value price">¥{{ order.baseInfo?.totalAmount?.toFixed(2) || '0.00' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">商品金额:</span>
                      <span class="info-value">¥{{ order.baseInfo?.sumProductPayment?.toFixed(2) || '0.00' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">运费:</span>
                      <span class="info-value">¥{{ order.baseInfo?.shippingFee?.toFixed(2) || '0.00' }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="order.productItems && order.productItems.length > 0" class="order-section">
                  <div class="section-title">商品列表 ({{ order.productItems.length }})</div>
                  <div class="product-list">
                    <div v-for="(item, itemIndex) in order.productItems" :key="itemIndex" class="product-item">
                      <div v-if="item.productImgUrl && item.productImgUrl.length > 0" class="product-image">
                        <el-image 
                          :src="item.productImgUrl[0]" 
                          :preview-src-list="item.productImgUrl"
                          fit="cover"
                          class="product-img"
                        >
                          <template #error>
                            <div class="image-error">
                              <el-icon><Picture /></el-icon>
                            </div>
                          </template>
                        </el-image>
                      </div>
                      <div class="product-info">
                        <a 
                          v-if="item.productSnapshotUrl" 
                          :href="item.productSnapshotUrl" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          class="product-name-link"
                        >
                          <div class="product-name">{{ item.name || '-' }}</div>
                        </a>
                        <div v-else class="product-name">{{ item.name || '-' }}</div>
                        <div class="product-sku" v-if="item.skuInfos && item.skuInfos.length > 0">
                          规格: {{ item.skuInfos.join(' / ') }}
                        </div>
                        <div class="product-meta">
                          <span>单价: ¥{{ item.price?.toFixed(2) || '0.00' }}</span>
                          <span>数量: {{ item.quantity || 0 }}</span>
                          <span>小计: ¥{{ item.itemAmount?.toFixed(2) || '0.00' }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </div>
        
        <div v-if="response" class="response-section">
          <div class="response-header">
            <span>响应结果</span>
          </div>
          <pre class="json-display">{{ JSON.stringify(response, null, 2) }}</pre>
        </div>
      </div>
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="orderDetailDialogVisible"
      title="订单详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-loading="orderDetailLoading" class="order-detail-content">
        <div v-if="currentOrderDetail" class="order-detail-wrapper">
          <!-- 买家信息 -->
          <div v-if="currentOrderDetail.baseInfo?.buyerContact" class="detail-section">
            <div class="section-title">买家信息</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">买家账号:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo?.buyerLoginId || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">买家姓名:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.buyerContact.name || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">公司名称:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.buyerContact.companyName || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">电话:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.buyerContact.phone || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">手机:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.buyerContact.mobile || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">旺旺:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.buyerContact.imInPlatform || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 收货信息 (receiverInfo) -->
          <div v-if="currentOrderDetail.baseInfo?.receiverInfo" class="detail-section">
            <div class="section-title">收货信息</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">收货人:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiverInfo.toFullName || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">电话:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiverInfo.toPhone || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">手机:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiverInfo.toMobile || '-' }}</span>
              </div>
              <div class="detail-item full-width">
                <span class="detail-label">地址:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiverInfo.toArea || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 收货信息 (receiveAddressInfo - 兼容旧格式) -->
          <div v-else-if="currentOrderDetail.baseInfo?.receiveAddressInfo" class="detail-section">
            <div class="section-title">收货信息</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">收货人:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiveAddressInfo.fullName || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">电话:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiveAddressInfo.phone || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">手机:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiveAddressInfo.mobile || '-' }}</span>
              </div>
              <div class="detail-item full-width">
                <span class="detail-label">地址:</span>
                <span class="detail-value">
                  {{ currentOrderDetail.baseInfo.receiveAddressInfo.province || '' }}
                  {{ currentOrderDetail.baseInfo.receiveAddressInfo.city || '' }}
                  {{ currentOrderDetail.baseInfo.receiveAddressInfo.area || '' }}
                  {{ currentOrderDetail.baseInfo.receiveAddressInfo.address || '' }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">邮编:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo.receiveAddressInfo.zip || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 基本信息 -->
          <div class="detail-section">
            <div class="section-title">基本信息</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">订单ID:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo?.id || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">订单号:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo?.idOfStr || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">订单状态:</span>
                <span class="detail-value">
                  <el-tag :type="getOrderStatusType(currentOrderDetail.baseInfo?.status)">
                    {{ currentOrderDetail.baseInfo?.status || '-' }}
                  </el-tag>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">退款状态:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo?.refundStatus || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">买家:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo?.buyerLoginId || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">卖家:</span>
                <span class="detail-value">{{ currentOrderDetail.baseInfo?.sellerLoginId || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间:</span>
                <span class="detail-value">{{ formatTime(currentOrderDetail.baseInfo?.createTime) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">付款时间:</span>
                <span class="detail-value">{{ formatTime(currentOrderDetail.baseInfo?.payTime) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">订单金额:</span>
                <span class="detail-value price">¥{{ currentOrderDetail.baseInfo?.totalAmount?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">商品金额:</span>
                <span class="detail-value">¥{{ currentOrderDetail.baseInfo?.sumProductPayment?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">运费:</span>
                <span class="detail-value">¥{{ currentOrderDetail.baseInfo?.shippingFee?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">折扣:</span>
                <span class="detail-value discount">-¥{{ currentOrderDetail.baseInfo?.discount?.toFixed(2) || '0.00' }}</span>
              </div>
            </div>
          </div>

          <!-- 商品列表 -->
          <div v-if="currentOrderDetail.productItems && currentOrderDetail.productItems.length > 0" class="detail-section">
            <div class="section-title">商品列表 ({{ currentOrderDetail.productItems.length }})</div>
            <div class="product-detail-list">
              <div v-for="(item, index) in currentOrderDetail.productItems" :key="index" class="product-detail-item">
                <div v-if="item.productImgUrl && item.productImgUrl.length > 0" class="product-detail-image">
                  <el-image 
                    :src="item.productImgUrl[0]" 
                    :preview-src-list="item.productImgUrl"
                    fit="cover"
                    class="product-detail-img"
                  >
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                </div>
                <div class="product-detail-info">
                  <div class="product-detail-name">{{ item.name || '-' }}</div>
                  <div v-if="item.skuInfos && item.skuInfos.length > 0" class="product-detail-sku">
                    规格: {{ item.skuInfos.map(s => s.name + ':' + s.value).join(' / ') }}
                  </div>
                  <div class="product-detail-meta">
                    <span>单价: ¥{{ item.price?.toFixed(2) || '0.00' }}</span>
                    <span>数量: {{ item.quantity || 0 }}</span>
                    <span>小计: ¥{{ item.itemAmount?.toFixed(2) || '0.00' }}</span>
                  </div>
                  <div v-if="item.productCargoNumber || item.cargoNumber" class="product-detail-cargo">
                    货号: {{ item.productCargoNumber || item.cargoNumber }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 物流信息 -->
          <div v-if="currentOrderDetail.nativeLogistics" class="detail-section">
            <div class="section-title">物流信息</div>
            <div class="logistics-detail-info">
              <div class="detail-item">
                <span class="detail-label">物流公司:</span>
                <span class="detail-value">{{ currentOrderDetail.nativeLogistics.logisticsCompanyName || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">物流单号:</span>
                <span class="detail-value">{{ currentOrderDetail.nativeLogistics.logisticsBillNo || '-' }}</span>
              </div>
              <div v-if="currentOrderDetail.nativeLogistics.logisticsItems && currentOrderDetail.nativeLogistics.logisticsItems.length > 0" class="logistics-items">
                <div v-for="(logisticsItem, idx) in currentOrderDetail.nativeLogistics.logisticsItems" :key="idx" class="logistics-item">
                  <div class="detail-item">
                    <span class="detail-label">物流状态:</span>
                    <span class="detail-value">{{ logisticsItem.status || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">发货时间:</span>
                    <span class="detail-value">{{ formatTime(logisticsItem.deliveredTime) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 原始数据 -->
          <div class="detail-section">
            <div class="section-title">原始数据</div>
            <pre class="json-display">{{ JSON.stringify(currentOrderDetail, null, 2) }}</pre>
          </div>
        </div>
        <div v-else-if="!orderDetailLoading" class="no-detail">
          <el-empty description="暂无订单详情" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { getStores, triggerDataPull, getOrderDetail } from '../api'

const stores = ref([])
const testing = ref(false)
const response = ref(null)
const activeRequestLogs = ref([])

const orderDetailDialogVisible = ref(false)
const orderDetailLoading = ref(false)
const currentOrderDetail = ref(null)
const currentOrderId = ref('')

const allOrders = computed(() => {
  if (!response.value || !response.value.request_logs) {
    return []
  }
  
  const orders = []
  response.value.request_logs.forEach(log => {
    if (log.response && log.response.result) {
      orders.push(...log.response.result)
    }
  })
  
  return orders
})

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const year = timeStr.substring(0, 4)
    const month = timeStr.substring(4, 6)
    const day = timeStr.substring(6, 8)
    const hour = timeStr.substring(8, 10)
    const minute = timeStr.substring(10, 12)
    const second = timeStr.substring(12, 14)
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  } catch (e) {
    return timeStr
  }
}

const getOrderStatusType = (status) => {
  const statusMap = {
    'WAIT_BUYER_PAY': 'warning',
    'WAIT_SELLER_SEND_GOODS': 'primary',
    'WAIT_BUYER_CONFIRM_GOODS': 'info',
    'TRADE_BUYER_SIGNED': 'success',
    'TRADE_FINISHED': 'success',
    'TRADE_CLOSED': 'danger',
    'TRADE_CLOSED_BY_TAOBAO': 'danger'
  }
  return statusMap[status] || 'info'
}

const handleOrderClick = async (order) => {
  const platformOrderId = order.baseInfo?.id || order.baseInfo?.idOfStr
  if (!platformOrderId || !testForm.value.storeId) {
    ElMessage.warning('无法获取订单ID')
    return
  }
  
  currentOrderId.value = platformOrderId
  orderDetailDialogVisible.value = true
  orderDetailLoading.value = true
  currentOrderDetail.value = null
  
  try {
    const res = await getOrderDetail(testForm.value.storeId, platformOrderId)
    if (res.data.success) {
      currentOrderDetail.value = res.data.order_detail
      ElMessage.success('获取订单详情成功')
    } else {
      ElMessage.error(res.data.error || '获取订单详情失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '获取订单详情失败')
  } finally {
    orderDetailLoading.value = false
  }
}

const testForm = ref({
  storeId: null,
  startTime: null,
  endTime: null
})

const fetchStores = async () => {
  try {
    const res = await getStores()
    stores.value = res.data.stores
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '获取店铺列表失败')
  }
}

const handleStoreChange = (storeId) => {
  const store = stores.value.find(s => s.id === storeId)
  if (store) {
    console.log('选择的店铺:', store)
  }
}

const handleTest = async () => {
  if (!testForm.value.storeId) {
    ElMessage.warning('请选择要测试的店铺')
    return
  }
  if (!testForm.value.startTime || !testForm.value.endTime) {
    ElMessage.warning('请选择开始时间和结束时间')
    return
  }

  testing.value = true
  response.value = null
  
  try {
    const res = await triggerDataPull(testForm.value.storeId, {
      start_time: testForm.value.startTime,
      end_time: testForm.value.endTime
    })
    response.value = res.data
    ElMessage.success('测试执行成功')
  } catch (error) {
    response.value = error.response?.data || { error: '测试执行失败' }
    ElMessage.error(error.response?.data?.error || '测试执行失败')
  } finally {
    testing.value = false
  }
}

const resetForm = () => {
  testForm.value = {
    storeId: null,
    startTime: null,
    endTime: null
  }
  response.value = null
}

onMounted(() => {
  fetchStores()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content {
  padding: 20px;
}

.response-section {
  margin-top: 30px;
  border-top: 1px solid #e6e6e6;
  padding-top: 20px;
}

.response-header {
  font-weight: 600;
  margin-bottom: 15px;
  color: #303133;
}

.request-logs {
  margin-bottom: 20px;
}

.request-title {
  font-weight: 500;
  color: #409eff;
}

.request-detail {
  padding: 15px;
  background-color: #fafafa;
  border-radius: 4px;
}

.request-info {
  margin-bottom: 15px;
  display: flex;
  gap: 20px;
}

.request-info .label {
  font-weight: 600;
  color: #606266;
  margin-right: 5px;
}

.request-params,
.request-response,
.request-error {
  margin-bottom: 15px;
}

.request-params .label,
.request-response .label,
.request-error .label {
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  display: block;
}

.json-display {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  margin: 0;
}

.no-request-logs {
  padding: 40px 0;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-card {
  border: 1px solid #e0e0e0;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-id {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.order-content {
  padding: 10px 0;
}

.order-section {
  margin-bottom: 20px;
}

.order-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 20px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-weight: 500;
  color: #909399;
  margin-right: 8px;
  white-space: nowrap;
}

.info-value {
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 16px;
}

.info-value.original-price {
  color: #909399;
  text-decoration: line-through;
  font-size: 14px;
}

.info-value.discount-price {
  color: #e6a23c;
  font-weight: 600;
  font-size: 14px;
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-item {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  gap: 15px;
}

.product-image {
  flex-shrink: 0;
}

.product-img {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #e0e0e0;
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  background-color: #f5f7fa;
  color: #909399;
  border-radius: 4px;
  border: 1px dashed #e0e0e0;
}

.image-error .el-icon {
  font-size: 32px;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.product-name-link {
  text-decoration: none;
  display: block;
}

.product-name-link:hover .product-name {
  color: #409eff;
  text-decoration: underline;
}

.product-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s;
}

.product-sku {
  font-size: 13px;
  color: #909399;
}

.product-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #606266;
  margin-top: 8px;
}

.receiver-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
}

/* 订单详情弹窗样式 */
.order-detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

.order-detail-wrapper {
  padding: 10px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px 20px;
}

.detail-item {
  display: flex;
  align-items: center;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-weight: 500;
  color: #909399;
  margin-right: 8px;
  white-space: nowrap;
}

.detail-value {
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail-value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 16px;
}

.detail-value.discount {
  color: #e6a23c;
  font-weight: 600;
}

.product-detail-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-detail-item {
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  gap: 16px;
}

.product-detail-image {
  flex-shrink: 0;
}

.product-detail-img {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.product-detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.product-detail-name {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.product-detail-sku {
  font-size: 13px;
  color: #909399;
}

.product-detail-meta {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #606266;
}

.product-detail-cargo {
  font-size: 13px;
  color: #409eff;
}

.receiver-detail-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 20px;
}

.logistics-detail-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 20px;
}

.logistics-items {
  width: 100%;
  margin-top: 12px;
}

.logistics-item {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.no-detail {
  padding: 40px 0;
}

.order-id.clickable {
  cursor: pointer;
  color: #409eff;
  text-decoration: underline;
}

.order-id.clickable:hover {
  color: #66b1ff;
}
</style>
