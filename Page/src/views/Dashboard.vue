<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF">
              <el-icon :size="30"><ShoppingCart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥128,560</div>
              <div class="stat-label">今日销售额</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" v-loading="productStatsLoading">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A">
              <el-icon :size="30"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ productStats.total_count }}</div>
              <div class="stat-label">商品总数</div>
              <div class="stat-extra">串珠 {{ productStats.bead_count }} / 配件 {{ productStats.accessory_count }} / 成品 {{ productStats.finished_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">1,234</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">856</div>
              <div class="stat-label">今日订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>销售趋势</span>
            </div>
          </template>
          <div ref="salesChartRef" style="height: 400px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>商品分类占比</span>
            </div>
          </template>
          <div ref="categoryChartRef" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getProductStats } from '@/api'

const salesChartRef = ref(null)
const categoryChartRef = ref(null)
const productStatsLoading = ref(false)
const productStats = reactive({
  total_count: 0,
  active_count: 0,
  bead_count: 0,
  accessory_count: 0,
  finished_count: 0,
  sku_count: 0
})
let salesChart = null
let categoryChart = null

const initSalesChart = () => {
  salesChart = echarts.init(salesChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额', '订单数'] },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: [
      { type: 'value', name: '销售额' },
      { type: 'value', name: '订单数' }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        data: [12000, 13200, 10100, 13400, 9000, 23000, 21000],
        smooth: true
      },
      {
        name: '订单数',
        type: 'bar',
        yAxisIndex: 1,
        data: [120, 132, 101, 134, 90, 230, 210]
      }
    ]
  }
  salesChart.setOption(option)
}

const initCategoryChart = () => {
  categoryChart = echarts.init(categoryChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '商品分类',
        type: 'pie',
        radius: '60%',
        data: [
          { value: 1048, name: '电子产品' },
          { value: 735, name: '服装鞋帽' },
          { value: 580, name: '家居用品' },
          { value: 484, name: '食品饮料' },
          { value: 300, name: '其他' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  categoryChart.setOption(option)
}

const handleResize = () => {
  salesChart && salesChart.resize()
  categoryChart && categoryChart.resize()
}

const fetchProductStats = async () => {
  productStatsLoading.value = true
  try {
    const response = await getProductStats()
    Object.assign(productStats, response.data.product_stats || {})
  } catch (error) {
    console.error('获取商品统计失败', error?.response?.data || error)
  } finally {
    productStatsLoading.value = false
  }
}

onMounted(() => {
  fetchProductStats()
  initSalesChart()
  initCategoryChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  salesChart && salesChart.dispose()
  categoryChart && categoryChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.stat-card {
  margin-bottom: 20px;
}
.stat-content {
  display: flex;
  align-items: center;
}
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 20px;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}
.stat-extra {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>