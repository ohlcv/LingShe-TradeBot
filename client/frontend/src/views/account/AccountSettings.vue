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
        
        <a-tab-pane key="2" tab="API密钥管理">
          <div class="api-keys-section">
            <div class="section-header">
              <h3>API密钥列表</h3>
              <a-button type="primary" @click="showAddKeyModal">添加API密钥</a-button>
            </div>
            
            <a-table
              :columns="apiKeyColumns"
              :dataSource="apiKeys"
              rowKey="id"
              :pagination="{ pageSize: 5 }"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'exchange'">
                  <a-tag :color="getExchangeColor(record.exchange)">{{ record.exchange }}</a-tag>
                </template>
                <template v-else-if="column.key === 'status'">
                  <a-badge :status="record.status === 'active' ? 'success' : 'default'" :text="record.status === 'active' ? '已启用' : '已禁用'" />
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-space>
                    <a-switch
                      :checked="record.status === 'active'"
                      @change="(checked: boolean) => toggleKeyStatus(record, checked)"
                    />
                    <a-button type="link" danger @click="() => deleteApiKey(record)">删除</a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </div>
        </a-tab-pane>
        
        <a-tab-pane key="3" tab="安全设置">
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
        
        <a-tab-pane key="4" tab="通知设置">
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
    
    <!-- API密钥添加弹窗 -->
    <a-modal
      v-model:visible="apiKeyModalVisible"
      title="添加API密钥"
      @ok="handleAddKey"
      :confirmLoading="confirmLoading"
    >
      <a-form :model="newApiKey" layout="vertical">
        <a-form-item label="交易所">
          <a-select v-model:value="newApiKey.exchange" placeholder="选择交易所">
            <a-select-option 
              v-for="exchange in availableExchanges" 
              :key="exchange.value" 
              :value="exchange.value"
            >
              {{ exchange.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="名称">
          <a-input v-model:value="newApiKey.name" placeholder="输入名称" />
        </a-form-item>
        <a-form-item label="API Key">
          <a-input v-model:value="newApiKey.apiKey" placeholder="输入API Key" />
        </a-form-item>
        <a-form-item label="Secret Key">
          <a-input-password v-model:value="newApiKey.secretKey" placeholder="输入Secret Key" />
        </a-form-item>
        <a-form-item label="Passphrase">
          <a-input-password v-model:value="newApiKey.passphrase" placeholder="输入Passphrase（如需）" />
          <div style="font-size: 12px; color: rgba(0, 0, 0, 0.45);">部分交易所（如OKX）需要设置Passphrase</div>
        </a-form-item>
        <a-form-item label="描述">
          <a-input v-model:value="newApiKey.description" placeholder="可选描述" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 修改密码弹窗 -->
    <a-modal
      v-model:visible="passwordModalVisible"
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
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import { useExchangeStore } from '../../store/modules/exchange';

// 使用Pinia store
const exchangeStore = useExchangeStore();

// 获取可用交易所列表
const availableExchanges = computed(() => {
  return exchangeStore.getActiveExchanges;
});

// 用户基本信息
const userForm = reactive({
  username: 'user123',
  nickname: '网格交易者',
  email: 'user@example.com',
  phone: '13800138000'
});

// API密钥列表
const apiKeys = ref([
  {
    id: 1,
    exchange: 'Binance',
    name: '币安主账户',
    apiKey: '3a7d*********************6f5c',
    secretKey: '5e9a*********************8c2d',
    passphrase: '',
    description: '主账户API',
    status: 'active'
  },
  {
    id: 2,
    exchange: 'OKX',
    name: 'OKX测试',
    apiKey: '7b6e*********************9d3a',
    secretKey: '2f8c*********************4b7d',
    passphrase: '******',
    description: '测试账户',
    status: 'inactive'
  }
]);

// API密钥表格列定义
const apiKeyColumns = [
  { title: '交易所', dataIndex: 'exchange', key: 'exchange' },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: 'API Key', dataIndex: 'apiKey', key: 'apiKey' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '状态', key: 'status' },
  { title: '操作', key: 'action' }
];

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

// API密钥弹窗状态
const apiKeyModalVisible = ref(false);
const confirmLoading = ref(false);
const newApiKey = reactive({
  exchange: '',
  name: '',
  apiKey: '',
  secretKey: '',
  passphrase: '',
  description: ''
});

// 密码修改弹窗状态
const passwordModalVisible = ref(false);
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 获取交易所颜色
const getExchangeColor = (exchange: string) => {
  const colors: Record<string, string> = {
    'Binance': 'gold',
    'OKX': 'blue',
    'Huobi': 'green',
    'Gate.io': 'purple'
  };
  return colors[exchange] || 'default';
};

// 显示添加API密钥弹窗
const showAddKeyModal = () => {
  apiKeyModalVisible.value = true;
};

// 添加API密钥
const handleAddKey = () => {
  confirmLoading.value = true;
  
  // 模拟API调用
  setTimeout(() => {
    confirmLoading.value = false;
    apiKeyModalVisible.value = false;
    
    const newId = apiKeys.value.length + 1;
    apiKeys.value.push({
      id: newId,
      exchange: newApiKey.exchange,
      name: newApiKey.name,
      apiKey: newApiKey.apiKey.substring(0, 4) + '*********************' + newApiKey.apiKey.substring(newApiKey.apiKey.length - 4),
      secretKey: newApiKey.secretKey.substring(0, 4) + '*********************' + newApiKey.secretKey.substring(newApiKey.secretKey.length - 4),
      passphrase: newApiKey.passphrase,
      description: newApiKey.description,
      status: 'active'
    });
    
    // 重置表单
    Object.assign(newApiKey, {
      exchange: '',
      name: '',
      apiKey: '',
      secretKey: '',
      passphrase: '',
      description: ''
    });
    
    message.success('API密钥添加成功');
  }, 1000);
};

// 切换API密钥状态
const toggleKeyStatus = (record: any, checked: boolean) => {
  const index = apiKeys.value.findIndex(item => item.id === record.id);
  if (index !== -1) {
    apiKeys.value[index].status = checked ? 'active' : 'inactive';
    message.success(`${record.description || 'API密钥'} ${checked ? '已启用' : '已禁用'}`);
  }
};

// 删除API密钥
const deleteApiKey = (record: any) => {
  apiKeys.value = apiKeys.value.filter(item => item.id !== record.id);
  message.success('API密钥已删除');
};

// 显示修改密码弹窗
const showChangePasswordModal = () => {
  passwordModalVisible.value = true;
};

// 修改密码
const handleChangePassword = () => {
  confirmLoading.value = true;
  
  // 简单验证
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    message.error('两次输入的密码不一致');
    confirmLoading.value = false;
    return;
  }
  
  // 模拟API调用
  setTimeout(() => {
    confirmLoading.value = false;
    passwordModalVisible.value = false;
    
    // 重置表单
    Object.assign(passwordForm, {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    
    message.success('密码修改成功');
  }, 1000);
};

// 组件挂载时加载数据
onMounted(() => {
  // 可以在这里从API获取用户相关设置
  // 这里使用了模拟数据
});
</script>

<style scoped>
.account-settings {
  padding: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
}

.api-keys-section {
  margin-bottom: 24px;
}
</style> 