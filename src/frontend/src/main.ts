import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import { router } from './router'
import * as echarts from 'echarts'
import './style.css'

const app = createApp(App)
app.provide('echarts', echarts)
app.use(ElementPlus).use(router).mount('#app')
