import { Exchange, ProductType } from '../types/exchange';

// 交易所定义配置
export const exchanges: Exchange[] = [
    // 币安 - 全球排名第1
    {
        name: 'binance',
        label: 'Binance',
        ranking: 1,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: true
    },

    // OKX - 全球排名第3-5
    {
        name: 'okx',
        label: 'OKX',
        ranking: 2,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: true
    },

    // Bybit - 全球排名第5-10
    {
        name: 'bybit',
        label: 'Bybit',
        ranking: 3,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: true
    },

    // Gate.io - 全球排名第10-15
    {
        name: 'gate_io',
        label: 'Gate.io',
        ranking: 4,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: true
    },

    // Bitget - 全球排名第10-15
    {
        name: 'bitget',
        label: 'Bitget',
        ranking: 5,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: true
    },

    // KuCoin - 全球排名第10-15
    {
        name: 'kucoin',
        label: 'KuCoin',
        ranking: 6,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: false
    },

    // HTX (原Huobi) - 全球排名第5-10
    {
        name: 'htx',
        label: 'HTX',
        ranking: 7,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Coinbase Advanced Trade - 全球排名第5-10
    {
        name: 'coinbase_advanced_trade',
        label: 'Coinbase',
        ranking: 8,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Kraken - 全球排名第10-15
    {
        name: 'kraken',
        label: 'Kraken',
        ranking: 9,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // MEXC - 全球排名第15-20
    {
        name: 'mexc',
        label: 'MEXC',
        ranking: 10,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Bitstamp - 全球排名第15-20
    {
        name: 'bitstamp',
        label: 'Bitstamp',
        ranking: 11,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // AscendEX - 全球排名第20-30
    {
        name: 'ascend_ex',
        label: 'AscendEX',
        ranking: 12,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // BitMart - 全球排名第20-25
    {
        name: 'bitmart',
        label: 'BitMart',
        ranking: 13,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: false
    },

    // BingX - 全球排名第30-40
    {
        name: 'bing_x',
        label: 'BingX',
        ranking: 14,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // HashKey - 全球排名第30-40
    {
        name: 'hashkey',
        label: 'HashKey',
        ranking: 15,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: false
    },

    // Bitrue - 全球排名第40-50
    {
        name: 'bitrue',
        label: 'Bitrue',
        ranking: 16,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // BTC Markets - 全球排名第50-60
    {
        name: 'btc_markets',
        label: 'BTC Markets',
        ranking: 17,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Cube - 全球排名第60-80
    {
        name: 'cube',
        label: 'Cube',
        ranking: 18,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Tegro - 全球排名第80-100
    {
        name: 'tegro',
        label: 'Tegro',
        ranking: 19,
        type: 'CEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // 去中心化交易所 (DEX)

    // dYdX v4 - DEX排名第1
    {
        name: 'dydx_v4',
        label: 'dYdX v4',
        ranking: 1,
        type: 'DEX',
        productTypes: [
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: true
    },

    // Injective - DEX排名第2
    {
        name: 'injective',
        label: 'Injective',
        ranking: 2,
        type: 'DEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '_v2' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_v2_perpetual' }
        ],
        visible: false
    },

    // Hyperliquid - DEX排名第3
    {
        name: 'hyperliquid',
        label: 'Hyperliquid',
        ranking: 3,
        type: 'DEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' },
            { value: 'perpetual', label: '永续合约', connectorSuffix: '_perpetual' }
        ],
        visible: false
    },

    // XRPL - DEX排名第4
    {
        name: 'xrpl',
        label: 'XRP Ledger',
        ranking: 4,
        type: 'DEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Vertex - DEX排名第5
    {
        name: 'vertex',
        label: 'Vertex',
        ranking: 5,
        type: 'DEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    },

    // Dexalot - DEX排名第6
    {
        name: 'dexalot',
        label: 'Dexalot',
        ranking: 6,
        type: 'DEX',
        productTypes: [
            { value: 'spot', label: '现货', connectorSuffix: '' }
        ],
        visible: false
    }
];

// 获取可见交易所列表
export const getVisibleExchanges = (): Exchange[] => {
    return exchanges.filter(exchange => exchange.visible);
};

// 获取按类型过滤的交易所列表
export const getExchangesByType = (type: 'CEX' | 'DEX'): Exchange[] => {
    return exchanges.filter(exchange => exchange.type === type);
};

// 获取交易所信息
export const getExchangeByName = (name: string): Exchange | undefined => {
    return exchanges.find(exchange => exchange.name === name);
};

// 获取交易所标签
export const getExchangeLabel = (name: string): string => {
    const exchange = getExchangeByName(name);
    return exchange ? exchange.label : name;
};

// 获取产品类型标签
export const getProductTypeLabel = (value: string): string => {
    switch (value) {
        case 'spot': return '现货';
        case 'perpetual': return '永续合约';
        default: return value;
    }
};

// 构建连接器名称
export const buildConnectorName = (exchangeName: string, productType: string): string => {
    const exchange = getExchangeByName(exchangeName);
    if (!exchange) return exchangeName;

    const product = exchange.productTypes.find((p: ProductType) => p.value === productType);
    if (!product) return exchangeName;

    return `${exchangeName}${product.connectorSuffix}`;
};

// 解析连接器名称
export const parseConnectorName = (connector: string): {
    exchangeName: string;
    productType: string;
    exchangeType: 'CEX' | 'DEX';
} => {
    let exchangeName = connector;
    let productType = 'spot';
    let exchangeType: 'CEX' | 'DEX' = 'CEX';

    // 查找匹配的交易所
    for (const exchange of exchanges) {
        // 检查连接器名称是否以交易所名称开头
        if (connector.startsWith(exchange.name)) {
            exchangeName = exchange.name;
            exchangeType = exchange.type;

            // 检查产品类型
            for (const type of exchange.productTypes) {
                const fullConnectorName = `${exchange.name}${type.connectorSuffix}`;
                if (connector === fullConnectorName) {
                    productType = type.value;
                    break;
                }
            }

            break;
        }
    }

    return { exchangeName, productType, exchangeType };
}; 