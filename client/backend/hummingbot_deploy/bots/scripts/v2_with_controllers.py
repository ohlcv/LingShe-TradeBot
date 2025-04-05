import os
import time
from decimal import Decimal
from typing import Dict, List, Optional, Set

from pydantic import Field

from hummingbot.client.hummingbot_application import HummingbotApplication
from hummingbot.connector.connector_base import ConnectorBase
from hummingbot.core.clock import Clock
from hummingbot.core.data_type.common import OrderType, TradeType
from hummingbot.data_feed.candles_feed.data_types import CandlesConfig
from hummingbot.remote_iface.mqtt import ETopicPublisher
from hummingbot.strategy.strategy_v2_base import StrategyV2Base, StrategyV2ConfigBase
from hummingbot.strategy_v2.models.base import RunnableStatus
from hummingbot.strategy_v2.models.executor_actions import (
    CreateExecutorAction,
    StopExecutorAction,
)


class GenericV2StrategyWithCashOutConfig(StrategyV2ConfigBase):
    """策略配置类，定义策略参数"""

    script_file_name: str = Field(
        default_factory=lambda: os.path.basename(__file__)
    )  # 脚本文件名
    candles_config: List[CandlesConfig] = []  # 蜡烛图配置列表
    markets: Dict[str, Set[str]] = {}  # 交易市场配置
    time_to_cash_out: Optional[int] = None  # 现金退出时间（秒）
    max_global_drawdown: Optional[float] = None  # 全局最大回撤比例
    max_controller_drawdown: Optional[float] = None  # 单个控制器的最大回撤比例
    performance_report_interval: int = 1  # 性能报告间隔（秒）
    rebalance_interval: Optional[int] = None  # 资产再平衡间隔（秒）
    extra_inventory: Optional[float] = 0.02  # 额外库存缓冲比例
    min_amount_to_rebalance_usd: Decimal = Decimal("8")  # 最小再平衡金额（USD）
    asset_to_rebalance: str = "USDT"  # 用于再平衡的基准资产


