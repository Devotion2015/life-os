<template>
  <div>
    <!-- ===== 添加/编辑 Objective 弹窗 ===== -->
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

    <!-- ===== 添加/编辑 KR 弹窗 ===== -->
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
              <label class="block text-sm font-medium text-gray-700 mb-1">目标值</label>
              <input v-model.number="editingKR.target" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">单位</label>
              <input v-model="editingKR.unit" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如: %" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">起始值</label>
              <input v-model.number="editingKR.current" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50" />
            </div>
          </div>
          <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-700">
            💡 <strong>起始值</strong>仅在 KR 没有关联项目时有效。关联项目后，进度由待办完成率自动计算。
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end">
          <button @click="deleteKRInModal" v-if="editingKR.id" class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg mr-auto">删除</button>
          <button @click="showKRModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveKR" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 标题 ===== -->
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

    <!-- ===== 统计卡片 ===== -->
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

    <!-- ===== OKR 列表 ===== -->
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
          <div v-for="kr in (obj.key_results || [])" :key="kr.id" class="px-4 sm:px-5 py-3">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0 w-10 h-10 relative">
                <svg class="w-10 h-10 transform -rotate-90">
                  <circle cx="20" cy="20" r="16" fill="none" stroke="#e5e7eb" stroke-width="4" />
                  <circle cx="20" cy="20" r="16" fill="none"
                    :stroke="krProgressColor(krProgressFor(kr))"
                    stroke-width="4" stroke-linecap="round"
                    :stroke-dasharray="100.5"
                    :stroke-dashoffset="100.5 - krProgressFor(kr)"
                    class="transition-all duration-700" />
                </svg>
                <span class="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-gray-600">
                  {{ Math.round(krProgressFor(kr)) }}%
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <span class="text-sm text-gray-700 font-medium">{{ kr.title }}</span>
                  <div class="flex items-center gap-0.5 flex-shrink-0">
                    <button @click="editKRForObj(obj, kr)" class="p-0.5 text-gray-300 hover:text-blue-500 rounded" title="编辑">✎</button>
                    <button @click="deleteKR(obj, kr)" class="p-0.5 text-gray-300 hover:text-red-500 rounded" title="删除">✕</button>
                  </div>
                </div>
                <div v-if="hasKRLinkedProjects(kr.id)" class="mt-1.5">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs text-green-600 font-medium">📊 自动 · {{ getKRTodoDone(kr.id) }}/{{ getKRTodoTotal(kr.id) }} 待办</span>
                    <span class="text-xs text-gray-400">{{ krAutoValue(kr) }} / {{ kr.target }} {{ kr.unit }}</span>
                  </div>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="p in getKRProjects(kr.id)" :key="p.id"
                      class="text-[10px] bg-green-50 text-green-700 px-1.5 py-0.5 rounded border border-green-100">{{ p.name }}</span>
                  </div>
                </div>
                <div v-else class="flex items-center gap-2 mt-1.5">
                  <input v-model.number="kr.current" type="range" :min="0" :max="kr.target"
                    class="flex-1 h-1.5 accent-blue-500 cursor-pointer" @input="persist()" />
                  <span class="text-xs text-gray-400 flex-shrink-0 min-w-[90px] text-right">{{ kr.current }} / {{ kr.target }} {{ kr.unit }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="getObjProjects(obj.id).length > 0" class="px-4 sm:px-5 py-3 bg-indigo-50 border-t border-indigo-100">
          <div class="text-xs font-medium text-indigo-700 mb-1.5">
            📋 本目标下 {{ getObjProjects(obj.id).length }} 个项目 · 合计 {{ getObjTodoDone(obj.id) }}/{{ getObjTodoTotal(obj.id) }} 待办完成
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="p in getObjProjects(obj.id)" :key="p.id"
              class="text-xs bg-white text-indigo-700 px-2 py-1 rounded border border-indigo-200">{{ p.name }}</span>
          </div>
        </div>

        <div class="px-4 sm:px-5 py-3 bg-gray-50 border-t border-gray-100">
          <button @click="openAddKR(obj)" class="text-sm text-blue-500 hover:text-blue-600 flex items-center gap-1"><span>+</span> 添加关键结果</button>
        </div>
      </div>

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

const okrs = ref([])
const allProjects = ref([])
const allTodos = ref([])
const showObjModal = ref(false)
const showKRModal = ref(false)
const editingObj = ref({})
const editingKR = ref({})
const editingObjForKR = ref(null)
const filterQuarter = ref('')

const krObjMap = computed(() => {
  const map = {}
  for (const obj of okrs.value) for (const kr of (obj.key_results || [])) map[kr.id] = obj.id
  return map
})

const availableQuarters = computed(() => {
  const qs = new Set(); okrs.value.forEach(o => qs.add(o.quarter))
  const now = new Date(); const y = now.getFullYear(); const m = now.getMonth()
  qs.add(`${y}-Q${Math.floor(m/3)+1}`)
  const nq = Math.floor(m/3)+2; qs.add(nq>4?`${y+1}-Q1`:`${y}-Q${nq}`)
  return Array.from(qs).sort().reverse()
})

onMounted(async () => {
  const s = localStorage.getItem('life-os-okrs')
  if (s) okrs.value = JSON.parse(s); else { try { const r = await fetch('/life-os/data/okr.json'); if (r.ok) okrs.value = await r.json() } catch(e){} }
  const sp = localStorage.getItem('life-os-projects')
  if (sp) allProjects.value = JSON.parse(sp); else { try { const r = await fetch('/life-os/data/projects.json'); if (r.ok) allProjects.value = await r.json() } catch(e){} }
  const st = localStorage.getItem('life-os-todos')
  if (st) allTodos.value = JSON.parse(st); else { try { const r = await fetch('/life-os/data/todos.json'); if (r.ok) allTodos.value = await r.json() } catch(e){} }
})

function getKRProjects(krId) { return allProjects.value.filter(p => (p.kr_ids||[]).includes(krId)) }
function getKRTodos(krId) { const pids = new Set(getKRProjects(krId).map(p=>p.id)); return allTodos.value.filter(t=>pids.has(t.project_id)) }
function hasKRLinkedProjects(krId) { return getKRProjects(krId).length > 0 }
function getKRTodoDone(krId) { return getKRTodos(krId).filter(t=>t.status==='completed').length }
function getKRTodoTotal(krId) { return getKRTodos(krId).length }
function krAutoProgress(krId) { const ts=getKRTodos(krId); return ts.length?Math.round(ts.filter(t=>t.status==='completed').length/ts.length*100):0 }
function krAutoValue(kr) { return Math.round(kr.target*krAutoProgress(kr.id)/100) }
function krProgressFor(kr) {
  if (hasKRLinkedProjects(kr.id)) return krAutoProgress(kr.id)
  if (!kr.target||kr.target===0) return 0; return Math.min(100,(kr.current/kr.target)*100)
}
function objProgress(obj) {
  const krs = obj.key_results||[]; if (krs.length===0) return obj.status==='completed'?100:0
  return Math.round(krs.reduce((s,kr)=>s+krProgressFor(kr),0)/krs.length)
}
function getObjProjects(objId) { return allProjects.value.filter(p=>(p.kr_ids||[]).some(kid=>krObjMap.value[kid]===objId)) }
function getObjTodoDone(objId) { const pids=new Set(getObjProjects(objId).map(p=>p.id)); return allTodos.value.filter(t=>pids.has(t.project_id)&&t.status==='completed').length }
function getObjTodoTotal(objId) { const pids=new Set(getObjProjects(objId).map(p=>p.id)); return allTodos.value.filter(t=>pids.has(t.project_id)).length }

const filteredOKRs = computed(()=>filterQuarter.value?okrs.value.filter(o=>o.quarter===filterQuarter.value):okrs.value)
const completedCount = computed(()=>okrs.value.filter(o=>o.status==='completed').length)
const activeCount = computed(()=>okrs.value.filter(o=>o.status==='active').length)
const overallProgress = computed(()=>{if(!okrs.value.length)return 0;return Math.round(okrs.value.reduce((s,o)=>s+objProgress(o),0)/okrs.value.length)})

const statusClass = s=>({active:'bg-blue-100 text-blue-700',completed:'bg-green-100 text-green-700',paused:'bg-gray-100 text-gray-600'}[s]||'bg-gray-100 text-gray-600')
const statusLabel = s=>({active:'进行中',completed:'已完成',paused:'暂停'}[s]||s)
const progressColor = p=>{if(p>=80)return'bg-green-500';if(p>=40)return'bg-blue-500';if(p>=20)return'bg-yellow-500';return'bg-red-400'}
const krProgressColor = p=>{if(p>=80)return'#22c55e';if(p>=40)return'#3b82f6';if(p>=20)return'#eab308';return'#f87171'}

const openAddObj = ()=>{editingObj.value={id:null,title:'',description:'',quarter:availableQuarters.value[0]||'',status:'active',key_results:[]};showObjModal.value=true}
const editObj = o=>{editingObj.value=JSON.parse(JSON.stringify(o));showObjModal.value=true}
const saveObj = ()=>{
  if(!editingObj.value.title.trim()){alert('请输入目标标题');return}
  const i=okrs.value.findIndex(o=>o.id===editingObj.value.id)
  if(i!==-1)okrs.value[i]={...editingObj.value}
  else okrs.value.push({...editingObj.value,id:Math.max(...okrs.value.map(o=>o.id),0)+1})
  showObjModal.value=false;persist()
}
const deleteObj = id=>{if(!id||!confirm('确定删除此目标？'))return;okrs.value=okrs.value.filter(o=>o.id!==id);showObjModal.value=false;persist()}
const openAddKR = obj=>{editingObjForKR.value=obj;editingKR.value={id:'',title:'',current:0,target:100,unit:'%'};showKRModal.value=true}
const editKRForObj = (obj,kr)=>{editingObjForKR.value=obj;editingKR.value={...kr};showKRModal.value=true}
const saveKR = ()=>{
  if(!editingKR.value.title.trim()){alert('请输入关键结果');return}
  const obj=editingObjForKR.value;if(!obj.key_results)obj.key_results=[]
  const i=obj.key_results.findIndex(k=>k.id===editingKR.value.id)
  if(i!==-1)obj.key_results[i]={...editingKR.value}
  else{let mn=0;for(const o of okrs.value)for(const k of(o.key_results||[])){const m=k.id.match(/^K(\d+)$/);if(m)mn=Math.max(mn,Number(m[1]))};obj.key_results.push({...editingKR.value,id:`K${String(mn+1).padStart(3,'0')}`})}
  const oi=okrs.value.findIndex(o=>o.id===obj.id);if(oi!==-1)okrs.value[oi]=JSON.parse(JSON.stringify(obj))
  showKRModal.value=false;persist()
}
const deleteKR = (obj, kr) => {
  if (!confirm(`确定删除「${kr.title}」？`)) return
  obj.key_results = (obj.key_results || []).filter(k => k.id !== kr.id)
  const oi = okrs.value.findIndex(o => o.id === obj.id)
  if (oi !== -1) okrs.value[oi] = JSON.parse(JSON.stringify(obj))
  persist()
}
const deleteKRInModal = () => {
  if (!editingKR.value.id) return
  const obj = editingObjForKR.value
  if (!obj) return
  deleteKR(obj, { id: editingKR.value.id, title: editingKR.value.title })
  showKRModal.value = false
}
const persist = ()=>localStorage.setItem('life-os-okrs',JSON.stringify(okrs.value))
</script>
