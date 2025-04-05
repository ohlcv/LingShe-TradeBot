// API响应的通用接口
export interface ApiResponse<T = any> {
    success: boolean;
    message?: string;
    data: T;
}

// API密钥信息接口
export interface ConnectorKeysInfo {
    connector: string;
    account_name: string;
    trading_type: string;
    api_key?: string;
    chain?: string;
    other_values?: Record<string, string>;
    created_at: string;
    updated_at: string;
} 