import { defineStore } from 'pinia';
import { getSupportedExchanges } from '../../api/services/exchange';

export interface ExchangeConfig {
    value: string;
    label: string;
    supportedMarketTypes: string[];
    maxLeverage: number;
    additionalParams: {
        name: string;
        label: string;
        type: string;
        required: boolean;
        description?: string;
    }[];
}

export interface ExchangeConfigState {
    exchangeConfigs: ExchangeConfig[];
    supportedExchanges: string[];
    loading: boolean;
    error: string | null;
}

// 初始交易所配置 - 仅在API请求失败时使用
const initialExchangeConfigs: ExchangeConfig[] = [
    {
        value: 'binance',
        label: 'Binance',
        supportedMarketTypes: ['spot', 'futures'],
        maxLeverage: 125,
        additionalParams: []
    },
    {
        value: 'okx',
        label: 'OKX',
        supportedMarketTypes: ['spot', 'futures'],
        maxLeverage: 100,
        additionalParams: []
    },
    {
        value: 'bitget',
        label: 'Bitget',
        supportedMarketTypes: ['spot', 'futures'],
        maxLeverage: 100,
        additionalParams: []
    },
    {
        value: 'bybit',
        label: 'Bybit',
        supportedMarketTypes: ['spot', 'futures'],
        maxLeverage: 100,
        additionalParams: []
    },
    {
        value: 'dydx',
        label: 'dYdX',
        supportedMarketTypes: ['futures'],
        maxLeverage: 20,
        additionalParams: [
            {
                name: 'stark_private_key',
                label: 'Stark Private Key',
                type: 'text',
                required: true,
                description: 'dYdX Stark Private Key'
            },
            {
                name: 'ethereum_address',
                label: 'Ethereum Address',
                type: 'text',
                required: true,
                description: 'dYdX Ethereum Address'
            }
        ]
    }
];

// 转换Hummingbot交易类型到内部市场类型
const mapTradingTypeToMarketType = (tradingType: string): string => {
    switch (tradingType.toUpperCase()) {
        case 'SPOT':
            return 'spot';
        case 'PERPETUAL':
            return 'futures';
        default:
            return 'spot';
    }
};

export const useExchangeConfigStore = defineStore('exchangeConfig', {
    state: (): ExchangeConfigState => ({
        exchangeConfigs: [...initialExchangeConfigs],
        supportedExchanges: initialExchangeConfigs.map(config => config.value),
        loading: false,
        error: null
    }),

    getters: {
        getAllExchangeConfigs: (state) => state.exchangeConfigs,
        getSupportedExchanges: (state) => state.supportedExchanges,
        getExchangeConfigByValue: (state) => {
            return (value: string) => state.exchangeConfigs.find(config => config.value === value);
        },
        getMaxLeverageByExchange: (state) => {
            return (value: string) => {
                const config = state.exchangeConfigs.find(config => config.value === value);
                return config ? config.maxLeverage : 20; // 默认最大杠杆
            };
        },
        getAdditionalParamsByExchange: (state) => {
            return (value: string) => {
                const config = state.exchangeConfigs.find(config => config.value === value);
                return config ? config.additionalParams : [];
            };
        },
        getSupportedMarketTypesByExchange: (state) => {
            return (value: string) => {
                const config = state.exchangeConfigs.find(config => config.value === value);
                return config ? config.supportedMarketTypes : ['spot']; // 默认支持现货
            };
        },
        isLoading: (state) => state.loading,
        getError: (state) => state.error
    },

    actions: {
        // 添加新的交易所配置
        addExchangeConfig(exchangeConfig: ExchangeConfig) {
            if (!this.exchangeConfigs.some(config => config.value === exchangeConfig.value)) {
                this.exchangeConfigs.push(exchangeConfig);
                this.supportedExchanges.push(exchangeConfig.value);
            }
        },

        // 更新交易所配置
        updateExchangeConfig(value: string, updates: Partial<ExchangeConfig>) {
            const index = this.exchangeConfigs.findIndex(config => config.value === value);
            if (index !== -1) {
                this.exchangeConfigs[index] = {
                    ...this.exchangeConfigs[index],
                    ...updates
                };
            }
        },

        // 删除交易所配置
        removeExchangeConfig(value: string) {
            this.exchangeConfigs = this.exchangeConfigs.filter(config => config.value !== value);
            this.supportedExchanges = this.supportedExchanges.filter(exchange => exchange !== value);
        },

        // 从API更新支持的交易所列表
        async fetchSupportedExchanges() {
            this.loading = true;
            this.error = null;

            try {
                const response = await getSupportedExchanges();

                if (response.data && response.data.success) {
                    const connectorsList = response.data.data.connectors;

                    // 清空现有配置
                    this.exchangeConfigs = [];
                    this.supportedExchanges = [];

                    // 转换API响应为内部配置格式
                    connectorsList.forEach(connector => {
                        // 只处理作为交易所的连接器
                        if (connector.trading_type && connector.trading_type.length > 0) {
                            const supportedMarketTypes = connector.trading_type.map(mapTradingTypeToMarketType);

                            // 映射额外参数 - 注意：这里不再映射额外参数，因为它们已在账户管理界面输入
                            // 我们只需要保存哪些交易所支持哪些交易类型

                            // 创建交易所配置
                            this.addExchangeConfig({
                                value: connector.name.toLowerCase(),
                                label: connector.name,
                                supportedMarketTypes,
                                maxLeverage: connector.maximum_leverage || 1,
                                additionalParams: [] // 清空额外参数，因为它们只在账户设置中使用
                            });
                        }
                    });

                    console.log('成功获取支持的交易所:', this.supportedExchanges);
                } else {
                    throw new Error(response.data.message || '获取交易所列表失败');
                }
            } catch (error) {
                console.error('获取支持的交易所列表失败', error);
                this.error = error instanceof Error ? error.message : '获取交易所列表失败';

                // 回退到硬编码的默认配置
                this.exchangeConfigs = [...initialExchangeConfigs];
                this.supportedExchanges = initialExchangeConfigs.map(config => config.value);
            } finally {
                this.loading = false;
            }
        }
    }
}); 