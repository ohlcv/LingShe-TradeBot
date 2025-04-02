<template>
  <div class="strategy-list">
    <!-- 筛选器 -->
    <Card class="filter-container" :bordered="false" style="margin-bottom: 16px">
      <div class="filters-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0;">
      </div>
      
      <Collapse :bordered="false" :default-active-key="['1']" class="custom-collapse">
        <Collapse.Panel key="1" header="筛选条件">
          <!-- 第一行：状态、盈亏和搜索 -->
          <div class="filters-row" style="margin-bottom: 12px;">
            <Select
              v-model:value="filters.status"
              style="width: 150px; margin-right: 12px"
              placeholder="状态"
              @change="handleFilterChange"
              allow-clear
            >
              <Select.OptGroup label="状态">
                <Select.Option value="">全部状态</Select.Option>
                <Select.Option value="running">运行中</Select.Option>
                <Select.Option value="paused">已暂停</Select.Option>
              </Select.OptGroup>
            </Select>
            <Select
              v-model:value="filters.profitStatus"
              style="width: 150px; margin-right: 12px"
              placeholder="盈亏"
              @change="handleFilterChange"
              allow-clear
            >
              <Select.OptGroup label="盈亏">
                <Select.Option value="">全部盈亏</Select.Option>
                <Select.Option value="profit">盈利</Select.Option>
                <Select.Option value="loss">亏损</Select.Option>
              </Select.OptGroup>
            </Select>
            <Input.Search
              v-model:value="filters.keyword"
              placeholder="搜索策略名称"
              style="width: 200px"
              @search="handleSearch"
              allow-clear
            />
          </div>
          
          <!-- 第二行：策略类型、交易所、合约类型、持仓方向 -->
          <div class="filters-row" style="margin-bottom: 12px;">
            <Select
              v-model:value="filters.strategyType"
              style="width: 140px; margin-right: 12px"
              placeholder="策略类型"
              @change="handleFilterChange"
              allow-clear
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
              @change="handleFilterChange"
              allow-clear
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
              v-model:value="filters.marketType"
              style="width: 140px; margin-right: 12px"
              placeholder="产品类型"
              @change="handleFilterChange"
              allow-clear
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
              style="width: 140px; margin-right: 12px"
              placeholder="持仓方向"
              @change="handleFilterChange"
              allow-clear
            >
              <Select.Option 
                v-for="option in directionOptions" 
                :key="option.value" 
                :value="option.value"
              >
                {{ option.label }}
              </Select.Option>
            </Select>
          </div>
        </Collapse.Panel>
      </Collapse>
    </Card>
    
    <!-- 策略列表 -->
    <Spin :spinning="loading">
      <div class="select-all-container" v-if="strategies.length > 0">
        <Checkbox
          :indeterminate="indeterminate"
          :checked="checkAll"
          @change="onCheckAllChange"
        >
          <span class="select-all-text">全选</span>
        </Checkbox>
        <span class="selected-count" v-if="selectedRowKeys.length > 0">
          已选择 {{ selectedRowKeys.length }} 个策略
        </span>
        <Button.Group v-if="selectedRowKeys.length > 0" class="batch-actions">
          <Button class="start-button" @click="batchStartStrategies" :disabled="!hasSelectedPaused">
            <PlayCircleOutlined /> 启动
          </Button>
          <Button class="pause-button-ghost" @click="batchPauseStrategies" :disabled="!hasSelectedRunning">
            <PauseCircleOutlined /> 暂停
          </Button>
          <Button danger @click="batchDeleteStrategies">
            <DeleteOutlined /> 删除
          </Button>
        </Button.Group>
      </div>
      
      <Row :gutter="[24, 24]" class="strategy-cards">
        <Col :xs="24" :sm="24" :md="24" :lg="12" :xl="8" v-for="strategy in filteredStrategies" :key="strategy.id">
          <Card 
            class="strategy-card" 
            :bordered="false" 
            hoverable 
            :class="{ 
              'card-long': strategy.direction === '做多', 
              'card-short': strategy.direction === '做空',
              'card-selected': selectedRowKeys.includes(strategy.id)
            }"
            @click="viewDetails(strategy)"
          >
            <template #extra>
              <Checkbox
                :checked="selectedRowKeys.includes(strategy.id)"
                @click.stop
                @change="(e: CheckboxChangeEvent) => toggleSelection(strategy.id, e.target.checked)"
              />
            </template>
            <template #title>
              <div class="card-title">
                <div class="title-left">
                  <span class="strategy-name">{{ strategy.name }}</span>
                  <Tag :color="getStatusColor(strategy.status)">{{ getStatusText(strategy.status) }}</Tag>
                </div>
                <div class="title-right">
                  <Dropdown>
                    <template #overlay>
                      <Menu>
                        <Menu.Item key="1" @click.stop="editStrategy(strategy)">
                          <EditOutlined /> 编辑
                        </Menu.Item>
                        <Menu.Item key="2" @click.stop="duplicateStrategy(strategy)">
                          <CopyOutlined /> 复制
                        </Menu.Item>
                      </Menu>
                    </template>
                    <Button type="link" class="ant-dropdown-link" @click.stop>
                      <EllipsisOutlined />
                    </Button>
                  </Dropdown>
                </div>
              </div>
            </template>
            
            <div class="card-content">
              <Descriptions :column="1" size="small" bordered>
                <Descriptions.Item label="策略类型">{{ strategy.strategyType === 'grid' ? '网格策略' : strategy.strategyType === 'trend' ? '趋势策略' : '动态策略' }}</Descriptions.Item>
                <Descriptions.Item label="交易所">{{ strategy.exchange }}</Descriptions.Item>
                <Descriptions.Item label="交易对">{{ strategy.pair }}</Descriptions.Item>
                <Descriptions.Item label="产品类型">{{ strategy.marketType }}</Descriptions.Item>
                <Descriptions.Item label="持仓方向">{{ strategy.direction }}</Descriptions.Item>
                <Descriptions.Item label="持仓价值">{{ strategy.holdingAmount }} USDT</Descriptions.Item>
                <Descriptions.Item label="收益">
                  <Typography.Text :class="{ 'profit-positive': strategy.profit > 0, 'profit-negative': strategy.profit < 0 }">
                    {{ strategy.profit > 0 ? '+' : '' }}{{ strategy.profit }} USDT
                  </Typography.Text>
                </Descriptions.Item>
              </Descriptions>
            </div>
            
            <Divider style="margin: 12px 0" />
            
            <div class="card-footer">
              <div class="footer-stats">
                <Row :gutter="16">
                  <Col :span="12">
                    <div class="stat-item">
                      <Typography.Title :level="4" class="stat-value">{{ strategy.runningDays }}</Typography.Title>
                      <Typography.Text class="stat-label">运行天数</Typography.Text>
                    </div>
                  </Col>
                  <Col :span="12">
                    <div class="stat-item">
                      <Typography.Title :level="4" class="stat-value">{{ strategy.completedOrders }}</Typography.Title>
                      <Typography.Text class="stat-label">已完成订单</Typography.Text>
                    </div>
                  </Col>
                </Row>
              </div>
              
              <div class="action-buttons" @click.stop>
                <Space>
                  <Button 
                    v-if="strategy.status === 'running'"
                    class="pause-button-ghost"
                    shape="round"
                    size="small"
                    @click="pauseStrategy(strategy)"
                  >
                    <PauseCircleOutlined />
                    暂停
                  </Button>
                  <Button 
                    v-if="strategy.status === 'paused'"
                    class="start-button"
                    shape="round"
                    size="small"
                    @click="resumeStrategy(strategy)"
                  >
                    <PlayCircleOutlined />
                    启动
                  </Button>
                  <Popconfirm
                    title="确定要删除此策略吗？"
                    ok-text="删除"
                    cancel-text="取消"
                    @confirm="deleteStrategy(strategy)"
                    placement="topRight"
                  >
                    <Button 
                      danger 
                      shape="round"
                      size="small"
                      @click.stop
                    >
                      <DeleteOutlined />
                      删除
                    </Button>
                  </Popconfirm>
                </Space>
              </div>
            </div>
          </Card>
        </Col>
        
        <!-- 添加策略卡片 -->
        <Col :xs="24" :sm="24" :md="24" :lg="12" :xl="8">
          <Card 
            class="strategy-card add-strategy-card" 
            :bordered="false" 
            hoverable 
            @click="createStrategy"
          >
            <div class="add-strategy-content">
              <div class="add-icon">
                <PlusOutlined />
              </div>
              <div class="add-text">创建新策略</div>
            </div>
          </Card>
        </Col>
      </Row>
    </Spin>

    <!-- 分页 -->
    <div class="pagination-container" v-if="totalItems > pageSize">
      <Pagination
        v-model:current="currentPage"
        :total="totalItems"
        :pageSize="pageSize"
        show-quick-jumper
        show-size-changer
        :pageSizeOptions="['12', '24', '36', '48']"
        @change="handlePageChange"
        @showSizeChange="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import { 
  PlusOutlined, 
  EditOutlined, 
  CopyOutlined, 
  DeleteOutlined,
  EllipsisOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from '@ant-design/icons-vue';
