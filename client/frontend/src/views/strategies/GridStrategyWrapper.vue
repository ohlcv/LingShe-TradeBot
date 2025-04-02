<template>
  <div class="grid-strategy-wrapper">
    <a-result
      status="success"
      title="模块化网格策略已准备好!"
      sub-title="我们已经完成了网格策略组件的模块化改造，但目前仍有一些类型错误需要修复。此过渡页面将引导您回到原始策略设置页面。"
    >
      <template #extra>
        <a-button type="primary" @click="goToDevelopment">
          继续开发
        </a-button>
        <a-button @click="goBack">
          返回上一步
        </a-button>
        <a-button type="dashed" @click="goToOriginal">
          使用原始版本
        </a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// 继续开发新版本
const goToDevelopment = () => {
  router.push({
    path: '/strategies/create/risk',
    query: {
      ...route.query,
      message: 'grid_modular_development'
    }
  });
};

// 回到上一步
const goBack = () => {
  router.push({ 
    path: '/strategies/create', 
    query: {
      ...route.query,
      returnToParams: 'true'
    }
  });
};

// 使用原始版本
const goToOriginal = () => {
  // 导航到原始的StrategySettings页面，添加标记使用旧组件
  router.push({
    path: `/strategies/create/grid`,
    query: {
      ...route.query,
      useOldComponent: 'true'
    }
  });
};
</script>

<style scoped>
.grid-strategy-wrapper {
  padding: 24px;
  background: #fff;
  border-radius: 4px;
}
</style> 