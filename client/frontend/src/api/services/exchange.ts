import { http } from '../client';
import type { ApiResponse, ConnectorKeysInfo } from '../types.ts';
import { message } from 'ant-design-vue';

// 交易所账户接口
export interface ConnectorInfo {
    name: string;
    description: string;
    trading_type: string[];
    supported_chains: string[];
    additional_parameters: {
        name: string;
        label?: string;
        type: string;
        required: boolean;
        description?: string;
    }[];
    maximum_leverage?: number;
}

export interface ConnectorListResponse {
    connectors: ConnectorInfo[];
}

export interface AccountInfo {
    account_name: string;
    wallet_address?: string;
    created_at: string;
    updated_at: string;
}

export interface AccountListResponse {
    accounts: AccountInfo[];
}

export interface ConnectorKeysListResponse {
    connectors: ConnectorKeysInfo[];
}

// 验证API密钥的有效性
export interface ValidateApiKeyResponse {
    is_valid: boolean;
    message?: string;
    balance?: {
        total_balance: Record<string, number>;
        available_balance: Record<string, number>;
    };
}

// 账户服务
export const accountService = {
    // 获取账户列表
    async getAccounts(): Promise<string[]> {
        try {
            const response = await http.get<ApiResponse<AccountListResponse>>('/list-accounts');
            if (response && response.data) {
                const data = response.data;
                if (data && typeof data === 'object') {
                    // 兼容直接返回字符串数组的情况
                    if (Array.isArray(data)) {
                        return data;
                    }
                    // 兼容返回AccountListResponse结构的情况
                    if ('accounts' in data && Array.isArray(data.accounts)) {
                        return data.accounts.map((account: any) => account.account_name);
                    }
                }
            }
            return [];
        } catch (error) {
            console.error('获取账户列表失败:', error);
            message.error('获取账户列表失败');
            return [];
        }
    },

    // 添加账户
    async addAccount(accountName: string): Promise<boolean> {
        try {
            await http.post('/add-account', null, {
                params: { account_name: accountName }
            });
            message.success(`账户 ${accountName} 创建成功`);
            return true;
        } catch (error) {
            console.error(`创建账户失败: ${accountName}`, error);
            message.error('创建账户失败');
            return false;
        }
    },

    // 删除账户
    async deleteAccount(accountName: string): Promise<boolean> {
        try {
            await http.post('/delete-account', null, {
                params: { account_name: accountName }
            });
            message.success(`账户 ${accountName} 已删除`);
            return true;
        } catch (error) {
            console.error(`删除账户失败: ${accountName}`, error);
            message.error('删除账户失败');
            return false;
        }
    }
};

// 凭证服务
export const credentialService = {
    // 获取账户凭证
    async getCredentials(accountName: string): Promise<string[]> {
        try {
            const response = await http.get<ApiResponse<any[]>>(`/list-credentials/${accountName}`);
            if (response && response.data) {
                return Array.isArray(response.data) ? response.data : [];
            }
            return [];
        } catch (error) {
            console.error(`获取账户凭证失败: ${accountName}`, error);
            message.error('获取账户凭证失败');
            return [];
        }
    },

    // 添加连接器密钥
    async addConnectorKeys(accountName: string, connectorName: string, keys: Record<string, string>): Promise<boolean> {
        try {
            // 确保移除可能的.yml后缀
            const cleanConnectorName = connectorName.replace(/\.yml$/, '');
            await http.post(`/add-connector-keys/${accountName}/${cleanConnectorName}`, keys);
            return true;
        } catch (error) {
            console.error(`添加密钥失败: ${accountName}/${connectorName}`, error);
            message.error('添加API密钥失败');
            return false;
        }
    },

    // 删除凭证
    async deleteCredential(accountName: string, connectorName: string): Promise<boolean> {
        try {
            // 确保移除可能的.yml后缀
            const cleanConnectorName = connectorName.replace(/\.yml$/, '');
            await http.post(`/delete-credential/${accountName}/${cleanConnectorName}`);
            message.success('API密钥删除成功');
            return true;
        } catch (error) {
            console.error(`删除密钥失败: ${accountName}/${connectorName}`, error);
            message.error('删除API密钥失败');
            return false;
        }
    },

    // 获取账户状态
    async getAccountState() {
        try {
            const response = await http.get('/accounts-state');
            return response.data;
        } catch (error) {
            console.error('获取账户状态失败:', error);
            return null;
        }
    }
};

// 连接器服务
export const connectorService = {
    // 获取支持的连接器
    async getSupportedExchanges() {
        try {
            const response = await http.get<ApiResponse<string[]>>('/available-connectors');
            if (response && response.data) {
                return Array.isArray(response.data) ? response.data : [];
            }
            return [];
        } catch (error) {
            console.error('获取连接器列表失败:', error);
            message.error('获取连接器列表失败');
            return [];
        }
    },

    // 获取连接器配置
    async getConnectorConfig(connectorName: string) {
        try {
            // 确保移除可能的.yml后缀
            const cleanConnectorName = connectorName.replace(/\.yml$/, '');
            const response = await http.get(`/connector-config-map/${cleanConnectorName}`);
            return response.data || [];
        } catch (error) {
            console.error(`获取连接器配置失败: ${connectorName}`, error);
            message.error(`获取连接器 ${connectorName} 配置失败`);
            // 返回空数组而不是抛出错误，防止UI崩溃
            return [];
        }
    },

    // 测试连接
    async testConnection(accountName: string, connectorName: string) {
        try {
            // 确保移除可能的.yml后缀
            const cleanConnectorName = connectorName.replace(/\.yml$/, '');
            const response = await http.get('/accounts-state');
            const accountState = response.data;

            // 首先检查干净的连接器名称 (不含.yml)
            let isConnected = accountState &&
                accountState[accountName] &&
                accountState[accountName][cleanConnectorName] &&
                accountState[accountName][cleanConnectorName].length > 0;

            // 如果找不到，也尝试检查原始连接器名称 (可能含.yml)
            if (!isConnected && connectorName !== cleanConnectorName) {
                isConnected = accountState &&
                    accountState[accountName] &&
                    accountState[accountName][connectorName] &&
                    accountState[accountName][connectorName].length > 0;
            }

            return {
                success: isConnected,
                data: isConnected ?
                    (accountState[accountName][cleanConnectorName] || accountState[accountName][connectorName]) :
                    null
            };
        } catch (error) {
            console.error(`测试连接失败: ${connectorName}`, error);
            return {
                success: false,
                error: error instanceof Error ? error.message : '连接失败'
            };
        }
    }
};

// 为了向后兼容，保留原来的单独导出
export const getSupportedExchanges = connectorService.getSupportedExchanges;
export const listAccounts = accountService.getAccounts;
export const listCredentials = credentialService.getCredentials;
export const deleteConnectorKeys = credentialService.deleteCredential;
