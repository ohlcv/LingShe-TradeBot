# LingShe Trade Bot - 前端

灵蛇交易机器人的前端项目，基于Vue 3 + TypeScript + Ant Design Vue开发。

## 开发进度

### 已完成功能
- 用户登录/注册
- 交易所管理
- 策略创建和管理
- 交易记录查询
- 风控设置
- 账户管理
- 通知中心

### 正在开发
- 网格策略模块化改造：已创建基础组件，但仍存在类型错误需要修复
  - ✅ 总体配置组件 (GridGeneralConfig)
  - ✅ 网格层级表格 (GridLevelTable)
  - ✅ 网格可视化 (GridVisualization)
  - ✅ 阶梯设置模态框 (LadderSettingsModal)
  - ✅ 整合的网格策略组件 (GridStrategy)
  - ❗ 修复类型错误和函数实现

## 快速开始

### 安装依赖
```bash
npm install
```

### 开发模式启动
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 网格策略模块化改造说明

原来的网格策略实现在`StrategySettings.vue`文件中，代码量大、结构复杂，不易维护。我们将其重构为以下模块化结构：

### 组件结构
- `GridGeneralConfig.vue`: 总体配置组件，包括网格类型、投资金额、网格数量等基础设置
- `GridLevelTable.vue`: 网格层级表格，展示和编辑网格层级信息
- `GridVisualization.vue`: 网格可视化组件，直观展示网格分布和当前价格
- `LadderSettingsModal.vue`: 阶梯设置模态框，用于配置阶梯止盈参数
- `GridStrategy.vue`: 整合以上组件的主组件

### 工具函数
在`utils.ts`中实现了多个网格策略相关的工具函数，如计算均价、生成网格层级等。

### 类型定义
在`types.ts`中定义了网格策略相关的接口和类型。

### 路由设置
修改了路由配置，使用路由守卫在访问网格策略时自动重定向到新组件，同时保留了使用旧组件的选项。

### 后续开发计划
1. 修复`GridStrategy.vue`中的类型错误
2. 完善网格可视化组件的交互功能
3. 实现数据持久化和与后端的通信
4. 添加更多单元测试

### 如何切换新旧组件
- 默认情况下，系统会自动使用新的模块化组件
- 如需使用原始组件，可在URL中添加`useOldComponent=true`参数
- 也可以在过渡页面点击"使用原始版本"按钮

## 项目结构
- `src/components/strategies/grid`: 网格策略相关组件
- `src/utils`: 工具函数
- `src/views`: 页面组件
- `src/router`: 路由配置
- `src/store`: 状态管理
- `src/api`: API接口 