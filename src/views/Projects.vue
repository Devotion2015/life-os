<template>
  <div>
    <!-- ===== 编辑弹窗 ===== -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[8vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-4 sm:p-6 max-h-[80vh] overflow-y-auto">
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
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
            <input v-model="editingProject.deadline" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>

          <!-- KR 关联选择器 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">
              关联关键结果 (KR)
              <span class="text-gray-400 font-normal text-xs ml-1">— 选择后，该项目的待办完成率会自动推动 KR 进度</span>
            </label>
            <div v-if="okrs.length === 0" class="text-xs text-gray-400 py-2">暂无 OKR 数据，请先在「目标 OKR」中创建</div>
            <div v-for="obj in okrs" :key="obj.id" class="mb-2">
              <div class="text-xs font-medium text-gray-500 mb-1 pl-0.5">
                🎯 {{ obj.title }}
                <span v-if="obj.quarter" class="text-gray-400 ml-1">{{ obj.quarter }}</span>
              </div>
              <div class="space-y-1">
                <label v-for="kr in (obj.key_results || [])" :key="kr.id"
                  class="flex items-center gap-2 py-1 px-2 rounded hover:bg-blue-50 cursor-pointer text-sm"
                  :class="{ 'bg-blue-50': isKRSelected(kr.id) }">
                  <input type="checkbox" :checked="isKRSelected(kr.id)" @change="toggleKR(kr.id)" class="w-4 h-4 text-blue-500 rounded accent-blue-500" />
                  <span class="text-gray-700 flex-1">{{ kr.title }}</span>
                  <span class="text-[10px] text-gray-400">{{ kr.target }}{{ kr.unit }}</span>
                </label>
              </div>
            </div>
          </div>

          <div class="bg-blue-50 rounded-lg p-3 text-xs text-blue-700">
            💡 项目的<strong>待办事项</strong>直接在下方卡片中管理，无需在此弹窗添加。
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveProject" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 头部 + 统计 ===== -->
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
        <div class="text-xl font-bold text-purple-600">{{ totalKRs }}</div>
        <div class="text-xs text-gray-500">关联 KR</div>
      </div>
    </div>

    <!-- ===== 筛选栏 ===== -->
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
        <input v-model="searchText" type="text" placeholder="搜索项目或待办..." class="w-full sm:flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
      </div>
    </div>

    <!-- ===== 看板三列 ===== -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

      <div class="bg-gray-100 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3">📌 规划中 ({{ filteredByStatus('planning').length }})</h3>
        <div v-if="filteredByStatus('planning').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        <ProjectCard v-for="p in filteredByStatus('planning')" :key="p.id" :project="p"
          :todos="projectTodos(p)" :krMap="krNameMap" :nextSession="nextSessionFor(p.id)"
          @edit="editProject" @delete="deleteProject" @toggle-todo="toggleTodoStatus"
          @add-todo="addTodoToProject" @quick-move="moveTo(p, $event)" />
      </div>

      <div class="bg-blue-50 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3">🚀 进行中 ({{ filteredByStatus('active').length }})</h3>
        <div v-if="filteredByStatus('active').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        <ProjectCard v-for="p in filteredByStatus('active')" :key="p.id" :project="p"
          :todos="projectTodos(p)" :krMap="krNameMap" :showProgress="true" :nextSession="nextSessionFor(p.id)"
          @edit="editProject" @delete="deleteProject" @toggle-todo="toggleTodoStatus"
          @add-todo="addTodoToProject" @quick-move="moveTo(p, $event)" />
      </div>

      <div class="bg-green-50 rounded-lg p-3 sm:p-4">
        <h3 class="font-semibold text-gray-700 mb-3">✅ 已完成 / 暂停 ({{ filteredByStatus('completed').length + filteredByStatus('paused').length }})</h3>
        <div v-if="filteredByStatus('completed').length + filteredByStatus('paused').length === 0" class="text-center py-6 text-gray-400 text-sm">暂无项目</div>
        <div v-for="p in [...filteredByStatus('completed'), ...filteredByStatus('paused')]" :key="p.id"
          class="bg-white rounded-lg shadow p-3 mb-3 hover:shadow-md group" :class="{ 'opacity-75': p.status === 'completed' }">
          <div class="flex items-start justify-between mb-2">
            <h4 class="font-medium text-gray-800 text-sm" :class="{ 'line-through': p.status === 'completed' }">{{ p.name }}</h4>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100">
              <button @click="editProject(p)" class="text-gray-400 hover:text-blue-500 px-1 text-xs">✏️</button>
              <button @click="deleteProject(p.id)" class="text-gray-400 hover:text-red-500 px-1 text-xs">🗑️</button>
            </div>
          </div>
          <div class="flex flex-wrap gap-1.5 mb-1">
            <span class="text-xs px-1.5 py-0.5 rounded text-white" :class="typeColor(p.type)">{{ typeLabel(p.type) }}</span>
            <span :class="['text-xs px-1.5 py-0.5 rounded', p.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700']">{{ statusLabel(p.status) }}</span>
          </div>
          <div v-if="(p.kr_ids || []).length > 0" class="flex flex-wrap gap-1 mb-1.5">
            <span v-for="kid in p.kr_ids" :key="kid" class="text-[10px] bg-indigo-100 text-indigo-600 px-1 py-0.5 rounded">{{ krNameMap[kid] || kid }}</span>
          </div>
          <div class="text-xs text-gray-400">✅ {{ projectTodos(p).filter(t => t.status === 'completed').length }}/{{ projectTodos(p).length }} 待办</div>
          <div class="mt-2 flex gap-1.5">
            <button v-if="p.status !== 'active'" @click="moveTo(p, 'active')" class="text-xs text-blue-500 hover:text-blue-700">🔄 重启</button>
            <button v-if="p.status !== 'planning'" @click="moveTo(p, 'planning')" class="text-xs text-gray-500 hover:text-gray-700">📌 移回规划</button>
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
import { ref, computed, onMounted, h } from 'vue'

// ==================== ProjectCard 组件 ====================
const ProjectCard = {
  props: { project: Object, todos: Array, krMap: Object, showProgress: { type: Boolean, default: false }, nextSession: Object },
  emits: ['edit', 'delete', 'toggle-todo', 'add-todo', 'quick-move'],
  setup(props, { emit }) {
    const expanded = ref(false); const newText = ref(''); const visibleCount = 3
    const progress = computed(() => {
      if (props.todos.length === 0) return 0
      return Math.round((props.todos.filter(t => t.status === 'completed').length / props.todos.length) * 100)
    })
    const visibleTodos = computed(() => expanded.value ? props.todos : props.todos.slice(0, visibleCount))
    const hiddenCount = computed(() => Math.max(0, props.todos.length - visibleCount))
    const typeMap = { teaching: '📖 教学', content: '📝 内容', research: '🔬 科研', personal: '👤 个人' }
    const typeColorMap = { teaching: 'bg-blue-500', content: 'bg-purple-500', research: 'bg-green-600', personal: 'bg-pink-500' }
    function pc(pct) { return pct >= 80 ? 'bg-green-500' : pct >= 40 ? 'bg-blue-500' : 'bg-yellow-500' }
    function isOverdue(d) { return d ? new Date(d) < new Date(new Date().toDateString()) : false }
    function add() { if (!newText.value.trim()) return; emit('add-todo', { pid: props.project.id, text: newText.value.trim() }); newText.value = '' }

    return () => {
      const p = props.project; const todos = props.todos; const pct = progress.value
      return h('div', { class: 'bg-white rounded-lg shadow-sm p-3 mb-3 hover:shadow-md group transition-shadow' }, [
        h('div', { class: 'flex items-start justify-between mb-2' }, [
          h('h4', { class: 'font-medium text-gray-800 text-sm flex-1' }, p.name),
          h('div', { class: 'flex gap-0.5 ml-1' }, [
            h('button', { class: 'text-gray-300 hover:text-blue-500 px-1 text-xs opacity-0 group-hover:opacity-100', onClick: () => emit('edit', p) }, '✏️'),
            h('button', { class: 'text-gray-300 hover:text-red-500 px-1 text-xs opacity-0 group-hover:opacity-100', onClick: () => emit('delete', p.id) }, '🗑️')
          ])
        ]),
        h('div', { class: 'flex flex-wrap gap-1.5 mb-2' }, [
          h('span', { class: `text-xs px-1.5 py-0.5 rounded text-white ${typeColorMap[p.type] || 'bg-gray-500'}` }, typeMap[p.type] || p.type),
          p.deadline ? h('span', { class: `text-xs ${isOverdue(p.deadline) ? 'text-red-500 font-medium' : 'text-gray-500'}` }, `${isOverdue(p.deadline) ? '⚠️' : '📅'} ${p.deadline}`) : null,
        ].filter(Boolean)),
        (p.kr_ids || []).length > 0 ? h('div', { class: 'flex flex-wrap gap-1 mb-2' },
          p.kr_ids.map(kid => h('span', { class: 'text-[10px] bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded inline-flex items-center gap-0.5', key: kid }, [h('span', '🎯'), h('span', props.krMap[kid] || kid)]))
        ) : null,
        props.showProgress ? [
          h('div', { class: 'mb-1.5' }, [
            h('div', { class: 'flex justify-between text-xs text-gray-500 mb-0.5' }, [h('span', `进度 ${pct}%`), h('span', `${todos.filter(t => t.status === 'completed').length}/${todos.length} 完成`)]),
            h('div', { class: 'w-full bg-gray-200 rounded-full h-1.5' }, [h('div', { class: `h-1.5 rounded-full transition-all duration-300 ${pc(pct)}`, style: { width: `${pct}%` } })])
          ])
        ] : null,
        // 下次工作时段
        props.nextSession ? h('div', { class: 'mt-1.5 pt-1.5 border-t border-gray-100' }, [
          h('span', { class: 'text-[10px] text-indigo-600 block truncate' }, `📅 下次: ${props.nextSession.date} ${props.nextSession.title}`)
        ]) : null,
        // 待办列表
        todos.length > 0 ? h('div', { class: 'mt-1.5 pt-1.5 border-t border-gray-100 space-y-0.5' }, [
          ...visibleTodos.value.map(todo => h('div', { class: 'flex items-center gap-2 py-1 cursor-pointer hover:bg-gray-50 rounded px-1 -mx-1', onClick: () => emit('toggle-todo', todo) }, [
            h('span', { class: `w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center text-[10px] ${todo.status === 'completed' ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300'}` }, todo.status === 'completed' ? '✓' : ''),
            h('span', { class: `text-xs flex-1 ${todo.status === 'completed' ? 'line-through text-gray-400' : 'text-gray-700'}` }, todo.text)
          ])),
          hiddenCount.value > 0 ? h('div', { class: 'text-xs text-blue-500 mt-0.5 cursor-pointer hover:text-blue-700', onClick: () => { expanded.value = !expanded.value } }, expanded.value ? '▲ 收起' : `▼ +${hiddenCount.value} 更多`) : null
        ]) : h('div', { class: 'text-xs text-gray-300 text-center py-2 mt-1.5 pt-1.5 border-t border-gray-100' }, '暂无待办'),
        h('div', { class: 'mt-2 pt-1.5 border-t border-gray-100 flex gap-1.5' }, [
          h('input', { type: 'text', value: newText.value, class: 'flex-1 px-2 py-1 border border-gray-200 rounded text-xs focus:border-blue-300 focus:outline-none', placeholder: '快速添加待办...', onInput: e => { newText.value = e.target.value }, onKeyup: e => { if (e.key === 'Enter') add() } }),
          h('button', { class: 'text-xs bg-blue-500 text-white px-2.5 py-1 rounded hover:bg-blue-600 flex-shrink-0', onClick: add }, '+')
        ]),
        h('div', { class: 'mt-2 pt-1.5 border-t border-gray-100 flex gap-2' }, [
          p.status === 'planning' ? h('button', { class: 'text-xs text-blue-500 hover:text-blue-700', onClick: () => emit('quick-move', 'active') }, '🚀 开始') : null,
          ...(p.status === 'active' ? [
            h('button', { class: 'text-xs text-green-600 hover:text-green-800', onClick: () => emit('quick-move', 'completed') }, '✅ 完成'),
            h('button', { class: 'text-xs text-yellow-600 hover:text-yellow-800', onClick: () => emit('quick-move', 'paused') }, '⏸️ 暂停'),
            h('button', { class: 'text-xs text-gray-500 hover:text-gray-700', onClick: () => emit('quick-move', 'planning') }, '📌 回到规划'),
          ] : []),
        ].filter(Boolean))
      ])
    }
  }
}

// ==================== 主组件 ====================
const projects = ref([]); const okrs = ref([]); const allTodos = ref([]); const allEvents = ref([])
const filterType = ref('all'); const filterStatus = ref('all'); const searchText = ref('')
const showModal = ref(false); const editingProject = ref({})

const krNameMap = computed(() => {
  const m = {}
  for (const o of okrs.value) for (const k of (o.key_results || [])) m[k.id] = k.title.length > 15 ? k.title.slice(0, 15) + '…' : k.title
  return m
})

onMounted(async () => {
  const sp = localStorage.getItem('life-os-projects')
  if (sp) projects.value = JSON.parse(sp); else { try { const r = await fetch('/life-os/data/projects.json'); if (r.ok) projects.value = await r.json() } catch (e) {} }
  const st = localStorage.getItem('life-os-todos')
  if (st) allTodos.value = JSON.parse(st); else { try { const r = await fetch('/life-os/data/todos.json'); if (r.ok) allTodos.value = await r.json() } catch (e) {} }
  const so = localStorage.getItem('life-os-okrs')
  if (so) okrs.value = JSON.parse(so); else { try { const r = await fetch('/life-os/data/okr.json'); if (r.ok) okrs.value = await r.json() } catch (e) {} }
  const se = localStorage.getItem('life-os-events')
  if (se) allEvents.value = JSON.parse(se); else { try { const r = await fetch('/life-os/data/events.json'); if (r.ok) allEvents.value = await r.json() } catch (e) {} }
})

function projectTodos(p) { return allTodos.value.filter(t => t.project_id === p.id) }
function nextSessionFor(pid) {
  const now = new Date().toISOString().split('T')[0]
  return allEvents.value.filter(e => e.project_id === pid && e.date >= now).sort((a, b) => a.date.localeCompare(b.date))[0] || null
}
const totalTodos = computed(() => { const ids = new Set(projects.value.map(p => p.id)); return allTodos.value.filter(t => ids.has(t.project_id)).length })
const totalKRs = computed(() => { const set = new Set(); projects.value.forEach(p => (p.kr_ids || []).forEach(id => set.add(id))); return set.size })
const activeCount = computed(() => projects.value.filter(p => p.status === 'active').length)
const typeMap = { teaching: '📖 教学', content: '📝 内容', research: '🔬 科研', personal: '👤 个人' }
const typeColorMap = { teaching: 'bg-blue-500', content: 'bg-purple-500', research: 'bg-green-600', personal: 'bg-pink-500' }
function typeLabel(t) { return typeMap[t] || t }
function typeColor(t) { return typeColorMap[t] || 'bg-gray-500' }
function statusLabel(s) { return { planning: '📌 规划中', active: '🚀 进行中', completed: '✅ 已完成', paused: '⏸️ 暂停' }[s] || s }

function filteredByStatus(status) {
  return projects.value.filter(p => {
    if (p.status !== status) return false
    if (filterType.value !== 'all' && p.type !== filterType.value) return false
    if (searchText.value) { const s = searchText.value.toLowerCase(); if (!p.name.toLowerCase().includes(s) && !projectTodos(p).some(t => t.text.toLowerCase().includes(s))) return false }
    return true
  })
}

function isKRSelected(krId) { return (editingProject.value.kr_ids || []).includes(krId) }
function toggleKR(krId) {
  const ids = editingProject.value.kr_ids || []
  editingProject.value.kr_ids = ids.includes(krId) ? ids.filter(id => id !== krId) : [...ids, krId]
}

function toggleTodoStatus(todo) {
  todo.status = todo.status === 'completed' ? 'pending' : 'completed'
  todo.completed_date = todo.completed_date ? '' : new Date().toISOString().split('T')[0]
  localStorage.setItem('life-os-todos', JSON.stringify(allTodos.value))
}
function addTodoToProject({ pid, text }) {
  const maxId = Math.max(...allTodos.value.map(t => t.id), 0)
  allTodos.value.push({ id: maxId + 1, text, status: 'pending', priority: 'medium', project_id: pid, semester: '', deadline: '', notes: '', completed_date: '', created_at: new Date().toISOString().split('T')[0] })
  localStorage.setItem('life-os-todos', JSON.stringify(allTodos.value))
}

function openAddModal() { editingProject.value = { id: null, name: '', type: 'teaching', status: 'planning', deadline: '', kr_ids: [] }; showModal.value = true }
function editProject(project) { editingProject.value = JSON.parse(JSON.stringify(project)); if (!editingProject.value.kr_ids) editingProject.value.kr_ids = []; showModal.value = true }
function saveProject() {
  if (!editingProject.value.name.trim()) { alert('请输入项目名称'); return }
  const idx = projects.value.findIndex(p => p.id === editingProject.value.id)
  if (idx !== -1) projects.value[idx] = { ...editingProject.value }
  else projects.value.push({ ...editingProject.value, id: 'P' + String(projects.value.length + 1).padStart(3, '0') })
  showModal.value = false; localStorage.setItem('life-os-projects', JSON.stringify(projects.value))
}
function deleteProject(id) { if (!confirm('确定删除？关联待办不会删除。')) return; projects.value = projects.value.filter(p => p.id !== id); localStorage.setItem('life-os-projects', JSON.stringify(projects.value)) }
function moveTo(project, newStatus) { const idx = projects.value.findIndex(p => p.id === project.id); if (idx !== -1) { projects.value[idx] = { ...projects.value[idx], status: newStatus }; localStorage.setItem('life-os-projects', JSON.stringify(projects.value)) } }
</script>
