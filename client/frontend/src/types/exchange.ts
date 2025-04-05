// 交易所类型定义
export interface Exchange {
    name: string;           // 交易所代码名称，如 'binance'
    label: string;          // 显示名称，如 'Binance'
    ranking: number;        // 交易所排名
    type: 'CEX' | 'DEX';    // 交易所类型：CEX(中心化) 或 DEX(去中心化)
    productTypes: ProductType[]; // 支持的产品类型
    visible: boolean;       // 是否在界面上显示
}

// 产品类型定义
export interface ProductType {
    value: string;          // 产品类型值，如 'spot' 或 'perpetual'
    label: string;          // 显示名称，如 '现货' 或 '永续合约'
    connectorSuffix: string; // 连接器名称后缀，如 '' 或 '_perpetual'
}

// 凭证状态
export type CredentialStatus = 'connected' | 'pending' | 'error';

// 凭证信息
export interface Credential {
    accountName: string;    // 账户名称
    connector: string;      // 连接器名称
    exchange: string;       // 交易所名称
    productType: string;    // 产品类型
    status: CredentialStatus; // 凭证状态
    keys: Record<string, string>; // API密钥字段
    type: 'CEX' | 'DEX';    // 交易所类型
} 