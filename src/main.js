import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'

// 页面组件
import Dashboard from './views/Dashboard.vue'
import Todos from './views/Todos.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/todos', component: Todos },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
