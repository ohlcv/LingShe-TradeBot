<template>
  <div class="transaction-records">
    <!-- 筛选与工具栏 -->
    <Card :bordered="false" style="margin-bottom: 16px">
      <div class="filter-toolbar">
        <!-- 第一行: 时间和搜索 -->
        <div class="filters-row" style="margin-bottom: 12px;">
          <DatePicker.RangePicker
            v-model:value="dateRange"
            style="width: 300px; margin-right: 12px"
            :placeholder="['开始日期', '结束日期']"
            @change="onDateRangeChange"
          />
          <Input.Search
            v-model:value="searchKeyword"
            placeholder="搜索交易记录"
            style="width: 200px"
            @search="onSearch"
          />
        </div>
        
        <!-- 筛选条件 -->
        <div class="filters-row">
          <Select
            v-model:value="filters.strategyType"
            style="width: 140px; margin-right: 12px"
            placeholder="策略类型"
            allowClear
          >
            <Select.Option 
              v-for="option in strategyTypeOptions" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </Select.Option>
          </Select>
          <Select
            v-model:value="filters.exchange"
            style="width: 140px; margin-right: 12px"
            placeholder="交易所"
            allowClear
          >
            <Select.Option 
              v-for="option in exchangeOptions" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </Select.Option>
          </Select>
          <Select
            v-model:value="filters.contractType"
            style="width: 130px; margin-right: 12px"
            placeholder="合约类型"
            allowClear
          >
            <Select.Option 
              v-for="option in marketTypeOptions" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </Select.Option>
          </Select>
          <Select
            v-model:value="filters.direction"
            style="width: 120px; margin-right: 12px"
            placeholder="持仓方向"
            allowClear
          >
            <Select.Option 
              v-for="option in directionOptions" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </Select.Option>
          </Select>
          <Select
            v-model:value="filters.type"
            style="width: 120px; margin-right: 12px"
            placeholder="开平"
            allowClear
          >
            <Select.OptGroup label="开平">
              <Select.Option value="">全部开平</Select.Option>
              <Select.Option value="open">开仓</Select.Option>
              <Select.Option value="close">平仓</Select.Option>
            </Select.OptGroup>
          </Select>
          <Select
            v-model:value="filters.profitStatus"
            style="width: 120px; margin-right: 12px"
            placeholder="盈亏"
            allowClear
          >
            <Select.OptGroup label="盈亏">
              <Select.Option value="">全部盈亏</Select.Option>
              <Select.Option value="profit">盈利</Select.Option>
              <Select.Option value="loss">亏损</Select.Option>
            </Select.OptGroup>
          </Select>
        </div>
      </div>
    </Card>

    <!-- 交易统计卡片 -->
    <Row :gutter="16" style="margin-bottom: 16px">
      <Col :span="4">
        <Card class="stat-card">
          <div class="stat-label">交易次数</div>
          <div class="stat-value">{{ statistics.totalTrades }}</div>
        </Card>
      </Col>
      <Col :span="4">
        <Card class="stat-card">
          <div class="stat-label">交易量</div>
          <div class="stat-value">${{ formatNumber(statistics.totalVolume) }}</div>
        </Card>
      </Col>
      <Col :span="4">
        <Card class="stat-card">
          <div class="stat-label">盈亏</div>
          <div class="stat-value" :class="getProfitClass(statistics.totalProfit)">
            {{ statistics.totalProfit > 0 ? '+' : '' }}${{ formatNumber(statistics.totalProfit) }}
          </div>
        </Card>
      </Col>
      <Col :span="4">
        <Card class="stat-card">
          <div class="stat-label">盈亏率</div>
          <div class="stat-value" :class="getProfitClass(statistics.profitRate)">
            {{ statistics.profitRate > 0 ? '+' : '' }}{{ statistics.profitRate }}%
          </div>
        </Card>
      </Col>
      <Col :span="4">
        <Card class="stat-card">
          <div class="stat-label">胜率</div>
          <div class="stat-value">{{ statistics.winRate }}%</div>
        </Card>
      </Col>
      <Col :span="4">
        <Card class="stat-card">
          <div class="stat-label">均笔盈亏</div>
          <div class="stat-value" :class="getProfitClass(statistics.avgProfit)">
            {{ statistics.avgProfit > 0 ? '+' : '' }}${{ formatNumber(statistics.avgProfit) }}
          </div>
        </Card>
      </Col>
    </Row>

    <!-- 交易记录表格 -->
    <Card :bordered="false" :loading="loading">
      <Table
        :dataSource="transactions"
        :columns="columns"
        :pagination="pagination"
        :rowKey="(record: Transaction) => record.id"
        :rowSelection="{ type: 'checkbox', onChange: onSelectionChange }"
        @change="onTableChange"
        expandRowByClick
        :showSorterTooltip="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <Tag :color="record.type === 'open' ? 'blue' : 'orange'">
              {{ record.type === 'open' ? '开仓' : '平仓' }}
            </Tag>
          </template>
          <template v-else-if="column.key === 'direction'">
            <Tag :color="record.direction === 'long' ? 'green' : 'magenta'">
              {{ record.direction === 'long' ? '做多' : '做空' }}
            </Tag>
          </template>
          <template v-else-if="column.key === 'profit'">
            <span :class="getProfitClass(record.profit)">
              {{ record.profit > 0 ? '+' : '' }}${{ formatNumber(record.profit) }}
            </span>
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div class="transaction-detail">
            <div class="detail-header">
              <div class="trade-id">交易ID: {{ record.id }}</div>
              <div class="detail-actions">
                <Button type="primary" size="small" @click="viewRelatedStrategy(record)" style="margin-left: 8px">
                  查看相关策略
                </Button>
                <Button size="small" @click="viewExchangeOrder(record)" style="margin-left: 8px">
                  查看交易所订单
                </Button>
              </div>
            </div>
            
            <Row :gutter="24">
              <Col :span="12">
                <h4>交易信息</h4>
                <Descriptions :column="1" size="small" bordered>
                  <Descriptions.Item label="状态">
                    <Tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="策略名称">{{ record.strategyName }}</Descriptions.Item>
                  <Descriptions.Item label="策略类型">{{ record.strategyType }}</Descriptions.Item>
                  <Descriptions.Item label="交易所">{{ record.exchange }}</Descriptions.Item>
                  <Descriptions.Item label="交易对">{{ record.pair }}</Descriptions.Item>
                  <Descriptions.Item label="开平">{{ record.type === 'open' ? '开仓' : '平仓' }}</Descriptions.Item>
                  <Descriptions.Item label="持仓方向">{{ record.direction === 'long' ? '做多' : '做空' }}</Descriptions.Item>
                  <Descriptions.Item label="触发原因">{{ record.triggerReason || '-' }}</Descriptions.Item>
                  <Descriptions.Item label="备注">{{ record.note || '-' }}</Descriptions.Item>
                </Descriptions>
              </Col>
              <Col :span="12">
                <h4>订单详情</h4>
                <Descriptions :column="1" size="small" bordered>
                  <Descriptions.Item label="订单ID">{{ record.orderId }}</Descriptions.Item>
                  <Descriptions.Item label="订单类型">{{ record.orderType }}</Descriptions.Item>
                  <Descriptions.Item label="基础币数量">{{ record.amount }}</Descriptions.Item>
                  <Descriptions.Item label="计价币数量">${{ formatNumber(record.price * record.amount) }}</Descriptions.Item>
                  <Descriptions.Item label="价值">${{ formatNumber(record.total) }}</Descriptions.Item>
                  <Descriptions.Item label="张数">{{ record.contracts }}张</Descriptions.Item>
                  <Descriptions.Item label="盈亏" :class="getProfitClass(record.profit)">
                    {{ record.profit > 0 ? '+' : '' }}${{ formatNumber(record.profit) }}
                  </Descriptions.Item>
                  <Descriptions.Item label="手续费">${{ formatNumber(record.fee) }}</Descriptions.Item>
                  <Descriptions.Item label="系统费">${{ formatNumber(record.systemFee) }}</Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </div>
        </template>
      </Table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import dayjs from 'dayjs';
