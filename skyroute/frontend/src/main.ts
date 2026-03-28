import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

import { Ion } from 'cesium'
Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkODg4MmNkMy02YzVjLTQ2ZDItYThiYy03MmNjNTk5ZWRmYzciLCJpZCI6NDA0NTMyLCJpYXQiOjE3NzM2NjcyNDl9.FySpItA3WmgjP7dZvTquwoujQ1IbqZa72VadnCd3rmI'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus, { size: 'small', zIndex: 3000 })

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
