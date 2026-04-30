<template>
  <div>
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">✅ 待办事项</h2>
      <button
        @click="showAddModal = true"
        class="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        + 新建待办
      </button>
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
      </div>
    </div>

    <!-- 待办列表 -->
    <div class="space-y-3">
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
              {{ todo.title }}
            </div>
            <div class="flex flex-wrap items-center gap-2 mt-2 text-xs sm:text-sm text-gray-500">
              <span v-if="todo.project" class="bg-gray-100 px-2 py-0.5 rounded">{{ todo.project }}</span>
              <span v-if="todo.due">📅 {{ todo.due }}</span>
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
            <div v-if="todo.tags && todo.tags.length" class="flex flex-wrap gap-1 mt-2">
              <span v-for="tag in todo.tags" :key="tag" class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded">
                #{{ tag }}
              </span>
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

    <!-- 新建待办弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl p-4 sm:p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
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
const isDataLoaded = ref(false)

const newTodo = ref({
  title: '',
  project: '',
  due: '',
  priority: 'medium',
  tagsText: ''
})

// 加载数据：始终从 JSON 文件加载初始数据，localStorage 仅作增量缓存
onMounted(async () => {
  try {
    const res = await fetch('/life-os/data/todos.json')
    if (res.ok) {
      const serverData = await res.json()
      // 如果 localStorage 有数据且非空，以服务端数据为基础保留本地新增的待办
      const savedData = localStorage.getItem('life-os-todos')
      if (savedData) {
        const localTodos = JSON.parse(savedData)
        // 收集服务端待办 ID 集合
        const serverIds = new Set(serverData.map(t => t.id))
        // 合并：服务端数据 + 本地新增的（不在服务端中的）
        const localOnly = localTodos.filter(t => !serverIds.has(t.id))
        todos.value = [...serverData, ...localOnly]
      } else {
        todos.value = serverData
      }
      saveTodos()
    } else {
        // fetch 失败时回退到 localStorage
        const savedData = localStorage.getItem('life-os-todos')
        if (savedData) todos.value = JSON.parse(savedData)
      }
    isDataLoaded.value = true
  } catch (e) {
    console.error('加载待办数据失败', e)
    // 最终回退
    const savedData = localStorage.getItem('life-os-todos')
    if (savedData) {
      todos.value = JSON.parse(savedData)
      isDataLoaded.value = true
    }
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
</script>
