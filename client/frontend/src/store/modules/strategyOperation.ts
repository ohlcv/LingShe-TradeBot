import { defineStore } from 'pinia'
import { ref } from 'vue'
import { message } from 'ant-design-vue'

export interface Strategy {
    id: string
    name: string
    status: 'running' | 'paused' | 'stopped'
    strategyType: string
    gridType?: 'arithmetic' | 'geometric' | 'custom'
    exchange: string
    pair: string
    marketType: string
    direction: string
    holdingAmount: number
    profit: number
    runningDays: number
    completedOrders: number
    riskConfig?: {
        totalLossLimit: number
        totalProfitLimit: number
        maxLossPerTrade: number
        maxPosition: number
        tradingTimeLimit: boolean
        tradingStartTime?: string
        tradingEndTime?: string
    }
}

export const useStrategyOperationStore = defineStore('strategyOperation', () => {
    // 策略列表
    const strategies = ref<Strategy[]>([])
    const loading = ref(false)
    const error = ref('')

    // 获取策略列表
    const fetchStrategies = async () => {
        // 本地模拟，直接返回内存中的策略列表
        return strategies.value
    }

    // 创建策略
    const createStrategy = async (config: any) => {
        loading.value = true
        try {
            // 生成唯一ID
            const id = Date.now().toString()

            // 创建新策略对象
            const newStrategy: Strategy = {
                id,
                name: config.name || `策略${id.slice(-4)}`,
                status: 'paused',
                strategyType: config.strategyType || 'grid',
                gridType: config.gridConfig?.gridType,
                exchange: config.exchange || 'Binance',
                pair: config.pair || 'BTC/USDT',
                marketType: config.marketType || '永续合约',
                direction: config.direction || '做多',
                holdingAmount: 0,
                profit: 0,
                runningDays: 0,
                completedOrders: 0,
                riskConfig: config.riskConfig
            }

            // 添加到策略列表
            strategies.value.push(newStrategy)

            // 模拟延迟
            await new Promise(resolve => setTimeout(resolve, 500))

            return newStrategy
        } catch (error) {
            console.error('创建策略失败:', error)
            throw new Error('创建策略失败')
        } finally {
            loading.value = false
        }
    }

    // 启动策略
    const startStrategy = async (id: string) => {
        const strategy = strategies.value.find(s => s.id === id)
        if (strategy) {
            strategy.status = 'running'
            await new Promise(resolve => setTimeout(resolve, 300))
            return true
        }
        return false
    }

    // 暂停策略
    const pauseStrategy = async (id: string) => {
        const strategy = strategies.value.find(s => s.id === id)
        if (strategy) {
            strategy.status = 'paused'
            await new Promise(resolve => setTimeout(resolve, 300))
            return true
        }
        return false
    }

    // 删除策略
    const deleteStrategy = async (id: string) => {
        const index = strategies.value.findIndex(s => s.id === id)
        if (index !== -1) {
            strategies.value.splice(index, 1)
            await new Promise(resolve => setTimeout(resolve, 300))
            return true
        }
        return false
    }

    // 获取策略列表的getter
    const getStrategies = () => strategies.value

    return {
        strategies,
        loading,
        error,
        fetchStrategies,
        createStrategy,
        startStrategy,
        pauseStrategy,
        deleteStrategy,
        getStrategies
    }
}) 