import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { cleanupPendingRequests } from './api/client'
import axios from 'axios'
import { message } from 'ant-design-vue'

// 导入基础样式
import 'ant-design-vue/dist/reset.css' // Ant Design Vue基础样式
import './assets/css/global.css'

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
    console.error('Vue应用错误:', err)
    console.error('错误信息:', info)
    // 可以在这里添加错误上报逻辑
}

// 添加应用卸载处理
const cleanupApp = () => {
    // 清理所有挂起的请求
    cleanupPendingRequests()
    console.log('应用资源已清理')
}

// 在窗口卸载时清理资源
window.addEventListener('beforeunload', cleanupApp)

// 保存原始的unmount方法
const originalUnmount = app.unmount

// 重写unmount方法，在卸载前执行清理
app.unmount = function () {
    // 先清理资源
    cleanupApp()
    // 然后调用原始的unmount方法
    originalUnmount.apply(this)
}

app.use(createPinia())
app.use(router)

// 创建全局API客户端
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
})

// 添加请求拦截器，为所有请求添加Basic认证头
apiClient.interceptors.request.use(config => {
    // 设置Basic认证头
    const auth = 'Basic ' + btoa('admin:admin')
    config.headers.Authorization = auth
    return config
}, error => {
    return Promise.reject(error)
})

// 添加响应拦截器，处理常见错误
apiClient.interceptors.response.use(
    response => response,
    error => {
        // 处理401错误
        if (error.response && error.response.status === 401) {
            console.error('认证失败:', error)
            message.error('API认证失败，请刷新页面或联系管理员')
        }

        // 处理网络错误
        if (!error.response) {
            console.error('网络错误:', error)

            // 处理Chrome扩展错误
            if (error.message && error.message.includes('message port closed')) {
                console.warn('检测到Chrome扩展通信错误，这通常是由于页面通信问题或长时间无响应导致')
                message.error('页面通信中断，请刷新页面后重试')
            } else {
                message.error('网络连接失败，请检查网络连接或API服务是否可用')
            }
        }

        return Promise.reject(error)
    }
)

// 设置全局请求超时
apiClient.defaults.timeout = 30000; // 30秒超时

// 将apiClient注入到全局属性中
app.config.globalProperties.$api = apiClient

app.mount('#app') 