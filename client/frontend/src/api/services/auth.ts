import { http } from '../client'

export interface LoginParams {
    username: string
    password: string
    remember?: boolean
}

export interface RegisterParams {
    username: string
    password: string
    email: string
    invitationCode: string
    agreeTerms: boolean
}

export interface TermsResponse {
    content: string
}

export const authService = {
    // 登录
    async login(params: LoginParams) {
        const response = await http.post('/api/auth/login/', params)
        return response.data
    },

    // 注册
    async register(params: RegisterParams) {
        const response = await http.post('/api/auth/register/', params)
        return response.data
    },

    // 验证邀请码
    async validateInvitationCode(code: string) {
        const response = await http.get(`/api/auth/validate-invitation/${code}/`)
        return response.data
    },

    // 忘记密码
    async forgotPassword(email: string) {
        return http.post('/api/v1/auth/forgot-password', { email })
    },

    // 重置密码
    async resetPassword(token: string, newPassword: string) {
        return http.post('/api/v1/auth/reset-password', { token, newPassword })
    },

    // 获取用户协议
    async getTerms(): Promise<TermsResponse> {
        const response = await http.get('/api/auth/terms/')
        return response.data
    },

    // 获取隐私政策
    async getPrivacy(): Promise<TermsResponse> {
        const response = await http.get('/api/auth/privacy/')
        return response.data
    }
} 