# LingShe-TradeBot 功能与API需求总结

## 系统功能概述

基于对现有代码和文档的分析，LingShe-TradeBot是一个加密货币交易机器人系统，提供自动化网格交易、风控管理和账户管理功能。以下是系统主要功能模块和对应的API需求。
我的UI在用户管理页API设置里可以先提前让用户创建多个交易所的多个api保存，在策略列表页可以动态创建启动停止删除多个策略，在策略创建页里可以选择具体交易所api交易对命名，有多个策略可供选择，每个策略的具体设置都不同，比如我的网格策略可以随时修改每一层的参数非常灵活，并且每个策略可以单独设置一些风控，随时可改。

## 1. 网格策略管理

### 核心功能
- 策略基本信息设置
- 网格级别配置
- 开仓参数设置
- 止盈策略配置
- 风控参数配置
- 策略执行与监控

### API需求
1. **策略管理API**
   - `GET /api/strategies` - 获取策略列表
   - `POST /api/strategies` - 创建新策略
   - `GET /api/strategies/:id` - 获取策略详情
   - `PUT /api/strategies/:id` - 更新策略配置
   - `DELETE /api/strategies/:id` - 删除策略
   - `POST /api/strategies/:id/start` - 启动策略
   - `POST /api/strategies/:id/stop` - 停止策略
   - `POST /api/strategies/:id/pause` - 暂停策略

2. **网格配置API**
   - `GET /api/strategies/:id/grid` - 获取网格配置
   - `PUT /api/strategies/:id/grid` - 更新网格配置
   - `POST /api/strategies/:id/grid/auto-generate` - 自动生成网格

## 2. 风控管理

### 核心功能
- 系统级风控条件设置（最大持仓币种数、最大持仓价值、最大亏损停止）
- 账户安全风控（单位时间最大亏损限制）
- 市场风险风控（价格波动监控、流动性监控）
- 技术风控（API响应监控、连接状态监控）
- 时间风控（交易时间限制、重要时间点管理）
- 风控历史记录查询

### API需求
1. **风控配置API**
   - `GET /api/risk/settings` - 获取风控配置
   - `PUT /api/risk/settings` - 更新风控配置
   - `POST /api/risk/reset` - 重置风控配置为默认值
   - `POST /api/risk/emergency-stop` - 紧急停止所有交易

2. **时间风控API**
   - `GET /api/risk/time-points` - 获取禁止交易时间点
   - `POST /api/risk/time-points` - 添加新的禁止交易时间点
   - `PUT /api/risk/time-points/:id` - 更新时间点
   - `DELETE /api/risk/time-points/:id` - 删除时间点

3. **风控历史API**
   - `GET /api/risk/history` - 获取风控触发历史
   - `GET /api/risk/stats` - 获取当前风控状态数据（持仓数、总价值、当前亏损等）

## 3. 账户管理

### 核心功能
- 个人信息管理
- API密钥管理（添加、启用/禁用、删除）
- 安全设置（密码修改、双因素认证、登录提醒）
- 通知设置（交易通知、风控预警、系统公告）

### API需求
1. **用户账户API**
   - `GET /api/user/profile` - 获取用户信息
   - `PUT /api/user/profile` - 更新用户信息
   - `PUT /api/user/password` - 修改密码
   - `PUT /api/user/security` - 更新安全设置

2. **API密钥管理API**
   - `GET /api/user/api-keys` - 获取API密钥列表
   - `POST /api/user/api-keys` - 添加新API密钥
   - `PUT /api/user/api-keys/:id` - 更新API密钥状态
   - `DELETE /api/user/api-keys/:id` - 删除API密钥
   - `POST /api/user/api-keys/:id/verify` - 验证API密钥有效性

3. **通知设置API**
   - `GET /api/user/notification-settings` - 获取通知设置
   - `PUT /api/user/notification-settings` - 更新通知设置

## 4. 通知中心

### 核心功能
- 通知列表查看（全部、策略、风控、系统）
- 通知筛选（全部/未读）
- 通知状态管理（标记已读、删除）
- 批量操作（全部标记已读、清空通知）

### API需求
1. **通知管理API**
   - `GET /api/notifications` - 获取通知列表，支持分类和筛选
   - `PUT /api/notifications/:id/read` - 标记单条通知为已读
   - `DELETE /api/notifications/:id` - 删除单条通知
   - `POST /api/notifications/read-all` - 标记所有通知为已读
   - `DELETE /api/notifications/clear` - 清空所有通知

## 5. 交易与行情数据

### 核心功能
- 实时行情数据获取
- 交易执行（下单、撤单）
- 交易历史记录

### API需求
1. **市场数据API**
   - `GET /api/market/tickers` - 获取行情列表
   - `GET /api/market/ticker/:symbol` - 获取单个交易对行情
   - `GET /api/market/klines/:symbol` - 获取K线数据

2. **交易API**
   - `POST /api/trade/order` - 创建订单
   - `DELETE /api/trade/order/:id` - 取消订单
   - `GET /api/trade/orders` - 获取订单列表
   - `GET /api/trade/transactions` - 获取交易记录

## 6. 系统配置与监控

### 核心功能
- 系统状态监控
- 交易所连接状态
- 系统参数配置

### API需求
1. **系统API**
   - `GET /api/system/status` - 获取系统状态
   - `GET /api/system/exchanges` - 获取交易所连接状态
   - `GET /api/system/settings` - 获取系统设置
   - `PUT /api/system/settings` - 更新系统设置

## 技术要求

1. **认证与授权**
   - 所有API需要JWT认证
   - 不同API需要不同的权限级别

2. **数据格式**
   - 请求和响应均使用JSON格式
   - 错误响应应包含错误码和详细信息

3. **安全考虑**
   - API密钥信息需加密存储
   - 敏感操作需要二次验证
   - 访问限制和速率限制

4. **实时通信**
   - 使用WebSocket提供行情和交易状态的实时更新
   - 支持通知的实时推送

## 数据存储需求

基于现有的数据模型设计，系统需要以下主要数据表：

1. 用户表 (users)
2. API密钥表 (api_keys)
3. 策略表 (strategies)
4. 网格配置表 (grid_configs)
5. 订单表 (orders)
6. 交易记录表 (transactions)
7. 风控设置表 (risk_settings)
8. 时间点表 (time_points)
9. 通知表 (notifications)
10. 用户偏好表 (user_preferences)
11. 系统设置表 (system_settings)

这些功能和API需求将为LingShe-TradeBot系统提供全面的加密货币交易自动化功能，包括策略管理、风险控制、账户管理和通知系统等核心功能模块。
