import json
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import (
    FastAPI,
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import paho.mqtt.client as mqtt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 路由器
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

# 活跃的WebSocket连接
active_connections: List[WebSocket] = []

# MQTT客户端
mqtt_client = None

# 内存缓存最近的交易记录（实际应用中应改用数据库）
recent_trades = []
trades_cache_limit = 1000  # 最多缓存1000条记录


# 交易记录模型
class TradeRecord(BaseModel):
    id: str
    strategy_id: str
    exchange_order_id: str
    time: str
    strategy_name: str
    strategy_type: str
    pair: str
    type: str  # open/close
    direction: str  # long/short
    price: float
    amount: float
    contracts: Optional[float] = None
    total: float
    profit: float
    fee: float
    system_fee: Optional[float] = None
    status: str
    exchange: str
    order_type: str
    note: Optional[str] = None
    trigger_reason: Optional[str] = None


# 交易记录查询请求模型
class TradeRecordRequest(BaseModel):
    strategyType: Optional[str] = None
    exchange: Optional[str] = None
    contractType: Optional[str] = None
    direction: Optional[str] = None
    type: Optional[str] = None
    profitStatus: Optional[str] = None
    dateRange: Optional[List[str]] = None
    searchKeyword: Optional[str] = None
    page: int = 1
    pageSize: int = 10


# 交易记录统计模型
class TradeStatistics(BaseModel):
    totalTrades: int
    totalVolume: float
    totalProfit: float
    profitRate: float
    winRate: float
    avgProfit: float


# 初始化MQTT客户端
def init_mqtt_client(
    broker_host="emqx", broker_port=1883, username="admin", password="admin"
):
    global mqtt_client

    # 创建MQTT客户端
    client_id = f"trade_records_service_{datetime.now().timestamp()}"
    mqtt_client = mqtt.Client(client_id=client_id)

    # 设置认证信息
    if username and password:
        mqtt_client.username_pw_set(username, password)

    # 设置回调函数
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message

    # 连接到MQTT代理
    try:
        mqtt_client.connect(broker_host, broker_port, 60)
        mqtt_client.loop_start()
        logger.info(f"MQTT客户端已连接到 {broker_host}:{broker_port}")
    except Exception as e:
        logger.error(f"MQTT连接失败: {e}")
        return False

    return True


# MQTT连接回调
def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("已连接到MQTT代理")
        # 订阅交易记录主题
        client.subscribe("hbot/+/+/trades")
        client.subscribe("hbot/+/+/status")
    else:
        logger.error(f"MQTT连接失败，返回码: {rc}")


# MQTT消息回调
def on_mqtt_message(client, userdata, msg):
    try:
        # 解析消息
        payload = json.loads(msg.payload.decode())
        topic = msg.topic

        logger.info(f"收到MQTT消息: {topic}")

        # 处理交易记录消息
        if "/trades" in topic:
            process_trade_record(payload, topic)
        # 处理状态更新消息
        elif "/status" in topic:
            process_status_update(payload, topic)
    except Exception as e:
        logger.error(f"处理MQTT消息时发生错误: {e}")


# 处理交易记录消息
def process_trade_record(payload, topic):
    try:
        # 解析主题以获取策略ID
        parts = topic.split("/")
        if len(parts) >= 3:
            strategy_id = parts[2]

            # 转换为交易记录格式
            trade = transform_hummingbot_trade(payload, strategy_id)
            if trade:
                # 添加到最近交易记录缓存
                add_to_recent_trades(trade)

                # 转发到WebSocket
                asyncio.create_task(broadcast_trade(trade))
    except Exception as e:
        logger.error(f"处理交易记录时发生错误: {e}")


# 处理状态更新消息
def process_status_update(payload, topic):
    # 将策略状态更新转发到WebSocket
    asyncio.create_task(broadcast_status(payload))


# 转换Hummingbot交易记录为标准格式
def transform_hummingbot_trade(hb_trade, strategy_id):
    try:
        # 从Hummingbot交易记录中提取数据
        trade_id = hb_trade.get("id", f"TX-{datetime.now().timestamp()}")

        trade = {
            "id": trade_id,
            "strategy_id": strategy_id,
            "exchange_order_id": hb_trade.get("exchange_order_id", ""),
            "time": hb_trade.get("executed_at", datetime.now().isoformat()),
            "strategy_name": hb_trade.get("strategy_name", ""),
            "strategy_type": hb_trade.get("strategy_type", "网格策略"),
            "pair": hb_trade.get("market", ""),
            "type": hb_trade.get("trade_type", "open"),
            "direction": hb_trade.get("position_side", "long"),
            "price": float(hb_trade.get("price", 0)),
            "amount": float(hb_trade.get("amount", 0)),
            "contracts": (
                float(hb_trade.get("contracts", 0)) if "contracts" in hb_trade else None
            ),
            "total": float(hb_trade.get("value", 0)),
            "profit": float(hb_trade.get("profit", 0)),
            "fee": float(hb_trade.get("fee", 0)),
            "system_fee": (
                float(hb_trade.get("system_fee", 0))
                if "system_fee" in hb_trade
                else None
            ),
            "status": hb_trade.get("status", "completed"),
            "exchange": hb_trade.get("exchange", ""),
            "order_type": hb_trade.get("order_type", "限价单"),
            "note": hb_trade.get("note", ""),
            "trigger_reason": hb_trade.get("trigger_reason", ""),
        }

        return trade
    except Exception as e:
        logger.error(f"转换交易记录时发生错误: {e}")
        return None


# 添加交易记录到最近交易缓存
def add_to_recent_trades(trade):
    global recent_trades
    recent_trades.append(trade)

    # 如果超过缓存限制，移除最早的记录
    if len(recent_trades) > trades_cache_limit:
        recent_trades = recent_trades[-trades_cache_limit:]


# 计算交易统计数据
def calculate_statistics(trades):
    try:
        if not trades:
            return {
                "totalTrades": 0,
                "totalVolume": 0,
                "totalProfit": 0,
                "profitRate": 0,
                "winRate": 0,
                "avgProfit": 0,
            }

        total_trades = len(trades)
        total_volume = sum(t.get("total", 0) for t in trades)
        total_profit = sum(t.get("profit", 0) for t in trades)
        win_count = sum(1 for t in trades if t.get("profit", 0) > 0)

        profit_rate = (total_profit / total_volume * 100) if total_volume > 0 else 0
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        avg_profit = (total_profit / total_trades) if total_trades > 0 else 0

        return {
            "totalTrades": total_trades,
            "totalVolume": round(total_volume, 2),
            "totalProfit": round(total_profit, 2),
            "profitRate": round(profit_rate, 1),
            "winRate": round(win_rate, 1),
            "avgProfit": round(avg_profit, 2),
        }
    except Exception as e:
        logger.error(f"计算统计数据时发生错误: {e}")
        return {
            "totalTrades": 0,
            "totalVolume": 0,
            "totalProfit": 0,
            "profitRate": 0,
            "winRate": 0,
            "avgProfit": 0,
        }


# 过滤交易记录
def filter_trades(trades, filters):
    filtered = []

    for trade in trades:
        # 应用筛选条件
        if filters.strategyType and trade.get("strategy_type") != filters.strategyType:
            continue
        if filters.exchange and trade.get("exchange") != filters.exchange:
            continue
        if filters.contractType and trade.get("contract_type") != filters.contractType:
            continue
        if filters.direction and trade.get("direction") != filters.direction:
            continue
        if filters.type and trade.get("type") != filters.type:
            continue

        # 筛选盈亏状态
        if filters.profitStatus:
            profit = trade.get("profit", 0)
            if filters.profitStatus == "profit" and profit <= 0:
                continue
            if filters.profitStatus == "loss" and profit >= 0:
                continue

        # 筛选日期范围
        if filters.dateRange and len(filters.dateRange) == 2:
            trade_time = datetime.fromisoformat(
                trade.get("time").replace("Z", "+00:00")
            )
            start_date = datetime.fromisoformat(filters.dateRange[0])
            end_date = datetime.fromisoformat(filters.dateRange[1])

            if trade_time < start_date or trade_time > end_date:
                continue

        # 关键词搜索
        if filters.searchKeyword:
            keyword = filters.searchKeyword.lower()
            searchable_fields = [
                trade.get("strategy_name", ""),
                trade.get("pair", ""),
                trade.get("exchange", ""),
                trade.get("exchange_order_id", ""),
            ]

            if not any(
                field and keyword in field.lower() for field in searchable_fields
            ):
                continue

        filtered.append(trade)

    return filtered


# API路由：获取交易记录
@router.post("/")
async def get_transactions(request: TradeRecordRequest):
    try:
        # 过滤交易记录
        filtered_trades = filter_trades(recent_trades, request)

        # 计算总数
        total = len(filtered_trades)

        # 分页
        start = (request.page - 1) * request.pageSize
        end = start + request.pageSize
        paginated_trades = filtered_trades[start:end]

        # 计算统计数据
        stats = calculate_statistics(filtered_trades)

        return {"records": paginated_trades, "total": total, "statistics": stats}
    except Exception as e:
        logger.error(f"获取交易记录时发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket连接管理
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# 广播交易记录到所有WebSocket连接
async def broadcast_trade(trade):
    message = {"type": "trade_update", "trade": trade}
    await broadcast_message(message)


# 广播状态更新到所有WebSocket连接
async def broadcast_status(status):
    message = {"type": "status_update", "status": status}
    await broadcast_message(message)


# 广播统计数据更新到所有WebSocket连接
async def broadcast_statistics(statistics):
    message = {"type": "statistics_update", "statistics": statistics}
    await broadcast_message(message)


# 广播消息到所有WebSocket连接
async def broadcast_message(message):
    json_message = json.dumps(message)
    for connection in active_connections:
        try:
            await connection.send_text(json_message)
        except Exception as e:
            logger.error(f"发送WebSocket消息时发生错误: {e}")
            # 移除失效的连接
            if connection in active_connections:
                active_connections.remove(connection)


# 初始化API
def init_app(app: FastAPI):
    app.include_router(router)
    # 初始化MQTT客户端
    init_mqtt_client()
    logger.info("交易记录服务已初始化")


# 单独启动（用于测试）
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    init_app(app)

    uvicorn.run(app, host="0.0.0.0", port=8001)
