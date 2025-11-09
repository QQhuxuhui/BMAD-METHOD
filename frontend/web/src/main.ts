import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import 'ant-design-vue/dist/reset.css'
import 'dayjs/locale/zh-cn'
import { MotionPlugin } from '@vueuse/motion'

import App from './App.vue'
import router from './router'
import '@/styles/global.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
// @ts-ignore - Ant Design Vue locale configuration
app.use(Antd, { locale: zhCN })
app.use(MotionPlugin)

app.mount('#app')
