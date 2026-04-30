<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <aside class="fixed left-0 top-0 h-full w-64 bg-white shadow-lg border-r border-gray-200">
      <div class="p-6 border-b border-gray-200">
        <h1 class="text-xl font-bold text-gray-800">🚪 阿财的任意门</h1>
        <p class="text-sm text-gray-500 mt-1">Personal Life OS</p>
      </div>
      <nav class="p-4">
        <ul class="space-y-2">
          <li>
            <router-link to="/" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">📊</span>
              <span>仪表盘</span>
            </router-link>
          </li>
          <li>
            <router-link to="/okr" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">🎯</span>
              <span>目标 OKR</span>
            </router-link>
          </li>
          <li>
            <router-link to="/projects" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">📋</span>
              <span>项目管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/todos" class="flex items-center px-4 py-3 bg-blue-50 text-blue-700 rounded-lg font-medium">
              <span class="mr-3">✅</span>
              <span>待办事项</span>
            </router-link>
          </li>
          <li>
            <router-link to="/calendar" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">📅</span>
              <span>日程管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/finance" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">💰</span>
              <span>财务管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/knowledge" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">📚</span>
              <span>知识管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/life" class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
              <span class="mr-3">🎮</span>
              <span>娱乐生活</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main class="ml-64 p-8">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
</script>
