# 组件使用文档

## 简介
本文档介绍了系统中使用的 Ant Design Vue 组件库的使用方法。所有组件都直接从 ant-design-vue 导入，通过自动导入功能自动注册。

## 使用方式

### 1. 基础组件
```vue
<script setup lang="ts">
import { Button, Input, Form } from 'ant-design-vue'
</script>

<template>
  <Form>
    <Form.Item>
      <Input />
    </Form.Item>
    <Button type="primary">提交</Button>
  </Form>
</template>
```

### 2. 直接使用组件 (自动导入)
```vue
<script setup lang="ts">
// 无需导入，通过unplugin-vue-components自动导入
</script>

<template>
  <a-form>
    <a-form-item>
      <a-input />
    </a-form-item>
    <a-button type="primary">提交</a-button>
  </a-form>
</template>
```

## 常用组件示例

### 表单组件
```vue
<template>
  <a-form :model="formState" @finish="onFinish">
    <a-form-item label="用户名" name="username">
      <a-input v-model:value="formState.username" />
    </a-form-item>
    <a-form-item label="密码" name="password">
      <a-input-password v-model:value="formState.password" />
    </a-form-item>
    <a-form-item>
      <a-button type="primary" html-type="submit">提交</a-button>
    </a-form-item>
  </a-form>
</template>
```

### 表格组件
```vue
<template>
  <a-table :columns="columns" :data-source="data">
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'action'">
        <a-space>
          <a-button type="link">编辑</a-button>
          <a-button type="link" danger>删除</a-button>
        </a-space>
      </template>
    </template>
  </a-table>
</template>
```

### 模态框组件
```vue
<template>
  <a-modal
    v-model:visible="visible"
    title="确认操作"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <p>确定要执行此操作吗？</p>
  </a-modal>
</template>
```

## 组件规范

### 1. 命名规范
- 自动导入的组件使用前缀a- (如 a-button、a-input)
- 在脚本中使用的组件直接从ant-design-vue导入

### 2. 属性规范
- 使用 v-model:value 进行双向绑定
- 使用 @finish 而不是 @submit 处理表单提交
- 使用 :model 而不是 :form 绑定表单数据

### 3. 样式规范
- 优先使用组件库提供的样式
- 自定义样式使用 scoped 或 CSS Modules
- 遵循 BEM 命名规范

## 注意事项

1. 组件导入
   - 模板中使用的组件无需导入（自动导入）
   - JS/TS中使用的组件需从 ant-design-vue 导入

2. 类型使用
   - 使用组件库提供的类型定义
   - 自定义类型继承自组件库类型

3. 性能优化
   - 合理使用 v-show 和 v-if
   - 避免不必要的组件重渲染
   - 使用计算属性优化数据转换

4. 错误处理
   - 使用 try-catch 处理异步操作
   - 统一使用 message 组件显示错误信息

## 常见问题

1. 组件不显示
   - 检查组件名称是否正确
   - 检查组件属性是否正确

2. 样式问题
   - 检查样式是否被覆盖
   - 检查样式作用域是否正确
   - 检查主题配置是否正确

3. 类型错误
   - 检查类型定义是否正确
   - 检查属性类型是否匹配
   - 检查事件处理函数类型 