<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">✅ 待办事项</h2>
      <button
        @click="showAddModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        + 新建待办
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex gap-4">
        <select v-model="filterStatus" class="px-3 py-2 border border-gray-300 rounded-lg">
          <option value="all">全部状态</option>
          <option value="pending">待完成</option>
          <option value="completed">已完成</option>
        </select>
        <select v-model="filterPriority" class="px-3 py-2 border border-gray-300 rounded-lg">
          <option value="all">全部优先级</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索待办..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
        />
      </div>
    </div>

    <!-- 待办列表 -->
    <div class="space-y-3">
      <div
        v-for="todo in filteredTodos"
        :key="todo.id"
        class="bg-white rounded-lg shadow p-4 flex items-center justify-between hover:shadow-md transition-shadow"
        :class="{ 'opacity-50': todo.status === 'completed' }"
      >
        <div class="flex items-center flex-1">
          <button
            @click="toggleTodo(todo)"
            class="w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center transition-colors"
            :class="todo.status === 'completed' ? 'bg-green-500 border-green-500' : 'border-gray-300 hover:border-green-500'"
          >
            <span v-if="todo.status === 'completed'" class="text-white text-sm">✓</span>
          </button>
          <div class="flex-1">
            <div class="font-medium text-gray-800" :class="{ 'line-through': todo.status === 'completed' }">
              {{ todo.title }}
            </div>
            <div class="flex items-center gap-3 mt-1 text-sm text-gray-500">
              <span v-if="todo.project" class="bg-gray-100 px-2 py-0.5 rounded">{{ todo.project }}</span>
              <span v-if="todo.due">📅 {{ todo.due }}</span>
              <span
                class="px-2 py-0.5 rounded text-white text-xs"
                :class="{
                  'bg-red-500': todo.priority === 'high',
                  'bg-yellow-500': todo.priority === 'medium',
                  'bg-gray-400': todo.priority === 'low'
                }"
              >
                {{ priorityText(todo.priority) }}
              </span>
            </div>
            <div v-if="todo.tags && todo.tags.length" class="flex gap-1 mt-2">
              <span v-for="tag in todo.tags" :key="tag" class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded">
                #{{ tag }}
              </span>
            </div>
          </div>
        </div>
        <button
          @click="deleteTodo(todo.id)"
          class="text-gray-400 hover:text-red-500 transition-colors px-2"
        >
          🗑️
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredTodos.length === 0" class="text-center py-12 text-gray-400">
      暂无待办事项
    </div>

    <!-- 新建待办弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">新建待办</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">标题</label>
            <input v-model="newTodo.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">项目</label>
            <input v-model="newTodo.project" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">截止日期</label>
            <input v-model="newTodo.due" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">优先级</label>
            <select v-model="newTodo.priority" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">标签（用逗号分隔）</label>
            <input v-model="newTodo.tagsText" type="text" placeholder="备课, 教案" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showAddModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="addTodo" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">添加</button>
        </div>
      </div>
    </div>

    <!-- 统计 -->
    <div class="mt-6 bg-white rounded-lg shadow p-4">
      <div class="flex justify-around text-center">
        <div>
          <div class="text-2xl font-bold text-gray-800">{{ todos.length }}</div>
          <div class="text-sm text-gray-500">全部待办</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-blue-600">{{ pendingCount }}</div>
          <div class="text-sm text-gray-500">待完成</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-green-600">{{ completedCount }}</div>
          <div class="text-sm text-gray-500">已完成</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const todos = ref([])
const showAddModal = ref(false)
const filterStatus = ref('all')
const filterPriority = ref('all')
const searchText = ref('')

const newTodo = ref({
  title: '',
  project: '',
  due: '',
  priority: 'medium',
  tagsText: ''
})

// 加载数据
onMounted(async () => {
  try {
    const res = await fetch('/data/todos.json')
    todos.value = await res.json()
  } catch (e) {
    console.error('加载待办数据失败', e)
  }
})

// 筛选后的待办列表
const filteredTodos = computed(() => {
  return todos.value.filter(todo => {
    if (filterStatus.value !== 'all' && todo.status !== filterStatus.value) return false
    if (filterPriority.value !== 'all' && todo.priority !== filterPriority.value) return false
    if (searchText.value && !todo.title.includes(searchText.value)) return false
    return true
  })
})

// 统计
const pendingCount = computed(() => todos.value.filter(t => t.status === 'pending').length)
const completedCount = computed(() => todos.value.filter(t => t.status === 'completed').length)

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
  saveTodos()
}

// 删除待办
const deleteTodo = (id) => {
  todos.value = todos.value.filter(t => t.id !== id)
  saveTodos()
}

// 添加待办
const addTodo = () => {
  const id = 'T' + String(Date.now()).slice(-6)
  const tags = newTodo.value.tagsText
    ? newTodo.value.tagsText.split(',').map(t => t.trim()).filter(t => t)
    : []

  todos.value.unshift({
    id,
    title: newTodo.value.title,
    project: newTodo.value.project || null,
    due: newTodo.value.due || null,
    priority: newTodo.value.priority,
    status: 'pending',
    tags,
    created: new Date().toISOString().split('T')[0]
  })

  saveTodos()
  showAddModal.value = false
  newTodo.value = { title: '', project: '', due: '', priority: 'medium', tagsText: '' }
}

// 保存数据（localStorage）
const saveTodos = () => {
  localStorage.setItem('life-os-todos', JSON.stringify(todos.value))
}

// 从 localStorage 恢复数据
const savedData = localStorage.getItem('life-os-todos')
if (savedData) {
  todos.value = JSON.parse(savedData)
}
</script>