import type { TablePaginationConfig } from 'ant-design-vue';
import type { Dayjs } from 'dayjs';
import { useStrategyStore } from '@/store/modules/strategy';
import { StrategyType } from '../../store/modules/strategy';
import { useExchangeStore } from '@/store/modules/exchange';
import { useMarketTypeStore } from '@/store/modules/marketType';
import { useDirectionStore } from '@/store/modules/direction';
import type { Exchange } from '../../store/modules/exchange';
import type { MarketType } from '../../store/modules/marketType';
import type { Direction } from '../../store/modules/direction';
import {
  Card,
  DatePicker,
  Input,
  Select,
  Row,
  Col,
  Table,
  Tag,
  Button,
  Descriptions,
  Space
} from 'ant-design-vue';
import type { Transaction } from '@/types/transaction';
import type { TableColumnsType } from 'ant-design-vue';
import type { Key } from 'ant-design-vue/es/table/interface';

// 加载各个Store
const strategyStore = useStrategyStore();
const exchangeStore = useExchangeStore();
const marketTypeStore = useMarketTypeStore();
const directionStore = useDirectionStore();

// 从Store中获取筛选选项数据
const strategyTypeOptions = computed(() => {
  return [
    { value: '', label: '全部策略类型' },
    ...strategyStore.getAllActiveTypes.map((type: StrategyType) => ({
      value: type.value,
      label: type.label
    }))
  ];
});

