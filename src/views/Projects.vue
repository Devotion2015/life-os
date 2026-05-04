<template>
  <div>
    <!-- 编辑弹窗 -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[10vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-4 sm:p-6 max-h-[75vh] overflow-y-auto">
        <h3 class="text-lg font-bold mb-4">{{ editingProject.id ? '编辑项目' : '新增项目' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">项目名称 <span class="text-red-500">*</span></label>
            <input v-model="editingProject.name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="输入项目名称..." />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">类型</label>
              <select v-model="editingProject.type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="teaching">📖 教学</option>
                <option value="content">📝 内容创作</option>
                <option value="research">🔬 科研</option>
                <option value="personal">👤 个人</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="editingProject.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="planning">📌 规划中</option>
                <option value="active">🚀 进行中</option>
                <option value="completed">✅ 已完成</option>
                <option value="paused">⏸️ 暂停</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
              <input v-model="editingProject.deadline" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">关联 OKR</label>
              <input v-model="editingProject.linked_okr" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如 O1-KR1" />
            </div>
          </div>

          <!-- 子任务管理 -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">子任务 <span class="text-gray-400 text-xs ml-1">({{ editingProject.tasks.length }} 项)</span></label>
            </div>
            <div class="space-y-1.5 mb-2 max-h-48 overflow-y-auto">
              <div
                v-for="(task, idx) in editingProject.tasks"
                :key="idx"
                class="flex items-center gap-2 p-1.5 rounded hover:bg-gray-50 group"
              >
                <input
                  v-model="task.completed"
                  type="checkbox"
                  class="w-4 h-4 text-blue-500 rounded border-gray-300 focus:ring-blue-500"
                  @change="updateProgress(editingProject)"
                />
                <input
                  v-model="task.text"
                  type="text"
                  class="flex-1 px-2 py-1 border border-gray-200 rounded text-sm focus:ring-1 focus:ring-blue-500"
                  :class="{ 'line-through text-gray-400': task.completed }"
                  placeholder="输入任务..."
                />
                <button @click="removeTask(idx)" class="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all text-sm" title="删除任务">✕</button>
              </div>
              <div v-if="editingProject.tasks.length === 0" class="text-center py-2 text-xs text-gray-400">
                暂无子任务
              </div>
            </div>
            <button @click="addTask" class="text-blue-500 text-sm hover:text-blue-700 transition-colors">+ 添加子任务</button>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">取消</button>
          <button @click="saveProject" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">保存</button>
        </div>
      </div>
    </div>

    <!-- 头部 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">📋 项目管理</h2>
      <button @click="openAddModal" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm sm:text-base">
        + 新增项目
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl sm:text-2xl font-bold text-gray-800">{{ projects.length }}</div>
        <div class="text-xs text-gray-500">全部项目</div>
      </div>
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl sm:text-2xl font-bold text-blue-600">{{ activeCount }}</div>
        <div class="text-xs text-gray-500">进行中</div>
      </div>
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl sm:text-2xl font-bold text-green-600">{{ completedCount }}</div>
        <div class="text-xs text-gray-500">已完成</div>
      </div>
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl sm:text-2xl font-bold text-orange-600">{{ overallProgress }}%</div>
        <div class="text-xs text-gray-500">整体进度</div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-lg shadow p-3 sm:p-4 mb-6">
      <div class="flex flex-col sm:flex-row gap-3">
        <select v-model="filterType" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="all">全部类型</option>
          <option value="teaching">📖 教学</option>
          <option value="content">📝 内容创作</option>
          <option value="research">🔬 科研</option>
          <option value="personal">👤 个人</option>
        </select>
        <select v-model="filterStatus" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="all">全部状态</option>
          <option value="planning">📌 规划中</option>
          <option value="active">🚀 进行中</option>
          <option value="completed">✅ 已完成</option>
          <option value="paused">⏸️ 暂停</option>
        </select>
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索项目或任务..."
          class="w-full sm:flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
    </div>

    <!-- 看板三列 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- 规划中 -->
      <div class="bg-gray-100 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span>📌</span> 规划中
          <span class="text-sm text-gray-400 ml-auto">({{ filteredByStatus('planning').length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="project in filteredByStatus('planning')"
            :key="project.id"
            class="bg-white rounded-lg shadow p-3 hover:shadow-md transition-shadow group"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-medium text-gray-800 text-sm leading-snug">{{ project.name }}</h4>
              <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0 ml-1">
                <button @click="editProject(project)" class="text-gray-400 hover:text-blue-500 px-1 text-xs" title="编辑">✏️</button>
                <button @click="deleteProject(project.id)" class="text-gray-400 hover:text-red-500 px-1 text-xs" title="删除">🗑️</button>
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-1.5 mb-2">
              <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(project.type)">
                {{ typeLabel(project.type) }}
              </span>
              <span v-if="project.linked_okr" class="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">{{ project.linked_okr }}</span>
              <span v-if="project.deadline" class="text-xs text-gray-500 ml-auto">📅 {{ project.deadline }}</span>
            </div>
          </div>
          <div v-if="filteredByStatus('planning').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        </div>
      </div>

      <!-- 进行中 -->
      <div class="bg-blue-50 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span>🚀</span> 进行中
          <span class="text-sm text-gray-400 ml-auto">({{ filteredByStatus('active').length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="project in filteredByStatus('active')"
            :key="project.id"
            class="bg-white rounded-lg shadow p-3 hover:shadow-md transition-shadow group"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-medium text-gray-800 text-sm leading-snug pr-1">{{ project.name }}</h4>
              <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                <button @click="editProject(project)" class="text-gray-400 hover:text-blue-500 px-1 text-xs" title="编辑">✏️</button>
                <button @click="deleteProject(project.id)" class="text-gray-400 hover:text-red-500 px-1 text-xs" title="删除">🗑️</button>
              </div>
            </div>
            <!-- 进度条 -->
            <div class="mb-2">
              <div class="flex items-center justify-between text-xs text-gray-500 mb-0.5">
                <span>进度 {{ calcProgress(project) }}%</span>
                <span>{{ project.tasks.filter(t => t.completed).length }}/{{ project.tasks.length }} 任务</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="h-1.5 rounded-full transition-all"
                  :class="progressBarColor(calcProgress(project))"
                  :style="{ width: calcProgress(project) + '%' }"
                ></div>
              </div>
            </div>
            <!-- 子任务预览（最多3条） -->
            <div v-if="project.tasks.length > 0" class="space-y-0.5 mb-2">
              <div
                v-for="task in project.tasks.slice(0, 3)"
                :key="task.id"
                class="flex items-center gap-1.5"
              >
                <span class="text-xs" :class="task.completed ? 'text-green-500' : 'text-gray-300'">
                  {{ task.completed ? '✓' : '○' }}
                </span>
                <span class="text-xs text-gray-700 truncate" :class="{ 'line-through text-gray-400': task.completed }">
                  {{ task.text }}
                </span>
              </div>
              <div v-if="project.tasks.length > 3" class="text-xs text-gray-400 pl-4">
                ...还有 {{ project.tasks.length - 3 }} 项
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(project.type)">
                {{ typeLabel(project.type) }}
              </span>
              <span v-if="project.linked_okr" class="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">{{ project.linked_okr }}</span>
              <span
                v-if="project.deadline"
                class="text-xs ml-auto"
                :class="isOverdue(project.deadline) ? 'text-red-500 font-medium' : 'text-gray-500'"
              >
                {{ isOverdue(project.deadline) ? '⚠️' : '📅' }} {{ project.deadline }}
              </span>
            </div>
          </div>
          <div v-if="filteredByStatus('active').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        </div>
      </div>

      <!-- 已完成 / 暂停 -->
      <div class="bg-green-50 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span>✅</span> 已完成 / 暂停
          <span class="text-sm text-gray-400 ml-auto">({{ filteredByStatus('completed').length + filteredByStatus('paused').length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="project in [...filteredByStatus('completed'), ...filteredByStatus('paused')]"
            :key="project.id"
            class="bg-white rounded-lg shadow p-3 hover:shadow-md transition-shadow group"
            :class="{ 'opacity-75': project.status === 'completed' }"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-medium text-gray-800 text-sm leading-snug" :class="{ 'line-through text-gray-500': project.status === 'completed' }">
                {{ project.name }}
              </h4>
              <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0 ml-1">
                <button @click="editProject(project)" class="text-gray-400 hover:text-blue-500 px-1 text-xs" title="编辑">✏️</button>
                <button @click="deleteProject(project.id)" class="text-gray-400 hover:text-red-500 px-1 text-xs" title="删除">🗑️</button>
              </div>
            </div>
            <!-- 进度条 -->
            <div v-if="project.tasks.length > 0" class="mb-2">
              <div class="flex items-center justify-between text-xs text-gray-500 mb-0.5">
                <span>进度 {{ calcProgress(project) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="h-1.5 rounded-full transition-all"
                  :class="project.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'"
                  :style="{ width: calcProgress(project) + '%' }"
                ></div>
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(project.type)">
                {{ typeLabel(project.type) }}
              </span>
              <span class="text-xs px-1.5 py-0.5 rounded" :class="project.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                {{ statusLabel(project.status) }}
              </span>
              <span v-if="project.linked_okr" class="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">{{ project.linked_okr }}</span>
            </div>
          </div>
          <div v-if="filteredByStatus('completed').length + filteredByStatus('paused').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="projects.length === 0" class="text-center py-16">
      <div class="text-5xl mb-4">📋</div>
      <p class="text-gray-400 mb-4">还没有任何项目</p>
      <button @click="openAddModal" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm">
        + 创建第一个项目
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// ===== 数据 =====
const projects = ref([])
const filterType = ref('all')
const filterStatus = ref('all')
const searchText = ref('')
const showModal = ref(false)
const editingProject = ref({})
const isEditingProject = ref(false)

// 初始示例数据
const sampleData = [
  {
    id: 'P001',
    name: '信息技术教案制作',
    type: 'teaching',
    status: 'active',
    deadline: '2026-06-30',
    linked_okr: 'O1-KR1',
    tasks: [
      { id: 'T001', text: '完成前12讲教案', completed: true },
      { id: 'T002', text: '完成中12讲教案', completed: true },
      { id: 'T003', text: '完成后12讲教案', completed: false },
      { id: 'T004', text: '完成安全教育教案', completed: false },
    ]
  },
  {
    id: 'P002',
    name: '公众号2026运营',
    type: 'content',
    status: 'active',
    deadline: null,
    linked_okr: 'O2',
    tasks: [
      { id: 'T005', text: '技术门文章 12 篇', completed: false },
      { id: 'T006', text: '影视门安利 6 篇', completed: false },
      { id: 'T007', text: '书单推荐 4 篇', completed: false },
    ]
  },
  {
    id: 'P003',
    name: '课堂测验题库构建',
    type: 'teaching',
    status: 'planning',
    deadline: '2026-09-01',
    linked_okr: '',
    tasks: [
      { id: 'T008', text: '确定题库范围与题型', completed: false },
      { id: 'T009', text: '编写第1-6讲测验题', completed: false },
      { id: 'T010', text: '编写第7-12讲测验题', completed: false },
    ]
  },
  {
    id: 'P004',
    name: 'bird-knowledge 鸟类科普站',
    type: 'personal',
    status: 'active',
    deadline: null,
    linked_okr: '',
    tasks: [
      { id: 'T011', text: '补充鸟类音频资源', completed: false },
      { id: 'T012', text: '新增鸟类品种（目标20+）', completed: false },
      { id: 'T013', text: '优化移动端展示效果', completed: false },
    ]
  },
]

// ===== 初始化 =====
onMounted(() => {
  const saved = localStorage.getItem('life-os-projects')
  if (saved) {
    projects.value = JSON.parse(saved)
  } else {
    projects.value = sampleData
    saveToStorage()
  }
})

// ===== 持久化 =====
function saveToStorage() {
  localStorage.setItem('life-os-projects', JSON.stringify(projects.value))
}

// ===== 计算属性 =====
const activeCount = computed(() => projects.value.filter(p => p.status === 'active').length)
const completedCount = computed(() => projects.value.filter(p => p.status === 'completed').length)
const planningCount = computed(() => projects.value.filter(p => p.status === 'planning').length)
const pausedCount = computed(() => projects.value.filter(p => p.status === 'paused').length)

const overallProgress = computed(() => {
  if (projects.value.length === 0) return 0
  const total = projects.value.reduce((sum, p) => sum + calcProgress(p), 0)
  return Math.round(total / projects.value.length)
})

// 主筛选过滤
const filteredProjects = computed(() => {
  return projects.value.filter(p => {
    if (filterType.value !== 'all' && p.type !== filterType.value) return false
    if (filterStatus.value !== 'all' && p.status !== filterStatus.value) return false
    if (searchText.value) {
      const s = searchText.value.toLowerCase()
      const matchName = p.name.toLowerCase().includes(s)
      const matchTask = p.tasks.some(t => t.text.toLowerCase().includes(s))
      const matchOKR = (p.linked_okr || '').toLowerCase().includes(s)
      if (!matchName && !matchTask && !matchOKR) return false
    }
    return true
  })
})

function projectsByStatus(status) {
  return filteredProjects.value.filter(p => p.status === status)
}

function filteredByStatus(status) {
  return filteredProjects.value.filter(p => p.status === status)
}

// ===== 进度计算 =====
function calcProgress(project) {
  if (!project.tasks || project.tasks.length === 0) return 0
  const done = project.tasks.filter(t => t.completed).length
  return Math.round((done / project.tasks.length) * 100)
}

function updateProgress(project) {
  // progress 实时反映 checkbox 变化，无需额外操作
}

// ===== 标签 =====
const typeMap = {
  teaching: '📖 教学',
  content: '📝 内容',
  research: '🔬 科研',
  personal: '👤 个人',
}
const typeColorMap = {
  teaching: 'bg-blue-500',
  content: 'bg-purple-500',
  research: 'bg-green-600',
  personal: 'bg-pink-500',
}
const statusMap = {
  planning: '📌 规划中',
  active: '🚀 进行中',
  completed: '✅ 已完成',
  paused: '⏸️ 已暂停',
}

function typeLabel(type) { return typeMap[type] || type }
function typeColor(type) { return typeColorMap[type] || 'bg-gray-500' }
function statusLabel(status) { return statusMap[status] || status }
function progressBarColor(pct) {
  if (pct >= 80) return 'bg-green-500'
  if (pct >= 40) return 'bg-blue-500'
  return 'bg-yellow-500'
}

// ===== 日期判断 =====
function isOverdue(deadline) {
  if (!deadline) return false
  return new Date(deadline) < new Date(new Date().toDateString())
}

// ===== 弹窗操作 =====
function openAddModal() {
  editingProject.value = {
    id: null,
    name: '',
    type: 'teaching',
    status: 'planning',
    deadline: '',
    linked_okr: '',
    tasks: [],
  }
  isEditingProject.value = false
  showModal.value = true
}

function editProject(project) {
  editingProject.value = {
    ...project,
    tasks: project.tasks.map(t => ({ ...t })),
  }
  isEditingProject.value = true
  showModal.value = true
}

function saveProject() {
  if (!editingProject.value.name.trim()) {
    alert('请输入项目名称')
    return
  }

  if (isEditingProject.value) {
    const idx = projects.value.findIndex(p => p.id === editingProject.value.id)
    if (idx !== -1) {
      projects.value[idx] = { ...editingProject.value }
    }
  } else {
    const id = 'P' + String(projects.value.length + 1).padStart(3, '0')
    projects.value.push({
      ...editingProject.value,
      id,
    })
  }

  showModal.value = false
  saveToStorage()
}

function deleteProject(id) {
  if (!confirm('确定要删除这个项目吗？')) return
  projects.value = projects.value.filter(p => p.id !== id)
  saveToStorage()
}

// ===== 子任务操作 =====
function addTask() {
  const taskId = 'T' + Date.now().toString(36).toUpperCase()
  editingProject.value.tasks.push({
    id: taskId,
    text: '',
    completed: false,
  })
}

function removeTask(idx) {
  editingProject.value.tasks.splice(idx, 1)
}
</script>