import { useStrategyStore } from '../../store/modules/strategy';
import { useStrategyOperationStore } from '@/store/modules/strategyOperation'
import { useExchangeStore } from '../../store/modules/exchange';
import { useMarketTypeStore } from '../../store/modules/marketType';
import { useDirectionStore } from '../../store/modules/direction';
import {
  Card,
  Select,
  Input,
  Collapse,
  Checkbox,
  Button,
  Row,
  Col,
  Tag,
  Dropdown,
  Menu,
  Descriptions,
  Spin,
  Divider,
  Space,
  Popconfirm,
  Pagination,
  Typography
} from 'ant-design-vue'

import type { CheckboxChangeEvent } from 'ant-design-vue/es/checkbox/interface'
import type { Strategy } from '@/store/modules/strategyOperation'

// 加载各个Store
const strategyStore = useStrategyStore();
const strategyOperationStore = useStrategyOperationStore();
const exchangeStore = useExchangeStore();
const marketTypeStore = useMarketTypeStore();
const directionStore = useDirectionStore();

// 从Store中获取筛选选项数据
const strategyTypeOptions = computed(() => [
  { value: '', label: '全部策略类型' },
  ...strategyStore.getAllActiveTypes.map(type => ({ value: type.value, label: type.label }))
]);

const exchangeOptions = computed(() => [
  { value: '', label: '全部交易所' },
  ...exchangeStore.getActiveExchanges.map(exchange => ({ value: exchange.value, label: exchange.label }))
]);

