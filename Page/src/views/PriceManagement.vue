<template>
  <div class="price-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">价格管理</span>
        </div>
      </template>
      
      <!-- 筛选区域 -->
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="商品类型">
          <el-select v-model="filterForm.product_type" placeholder="请选择商品类型" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="串珠" value="bead" />
            <el-option label="手串配件" value="accessory" />
            <el-option label="手串成品" value="finished" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="商品">
          <el-select 
            v-model="filterForm.product_id" 
            placeholder="请选择商品" 
            clearable 
            filterable 
            @change="handleProductChange"
            style="width: 300px"
          >
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="`${product.code} - ${product.name}`"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="价格类型">
          <el-select v-model="filterForm.price_type" placeholder="请选择价格类型" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="采购成本" value="purchase_cost" />
            <el-option label="成本价格" value="cost_price" />
            <el-option label="销售价格" value="selling_price" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="fetchPriceHistory">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 价格走势图表 -->
    <el-card class="chart-card" v-if="filterForm.product_id">
      <template #header>
        <div class="card-header">
          <span class="title">价格走势</span>
        </div>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>
    
    <!-- 价格历史表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span class="title">价格变更历史</span>
        </div>
      </template>
      
      <el-table
        :data="priceHistory"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="created_at" label="变更时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="product.code" label="商品货号" width="120" />
        <el-table-column prop="product.name" label="商品名称" min-width="150" />
        <el-table-column prop="product.product_type_display" label="商品类型" width="120" />
        <el-table-column prop="price_type_display" label="价格类型" width="120" />
        <el-table-column label="变更前价格" width="140">
          <template #default="{ row }">
            <span class="old-price">{{ formatPrice(row.old_value) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="变更后价格" width="140">
          <template #default="{ row }">
            <span class="new-price">{{ formatPrice(row.new_value) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="价格变化" width="120">
          <template #default="{ row }">
            <span :class="getChangeClass(row.new_value - row.old_value)">
              {{ formatChange(row.new_value - row.old_value) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="changed_by.username" label="操作人" width="120" />
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';
import { getProducts, getPriceHistory, getPriceChartData } from '@/api/store';

// 响应式数据
const chartRef = ref(null);
let chartInstance = null;

const loading = ref(false);
const products = ref([]);
const priceHistory = ref([]);
const dateRange = ref([]);

const filterForm = ref({
  product_type: '',
  product_id: null,
  price_type: '',
  start_date: '',
  end_date: ''
});

const pagination = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0
});

// 获取商品列表
const fetchProducts = async () => {
  try {
    const res = await getProducts({ page_size: 1000 });
    products.value = res.data.products;
  } catch (error) {
    ElMessage.error('获取商品列表失败');
    console.error(error);
  }
};

// 获取价格历史
const fetchPriceHistory = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.value.currentPage,
      page_size: pagination.value.pageSize
    };
    
    if (filterForm.value.product_type) {
      params.product_type = filterForm.value.product_type;
    }
    if (filterForm.value.product_id) {
      params.product_id = filterForm.value.product_id;
    }
    if (filterForm.value.price_type) {
      params.price_type = filterForm.value.price_type;
    }
    if (filterForm.value.start_date) {
      params.start_date = filterForm.value.start_date;
    }
    if (filterForm.value.end_date) {
      params.end_date = filterForm.value.end_date;
    }
    
    const res = await getPriceHistory(params);
    priceHistory.value = res.data.price_history || [];
    pagination.value.total = res.data.total_count || 0;
    
    // 如果选择了商品，同时获取图表数据
    if (filterForm.value.product_id) {
      fetchChartData();
    }
  } catch (error) {
    ElMessage.error('获取价格历史失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 获取图表数据
const fetchChartData = async () => {
  try {
    const params = { product_id: filterForm.value.product_id };
    if (filterForm.value.price_type) {
      params.price_type = filterForm.value.price_type;
    }
    
    const res = await getPriceChartData(params);
    const chartData = res.data.chart_data || { dates: [], values: [] };
    
    await nextTick();
    renderChart(chartData, res.data.price_type_display || '价格');
  } catch (error) {
    ElMessage.error('获取价格走势数据失败');
    console.error(error);
  }
};

// 渲染图表
const renderChart = (data, priceTypeLabel) => {
  if (!chartRef.value) return;
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates || []
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: priceTypeLabel,
        type: 'line',
        smooth: true,
        data: data.values || [],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        itemStyle: {
          color: '#409EFF'
        },
        lineStyle: {
          color: '#409EFF',
          width: 2
        }
      }
    ]
  };
  
  chartInstance.setOption(option);
};

// 处理筛选变化
const handleFilterChange = () => {
  pagination.value.currentPage = 1;
  fetchPriceHistory();
};

// 处理商品选择变化
const handleProductChange = () => {
  pagination.value.currentPage = 1;
  fetchPriceHistory();
};

// 处理日期范围变化
const handleDateRangeChange = (value) => {
  if (value && value.length === 2) {
    filterForm.value.start_date = value[0];
    filterForm.value.end_date = value[1];
  } else {
    filterForm.value.start_date = '';
    filterForm.value.end_date = '';
  }
  pagination.value.currentPage = 1;
  fetchPriceHistory();
};

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    product_type: '',
    product_id: null,
    price_type: '',
    start_date: '',
    end_date: ''
  };
  dateRange.value = [];
  pagination.value.currentPage = 1;
  fetchPriceHistory();
};

// 处理分页
const handleSizeChange = (size) => {
  pagination.value.pageSize = size;
  pagination.value.currentPage = 1;
  fetchPriceHistory();
};

const handlePageChange = (page) => {
  pagination.value.currentPage = page;
  fetchPriceHistory();
};

// 格式化价格
const formatPrice = (price) => {
  return `¥${parseFloat(price).toFixed(2)}`;
};

// 格式化日期时间
const formatDateTime = (datetime) => {
  if (!datetime) return '';
  const date = new Date(datetime);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 计算变化样式
const getChangeClass = (change) => {
  if (change > 0) return 'price-up';
  if (change < 0) return 'price-down';
  return '';
};

// 格式化变化值
const formatChange = (change) => {
  if (change > 0) return `+¥${change.toFixed(2)}`;
  if (change < 0) return `-¥${Math.abs(change).toFixed(2)}`;
  return '-';
};

// 窗口变化时重绘图表
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

// 生命周期
onMounted(() => {
  fetchProducts();
  fetchPriceHistory();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.price-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
}

.filter-form {
  margin-bottom: 0;
}

.chart-card {
  margin-top: 20px;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.table-card {
  margin-top: 20px;
}

.old-price {
  text-decoration: line-through;
  color: #909399;
}

.new-price {
  color: #303133;
  font-weight: bold;
}

.price-up {
  color: #F56C6C;
  font-weight: bold;
}

.price-down {
  color: #67C23A;
  font-weight: bold;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
