import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { message } from 'ant-design-vue'

// 创建axios实例
const http: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
http.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 从localStorage获取token
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
        const { data } = response
        // 如果响应成功，直接返回数据
        if (data.code === 0) {
            return data.data
        }
        // 否则显示错误信息
        message.error(data.message || '请求失败')
        return Promise.reject(new Error(data.message || '请求失败'))
    },
    (error: AxiosError) => {
        // 处理HTTP错误
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 未授权，清除token并跳转到登录页
                    localStorage.removeItem('token')
                    window.location.href = '/login'
                    break
                case 403:
                    message.error('没有权限访问')
                    break
                case 404:
                    message.error('请求的资源不存在')
                    break
                case 500:
                    message.error('服务器错误')
                    break
                default:
                    message.error('网络错误')
            }
        } else {
            message.error('网络连接失败')
        }
        return Promise.reject(error)
    }
)

export { http }