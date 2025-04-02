<template>
  <div class="notification-center">
    <a-card :bordered="false">
      <template #title>
        <div class="page-header">
          <h2>通知中心</h2>
          <div class="header-actions">
            <a-button type="link" @click="markAllAsRead" v-if="hasUnread">
              <template #icon><CheckOutlined /></template>
              全部标记为已读
            </a-button>
            <a-button type="link" @click="clearAllNotifications">
              <template #icon><DeleteOutlined /></template>
              清空通知
            </a-button>
            <a-radio-group v-model:value="filterType" button-style="solid" style="margin-left: 16px">
              <a-radio-button value="all">全部</a-radio-button>
              <a-radio-button value="unread">未读</a-radio-button>
            </a-radio-group>
          </div>
        </div>
      </template>
      
      <!-- 通知类型选择器 -->
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="all" tab="全部通知"></a-tab-pane>
        <a-tab-pane key="strategy" tab="策略通知"></a-tab-pane>
        <a-tab-pane key="risk" tab="风控通知"></a-tab-pane>
        <a-tab-pane key="system" tab="系统通知"></a-tab-pane>
      </a-tabs>
      
      <div class="notification-list">
        <!-- 空状态 -->
        <a-empty v-if="filteredNotifications.length === 0" description="暂无通知" />
        
        <!-- 通知列表 -->
        <a-list
          v-else
          itemLayout="horizontal"
          :dataSource="filteredNotifications"
          :pagination="{ pageSize: 10, showQuickJumper: true }"
        >
          <template #renderItem="{ item }">
            <a-list-item :class="{ 'unread-item': !item.read }">
              <a-list-item-meta>
                <template #avatar>
                  <a-avatar :style="{ backgroundColor: getTypeColor(item.type) }">
                    <template #icon>
                      <CheckCircleOutlined v-if="item.type === 'success'" />
                      <WarningOutlined v-else-if="item.type === 'warning'" />
                      <CloseCircleOutlined v-else-if="item.type === 'error'" />
                      <InfoCircleOutlined v-else />
                    </template>
                  </a-avatar>
                </template>
                <template #title>
                  <div class="notification-title">
                    <span>{{ item.title }}</span>
                    <a-tag v-if="!item.read" color="blue">未读</a-tag>
                  </div>
                </template>
                <template #description>
                  <div class="notification-content">
                    <div class="notification-message">{{ item.content }}</div>
                    <div class="notification-time">{{ item.time }}</div>
                  </div>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-button type="link" @click="markAsRead(item)" v-if="!item.read">
                  标记为已读
                </a-button>
                <a-button type="link" danger @click="deleteNotification(item)">
                  删除
                </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  CheckOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue';

// 通知类型定义
interface Notification {
  id: number;
  title: string;
  content: string;
  time: string;
  type: 'success' | 'warning' | 'error' | 'info';
  read: boolean;
  category: 'strategy' | 'risk' | 'system';
}

// 模拟通知数据
const notifications = ref<Notification[]>([
  {
    id: 1,
    title: '策略已启动',
    content: '您的BTC/USDT网格策略已成功启动，当前价格: 65,421 USDT',
    time: '2023-12-15 10:30:45',
    type: 'success',
    read: false,
    category: 'strategy'
  },
  {
    id: 2,
    title: '风控预警',
    content: 'ETH/USDT价格波动幅度超过20%，触发风控条件',
    time: '2023-12-15 09:45:22',
    type: 'warning',
    read: false,
    category: 'risk'
  },
  {
    id: 3,
    title: '系统更新',
    content: '系统已更新到最新版本v2.3.0，新增多项功能和优化',
    time: '2023-12-14 15:20:10',
    type: 'info',
    read: true,
    category: 'system'
  },
  {
    id: 4,
    title: '订单已成交',
    content: '订单#12345已成功成交，BTC买入0.05个，价格62,150 USDT',
    time: '2023-12-14 14:10:33',
    type: 'success',
    read: true,
    category: 'strategy'
  },
  {
    id: 5,
    title: '风控止损执行',
    content: 'SOL/USDT止损条件已触发，平仓价格: 78.5 USDT',
    time: '2023-12-13 11:05:18',
    type: 'error',
    read: true,
    category: 'risk'
  },
  {
    id: 6,
    title: '服务器维护通知',
    content: '系统将于2023-12-20 03:00-05:00进行服务器维护，期间可能无法访问',
    time: '2023-12-12 16:30:00',
    type: 'info',
    read: true,
    category: 'system'
  }
]);

// 过滤和分类
const activeTab = ref('all');
const filterType = ref('all');

// 筛选后的通知
const filteredNotifications = computed(() => {
  let result = notifications.value;
  
  // 按分类筛选
  if (activeTab.value !== 'all') {
    result = result.filter(item => item.category === activeTab.value);
  }
  
  // 按已读/未读筛选
  if (filterType.value === 'unread') {
    result = result.filter(item => !item.read);
  }
  
  return result;
});

// 是否有未读通知
const hasUnread = computed(() => {
  return notifications.value.some(item => !item.read);
});

// 获取通知类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'success': '#52c41a',
    'warning': '#faad14',
    'error': '#f5222d',
    'info': '#1890ff'
  };
  return colors[type] || '#1890ff';
};

// 标记单个通知为已读
const markAsRead = (notification: Notification) => {
  const index = notifications.value.findIndex(item => item.id === notification.id);
  if (index !== -1) {
    notifications.value[index].read = true;
    message.success('已标记为已读');
  }
};

// 标记所有通知为已读
const markAllAsRead = () => {
  notifications.value.forEach(item => {
    item.read = true;
  });
  message.success('已将所有通知标记为已读');
};

// 删除单个通知
const deleteNotification = (notification: Notification) => {
  notifications.value = notifications.value.filter(item => item.id !== notification.id);
  message.success('通知已删除');
};

// 清空所有通知
const clearAllNotifications = () => {
  notifications.value = [];
  message.success('已清空所有通知');
};

// 组件挂载时从后端获取通知数据
onMounted(() => {
  // 这里可以加载实际的通知数据
  // loadNotifications();
});
</script>

<style scoped>
.notification-center {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.notification-list {
  margin-top: 16px;
}

.notification-title {
  display: flex;
  align-items: center;
}

.notification-title span {
  margin-right: 8px;
}

.notification-content {
  display: flex;
  flex-direction: column;
}

.notification-message {
  margin-bottom: 4px;
}

.notification-time {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.unread-item {
  background-color: #f0f7ff;
}
</style>

 