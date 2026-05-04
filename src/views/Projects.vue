<template>
  <div>
    <!-- 编辑弹窗 -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[10vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-4 sm:p-6 max-h-[75vh] overflow-y-auto">
        <h3 class="text-lg font-bold mb-4">{{ editingProject.id ? '编辑项目' : '新增项目' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">项目名称 <span class="text-red-500">*</span></label>
            <input v-model="editingProject.name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="输入项目名称..." />
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
              <select v-model="editingProject.okr_ids" multiple class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm h-24">
                <option v-for="o in okrs" :key="o.id" :value="o.id">{{ o.title }}</option>
              </select>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">子任务 ({{ editingProject.tasks.length }} 项)</label>
            </div>
            <div class="space-y-1.5 mb-2 max-h-48 overflow-y-auto">
              <div v-for="(task, idx) in editingProject.tasks" :key="idx" class="flex items-center gap-2 p-1.5 rounded hover:bg-gray-50 group">
                <input v-model="task.completed" type="checkbox" class="w-4 h-4 text-blue-500 rounded border-gray-300" />
                <input v-model="task.text" type="text" class="flex-1 px-2 py-1 border border-gray-200 rounded text-sm"
                  :class="{ 'line-through text-gray-400': task.completed }" placeholder="输入任务..." />
                <button @click="removeTask(idx)" class="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 text-sm">✕</button>
              </div>
            </div>
            <button @click="addTask" class="text-blue-500 text-sm hover:text-blue-700">+ 添加子任务</button>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveProject" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- 头部 + 统计 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">📋 项目管理</h2>
      <button @click="openAddModal" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm">+ 新增项目</button>
    </div>
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl font-bold text-gray-800">{{ projects.length }}</div>
        <div class="text-xs text-gray-500">全部项目</div>
      </div>
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl font-bold text-blue-600">{{ activeCount }}</div>
        <div class="text-xs text-gray-500">进行中</div>
      </div>
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl font-bold text-orange-600">{{ totalTodos }}</div>
        <div class="text-xs text-gray-500">关联待办</div>
      </div>
      <div class="bg-white rounded-lg shadow p-3 text-center">
        <div class="text-xl font-bold text-purple-600">{{ totalOKRs }}</div>
        <div class="text-xs text-gray-500">关联目标</div>
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
        <input v-model="searchText" type="text" placeholder="搜索项目、任务或关联待办..."
          class="w-full sm:flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
      </div>
    </div>

    <!-- 看板三列 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="bg-gray-100 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3">📌 规划中 ({{ filteredByStatus('planning').length }})</h3>
        <div v-if="filteredByStatus('planning').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        <div v-for="p in filteredByStatus('planning')" :key="p.id" class="bg-white rounded-lg shadow p-3 mb-3 hover:shadow-md group">
          <div class="flex items-start justify-between mb-2">
            <h4 class="font-medium text-gray-800 text-sm">{{ p.name }}</h4>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100">
              <button @click="editProject(p)" class="text-gray-400 hover:text-blue-500 px-1 text-xs">✏️</button>
              <button @click="deleteProject(p.id)" class="text-gray-400 hover:text-red-500 px-1 text-xs">🗑️</button>
            </div>
          </div>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(p.type)">{{ typeLabel(p.type) }}</span>
            <span v-if="p.deadline" class="text-xs text-gray-500">📅 {{ p.deadline }}</span>
          </div>
          <!-- 关联 OKR -->
          <div v-if="(p.okr_ids || []).length > 0" class="flex flex-wrap gap-1 mb-2">
            <span v-for="oid in p.okr_ids" :key="oid" class="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">
              🎯 {{ getOKRName(oid) }}
            </span>
          </div>
          <!-- 关联待办 -->
          <div class="text-xs text-gray-400">
            ✅ {{ getProjectTodos(p.id).filter(t => t.status === 'completed').length }}/{{ getProjectTodos(p.id).length }} 待办完成
          </div>
        </div>
      </div>

      <div class="bg-blue-50 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3">🚀 进行中 ({{ filteredByStatus('active').length }})</h3>
        <div v-if="filteredByStatus('active').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        <div v-for="p in filteredByStatus('active')" :key="p.id" class="bg-white rounded-lg shadow p-3 mb-3 hover:shadow-md group">
          <div class="flex items-start justify-between mb-2">
            <h4 class="font-medium text-gray-800 text-sm">{{ p.name }}</h4>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100">
              <button @click="editProject(p)" class="text-gray-400 hover:text-blue-500 px-1 text-xs">✏️</button>
              <button @click="deleteProject(p.id)" class="text-gray-400 hover:text-red-500 px-1 text-xs">🗑️</button>
            </div>
          </div>
          <div class="mb-2">
            <div class="flex justify-between text-xs text-gray-500 mb-0.5">
              <span>进度 {{ calcProgress(p) }}%</span>
              <span>{{ (p.tasks||[]).filter(t=>t.completed).length }}/{{ (p.tasks||[]).length }} 子任务</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5">
              <div class="h-1.5 rounded-full" :class="progressColor(calcProgress(p))" :style="{ width: calcProgress(p)+'%' }"></div>
            </div>
          </div>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(p.type)">{{ typeLabel(p.type) }}</span>
            <span v-if="p.deadline" :class="['text-xs', isOverdue(p.deadline)?'text-red-500':'text-gray-500']">
              {{ isOverdue(p.deadline) ? '⚠️' : '📅' }} {{ p.deadline }}
            </span>
          </div>
          <div v-if="(p.okr_ids || []).length > 0" class="flex flex-wrap gap-1 mb-2">
            <span v-for="oid in p.okr_ids" :key="oid" class="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">
              🎯 {{ getOKRName(oid) }}
            </span>
          </div>
          <div class="text-xs text-gray-400">
            ✅ {{ getProjectTodos(p.id).filter(t => t.status === 'completed').length }}/{{ getProjectTodos(p.id).length }} 待办完成
          </div>
        </div>
      </div>

      <div class="bg-green-50 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3">✅ 已完成 / 暂停 ({{ filteredByStatus('completed').length + filteredByStatus('paused').length }})</h3>
        <div v-if="filteredByStatus('completed').length + filteredByStatus('paused').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        <div v-for="p in [...filteredByStatus('completed'), ...filteredByStatus('paused')]" :key="p.id"
          class="bg-white rounded-lg shadow p-3 mb-3 hover:shadow-md group" :class="{ 'opacity-75': p.status === 'completed' }">
          <h4 class="font-medium text-gray-800 text-sm mb-2" :class="{ 'line-through': p.status==='completed' }">{{ p.name }}</h4>
          <div class="flex flex-wrap gap-1.5">
            <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(p.type)">{{ typeLabel(p.type) }}</span>
            <span :class="['text-xs px-1.5 py-0.5 rounded', p.status==='completed'?'bg-green-100 text-green-700':'bg-yellow-100 text-yellow-700']">
              {{ statusLabel(p.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="projects.length === 0" class="text-center py-16">
      <div class="text-5xl mb-4">📋</div>
      <p class="text-gray-400 mb-4">还没有任何项目</p>
      <button @click="openAddModal" class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm">+ 创建第一个项目</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const projects = ref([])
const okrs = ref([])
const allTodos = ref([])
const filterType = ref('all')
const filterStatus = ref('all')
const searchText = ref('')
const showModal = ref(false)
const editingProject = ref({})
const isEditingProject = ref(false)

onMounted(async () => {
  try { const r = await fetch('/life-os/data/projects.json'); if (r.ok) projects.value = await r.json() }
  catch (e) { const s = localStorage.getItem('life-os-projects'); if (s) projects.value = JSON.parse(s) }
  try { const r = await fetch('/life-os/data/okr.json'); if (r.ok) okrs.value = await r.json() }
  catch (e) {}
  try { const r = await fetch('/life-os/data/todos.json'); if (r.ok) allTodos.value = await r.json() }
  catch (e) {}
})

function getProjectTodos(pid) { return allTodos.value.filter(t => t.project_id === pid) }
function getOKRName(id) { const o = okrs.value.find(o => o.id === id); return o ? o.title : `目标${id}` }

const totalTodos = computed(() => {
  const ids = new Set(projects.value.map(p => p.id))
  return allTodos.value.filter(t => ids.has(t.project_id)).length
})
const totalOKRs = computed(() => {
  const ids = new Set()
  projects.value.forEach(p => (p.okr_ids || []).forEach(id => ids.add(id)))
  return ids.size
})
const activeCount = computed(() => projects.value.filter(p => p.status === 'active').length)

function filteredByStatus(status) {
  return projects.value.filter(p => {
    if (p.status !== status) return false
    if (filterType.value !== 'all' && p.type !== filterType.value) return false
    if (searchText.value) {
      const s = searchText.value.toLowerCase()
      const mn = p.name.toLowerCase().includes(s)
      const mt = (p.tasks || []).some(t => t.text.toLowerCase().includes(s))
      const pt = getProjectTodos(p.id).some(t => t.text.toLowerCase().includes(s))
      if (!mn && !mt && !pt) return false
    }
    return true
  })
}

function calcProgress(p) {
  if (!p.tasks || p.tasks.length === 0) return 0
  return Math.round((p.tasks.filter(t => t.completed).length / p.tasks.length) * 100)
}
function progressColor(pct) { return pct >= 80 ? 'bg-green-500' : pct >= 40 ? 'bg-blue-500' : 'bg-yellow-500' }
function isOverdue(d) { return d ? new Date(d) < new Date(new Date().toDateString()) : false }

const typeMap = { teaching: '📖 教学', content: '📝 内容', research: '🔬 科研', personal: '👤 个人' }
const typeColorMap = { teaching: 'bg-blue-500', content: 'bg-purple-500', research: 'bg-green-600', personal: 'bg-pink-500' }
function typeLabel(t) { return typeMap[t] || t }
function typeColor(t) { return typeColorMap[t] || 'bg-gray-500' }
function statusLabel(s) { return { planning: '📌 规划中', active: '🚀 进行中', completed: '✅ 已完成', paused: '⏸️ 暂停' }[s] || s }

function openAddModal() {
  editingProject.value = { id: null, name: '', type: 'teaching', status: 'planning', deadline: '', okr_ids: [], tasks: [] }
  isEditingProject.value = false; showModal.value = true
}
function editProject(project) {
  editingProject.value = JSON.parse(JSON.stringify(project)); isEditingProject.value = true; showModal.value = true
}
function saveProject() {
  if (!editingProject.value.name.trim()) { alert('请输入项目名称'); return }
  if (isEditingProject.value) {
    const idx = projects.value.findIndex(p => p.id === editingProject.value.id)
    if (idx !== -1) projects.value[idx] = { ...editingProject.value }
  } else {
    const id = 'P' + String(projects.value.length + 1).padStart(3, '0')
    projects.value.push({ ...editingProject.value, id })
  }
  showModal.value = false; localStorage.setItem('life-os-projects', JSON.stringify(projects.value))
}
function deleteProject(id) {
  if (!confirm('确定要删除这个项目吗？')) return
  projects.value = projects.value.filter(p => p.id !== id)
  localStorage.setItem('life-os-projects', JSON.stringify(projects.value))
}
function addTask() {
  const taskId = 'T' + Date.now().toString(36).toUpperCase()
  editingProject.value.tasks.push({ id: taskId, text: '', completed: false })
}
function removeTask(idx) { editingProject.value.tasks.splice(idx, 1) }
</script>
