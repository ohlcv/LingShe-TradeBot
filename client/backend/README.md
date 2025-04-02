 

LingShe TradeBot的后端核心引擎，负责执行网格交易策略、风险控制和交易所API交互。

## 功能特性

- 网格交易策略执行
- 多交易所API集成
- 风险控制系统
- 本地数据存储
- 实时市场数据监控

## 安装

1. 确保Python 3.9或更高版本已安装
2. 克隆仓库
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 安装开发模式：
   ```bash
   pip install -e .
   ```

## 开发

### 代码风格

- 使用black进行代码格式化
- 使用isort进行导入排序
- 使用mypy进行类型检查

### 运行测试

```bash
pytest
```

### 代码检查

```bash
# 格式化代码
black .

# 排序导入
isort .

# 类型检查
mypy .
```

## 目录结构

```
backend/
├── config/             # 配置文件
├── core/              # 核心业务逻辑
│   ├── engine/        # 网格策略引擎
│   ├── risk/          # 风险控制
│   ├── exchange/      # 交易所API
│   └── execution/     # 交易执行
├── data/              # 数据管理
├── api/               # API接口
├── ipc/               # 进程间通信
└── utils/             # 工具函数
```

## 许可证

MIT License