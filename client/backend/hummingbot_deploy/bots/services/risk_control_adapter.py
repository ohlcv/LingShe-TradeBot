from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import logging

from .global_risk_control import (
    global_risk_control,
    GlobalRiskControlConfig,
    FundRiskConfig,
    TimeRiskConfig,
    TradeProtectionConfig,
    MarketRiskConfig,
    IntelligentRiskConfig,
    RiskLevel,
    TimeUnit,
)


class RiskControlAdapter:
    """风控适配器

    用于将全局风控服务集成到现有策略中。
    可以单独使用，也可以作为现有风控配置的替代品。
    """

    def __init__(self, strategy_id: str, use_global_risk_control: bool = True):
        """初始化风控适配器

        Args:
            strategy_id: 策略ID
            use_global_risk_control: 是否使用全局风控服务
        """
        self.strategy_id = strategy_id
        self.use_global_risk_control = use_global_risk_control
        self.logger = logging.getLogger(__name__)

        # 如果使用全局风控，注册到全局风控服务
        if self.use_global_risk_control:
            global_risk_control.register_strategy(self.strategy_id)

    def check_trading_allowed(self) -> Tuple[bool, Optional[str]]:
        """检查策略是否允许交易

        Returns:
            Tuple[bool, Optional[str]]: (是否允许交易, 不允许的原因)
        """
        if not self.use_global_risk_control:
            return True, None

        return global_risk_control.check_trading_allowed(self.strategy_id)

    def update_strategy_state(
        self,
        total_pnl: Optional[Decimal] = None,
        position_value: Optional[Decimal] = None,
        trade_result: Optional[Decimal] = None,
    ) -> None:
        """更新策略状态

        Args:
            total_pnl: 策略总盈亏
            position_value: 策略持仓价值
            trade_result: 新的交易结果（盈利为正，亏损为负）
        """
        if not self.use_global_risk_control:
            return

        global_risk_control.update_strategy_state(
            self.strategy_id,
            total_pnl=total_pnl,
            position_value=position_value,
            trade_result=trade_result,
        )

    def reset_risk_state(self) -> None:
        """重置策略的风控状态"""
        if not self.use_global_risk_control:
            return

        global_risk_control.reset_strategy_risk_state(self.strategy_id)

    def get_risk_status(self) -> Dict[str, Any]:
        """获取策略的风控状态"""
        if not self.use_global_risk_control:
            return {}

        report = global_risk_control.get_risk_status_report()
        if self.strategy_id in report["strategies"]:
            return report["strategies"][self.strategy_id]
        return {}

    def convert_strategy_risk_to_global(
        self, strategy_risk_config: Dict[str, Any]
    ) -> None:
        """将策略特定的风控配置转换为全局风控配置

        这个方法允许将现有策略的风控配置无缝集成到全局风控系统中。

        Args:
            strategy_risk_config: 策略特定的风控配置
        """
        if not self.use_global_risk_control:
            return

        try:
            # 更新资金风控配置
            fund_risk = {}
            if "totalLossLimit" in strategy_risk_config:
                fund_risk["strategy_total_loss_limit"] = Decimal(
                    str(strategy_risk_config["totalLossLimit"])
                )
            if "totalProfitLimit" in strategy_risk_config:
                fund_risk["strategy_total_profit_limit"] = Decimal(
                    str(strategy_risk_config["totalProfitLimit"])
                )
            if "maxLossPerTrade" in strategy_risk_config:
                fund_risk["strategy_max_loss_per_trade"] = Decimal(
                    str(strategy_risk_config["maxLossPerTrade"])
                )
            if "maxPosition" in strategy_risk_config:
                fund_risk["strategy_max_position"] = Decimal(
                    str(strategy_risk_config["maxPosition"])
                )

            # 更新时间风控配置
            time_risk = {}
            if "tradingTimeLimit" in strategy_risk_config:
                time_risk["trading_time_limit"] = strategy_risk_config[
                    "tradingTimeLimit"
                ]
            if "tradingStartTime" in strategy_risk_config:
                time_risk["trading_start_time"] = str(
                    strategy_risk_config["tradingStartTime"]
                )
            if "tradingEndTime" in strategy_risk_config:
                time_risk["trading_end_time"] = str(
                    strategy_risk_config["tradingEndTime"]
                )
            if "timePointLimit" in strategy_risk_config:
                time_risk["time_point_limit"] = strategy_risk_config["timePointLimit"]
            if "forbiddenTimePoints" in strategy_risk_config:
                time_risk["forbidden_time_points"] = strategy_risk_config[
                    "forbiddenTimePoints"
                ]

            # 更新交易保护配置
            trade_protection = {}
            if "consecutiveLossLimit" in strategy_risk_config:
                trade_protection["consecutive_loss_limit"] = strategy_risk_config[
                    "consecutiveLossLimit"
                ]
            if "consecutiveLossWindow" in strategy_risk_config:
                trade_protection["consecutive_loss_window"] = strategy_risk_config[
                    "consecutiveLossWindow"
                ]
            if "consecutiveLossWindowUnit" in strategy_risk_config:
                trade_protection["consecutive_loss_window_unit"] = (
                    self._convert_time_unit(
                        strategy_risk_config["consecutiveLossWindowUnit"]
                    )
                )
            if "orderFrequencyLimit" in strategy_risk_config:
                trade_protection["order_frequency_limit"] = strategy_risk_config[
                    "orderFrequencyLimit"
                ]
            if "orderFrequencyWindow" in strategy_risk_config:
                trade_protection["order_frequency_window"] = strategy_risk_config[
                    "orderFrequencyWindow"
                ]
            if "orderFrequencyWindowUnit" in strategy_risk_config:
                trade_protection["order_frequency_window_unit"] = (
                    self._convert_time_unit(
                        strategy_risk_config["orderFrequencyWindowUnit"]
                    )
                )

            # 更新智能风控配置
            intelligent_risk = {}
            if "volatilityAdjustedStopLoss" in strategy_risk_config:
                intelligent_risk["volatility_adjusted_stop_loss"] = (
                    strategy_risk_config["volatilityAdjustedStopLoss"]
                )
            if "hedgingProtection" in strategy_risk_config:
                intelligent_risk["hedging_protection"] = strategy_risk_config[
                    "hedgingProtection"
                ]

            # 更新全局风控配置
            updates = {}
            if fund_risk:
                updates["fund_risk"] = global_risk_control.config.fund_risk.copy(
                    update=fund_risk
                )
            if time_risk:
                updates["time_risk"] = global_risk_control.config.time_risk.copy(
                    update=time_risk
                )
            if trade_protection:
                updates["trade_protection"] = (
                    global_risk_control.config.trade_protection.copy(
                        update=trade_protection
                    )
                )
            if intelligent_risk:
                updates["intelligent_risk"] = (
                    global_risk_control.config.intelligent_risk.copy(
                        update=intelligent_risk
                    )
                )

            if updates:
                global_risk_control.update_config(updates)
                self.logger.info(
                    f"已将策略 {self.strategy_id} 的风控配置转换为全局风控配置"
                )

        except Exception as e:
            self.logger.error(f"转换风控配置时出错: {e}")

    def _convert_time_unit(self, unit_str: str) -> TimeUnit:
        """将字符串时间单位转换为TimeUnit枚举"""
        if unit_str == "minutes":
            return TimeUnit.MINUTE
        elif unit_str == "hours":
            return TimeUnit.HOUR
        elif unit_str == "days":
            return TimeUnit.DAY
        elif unit_str == "weeks":
            return TimeUnit.WEEK
        return TimeUnit.HOUR  # 默认为小时

    def cleanup(self) -> None:
        """清理资源"""
        if self.use_global_risk_control:
            global_risk_control.unregister_strategy(self.strategy_id)
            self.logger.info(f"已注销策略 {self.strategy_id} 的风控服务")
