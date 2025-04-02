#!/bin/bash

# 创建交易所接口文件
touch backend/core/exchange/base.py
touch backend/core/exchange/binance.py
touch backend/core/exchange/okx.py
touch backend/core/exchange/mock.py

# 创建执行模块文件
touch backend/core/execution/executor.py
touch backend/core/execution/order.py
touch backend/core/execution/position.py

# 创建数据管理模块
mkdir -p backend/data
touch backend/data/storage.py
touch backend/data/sqlite.py
touch backend/data/encryption.py
touch backend/data/sync.py

# 创建API通信模块
mkdir -p backend/api
touch backend/api/client.py
touch backend/api/auth.py
touch backend/api/endpoints.py
touch backend/api/websocket.py

# 创建IPC通信模块
mkdir -p backend/ipc
touch backend/ipc/server.py
touch backend/ipc/handlers.py
touch backend/ipc/serializers.py

# 创建工具函数和辅助模块
mkdir -p backend/utils
touch backend/utils/logger.py
touch backend/utils/error_handler.py
touch backend/utils/calculation.py
touch backend/utils/validators.py

# 创建客户端脚本目录
touch scripts/build-electron.js
touch scripts/start-dev.sh

# 创建测试目录
mkdir -p tests/unit
mkdir -p tests/e2e

# 创建根级别配置文件
touch package.json
touch README.md 