const marketTypeOptions = computed(() => [
  { value: '', label: '全部产品类型' },
  ...marketTypeStore.getActiveMarketTypes.map(type => ({ value: type.value, label: type.label }))
]);

const directionOptions = computed(() => [
  { value: '', label: '全部持仓方向' },
  ...directionStore.getActiveDirections.map(dir => ({ value: dir.value, label: dir.label }))
]);

// 类型定义
interface Filters {
  status: 'running' | 'paused' | 'stopped' | ''
  profitStatus: 'profit' | 'loss' | ''
  keyword: string
  strategyType: 'grid' | 'trend' | 'dynamic' | ''
  exchange: string
  marketType: string
  direction: string
}

const router = useRouter();
const loading = ref(true);
const currentPage = ref(1);
const pageSize = ref(12);
const totalItems = ref(0);

// 筛选条件
const filters = reactive<Filters>({
  status: '',
  profitStatus: '',
  keyword: '',
  strategyType: '',
  exchange: '',
  marketType: '',
  direction: ''
});

// 策略数据
const strategies = ref<Strategy[]>([]);

// 选中的策略
const selectedRowKeys = ref<string[]>([]);

// 全选状态
const checkAll = ref(false);
const indeterminate = ref(false);

// 计算是否有选中的暂停策略
const hasSelectedPaused = computed(() => {
  return strategies.value.some(s => 
    selectedRowKeys.value.includes(s.id) && s.status === 'paused'
  );
});

// 计算是否有选中的运行中策略
const hasSelectedRunning = computed(() => {
  return strategies.value.some(s => 
    selectedRowKeys.value.includes(s.id) && s.status === 'running'
  );
});

// 切换单个策略选择状态
const toggleSelection = (id: string, checked: boolean) => {
  if (checked) {
    if (!selectedRowKeys.value.includes(id)) {
      selectedRowKeys.value.push(id)
    }
  } else {
    selectedRowKeys.value = selectedRowKeys.value.filter(key => key !== id)
  }
  updateCheckAllStatus()
}

