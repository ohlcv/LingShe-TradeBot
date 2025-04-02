<template>
  <div class="dashboard">
    <Row :gutter="16" style="margin-top: 16px">
      <!-- 统计卡片 -->
      <Col :span="8" v-for="(card, index) in statCards" :key="index">
        <Card class="stat-card" :loading="loading">
          <template #title>
            <div class="card-title">
              <component :is="card.icon" class="card-icon" />
              <span>{{ card.title }}</span>
            </div>
          </template>
          <div class="card-content">
            <div class="card-value">{{ card.value }}</div>
            <div class="card-change" :class="{ 'up': card.change > 0, 'down': card.change < 0 }">
              <ArrowUpOutlined v-if="card.change > 0" />
              <ArrowDownOutlined v-if="card.change < 0" />
              <span v-if="card.change !== 0">{{ Math.abs(card.change) }}%</span>
              <span v-else>-</span>
            </div>
          </div>
        </Card>
      </Col>
    </Row>

    <!-- 资产分布图表 (单独一行) -->
    <Row style="margin-top: 16px">
      <Col :span="24">
        <Card :loading="loading">
          <template #title>
            <div class="card-header">
              <span>资产分布</span>
            </div>
          </template>
          <div ref="assetChartRef" class="chart-container"></div>
        </Card>
      </Col>
    </Row>

    <!-- 时间选择控件 (在图表上方) -->
    <Row style="margin-top: 16px">
      <Col :span="24">
        <Card :bordered="false" :body-style="{padding: '12px'}">
          <div class="date-control-panel">
            <Radio.Group v-model:value="dateRange" @change="handleDateRangeChange" size="small">
              <Radio.Button value="day">今日</Radio.Button>
              <Radio.Button value="week">本周</Radio.Button>
              <Radio.Button value="month">本月</Radio.Button>
              <Radio.Button value="year">今年</Radio.Button>
            </Radio.Group>
            <DatePicker.RangePicker 
              v-model:value="customDateRange" 
              @change="handleCustomDateChange"
              :disabledDate="disabledDate"
              format="YYYY-MM-DD"
              :allowClear="false"
              size="small"
              style="width: 240px"
            />
          </div>
        </Card>
      </Col>
    </Row>

    <!-- 收益曲线和资金曲线图表 (同一行) -->
    <Row :gutter="16" style="margin-top: 16px">
      <!-- 收益曲线图表 -->
      <Col :span="12">
        <Card :loading="loading">
          <template #title>
            <div class="card-header">
              <span>收益曲线</span>
            </div>
          </template>
          <div ref="profitChartRef" class="chart-container"></div>
        </Card>
      </Col>
      
      <!-- 资金曲线图表 -->
      <Col :span="12">
        <Card :loading="loading">
          <template #title>
            <div class="card-header">
              <span>资金曲线</span>
            </div>
          </template>
          <div ref="capitalChartRef" class="chart-container"></div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { DollarOutlined, AreaChartOutlined, LineChartOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons-vue';
import * as echarts from 'echarts/core';
import { PieChart, LineChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent, GridComponent, TitleComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import {
  Row,
  Col,
  Card,
  Radio,
  DatePicker
} from 'ant-design-vue';
import type { RadioChangeEvent } from 'ant-design-vue';

// 注册 ECharts 组件
echarts.use([PieChart, LineChart, TooltipComponent, LegendComponent, GridComponent, TitleComponent, CanvasRenderer]);

// 图表引用
const assetChartRef = ref<HTMLElement>();
const profitChartRef = ref<HTMLElement>();
const capitalChartRef = ref<HTMLElement>();

// 加载状态
const loading = ref(true);

// 日期范围选择
const dateRange = ref<string>('week');
const customDateRange = ref<[Dayjs, Dayjs]>([dayjs().subtract(7, 'day'), dayjs()]);

// 统计卡片数据
const statCards = reactive([
  { 
    title: '总资产', 
    value: '12,345.67 USDT', 
    change: 2.5, 
    icon: DollarOutlined 
  },
  { 
    title: '当期收益', 
    value: '123.45 USDT', 
    change: 1.2, 
    icon: AreaChartOutlined 
  },
  { 
    title: '累计收益', 
    value: '1,234.56 USDT', 
    change: 5.8, 
    icon: LineChartOutlined 
  }
]);

// 禁用日期选择
const disabledDate = (current: Dayjs) => {
  return current && current > dayjs().endOf('day');
};

// 处理日期范围变化
const handleDateRangeChange = (e: RadioChangeEvent) => {
  const value = e.target.value;
  
  if (value === 'custom') return;
  
  let startDate: Dayjs;
  const endDate = dayjs();
  
  switch (value) {
    case 'day':
      startDate = dayjs().startOf('day');
      break;
    case 'week':
      startDate = dayjs().subtract(7, 'day');
      break;
    case 'month':
      startDate = dayjs().subtract(30, 'day');
      break;
    case 'year':
      startDate = dayjs().subtract(365, 'day');
      break;
    default:
      startDate = dayjs().subtract(7, 'day');
  }
  
  customDateRange.value = [startDate, endDate];
  fetchData(startDate, endDate);
};

// 处理自定义日期变化
const handleCustomDateChange = (dates: [Dayjs, Dayjs] | [string, string], dateStrings: [string, string]) => {
  if (dates && dates.length === 2) {
    dateRange.value = 'custom';
    // 确保使用的是 dayjs 对象
    const startDate = typeof dates[0] === 'string' ? dayjs(dates[0]) : dates[0];
    const endDate = typeof dates[1] === 'string' ? dayjs(dates[1]) : dates[1];
    fetchData(startDate, endDate);
  }
};

// 获取数据
const fetchData = (startDate: Dayjs, endDate: Dayjs) => {
  loading.value = true;
  console.log('获取从', startDate.format('YYYY-MM-DD'), '到', endDate.format('YYYY-MM-DD'), '的数据');
  
  // 模拟API请求
  setTimeout(() => {
    // 更新统计卡片和图表数据
    loading.value = false;
    // 确保 DOM 已经更新后再初始化图表
    setTimeout(() => {
      initCharts();
    }, 0);
  }, 1000);
};

// 初始化图表
const initCharts = () => {
  // 资产分布图表
  if (assetChartRef.value) {
    const assetChart = echarts.init(assetChartRef.value);
    assetChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} USDT ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 10,
        data: ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'USDT']
      },
      series: [
        {
          name: '资产分布',
          type: 'pie',
          radius: ['50%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 5623.45, name: 'BTC' },
            { value: 3421.56, name: 'ETH' },
            { value: 956.78, name: 'BNB' },
            { value: 789.32, name: 'SOL' },
            { value: 456.78, name: 'XRP' },
            { value: 1097.78, name: 'USDT' }
          ]
        }
      ]
    });

    window.addEventListener('resize', () => {
      assetChart.resize();
    });
  }

  // 收益曲线图表
  if (profitChartRef.value) {
    const profitChart = echarts.init(profitChartRef.value);
    profitChart.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}<br/>{a}: {c} USDT'
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
        data: getDateArray()
      },
      yAxis: {
        type: 'value',
        name: '收益(USDT)'
      },
      series: [
        {
          name: '收益',
          type: 'line',
          data: generateRandomData(dateRange.value),
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(24, 144, 255, 0.8)'
              }, {
                offset: 1, color: 'rgba(24, 144, 255, 0.1)'
              }]
            }
          },
          emphasis: {
            focus: 'series'
          },
          itemStyle: {
            color: '#1890ff'
          },
          smooth: true
        }
      ]
    });

    window.addEventListener('resize', () => {
      profitChart.resize();
    });
  }
  
  // 资金曲线图表
  if (capitalChartRef.value) {
    const capitalChart = echarts.init(capitalChartRef.value);
    capitalChart.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}<br/>{a}: {c} USDT'
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
        data: getDateArray()
      },
      yAxis: {
        type: 'value',
        name: '资金(USDT)'
      },
      series: [
        {
          name: '资金',
          type: 'line',
          data: generateCapitalData(dateRange.value),
          emphasis: {
            focus: 'series'
          },
          itemStyle: {
            color: '#52c41a'
          },
          smooth: true
        }
      ]
    });

    window.addEventListener('resize', () => {
      capitalChart.resize();
    });
  }
};

