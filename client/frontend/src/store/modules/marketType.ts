import { defineStore } from 'pinia';

export interface MarketType {
    value: string;
    label: string;
    status?: 'active' | 'unavailable';
}

export interface MarketTypeState {
    marketTypes: MarketType[];
}

// 初始交易类型列表
const initialMarketTypes: MarketType[] = [
    { value: 'spot', label: '现货', status: 'active' },
    { value: 'futures', label: '合约', status: 'active' },
];

export const useMarketTypeStore = defineStore('marketType', {
    state: (): MarketTypeState => ({
        marketTypes: [...initialMarketTypes]
    }),

    getters: {
        getAllMarketTypes: (state) => state.marketTypes,
        getActiveMarketTypes: (state) => state.marketTypes.filter(type => type.status === 'active'),
        getMarketTypeByValue: (state) => {
            return (value: string) => state.marketTypes.find(type => type.value === value);
        }
    },

    actions: {
        // 添加新交易类型
        addMarketType(marketType: MarketType) {
            if (!this.marketTypes.some(type => type.value === marketType.value)) {
                this.marketTypes.push(marketType);
            }
        },

        // 更新交易类型
        updateMarketType(value: string, updates: Partial<MarketType>) {
            const index = this.marketTypes.findIndex(type => type.value === value);
            if (index !== -1) {
                this.marketTypes[index] = {
                    ...this.marketTypes[index],
                    ...updates
                };
            }
        },

        // 删除交易类型
        removeMarketType(value: string) {
            this.marketTypes = this.marketTypes.filter(type => type.value !== value);
        },

        // 设置交易类型状态
        setMarketTypeStatus(value: string, status: 'active' | 'unavailable') {
            const index = this.marketTypes.findIndex(type => type.value === value);
            if (index !== -1) {
                this.marketTypes[index].status = status;
            }
        }
    }
}); 