// 全选切换处理
const onCheckAllChange = (e: CheckboxChangeEvent) => {
  const checked = e.target.checked
  selectedRowKeys.value = checked ? filteredStrategies.value.map(s => s.id) : []
  updateCheckAllStatus()
}

// 更新全选状态
const updateCheckAllStatus = () => {
  const filteredIds = filteredStrategies.value.map(s => s.id)
  const filteredSelectedCount = selectedRowKeys.value.filter(id => filteredIds.includes(id)).length
  
  indeterminate.value = filteredSelectedCount > 0 && filteredSelectedCount < filteredIds.length
  checkAll.value = filteredIds.length > 0 && filteredSelectedCount === filteredIds.length
}

// 批量启动策略
const batchStartStrategies = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要启动的策略')
    return
  }

  try {
    loading.value = true
    const selectedStrategies = strategies.value.filter(s => 
      selectedRowKeys.value.includes(s.id) && s.status === 'paused'
    )
    
    // 实现批量启动逻辑
    await Promise.all(selectedStrategies.map(strategy => 
      strategyOperationStore.startStrategy(strategy.id)
    ))
    
    message.success(`已启动 ${selectedStrategies.length} 个策略`)
    await strategyOperationStore.fetchStrategies()
  } catch (error) {
    message.error('启动策略失败')
    console.error('启动策略失败:', error)
  } finally {
    loading.value = false
  }
}

// 批量暂停策略
const batchPauseStrategies = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要暂停的策略')
    return
  }

  try {
    loading.value = true
    const selectedStrategies = strategies.value.filter(s => 
      selectedRowKeys.value.includes(s.id) && s.status === 'running'
    )
    
    // 实现批量暂停逻辑
    await Promise.all(selectedStrategies.map(strategy => 
      strategyOperationStore.pauseStrategy(strategy.id)
    ))
    
    message.success(`已暂停 ${selectedStrategies.length} 个策略`)
    await strategyOperationStore.fetchStrategies()
  } catch (error) {
    message.error('暂停策略失败')
    console.error('暂停策略失败:', error)
  } finally {
    loading.value = false
  }
}

