<template>
  <Layout class="main-layout">
    <!-- 侧边菜单 -->
    <Layout.Sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sidebar"
    >
      <div class="logo">
        <span v-if="!collapsed">灵蛇交易机器人</span>
      </div>
      <Menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
      >
        <Menu.Item key="dashboard" @click="navigateTo('/dashboard')">
          <template #icon><DashboardOutlined /></template>
          <span>仪表盘</span>
        </Menu.Item>
        
        <!-- 策略列表 -->
        <Menu.Item key="strategy-list" @click="navigateTo('/strategies')">
          <template #icon><AppstoreOutlined /></template>
          <span>策略管理</span>
        </Menu.Item>
        
        <Menu.Item key="transactions" @click="navigateTo('/transactions')">
          <template #icon><TransactionOutlined /></template>
          <span>成交记录</span>
        </Menu.Item>
        <Menu.Item key="risk" @click="navigateTo('/risk')">
          <template #icon><AlertOutlined /></template>
          <span>风控管理</span>
        </Menu.Item>
        <Menu.Item key="account" @click="navigateTo('/account')">
          <template #icon><UserOutlined /></template>
          <span>账户管理</span>
        </Menu.Item>
      </Menu>
    </Layout.Sider>

    <!-- 主内容区域 -->
    <Layout>
      <!-- 顶部导航 -->
      <Layout.Header class="header">
        <div class="header-left">
          <MenuUnfoldOutlined
            v-if="collapsed"
            class="trigger"
            @click="toggleCollapsed"
          />
          <MenuFoldOutlined
            v-else
            class="trigger"
            @click="toggleCollapsed"
          />
          <span class="header-title">{{ getPageTitle() }}</span>
        </div>
        <div class="header-right">
          <Dropdown 
            :trigger="['click']" 
            placement="bottomRight" 
            :getPopupContainer="(triggerNode: HTMLElement) => triggerNode.parentNode as HTMLElement"
          >
            <div 
              class="notification-icon"
              style="display: inline-block; padding: 0 12px;"
            >
              <Badge :count="unreadNotifications" :dot="unreadNotifications > 0">
                <BellOutlined style="font-size: 16px; cursor: pointer;" />
              </Badge>
            </div>
            <template #overlay>
              <Menu style="width: 360px">
                <Menu.Item key="noti-header" style="cursor: default; padding: 8px 12px;">
                  <div class="notification-header">
                    <span class="notification-title">通知</span>
                    <Button type="link" @click="markAllAsRead" size="small">
                      全部已读
                    </Button>
                  </div>
                </Menu.Item>
                <Menu.Divider />
                <div style="max-height: 400px; overflow-y: auto;">
                  <Empty 
                    v-if="notifications.length === 0" 
                    description="暂无通知" 
                    style="padding: 16px 0;"
                  />
                  <Menu.Item 
                    v-for="noti in notifications.slice(0, 5)" 
                    :key="noti.id"
                    :style="!noti.read ? { backgroundColor: '#f0f7ff' } : {}"
                  >
                    <div class="notification-item">
                      <div class="notification-dot" :class="noti.type" v-if="!noti.read" />
                      <div class="notification-content">
                        <div class="notification-item-title">{{ noti.title }}</div>
                        <div class="notification-time">{{ noti.time }}</div>
                      </div>
                    </div>
                  </Menu.Item>
                </div>
                <Menu.Divider />
                <Menu.Item key="view-all">
                  <a @click.stop="viewAllNotifications" style="display: block; text-align: center;">
                    查看所有通知
                  </a>
                </Menu.Item>
              </Menu>
            </template>
          </Dropdown>
          <Dropdown>
            <a class="user-dropdown">
              <UserOutlined style="font-size: 16px;" />
            </a>
            <template #overlay>
              <Menu class="user-menu">
                <Menu.Item key="profile">
                  <UserOutlined />
                  <span class="menu-text">个人信息</span>
                </Menu.Item>
                <Menu.Item key="settings">
                  <SettingOutlined />
                  <span class="menu-text">系统设置</span>
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item key="logout" @click="handleLogout">
                  <LogoutOutlined />
                  <span class="menu-text">退出登录</span>
                </Menu.Item>
              </Menu>
            </template>
          </Dropdown>
        </div>
      </Layout.Header>

      <!-- 内容区域 -->
      <Layout.Content class="content">
        <router-view></router-view>
      </Layout.Content>
    </Layout>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message, Layout, Menu, Dropdown, Badge, Button, Empty } from 'ant-design-vue';
