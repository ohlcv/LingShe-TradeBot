<template>
  <div class="style-load-test">
    <h2>样式按需加载测试</h2>
    <div class="component-row">
      <a-button type="primary">主要按钮</a-button>
      <a-button>默认按钮</a-button>
      <a-button type="dashed">虚线按钮</a-button>
      <a-button type="link">链接按钮</a-button>
    </div>
    
    <div class="component-row">
      <a-alert message="成功提示" type="success" show-icon />
      <a-alert message="警告提示" type="warning" show-icon />
      <a-alert message="错误提示" type="error" show-icon />
    </div>
    
    <div class="component-row">
      <a-card title="卡片测试" style="width: 300px;">
        <p>Card content</p>
        <p>Card content</p>
      </a-card>
    </div>
    
    <div class="component-row">
      <a-date-picker />
      <a-range-picker />
    </div>
    
    <div class="component-row">
      <a-table :columns="columns" :data-source="data" :pagination="false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const columns = [
  {
    title: '姓名',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '年龄',
    dataIndex: 'age',
    key: 'age',
  }
];

const data = ref([
  {
    key: '1',
    name: '张三',
    age: 32
  },
  {
    key: '2',
    name: '李四',
    age: 42
  }
]);
</script>

<style scoped lang="less">
.style-load-test {
  padding: 24px;
  background-color: #fff;
  
  h2 {
    margin-bottom: 20px;
    color: @primary-color; // 使用自定义主题中的变量
  }
  
  .component-row {
    margin-bottom: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: flex-start;
  }
}
</style> 