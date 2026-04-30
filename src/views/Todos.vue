<template>
  <div>
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">✅ 待办事项</h2>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-lg shadow p-3 sm:p-4 mb-6">
      <div class="flex flex-col sm:flex-row gap-3">
        <select v-model="filterStatus" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="all">全部状态</option>
          <option value="pending">待完成</option>
          <option value="completed">已完成</option>
        </select>
        <select v-model="filterPriority" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="all">全部优先级</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索待办..."
          class="w-full sm:flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
    </div>

    <!-- 统计 -->
    <div class="mt-6 bg-white rounded-lg shadow p-4">
      <div class="flex justify-around text-center">
        <div>
          <div class="text-xl sm:text-2xl font-bold text-gray-800">{{ todos.length }}</div>
          <div class="text-xs sm:text-sm text-gray-500">全部待办</div>
        </div>
        <div>
          <div class="text-xl sm:text-2xl font-bold text-blue-600">{{ pendingCount }}</div>
          <div class="text-xs sm:text-sm text-gray-500">待完成</div>
        </div>
        <div>
          <div class="text-xl sm:text-2xl font-bold text-green-600">{{ completedCount }}</div>
          <div class="text-xs sm:text-sm text-gray-500">已完成</div>
        </div>
        <div>
          <div class="text-xl sm:text-2xl font-bold text-red-600">{{ highCount }}</div>
          <div class="text-xs sm:text-sm text-gray-500">高优先级</div>
        </div>
      </div>
    </div>

    <!-- 待办列表 -->
    <div class="space-y-3 mt-6">
      <div
        v-for="todo in filteredTodos"
        :key="todo.id"
        class="bg-white rounded-lg shadow p-3 sm:p-4 hover:shadow-md transition-shadow"
        :class="{ 'opacity-50': todo.status === 'completed' }"
      >
        <div class="flex items-start gap-3">
          <button
            @click="toggleTodo(todo)"
            class="w-6 h-6 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-colors mt-0.5"
            :class="todo.status === 'completed' ? 'bg-green-500 border-green-500' : 'border-gray-300 hover:border-green-500'"
          >
            <span v-if="todo.status === 'completed'" class="text-white text-sm">✓</span>
          </button>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-gray-800 break-words" :class="{ 'line-through': todo.status === 'completed' }">
              {{ todo.text }}
            </div>
            <div class="flex flex-wrap items-center gap-2 mt-2 text-xs sm:text-sm text-gray-500">
              <span v-if="todo.semester" class="bg-gray-100 px-2 py-0.5 rounded">{{ todo.semester }}</span>
              <span v-if="todo.deadline">📅 {{ todo.deadline }}</span>
              <span
                class="px-2 py-0.5 rounded text-white"
                :class="{
                  'bg-red-500': todo.priority === 'high',
                  'bg-yellow-500': todo.priority === 'medium',
                  'bg-gray-400': todo.priority === 'low'
                }"
              >
                {{ priorityText(todo.priority) }}
              </span>
            </div>
            <!-- 备注信息 -->
            <div v-if="todo.notes" class="mt-2 text-xs sm:text-sm text-gray-600 bg-yellow-50 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg border-l-4 border-yellow-400">
              📝 {{ todo.notes }}
            </div>
          </div>
          <button
            @click="deleteTodo(todo.id)"
            class="text-gray-400 hover:text-red-500 transition-colors px-2 flex-shrink-0"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredTodos.length === 0" class="text-center py-12 text-gray-400">
      暂无待办事项
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const todos = ref([])
const filterStatus = ref('all')
const filterPriority = ref('all')
const searchText = ref('')

// 加载数据：始终以服务端 JSON 文件为主
onMounted(async () => {
  try {
    const res = await fetch('/life-os/data/todos.json')
    if (res.ok) {
      const serverData = await res.json()
      // 直接使用服务端数据，不需要 localStorage 逻辑
      todos.value = serverData
    } else {
      // fetch 失败时尝试 localStorage
      const savedData = localStorage.getItem('life-os-todos')
      if (savedData) todos.value = JSON.parse(savedData)
    }
  } catch (e) {
    console.error('加载待办数据失败', e)
    const savedData = localStorage.getItem('life-os-todos')
    if (savedData) todos.value = JSON.parse(savedData)
  }
})

// 筛选后的待办列表
const filteredTodos = computed(() => {
  return todos.value.filter(todo => {
    if (filterStatus.value !== 'all' && todo.status !== filterStatus.value) return false
    if (filterPriority.value !== 'all' && todo.priority !== filterPriority.value) return false
    if (searchText.value && !todo.text.includes(searchText.value)) return false
    return true
  })
})

// 统计
const pendingCount = computed(() => todos.value.filter(t => t.status === 'pending').length)
const completedCount = computed(() => todos.value.filter(t => t.status === 'completed').length)
const highCount = computed(() => todos.value.filter(t => t.priority === 'high').length)

// 优先级文本
const priorityText = (priority) => {
  const map = { high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

// 切换完成状态
const toggleTodo = (todo) => {
  if (todo.status === 'completed') {
    todo.status = 'pending'
    delete todo.completed_date
  } else {
    todo.status = 'completed'
    todo.completed_date = new Date().toISOString().split('T')[0]
  }
  localStorage.setItem('life-os-todos', JSON.stringify(todos.value))
}

// 删除待办
const deleteTodo = (id) => {
  todos.value = todos.value.filter(t => t.id !== id)
  localStorage.setItem('life-os-todos', JSON.stringify(todos.value))
}
</script>
