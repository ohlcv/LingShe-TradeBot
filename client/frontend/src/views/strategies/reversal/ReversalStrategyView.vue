<template>
  <div class="strategy-view">
    <a-card :bordered="false">
      <template #title>
        <div class="card-title">
          <h2>反转策略设置</h2>
          <a-steps :current="1" size="small" style="max-width: 600px;" class="nav-steps">
            <a-step>
              <template #title>
                <span class="clickable-step" @click="goToStep('basic')">基本设置</span>
              </template>
            </a-step>
            <a-step>
              <template #title>
                <span>策略参数</span>
              </template>
            </a-step>
            <a-step>
              <template #title>
                <span class="clickable-step" @click="goToStep('risk')">风控配置</span>
              </template>
            </a-step>
            <a-step>
              <template #title>
                <span class="clickable-step" @click="goToStep('finish')">完成</span>
              </template>
            </a-step>
          </a-steps>
        </div>
      </template>

      <a-form
        :model="reversalForm"
        ref="formRef"
        layout="vertical"
        class="strategy-form"
      >
        <a-result
          status="info"
          title="反转策略正在开发中"
          sub-title="我们正在开发反转策略的模块化组件，敬请期待！"
          style="text-align: center; margin: 40px 0;"
        >
          <template #extra>
            <a-button type="primary" @click="goBack">返回上一步</a-button>
            <a-button @click="goToOldComponent">使用旧版界面</a-button>
          </template>
        </a-result>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';

const router = useRouter();
const route = useRoute();
const formRef = ref();

// 从URL获取基础参数
const exchange = route.query.exchange as string;
const marketType = route.query.marketType as string;
const direction = route.query.direction as string;
const baseCurrency = route.query.baseCurrency as string;
const quoteCurrency = route.query.quoteCurrency as string;
const strategyNameFromQuery = route.query.strategyName as string;

// 初始化表单数据
const reversalForm = reactive({
  // 基本信息
  name: strategyNameFromQuery || `${baseCurrency || ''}${direction === 'long' ? '做多' : direction === 'short' ? '做空' : ''}反转`,
  
  // 指标设置
  primaryIndicator: 'rsi',
  rsiPeriod: 14,
  overboughtThreshold: 70,
  oversoldThreshold: 30,
  bollingerPeriod: 20,
  bollingerDeviation: 2,
  secondaryIndicator: 'none',
  emaShortPeriod: 9,
  emaLongPeriod: 21,
  
  // 交易设置
  confirmationCandles: 2,
  takeProfitRatio: 5.0,
  stopLossRatio: 2.0,
  trailingProfit: true,
  trailingProfitRatio: 1.0,
  
  // 高级设置
  timeframe: '15m',
  trendFilter: false,
  trendTimeframe: '4h',
  trendMethod: 'ema'
});

// 导航到其他步骤
const goToStep = (step: string) => {
  if (step === 'basic') {
    goBack();
  } else if (step === 'risk') {
    router.push({
      path: '/strategies/create/risk',
      query: route.query
    });
  } else if (step === 'finish') {
    router.push({
      path: '/strategies',
    });
  }
};

// 判断时间周期是否小于等于当前选择的周期
const isTimeframeSmallerOrEqual = (tf: string) => {
  const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];
  const currentIndex = timeframes.indexOf(reversalForm.timeframe);
  const comparedIndex = timeframes.indexOf(tf);
  return currentIndex >= comparedIndex;
};

// 监听timeframe变化，自动调整trendTimeframe
watch(() => reversalForm.timeframe, (newVal) => {
  if (reversalForm.trendFilter) {
    const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];
    const currentIndex = timeframes.indexOf(newVal);
    
    // 如果当前趋势周期小于等于K线周期，自动调整为更大的周期
    if (isTimeframeSmallerOrEqual(reversalForm.trendTimeframe)) {
      for (let i = currentIndex + 1; i < timeframes.length; i++) {
        reversalForm.trendTimeframe = timeframes[i];
        break;
      }
    }
  }
});

// 返回上一步
const goBack = () => {
  router.push({ 
    path: '/strategies/create', 
    query: {
      ...route.query,
      returnToParams: 'true'
    }
  });
};

// 使用旧组件
const goToOldComponent = () => {
  router.push({
    path: `/strategies/create/reversal`,
    query: {
      ...route.query,
      useOldComponent: 'true'
    }
  });
};

// 下一步
const nextStep = async () => {
  try {
    await formRef.value.validate();
    // 验证通过，保存设置并进入下一步
    router.push({
      path: '/strategies/create/risk',
      query: {
        exchange: exchange,
        marketType: marketType,
        direction: direction,
        baseCurrency: baseCurrency,
        quoteCurrency: quoteCurrency,
        strategyName: reversalForm.name,
        strategyType: 'reversal',
        // 保存反转策略特有参数
        primaryIndicator: reversalForm.primaryIndicator,
        takeProfitRatio: reversalForm.takeProfitRatio.toString(),
        stopLossRatio: reversalForm.stopLossRatio.toString(),
        timeframe: reversalForm.timeframe
      }
    });
  } catch (error) {
    console.error('表单验证失败', error);
    message.error('请填写完整的策略配置信息');
  }
};
</script>

<style scoped>
.strategy-view {
  width: 100%;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.card-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.clickable-step {
  cursor: pointer;
  color: #1890ff;
}

.settings-card {
  margin-bottom: 16px;
}

.form-hint {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  margin-top: 4px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}
</style> 