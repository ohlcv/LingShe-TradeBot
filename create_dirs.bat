@echo off
cd client

REM 创建数据模块目录和文件
mkdir backend\data
type nul > backend\data\storage.py
type nul > backend\data\sqlite.py
type nul > backend\data\encryption.py
type nul > backend\data\sync.py

REM 创建API模块目录和文件
mkdir backend\api
type nul > backend\api\client.py
type nul > backend\api\auth.py
type nul > backend\api\endpoints.py
type nul > backend\api\websocket.py

REM 创建IPC通信模块目录和文件
mkdir backend\ipc
type nul > backend\ipc\server.py
type nul > backend\ipc\handlers.py
type nul > backend\ipc\serializers.py

REM 创建工具函数模块目录和文件
mkdir backend\utils
type nul > backend\utils\logger.py
type nul > backend\utils\error_handler.py
type nul > backend\utils\calculation.py
type nul > backend\utils\validators.py

REM 创建执行模块文件
mkdir backend\core\execution
type nul > backend\core\execution\executor.py
type nul > backend\core\execution\order.py
type nul > backend\core\execution\position.py

REM 创建交易所接口文件
mkdir backend\core\exchange
type nul > backend\core\exchange\base.py
type nul > backend\core\exchange\binance.py
type nul > backend\core\exchange\okx.py
type nul > backend\core\exchange\mock.py

REM 创建客户端脚本目录和文件
mkdir scripts
type nul > scripts\build-electron.js
type nul > scripts\start-dev.sh

REM 创建测试目录
mkdir tests\unit
mkdir tests\e2e 