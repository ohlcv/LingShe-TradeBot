<template>
  <div class="create-strategy">
    <a-card :bordered="false">
      <template #title>
        <div class="strategy-steps">
          <div class="step-item" :class="{ active: currentStep === 0 }">
            <div class="step-number" v-if="currentStep === 0">1</div>
            <check-circle-outlined class="step-icon completed" v-else />
            <span class="step-text">基本设置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item" :class="{ active: currentStep === 1 }">
            <div class="step-number" v-if="currentStep <= 1">2</div>
            <check-circle-outlined class="step-icon completed" v-else />
            <span class="step-text">策略参数</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item" :class="{ active: currentStep === 2 }">
            <div class="step-number" v-if="currentStep <= 2">3</div>
            <check-circle-outlined class="step-icon completed" v-else />
            <span class="step-text">风控配置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item" :class="{ active: currentStep === 3 }">
            <div class="step-number">4</div>
            <span class="step-text">完成</span>
          </div>
        </div>
      </template>

      <h1 class="page-title">
        <a-button type="link" style="margin-right: 8px; padding: 0" @click="returnToStrategyList">
          <ArrowLeftOutlined />
        </a-button>
        创建新策略
      </h1>
      
      <!-- 步骤1：基本设置 -->
      <div v-if="currentStep === 0" class="step-container">
        <a-form
          :model="formState"
          :rules="rules"
          ref="formRef"
          layout="vertical"
          class="strategy-form"
        >
          <!-- 第一行：策略ID -->
          <a-row :gutter="24">
            <a-col :span="24">
              <a-form-item label="策略ID" name="strategyId">
                <a-input 
                  v-model:value="formState.strategyId"
                  placeholder="系统自动生成"
                  disabled
                />
                <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">策略ID为系统自动生成的唯一标识</div>
              </a-form-item>
            </a-col>
          </a-row>
          
          <!-- 第二行：策略名称和交易对 -->
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="策略名称" name="strategyName">
                <a-input 
                  v-model:value="formState.strategyName"
                  placeholder="请输入策略名称"
                  :maxLength="30"
                />
                <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">
                  <a @click="generateStrategyName">自动生成名称</a>
                </div>
              </a-form-item>
            </a-col>
            
            <a-col :span="12">
              <a-form-item label="交易对" required>
                <a-row :gutter="8">
                  <a-col :span="11">
                    <a-form-item 
                      name="baseCurrency" 
                      noStyle
                      :rules="[{ required: true, message: '请输入基础币' }]"
                    >
                      <a-input
                        v-model:value="formState.baseCurrency"
                        placeholder="基础币 (如: BTC)"
                        :maxLength="10"
                        @change="handleInputChange"
                      />
                    </a-form-item>
                  </a-col>
                  <a-col :span="2" style="text-align: center">
                    <span style="line-height: 32px">/</span>
                  </a-col>
                  <a-col :span="11">
                    <a-form-item 
                      name="quoteCurrency" 
                      noStyle
                      :rules="[{ required: true, message: '请输入计价币' }]"
                    >
                      <a-input
                        v-model:value="formState.quoteCurrency"
                        placeholder="计价币 (如: USDT)"
                        :maxLength="10"
                        @change="handleInputChange"
                      />
                    </a-form-item>
                  </a-col>
                </a-row>
              </a-form-item>
            </a-col>
          </a-row>
          
          <!-- 第三行：交易所和API密钥 -->
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="交易所" name="exchange">
                <a-select
                  v-model:value="formState.exchange"
                  placeholder="请选择交易所"
                  @change="handleExchangeChange"
                >
                  <a-select-option v-for="exchange in exchanges" :key="exchange.value" :value="exchange.value">
                    {{ exchange.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            
            <a-col :span="12">
              <a-form-item label="API密钥" name="apiKey">
                <a-select
                  v-model:value="formState.apiKey"
                  placeholder="请选择API密钥"
                  :disabled="!formState.exchange"
                >
                  <a-empty v-if="!availableApiKeys.length" description="请先选择交易所" />
                  <a-select-option v-for="api in availableApiKeys" :key="api.id" :value="api.id">
                    {{ api.name }}
                  </a-select-option>
                </a-select>
                <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">选择用于此策略的交易所API密钥</div>
              </a-form-item>
            </a-col>
          </a-row>
          
          <!-- 第四行：产品类型和持仓方向 -->
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="产品类型" name="marketType">
                <a-select
                  v-model:value="formState.marketType"
                  placeholder="请选择产品类型"
                  @change="handleMarketTypeChange"
                >
                  <a-select-option v-for="type in marketTypes" :key="type.value" :value="type.value">
                    {{ type.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            
            <a-col :span="12">
              <a-form-item label="持仓方向" name="direction">
                <a-select
                  v-model:value="formState.direction"
                  placeholder="请选择持仓方向"
                  @change="handleDirectionChange"
                >
                  <a-select-option v-for="direction in directions" :key="direction.value" :value="direction.value">
                    {{ direction.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-form-item label="策略类型" name="strategyType">
            <a-radio-group v-model:value="formState.strategyType" hidden>
              <a-radio v-for="strategy in strategyTypes" :key="strategy.value" :value="strategy.value"></a-radio>
            </a-radio-group>
            <div class="all-strategy-types">
              <div class="strategy-card-container" v-for="strategy in strategyTypes" :key="strategy.value">
                <a-card 
                  class="strategy-card"
                  :class="{'selected-strategy': formState.strategyType === strategy.value}"
                  @click="() => formState.strategyType = strategy.value"
                >
                  <template #cover>
                    <div class="strategy-card-header">
                      <a-radio :value="strategy.value" :checked="formState.strategyType === strategy.value" @change="() => formState.strategyType = strategy.value" />
                      <component :is="strategy.icon" style="font-size: 24px;" />
                    </div>
                  </template>
                  <a-card-meta :title="strategy.label" :description="strategy.description" />
                </a-card>
              </div>
              
              <!-- 即将推出的策略 -->
              <div class="strategy-card-container" v-for="strategy in comingSoonStrategies" :key="strategy.value">
                <a-card 
                  class="strategy-card coming-soon-card"
                  @click="handleComingSoonStrategy(strategy)"
                >
                  <template #cover>
                    <div class="strategy-card-header">
                      <a-radio :value="strategy.value" :disabled="true" />
                      <component :is="strategy.icon" style="font-size: 24px; opacity: 0.5;" />
                    </div>
                  </template>
                  <a-card-meta :title="strategy.label" :description="strategy.description" />
                  <div class="coming-soon-badge">敬请期待</div>
                </a-card>
              </div>
            </div>
          </a-form-item>
        </a-form>
      </div>

      <div class="step-actions">
        <a-space>
          <a-button @click="goBack" v-if="currentStep > 0">
            上一步
          </a-button>
          <a-button type="primary" @click="nextStep">
            {{ currentStep === 3 ? '完成' : '下一步' }}
          </a-button>
        </a-space>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  AppstoreOutlined,
  LineChartOutlined,
  PartitionOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  TeamOutlined,
  SwapOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons-vue';
import { useStrategyStore } from '../../store/modules/strategy';
import { useExchangeStore } from '../../store/modules/exchange';
import { useMarketTypeStore } from '../../store/modules/marketType';
import { useDirectionStore } from '../../store/modules/direction';

const router = useRouter();
const route = useRoute();
const formRef = ref();
const currentStep = ref(0);

// 加载各个Store
const strategyStore = useStrategyStore();
const exchangeStore = useExchangeStore();
const marketTypeStore = useMarketTypeStore();
const directionStore = useDirectionStore();

// 模拟API密钥列表
const allApiKeys = ref([
  {
    id: 1,
    exchange: 'binance',
    name: '币安主账户',
    apiKey: '3a7d*********************6f5c',
    secretKey: '5e9a*********************8c2d',
    passphrase: '',
    description: '主账户API',
    status: 'active'
  },
  {
    id: 2,
    exchange: 'okx',
    name: 'OKX测试',
    apiKey: '7b6e*********************9d3a',
    secretKey: '2f8c*********************4b7d',
    passphrase: '******',
    description: '测试账户',
    status: 'active'
  }
]);

// 根据交易所过滤可用的API密钥
const availableApiKeys = computed(() => {
  if (!formState.exchange) return [];
  return allApiKeys.value.filter(
    api => api.exchange === formState.exchange && api.status === 'active'
  );
});

// 自动生成策略ID
const generateStrategyId = () => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 4; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
};

// 自动生成策略名称
const generateStrategyName = () => {
  if (!formState.baseCurrency || !formState.quoteCurrency) return;
  
  const baseCurr = formState.baseCurrency.toUpperCase();
  const quoteCurr = formState.quoteCurrency.toUpperCase();
  
  let typeName = '';
  let directionName = '';
  let exchangeName = '';
  
  // 获取市场类型名称
  if (formState.marketType) {
    const marketType = marketTypeStore.getActiveMarketTypes.find(t => t.value === formState.marketType);
    if (marketType) typeName = marketType.label;
  }
  
  // 获取方向名称
  if (formState.direction) {
    const direction = directionStore.getActiveDirections.find(d => d.value === formState.direction);
    if (direction) directionName = direction.label;
  }
  
  // 获取交易所名称
  if (formState.exchange) {
    const exchange = exchangeStore.getActiveExchanges.find(e => e.value === formState.exchange);
    if (exchange) exchangeName = exchange.label;
  }
  
  // 构建策略名称
  let name = `${baseCurr}/${quoteCurr}`;
  
  if (typeName) name += `-${typeName}`;
  if (directionName) name += `-${directionName}`;
  if (exchangeName) name += `-${exchangeName}`;
  
  formState.strategyName = name;
};

// 处理输入框变化，自动更新策略名称
const handleInputChange = () => {
  // 如果策略名称为空或之前是自动生成的，则再次自动生成
  if (!formState.strategyName || formState.strategyName.includes('/')) {
    generateStrategyName();
  }
};

// 表单数据
const formState = reactive({
  strategyId: generateStrategyId(),
  exchange: '' as string,
  marketType: '' as string,
  direction: '' as string,
  baseCurrency: '' as string,
  quoteCurrency: '' as string,
  strategyName: '' as string,
  strategyType: 'grid' as string,
  apiKey: null as number | null
});

// 表单验证规则
const rules = {
  exchange: [{ required: true, message: '请选择交易所' }],
  marketType: [{ required: true, message: '请选择产品类型' }],
  direction: [{ required: true, message: '请选择持仓方向' }],
  baseCurrency: [{ required: true, message: '请输入基础币' }],
  quoteCurrency: [{ required: true, message: '请输入计价币' }],
  strategyName: [{ required: true, message: '请输入策略名称' }],
  strategyType: [{ required: true, message: '请选择策略类型' }],
  apiKey: [{ required: true, message: '请选择API密钥' }]
};

// 从Store中获取筛选选项数据
const exchanges = computed(() => exchangeStore.getActiveExchanges);
const marketTypes = computed(() => marketTypeStore.getActiveMarketTypes);
const directions = computed(() => directionStore.getActiveDirections);
const strategyTypes = computed(() => strategyStore.getAllActiveTypes);
const comingSoonStrategies = computed(() => strategyStore.getAllComingSoonTypes);

// 交易对过滤函数
const filterOption = (input: string, option: any) => {
  if (typeof option.label === 'string') {
    return option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0;
  }
  return false;
};

// 交易所变更处理
const handleExchangeChange = () => {
  // 交易所变更时清空API密钥选择
  formState.apiKey = null;
  handleInputChange();
};

// 产品类型变更处理
const handleMarketTypeChange = () => {
  // 可以根据产品类型调整其他相关配置
  handleInputChange();
};

// 持仓方向变更处理
const handleDirectionChange = () => {
  // 可以根据持仓方向调整其他相关配置
  handleInputChange();
};

// 处理即将推出的策略类型点击
const handleComingSoonStrategy = (strategy: any) => {
  message.info(`${strategy.label}功能即将推出，敬请期待！`);
};

// 下一步
const nextStep = async () => {
  try {
    await formRef.value.validate();
    
    // 根据策略类型跳转到对应的模块化组件
    switch (formState.strategyType) {
      case 'grid':
        router.push({
          path: '/strategies/create/grid',
          query: {
            exchange: formState.exchange,
            marketType: formState.marketType,
            direction: formState.direction,
            baseCurrency: formState.baseCurrency,
            quoteCurrency: formState.quoteCurrency,
            strategyName: formState.strategyName,
            strategyType: formState.strategyType,
            strategyId: formState.strategyId
          }
        });
        break;
        
      case 'tv':
        router.push({
          path: '/strategies/create/tv',
          query: {
            exchange: formState.exchange,
            marketType: formState.marketType,
            direction: formState.direction,
            baseCurrency: formState.baseCurrency,
            quoteCurrency: formState.quoteCurrency,
            strategyName: formState.strategyName,
            strategyType: formState.strategyType,
            strategyId: formState.strategyId
          }
        });
        break;
        
      default:
        // 构建交易对
        const pair = formState.baseCurrency && formState.quoteCurrency 
          ? `${formState.baseCurrency}/${formState.quoteCurrency}`
          : undefined;
        
        // 获取从策略参数页保存的参数（如果有）
        const gridType = localStorage.getItem('gridType') || 'arithmetic';
        const upperPrice = localStorage.getItem('upperPrice') || '';
        const lowerPrice = localStorage.getItem('lowerPrice') || '';
        const gridCount = localStorage.getItem('gridCount') || '5';
        const investment = localStorage.getItem('investment') || '1000';
        const gridLevelsData = localStorage.getItem('gridLevelsData') || '';
        
        // 对于其他策略类型或未来扩展，使用旧版页面
        router.push({
          path: `/strategies/create/${formState.strategyType}`,
          query: {
            exchange: formState.exchange,
            marketType: formState.marketType,
            direction: formState.direction,
            baseCurrency: formState.baseCurrency,
            quoteCurrency: formState.quoteCurrency,
            pair: pair,
            strategyName: formState.strategyName,
            strategyType: formState.strategyType,
            strategyId: formState.strategyId,
            // 如果从参数页返回过基本设置，传递保存的参数
            ...(route.query.returnToParams ? {
              gridType,
              upperPrice,
              lowerPrice,
              gridCount,
              investment,
              gridLevelsData
            } : {})
          }
        });
    }
  } catch (error) {
    console.log('validate error', error);
    message.error('请完成表单填写');
  }
};

// 上一步
const goBack = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  } else {
    router.push('/strategies');
  }
};

// 页面加载时，尝试从路由参数中恢复表单状态
onMounted(() => {
  // 从URL参数中恢复表单状态（如果有）
  const { 
    exchange, marketType, direction, strategyType, baseCurrency, quoteCurrency, 
    strategyName, gridType, upperPrice, lowerPrice, gridCount, investment, 
    returnToParams, gridLevelsData 
  } = route.query;
  
  // 只有当明确从参数页返回时，才恢复完整的表单数据
  if (returnToParams === 'true') {
    if (exchange) formState.exchange = exchange as string;
    if (marketType) formState.marketType = marketType as string;
    if (direction) formState.direction = direction as string;
    if (strategyType) formState.strategyType = strategyType as string;
    if (baseCurrency) formState.baseCurrency = baseCurrency as string;
    if (quoteCurrency) formState.quoteCurrency = quoteCurrency as string;
    if (strategyName) formState.strategyName = strategyName as string;
    
    // 保存其他参数供后续使用
    if (gridType) localStorage.setItem('gridType', gridType as string);
    if (upperPrice) localStorage.setItem('upperPrice', upperPrice as string);
    if (lowerPrice) localStorage.setItem('lowerPrice', lowerPrice as string);
    if (gridCount) localStorage.setItem('gridCount', gridCount as string);
    if (investment) localStorage.setItem('investment', investment as string);
    if (gridLevelsData) localStorage.setItem('gridLevelsData', gridLevelsData as string);
  }
  // 如果是普通访问，尝试从localStorage读取之前保存的数据
  else if (exchange) {
    formState.exchange = exchange as string;
    if (marketType) formState.marketType = marketType as string;
    if (direction) formState.direction = direction as string;
    if (strategyType) formState.strategyType = strategyType as string;
    if (baseCurrency) formState.baseCurrency = baseCurrency as string;
    if (quoteCurrency) formState.quoteCurrency = quoteCurrency as string;
    if (strategyName) formState.strategyName = strategyName as string;
  }
});

// 返回策略列表
const returnToStrategyList = () => {
  router.push('/strategies');
};
</script>

<style scoped>
.create-strategy {
  background-color: #f0f2f5;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

.card-title {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.step-container {
  padding: 24px 0;
  max-width: 800px;
  margin: 0 auto;
}

.strategy-form {
  margin-bottom: 24px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.strategy-type-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  width: 100%;
}

:deep(.ant-radio-wrapper-in-form-item) {
  margin-right: 0;
  display: block;
}

:deep(.ant-card) {
  margin: 0;
  border-radius: 0;
}

:deep(.ant-card-head) {
  padding: 0 16px;
}

:deep(.ant-card-body) {
  padding: 16px;
}

/* 单选卡片样式 */
:deep(.strategy-type-group) .ant-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
}

:deep(.strategy-type-group) .ant-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  border-color: #1890ff;
}

:deep(.strategy-type-group) .ant-radio-wrapper-checked .ant-card {
  border-color: #1890ff;
  background-color: #e6f7ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

/* 新增样式 */
.all-strategy-types {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 20px;
  width: 100%;
  margin-top: 10px;
}

.coming-soon-strategies {
  display: contents;
}

.coming-soon-card {
  opacity: 0.7;
  position: relative;
  cursor: not-allowed;
}

.coming-soon-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #ff7875;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.strategy-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.strategy-card .ant-card-meta-title {
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: bold;
}

.strategy-card-container {
  display: flex;
  flex-direction: column;
}

.strategy-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 4px;
  overflow: hidden;
}

:deep(.ant-card-body) {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

:deep(.ant-card-meta) {
  flex: 1;
}

:deep(.ant-card-meta-description) {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}

.selected-strategy {
  border-color: #1890ff;
  background-color: #e6f7ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

:deep(.ant-radio) {
  margin-right: 0;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  margin: 16px 0 24px 0;
  padding: 0;
}

.strategy-steps {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 0;
  padding: 0;
}

.step-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 8px;
}

.step-divider {
  height: 1px;
  background-color: #1890ff;
  flex-grow: 1;
  margin: 0 8px;
}

.step-icon {
  font-size: 18px;
  margin-right: 8px;
  color: #1890ff;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #1890ff;
  color: white;
  font-size: 14px;
  margin-right: 8px;
}

.step-item:not(.active) .step-number {
  background-color: #f0f0f0;
  color: rgba(0, 0, 0, 0.65);
}

.step-text {
  font-size: 14px;
}

.step-item.active .step-text {
  color: #1890ff;
  font-weight: 500;
}
</style> 