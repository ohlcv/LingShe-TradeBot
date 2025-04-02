<template>
  <div class="strategy-view">
    <a-card :bordered="false">
      <template #title>
        <div class="card-title">
          <h2>趋势策略设置</h2>
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

      <a-result
        status="info"
        title="趋势策略正在开发中"
        sub-title="我们正在开发趋势策略的模块化组件，敬请期待！"
      >
        <template #extra>
          <a-button type="primary" @click="goBack">返回上一步</a-button>
          <a-button @click="goToOldComponent">使用旧版界面</a-button>
        </template>
      </a-result>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

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
    path: `/strategies/create/trend`,
    query: {
      ...route.query,
      useOldComponent: 'true'
    }
  });
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
</style> 