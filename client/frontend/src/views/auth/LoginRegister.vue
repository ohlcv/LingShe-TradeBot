<template>
  <div class="login-register-container">
    <div class="form-container">
      <h2>{{ isLogin ? '登录' : '注册' }} - 灵蛇交易机器人</h2>
      <a-form
        :model="formData"
        :rules="rules"
        ref="formRef"
        layout="vertical"
      >
        <a-form-item 
          name="username" 
          label="用户名"
        >
          <a-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item 
          name="password"
          label="密码"
        >
          <a-input-password
            v-model:value="formData.password"
            placeholder="请输入密码"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <template v-if="!isLogin">
          <a-form-item 
            name="email"
            label="邮箱"
          >
            <a-input
              v-model:value="formData.email"
              placeholder="请输入邮箱"
            >
              <template #prefix>
                <MailOutlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item 
            name="invitationCode"
            label="邀请码"
          >
            <a-input
              v-model:value="formData.invitationCode"
              placeholder="请输入邀请码"
              @change="handleInvitationCodeChange"
            />
          </a-form-item>

          <a-form-item name="agreeTerms">
            <a-checkbox v-model:checked="formData.agreeTerms">
              我已阅读并同意
              <a @click.prevent="showTerms">用户协议</a>
              和
              <a @click.prevent="showPrivacy">隐私政策</a>
            </a-checkbox>
          </a-form-item>
        </template>

        <a-form-item>
          <a-button
            type="primary"
            :loading="loading"
            block
            @click="isLogin ? handleLogin() : handleRegister()"
          >
            {{ isLogin ? '登录' : '注册' }}
          </a-button>
        </a-form-item>

        <div class="switch-form">
          <a @click="isLogin = !isLogin">
            {{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}
          </a>
        </div>
      </a-form>
    </div>

    <a-modal
      v-model:visible="termsVisible"
      title="用户协议"
      :footer="null"
      width="700px"
    >
      <div v-html="termsContent"></div>
    </a-modal>
    
    <a-modal
      v-model:visible="privacyVisible"
      title="隐私政策"
      :footer="null"
      width="700px"
    >
      <div v-html="privacyContent"></div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons-vue'
import { useRouter } from 'vue-router'
import type { Rule } from 'ant-design-vue/es/form'

const router = useRouter()
const formRef = ref()

const isLogin = ref(true)
const loading = ref(false)
const termsVisible = ref(false)
const privacyVisible = ref(false)
const termsContent = ref('用户协议内容...')
const privacyContent = ref('隐私政策内容...')

const formData = reactive({
  username: '',
  password: '',
  email: '',
  invitationCode: '',
  agreeTerms: false,
  remember: false
})

const rules: Record<string, Rule[]> = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, message: '用户名至少3个字符' }
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6个字符' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  invitationCode: [
    // 移除必填规则
  ],
  agreeTerms: [
    { 
      validator: async (_rule: any, value: boolean) => {
        if (!value) {
          return Promise.reject('请阅读并同意用户协议和隐私政策')
        }
        return Promise.resolve()
      }
    }
  ]
}

const handleLogin = async () => {
  try {
    loading.value = true
    await formRef.value?.validateFields()
    // 这里会调用登录API
    console.log('登录信息:', {
      username: formData.username,
      password: formData.password
    })
    // 临时模拟登录成功
    setTimeout(() => {
      loading.value = false
      // 设置认证状态
      localStorage.setItem('isAuthenticated', 'true')
      localStorage.setItem('username', formData.username)
      // 导航到仪表盘
      router.push('/dashboard')
    }, 1000)
  } catch (error: any) {
    loading.value = false
    console.error('登录失败:', error)
  }
}

const handleRegister = async () => {
  try {
    loading.value = true
    await formRef.value?.validateFields()
    // 这里会调用注册API
    console.log('注册信息:', {
      username: formData.username,
      password: formData.password,
      email: formData.email,
      invitationCode: formData.invitationCode,
      agreeTerms: formData.agreeTerms
    })
    // 临时模拟注册成功
    setTimeout(() => {
      loading.value = false
      isLogin.value = true
    }, 1000)
  } catch (error: any) {
    loading.value = false
    console.error('注册失败:', error)
  }
}

const handleInvitationCodeChange = (e: any) => {
  const value = e.target.value
  if (value.length === 8) {
    // 这里会验证邀请码
    console.log('验证邀请码:', value)
  }
}

const showTerms = () => {
  termsVisible.value = true
}

const showPrivacy = () => {
  privacyVisible.value = true
}
</script>

<style scoped>
.login-register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 20px;
}

.form-container {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-container h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #1890ff;
}

.switch-form {
  text-align: center;
  margin-top: 16px;
}

.switch-form a {
  color: #1890ff;
  cursor: pointer;
}

.switch-form a:hover {
  text-decoration: underline;
}
</style> 