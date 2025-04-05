"""
风控服务API

提供HTTP API接口，用于管理全局风控配置。
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from decimal import Decimal
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


# API路由
router = APIRouter(
    prefix="/risk",
    tags=["risk_management"],
    responses={404: {"description": "Not found"}},
)

# 日志器
logger = logging.getLogger(__name__)


# API模型
class RiskStatusResponse(BaseModel):
    """风控状态响应"""

    enabled: bool
    risk_level: str
    system_total_pnl: float
    system_position_value: float
    strategies_status: Dict[str, Dict[str, Any]]
    trading_allowed: bool


class RiskConfigResponse(BaseModel):
    """风控配置响应"""

    enabled: bool
    risk_level: str
    fund_risk: Dict[str, Any]
    time_risk: Dict[str, Any]
    trade_protection: Dict[str, Any]
    intelligent_risk: Dict[str, Any]


class UpdateRiskConfigRequest(BaseModel):
    """更新风控配置请求"""

    enabled: Optional[bool] = None
    risk_level: Optional[str] = None
    fund_risk: Optional[Dict[str, Any]] = None
    time_risk: Optional[Dict[str, Any]] = None
    trade_protection: Optional[Dict[str, Any]] = None
    intelligent_risk: Optional[Dict[str, Any]] = None


class StrategyRiskUpdateRequest(BaseModel):
    """策略风控状态更新请求"""

    total_pnl: Optional[float] = None
    position_value: Optional[float] = None
    trade_result: Optional[float] = None


class EmergencyStopResponse(BaseModel):
    """紧急停止响应"""

    success: bool
    affected_strategies: List[str]


@router.get("/status", response_model=RiskStatusResponse)
async def get_risk_status():
    """获取当前风控状态"""
    status = global_risk_control.get_risk_status_report()

    # 转换为API响应格式
    response = {
        "enabled": global_risk_control.enabled,
        "risk_level": global_risk_control.risk_level.name,
        "system_total_pnl": float(global_risk_control.system_total_pnl),
        "system_position_value": float(global_risk_control.system_position_value),
        "strategies_status": {},
        "trading_allowed": global_risk_control.is_trading_allowed(),
    }

    # 添加策略状态
    for strategy_id, strategy_status in global_risk_control.strategies.items():
        response["strategies_status"][strategy_id] = {
            "total_pnl": float(strategy_status.get("total_pnl", 0)),
            "position_value": float(strategy_status.get("position_value", 0)),
            "last_trade_result": (
                float(strategy_status.get("last_trade_result", 0))
                if strategy_status.get("last_trade_result") is not None
                else None
            ),
            "trading_allowed": global_risk_control.is_trading_allowed(strategy_id),
        }

    return response


@router.get("/config", response_model=RiskConfigResponse)
async def get_risk_config():
    """获取当前风控配置"""
    config = global_risk_control.get_config()

    # 转换为API响应格式
    response = {
        "enabled": config.get("enabled", True),
        "risk_level": config.get("risk_level", RiskLevel.MEDIUM).name,
        "fund_risk": {
            "system_max_position_value": float(
                config.get("fund_risk", {}).get("system_max_position_value", 0)
            ),
            "system_max_loss_cutoff": float(
                config.get("fund_risk", {}).get("system_max_loss_cutoff", 0)
            ),
        },
        "time_risk": config.get("time_risk", {}),
        "trade_protection": config.get("trade_protection", {}),
        "intelligent_risk": config.get("intelligent_risk", {}),
    }

    return response


@router.post("/config", response_model=RiskConfigResponse)
async def update_risk_config(request: UpdateRiskConfigRequest):
    """更新风控配置"""
    # 构建更新配置
    update_config = {}

    if request.enabled is not None:
        update_config["enabled"] = request.enabled

    if request.risk_level is not None:
        try:
            update_config["risk_level"] = RiskLevel[request.risk_level]
        except KeyError:
            raise HTTPException(
                status_code=400, detail=f"无效的风险级别: {request.risk_level}"
            )

    if request.fund_risk is not None:
        # 转换数值为Decimal
        fund_risk = {}
        for key, value in request.fund_risk.items():
            if isinstance(value, (int, float)):
                fund_risk[key] = Decimal(str(value))
            else:
                fund_risk[key] = value
        update_config["fund_risk"] = fund_risk

    if request.time_risk is not None:
        update_config["time_risk"] = request.time_risk

    if request.trade_protection is not None:
        update_config["trade_protection"] = request.trade_protection

    if request.intelligent_risk is not None:
        update_config["intelligent_risk"] = request.intelligent_risk

    # 更新配置
    global_risk_control.update_config(update_config)
    logger.info(f"已更新风控配置: {update_config}")

    # 返回更新后的配置
    return await get_risk_config()


@router.get("/strategy/{strategy_id}")
async def get_strategy_risk_status(strategy_id: str):
    """获取特定策略的风控状态"""
    if strategy_id not in global_risk_control.strategies:
        raise HTTPException(status_code=404, detail=f"策略未找到: {strategy_id}")

    strategy_status = global_risk_control.strategies[strategy_id]

    return {
        "strategy_id": strategy_id,
        "total_pnl": float(strategy_status.get("total_pnl", 0)),
        "position_value": float(strategy_status.get("position_value", 0)),
        "last_trade_result": (
            float(strategy_status.get("last_trade_result", 0))
            if strategy_status.get("last_trade_result") is not None
            else None
        ),
        "trading_allowed": global_risk_control.is_trading_allowed(strategy_id),
    }


@router.post("/strategy/{strategy_id}/update")
async def update_strategy_risk_state(
    strategy_id: str, request: StrategyRiskUpdateRequest
):
    """更新策略风控状态"""
    # 如果策略不存在，创建
    if strategy_id not in global_risk_control.strategies:
        global_risk_control.strategies[strategy_id] = {}

    # 更新策略状态
    if request.total_pnl is not None:
        global_risk_control.strategies[strategy_id]["total_pnl"] = Decimal(
            str(request.total_pnl)
        )

    if request.position_value is not None:
        global_risk_control.strategies[strategy_id]["position_value"] = Decimal(
            str(request.position_value)
        )

    if request.trade_result is not None:
        global_risk_control.strategies[strategy_id]["last_trade_result"] = Decimal(
            str(request.trade_result)
        )

    # 更新全局状态
    global_risk_control._update_system_stats()

    logger.info(f"已更新策略 {strategy_id} 风控状态")

    return {"status": "success", "message": f"已更新策略 {strategy_id} 风控状态"}


@router.post("/strategy/{strategy_id}/reset")
async def reset_strategy_risk_state(strategy_id: str):
    """重置策略风控状态"""
    if strategy_id in global_risk_control.strategies:
        global_risk_control.strategies[strategy_id] = {
            "total_pnl": Decimal("0"),
            "position_value": Decimal("0"),
            "last_trade_result": None,
        }

        # 更新全局状态
        global_risk_control._update_system_stats()

        logger.info(f"已重置策略 {strategy_id} 风控状态")

    return {"status": "success", "message": f"已重置策略 {strategy_id} 风控状态"}


@router.post("/emergency-stop", response_model=EmergencyStopResponse)
async def emergency_stop():
    """执行紧急停止"""
    affected_strategies = global_risk_control.emergency_stop_all()
    logger.warning(f"已执行紧急停止，影响策略: {affected_strategies}")

    return {"success": True, "affected_strategies": affected_strategies}


@router.get("/check/{strategy_id}")
async def check_trading_allowed(strategy_id: str):
    """检查特定策略是否允许交易"""
    allowed = global_risk_control.is_trading_allowed(strategy_id)
    reason = ""

    if not allowed:
        reason = global_risk_control.get_trading_disallowed_reason(strategy_id)

    return {"strategy_id": strategy_id, "trading_allowed": allowed, "reason": reason}


def init_app(app):
    """初始化应用，注册路由器"""
    from main import get_auth  # 导入认证依赖

    # 为所有路由添加认证依赖
    for route in router.routes:
        # 确保路由有dependencies属性
        if not hasattr(route, "dependencies") or route.dependencies is None:
            route.dependencies = []
        # 添加认证依赖
        route.dependencies.append(Depends(get_auth))

    # 注册路由
    app.include_router(router)
    logger.info("风控服务API已初始化，已为所有路由添加认证依赖")
