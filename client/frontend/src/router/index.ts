import { createRouter, createWebHashHistory, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import LoginRegister from '@/views/auth/LoginRegister.vue'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: LoginRegister
    },
    {
        path: '/',
        component: MainLayout,
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/dashboard/Dashboard.vue')
            },
            // 测试路由 - CSS按需加载测试
            {
                path: 'style-test',
                name: 'StyleTest',
                component: () => import('@/components/StyleLoadTest.vue')
            },
            {
                path: 'strategies',
                name: 'Strategies',
                component: () => import('@/views/strategies/StrategyList.vue')
            },
            {
                path: 'strategies/create',
                name: 'CreateStrategy',
                component: () => import('@/views/strategies/CreateStrategy.vue')
            },
            // 旧的策略设置路由，保留用于兼容性，将被弃用
            {
                path: 'strategies/create/:type',
                name: 'OldStrategySettings',
                component: () => import('@/views/strategies/StrategySettings.vue'),
                props: true
            },
            // 新的网格策略路由
            {
                path: 'strategies/grid',
                name: 'GridStrategy',
                component: () => import('@/views/strategies/grid/GridStrategyView.vue'),
                props: true
            },
            // 其他策略类型的专用路由
            {
                path: 'strategies/trend',
                name: 'TrendStrategy',
                component: () => import('@/views/strategies/trend/TrendStrategyView.vue'),
                props: true
            },
            {
                path: 'strategies/scalping',
                name: 'ScalpingStrategy',
                component: () => import('@/views/strategies/scalping/ScalpingStrategyView.vue'),
                props: true
            },
            {
                path: 'strategies/reversal',
                name: 'ReversalStrategy',
                component: () => import('@/views/strategies/reversal/ReversalStrategyView.vue'),
                props: true
            },
            {
                path: 'strategies/news',
                name: 'NewsStrategy',
                component: () => import('@/views/strategies/news/NewsStrategyView.vue'),
                props: true
            },
            {
                path: 'strategies/copy',
                name: 'CopyStrategy',
                component: () => import('@/views/strategies/copy/CopyStrategyView.vue'),
                props: true
            },
            {
                path: 'strategies/create/risk',
                name: 'RiskConfig',
                component: () => import('@/views/strategies/risk/StrategyRiskView.vue'),
                props: true
            },
            {
                path: 'strategies/create/finish',
                name: 'StrategyFinish',
                component: () => import('@/views/strategies/finish/StrategyFinishView.vue'),
                props: true
            },
            {
                path: 'transactions',
                name: 'Transactions',
                component: () => import('@/views/transactions/TransactionRecords.vue')
            },
            {
                path: 'risk',
                name: 'Risk',
                component: () => import('@/views/risk/RiskManagement.vue')
            },
            {
                path: 'account',
                name: 'Account',
                component: () => import('@/views/account/AccountSettings.vue')
            },
            {
                path: 'notifications',
                name: 'Notifications',
                component: () => import('@/views/notifications/NotificationCenter.vue')
            },
            // 添加TV策略路由
            {
                path: 'strategies/create/tv',
                name: 'TVStrategy',
                component: () => import('@/views/strategies/tv/TVStrategyView.vue'),
                props: true
            }
        ]
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 添加路由守卫
router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const isAuthenticated = localStorage.getItem('isAuthenticated')

    if (to.path !== '/login' && !isAuthenticated) {
        next('/login')
    } else if (to.path.includes('/strategies/create/grid') && !to.query.useOldComponent) {
        // 如果是访问旧的网格策略页面且没有指定使用旧组件，重定向到新组件
        next({
            path: '/strategies/grid',
            query: to.query
        })
    } else if (to.path.includes('/strategies/create/trend')) {
        next({
            path: '/strategies/trend',
            query: to.query
        })
    } else if (to.path.includes('/strategies/create/scalping')) {
        next({
            path: '/strategies/scalping',
            query: to.query
        })
    } else if (to.path.includes('/strategies/create/reversal')) {
        next({
            path: '/strategies/reversal',
            query: to.query
        })
    } else if (to.path.includes('/strategies/create/news')) {
        next({
            path: '/strategies/news',
            query: to.query
        })
    } else if (to.path.includes('/strategies/create/copy')) {
        next({
            path: '/strategies/copy',
            query: to.query
        })
    } else if (to.path.includes('/strategies/create/tv') && !to.query.useOldComponent) {
        // 保持在原路径，不做重定向，TV策略使用 strategies/create/tv 路径
        next()
    } else {
        next()
    }
})

export default router 