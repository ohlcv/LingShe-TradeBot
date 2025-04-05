<template>
  <div class="account-settings">
    <a-card title="账户设置" :bordered="false">
      <a-tabs default-active-key="1">
        <a-tab-pane key="1" tab="个人信息">
          <a-form :model="userForm" layout="vertical">
            <a-form-item label="用户名">
              <a-input v-model:value="userForm.username" disabled />
            </a-form-item>
            <a-form-item label="昵称">
              <a-input v-model:value="userForm.nickname" placeholder="输入昵称" />
            </a-form-item>
            <a-form-item label="邮箱">
              <a-input v-model:value="userForm.email" placeholder="输入邮箱" />
            </a-form-item>
            <a-form-item label="手机号">
              <a-input v-model:value="userForm.phone" placeholder="输入手机号" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary">保存修改</a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>
        
        <a-tab-pane key="2" tab="安全设置">
          <a-list item-layout="horizontal">
            <a-list-item>
              <a-list-item-meta title="修改密码">
                <template #description>定期更换密码可以提高账户安全性</template>
              </a-list-item-meta>
              <template #extra>
                <a-button @click="showChangePasswordModal">修改</a-button>
              </template>
            </a-list-item>
            
            <a-list-item>
              <a-list-item-meta title="双因素认证">
                <template #description>启用双因素认证以提高账户安全性</template>
              </a-list-item-meta>
              <template #extra>
                <a-switch v-model:checked="securitySettings.twoFactorEnabled" />
              </template>
            </a-list-item>
            
            <a-list-item>
              <a-list-item-meta title="登录提醒">
                <template #description>当有新设备登录账户时通过邮件通知</template>
              </a-list-item-meta>
              <template #extra>
                <a-switch v-model:checked="securitySettings.loginAlert" />
              </template>
            </a-list-item>
          </a-list>
        </a-tab-pane>
        
        <a-tab-pane key="3" tab="通知设置">
          <a-list item-layout="horizontal">
            <a-list-item>
              <a-list-item-meta title="交易通知">
                <template #description>当订单执行或取消时发送通知</template>
              </a-list-item-meta>
              <template #extra>
                <a-switch v-model:checked="notificationSettings.tradeNotification" />
              </template>
            </a-list-item>
            
            <a-list-item>
              <a-list-item-meta title="风控预警">
                <template #description>当触发风控预警条件时发送通知</template>
              </a-list-item-meta>
              <template #extra>
                <a-switch v-model:checked="notificationSettings.riskAlert" />
              </template>
            </a-list-item>
            
            <a-list-item>
              <a-list-item-meta title="系统公告">
                <template #description>接收系统更新和维护通知</template>
              </a-list-item-meta>
              <template #extra>
                <a-switch v-model:checked="notificationSettings.systemAnnouncement" />
              </template>
            </a-list-item>
          </a-list>
        </a-tab-pane>
      </a-tabs>
    </a-card>
    
    <!-- 修改密码弹窗 -->
    <a-modal
      v-model:open="passwordModalVisible"
      title="修改密码"
      @ok="handleChangePassword"
      :confirmLoading="confirmLoading"
    >
      <a-form :model="passwordForm" layout="vertical">
        <a-form-item label="当前密码">
          <a-input-password v-model:value="passwordForm.currentPassword" placeholder="输入当前密码" />
        </a-form-item>
        <a-form-item label="新密码">
          <a-input-password v-model:value="passwordForm.newPassword" placeholder="输入新密码" />
        </a-form-item>
        <a-form-item label="确认新密码">
          <a-input-password v-model:value="passwordForm.confirmPassword" placeholder="再次输入新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';

// 用户基本信息
const userForm = reactive({
  username: 'user123',
  nickname: '网格交易者',
  email: 'user@example.com',
  phone: '13800138000'
});

// 安全设置
const securitySettings = reactive({
  twoFactorEnabled: false,
  loginAlert: true
});

// 通知设置
const notificationSettings = reactive({
  tradeNotification: true,
  riskAlert: true,
  systemAnnouncement: true
});

// 确认加载状态
const confirmLoading = ref(false);

// 密码修改弹窗状态
const passwordModalVisible = ref(false);
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 显示修改密码弹窗
const showChangePasswordModal = () => {
  passwordModalVisible.value = true;
};

// 处理修改密码
const handleChangePassword = async () => {
  // 验证
  if (!passwordForm.currentPassword) {
    message.error('请输入当前密码');
    return;
  }
  if (!passwordForm.newPassword) {
    message.error('请输入新密码');
    return;
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    message.error('两次输入的新密码不一致');
    return;
  }

  confirmLoading.value = true;
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    message.success('密码修改成功');
    passwordModalVisible.value = false;
    
    // 重置表单
    passwordForm.currentPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';
  } catch (error) {
    message.error('密码修改失败，请重试');
  } finally {
    confirmLoading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  // 可以添加获取用户信息的逻辑
});
</script>

<style scoped>
.account-settings {
  background-color: #f0f2f5;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
</style> 