<template>
  <div>
    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingTodo.id ? '编辑待办' : '新增待办' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">待办内容</label>
            <input v-model="editingTodo.text" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="输入待办内容..." />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="editingTodo.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="pending">待完成</option>
                <option value="completed">已完成</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">优先级</label>
              <select v-model="editingTodo.priority" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
              <input v-model="editingTodo.deadline" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">学期</label>
              <input v-model="editingTodo.semester" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如 2023-2024-1" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">所属项目</label>
            <select v-model="editingTodo.project_id" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">无</option>
              <option v-for="p in allProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <textarea v-model="editingTodo.notes" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="添加备注..."></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end">
          <button @click="showEditModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveTodo" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">✅ 待办事项</h2>
      <button @click="openAddModal" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm sm:text-base">
        + 新增待办
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
        <select v-model="filterProject" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="all">全部项目</option>
          <option value="none">无项目</option>
          <option v-for="p in allProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索标题、备注、日期、学期..."
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
              <span v-if="todo.completed_date">✅ {{ todo.completed_date }}</span>
              <span v-if="getProjectName(todo.project_id)" class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs">
                📋 {{ getProjectName(todo.project_id) }}
              </span>
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
            <div v-if="todo.notes && todo.notes.trim()" class="mt-2 text-xs sm:text-sm text-gray-600 bg-yellow-50 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg border-l-4 border-yellow-400">
              📝 {{ todo.notes }}
            </div>
          </div>
          <div class="flex gap-1 flex-shrink-0">
            <button
              @click="editTodo(todo)"
              class="text-gray-400 hover:text-blue-500 transition-colors px-2"
              title="编辑"
            >
              ✏️
            </button>
            <button
              @click="deleteTodo(todo.id)"
              class="text-gray-400 hover:text-red-500 transition-colors px-2"
              title="删除"
            >
              🗑️
            </button>
          </div>
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
const allProjects = ref([])
const filterStatus = ref('all')
const filterPriority = ref('all')
const filterProject = ref('all')
const searchText = ref('')

// 编辑弹窗状态
const showEditModal = ref(false)
const editingTodo = ref({})
const isEditing = ref(false)

// 加载数据：始终以服务端 JSON 文件为主
onMounted(async () => {
  try {
    const res = await fetch('/life-os/data/todos.json')
    if (res.ok) {
      const serverData = await res.json()
      todos.value = serverData
    } else {
      const savedData = localStorage.getItem('life-os-todos')
      if (savedData) todos.value = JSON.parse(savedData)
    }
  } catch (e) {
    console.error('加载待办数据失败', e)
    const savedData = localStorage.getItem('life-os-todos')
    if (savedData) todos.value = JSON.parse(savedData)
  }

  // 加载项目列表（用于筛选和显示名称）
  try {
    const res = await fetch('/life-os/data/projects.json')
    if (res.ok) allProjects.value = await res.json()
  } catch (e) {
    const saved = localStorage.getItem('life-os-projects')
    if (saved) allProjects.value = JSON.parse(saved)
  }
})

// 通过 project_id 获取项目名称
function getProjectName(pid) {
  if (!pid) return null
  const p = allProjects.value.find(p => p.id === pid)
  return p ? p.name : null
}

// 筛选后的待办列表
const filteredTodos = computed(() => {
  return todos.value.filter(todo => {
    if (filterStatus.value !== 'all' && todo.status !== filterStatus.value) return false
    if (filterPriority.value !== 'all' && todo.priority !== filterPriority.value) return false
    if (filterProject.value !== 'all') {
      if (filterProject.value === 'none') {
        if (todo.project_id) return false
      } else {
        if (todo.project_id !== filterProject.value) return false
      }
    }
    if (searchText.value) {
      const search = searchText.value.toLowerCase()
      const matchText = todo.text?.toLowerCase().includes(search)
      const matchDeadline = todo.deadline?.toLowerCase().includes(search)
      const matchSemester = todo.semester?.toLowerCase().includes(search)
      const matchNotes = todo.notes?.toLowerCase().includes(search)
      const matchCompleted = todo.completed_date?.toLowerCase().includes(search)
      const matchProject = getProjectName(todo.project_id)?.toLowerCase().includes(search)
      if (!matchText && !matchDeadline && !matchSemester && !matchNotes && !matchCompleted && !matchProject) return false
    }
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
  saveToLocalStorage()
}

// 打开新增弹窗
const openAddModal = () => {
  editingTodo.value = {
    id: null,
    text: '',
    status: 'pending',
    priority: 'medium',
    semester: '',
    deadline: '',
    notes: ''
  }
  isEditing.value = false
  showEditModal.value = true
}

// 打开编辑弹窗
const editTodo = (todo) => {
  editingTodo.value = { ...todo }
  isEditing.value = true
  showEditModal.value = true
}

// 保存待办
const saveTodo = () => {
  if (!editingTodo.value.text.trim()) {
    alert('请输入待办内容')
    return
  }
  if (isEditing.value) {
    // 编辑模式：更新现有
    const index = todos.value.findIndex(t => t.id === editingTodo.value.id)
    if (index !== -1) {
      todos.value[index] = { ...editingTodo.value }
    }
  } else {
    // 新增模式：生成新 ID
    const maxId = Math.max(...todos.value.map(t => t.id), 0)
    todos.value.push({
      ...editingTodo.value,
      id: maxId + 1,
      source: '手动添加'
    })
  }
  showEditModal.value = false
  saveToLocalStorage()
}

// 保存到 localStorage
const saveToLocalStorage = () => {
  localStorage.setItem('life-os-todos', JSON.stringify(todos.value))
}
</script>
