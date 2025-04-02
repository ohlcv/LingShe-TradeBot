import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface GridLevel {
    level: number
    openRatio: number
    openReboundRatio: number
    size: number
    status: string
    editable: boolean
    takeProfitLevels: TakeProfitLevel[]
}

export interface TakeProfitLevel {
    level: number
    ratio: number
    reboundRatio: number
    portion: number
    status: string
}

export interface GridConfig {
    gridType: 'arithmetic' | 'geometric' | 'custom'
    investment: number
    gridCount: number
    upperPrice: number
    lowerPrice: number
    takeProfitType: 'grid' | 'global'
    gridLevels: {
        level: number
        openRatio: number
        openReboundRatio: number
        size: number
        status: string
        editable: boolean
        takeProfitLevels: {
            price: number
            ratio: number
        }[]
    }[]
}

export interface RiskConfig {
    totalLossLimit: number
    totalProfitLimit: number
    maxLossPerTrade: number
    maxPosition: number
    tradingTimeLimit: boolean
    tradingStartTime?: string
    tradingEndTime?: string
}

export interface StrategyCreationState {
    // 基本设置
    strategyName: string
    strategyType: string
    exchange: string
    marketType: string
    direction: string
    baseCurrency: string
    quoteCurrency: string

    // 网格策略配置
    gridConfig: GridConfig | null

    // 风控配置
    riskConfig: RiskConfig | null
}

export const useStrategyCreationStore = defineStore('strategyCreation', () => {
    // 基本信息
    const name = ref('')
    const strategyType = ref('')
    const exchange = ref('')
    const pair = ref('')
    const marketType = ref('')
    const direction = ref('')

    // 网格配置
    const gridConfig = ref<GridConfig | null>(null)

    // 风控配置
    const riskConfig = ref<RiskConfig | null>(null)

    // 重置所有状态
    const resetAll = () => {
        name.value = ''
        strategyType.value = ''
        exchange.value = ''
        pair.value = ''
        marketType.value = ''
        direction.value = ''
        gridConfig.value = null
        riskConfig.value = null
    }

    // 设置基本信息
    const setBasicInfo = (info: {
        name: string
        strategyType: string
        exchange: string
        pair: string
        marketType: string
        direction: string
    }) => {
        name.value = info.name
        strategyType.value = info.strategyType
        exchange.value = info.exchange
        pair.value = info.pair
        marketType.value = info.marketType
        direction.value = info.direction
    }

    // 设置网格配置
    const setGridConfig = (config: GridConfig) => {
        gridConfig.value = config
    }

    // 设置风控配置
    const setRiskConfig = (config: RiskConfig) => {
        riskConfig.value = config
    }

    return {
        // 状态
        name,
        strategyType,
        exchange,
        pair,
        marketType,
        direction,
        gridConfig,
        riskConfig,

        // 方法
        resetAll,
        setBasicInfo,
        setGridConfig,
        setRiskConfig
    }
}) 