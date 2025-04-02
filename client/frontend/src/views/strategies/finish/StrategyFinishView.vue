<template>
  <div class="strategy-view">
    <a-card :bordered="false">
      <template #title>
        <div class="strategy-steps">
          <div class="step-item clickable" @click="goToStep('basic')">
            <check-circle-outlined class="step-icon completed" />
            <span class="step-text">基本设置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item clickable" @click="goToStep('params')">
            <check-circle-outlined class="step-icon completed" />
            <span class="step-text">策略参数</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item clickable" @click="goToStep('risk')">
            <check-circle-outlined class="step-icon completed" />
            <span class="step-text">风控配置</span>
          </div>
          <div class="step-divider"></div>
          <div class="step-item active">
            <div class="step-number">4</div>
            <span class="step-text">完成</span>
          </div>
        </div>
      </template>

      <div class="completion-content">
        <a-result
          status="success"
          title="策略配置完成！"
          sub-title="您可以立即启动策略或返回策略列表"
        >
          <template #extra>
            <a-space>
              <a-button @click="goBack">返回上一步</a-button>
              <a-button @click="goToList">返回列表</a-button>
              <a-button type="primary" @click="startStrategy" :loading="loading">
                立即启动
              </a-button>
            </a-space>
          </template>

          <div class="strategy-summary">
            <h3>策略配置摘要</h3>
            <a-descriptions bordered>
              <a-descriptions-item label="策略名称">
                {{ strategyConfig.name }}
              </a-descriptions-item>
              <a-descriptions-item label="交易所">
                {{ strategyConfig.exchange }}
              </a-descriptions-item>
              <a-descriptions-item label="交易对">
                {{ strategyConfig.pair }}
              </a-descriptions-item>
              <a-descriptions-item label="市场类型">
                {{ strategyConfig.marketType }}
              </a-descriptions-item>
              <a-descriptions-item label="交易方向">
                {{ strategyConfig.direction }}
              </a-descriptions-item>
              
              <!-- 网格策略特有参数 -->
              <template v-if="strategyConfig.strategyType === 'grid'">
                <a-descriptions-item label="网格类型">
                  {{ gridTypeText }}
                </a-descriptions-item>
                <a-descriptions-item label="投资金额">
                  {{ strategyConfig.gridConfig?.investment }} USDT
                </a-descriptions-item>
                <a-descriptions-item label="网格数量">
                  {{ strategyConfig.gridConfig?.gridCount }}
                </a-descriptions-item>
                <a-descriptions-item label="上边界">
                  {{ strategyConfig.gridConfig?.upperPrice }} USDT
                </a-descriptions-item>
                <a-descriptions-item label="下边界">
                  {{ strategyConfig.gridConfig?.lowerPrice }} USDT
                </a-descriptions-item>
              </template>

              <!-- 风控参数 -->
              <a-descriptions-item label="总亏损停止">
                {{ riskConfig?.totalLossLimit || '-' }} USDT
              </a-descriptions-item>
              <a-descriptions-item label="总盈利停止">
                {{ riskConfig?.totalProfitLimit || '-' }} USDT
              </a-descriptions-item>
              <a-descriptions-item label="单笔最大亏损">
                {{ riskConfig?.maxLossPerTrade || '-' }} USDT
              </a-descriptions-item>
            </a-descriptions>
          </div>
        </a-result>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { CheckCircleOutlined } from '@ant-design/icons-vue'
import { useStrategyCreationStore } from '@/store/modules/strategyCreation'
import { useStrategyOperationStore } from '@/store/modules/strategyOperation'

const router = useRouter()
const strategyCreationStore = useStrategyCreationStore()
const strategyOperationStore = useStrategyOperationStore()

const loading = ref(false)

// 获取策略配置
const strategyConfig = computed(() => ({
  name: strategyCreationStore.name,
  strategyType: strategyCreationStore.strategyType,
  exchange: strategyCreationStore.exchange,
  pair: strategyCreationStore.pair,
  marketType: strategyCreationStore.marketType,
  direction: strategyCreationStore.direction,
  gridConfig: strategyCreationStore.gridConfig
}))

// 获取风控配置
const riskConfig = computed(() => strategyCreationStore.riskConfig)

// 网格类型文本
const gridTypeText = computed(() => {
  const typeMap = {
    arithmetic: '等差网格',
    geometric: '等比网格',
    custom: '自定义网格'
  }
  return typeMap[strategyConfig.value.gridConfig?.gridType || 'arithmetic']
})

// 启动策略
const startStrategy = async () => {
  loading.value = true
  try {
    // 检查必要的配置是否存在
    if (!strategyConfig.value.name) {
      throw new Error('策略名称不能为空')
    }
    if (!strategyConfig.value.strategyType) {
      throw new Error('策略类型不能为空')
    }
    if (!strategyConfig.value.exchange) {
      throw new Error('交易所不能为空')
    }
    if (!strategyConfig.value.pair) {
      throw new Error('交易对不能为空')
    }
    if (!strategyConfig.value.marketType) {
      throw new Error('市场类型不能为空')
    }
    if (!strategyConfig.value.direction) {
      throw new Error('交易方向不能为空')
    }
    if (!riskConfig.value) {
      throw new Error('风控配置不能为空')
    }

    // 创建策略
    const strategy = await strategyOperationStore.createStrategy({
      ...strategyConfig.value,
      riskConfig: riskConfig.value
    })
    
    // 启动策略
    if (strategy) {
      await strategyOperationStore.startStrategy(strategy.id)
      message.success('策略已创建并启动')
      router.push('/strategies')
    } else {
      throw new Error('创建策略失败：未返回策略对象')
    }
  } catch (error) {
    console.error('创建策略失败:', error)
    message.error(error instanceof Error ? error.message : '创建策略失败')
  } finally {
    loading.value = false
  }
}

// 返回上一步
const goBack = () => {
  router.push('/strategies/create/risk')
}

// 返回列表
const goToList = () => {
  router.push('/strategies')
}

// 导航到指定步骤
const goToStep = (step: string) => {
  router.push(`/strategies/create/${step}`)
}
</script>

<style scoped>
.strategy-view {
  width: 100%;
  background-color: #f0f2f5;
  margin: 0;
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
  width: 24px;
  height: 24px;
  line-height: 24px;
  border-radius: 50%;
  background-color: rgba(24, 144, 255, 0.1);
  color: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
}

.step-text {
  font-size: 14px;
}

.step-item.active .step-text {
  color: #1890ff;
  font-weight: 500;
}

.step-item.clickable:hover {
  background-color: rgba(24, 144, 255, 0.05);
  border-radius: 4px;
  padding: 2px 4px;
  margin: -2px 4px -2px -4px;
  transition: all 0.3s;
}

.completion-content {
  padding: 24px;
}

.strategy-summary {
  margin-top: 32px;
  text-align: left;
}

.strategy-summary h3 {
  margin-bottom: 16px;
  font-weight: 500;
}

:deep(.ant-descriptions) {
  background-color: #fff;
}

:deep(.ant-descriptions-item-label) {
  width: 120px;
  font-weight: 500;
}
</style> 