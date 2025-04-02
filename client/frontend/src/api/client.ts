import axios from 'axios'
import type { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

export const http = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
http.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('token')
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error: AxiosError) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
http.interceptors.response.use(
    (response: AxiosResponse) => {
        return response
    },
    (error: AxiosError) => {
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
                case 500:
                    // 服务器错误
                    console.error('服务器错误')
                    break
                default:
                    console.error('发生错误:', error.response.data)
            }
        }
        return Promise.reject(error)
    }
) 