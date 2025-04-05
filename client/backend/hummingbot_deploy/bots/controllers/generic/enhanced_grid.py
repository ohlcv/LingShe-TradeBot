from decimal import Decimal
from typing import Dict, List, Optional, Set, Any, Tuple, Union
import time

from pydantic import BaseModel, Field

from hummingbot.client.config.config_data_types import ClientFieldData
from hummingbot.core.data_type.common import (
    OrderType,
    PositionMode,
    PriceType,
    TradeType,
)
from hummingbot.core.data_type.trade_fee import TokenAmount
from hummingbot.data_feed.candles_feed.data_types import CandlesConfig
from hummingbot.strategy_v2.controllers import ControllerBase, ControllerConfigBase
from hummingbot.strategy_v2.executors.position_executor.data_types import (
    PositionExecutorConfig,
    TripleBarrierConfig,
)
from hummingbot.strategy_v2.models.executor_actions import (
    CreateExecutorAction,
    ExecutorAction,
    StopExecutorAction,
)
from hummingbot.strategy_v2.models.executors_info import ExecutorInfo
from ...services.risk_control_adapter import RiskControlAdapter


# 止盈批次配置
class TakeProfitBatch(BaseModel):
    """止盈批次配置"""

    level: int  # 批次级别
    profit_ratio: Decimal  # 止盈比例
    rebound_ratio: Decimal  # 回调比例
    portion: Decimal  # 平仓比例
    status: str = "未触发"  # 状态：未触发/已触发


# 网格层级配置
class GridLevelConfig(BaseModel):
    """网格层级配置"""

    level: int  # 层级编号
    amount: Decimal  # 该层级的投资金额
    open_ratio: Decimal  # 开仓间隔比例
    open_rebound_ratio: Decimal  # 开仓反弹比例
    take_profit_batches: List[TakeProfitBatch] = []  # 止盈批次
    status: str = "未开仓"  # 层级状态：未开仓/待开仓/已开仓/待止盈
    is_active: bool = True  # 是否激活


# 风控配置
class RiskControlConfig(BaseModel):
    """风控配置"""

    # 资金风控
    total_loss_limit: Optional[Decimal] = None  # 总亏损停止阈值
    total_profit_limit: Optional[Decimal] = None  # 总盈利停止阈值
    max_loss_per_trade: Optional[Decimal] = None  # 单笔最大亏损额
    max_position: Optional[Decimal] = None  # 最大持仓金额

    # 时间风控
    trading_time_limit: bool = False  # 交易时间限制
    trading_start_time: Optional[str] = None  # 交易开始时间
    trading_end_time: Optional[str] = None  # 交易结束时间

    # 交易保护
    consecutive_loss_limit: Optional[int] = None  # 连续亏损限制
    order_frequency_limit: Optional[int] = None  # 下单频率限制
    price_volatility_protection: bool = False  # 价格波动保护

    # 智能风控
    volatility_adjusted_stop_loss: bool = False  # 波动率调整止损
    hedging_protection: bool = False  # 对冲保护