// 生成日期数组
const getDateArray = () => {
  const dates = [];
  let days = 7;
  
  switch(dateRange.value) {
    case 'day':
      days = 24; // 24小时
      for(let i = 0; i < days; i++) {
        dates.push(i + ':00');
      }
      break;
    case 'week':
      days = 7;
      for(let i = 0; i < days; i++) {
        dates.push(dayjs().subtract(days - i - 1, 'day').format('MM-DD'));
      }
      break;
    case 'month':
      days = 30;
      for(let i = 0; i < days; i++) {
        if(i % 3 === 0) dates.push(dayjs().subtract(days - i - 1, 'day').format('MM-DD'));
        else dates.push('');
      }
      break;
    case 'year':
      days = 12;
      for(let i = 0; i < days; i++) {
        dates.push(dayjs().subtract(days - i - 1, 'month').format('YYYY-MM'));
      }
      break;
    default:
      for(let i = 0; i < days; i++) {
        dates.push(dayjs().subtract(days - i - 1, 'day').format('MM-DD'));
      }
  }
  
  return dates;
};

// 生成随机收益数据
const generateRandomData = (range: string) => {
  const data = [];
  let days = 7;
  let baseValue = 0;
  
  switch(range) {
    case 'day':
      days = 24;
      break;
    case 'week':
      days = 7;
      break;
    case 'month':
      days = 30;
      break;
    case 'year':
      days = 12;
      break;
  }
  
  for(let i = 0; i < days; i++) {
    // 收益可能为正也可能为负
    const change = Math.random() * 20 - 10;
    baseValue += change;
    data.push(parseFloat(baseValue.toFixed(2)));
  }
  
  return data;
};

// 生成资金曲线数据
const generateCapitalData = (range: string) => {
  const data = [];
  let days = 7;
  let baseValue = 10000; // 基础资金
  
  switch(range) {
    case 'day':
      days = 24;
      break;
    case 'week':
      days = 7;
      break;
    case 'month':
      days = 30;
      break;
    case 'year':
      days = 12;
      break;
  }
  
  for(let i = 0; i < days; i++) {
    // 资金变化
    const change = Math.random() * 200 - 50;
    baseValue += change;
    data.push(parseFloat(baseValue.toFixed(2)));
  }
  
  return data;
};

// 监听日期范围变化
watch(dateRange, (newValue) => {
  if (newValue !== 'custom') {
    handleDateRangeChange({ target: { value: newValue } } as any);
  }
});

// 组件挂载后初始化
onMounted(() => {
  // 默认选择本周数据
  handleDateRangeChange({ target: { value: dateRange.value } } as any);
});
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.date-control-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.date-selector {
  margin-left: auto;
}

.stat-card {
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
}

.card-content {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
}

.card-change {
  font-size: 14px;
}

.card-change.up {
  color: #52c41a;
}

.card-change.down {
  color: #f5222d;
}

.chart-container {
  height: 300px;
  width: 100%;
}
</style> 