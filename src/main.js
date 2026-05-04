import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'

// 页面组件
import Dashboard from './views/Dashboard.vue'
import Todos from './views/Todos.vue'
import Projects from './views/Projects.vue'
import Calendar from './views/Calendar.vue'
import OKR from './views/OKR.vue'
import Knowledge from './views/Knowledge.vue'
import Life from './views/Life.vue'
import Finance from './views/Finance.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/okr', component: OKR },
  { path: '/todos', component: Todos },
  { path: '/projects', component: Projects },
  { path: '/calendar', component: Calendar },
  { path: '/knowledge', component: Knowledge },
  { path: '/life', component: Life },
  { path: '/finance', component: Finance },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
