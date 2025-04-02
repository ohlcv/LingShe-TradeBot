<template>
  <div class="home">
    <h2>首页</h2>
    <p>欢迎使用LingShe TradeBot</p>
    <Button type="primary" @click="goToLogin">登录/注册</Button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from 'ant-design-vue'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.home {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
</style> 