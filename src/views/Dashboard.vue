<template>
  <div>
    <h2 class="text-xl sm:text-2xl font-bold text-gray-800 mb-6">📊 仪表盘</h2>

    <!-- 统计卡片 — 实时数据 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-xs text-gray-500 mb-1">待办事项</div>
        <div class="text-2xl font-bold text-blue-600">{{ todoStats.pending }} <span class="text-sm font-normal text-gray-400">/ {{ todoStats.total }}</span></div>
        <div class="text-xs text-gray-400 mt-1">{{ todoStats.completed }} 已完成 · {{ todoStats.high }} 高优</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-xs text-gray-500 mb-1">项目管理</div>
        <div class="text-2xl font-bold text-purple-600">{{ projectStats.active }} <span class="text-sm font-normal text-gray-400">/ {{ projectStats.total }}</span></div>
        <div class="text-xs text-gray-400 mt-1">进行中 · {{ projectStats.avgProgress }}% 平均进度</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-xs text-gray-500 mb-1">OKR 目标</div>
        <div class="text-2xl font-bold text-orange-600">{{ okrStats.progress }}%</div>
        <div class="text-xs text-gray-400 mt-1">{{ okrStats.total }} 目标 · {{ okrStats.completed }} 已完成</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-xs text-gray-500 mb-1">今日日程</div>
        <div class="text-2xl font-bold text-green-600">{{ todayEvents.length }}</div>
        <div class="text-xs text-gray-400 mt-1">{{ weekEvents }} 项本周安排</div>
      </div>
    </div>

    <!-- 主体两栏 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左栏：进行中项目 -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800">🚀 进行中项目</h3>
          <router-link to="/projects" class="text-xs text-blue-500 hover:text-blue-700">查看全部 →</router-link>
        </div>
        <div v-if="activeProjectsList.length === 0" class="text-center py-8 text-gray-400 text-sm">暂无进行中项目</div>
        <div v-for="p in activeProjectsList" :key="p.id" class="mb-3 last:mb-0">
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium text-gray-700">{{ p.name }}</span>
            <span class="text-xs text-gray-400">{{ projectProgress(p) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="h-2 rounded-full transition-all" :class="progressBarColor(projectProgress(p))"
              :style="{ width: projectProgress(p) + '%' }"></div>
          </div>
          <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
            <span v-for="oid in (p.okr_ids || [])" :key="oid" class="text-purple-500">🎯 {{ getOKRName(oid) }}</span>
            <span class="ml-auto">{{ getProjectTodoDone(p.id) }}/{{ getProjectTodoCount(p.id) }} 待办</span>
          </div>
        </div>
      </div>

      <!-- 右栏上：OKR 概览 -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800">🎯 OKR 进度概览</h3>
          <router-link to="/okr" class="text-xs text-blue-500 hover:text-blue-700">查看全部 →</router-link>
        </div>
        <div v-if="activeOKRs.length === 0" class="text-center py-8 text-gray-400 text-sm">暂无进行中目标</div>
        <div v-for="obj in activeOKRs" :key="obj.id" class="mb-3 last:mb-0">
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium text-gray-700 truncate mr-2">{{ obj.title }}</span>
            <span class="text-xs text-gray-400 flex-shrink-0">{{ objProgress(obj) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2 mb-1">
            <div class="h-2 rounded-full transition-all" :class="progressBarColor(objProgress(obj))"
              :style="{ width: objProgress(obj) + '%' }"></div>
          </div>
          <!-- KR 迷你条 -->
          <div class="space-y-0.5 mt-1.5">
            <div v-for="kr in (obj.key_results || [])" :key="kr.id" class="flex items-center gap-1.5 text-xs">
              <span class="text-gray-500 w-3 text-right">{{ Math.round(krProgress(kr)) }}%</span>
              <div class="flex-1 bg-gray-100 rounded-full h-1">
                <div class="h-1 rounded-full" :class="krMiniBarColor(krProgress(kr))"
                  :style="{ width: krProgress(kr) + '%' }"></div>
              </div>
              <span class="text-gray-400 truncate max-w-[160px]">{{ kr.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：今日日程 + 临近截止 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <!-- 今日日程 -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800">📅 今日日程 ({{ todayStr }})</h3>
          <router-link to="/calendar" class="text-xs text-blue-500 hover:text-blue-700">日程管理 →</router-link>
        </div>
        <div v-if="todayEvents.length === 0" class="text-center py-6 text-gray-400 text-sm">今日暂无安排 🎉</div>
        <div v-for="ev in todayEvents" :key="ev.id" class="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
          <span class="w-12 text-xs text-gray-500 flex-shrink-0">{{ ev.start_time || '' }}</span>
          <span class="px-1.5 py-0.5 rounded text-[10px] text-white flex-shrink-0" :class="catColor(ev.category)">
            {{ ev.category }}
          </span>
          <span class="text-sm text-gray-700">{{ ev.title }}</span>
          <span v-if="ev.project_id" class="ml-auto text-[10px] text-blue-500 bg-blue-50 px-1.5 py-0.5 rounded flex-shrink-0">
            {{ getProjectName(ev.project_id) }}
          </span>
        </div>
      </div>

      <!-- 临近截止待办 -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800">⏰ 临近截止</h3>
          <router-link to="/todos" class="text-xs text-blue-500 hover:text-blue-700">全部待办 →</router-link>
        </div>
        <div v-if="upcomingTodos.length === 0" class="text-center py-6 text-gray-400 text-sm">暂无临近截止待办</div>
        <div v-for="todo in upcomingTodos.slice(0, 8)" :key="todo.id"
          class="flex items-center gap-2 py-2 border-b border-gray-50 last:border-0">
          <span class="w-16 text-xs flex-shrink-0"
            :class="isOverdue(todo.deadline) ? 'text-red-500 font-medium' : 'text-gray-400'">
            {{ isOverdue(todo.deadline) ? '⚠️ ' : '' }}{{ todo.deadline || '无日期' }}
          </span>
          <span class="text-sm text-gray-700 truncate flex-1">{{ todo.text }}</span>
          <span v-if="todo.project_id" class="text-[10px] text-blue-500 bg-blue-50 px-1.5 py-0.5 rounded flex-shrink-0">
            {{ getProjectName(todo.project_id) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 数据源
const todos = ref([])
const projects = ref([])
const okrs = ref([])
const events = ref([])

// 今天
const todayStr = computed(() => new Date().toISOString().split('T')[0])

onMounted(async () => {
  // 并行加载所有数据
  const fetchers = [
    ['/life-os/data/todos.json', (d) => { todos.value = d }],
    ['/life-os/data/projects.json', (d) => { projects.value = d }],
    ['/life-os/data/okr.json', (d) => { okrs.value = d }],
    ['/life-os/data/events.json', (d) => { events.value = d }],
  ]
  await Promise.all(fetchers.map(async ([url, setter]) => {
    try {
      const res = await fetch(url)
      if (res.ok) setter(await res.json())
    } catch (e) { /* 静默失败，用 localStorage fallback */ }
  }))

  // localStorage fallback
  if (!todos.value.length) {
    const s = localStorage.getItem('life-os-todos'); if (s) todos.value = JSON.parse(s)
  }
  if (!projects.value.length) {
    const s = localStorage.getItem('life-os-projects'); if (s) projects.value = JSON.parse(s)
  }
  if (!okrs.value.length) {
    const s = localStorage.getItem('life-os-okrs'); if (s) okrs.value = JSON.parse(s)
  }
})

// ---- 统计 ----

const todoStats = computed(() => ({
  total: todos.value.length,
  pending: todos.value.filter(t => t.status === 'pending').length,
  completed: todos.value.filter(t => t.status === 'completed').length,
  high: todos.value.filter(t => t.priority === 'high').length,
}))

const projectStats = computed(() => {
  const active = projects.value.filter(p => p.status === 'active')
  const progs = active.map(p => projectProgress(p))
  const avgProgress = progs.length ? Math.round(progs.reduce((a, b) => a + b, 0) / progs.length) : 0
  return {
    total: projects.value.length,
    active: active.length,
    avgProgress,
  }
})

const okrStats = computed(() => {
  const active = okrs.value.filter(o => o.status === 'active')
  const progs = active.map(o => objProgress(o))
  const avgProgress = progs.length ? Math.round(progs.reduce((a, b) => a + b, 0) / progs.length) : 0
  return {
    total: okrs.value.length,
    completed: okrs.value.filter(o => o.status === 'completed').length,
    progress: avgProgress,
  }
})

const todayEvents = computed(() =>
  events.value.filter(e => e.date === todayStr.value).sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''))
)

const weekEvents = computed(() => {
  const now = new Date()
  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay() + 1) // 周一
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6) // 周日
  return events.value.filter(e => {
    const d = new Date(e.date)
    return d >= weekStart && d <= weekEnd
  }).length
})

const upcomingTodos = computed(() =>
  todos.value
    .filter(t => t.status === 'pending' && t.deadline)
    .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))
    .slice(0, 8)
)

// 进行中项目列表
const activeProjectsList = computed(() =>
  projects.value.filter(p => p.status === 'active').slice(0, 5)
)

// 进行中 OKR 列表
const activeOKRs = computed(() =>
  okrs.value.filter(o => o.status === 'active').slice(0, 4)
)

// ---- 辅助函数 ----

function projectProgress(p) {
  if (!p.tasks || p.tasks.length === 0) {
    // 没有子任务时，用关联待办完成率
    const pts = getProjectTodoCount(p.id)
    if (pts === 0) return 0
    return Math.round((getProjectTodoDone(p.id) / pts) * 100)
  }
  return Math.round((p.tasks.filter(t => t.completed).length / p.tasks.length) * 100)
}

function krProgress(kr) {
  if (!kr.target || kr.target === 0) return 0
  return Math.min(100, (kr.current / kr.target) * 100)
}

function objProgress(obj) {
  const krs = obj.key_results || []
  if (krs.length === 0) return obj.status === 'completed' ? 100 : 0
  return Math.round(krs.reduce((s, kr) => s + krProgress(kr), 0) / krs.length)
}

function getProjectTodos(pid) { return todos.value.filter(t => t.project_id === pid) }
function getProjectTodoCount(pid) { return getProjectTodos(pid).length }
function getProjectTodoDone(pid) { return getProjectTodos(pid).filter(t => t.status === 'completed').length }

function getProjectName(pid) {
  const p = projects.value.find(p => p.id === pid)
  return p ? p.name : null
}

function getOKRName(id) {
  const o = okrs.value.find(o => o.id === id)
  return o ? o.title : `目标${id}`
}

function isOverdue(d) { return d ? new Date(d) < new Date(todayStr.value) : false }

function progressBarColor(p) {
  if (p >= 80) return 'bg-green-500'
  if (p >= 40) return 'bg-blue-500'
  return 'bg-yellow-500'
}

function krMiniBarColor(p) {
  if (p >= 80) return 'bg-green-400'
  if (p >= 40) return 'bg-blue-400'
  return 'bg-yellow-400'
}

function catColor(c) {
  return {
    '教学': 'bg-blue-500', '行政': 'bg-gray-500', '科研': 'bg-green-600', '个人': 'bg-pink-500',
  }[c] || 'bg-gray-400'
}
</script>