// 批量删除策略
const batchDeleteStrategies = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的策略')
    return
  }

  Modal.confirm({
    title: '确认删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个策略吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        loading.value = true
        // 实现批量删除逻辑
        await Promise.all(selectedRowKeys.value.map(id => 
          strategyOperationStore.deleteStrategy(id)
        ))
        
        message.success(`已删除 ${selectedRowKeys.value.length} 个策略`)
        await strategyOperationStore.fetchStrategies()
      } catch (error) {
        message.error('删除策略失败')
        console.error('删除策略失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

// 筛选后的策略
const filteredStrategies = computed(() => {
  return strategies.value.filter(strategy => {
    // 状态筛选
    if (filters.status && strategy.status !== filters.status) {
      return false;
    }
    
    // 盈亏筛选
    if (filters.profitStatus) {
      if (filters.profitStatus === 'profit' && strategy.profit <= 0) {
        return false;
      }
      if (filters.profitStatus === 'loss' && strategy.profit >= 0) {
        return false;
      }
    }
    
    // 策略类型筛选 - 只有grid/网格类型，匹配所有网格类型
    if (filters.strategyType && filters.strategyType === 'grid') {
      if (!strategy.gridType || !['arithmetic', 'geometric', 'custom'].includes(strategy.gridType)) {
        return false;
      }
    }
    
    // 交易所筛选
    if (filters.exchange && strategy.exchange !== filters.exchange) {
      return false;
    }
    
    // 产品类型筛选
    if (filters.marketType && strategy.marketType !== filters.marketType) {
      return false;
    }
    
    // 持仓方向筛选
    if (filters.direction && strategy.direction !== filters.direction) {
      return false;
    }
    
    // 关键词搜索
    if (filters.keyword && !strategy.name.toLowerCase().includes(filters.keyword.toLowerCase())) {
      return false;
    }
    
    return true;
  });
});

// 获取状态颜色
const getStatusColor = (status: 'running' | 'paused' | 'stopped'): string => {
  switch (status) {
    case 'running':
      return 'success'
    case 'paused':
      return 'warning'
    case 'stopped':
      return 'default'
    default:
      return 'default'
  }
}

// 获取状态文本
const getStatusText = (status: 'running' | 'paused' | 'stopped'): string => {
  switch (status) {
    case 'running':
      return '运行中'
    case 'paused':
      return '已暂停'
    case 'stopped':
      return '已停止'
    default:
      return '未知状态'
  }
}

// 处理筛选条件变化
const handleFilterChange = () => {
  // 重置分页到第一页
  currentPage.value = 1;
  // 实际项目中可以调用API重新获取数据
  // 这里直接使用本地数据进行筛选
};

// 处理搜索
const handleSearch = (value: string) => {
  filters.keyword = value;
  handleFilterChange();
};

// 处理分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page;
  // 实际项目中可以调用API获取对应页的数据
};

// 创建新策略
const createStrategy = () => {
  router.push('/strategies/create');
};

// 编辑策略
const editStrategy = (strategy: Strategy) => {
  router.push(`/grid/${strategy.id}`);
};

// 复制策略
const duplicateStrategy = (strategy: Strategy) => {
  message.success(`已复制策略: ${strategy.name}`);
  // 实际项目中可以调用API复制策略
};

// 删除策略
const deleteStrategy = async (strategy: Strategy) => {
  try {
    loading.value = true
    await strategyOperationStore.deleteStrategy(strategy.id)
    message.success('删除成功')
    await strategyOperationStore.fetchStrategies()
  } catch (error) {
    message.error('删除失败')
    console.error('删除策略失败:', error)
  } finally {
    loading.value = false
  }
}

// 暂停策略
const pauseStrategy = async (strategy: Strategy) => {
  try {
    loading.value = true
    await strategyOperationStore.pauseStrategy(strategy.id)
    message.success('暂停成功')
    await strategyOperationStore.fetchStrategies()
  } catch (error) {
    message.error('暂停失败')
    console.error('暂停策略失败:', error)
  } finally {
    loading.value = false
  }
}

// 恢复策略
const resumeStrategy = async (strategy: Strategy) => {
  try {
    loading.value = true
    await strategyOperationStore.startStrategy(strategy.id)
    message.success('启动成功')
    await strategyOperationStore.fetchStrategies()
  } catch (error) {
    message.error('启动失败')
    console.error('启动策略失败:', error)
  } finally {
    loading.value = false
  }
}

// 查看策略详情
const viewDetails = (strategy: Strategy) => {
  router.push(`/strategies/${strategy.id}`);
};

// 加载策略数据
const loadStrategies = async () => {
  try {
    loading.value = true
    await strategyOperationStore.fetchStrategies()
    strategies.value = strategyOperationStore.getStrategies()
    totalItems.value = strategies.value.length
  } catch (error) {
    message.error('加载策略列表失败')
    console.error('加载策略列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听筛选条件变化，更新全选状态
watch([filters, strategies], () => {
  updateCheckAllStatus();
}, { deep: true });

// 组件挂载时加载数据
onMounted(() => {
  loadStrategies();
});

// 处理每页显示数量变化
const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  // 实际项目中可以调用API重新获取对应页的数据
};
</script>

<style scoped>
.strategy-list {
  padding: 0;
  background-color: #f0f2f5;
  min-height: 100vh;
}

.filter-container {
  margin-bottom: 0px;
  border-radius: 0;
}

.strategy-cards {
  margin-bottom: 24px;
  padding: 0 12px;
}

.strategy-card {
  height: 100%;
  transition: all 0.3s;
  cursor: pointer;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-long::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background-color: #52c41a;
}

.card-short::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background-color: #f5222d;
}

.strategy-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.strategy-card:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  flex-wrap: nowrap;
}

.title-left {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  overflow: hidden;
  gap: 8px;
  max-width: calc(100% - 32px);
}

.strategy-name {
  font-weight: 600;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 60%;
}

.card-content {
  margin-bottom: 8px;
  flex-grow: 1;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  line-height: 1.5;
}

.info-label {
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
  min-width: 70px;
  flex-shrink: 0;
  text-align: left;
}

.info-value {
  font-weight: 500;
  text-align: right;
  flex-grow: 1;
  padding-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profit-row {
  margin-top: 8px;
  margin-bottom: 4px;
}

.profit-percent-row {
  margin-bottom: 0;
}

.profit-row .info-value,
.profit-percent-row .info-value {
  font-weight: 600;
  font-size: 15px;
}

.profit-positive {
  color: #52c41a;
}

.profit-negative {
  color: #f5222d;
}

.card-footer {
  padding-top: 12px;
  margin-top: auto;
}

.footer-stats {
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 4px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1890ff;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  justify-content: center;
}

.empty-container {
  margin: 48px 0;
  background-color: white;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.pagination-container {
  text-align: center;
  margin-top: 24px;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .strategy-name {
    max-width: 50%;
  }
}

@media (max-width: 576px) {
  .strategy-name {
    max-width: 70%;
  }
  
  .info-label {
    min-width: 80px;
  }
}

.max-positions-setting {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.setting-label {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  min-width: 110px;
}

.setting-item {
  padding: 12px 0;
}

.setting-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.setting-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-status {
  display: flex;
  align-items: center;
}

.setting-status .ant-tag {
  font-size: 14px;
  padding: 3px 8px;
  font-weight: 500;
}

.card-selected {
  box-shadow: 0 0 0 2px #1890ff;
}

.batch-action-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 12px;
}

.select-all-container {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 12px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  padding: 12px;
}

.select-all-text {
  font-weight: 500;
  font-size: 14px;
}

.selected-count {
  margin-left: 16px;
  color: #1890ff;
  font-weight: 500;
}

.batch-actions {
  margin-left: auto;
}

.add-strategy-card {
  height: 100%;
  border: 2px dashed #d9d9d9;
  background-color: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.add-strategy-card:hover {
  border-color: #1890ff;
  background-color: rgba(24, 144, 255, 0.05);
}

.add-strategy-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px;
}

.add-icon {
  font-size: 48px;
  color: #1890ff;
  margin-bottom: 16px;
}

.add-text {
  font-size: 18px;
  font-weight: 500;
  color: #1890ff;
}

.risk-card {
  height: 100%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.risk-card :deep(.ant-card-head) {
  min-height: 40px;
}

.risk-card :deep(.ant-card-head-title) {
  padding: 8px 0;
  font-size: 14px;
}

.risk-status {
  margin-top: 12px;
}

.risk-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.risk-value {
  font-size: 12px;
  min-width: 45px;
  text-align: right;
  padding-left: 8px;
  flex-shrink: 0;
}

.risk-progress {
  flex-grow: 1;
  margin-right: 8px;
}

.risk-status :deep(.ant-progress-inner) {
  background-color: #f5f5f5;
}

.risk-status :deep(.ant-progress-bg) {
  transition: all 0.3s ease;
}

.custom-collapse {
  background: white;
  border-radius: 8px;
}

.custom-collapse :deep(.ant-collapse-header) {
  font-weight: 500;
  font-size: 16px;
}

.zero-progress {
  background-color: #f5f5f5;
}

.zero-progress :deep(.ant-progress-bg) {
  width: 0 !important;
  background: transparent !important;
}

.zero-progress :deep(.ant-progress-text) {
  color: rgba(0, 0, 0, 0.65);
}

.filters-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.start-button {
  background-color: transparent;
  border-color: #1890ff;
  color: #1890ff;
}

.start-button:hover, 
.start-button:focus {
  background-color: rgba(24, 144, 255, 0.1);
  border-color: #40a9ff;
  color: #40a9ff;
}

.start-button:active {
  background-color: rgba(24, 144, 255, 0.2);
  border-color: #096dd9;
  color: #096dd9;
}

.pause-button-ghost {
  background-color: transparent;
  border-color: #faad14;
  color: #faad14;
}

.pause-button-ghost:hover,
.pause-button-ghost:focus {
  background-color: rgba(250, 173, 20, 0.1);
  border-color: #ffc53d;
  color: #ffc53d;
}

.pause-button-ghost:active {
  background-color: rgba(250, 173, 20, 0.2);
  border-color: #d48806;
  color: #d48806;
}
</style> 