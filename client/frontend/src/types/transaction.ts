export interface Transaction {
    id: string;
    orderId: string;
    time: string;
    strategyName: string;
    strategyType: string;
    pair: string;
    type: string;
    direction: string;
    price: number;
    amount: number;
    contracts: number;
    total: number;
    profit: number;
    fee: number;
    systemFee: number;
    status: string;
    exchange: string;
    orderType: string;
    note?: string;
    triggerReason?: string;
} 