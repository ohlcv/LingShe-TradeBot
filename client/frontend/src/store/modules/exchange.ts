import { defineStore } from 'pinia';

export interface Exchange {
    value: string;
    label: string;
    status?: 'active' | 'maintenance' | 'unavailable';
    logo?: string;
}

export interface ExchangeState {
    exchanges: Exchange[];
}

// 初始交易所列表
const initialExchanges: Exchange[] = [
    { value: 'binance', label: 'Binance', status: 'active' },
    { value: 'okx', label: 'OKX', status: 'active' },
    { value: 'bitget', label: 'Bitget', status: 'active' },
];

export const useExchangeStore = defineStore('exchange', {
    state: (): ExchangeState => ({
        exchanges: [...initialExchanges]
    }),

    getters: {
        getAllExchanges: (state) => state.exchanges,
        getActiveExchanges: (state) => state.exchanges.filter(exchange => exchange.status === 'active'),
        getExchangeByValue: (state) => {
            return (value: string) => state.exchanges.find(exchange => exchange.value === value);
        }
    },

    actions: {
        // 添加新交易所
        addExchange(exchange: Exchange) {
            if (!this.exchanges.some(e => e.value === exchange.value)) {
                this.exchanges.push(exchange);
            }
        },

        // 更新交易所
        updateExchange(value: string, updates: Partial<Exchange>) {
            const index = this.exchanges.findIndex(exchange => exchange.value === value);
            if (index !== -1) {
                this.exchanges[index] = {
                    ...this.exchanges[index],
                    ...updates
                };
            }
        },

        // 删除交易所
        removeExchange(value: string) {
            this.exchanges = this.exchanges.filter(exchange => exchange.value !== value);
        },

        // 设置交易所状态
        setExchangeStatus(value: string, status: 'active' | 'maintenance' | 'unavailable') {
            const index = this.exchanges.findIndex(exchange => exchange.value === value);
            if (index !== -1) {
                this.exchanges[index].status = status;
            }
        }
    }
}); 