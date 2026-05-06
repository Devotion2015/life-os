<template>
  <!-- 未登录 → 登录门 -->
  <LoginGate v-if="authenticated === false" @login="authenticated = true" />

  <!-- 加载中 -->
  <div v-else-if="authenticated === null" class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-gray-400 text-lg">⏳ 加载中...</div>
  </div>

  <!-- 已登录 → 完整应用 -->
  <div v-else class="min-h-screen bg-gray-50">
    <!-- Mobile: backdrop overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity"
      @click="sidebarOpen = false"
    />

    <!-- 侧边栏 -->
    <aside
      class="fixed left-0 top-0 h-full w-64 bg-white shadow-lg border-r border-gray-200 z-50 transition-transform duration-300 flex flex-col -translate-x-full lg:translate-x-0"
      :class="{ '!translate-x-0': sidebarOpen, 'lg:!w-16': sidebarCollapsed }"
    >
      <!-- 头部 -->
      <div class="p-6 border-b border-gray-200 flex-shrink-0" :class="{ 'lg:!p-3': sidebarCollapsed }">
        <div class="flex items-center justify-between">
          <div v-if="!sidebarCollapsed" class="overflow-hidden min-w-0">
            <h1 class="text-xl font-bold text-gray-800 truncate">🚪 阿财的任意门</h1>
            <p class="text-sm text-gray-500 mt-1 truncate">Personal Life OS</p>
          </div>
          <div v-else class="text-center w-full">
            <span class="text-xl">🚪</span>
          </div>
          <!-- 移动端关闭按钮 -->
          <button
            @click="sidebarOpen = false"
            class="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors lg:hidden"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <!-- 桌面端折叠按钮 -->
          <button
            @click="toggleCollapse"
            class="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors hidden lg:block flex-shrink-0"
            :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
          >
            <svg v-if="!sidebarCollapsed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 导航 -->
      <nav class="p-4 flex-1 overflow-y-auto">
        <ul class="space-y-2">
          <li v-for="item in navItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
              :class="{ 'lg:justify-center lg:px-2': sidebarCollapsed }"
              @click="onNavClick"
            >
              <span class="text-lg flex-shrink-0">{{ item.icon }}</span>
              <span v-if="!sidebarCollapsed" class="ml-3 truncate">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main
      class="p-4 md:p-8 transition-all duration-300 lg:ml-64"
      :class="{ 'lg:!ml-16': sidebarCollapsed }"
    >
      <!-- 移动端顶部栏 -->
      <div class="lg:hidden sticky top-0 z-30 bg-gray-50 pb-3 pt-2 -mx-4 px-4 flex items-center gap-3">
        <button
          @click="sidebarOpen = true"
          class="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
          aria-label="打开菜单"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="text-lg font-bold text-gray-800">🚪 阿财的任意门</h1>
      </div>

      <router-view @refresh-data="refreshAllData"></router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import LoginGate from './components/LoginGate.vue'
import { AUTH_HASH } from './config.js'

// 认证状态：null=加载中 / false=未登录 / true=已登录
const authenticated = ref(null)

// 移动端：抽屉打开/关闭
const sidebarOpen = ref(false)

// 桌面端：侧边栏折叠/展开（持久化到 localStorage）
const sidebarCollapsed = ref(false)

const navItems = [
  { path: '/', icon: '📊', label: '仪表盘' },
  { path: '/okr', icon: '🎯', label: '目标 OKR' },
  { path: '/projects', icon: '📋', label: '项目管理' },
  { path: '/todos', icon: '✅', label: '待办事项' },
  { path: '/calendar', icon: '📅', label: '日程管理' },
  { path: '/finance', icon: '💰', label: '财务管理' },
  { path: '/knowledge', icon: '📚', label: '知识管理' },
  { path: '/life', icon: '🎮', label: '娱乐生活' },
]

onMounted(() => {
  // 恢复侧边栏折叠状态
  const saved = localStorage.getItem('life-os-sidebar-collapsed')
  if (saved !== null) {
    sidebarCollapsed.value = saved === 'true'
  }

  // 认证检查：localStorage 已有 token
  const stored = localStorage.getItem('life-os-auth')
  if (stored === AUTH_HASH) {
    authenticated.value = true
  } else {
    authenticated.value = false
  }
})

watch(sidebarCollapsed, (val) => {
  localStorage.setItem('life-os-sidebar-collapsed', String(val))
})

function toggleCollapse() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function refreshAllData() {
  const keys = ['life-os-todos', 'life-os-projects', 'life-os-okrs', 'life-os-events',
    'life-os-finance', 'life-os-knowledge', 'life-os-life']
  keys.forEach(k => localStorage.removeItem(k))
  window.location.reload()
}

function onNavClick() {
  sidebarOpen.value = false
}
</script>
