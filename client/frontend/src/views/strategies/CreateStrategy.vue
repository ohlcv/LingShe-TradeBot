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
            <span class="step-text">策略风控</span>
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
          <!-- 第一行：策略ID和策略名称 -->
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="策略ID" name="strategyId">
                <a-input 
                  v-model:value="formState.strategyId"
                  placeholder="系统自动生成"
                  disabled
                />
                <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">策略ID为系统自动生成的唯一标识</div>
              </a-form-item>
            </a-col>
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
          </a-row>
          
          <!-- 第二行：账户选择 -->
          <a-row :gutter="24">
            <a-col :span="24">
              <a-form-item label="账户名称" name="accountName">
                <a-select
                  v-model:value="formState.accountName"
                  placeholder="请选择账户"
                  @change="handleAccountChange"
                  :loading="loadingApiKeys"
                >
                  <template #notFoundContent>
                    <div v-if="!loadingApiKeys && allAccounts.length === 0">
                      <p style="padding: 8px 0;">未找到可用的账户</p>
                      <p style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">
                        请先在<router-link to="/exchange">交易所管理</router-link>页添加账户
                      </p>
                    </div>
                    <a-spin v-else size="small" />
                  </template>
                  <a-select-option v-for="account in allAccounts" :key="account" :value="account">
                    {{ account }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          
          <!-- 第三行：交易所和产品类型 -->
          <a-row :gutter="24">
            <!-- 交易所选择 -->
            <a-col :span="12">
              <a-form-item label="交易所" name="exchange">
                <a-select
                  v-model:value="formState.exchange"
                  placeholder="请选择交易所"
                  @change="handleExchangeChange"
                  :disabled="!formState.accountName"
                >
                  <template #notFoundContent>
                    <div v-if="!loadingApiKeys && formState.accountName && availableExchanges.length === 0">
                      <p style="padding: 8px 0;">当前账户下未找到可用的交易所</p>
                      <p style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">
                        请先在<router-link to="/exchange">交易所管理</router-link>页为该账户添加交易所API
                      </p>
                    </div>
                    <a-empty v-else-if="!formState.accountName" description="请先选择账户" />
                    <a-spin v-else size="small" />
                  </template>
                  <a-select-option v-for="exchange in availableExchanges" :key="exchange.value" :value="exchange.value">
                    {{ exchange.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            
            <!-- 产品类型选择 -->
            <a-col :span="12">
              <a-form-item label="产品类型" name="marketType">
                <a-select
                  v-model:value="formState.marketType"
                  placeholder="请选择产品类型"
                  @change="handleMarketTypeChange"
                  :disabled="!formState.exchange"
                >
                  <a-select-option v-for="type in availableMarketTypes" :key="type.value" :value="type.value">
                    {{ type.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          
          <!-- 第四行：API密钥和交易对 -->
          <a-row :gutter="24">
            <!-- API密钥选择 -->
            <a-col :span="12">
              <a-form-item label="API密钥" name="apiKey">
                <a-select
                  v-model:value="formState.apiKey"
                  placeholder="请选择API密钥"
                  :disabled="!formState.exchange || !formState.marketType"
                  :loading="loadingApiKeys"
                >
                  <template #notFoundContent>
                    <div v-if="!loadingApiKeys && formState.exchange && formState.marketType && filteredApiKeys.length === 0">
                      <p style="padding: 8px 0;">未找到可用的API密钥</p>
                      <p style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">
                        请先在<router-link to="/exchange">交易所管理</router-link>页添加并验证交易所API
                      </p>
                    </div>
                    <a-empty v-else-if="!formState.exchange" description="请先选择交易所" />
                    <a-empty v-else-if="!formState.marketType" description="请先选择产品类型" />
                    <a-spin v-else size="small" />
                  </template>
                  <a-select-option v-for="api in filteredApiKeys" :key="api.id" :value="api.id">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                      <span>{{ api.connector_name }}</span>
                      <a-tag :color="api.status === 'connected' ? 'success' : (api.status === 'pending' ? 'warning' : 'error')">
                        {{ api.status === 'connected' ? '已验证' : (api.status === 'pending' ? '待验证' : '验证失败') }}
                      </a-tag>
                    </div>
                  </a-select-option>
                </a-select>
                <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">
                  选择用于此策略的API密钥（建议使用已验证的密钥）
                </div>
              </a-form-item>
            </a-col>
            
            <!-- 交易对选择 -->
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
          
          <!-- 第五行：持仓方向（仅合约显示） -->
          <a-row :gutter="24" v-if="formState.marketType === 'futures'">
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
            
            <!-- 杠杆倍数（仅合约显示） -->
            <a-col :span="12">
              <a-form-item label="杠杆倍数" name="leverage">
                <a-input-number
                  v-model:value="formState.leverage"
                  :min="1"
                  :max="maxLeverageForExchange"
                  :step="1"
                  style="width: 100%"
                  placeholder="请输入杠杆倍数"
                />
                <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">
                  当前交易所最大支持 {{ maxLeverageForExchange }}x 杠杆
                </div>
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
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message, Form } from 'ant-design-vue';
import { http } from '../../api/client';
import {
  AppstoreOutlined,
  LineChartOutlined,
  PartitionOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  TeamOutlined,
  SwapOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue';
import { useStrategyStore } from '../../store/modules/strategy';
import { useExchangeStore } from '../../store/modules/exchange';
import { useMarketTypeStore } from '../../store/modules/marketType';
import { useDirectionStore } from '../../store/modules/direction';
import { useExchangeConfigStore } from '../../store/modules/exchangeConfig';
import { getConnectorKeys } from '../../api/services/exchange';
import { exchanges } from '../../config/exchangeConfig';
import { Exchange, ProductType } from '../../types/exchange';

const router = useRouter();
const route = useRoute();
const formRef = ref<typeof Form>();
const currentStep = ref(0);

// 加载各个Store
const strategyStore = useStrategyStore();
const exchangeStore = useExchangeStore();
const marketTypeStore = useMarketTypeStore();
const directionStore = useDirectionStore();
const exchangeConfigStore = useExchangeConfigStore();

// 修正后的API密钥接口
interface ApiKey {
  id: string;
  exchange: string;
  productType?: string;
  name: string;
  account_name: string;
  connector_name: string;
  trading_type?: string[];
  status: 'connected' | 'pending' | 'error';
  type?: 'CEX' | 'DEX';
}

// API密钥列表，从API获取
const allApiKeys = ref<ApiKey[]>([]);
const loadingApiKeys = ref(false);

// 新增账户相关变量
const allAccounts = ref<string[]>([]);
const loadingAccounts = ref(false);

// 获取所有账户和API密钥
const fetchApiKeys = async () => {
  loadingApiKeys.value = true;
  loadingAccounts.value = true;
  
  try {
    // 模拟API调用 - 使用模拟数据代替实际API调用
    const mockConnectors = [
      {
        account_name: "default",
        connector: "binance_perpetual",
        trading_enabled: true,
        trading_type: ["perp"]
      },
      {
        account_name: "default",
        connector: "binance",
        trading_enabled: true,
        trading_type: ["spot"]
      },
      {
        account_name: "test_account",
        connector: "okx_perpetual",
        trading_enabled: true,
        trading_type: ["perp"]
      },
      {
        account_name: "test_account",
        connector: "okx",
        trading_enabled: false,
        trading_type: ["spot"]
      }
    ];
    
    // 处理模拟连接器数据
    allApiKeys.value = mockConnectors.map((c: any) => {
      const exchangeName = c.connector.split('_')[0]; // 简化的方式获取交易所名称
      const productType = c.connector.includes('_perpetual') ? 'perpetual' : 'spot';
      const exchangeObj = exchanges.find(e => e.name === exchangeName);
      
      return {
        id: `${c.account_name}-${c.connector}`,
        exchange: exchangeName,
        productType,
        name: `${c.account_name} (${exchangeObj?.label || exchangeName}-${productType === 'perpetual' ? '永续合约' : '现货'})`,
        account_name: c.account_name,
        connector_name: c.connector,
        trading_type: c.trading_type || [],
        status: c.trading_enabled ? 'connected' : 'pending',
        type: exchangeObj?.type || 'CEX',
      };
    });
    
    console.log('API密钥列表获取成功', allApiKeys.value);
    
    // 从API密钥中提取唯一的账户名
    allAccounts.value = Array.from(new Set(allApiKeys.value.map(key => key.account_name)));
    console.log('可用账户:', allAccounts.value);
    
  } catch (error) {
    console.error('获取API密钥失败', error);
    message.error('获取API密钥失败，请检查网络连接');
    allApiKeys.value = [];
    allAccounts.value = [];
  } finally {
    loadingApiKeys.value = false;
    loadingAccounts.value = false;
  }
};

// 自动生成策略ID
const generateStrategyId = () => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 8; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
};

// 表单数据
const formState = reactive({
  strategyId: generateStrategyId(),
  strategyName: '',
  strategyType: 'grid',
  accountName: '',  // 新增账户字段
  exchange: '',
  marketType: '',
  direction: 'long',
  baseCurrency: '',
  quoteCurrency: '',
  apiKey: null,
  leverage: 1,
  stopLoss: null,
  takeProfit: null,
  additionalParams: {} as Record<string, string>
});

// 表单验证规则
const rules = computed(() => {
  const baseRules: Record<string, any> = {
    accountName: [{ required: true, message: '请选择账户' }],
    exchange: [{ required: true, message: '请选择交易所' }],
    marketType: [{ required: true, message: '请选择产品类型' }],
    baseCurrency: [{ required: true, message: '请输入基础币' }],
    quoteCurrency: [{ required: true, message: '请输入计价币' }],
    strategyName: [{ required: true, message: '请输入策略名称' }],
    strategyType: [{ required: true, message: '请选择策略类型' }],
    apiKey: [{ required: true, message: '请选择API密钥' }],
  };
  
  // 仅在期货交易时需要持仓方向和杠杆倍数
  if (formState.marketType === 'futures') {
    baseRules.direction = [{ required: true, message: '请选择持仓方向' }];
    baseRules.leverage = [{ required: true, message: '请输入杠杆倍数' }];
  }
  
  return baseRules;
});

// 从Store中获取筛选选项数据
const marketTypes = computed(() => marketTypeStore.getActiveMarketTypes);
const directions = computed(() => directionStore.getActiveDirections);
const strategyTypes = computed(() => strategyStore.getAllActiveTypes);
const comingSoonStrategies = computed(() => strategyStore.getAllComingSoonTypes);

// 修改获取可用市场类型的计算属性
const availableMarketTypes = computed(() => {
  if (!formState.exchange) return marketTypeStore.getActiveMarketTypes;
  
  const exchange = exchanges.find((e: Exchange) => e.name === formState.exchange);
  if (!exchange) return marketTypeStore.getActiveMarketTypes;
  
  // 将交易所配置中的产品类型映射到市场类型
  const supportedTypes = exchange.productTypes.map((pt: ProductType) => 
    pt.value === 'perpetual' ? 'futures' : pt.value
  );
  
  return marketTypeStore.getActiveMarketTypes.filter(type => 
    supportedTypes.includes(type.value)
  );
});

// 在用户选择账户时可用的交易所
const availableExchanges = ref<Exchange[]>([]);

// 根据交易所过滤可用的API密钥
const filteredApiKeys = computed(() => {
  if (!formState.accountName || !formState.exchange || !formState.marketType || !allApiKeys.value.length) 
    return [];
  
  // 根据选择的产品类型确定连接器后缀
  const connectorSuffix = formState.marketType === 'futures' ? '_perpetual' : '';
  const connectorPrefix = formState.exchange;
  
  // 构建完整连接器名称
  const fullConnectorName = connectorPrefix + connectorSuffix;
  
  return allApiKeys.value.filter(api => 
    api.account_name === formState.accountName &&
    api.connector_name.toLowerCase() === fullConnectorName.toLowerCase() && 
    (api.status === 'connected' || api.status === 'pending')
  );
});

// 交易对过滤函数
const filterOption = (input: string, option: any) => {
  if (typeof option.label === 'string') {
    return option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0;
  }
  return false;
};

// 处理账户变更
const handleAccountChange = () => {
  // 账户变更时清空交易所和API密钥选择
  formState.exchange = '';
  formState.marketType = '';
  formState.apiKey = null;
  formState.leverage = 1;
  
  handleInputChange();
};

// 修改 handleExchangeChange 函数
const handleExchangeChange = () => {
  // 交易所变更时清空API密钥选择
  formState.apiKey = null;
  formState.marketType = '';
  
  handleInputChange();
};

// 产品类型变更处理
const handleMarketTypeChange = () => {
  // 清空API密钥选择
  formState.apiKey = null;
  
  // 如果是合约市场，更新最大杠杆倍数
  if (formState.marketType === 'futures') {
    // 可以设置默认杠杆倍数
    formState.leverage = 1;
  } else {
    formState.leverage = 1;
  }
  
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

// 在开始创建策略前验证表单
const validateForm = async () => {
  try {
    // 合并基本规则和额外参数规则
    const mergedRules = { ...rules.value, ...getAdditionalParamsRules.value };
    if (formRef.value) {
      await formRef.value.validate(mergedRules);
      return true;
    }
    return false;
  } catch (error) {
    console.error('表单验证失败', error);
    return false;
  }
};

// 下一步按钮处理
const nextStep = async () => {
  if (currentStep.value === 0) {
    // 在基本设置步骤，验证表单
    const valid = await validateForm();
    if (!valid) {
      message.error('请完成表单填写');
      return;
    }
    
    // 表单验证通过后，根据策略类型跳转到对应的模块化组件
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
            strategyId: formState.strategyId,
            leverage: formState.marketType === 'futures' ? formState.leverage.toString() : '1',
            apiKey: formState.apiKey,
            // 不再传递额外参数
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
            strategyId: formState.strategyId,
            leverage: formState.marketType === 'futures' ? formState.leverage.toString() : '1',
            apiKey: formState.apiKey,
            // 不再传递额外参数
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
            leverage: formState.marketType === 'futures' ? formState.leverage.toString() : '1',
            apiKey: formState.apiKey,
            // 不再传递额外参数
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
  } else if (currentStep.value < 3) {
    // 其他步骤直接前进
    currentStep.value += 1;
  } else {
    // 最后一步完成创建
    router.push('/strategies');
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

// 页面加载时初始化数据
onMounted(async () => {
  // 获取支持的交易所配置
  try {
    await Promise.all([
      exchangeConfigStore.fetchSupportedExchanges(),
      fetchApiKeys() // 获取API密钥列表
    ]);
  } catch (error) {
    console.error('初始化数据失败', error);
    message.error('初始化数据失败，部分功能可能不可用');
  }
  
  // 从URL参数中恢复表单状态（如果有）
  const { 
    exchange, marketType, direction, strategyType, baseCurrency, quoteCurrency, 
    strategyName, gridType, upperPrice, lowerPrice, gridCount, investment, 
    returnToParams, gridLevelsData, leverage
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
    
    // 处理杠杆设置
    if (leverage && marketType === 'futures') {
      formState.leverage = parseInt(leverage as string) || 1;
    }
    
    // 处理额外参数
    formState.additionalParams = {};
    // 查找所有以 param_ 开头的查询参数，并将其解析为额外参数
    Object.entries(route.query).forEach(([key, value]) => {
      if (key.startsWith('param_') && typeof value === 'string') {
        const paramName = key.replace('param_', '');
        formState.additionalParams[paramName] = value;
      }
    });
    
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
    
    // 处理杠杆设置
    if (leverage && marketType === 'futures') {
      formState.leverage = parseInt(leverage as string) || 1;
    }
    
    // 处理额外参数
    formState.additionalParams = {};
    // 查找所有以 param_ 开头的查询参数，并将其解析为额外参数
    Object.entries(route.query).forEach(([key, value]) => {
      if (key.startsWith('param_') && typeof value === 'string') {
        const paramName = key.replace('param_', '');
        formState.additionalParams[paramName] = value;
      }
    });
  }
});

// 返回策略列表
const returnToStrategyList = () => {
  router.push('/strategies');
};

// 修改根据交易所获取最大杠杆倍数的计算属性
const maxLeverageForExchange = computed(() => {
  if (!formState.exchange || formState.marketType !== 'futures') return 20;
  
  const exchange = exchanges.find((e: Exchange) => e.name === formState.exchange);
  if (!exchange) return 20;
  
  // 尝试从交易所配置中获取最大杠杆，或使用默认值
  const perpetualProductType = exchange.productTypes.find((pt: ProductType) => pt.value === 'perpetual');
  if (perpetualProductType && (perpetualProductType as any).maxLeverage) {
    return (perpetualProductType as any).maxLeverage;
  }
  
  // 根据交易所设置默认最大杠杆
  switch (formState.exchange) {
    case 'binance':
      return 125;
    case 'bybit':
      return 100;
    case 'okx':
      return 125;
    case 'gate_io':
      return 100;
    case 'bitget':
      return 125;
    default:
      return 20;
  }
});

// 获取交易所额外参数
const additionalExchangeParams = computed(() => {
  return exchangeConfigStore.getAdditionalParamsByExchange(formState.exchange);
});

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

// 动态生成额外参数的验证规则
const getAdditionalParamsRules = computed(() => {
  const additionalRules: Record<string, any> = {};
  
  if (formState.exchange) {
    const params = exchangeConfigStore.getAdditionalParamsByExchange(formState.exchange);
    params.forEach(param => {
      if (param.required) {
        additionalRules[`additionalParams.${param.name}`] = [
          { required: true, message: `请输入${param.label}` }
        ];
      }
    });
  }
  
  return additionalRules;
});
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

.additional-params-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.85);
}
</style> 