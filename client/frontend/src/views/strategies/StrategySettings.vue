<template>
  <div>
    <a-spin v-if="loading" tip="Loading..." size="large" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const loading = ref(true);

// 根据策略类型重定向到适当的组件
onMounted(() => {
  const { type } = route.params;
  const query = { ...route.query, useOldComponent: 'true' };
  
  // 根据策略类型重定向
  switch (type) {
    case 'grid':
      router.replace({ path: '/strategies/grid', query });
      break;
    case 'trend':
      router.replace({ path: '/strategies/trend', query });
      break;
    case 'scalping':
      router.replace({ path: '/strategies/scalping', query });
      break;
    case 'reversal':
      router.replace({ path: '/strategies/reversal', query });
      break;
    case 'news':
      router.replace({ path: '/strategies/news', query });
      break;
    case 'copy':
      router.replace({ path: '/strategies/copy', query });
      break;
    case 'risk':
      router.replace({ path: '/strategies/create/risk', query });
      break;
    case 'tv':
      router.replace({ path: '/strategies/tv', query });
      break;
    default:
      // 如果找不到对应的组件，重定向到创建策略页面
      router.replace({ path: '/strategies/create', query });
      break;
  }
});
</script>

<style scoped>
/* 加载状态的样式 */
:deep(.ant-spin) {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style> 