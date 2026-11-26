<template>
  <el-dialog
    v-model="dialogVisible"
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
                  {{ getOrderStatusText(currentOrderDetail.baseInfo?.status) || '-' }}
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
              <span class="detail-label">原始总价:</span>
              <span class="detail-value original-price">¥{{ currentOrderDetail.baseInfo?.sumProductPayment?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">折扣后金额:</span>
              <span class="detail-value">¥{{ ((currentOrderDetail.baseInfo?.totalAmount || 0) - (currentOrderDetail.baseInfo?.shippingFee || 0)).toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">运费:</span>
              <span class="detail-value">¥{{ currentOrderDetail.baseInfo?.shippingFee?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">订单总价:</span>
              <span class="detail-value price">¥{{ currentOrderDetail.baseInfo?.totalAmount?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">退款金额:</span>
              <span class="detail-value discount">-¥{{ currentOrderDetail.baseInfo?.refund?.toFixed(2) || '0.00' }}</span>
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
                  referrerpolicy="no-referrer"
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
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { getOrderDetail } from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  storeId: {
    type: [String, Number],
    default: null
  },
  orderId: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const orderDetailLoading = ref(false)
const currentOrderDetail = ref(null)

const loadDetail = async () => {
  if (!props.orderId || !props.storeId) {
    currentOrderDetail.value = null
    return
  }

  orderDetailLoading.value = true
  currentOrderDetail.value = null

  try {
    const res = await getOrderDetail(props.storeId, props.orderId)
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

watch(() => props.modelValue, (visible) => {
  if (visible) {
    loadDetail()
  }
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

const orderStatusMap = {
  'WAIT_BUYER_PAY': '待买家付款',
  'WAIT_SELLER_SEND_GOODS': '待卖家发货',
  'WAIT_BUYER_CONFIRM_GOODS': '待买家确认收货',
  'TRADE_BUYER_SIGNED': '买家已签收',
  'TRADE_FINISHED': '交易完成',
  'TRADE_CLOSED': '交易关闭',
  'TRADE_CLOSED_BY_TAOBAO': '交易被淘宝关闭',
  'waitbuyerreceive': '待买家收货',
  'waitbuyerpay': '待买家付款',
  'waitpay': '待付款',
  'waitsend': '待发货',
  'waitreceive': '待收货',
  'success': '交易成功',
  'closed': '交易关闭'
}

const getOrderStatusText = (status) => {
  return orderStatusMap[status] || status
}

const getOrderStatusType = (status) => {
  const statusMap = {
    'WAIT_BUYER_PAY': 'warning',
    'WAIT_SELLER_SEND_GOODS': 'primary',
    'WAIT_BUYER_CONFIRM_GOODS': 'info',
    'TRADE_BUYER_SIGNED': 'success',
    'TRADE_FINISHED': 'success',
    'TRADE_CLOSED': 'danger',
    'TRADE_CLOSED_BY_TAOBAO': 'danger',
    'waitbuyerreceive': 'info',
    'waitbuyerpayseller': 'warning',
    'waitpay': 'warning',
    'waitsend': 'primary',
    'waitreceive': 'info',
    'success': 'success',
    'closed': 'danger'
  }
  return statusMap[status] || 'info'
}
</script>

<style scoped>
.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
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
</style>
