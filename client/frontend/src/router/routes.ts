// 假设这里有一个风控管理路由
{
    path: '/risk',
        name: 'RiskManagement',
            component: () => import('@/views/risk/RiskManagement.vue'),
                meta: {
        title: '风控管理',
            icon: 'safety-outlined',
                roles: ['admin']
    }
},
// 添加交易所管理路由
{
    path: '/exchange',
        name: 'ExchangeManagement',
            component: () => import('@/views/exchange/ExchangeManagement.vue'),
                meta: {
        title: '交易所管理',
            icon: 'bank-outlined',
                roles: ['admin']
    }
}, 