const exchangeOptions = computed(() => {
  return [
    { value: '', label: '全部交易所' },
    ...exchangeStore.getActiveExchanges.map((exchange: Exchange) => ({
      value: exchange.value,
      label: exchange.label
    }))
  ];
});

const marketTypeOptions = computed(() => {
  return [
    { value: '', label: '全部合约类型' },
    ...marketTypeStore.getActiveMarketTypes.map((type: MarketType) => ({
      value: type.value,
      label: type.label
    }))
  ];
});

const directionOptions = computed(() => {
  return [
    { value: '', label: '全部持仓方向' },
    ...directionStore.getActiveDirections.map((direction: Direction) => ({
      value: direction.value,
      label: direction.label
    }))
  ];
});

// 加载状态
const loading = ref(false);

// 筛选条件
const filters = reactive({
  strategyType: undefined,
  exchange: undefined,
  contractType: undefined,
  direction: undefined,
  type: undefined,
  profitStatus: undefined,
});

// 日期范围
const dateRange = ref<[Dayjs, Dayjs]>([
  dayjs().subtract(30, 'day'),
  dayjs()
]);

// 搜索关键词
const searchKeyword = ref('');

// 选中的行
const selectedRows = ref<Transaction[]>([]);

// 分页设置
const pagination = reactive<TablePaginationConfig>({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`,
});

// 合约类型选项
const contractTypeOptions = [
  { value: '', label: '全部' },
  { value: 'spot', label: '现货' },
  { value: 'futures', label: '合约' },
];

// 开平选项
const typeOptions = [
  { value: '', label: '全部' },
  { value: 'open', label: '开仓' },
  { value: 'close', label: '平仓' },
];

// 盈亏状态选项
const profitStatusOptions = [
  { value: '', label: '全部' },
  { value: 'profit', label: '盈利' },
  { value: 'loss', label: '亏损' },
];

// 表格列定义
const columns: TableColumnsType<Transaction> = [
  { title: '时间', dataIndex: 'time', key: 'time', width: 180, sorter: true, align: 'center' },
  { title: '策略名称', dataIndex: 'strategyName', key: 'strategyName', width: 150, align: 'center' },
  { title: '交易对', dataIndex: 'pair', key: 'pair', width: 120, align: 'center' },
  { title: '类型', dataIndex: 'type', key: 'type', width: 100, align: 'center' },
  { title: '方向', dataIndex: 'direction', key: 'direction', width: 100, align: 'center' },
  { title: '价格', dataIndex: 'price', key: 'price', width: 120, align: 'center' },
  { title: '数量', dataIndex: 'amount', key: 'amount', width: 120, align: 'center' },
  { title: '价值', dataIndex: 'total', key: 'total', width: 120, align: 'center' },
  { title: '盈亏', dataIndex: 'profit', key: 'profit', width: 120, align: 'center' }
];

// 统计数据
const statistics = reactive({
  totalTrades: 1258,
  totalVolume: 125350,
  totalProfit: 3852,
  profitRate: 15.4,
  winRate: 65.4,
  avgProfit: 6.20,
});

// 模拟交易数据
const transactions = ref<Transaction[]>([
  {
    id: 'TX-001',
    orderId: 'OR-78901',
    time: '2023-05-20 15:30:45',
    strategyName: 'BTC网格现货做多',
    strategyType: '网格策略',
    pair: 'BTC/USDT',
    type: 'open',
    direction: 'long',
    price: 45678.12,
    amount: 0.25,
    contracts: 5,
    total: 11419.53,
    profit: 0,
    fee: 11.42,
    systemFee: 17.13,
    status: 'completed',
    exchange: 'Binance',
    orderType: '限价单',
    note: '网格层级2',
    triggerReason: '网格触发'
  },
  {
    id: 'TX-002',
    orderId: 'OR-78902',
    time: '2023-05-20 14:15:23',
    strategyName: 'ETH趋势做多',
    strategyType: '趋势策略',
    pair: 'ETH/USDT',
    type: 'close',
    direction: 'long',
    price: 2345.67,
    amount: 1.5,
    contracts: 3,
    total: 3518.51,
    profit: 120.45,
    fee: 3.52,
    systemFee: 5.28,
    status: 'completed',
    exchange: 'Binance',
    orderType: '市价单',
    note: '止盈触发',
    triggerReason: '价格突破上轨'
  },
  {
    id: 'TX-003',
    orderId: 'OR-78903',
    time: '2023-05-20 09:15:02',
    strategyName: 'BNB网格合约做空',
    strategyType: '网格策略',
    pair: 'BNB/USDT',
    type: 'open',
    direction: 'long',
    price: 325.45,
    amount: 5,
    contracts: 5,
    total: 1627.25,
    profit: 0,
    fee: 1.63,
    systemFee: 2.44,
    status: 'processing',
    exchange: 'Binance',
    orderType: '限价单',
    note: '网格层级1',
    triggerReason: '网格触发'
  },
  {
    id: 'TX-004',
    orderId: 'OR-78904',
    time: '2023-05-19 18:23:45',
    strategyName: 'SOL高频交易',
    strategyType: '高频策略',
    pair: 'SOL/USDT',
    type: 'close',
    direction: 'short',
    price: 178.32,
    amount: 10,
    contracts: 2,
    total: 1783.2,
    profit: -25.67,
    fee: 1.78,
    systemFee: 2.67,
    status: 'completed',
    exchange: 'Binance',
    orderType: '市价单',
    note: '止损触发',
    triggerReason: '价格突破下轨'
  },
  {
    id: 'TX-005',
    orderId: 'OR-78905',
    time: '2023-05-19 16:18:29',
    strategyName: 'XRP长线投资',
    strategyType: '长线策略',
    pair: 'XRP/USDT',
    type: 'open',
    direction: 'long',
    price: 0.65,
    amount: 1000,
    contracts: 1,
    total: 650,
    profit: 0,
    fee: 0.65,
    systemFee: 0.98,
    status: 'completed',
    exchange: 'Binance',
    orderType: '限价单',
    note: '定投',
    triggerReason: '定时触发'
  }
]);

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    completed: 'green',
    processing: 'blue',
    failed: 'red',
    pending: 'orange',
    canceled: 'gray'
  };
  return colors[status] || 'default';
};

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
    pending: '待处理',
    canceled: '已取消'
  };
  return texts[status] || status;
};

// 获取盈亏样式类
const getProfitClass = (value: number) => {
  return value > 0 ? 'profit-positive' : value < 0 ? 'profit-negative' : '';
};

// 格式化数字
const formatNumber = (value: number) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 处理表格变化
const onTableChange = (pag: TablePaginationConfig) => {
  pagination.current = pag.current || 1;
  pagination.pageSize = pag.pageSize || 10;
  fetchData();
};

// 处理日期范围变化
const onDateRangeChange = (value: [Dayjs, Dayjs] | [string, string], dateString: [string, string]) => {
  if (Array.isArray(value) && value.length === 2 && typeof value[0] !== 'string') {
    // 处理日期变化
    fetchData();
  }
};

// 处理搜索
const onSearch = () => {
  pagination.current = 1;
  fetchData();
};

// 处理选择变化
const onSelectionChange = (selectedRowKeys: Key[], rows: Transaction[]) => {
  selectedRows.value = rows;
};

// 查看相关策略
const viewRelatedStrategy = (record: Transaction) => {
  console.log('查看相关策略:', record.strategyName);
};

// 查看交易所订单
const viewExchangeOrder = (record: Transaction) => {
  console.log('查看交易所订单:', record.orderId);
};

// 计算统计数据
const calculateStatistics = (data: Transaction[]) => {
  // 初始化值
  let trades = 0;
  let volume = 0;
  let profit = 0;
  let winCount = 0;

  // 遍历交易记录计算统计值
  data.forEach(transaction => {
    trades++;
    volume += transaction.total;
    profit += transaction.profit;

    // 计算盈利交易数量（用于胜率计算）
    if (transaction.profit > 0) {
      winCount++;
    }
  });

  // 更新统计数据
  statistics.totalTrades = trades;
  statistics.totalVolume = volume;
  statistics.totalProfit = profit;
  statistics.profitRate = trades > 0 ? (profit / volume) * 100 : 0;
  statistics.winRate = trades > 0 ? (winCount / trades) * 100 : 0;
  statistics.avgProfit = trades > 0 ? profit / trades : 0;
  
  // 格式化数值以限制小数位数
  statistics.profitRate = parseFloat(statistics.profitRate.toFixed(1));
  statistics.winRate = parseFloat(statistics.winRate.toFixed(1));
  statistics.avgProfit = parseFloat(statistics.avgProfit.toFixed(2));
};

// 获取数据
const fetchData = () => {
  loading.value = true;
  
  // 模拟API请求
  setTimeout(() => {
    // 这里应该是实际的API请求
    console.log('获取交易记录，筛选条件:', {
      strategyType: filters.strategyType,
      exchange: filters.exchange,
      contractType: filters.contractType,
      direction: filters.direction,
      type: filters.type,
      profitStatus: filters.profitStatus,
      dateRange: dateRange.value ? [
        dateRange.value[0].format('YYYY-MM-DD'),
        dateRange.value[1].format('YYYY-MM-DD')
      ] : null,
      searchKeyword: searchKeyword.value,
      page: pagination.current,
      pageSize: pagination.pageSize
    });
    
    // 假设这是API返回的分页信息
    pagination.total = 58;
    
    // 在实际应用中，这里会使用API返回的数据来更新统计数据
    // 目前我们使用模拟数据进行统计
    calculateStatistics(transactions.value);
    
    loading.value = false;
  }, 500);
};

// 监听筛选条件变化，重新计算统计数据
watch([filters, dateRange, searchKeyword], () => {
  // 在真实环境中，这里会通过API获取新的数据，并重新计算统计数据
  // 在示例中，我们模拟一些随机变化
  fetchData();
}, { deep: true });

// 组件挂载后初始化
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.transaction-records {
  padding: 0;
}

.filter-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.filters-row {
  display: flex;
  align-items: center;
}

.stat-card {
  text-align: center;
  height: 100%;
}

.stat-label {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.65);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

.profit-positive {
  color: #52c41a;
}

.profit-negative {
  color: #f5222d;
}

.transaction-detail {
  padding: 16px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.trade-id {
  font-weight: bold;
}

.detail-actions {
  display: flex;
  align-items: center;
}

h4 {
  margin-top: 0;
  margin-bottom: 12px;
  font-weight: bold;
}
</style> 