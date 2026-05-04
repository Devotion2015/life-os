<template>
  <div class="min-h-screen bg-gray-50">
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
      <div class="lg:hidden mb-4 flex items-center gap-3">
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

      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

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
  const saved = localStorage.getItem('life-os-sidebar-collapsed')
  if (saved !== null) {
    sidebarCollapsed.value = saved === 'true'
  }
})

watch(sidebarCollapsed, (val) => {
  localStorage.setItem('life-os-sidebar-collapsed', String(val))
})

function toggleCollapse() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function onNavClick() {
  // 移动端点击导航后自动关闭侧边栏
  sidebarOpen.value = false
}
</script>
