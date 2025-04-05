from decimal import Decimal
from typing import Dict, List, Optional, Set, Any, Tuple
import time
import logging
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeUnit(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"


class TimeWindowState(BaseModel):
    """时间窗口状态记录"""

    start_time: float
    end_time: float
    total_loss: Decimal = Decimal(0)
    total_profit: Decimal = Decimal(0)
    trade_count: int = 0
    consecutive_losses: int = 0


class FundRiskConfig(BaseModel):
    """资金风控配置"""

    # 系统级资金风控
    system_max_position_value: Optional[Decimal] = None  # 系统最大持仓价值
    system_max_loss_cutoff: Optional[Decimal] = None  # 系统最大亏损停止
    system_max_position_coins: Optional[int] = None  # 系统最大持仓币种数

    # 账户级资金风控
    account_loss_limit: Optional[Decimal] = None  # 账户亏损限制
    account_loss_time_unit: TimeUnit = TimeUnit.DAY  # 账户亏损限制的时间单位

    # 策略级资金风控
    strategy_total_loss_limit: Optional[Decimal] = None  # 策略总亏损停止阈值
    strategy_total_profit_limit: Optional[Decimal] = None  # 策略总盈利停止阈值
    strategy_max_loss_per_trade: Optional[Decimal] = None  # 策略单笔最大亏损额
    strategy_max_position: Optional[Decimal] = None  # 策略最大持仓金额


class TimeRiskConfig(BaseModel):
    """时间风控配置"""

    trading_time_limit: bool = False  # 交易时间限制
    trading_start_time: Optional[str] = None  # 交易开始时间
    trading_end_time: Optional[str] = None  # 交易结束时间
    time_point_limit: bool = False  # 重要时间点禁止交易
    forbidden_time_points: List[str] = []  # 禁止交易的时间点列表


class TradeProtectionConfig(BaseModel):
    """交易保护配置"""

    consecutive_loss_limit: Optional[int] = None  # 连续亏损限制
    consecutive_loss_window: Optional[int] = None  # 连续亏损时间窗口
    consecutive_loss_window_unit: TimeUnit = TimeUnit.HOUR  # 连续亏损时间窗口单位
    order_frequency_limit: Optional[int] = None  # 下单频率限制
    order_frequency_window: Optional[int] = None  # 下单频率时间窗口
    order_frequency_window_unit: TimeUnit = TimeUnit.MINUTE  # 下单频率时间窗口单位


class MarketRiskConfig(BaseModel):
    """市场风控配置"""

    price_volatility_monitoring: bool = False  # 价格异常波动监控
    volatility_threshold: Decimal = Decimal("3.0")  # 波动阈值百分比
    volatility_time_window: int = 5  # 监控时间窗口
    volatility_time_unit: TimeUnit = TimeUnit.MINUTE  # 监控时间窗口单位
    volatility_calculation_method: str = "highLow"  # 波动计算方式

    liquidity_monitoring: bool = False  # 流动性监控
    max_allowed_slippage: Decimal = Decimal("0.5")  # 最大允许滑点百分比


class IntelligentRiskConfig(BaseModel):
    """智能风控配置"""

    volatility_adjusted_stop_loss: bool = False  # 波动率调整止损
    hedging_protection: bool = False  # 对冲保护


class GlobalRiskControlConfig(BaseModel):
    """全局风控配置"""

    # 各类风控配置
    fund_risk: FundRiskConfig = Field(default_factory=FundRiskConfig)
    time_risk: TimeRiskConfig = Field(default_factory=TimeRiskConfig)
    trade_protection: TradeProtectionConfig = Field(
        default_factory=TradeProtectionConfig
    )
    market_risk: MarketRiskConfig = Field(default_factory=MarketRiskConfig)
    intelligent_risk: IntelligentRiskConfig = Field(
        default_factory=IntelligentRiskConfig
    )

    # 全局风控级别
    risk_level: RiskLevel = RiskLevel.MEDIUM

    # 是否启用全局风控
    enabled: bool = True


class StrategyRiskState(BaseModel):
    """策略风控状态"""

    strategy_id: str
    total_pnl: Decimal = Decimal(0)
    position_value: Decimal = Decimal(0)
    last_trade_time: Optional[float] = None
    trade_count_windows: Dict[str, TimeWindowState] = {}  # 时间窗口内的交易统计
    consecutive_losses: int = 0  # 连续亏损计数
    is_paused_by_risk: bool = False  # 是否因风控被暂停
    pause_reason: Optional[str] = None  # 暂停原因


class GlobalRiskControl:
    """全局风控服务

    该服务提供统一的风控管理，所有策略共享同一套风控规则。
    风控分为系统级、账户级和策略级三个层次，从上到下逐级设置。
    """

    def __init__(self, config: GlobalRiskControlConfig = None):
        """初始化全局风控服务"""
        self.config = config or GlobalRiskControlConfig()
        self.strategy_states: Dict[str, StrategyRiskState] = {}
        self.system_state = {
            "total_position_value": Decimal(0),
            "active_position_coins": 0,
            "current_max_loss": Decimal(0),
            "account_time_windows": {},  # 账户级时间窗口统计
        }
        self.logger = logging.getLogger(__name__)

    def get_config(self) -> GlobalRiskControlConfig:
        """获取当前配置"""
        return self.config

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """更新风控配置"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.logger.info(f"已更新全局风控配置: {new_config}")

    def register_strategy(self, strategy_id: str) -> None:
        """注册新策略到风控系统"""
        if strategy_id not in self.strategy_states:
            self.strategy_states[strategy_id] = StrategyRiskState(
                strategy_id=strategy_id
            )
            self.logger.info(f"已注册策略到风控系统: {strategy_id}")

    def unregister_strategy(self, strategy_id: str) -> None:
        """从风控系统中注销策略"""
        if strategy_id in self.strategy_states:
            del self.strategy_states[strategy_id]
            self.logger.info(f"已从风控系统注销策略: {strategy_id}")

    def update_strategy_state(
        self,
        strategy_id: str,
        total_pnl: Optional[Decimal] = None,
        position_value: Optional[Decimal] = None,
        trade_result: Optional[Decimal] = None,
    ) -> None:
        """更新策略状态

        Args:
            strategy_id: 策略ID
            total_pnl: 策略总盈亏
            position_value: 策略持仓价值
            trade_result: 新的交易结果（盈利为正，亏损为负）
        """
        if strategy_id not in self.strategy_states:
            self.register_strategy(strategy_id)

        state = self.strategy_states[strategy_id]

        if total_pnl is not None:
            state.total_pnl = total_pnl

        if position_value is not None:
            # 更新策略持仓价值
            old_position_value = state.position_value
            state.position_value = position_value

            # 更新系统总持仓价值
            self.system_state["total_position_value"] += (
                position_value - old_position_value
            )

        if trade_result is not None:
            # 记录交易时间
            current_time = time.time()
            state.last_trade_time = current_time

            # 更新连续亏损计数
            if trade_result < 0:
                state.consecutive_losses += 1
                # 更新系统当前最大亏损
                if abs(trade_result) > self.system_state["current_max_loss"]:
                    self.system_state["current_max_loss"] = abs(trade_result)
            else:
                state.consecutive_losses = 0

            # 更新各时间窗口统计
            self._update_time_windows(strategy_id, trade_result, current_time)

    def _update_time_windows(
        self, strategy_id: str, trade_result: Decimal, current_time: float
    ) -> None:
        """更新各时间窗口的统计数据"""
        state = self.strategy_states[strategy_id]

        # 更新策略级时间窗口
        self._update_strategy_time_windows(state, trade_result, current_time)

        # 更新账户级时间窗口
        self._update_account_time_windows(trade_result, current_time)

    def _update_strategy_time_windows(
        self, state: StrategyRiskState, trade_result: Decimal, current_time: float
    ) -> None:
        """更新策略级时间窗口统计"""
        # 检查下单频率限制的时间窗口
        if self.config.trade_protection.order_frequency_limit:
            window_key = "order_frequency"
            window_seconds = self._get_window_seconds(
                self.config.trade_protection.order_frequency_window,
                self.config.trade_protection.order_frequency_window_unit,
            )

            if window_key not in state.trade_count_windows:
                state.trade_count_windows[window_key] = TimeWindowState(
                    start_time=current_time,
                    end_time=current_time + window_seconds,
                    trade_count=1,
                )
            else:
                window = state.trade_count_windows[window_key]

                # 检查是否需要滚动窗口
                if current_time > window.end_time:
                    window.start_time = current_time
                    window.end_time = current_time + window_seconds
                    window.trade_count = 1
                else:
                    window.trade_count += 1

        # 更新连续亏损限制的时间窗口统计
        if self.config.trade_protection.consecutive_loss_limit:
            window_key = "consecutive_loss"
            window_seconds = self._get_window_seconds(
                self.config.trade_protection.consecutive_loss_window,
                self.config.trade_protection.consecutive_loss_window_unit,
            )

            if window_key not in state.trade_count_windows:
                window = TimeWindowState(
                    start_time=current_time,
                    end_time=current_time + window_seconds,
                    consecutive_losses=1 if trade_result < 0 else 0,
                )
                state.trade_count_windows[window_key] = window
            else:
                window = state.trade_count_windows[window_key]

                # 检查是否需要滚动窗口
                if current_time > window.end_time:
                    window.start_time = current_time
                    window.end_time = current_time + window_seconds
                    window.consecutive_losses = 1 if trade_result < 0 else 0
                else:
                    if trade_result < 0:
                        window.consecutive_losses += 1
                    else:
                        window.consecutive_losses = 0

    def _update_account_time_windows(
        self, trade_result: Decimal, current_time: float
    ) -> None:
        """更新账户级时间窗口统计"""
        if self.config.fund_risk.account_loss_limit:
            window_key = str(self.config.fund_risk.account_loss_time_unit)
            window_seconds = self._get_window_seconds(
                1, self.config.fund_risk.account_loss_time_unit
            )

            if window_key not in self.system_state["account_time_windows"]:
                window = TimeWindowState(
                    start_time=current_time,
                    end_time=current_time + window_seconds,
                    total_loss=abs(trade_result) if trade_result < 0 else Decimal(0),
                    total_profit=trade_result if trade_result > 0 else Decimal(0),
                )
                self.system_state["account_time_windows"][window_key] = window
            else:
                window = self.system_state["account_time_windows"][window_key]

                # 检查是否需要滚动窗口
                if current_time > window.end_time:
                    window.start_time = current_time
                    window.end_time = current_time + window_seconds
                    window.total_loss = (
                        abs(trade_result) if trade_result < 0 else Decimal(0)
                    )
                    window.total_profit = (
                        trade_result if trade_result > 0 else Decimal(0)
                    )
                else:
                    if trade_result < 0:
                        window.total_loss += abs(trade_result)
                    else:
                        window.total_profit += trade_result

    def _get_window_seconds(self, value: int, unit: TimeUnit) -> int:
        """将时间单位转换为秒数"""
        if unit == TimeUnit.MINUTE:
            return value * 60
        elif unit == TimeUnit.HOUR:
            return value * 3600
        elif unit == TimeUnit.DAY:
            return value * 86400
        elif unit == TimeUnit.WEEK:
            return value * 604800
        return 3600  # 默认为1小时

    def check_trading_allowed(self, strategy_id: str) -> Tuple[bool, Optional[str]]:
        """检查策略是否允许交易

        Returns:
            Tuple[bool, Optional[str]]: (是否允许交易, 不允许的原因)
        """
        if not self.config.enabled:
            return True, None

        # 检查该策略是否已经被风控暂停
        state = self.strategy_states.get(strategy_id)
        if state and state.is_paused_by_risk:
            return False, state.pause_reason

        # 逐级检查风控规则

        # 1. 系统级风控
        system_allowed, system_reason = self._check_system_risk_limits()
        if not system_allowed:
            return False, system_reason

        # 2. 时间风控
        time_allowed, time_reason = self._check_time_risk_limits()
        if not time_allowed:
            return False, time_reason

        # 3. 策略级风控
        strategy_allowed, strategy_reason = self._check_strategy_risk_limits(
            strategy_id
        )
        if not strategy_allowed:
            # 更新策略风控状态
            if state:
                state.is_paused_by_risk = True
                state.pause_reason = strategy_reason
            return False, strategy_reason

        return True, None

    def _check_system_risk_limits(self) -> Tuple[bool, Optional[str]]:
        """检查系统级风控限制"""
        # 检查系统最大持仓价值
        if (
            self.config.fund_risk.system_max_position_value
            and self.system_state["total_position_value"]
            >= self.config.fund_risk.system_max_position_value
        ):
            return (
                False,
                f"系统持仓价值超过限制: {self.system_state['total_position_value']} > {self.config.fund_risk.system_max_position_value}",
            )

        # 检查系统最大亏损停止
        if (
            self.config.fund_risk.system_max_loss_cutoff
            and self.system_state["current_max_loss"]
            >= self.config.fund_risk.system_max_loss_cutoff
        ):
            return (
                False,
                f"系统亏损超过限制: {self.system_state['current_max_loss']} > {self.config.fund_risk.system_max_loss_cutoff}",
            )

        # 检查账户时间窗口内的亏损限制
        if self.config.fund_risk.account_loss_limit:
            window_key = str(self.config.fund_risk.account_loss_time_unit)
            if window_key in self.system_state["account_time_windows"]:
                window = self.system_state["account_time_windows"][window_key]
                if window.total_loss >= self.config.fund_risk.account_loss_limit:
                    return (
                        False,
                        f"{self._time_unit_to_text(self.config.fund_risk.account_loss_time_unit)}亏损超过限制: {window.total_loss} > {self.config.fund_risk.account_loss_limit}",
                    )

        return True, None

    def _check_time_risk_limits(self) -> Tuple[bool, Optional[str]]:
        """检查时间风控限制"""
        if not self.config.time_risk.trading_time_limit:
            return True, None

        # 检查交易时间限制
        if (
            self.config.time_risk.trading_start_time
            and self.config.time_risk.trading_end_time
        ):
            current_time = datetime.now().strftime("%H:%M:%S")
            if not (
                self.config.time_risk.trading_start_time
                <= current_time
                <= self.config.time_risk.trading_end_time
            ):
                return (
                    False,
                    f"当前时间 {current_time} 不在交易时间范围内: {self.config.time_risk.trading_start_time} - {self.config.time_risk.trading_end_time}",
                )

        # 检查禁止交易的时间点
        if (
            self.config.time_risk.time_point_limit
            and self.config.time_risk.forbidden_time_points
        ):
            current_time = datetime.now().strftime("%H:%M:%S")
            for time_point in self.config.time_risk.forbidden_time_points:
                # 简单实现: 检查当前时间是否在某个时间点前后5分钟内
                time_point_dt = datetime.strptime(time_point, "%H:%M:%S")
                current_dt = datetime.strptime(current_time, "%H:%M:%S")
                buffer_minutes = 5

                time_diff = abs((current_dt - time_point_dt).total_seconds()) / 60
                if time_diff <= buffer_minutes:
                    return (
                        False,
                        f"当前时间 {current_time} 接近禁止交易时间点 {time_point}",
                    )

        return True, None

    def _check_strategy_risk_limits(
        self, strategy_id: str
    ) -> Tuple[bool, Optional[str]]:
        """检查策略级风控限制"""
        if strategy_id not in self.strategy_states:
            return True, None

        state = self.strategy_states[strategy_id]

        # 检查策略总亏损停止阈值
        if (
            self.config.fund_risk.strategy_total_loss_limit
            and state.total_pnl < -self.config.fund_risk.strategy_total_loss_limit
        ):
            return (
                False,
                f"策略总亏损超过限制: {-state.total_pnl} > {self.config.fund_risk.strategy_total_loss_limit}",
            )

        # 检查策略总盈利停止阈值
        if (
            self.config.fund_risk.strategy_total_profit_limit
            and state.total_pnl > self.config.fund_risk.strategy_total_profit_limit
        ):
            return (
                False,
                f"策略总盈利超过限制: {state.total_pnl} > {self.config.fund_risk.strategy_total_profit_limit}",
            )

        # 检查策略最大持仓金额
        if (
            self.config.fund_risk.strategy_max_position
            and state.position_value > self.config.fund_risk.strategy_max_position
        ):
            return (
                False,
                f"策略持仓金额超过限制: {state.position_value} > {self.config.fund_risk.strategy_max_position}",
            )

        # 检查连续亏损限制
        if self.config.trade_protection.consecutive_loss_limit:
            if "consecutive_loss" in state.trade_count_windows:
                window = state.trade_count_windows["consecutive_loss"]
                if (
                    window.consecutive_losses
                    >= self.config.trade_protection.consecutive_loss_limit
                ):
                    return (
                        False,
                        f"连续亏损次数超过限制: {window.consecutive_losses} >= {self.config.trade_protection.consecutive_loss_limit}",
                    )

        # 检查下单频率限制
        if self.config.trade_protection.order_frequency_limit:
            if "order_frequency" in state.trade_count_windows:
                window = state.trade_count_windows["order_frequency"]
                if (
                    window.trade_count
                    >= self.config.trade_protection.order_frequency_limit
                ):
                    window_text = self._get_window_text(
                        self.config.trade_protection.order_frequency_window,
                        self.config.trade_protection.order_frequency_window_unit,
                    )
                    return (
                        False,
                        f"{window_text}内下单次数超过限制: {window.trade_count} >= {self.config.trade_protection.order_frequency_limit}",
                    )

        return True, None

    def _time_unit_to_text(self, unit: TimeUnit) -> str:
        """将时间单位转换为文本描述"""
        if unit == TimeUnit.MINUTE:
            return "每分钟"
        elif unit == TimeUnit.HOUR:
            return "每小时"
        elif unit == TimeUnit.DAY:
            return "每日"
        elif unit == TimeUnit.WEEK:
            return "每周"
        return "未知时间单位"

    def _get_window_text(self, value: int, unit: TimeUnit) -> str:
        """获取时间窗口的文本描述"""
        if unit == TimeUnit.MINUTE:
            return f"{value}分钟"
        elif unit == TimeUnit.HOUR:
            return f"{value}小时"
        elif unit == TimeUnit.DAY:
            return f"{value}天"
        elif unit == TimeUnit.WEEK:
            return f"{value}周"
        return f"{value}小时"

    def reset_strategy_risk_state(self, strategy_id: str) -> None:
        """重置策略的风控状态"""
        if strategy_id in self.strategy_states:
            state = self.strategy_states[strategy_id]
            state.is_paused_by_risk = False
            state.pause_reason = None
            self.logger.info(f"已重置策略风控状态: {strategy_id}")

    def emergency_stop_all(self) -> None:
        """紧急停止所有策略"""
        for strategy_id, state in self.strategy_states.items():
            state.is_paused_by_risk = True
            state.pause_reason = "系统紧急停止"
        self.logger.warning("已执行系统紧急停止，所有策略已暂停")

    def get_risk_status_report(self) -> Dict[str, Any]:
        """获取风控状态报告"""
        report = {
            "system": {
                "total_position_value": float(
                    self.system_state["total_position_value"]
                ),
                "active_position_coins": self.system_state["active_position_coins"],
                "current_max_loss": float(self.system_state["current_max_loss"]),
                "risk_level": self.config.risk_level,
                "enabled": self.config.enabled,
            },
            "strategies": {},
            "paused_strategies": [],
        }

        for strategy_id, state in self.strategy_states.items():
            strategy_report = {
                "total_pnl": float(state.total_pnl),
                "position_value": float(state.position_value),
                "consecutive_losses": state.consecutive_losses,
                "is_paused": state.is_paused_by_risk,
                "pause_reason": state.pause_reason,
                "last_trade_time": state.last_trade_time,
            }
            report["strategies"][strategy_id] = strategy_report

            if state.is_paused_by_risk:
                report["paused_strategies"].append(
                    {"id": strategy_id, "reason": state.pause_reason}
                )

        return report


# 全局风控服务实例
global_risk_control = GlobalRiskControl()
