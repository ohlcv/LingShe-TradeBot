import { defineStore } from 'pinia';
import {
    AppstoreOutlined,
    LineChartOutlined,
    PartitionOutlined,
    ThunderboltOutlined,
    FileTextOutlined,
    TeamOutlined,
    SwapOutlined,
    RobotOutlined
} from '@ant-design/icons-vue';

export interface StrategyType {
    value: string;
    label: string;
    icon: any;
    description: string;
    disabled?: boolean;
    comingSoon?: boolean;
}

// 初始策略类型
const initialActiveTypes: StrategyType[] = [
    {
        value: 'grid',
        label: '网格策略',
        icon: PartitionOutlined,
        description: '自动在价格区间内高抛低吸，适合震荡行情',
        disabled: false,
        comingSoon: false
    },
    {
        value: 'tv',
        label: 'TV策略',
        icon: LineChartOutlined,
        description: '基于TradingView平台信号的自动交易策略',
        disabled: false,
        comingSoon: false
    }
];

// 即将推出的策略类型
const initialComingSoonTypes: StrategyType[] = [
    {
        value: 'ai',
        label: 'AI策略',
        icon: RobotOutlined,
        description: '利用人工智能分析市场数据，自动生成交易信号的高级策略',
        comingSoon: true
    },
    {
        value: 'reversal',
        label: '反转策略',
        icon: SwapOutlined,
        description: '捕捉市场超买超卖点位，逆势而为抢占先机',
        comingSoon: true
    },
    {
        value: 'scalping',
        label: '高频策略',
        icon: ThunderboltOutlined,
        description: '短时间内快速进出，捕捉微小价格波动',
        comingSoon: true
    },
    {
        value: 'arbitrage',
        label: '套利策略',
        icon: SwapOutlined,
        description: '利用不同市场间价格差异获利的交易策略',
        comingSoon: true
    },
    {
        value: 'news',
        label: '新闻策略',
        icon: FileTextOutlined,
        description: '基于市场新闻和事件快速交易，获取信息差收益',
        comingSoon: true
    },
    {
        value: 'copy',
        label: '跟单策略',
        icon: TeamOutlined,
        description: '复制顶级交易者的交易策略和操作，轻松获利',
        comingSoon: true
    },
    {
        value: 'trend',
        label: '趋势策略',
        icon: LineChartOutlined,
        description: '追踪市场趋势，适合单边行情',
        comingSoon: true
    }
];

export interface StrategyState {
    activeStrategyTypes: StrategyType[];
    comingSoonStrategyTypes: StrategyType[];
}

export const useStrategyStore = defineStore('strategy', {
    state: (): StrategyState => ({
        activeStrategyTypes: [...initialActiveTypes],
        comingSoonStrategyTypes: [...initialComingSoonTypes]
    }),

    getters: {
        getAllActiveTypes: (state) => state.activeStrategyTypes,
        getAllComingSoonTypes: (state) => state.comingSoonStrategyTypes,
        getStrategyTypeByValue: (state) => {
            return (value: string) => {
                return [...state.activeStrategyTypes, ...state.comingSoonStrategyTypes]
                    .find(type => type.value === value);
            };
        }
    },

    actions: {
        // 添加新的活跃策略类型
        addActiveStrategyType(strategyType: StrategyType) {
            if (!this.activeStrategyTypes.some(type => type.value === strategyType.value)) {
                this.activeStrategyTypes.push(strategyType);
            }
        },

        // 添加即将推出的策略类型
        addComingSoonStrategyType(strategyType: StrategyType) {
            if (!this.comingSoonStrategyTypes.some(type => type.value === strategyType.value)) {
                this.comingSoonStrategyTypes.push(strategyType);
            }
        },

        // 从即将推出移动到活跃
        promoteToActive(value: string) {
            const typeIndex = this.comingSoonStrategyTypes.findIndex(type => type.value === value);
            if (typeIndex !== -1) {
                const strategyType = { ...this.comingSoonStrategyTypes[typeIndex], comingSoon: false };
                this.comingSoonStrategyTypes.splice(typeIndex, 1);
                this.activeStrategyTypes.push(strategyType);
            }
        },

        // 更新策略类型
        updateStrategyType(value: string, updates: Partial<StrategyType>) {
            let typeIndex = this.activeStrategyTypes.findIndex(type => type.value === value);
            if (typeIndex !== -1) {
                this.activeStrategyTypes[typeIndex] = {
                    ...this.activeStrategyTypes[typeIndex],
                    ...updates
                };
                return;
            }

            typeIndex = this.comingSoonStrategyTypes.findIndex(type => type.value === value);
            if (typeIndex !== -1) {
                this.comingSoonStrategyTypes[typeIndex] = {
                    ...this.comingSoonStrategyTypes[typeIndex],
                    ...updates
                };
            }
        },

        // 删除策略类型
        removeStrategyType(value: string) {
            this.activeStrategyTypes = this.activeStrategyTypes.filter(type => type.value !== value);
            this.comingSoonStrategyTypes = this.comingSoonStrategyTypes.filter(type => type.value !== value);
        }
    }
}); 