import { useMenuStore } from '@/store/modules/menu';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  AppstoreOutlined,
  AlertOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  TransactionOutlined,
  BellOutlined,
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const menuStore = useMenuStore();

// 侧边栏折叠状态
const collapsed = ref(false);
const toggleCollapsed = () => {
  collapsed.value = !collapsed.value;
};

// 使用Pinia中的selectedKeys
const selectedKeys = computed(() => menuStore.selectedKeys);

// 用户信息
const username = computed(() => {
  return localStorage.getItem('username') || '用户';
});

// 页面挂载时设置当前选中的菜单
onMounted(() => {
  menuStore.updateSelectedKeysByPath(route.path);
});

// 监听路由变化，更新选中菜单
watch(() => route.path, (newPath) => {
  menuStore.updateSelectedKeysByPath(newPath);
}, { immediate: true });

// 导航到指定路由
const navigateTo = (path: string) => {
  router.push(path);
};

// 获取当前页面标题
const getPageTitle = () => {
  const pathMap: Record<string, string> = {
    dashboard: '仪表盘',
    strategies: '策略管理',
    transactions: '成交记录',
    risk: '风控管理',
    account: '账户管理'
  };
  const path = route.path.split('/')[1] || 'dashboard';
  return pathMap[path] || '灵蛇交易机器人';
};

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('username');
  router.push('/login');
};

// 通知接口定义
interface Notification {
  id: number;
  title: string;
  content?: string;
  time: string;
  type: 'success' | 'warning' | 'error' | 'info';
  read: boolean;
  category: 'strategy' | 'risk' | 'system';
}

// 通知相关
const notifications = ref<Notification[]>([
  {
    id: 1,
    title: '策略已启动',
    content: '您的BTC/USDT网格策略已成功启动',
    time: '10分钟前',
    type: 'success',
    read: false,
    category: 'strategy'
  },
  {
    id: 2,
    title: '风控预警',
    content: 'ETH/USDT价格波动超过阈值',
    time: '30分钟前',
    type: 'warning',
    read: false,
    category: 'risk'
  },
  {
    id: 3,
    title: '系统更新',
    content: '系统已更新到最新版本',
    time: '2小时前',
    type: 'info',
    read: true,
    category: 'system'
  }
]);

// 计算未读通知数量
const unreadNotifications = computed(() => {
  return notifications.value.filter(item => !item.read).length;
});

const markAllAsRead = () => {
  notifications.value = notifications.value.map(item => {
    return { ...item, read: true };
  });
  message.success('已将所有通知标记为已读');
};

const viewAllNotifications = () => {
  router.push('/notifications');
};
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.sidebar {
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  z-index: 10;
}

.logo {
  height: 32px;
  margin: 16px;
  color: white;
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.logo img {
  height: 32px;
  margin-right: 8px;
}

.header {
  padding: 0 16px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 9;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  margin-left: 16px;
  font-size: 16px;
  font-weight: bold;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 12px;
  transition: all 0.3s;
}

.user-dropdown:hover {
  background: rgba(0, 0, 0, 0.025);
}

.username {
  margin-left: 8px;
}

.content {
  background: transparent;
  min-height: 280px;
  padding: 0;
  margin: 0;
}

.notification-badge {
  margin-right: 16px;
}

.notification-icon {
  cursor: pointer;
  transition: color 0.3s;
}

.notification-icon:hover {
  color: #1890ff;
}

.notification-menu {
  width: 300px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-title {
  font-weight: 500;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 8px 0;
}

.notification-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  margin-top: 6px;
}

.notification-dot.success {
  background-color: #52c41a;
}

.notification-dot.warning {
  background-color: #faad14;
}

.notification-dot.error {
  background-color: #f5222d;
}

.notification-dot.info {
  background-color: #1890ff;
}

.notification-content {
  flex: 1;
}

.notification-item-title {
  font-weight: 400;
  margin-bottom: 4px;
}

.notification-time {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.notification-footer {
  padding: 12px 16px;
  text-align: center;
}

/* 用户菜单样式 */
.user-menu {
  min-width: 120px;
}

.menu-text {
  white-space: nowrap;
  margin-left: 8px;
}

/* 全局覆盖输入框和选择器聚焦状态的样式 */
:deep(.ant-input:focus),
:deep(.ant-input-focused),
:deep(.ant-input-affix-wrapper:focus),
:deep(.ant-input-affix-wrapper-focused),
:deep(.ant-select-focused .ant-select-selector) {
  background-color: #fff !important;
}

:deep(.ant-select-selector) {
  background-color: #fff !important;
}
</style> 