<template>
  <div>
    <!-- 添加/编辑 Objective 弹窗 -->
    <div v-if="showObjModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingObj.id ? '编辑目标' : '新增目标' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">目标标题 *</label>
            <input v-model="editingObj.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="目标..." />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
            <textarea v-model="editingObj.description" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="描述这个目标..."></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">季度</label>
              <select v-model="editingObj.quarter" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option v-for="q in availableQuarters" :key="q" :value="q">{{ q }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="editingObj.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="active">进行中</option>
                <option value="completed">已完成</option>
                <option value="paused">暂停</option>
              </select>
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end">
          <button @click="deleteObj(editingObj.id)" v-if="editingObj.id" class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg mr-auto">删除</button>
          <button @click="showObjModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveObj" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑 KR 弹窗 -->
    <div v-if="showKRModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingKR.id ? '编辑关键结果' : '新增关键结果' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">KR 描述 *</label>
            <input v-model="editingKR.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="关键结果..." />
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">当前值</label>
              <input v-model.number="editingKR.current" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">目标值</label>
              <input v-model.number="editingKR.target" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">单位</label>
              <input v-model="editingKR.unit" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如: %" />
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end">
          <button @click="showKRModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveKR" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- 标题 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">🎯 目标 OKR</h2>
      <div class="flex gap-2">
        <select v-model="filterQuarter" class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="">全部季度</option>
          <option v-for="q in availableQuarters" :key="q" :value="q">{{ q }}</option>
        </select>
        <button @click="openAddObj" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm">+ 新增目标</button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-blue-600">{{ filteredOKRs.length }}</div>
        <div class="text-xs text-gray-500">目标总数</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-green-600">{{ completedCount }}</div>
        <div class="text-xs text-gray-500">已完成</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-orange-600">{{ activeCount }}</div>
        <div class="text-xs text-gray-500">进行中</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-purple-600">{{ overallProgress }}%</div>
        <div class="text-xs text-gray-500">整体进度</div>
      </div>
    </div>

    <!-- OKR 列表 -->
    <div class="space-y-4">
      <div v-for="obj in filteredOKRs" :key="obj.id" class="bg-white rounded-lg shadow overflow-hidden">
        <!-- Objective 头部 -->
        <div class="p-4 sm:p-5 border-b border-gray-100">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2 py-0.5 text-xs rounded-full font-medium" 
                  :class="statusClass(obj.status)">{{ statusLabel(obj.status) }}</span>
                <span class="text-xs text-gray-400">{{ obj.quarter }}</span>
              </div>
              <h3 class="text-lg font-bold text-gray-800">{{ obj.title }}</h3>
              <p v-if="obj.description" class="text-sm text-gray-500 mt-1">{{ obj.description }}</p>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0">
              <button @click="editObj(obj)" class="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors" title="编辑">✏️</button>
            </div>
          </div>
          <!-- Objective 进度条 -->
          <div class="mt-3">
            <div class="flex justify-between text-xs text-gray-500 mb-1">
              <span>目标进度</span>
              <span>{{ objProgress(obj) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="h-2 rounded-full transition-all duration-500"
                :class="progressColor(objProgress(obj))"
                :style="{ width: objProgress(obj) + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Key Results 列表 -->
        <div class="divide-y divide-gray-50">
          <div v-for="kr in (obj.key_results || [])" :key="kr.id"
            class="px-4 sm:px-5 py-3 flex items-center gap-3 group">
            <!-- KR 进度圆环 -->
            <div class="flex-shrink-0 w-10 h-10 relative">
              <svg class="w-10 h-10 transform -rotate-90">
                <circle cx="20" cy="20" r="16" fill="none" stroke="#e5e7eb" stroke-width="4" />
                <circle cx="20" cy="20" r="16" fill="none"
                  :stroke="krProgressColor(krProgress(kr))"
                  stroke-width="4"
                  stroke-linecap="round"
                  :stroke-dasharray="100.5"
                  :stroke-dashoffset="100.5 - krProgress(kr)"
                  class="transition-all duration-700" />
              </svg>
              <span class="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-gray-600">
                {{ Math.round(krProgress(kr)) }}%
              </span>
            </div>

            <!-- KR 内容 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <span class="text-sm text-gray-700">{{ kr.title }}</span>
                <button @click="editKRForObj(obj, kr)" class="p-0.5 text-gray-300 hover:text-blue-500 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0" title="编辑">✎</button>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <input v-model.number="kr.current" type="range"
                  :min="0" :max="kr.target"
                  class="flex-1 h-1.5 accent-blue-500 cursor-pointer"
                  @input="saveKRProgress(obj)" />
                <span class="text-xs text-gray-400 flex-shrink-0 min-w-[80px] text-right">
                  {{ kr.current }} / {{ kr.target }} {{ kr.unit }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 关联项目 -->
        <div v-if="getLinkedProjects(obj.id).length > 0" class="px-4 sm:px-5 py-3 bg-purple-50 border-t border-purple-100">
          <div class="text-xs font-medium text-purple-700 mb-1.5">📋 关联项目</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="p in getLinkedProjects(obj.id)" :key="p.id"
              class="text-xs bg-white text-purple-700 px-2 py-1 rounded border border-purple-200">
              {{ p.name }}
              <span v-if="getProjectTodoCount(p.id) > 0" class="text-purple-400 ml-1">
                ({{ getProjectTodoDone(p.id) }}/{{ getProjectTodoCount(p.id) }})
              </span>
            </span>
          </div>
        </div>

        <!-- 底部：添加 KR -->
        <div class="px-4 sm:px-5 py-3 bg-gray-50 border-t border-gray-100">
          <button @click="openAddKR(obj)" class="text-sm text-blue-500 hover:text-blue-600 flex items-center gap-1">
            <span>+</span> 添加关键结果
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredOKRs.length === 0" class="text-center py-16 text-gray-400">
        <div class="text-4xl mb-3">🎯</div>
        <p>{{ filterQuarter ? '该季度暂无目标' : '还没有目标，开始设定第一个吧！' }}</p>
        <button @click="openAddObj" class="mt-3 px-4 py-2 bg-blue-500 text-white rounded-lg text-sm">+ 新增目标</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 状态
const okrs = ref([])
const allProjects = ref([])
const allTodos = ref([])
const showObjModal = ref(false)
const showKRModal = ref(false)
const editingObj = ref({})
const editingKR = ref({})
const editingObjForKR = ref(null)
const filterQuarter = ref('')

// 可用季度
const availableQuarters = computed(() => {
  const quarters = new Set()
  okrs.value.forEach(o => quarters.add(o.quarter))
  // 加上当前季度
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth()
  const currentQ = `${y}-Q${Math.floor(m / 3) + 1}`
  quarters.add(currentQ)
  // 加下季度
  const nextQ = Math.floor(m / 3) + 2
  if (nextQ > 4) {
    quarters.add(`${y + 1}-Q1`)
  } else {
    quarters.add(`${y}-Q${nextQ}`)
  }
  return Array.from(quarters).sort().reverse()
})

// 加载数据
onMounted(async () => {
  // OKR 数据：优先 localStorage
  const savedOKR = localStorage.getItem('life-os-okrs')
  if (savedOKR) {
    okrs.value = JSON.parse(savedOKR)
  } else {
    try { const res = await fetch('/life-os/data/okr.json'); if (res.ok) okrs.value = await res.json() }
    catch (e) {}
  }
  // 项目数据：优先 localStorage（用户最新数据）
  const savedProj = localStorage.getItem('life-os-projects')
  if (savedProj) {
    allProjects.value = JSON.parse(savedProj)
  } else {
    try { const res = await fetch('/life-os/data/projects.json'); if (res.ok) allProjects.value = await res.json() }
    catch (e) {}
  }
  // 待办数据
  try { const res = await fetch('/life-os/data/todos.json'); if (res.ok) allTodos.value = await res.json() }
  catch (e) {}
})

// 筛选
const filteredOKRs = computed(() => {
  if (!filterQuarter.value) return okrs.value
  return okrs.value.filter(o => o.quarter === filterQuarter.value)
})

const completedCount = computed(() => okrs.value.filter(o => o.status === 'completed').length)
const activeCount = computed(() => okrs.value.filter(o => o.status === 'active').length)

const overallProgress = computed(() => {
  if (okrs.value.length === 0) return 0
  const sum = okrs.value.reduce((s, o) => s + objProgress(o), 0)
  return Math.round(sum / okrs.value.length)
})

// KR 进度
const krProgress = (kr) => {
  if (!kr.target || kr.target === 0) return 0
  return Math.min(100, (kr.current / kr.target) * 100)
}

// Objective 进度（KR 平均）
const objProgress = (obj) => {
  const krs = obj.key_results || []
  if (krs.length === 0) return obj.status === 'completed' ? 100 : 0
  const sum = krs.reduce((s, kr) => s + krProgress(kr), 0)
  return Math.round(sum / krs.length)
}

// 样式辅助
const statusClass = (s) => ({
  active: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  paused: 'bg-gray-100 text-gray-600'
}[s] || 'bg-gray-100 text-gray-600')

const statusLabel = (s) => ({ active: '进行中', completed: '已完成', paused: '暂停' }[s] || s)

const progressColor = (p) => {
  if (p >= 80) return 'bg-green-500'
  if (p >= 40) return 'bg-blue-500'
  if (p >= 20) return 'bg-yellow-500'
  return 'bg-red-400'
}

const krProgressColor = (p) => {
  if (p >= 80) return '#22c55e'
  if (p >= 40) return '#3b82f6'
  if (p >= 20) return '#eab308'
  return '#f87171'
}

// Object 操作
const openAddObj = () => {
  editingObj.value = {
    id: null,
    title: '',
    description: '',
    quarter: availableQuarters.value[0] || '',
    status: 'active',
    key_results: []
  }
  showObjModal.value = true
}

const editObj = (obj) => {
  editingObj.value = JSON.parse(JSON.stringify(obj))
  showObjModal.value = true
}

const saveObj = () => {
  if (!editingObj.value.title.trim()) {
    alert('请输入目标标题')
    return
  }
  const idx = okrs.value.findIndex(o => o.id === editingObj.value.id)
  if (idx !== -1) {
    okrs.value[idx] = { ...editingObj.value }
  } else {
    const maxId = Math.max(...okrs.value.map(o => o.id), 0)
    okrs.value.push({ ...editingObj.value, id: maxId + 1 })
  }
  showObjModal.value = false
  persist()
}

const deleteObj = (id) => {
  if (!id) return
  if (confirm('确定删除此目标及其所有关键结果？')) {
    okrs.value = okrs.value.filter(o => o.id !== id)
    showObjModal.value = false
    persist()
  }
}

// KR 操作
const openAddKR = (obj) => {
  editingObjForKR.value = obj
  editingKR.value = { id: null, title: '', current: 0, target: 100, unit: '%' }
  showKRModal.value = true
}

const editKRForObj = (obj, kr) => {
  editingObjForKR.value = obj
  editingKR.value = { ...kr }
  showKRModal.value = true
}

const saveKR = () => {
  if (!editingKR.value.title.trim()) {
    alert('请输入关键结果')
    return
  }
  const obj = editingObjForKR.value
  if (!obj.key_results) obj.key_results = []

  const idx = obj.key_results.findIndex(k => k.id === editingKR.value.id)
  if (idx !== -1) {
    obj.key_results[idx] = { ...editingKR.value }
    // 同时更新 okrs
    const objIdx = okrs.value.findIndex(o => o.id === obj.id)
    if (objIdx !== -1) okrs.value[objIdx] = JSON.parse(JSON.stringify(obj))
  } else {
    const maxId = Math.max(...obj.key_results.map(k => k.id), 0)
    obj.key_results.push({ ...editingKR.value, id: maxId + 1 })
    const objIdx = okrs.value.findIndex(o => o.id === obj.id)
    if (objIdx !== -1) okrs.value[objIdx] = JSON.parse(JSON.stringify(obj))
  }
  showKRModal.value = false
  persist()
}

const saveKRProgress = (obj) => {
  const objIdx = okrs.value.findIndex(o => o.id === obj.id)
  if (objIdx !== -1) okrs.value[objIdx] = JSON.parse(JSON.stringify(obj))
  persist()
}

// 获取关联到此 OKR 的项目
function getLinkedProjects(okrId) {
  return allProjects.value.filter(p => (p.okr_ids || []).includes(okrId))
}
function getProjectTodoCount(pid) {
  return allTodos.value.filter(t => t.project_id === pid).length
}
function getProjectTodoDone(pid) {
  return allTodos.value.filter(t => t.project_id === pid && t.status === 'completed').length
}

const persist = () => {
  localStorage.setItem('life-os-okrs', JSON.stringify(okrs.value))
}
</script>