# 增强网格控制器配置
class EnhancedGridConfig(ControllerConfigBase):
    """增强网格策略配置"""

    controller_name: str = "enhanced_grid"
    controller_type: str = "generic"
    candles_config: List[CandlesConfig] = []

    # 基本参数
    connector_name: str = Field(  # 交易所
        default="binance_perpetual", client_data=ClientFieldData(is_updatable=True)
    )
    trading_pair: str = Field(  # 交易对
        default="BTC-USDT", client_data=ClientFieldData(is_updatable=True)
    )
    position_mode: PositionMode = Field(  # 仓位模式
        default=PositionMode.HEDGE, client_data=ClientFieldData(is_updatable=True)
    )
    leverage: int = Field(  # 杠杆
        default=1, client_data=ClientFieldData(is_updatable=True)
    )

    # 网格参数
    total_investment: Decimal = Field(  # 总投资金额
        default=Decimal("1000"), client_data=ClientFieldData(is_updatable=True)
    )
    grid_levels: List[GridLevelConfig] = Field(  # 网格层级
        default=[], client_data=ClientFieldData(is_updatable=True)
    )

    # 全局止盈设置
    global_take_profit_batches: List[TakeProfitBatch] = Field(  # 全局止盈批次
        default=[], client_data=ClientFieldData(is_updatable=True)
    )

    # 风控设置
    risk_control: RiskControlConfig = Field(  # 风控配置
        default=RiskControlConfig(), client_data=ClientFieldData(is_updatable=True)
    )

    # 更新设置
    update_interval: int = Field(  # 更新间隔(秒)
        default=30, client_data=ClientFieldData(is_updatable=True)
    )

    # 动态配置
    enable_dynamic_grid: bool = Field(  # 启用动态网格
        default=True, client_data=ClientFieldData(is_updatable=True)
    )
    max_grid_levels: int = Field(  # 最大网格层级数
        default=10, client_data=ClientFieldData(is_updatable=True)
    )

    def update_markets(self, markets: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """更新市场配置"""
        if self.connector_name not in markets:
            markets[self.connector_name] = set()
        markets[self.connector_name].add(self.trading_pair)
        return markets


class EnhancedGridController(ControllerBase):
    """增强网格策略控制器，支持单策略风控和全局风控同时生效"""

    def __init__(self, config: EnhancedGridConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.config = config
        self._last_update_timestamp = 0
        self.executor_grid_map = {}  # 执行器ID对应的网格层级
        self.pending_updates = {}  # 待处理的参数更新
        self._last_trades = []  # 最近的交易记录
        self._consecutive_losses = 0  # 连续亏损计数
        self._pending_grid_changes = False  # 是否有待处理的网格变更
        self._trade_count = 0  # 交易计数

        # 本地风控状态
        self._local_risk_active = True

        # 全局风控状态（默认启用）
        self._global_risk_active = kwargs.get("enable_global_risk", True)

        # 初始化风控适配器，用于与全局风控服务通信
        self.risk_adapter = RiskControlAdapter(
            strategy_id=str(self.config.id),
            use_global_risk_control=True,  # 始终连接全局风控服务，但可能不使用其决策
        )

        # 如果启用全局风控，则转换策略特定的风控配置为全局风控配置
        if self._global_risk_active:
            self._convert_risk_config_to_global()

        # 初始化网格层级配置
        for level in config.grid_levels:
            self.executor_grid_map[level.level] = level.level

        self.logger().info(
            f"增强型网格控制器已初始化, 策略ID: {config.id}, 本地风控: {self._local_risk_active}, 全局风控: {self._global_risk_active}"
        )

    def _convert_risk_config_to_global(self):
        """将本地风控配置转换为全局风控配置"""
        risk_config = self.config.risk_control

        strategy_risk_config = {
            "totalLossLimit": (
                float(risk_config.total_loss_limit)
                if risk_config.total_loss_limit
                else None
            ),
            "totalProfitLimit": (
                float(risk_config.total_profit_limit)
                if risk_config.total_profit_limit
                else None
            ),
            "maxLossPerTrade": (
                float(risk_config.max_loss_per_trade)
                if risk_config.max_loss_per_trade
                else None
            ),
            "maxPosition": (
                float(risk_config.max_position) if risk_config.max_position else None
            ),
            "tradingTimeLimit": risk_config.trading_time_limit,
            "tradingStartTime": risk_config.trading_start_time,
            "tradingEndTime": risk_config.trading_end_time,
            "consecutiveLossLimit": risk_config.consecutive_loss_limit,
            "volatilityAdjustedStopLoss": risk_config.volatility_adjusted_stop_loss,
            "hedgingProtection": risk_config.hedging_protection,
        }

        self.risk_adapter.convert_strategy_risk_to_global(strategy_risk_config)
        self.logger().info(
            f"已将策略特定风控配置转换为全局风控配置: {strategy_risk_config}"
        )

    def get_mid_price(self) -> Decimal:
        """获取中间价格"""
        return self.market_data_provider.get_price_by_type(
            self.config.connector_name, self.config.trading_pair, PriceType.MidPrice
        )

    async def update_processed_data(self):
        """更新处理数据"""
        mid_price = self.get_mid_price()

        # 处理待更新的参数
        if self.pending_updates:
            self._apply_pending_updates()

        # 更新网格层级状态
        active_executors = [e for e in self.executors_info if e.is_active]

        # 创建网格层级状态映射
        grid_states = {}
        for executor in active_executors:
            level_id = self.executor_grid_map.get(executor.id)
            if level_id is not None:
                if executor.is_trading:
                    if executor.filled_amount > 0:
                        grid_states[level_id] = "待止盈"
                    else:
                        grid_states[level_id] = "已开仓"
                else:
                    grid_states[level_id] = "待开仓"

        # 更新每个网格层级的状态
        for grid_level in self.config.grid_levels:
            if grid_level.level in grid_states:
                grid_level.status = grid_states[grid_level.level]
            elif grid_level.is_active:
                # 计算层级价格
                level_price = self._calculate_level_price(grid_level, mid_price)

                # 如果当前价格低于层级价格的开仓反弹点，标记为待开仓
                rebound_threshold = level_price * (
                    1 - grid_level.open_rebound_ratio / 100
                )
                if mid_price <= rebound_threshold:
                    grid_level.status = "待开仓"
                else:
                    grid_level.status = "未开仓"

        # 如果启用了动态网格，检查是否需要调整网格
        if self.config.enable_dynamic_grid:
            self._check_dynamic_grid_adjustment(mid_price)

        # 更新处理后的数据
        self.processed_data.update(
            {
                "mid_price": mid_price,
                "grid_levels": self.config.grid_levels,
                "active_executors": active_executors,
                "global_pnl": self._calculate_global_pnl(),
                "trading_allowed": self._is_trading_allowed(),
                "pending_grid_changes": self._pending_grid_changes,
            }
        )

    def _check_dynamic_grid_adjustment(self, current_price: Decimal):
        """检查是否需要动态调整网格"""
        # 这里可以实现根据价格走势动态调整网格的逻辑
        # 例如，价格大幅变动时，重新分配网格层级等
        pass

    def _apply_pending_updates(self):
        """应用待处理的参数更新"""
        updates = self.pending_updates.copy()
        self.pending_updates.clear()

        # 更新基本参数
        if "connector_name" in updates:
            self.config.connector_name = updates["connector_name"]

        if "trading_pair" in updates:
            self.config.trading_pair = updates["trading_pair"]

        if "position_mode" in updates:
            self.config.position_mode = updates["position_mode"]

        if "leverage" in updates:
            self.config.leverage = updates["leverage"]

        if "total_investment" in updates:
            self.config.total_investment = updates["total_investment"]

        # 更新网格层级参数
        if "grid_levels" in updates:
            self._update_grid_levels(updates["grid_levels"])
            self._pending_grid_changes = True

        # 更新风控参数
        if "risk_control" in updates:
            self._update_risk_control(updates["risk_control"])

        # 更新动态网格设置
        if "enable_dynamic_grid" in updates:
            self.config.enable_dynamic_grid = updates["enable_dynamic_grid"]

        if "max_grid_levels" in updates:
            self.config.max_grid_levels = updates["max_grid_levels"]

        # 记录配置更新
        self.logger().info(f"应用配置更新: {updates}")

    def _update_grid_levels(self, grid_levels_data):
        """更新网格层级参数"""
        # 获取现有层级的映射
        current_levels = {level.level: level for level in self.config.grid_levels}
        active_executors_levels = set(self.executor_grid_map.values())

        # 处理要删除的层级
        levels_to_remove = set(current_levels.keys()) - {
            level["level"] for level in grid_levels_data
        }
        for level_id in levels_to_remove:
            # 如果层级已有活跃执行器，不能直接删除，只能停用
            if level_id in active_executors_levels:
                current_levels[level_id].is_active = False
                self.logger().warning(f"层级 {level_id} 有活跃执行器，已标记为停用")
            else:
                # 完全删除层级
                self.config.grid_levels = [
                    level
                    for level in self.config.grid_levels
                    if level.level != level_id
                ]
                self.logger().info(f"已删除层级 {level_id}")

        # 更新或添加层级
        for level_data in grid_levels_data:
            level_id = level_data["level"]

            # 检查是否是已执行层级，已执行层级不允许修改某些关键参数
            if level_id in active_executors_levels:
                # 可以修改的参数：激活状态、止盈批次
                safe_updates = {"is_active", "take_profit_batches"}
                for key in list(level_data.keys()):
                    if key not in safe_updates and key != "level":
                        self.logger().warning(
                            f"忽略对已执行层级 {level_id} 的参数 {key} 的更新"
                        )
                        level_data.pop(key)

            # 如果是新层级，添加到配置中
            if level_id not in current_levels:
                new_level = GridLevelConfig(**level_data)
                self.config.grid_levels.append(new_level)
                self.logger().info(f"已添加新层级 {level_id}")
            else:
                # 更新现有层级
                for key, value in level_data.items():
                    if key != "level" and key != "status":
                        setattr(current_levels[level_id], key, value)

        # 检查网格层级数是否超过最大限制
        if len(self.config.grid_levels) > self.config.max_grid_levels:
            # 对层级进行排序，保留优先级最高的层级
            sorted_levels = sorted(
                self.config.grid_levels,
                key=lambda x: (
                    not x.is_active,
                    x.level not in active_executors_levels,
                    x.level,
                ),
            )
            self.config.grid_levels = sorted_levels[: self.config.max_grid_levels]
            self.logger().warning(
                f"网格层级数超过最大限制 {self.config.max_grid_levels}，已裁剪"
            )

    def _update_risk_control(self, risk_control_data):
        """更新风控参数"""
        for key, value in risk_control_data.items():
            if hasattr(self.config.risk_control, key):
                setattr(self.config.risk_control, key, value)

        # 如果风控配置更新且全局风控启用，重新转换配置
        if self._global_risk_active:
            self._convert_risk_config_to_global()

    def _is_trading_allowed(self) -> bool:
        """检查是否允许交易，同时考虑本地风控和全局风控规则"""
        # 检查本地风控
        if self._local_risk_active:
            local_allowed = self._check_local_risk_rules()
            if not local_allowed:
                self.logger().warning("本地风控禁止交易")
                return False

        # 检查全局风控
        if self._global_risk_active:
            global_allowed, reason = self.risk_adapter.check_trading_allowed()
            if not global_allowed:
                self.logger().warning(f"全局风控禁止交易，原因: {reason}")
                return False

        return True

    def _check_local_risk_rules(self) -> bool:
        """检查本地风控规则"""
        risk_config = self.config.risk_control

        # 检查总亏损限制
        if risk_config.total_loss_limit is not None:
            total_pnl = self._calculate_local_pnl()
            if total_pnl < -risk_config.total_loss_limit:
                self.logger().warning(
                    f"触发总亏损限制: {total_pnl} < -{risk_config.total_loss_limit}"
                )
                return False

        # 检查总盈利限制
        if risk_config.total_profit_limit is not None:
            total_pnl = self._calculate_local_pnl()
            if total_pnl > risk_config.total_profit_limit:
                self.logger().warning(
                    f"触发总盈利限制: {total_pnl} > {risk_config.total_profit_limit}"
                )
                return False

        # 检查连续亏损限制
        if (
            risk_config.consecutive_loss_limit is not None
            and self._consecutive_losses >= risk_config.consecutive_loss_limit
        ):
            self.logger().warning(
                f"触发连续亏损限制: {self._consecutive_losses} >= {risk_config.consecutive_loss_limit}"
            )
            return False

        # 检查交易时间限制
        if risk_config.trading_time_limit and not self._is_trading_time_allowed():
            self.logger().warning("当前时间不允许交易")
            return False

        return True

    def _is_trading_time_allowed(self) -> bool:
        """检查当前时间是否允许交易"""
        risk_config = self.config.risk_control

        # 如果未设置交易时间限制，则允许交易
        if not risk_config.trading_time_limit:
            return True

        # 如果未设置开始或结束时间，则允许交易
        if not risk_config.trading_start_time or not risk_config.trading_end_time:
            return True

        # 获取当前时间
        current_time = time.localtime()
        current_time_str = time.strftime("%H:%M:%S", current_time)

        # 检查当前时间是否在允许交易的时间范围内
        return (
            risk_config.trading_start_time
            <= current_time_str
            <= risk_config.trading_end_time
        )

    def _calculate_local_pnl(self) -> Decimal:
        """计算本地盈亏（不更新全局风控状态）"""
        total_pnl = Decimal("0")

        for executor in self.executors_info:
            if hasattr(executor, "total_pnl") and executor.total_pnl is not None:
                total_pnl += executor.total_pnl

        return total_pnl

    def _calculate_global_pnl(self) -> Decimal:
        """计算全局盈亏并更新风控状态"""
        total_pnl = self._calculate_local_pnl()
        position_value = Decimal("0")

        for executor in self.executors_info:
            if (
                hasattr(executor, "position_value")
                and executor.position_value is not None
            ):
                position_value += executor.position_value

        # 更新风控适配器中的状态
        if self._global_risk_active:
            self.risk_adapter.update_strategy_state(
                total_pnl=total_pnl, position_value=position_value
            )

        return total_pnl

    def process_trade_result(self, trade_info: Dict):
        """处理交易结果，更新风控状态"""
        # 假设trade_info包含trade_result字段表示此次交易的盈亏
        if "trade_result" in trade_info and trade_info["trade_result"] is not None:
            trade_result = Decimal(str(trade_info["trade_result"]))

            # 更新连续亏损计数（本地风控使用）
            if trade_result < 0:
                self._consecutive_losses += 1
            else:
                self._consecutive_losses = 0

            # 更新全局风控适配器中的交易结果
            if self._global_risk_active:
                self.risk_adapter.update_strategy_state(trade_result=trade_result)

        self._trade_count += 1

    def start(self):
        """启动策略"""
        if self.is_running:
            self.logger().warning("策略已经在运行中")
            return

        # 重置风控状态
        self._consecutive_losses = 0
        self.risk_adapter.reset_risk_state()

        self.is_running = True
        self.logger().info(f"策略已启动，ID: {self.config.id}")

    def stop(self):
        """停止策略"""
        if not self.is_running:
            self.logger().warning("策略已经停止")
            return

        self.is_running = False
        self.logger().info(f"策略已停止，ID: {self.config.id}")

    def cleanup(self):
        """清理资源"""
        self.stop()

        # 清理风控适配器资源
        self.risk_adapter.cleanup()

        self.logger().info("资源已清理")

    def toggle_local_risk_control(self, active: bool):
        """开启或关闭本地风控"""
        if self._local_risk_active == active:
            return

        self._local_risk_active = active
        self.logger().info(f"本地风控状态已切换为: {'启用' if active else '禁用'}")

    def toggle_global_risk_control(self, active: bool):
        """开启或关闭全局风控"""
        if self._global_risk_active == active:
            return

        self._global_risk_active = active

        if active:
            # 如果重新启用全局风控，转换策略特定的风控配置
            self._convert_risk_config_to_global()

        self.logger().info(f"全局风控状态已切换为: {'启用' if active else '禁用'}")

    def _update_risk_control(self, risk_control_data):
        """更新风控参数"""
        for key, value in risk_control_data.items():
            if hasattr(self.config.risk_control, key):
                setattr(self.config.risk_control, key, value)

        # 如果风控配置更新且全局风控启用，重新转换配置
        if self._global_risk_active:
            self._convert_risk_config_to_global()

    def determine_executor_actions(self) -> List[ExecutorAction]:
        """决定执行器动作"""
        current_time = self.market_data_provider.time()

        # 检查是否需要更新
        if current_time - self._last_update_timestamp < self.config.update_interval:
            return []

        self._last_update_timestamp = current_time

        # 检查是否允许交易
        if not self.processed_data.get("trading_allowed", True):
            self.logger().info("当前不允许交易，跳过动作生成")
            return []

        # 如果有待处理的网格变更，重置标记
        if self._pending_grid_changes:
            self._pending_grid_changes = False

        # 生成创建和停止执行器的动作
        return (
            self.determine_create_executor_actions()
            + self.determine_stop_executor_actions()
        )

    def determine_create_executor_actions(self) -> List[ExecutorAction]:
        """决定创建执行器的动作"""
        mid_price = self.processed_data["mid_price"]
        create_actions = []

        # 获取活跃执行器对应的网格层级
        active_levels = set(self.executor_grid_map.values())

        # 遍历网格层级，为符合条件的层级创建执行器
        for grid_level in sorted(self.config.grid_levels, key=lambda x: x.level):
            # 跳过非激活或已有执行器的层级
            if not grid_level.is_active or grid_level.level in active_levels:
                continue

            # 只处理"待开仓"或"未开仓"状态的层级
            if grid_level.status not in ["待开仓", "未开仓"]:
                continue

            # 计算层级价格
            level_price = self._calculate_level_price(grid_level, mid_price)

            # 计算反弹阈值
            rebound_threshold = level_price * (1 - grid_level.open_rebound_ratio / 100)

            # 检查是否满足开仓条件
            if grid_level.status == "待开仓" or mid_price <= rebound_threshold:
                # 创建执行器动作
                action = self._create_executor_for_grid_level(
                    grid_level, level_price, mid_price
                )
                if action:
                    # 记录执行器与网格层级的关系
                    self.executor_grid_map[action.executor_id] = grid_level.level
                    create_actions.append(action)

        return create_actions

    def _create_executor_for_grid_level(
        self, grid_level: GridLevelConfig, level_price: Decimal, mid_price: Decimal
    ) -> Optional[CreateExecutorAction]:
        """为网格层级创建执行器"""
        # 计算实际交易量
        quote_amount = grid_level.amount  # 投资金额（计价货币）

        # 计算基础货币数量
        base_amount = quote_amount / level_price

        # 执行数量精度处理
        amount = self.market_data_provider.quantize_order_amount(
            self.config.connector_name, self.config.trading_pair, base_amount
        )

        # 执行价格精度处理
        entry_price = self.market_data_provider.quantize_order_price(
            self.config.connector_name, self.config.trading_pair, level_price
        )

        # 创建止盈配置
        take_profit_config = self._create_take_profit_config(grid_level)

        # 创建执行器配置
        executor_config = PositionExecutorConfig(
            timestamp=self.market_data_provider.time(),
            connector_name=self.config.connector_name,
            trading_pair=self.config.trading_pair,
            side=TradeType.BUY,  # 买入做多
            entry_price=entry_price,
            amount=amount,
            leverage=self.config.leverage,
            position_mode=self.config.position_mode,
            custom_info={
                "level_id": grid_level.level,
                "investment_amount": float(grid_level.amount),
            },
            triple_barrier_config=TripleBarrierConfig(
                take_profit=take_profit_config,
                time_limit=None,  # 无时间限制
                open_order_type=OrderType.LIMIT_MAKER,
                take_profit_order_type=OrderType.LIMIT,
            ),
        )

        return CreateExecutorAction(
            controller_id=self.config.id, executor_config=executor_config
        )

    def _create_take_profit_config(self, grid_level: GridLevelConfig) -> Any:
        """创建止盈配置"""
        # 如果没有设置止盈批次，使用默认值
        if not grid_level.take_profit_batches:
            return Decimal("0.02")  # 默认2%止盈

        # 转换止盈批次为Hummingbot接受的格式
        batches = []
        for batch in grid_level.take_profit_batches:
            tp_config = {
                "profit_ratio": batch.profit_ratio / 100,  # 转为小数
                "rebound_ratio": batch.rebound_ratio / 100,
                "portion": batch.portion / 100,
            }
            batches.append(tp_config)

        # 返回止盈配置
        return batches

    def determine_stop_executor_actions(self) -> List[ExecutorAction]:
        """决定停止执行器的动作"""
        stop_actions = []

        # 获取未关联到有效网格层级的执行器
        for executor in self.executors_info:
            if not executor.is_active:
                continue

            grid_level_id = self.executor_grid_map.get(executor.id)
            if grid_level_id is None:
                continue

            # 检查对应的网格层级是否存在且是否激活
            grid_level = None
            for level in self.config.grid_levels:
                if level.level == grid_level_id:
                    grid_level = level
                    break

            # 如果网格层级不存在或已被禁用，停止对应执行器
            if grid_level is None or not grid_level.is_active:
                stop_actions.append(
                    StopExecutorAction(
                        controller_id=self.config.id, executor_id=executor.id
                    )
                )

        return stop_actions

    def get_balance_requirements(self) -> List[TokenAmount]:
        """获取余额需求"""
        if "perpetual" in self.config.connector_name:
            return []

        quote_currency = self.config.trading_pair.split("-")[1]

        # 计算所有网格层级需要的计价货币总量
        total_quote_amount = Decimal("0")
        for grid_level in self.config.grid_levels:
            if grid_level.is_active and grid_level.status in ["未开仓", "待开仓"]:
                total_quote_amount += grid_level.amount

        # 添加10%的缓冲
        total_quote_amount = total_quote_amount * Decimal("1.1")

        return [TokenAmount(quote_currency, total_quote_amount)]

    def update_config(self, updates: Dict[str, Any]):
        """更新控制器配置"""
        self.pending_updates.update(updates)
        self.logger().info(f"接收配置更新: {updates}")

    def _calculate_level_price(
        self, grid_level: GridLevelConfig, mid_price: Decimal
    ) -> Decimal:
        """计算网格层级价格"""
        # 查找前一层级
        previous_level = None
        previous_price = mid_price

        # 找出前一层级
        for level in sorted(self.config.grid_levels, key=lambda x: x.level):
            if level.level == grid_level.level:
                break
            previous_level = level

        # 计算当前层级价格
        if previous_level:
            # 根据前一层级和开仓间隔计算当前层级价格
            current_level_price = previous_price * (1 - grid_level.open_ratio / 100)
        else:
            # 第一层级直接用中间价
            current_level_price = mid_price

        return current_level_price
