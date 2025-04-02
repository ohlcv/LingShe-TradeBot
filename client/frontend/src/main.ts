import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 导入基础样式
import 'ant-design-vue/dist/reset.css' // Ant Design Vue基础样式
import './assets/css/global.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app') 