class GenericV2StrategyWithCashOut(StrategyV2Base):
    """
    带现金退出功能的通用V2策略
    功能：
    - 根据时间自动停止策略
    - 根据最大回撤自动停止
    - 资产再平衡
    - 性能报告
    - MQTT集成
    """

    def __init__(
        self,
        connectors: Dict[str, ConnectorBase],
        config: GenericV2StrategyWithCashOutConfig,
    ):
        """初始化策略实例"""
        super().__init__(connectors, config)
        self.config = config
        self.cashing_out = False  # 现金退出标志
        self.max_pnl_by_controller = {}  # 各控制器的最大盈利记录
        self.performance_reports = {}  # 性能报告数据
        self.max_global_pnl = Decimal("0")  # 全局最大盈利
        self.drawdown_exited_controllers = []  # 因回退退出的控制器列表
        self.closed_executors_buffer: int = 30  # 已关闭执行器的缓冲时间
        self.performance_report_interval: int = self.config.performance_report_interval
        self.rebalance_interval: int = self.config.rebalance_interval
        self._last_performance_report_timestamp = 0  # 上次报告时间
        self._last_rebalance_check_timestamp = 0  # 上次再平衡检查时间
        hb_app = HummingbotApplication.main_application()
        self.mqtt_enabled = hb_app._mqtt is not None  # MQTT是否启用
        self._pub: Optional[ETopicPublisher] = None  # MQTT发布器
        # 计算现金退出时间
        if self.config.time_to_cash_out:
            self.cash_out_time = self.config.time_to_cash_out + time.time()
        else:
            self.cash_out_time = None

    def start(self, clock: Clock, timestamp: float) -> None:
        """启动策略时的初始化操作"""
        self._last_timestamp = timestamp
        self.apply_initial_setting()  # 应用初始设置
        if self.mqtt_enabled:
            self._pub = ETopicPublisher(
                "performance", use_bot_prefix=True
            )  # 初始化MQTT发布器

    async def on_stop(self):
        """策略停止时的清理操作"""
        await super().on_stop()
        if self.mqtt_enabled:
            self._pub({controller_id: {} for controller_id in self.controllers.keys()})
            self._pub = None

    def on_tick(self):
        """每个tick执行的主逻辑"""
        super().on_tick()
        # 生成各控制器的性能报告
        self.performance_reports = {
            controller_id: self.executor_orchestrator.generate_performance_report(
                controller_id=controller_id
            ).dict()
            for controller_id in self.controllers.keys()
        }
        self.control_rebalance()  # 资产再平衡控制
        self.control_cash_out()  # 现金退出控制
        self.control_max_drawdown()  # 最大回撤控制
        self.send_performance_report()  # 发送性能报告

    def control_rebalance(self):
        """资产再平衡逻辑"""
        if (
            self.rebalance_interval
            and self._last_rebalance_check_timestamp + self.rebalance_interval
            <= self.current_timestamp
        ):
            balance_required = {}
            # 计算各控制器需要的资产余额
            for controller_id, controller in self.controllers.items():
                connector_name = controller.config.dict().get("connector_name")
                if connector_name and "perpetual" in connector_name:  # 永续合约跳过
                    continue
                if connector_name not in balance_required:
                    balance_required[connector_name] = {}
                # 获取控制器需要的代币余额
                tokens_required = controller.get_balance_requirements()
                for token, amount in tokens_required:
                    balance_required[connector_name][token] = (
                        balance_required[connector_name].get(token, 0) + amount
                    )

            # 执行再平衡操作
            for connector_name, balance_requirements in balance_required.items():
                connector = self.connectors[connector_name]
                for token, amount in balance_requirements.items():
                    if token == self.config.asset_to_rebalance:
                        continue
                    balance = connector.get_balance(token)
                    trading_pair = f"{token}-{self.config.asset_to_rebalance}"
                    mid_price = connector.get_mid_price(trading_pair)
                    trading_rule = connector.trading_rules[trading_pair]
                    # 计算带安全边际的需求量
                    amount_with_safe_margin = amount * (
                        1 + Decimal(self.config.extra_inventory)
                    )
                    # 获取活跃执行器的未匹配金额
                    active_executors_for_pair = self.filter_executors(
                        executors=self.get_all_executors(),
                        filter_func=lambda x: x.is_active
                        and x.trading_pair == trading_pair
                        and x.connector_name == connector_name,
                    )
                    unmatched_amount = sum(
                        [
                            executor.filled_amount_quote
                            for executor in active_executors_for_pair
                            if executor.side == TradeType.SELL
                        ]
                    ) - sum(
                        [
                            executor.filled_amount_quote
                            for executor in active_executors_for_pair
                            if executor.side == TradeType.BUY
                        ]
                    )
                    balance += unmatched_amount / mid_price
                    base_balance_diff = balance - amount_with_safe_margin
                    abs_balance_diff = abs(base_balance_diff)
                    # 检查交易规则条件
                    trading_rules_condition = (
                        abs_balance_diff > trading_rule.min_order_size
                        and abs_balance_diff * mid_price
                        > trading_rule.min_notional_size
                        and abs_balance_diff * mid_price
                        > self.config.min_amount_to_rebalance_usd
                    )
                    order_type = OrderType.MARKET

                    # 执行卖出或买入操作
                    if base_balance_diff > 0:
                        if trading_rules_condition:
                            self.logger().debug(
                                f"再平衡: 卖出 {amount_with_safe_margin} {token} 兑换 {self.config.asset_to_rebalance}"
                            )
                            connector.sell(
                                trading_pair=trading_pair,
                                amount=abs_balance_diff,
                                order_type=order_type,
                                price=mid_price,
                            )
                    else:
                        # 计算合适的买入数量
                        amount = (
                            max(
                                [
                                    self.config.min_amount_to_rebalance_usd / mid_price,
                                    trading_rule.min_order_size,
                                    trading_rule.min_notional_size / mid_price,
                                ]
                            )
                            if not trading_rules_condition
                            else abs_balance_diff
                        )
                        connector.buy(
                            trading_pair=trading_pair,
                            amount=amount,
                            order_type=order_type,
                            price=mid_price,
                        )
            self._last_rebalance_check_timestamp = self.current_timestamp

    def control_max_drawdown(self):
        """最大回撤控制入口"""
        if self.config.max_controller_drawdown:
            self.check_max_controller_drawdown()  # 检查单个控制器的回撤
        if self.config.max_global_drawdown:
            self.check_max_global_drawdown()  # 检查全局回撤

    def check_max_controller_drawdown(self):
        """检查单个控制器的最大回撤"""
        for controller_id, controller in self.controllers.items():
            controller_pnl = self.performance_reports[controller_id]["global_pnl_quote"]
            last_max_pnl = self.max_pnl_by_controller[controller_id]
            if controller_pnl > last_max_pnl:
                self.max_pnl_by_controller[controller_id] = controller_pnl
            else:
                current_drawdown = last_max_pnl - controller_pnl
                if current_drawdown > self.config.max_controller_drawdown:
                    self.logger().info(f"控制器 {controller_id} 达到最大回撤，停止运行")
                    controller.stop()
                    # 停止未交易的执行器
                    executors_order_placed = self.filter_executors(
                        executors=self.executors_info[controller_id],
                        filter_func=lambda x: x.is_active and not x.is_trading,
                    )
                    self.executor_orchestrator.execute_actions(
                        actions=[
                            StopExecutorAction(
                                controller_id=controller_id, executor_id=executor.id
                            )
                            for executor in executors_order_placed
                        ]
                    )
                    self.drawdown_exited_controllers.append(controller_id)

    def check_max_global_drawdown(self):
        """检查全局最大回撤"""
        current_global_pnl = sum(
            [report["global_pnl_quote"] for report in self.performance_reports.values()]
        )
        if current_global_pnl > self.max_global_pnl:
            self.max_global_pnl = current_global_pnl
        else:
            current_global_drawdown = self.max_global_pnl - current_global_pnl
            if current_global_drawdown > self.config.max_global_drawdown:
                self.drawdown_exited_controllers.extend(list(self.controllers.keys()))
                self.logger().info("达到全局最大回撤，停止策略")
                HummingbotApplication.main_application().stop()

    def send_performance_report(self):
        """通过MQTT发送性能报告"""
        if (
            self.current_timestamp - self._last_performance_report_timestamp
            >= self.performance_report_interval
            and self.mqtt_enabled
        ):
            self._pub(self.performance_reports)
            self._last_performance_report_timestamp = self.current_timestamp

    def control_cash_out(self):
        """现金退出控制主逻辑"""
        self.evaluate_cash_out_time()  # 检查是否到达现金退出时间
        if self.cashing_out:
            self.check_executors_status()  # 检查执行器状态
        else:
            self.check_manual_cash_out()  # 检查手动退出

    def evaluate_cash_out_time(self):
        """评估是否到达预设的现金退出时间"""
        if (
            self.cash_out_time
            and self.current_timestamp >= self.cash_out_time
            and not self.cashing_out
        ):
            self.logger().info("到达现金退出时间，停止所有控制器")
            for controller_id, controller in self.controllers.items():
                if controller.status == RunnableStatus.RUNNING:
                    controller.stop()
            self.cashing_out = True

    def check_manual_cash_out(self):
        """处理手动现金退出请求"""
        for controller_id, controller in self.controllers.items():
            # 处理手动停止开关
            if (
                controller.config.manual_kill_switch
                and controller.status == RunnableStatus.RUNNING
            ):
                self.logger().info(f"手动停止控制器 {controller_id}")
                controller.stop()
                executors_to_stop = self.get_executors_by_controller(controller_id)
                self.executor_orchestrator.execute_actions(
                    [
                        StopExecutorAction(
                            executor_id=executor.id,
                            controller_id=executor.controller_id,
                        )
                        for executor in executors_to_stop
                    ]
                )
            # 处理控制器重启
            if (
                not controller.config.manual_kill_switch
                and controller.status == RunnableStatus.TERMINATED
            ):
                if controller_id in self.drawdown_exited_controllers:
                    continue
                self.logger().info(f"重启控制器 {controller_id}")
                controller.start()

    def check_executors_status(self):
        """检查执行器状态，当所有执行器完成后停止策略"""
        active_executors = self.filter_executors(
            executors=self.get_all_executors(),
            filter_func=lambda executor: executor.status == RunnableStatus.RUNNING,
        )
        if not active_executors:
            self.logger().info("所有执行器已完成，停止策略")
            HummingbotApplication.main_application().stop()
        else:
            # 停止非交易中的执行器
            non_trading_executors = self.filter_executors(
                executors=active_executors,
                filter_func=lambda executor: not executor.is_trading,
            )
            self.executor_orchestrator.execute_actions(
                [
                    StopExecutorAction(
                        executor_id=executor.id, controller_id=executor.controller_id
                    )
                    for executor in non_trading_executors
                ]
            )

    def create_actions_proposal(self) -> List[CreateExecutorAction]:
        """创建执行器提案（需子类实现）"""
        return []

    def stop_actions_proposal(self) -> List[StopExecutorAction]:
        """停止执行器提案（需子类实现）"""
        return []

    def apply_initial_setting(self):
        """应用初始设置（杠杆、仓位模式等）"""
        connectors_position_mode = {}
        for controller_id, controller in self.controllers.items():
            self.max_pnl_by_controller[controller_id] = Decimal("0")
            config_dict = controller.config.dict()
            if "connector_name" in config_dict:
                # 处理永续合约设置
                if self.is_perpetual(config_dict["connector_name"]):
                    if "position_mode" in config_dict:
                        connectors_position_mode[config_dict["connector_name"]] = (
                            config_dict["position_mode"]
                        )
                    if "leverage" in config_dict:
                        self.connectors[config_dict["connector_name"]].set_leverage(
                            leverage=config_dict["leverage"],
                            trading_pair=config_dict["trading_pair"],
                        )
        # 设置仓位模式
        for connector_name, position_mode in connectors_position_mode.items():
            self.connectors[connector_name].set_position_mode(position_mode)
