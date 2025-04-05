import axios from 'axios'
import type { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// 创建axios实例，使用Nginx反向代理
export const http = axios.create({
    // 使用/api前缀，由Nginx转发并添加认证
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 30000,
    // 确保cookie不被发送，避免一些CORS问题
    withCredentials: false,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

// 创建一个全局的取消令牌存储
const pendingRequests = new Map();

// 生成请求的唯一标识符
const getRequestKey = (config: InternalAxiosRequestConfig) => {
    const { url, method, params, data } = config;
    return `${method}:${url}:${JSON.stringify(params)}:${JSON.stringify(data)}`;
};

// 请求拦截器 - 添加Basic认证
http.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 添加取消令牌
        const requestKey = getRequestKey(config);

        // 如果已存在相同的请求，取消它
        if (pendingRequests.has(requestKey)) {
            const controller = pendingRequests.get(requestKey);
            controller.abort();
            pendingRequests.delete(requestKey);
        }

        // 创建新的AbortController并存储
        const controller = new AbortController();
        config.signal = controller.signal;
        pendingRequests.set(requestKey, controller);

        // 添加Basic认证
        const username = 'admin';
        const password = 'admin';
        const base64Credentials = btoa(`${username}:${password}`);
        if (config.headers) {
            config.headers['Authorization'] = `Basic ${base64Credentials}`;
        }

        // 确保请求有正确的Content-Type
        if (config.method?.toLowerCase() === 'post' && config.headers) {
            // 默认所有POST请求使用JSON格式
            if (!config.headers['Content-Type']) {
                config.headers['Content-Type'] = 'application/json';
            }
        }

        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
)

// 响应拦截器
http.interceptors.response.use(
    (response: AxiosResponse) => {
        // 请求成功，从pendingRequests中删除
        const requestKey = getRequestKey(response.config as InternalAxiosRequestConfig);
        pendingRequests.delete(requestKey);
        return response;
    },
    (error: AxiosError) => {
        // 即使是错误响应，也需要清理pendingRequests
        if (error.config) {
            const requestKey = getRequestKey(error.config as InternalAxiosRequestConfig);
            pendingRequests.delete(requestKey);
        }

        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 未授权，清除token并跳转到登录页
                    localStorage.removeItem('token')
                    window.location.href = '/auth'
                    break
                case 403:
                    // 权限不足
                    console.error('权限不足')
                    break
                case 404:
                    // 资源不存在
                    console.error('请求的资源不存在')
                    break
                case 405:
                    // 方法不允许（OPTIONS 预检请求被拒绝）
                    console.error('请求方法不被允许，可能是CORS预检请求被拒绝')
                    break
                case 500:
                    // 服务器错误
                    console.error('服务器错误')
                    break
                default:
                    console.error('发生错误:', error.response.data)
            }
        } else if (error.request) {
            // 请求已发送但没有收到响应
            console.error('服务器无响应，请检查网络连接')
        } else {
            // 请求配置出错
            console.error('请求配置错误:', error.message)
        }
        return Promise.reject(error)
    }
)

// 定义一个清理函数，在应用关闭或页面刷新时取消所有挂起的请求
export const cleanupPendingRequests = () => {
    for (const controller of pendingRequests.values()) {
        controller.abort();
    }
    pendingRequests.clear();
};

// 在应用卸载时清理挂起的请求
if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', cleanupPendingRequests);
} 