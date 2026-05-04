import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'

// 页面组件
import Dashboard from './views/Dashboard.vue'
import Todos from './views/Todos.vue'
import Projects from './views/Projects.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/todos', component: Todos },
  { path: '/projects', component: Projects },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
