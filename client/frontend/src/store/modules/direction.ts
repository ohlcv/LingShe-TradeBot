import { defineStore } from 'pinia';

export interface Direction {
    value: string;
    label: string;
    status?: 'active' | 'unavailable';
}

export interface DirectionState {
    directions: Direction[];
}

// 初始持仓方向列表
const initialDirections: Direction[] = [
    { value: 'long', label: '做多', status: 'active' },
    { value: 'short', label: '做空', status: 'active' },
    { value: 'both', label: '双向持仓', status: 'active' },
];

export const useDirectionStore = defineStore('direction', {
    state: (): DirectionState => ({
        directions: [...initialDirections]
    }),

    getters: {
        getAllDirections: (state) => state.directions,
        getActiveDirections: (state) => state.directions.filter(dir => dir.status === 'active'),
        getDirectionByValue: (state) => {
            return (value: string) => state.directions.find(dir => dir.value === value);
        }
    },

    actions: {
        // 添加新持仓方向
        addDirection(direction: Direction) {
            if (!this.directions.some(dir => dir.value === direction.value)) {
                this.directions.push(direction);
            }
        },

        // 更新持仓方向
        updateDirection(value: string, updates: Partial<Direction>) {
            const index = this.directions.findIndex(dir => dir.value === value);
            if (index !== -1) {
                this.directions[index] = {
                    ...this.directions[index],
                    ...updates
                };
            }
        },

        // 删除持仓方向
        removeDirection(value: string) {
            this.directions = this.directions.filter(dir => dir.value !== value);
        },

        // 设置持仓方向状态
        setDirectionStatus(value: string, status: 'active' | 'unavailable') {
            const index = this.directions.findIndex(dir => dir.value === value);
            if (index !== -1) {
                this.directions[index].status = status;
            }
        }
    }
}); 