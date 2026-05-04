<template>
  <div>
    <!-- 事件编辑弹窗 -->
    <div v-if="showEventModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingEvent.id ? '编辑日程' : '新增日程' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题 *</label>
            <input v-model="editingEvent.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="日程标题..." />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">日期 *</label>
              <input v-model="editingEvent.date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
              <select v-model="editingEvent.category" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.emoji }} {{ cat.label }}</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">开始时间</label>
              <input v-model="editingEvent.start_time" type="time" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">结束时间</label>
              <input v-model="editingEvent.end_time" type="time" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">地点</label>
            <input v-model="editingEvent.location" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如: 教A-301" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <textarea v-model="editingEvent.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="补充说明..."></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end">
          <button @click="deleteEvent(editingEvent.id)" v-if="editingEvent.id" class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg mr-auto">删除</button>
          <button @click="showEventModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveEvent" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- 标题 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">📅 日程管理</h2>
      <div class="flex gap-2">
        <button @click="openAddModal" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm">+ 新增日程</button>
        <button @click="goToToday" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 text-sm">今天</button>
      </div>
    </div>

    <!-- 视图切换 & 导航 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
      <div class="flex items-center gap-2">
        <button @click="prevPeriod" class="px-3 py-1.5 border rounded-lg hover:bg-gray-100">&lt;</button>
        <h3 class="text-lg font-semibold text-gray-700 min-w-[160px] text-center">{{ periodLabel }}</h3>
        <button @click="nextPeriod" class="px-3 py-1.5 border rounded-lg hover:bg-gray-100">&gt;</button>
      </div>
      <div class="flex gap-1 bg-gray-100 rounded-lg p-1">
        <button v-for="v in views" :key="v.value" @click="currentView = v.value"
          class="px-3 py-1.5 rounded-md text-sm transition-colors"
          :class="currentView === v.value ? 'bg-white shadow text-blue-600 font-medium' : 'text-gray-600 hover:text-gray-800'">
          {{ v.label }}
        </button>
      </div>
    </div>

    <!-- 分类图例 -->
    <div class="flex flex-wrap gap-2 mb-4">
      <span v-for="cat in categories" :key="cat.value"
        class="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs"
        :class="[cat.bg, cat.text]">
        <span class="w-2 h-2 rounded-full" :class="cat.dot"></span>
        {{ cat.emoji }} {{ cat.label }}
      </span>
    </div>

    <!-- 月视图 -->
    <div v-if="currentView === 'month'" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="grid grid-cols-7 border-b">
        <div v-for="day in dayHeaders" :key="day" class="py-2 text-center text-xs sm:text-sm font-medium text-gray-500 bg-gray-50">
          {{ day }}
        </div>
      </div>
      <div class="grid grid-cols-7">
        <div v-for="day in monthDays" :key="day.key"
          @click="selectDay(day)"
          class="border-b border-r min-h-[60px] sm:min-h-[80px] p-1.5 cursor-pointer hover:bg-blue-50 transition-colors"
          :class="{
            'bg-blue-50': isToday(day.date),
            'text-gray-300': !day.isCurrentMonth,
            'ring-2 ring-blue-400': selectedDate === day.date
          }">
          <div class="text-xs sm:text-sm mb-1"
            :class="{
              'bg-blue-500 text-white w-6 h-6 rounded-full flex items-center justify-center font-bold': isToday(day.date),
              'text-gray-400': !day.isCurrentMonth
            }">
            {{ day.day }}
          </div>
          <div class="space-y-0.5">
            <div v-for="evt in day.events" :key="evt.id"
              class="text-[10px] sm:text-xs truncate px-1 py-0.5 rounded"
              :class="categoryColor(evt.category, 'bg')"
              @click.stop="editEvent(evt)"
              :title="evt.title">
              {{ evt.start_time ? evt.start_time + ' ' : '' }}{{ evt.title }}
            </div>
            <div v-if="day.moreCount > 0" class="text-[10px] text-gray-400 pl-1">
              +{{ day.moreCount }} 更多
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 周视图 / 日视图 -->
    <div v-if="currentView === 'week' || currentView === 'day'" class="bg-white rounded-lg shadow overflow-hidden">
      <!-- 列头 -->
      <div v-if="currentView === 'week'" class="grid grid-cols-8 border-b">
        <div class="py-2 text-center text-xs font-medium text-gray-500 bg-gray-50 border-r"></div>
        <div v-for="d in weekDays" :key="d.key"
          @click="selectedDate = d.date"
          class="py-2 text-center text-xs sm:text-sm cursor-pointer hover:bg-blue-50 transition-colors border-r"
          :class="{
            'bg-blue-50': isToday(d.date),
            'ring-2 ring-inset ring-blue-400': selectedDate === d.date
          }">
          <div class="font-medium">{{ d.weekDay }}</div>
          <div :class="{ 'bg-blue-500 text-white w-6 h-6 inline-flex items-center justify-center rounded-full': isToday(d.date), 'text-xs text-gray-500 mt-0.5': !isToday(d.date) }">
            {{ d.day }}
          </div>
        </div>
      </div>

      <!-- 时间轴 -->
      <div class="flex" :class="currentView === 'week' ? 'grid grid-cols-8' : ''">
        <!-- 时间标尺 -->
        <div class="flex-shrink-0 w-14 sm:w-16 border-r">
          <div v-for="h in 24" :key="h" class="text-[10px] sm:text-xs text-gray-400 text-right pr-1.5 relative" style="height: 48px;">
            <span class="absolute top-0 right-1.5 -translate-y-1/2">{{ h - 1 }}:00</span>
          </div>
        </div>

        <!-- 事件列（周视图多列） -->
        <template v-if="currentView === 'week'">
          <div v-for="d in weekDays" :key="d.key" class="flex-1 relative border-r"
            :class="{ 'bg-blue-50/30': isToday(d.date) }"
            style="height: 1152px;">
            <!-- 事件块 -->
            <div v-for="evt in d.events" :key="evt.id"
              @click="editEvent(evt)"
              class="absolute left-0.5 right-0.5 rounded px-1 py-0.5 cursor-pointer hover:opacity-80 transition-opacity overflow-hidden z-10"
              :class="categoryColor(evt.category, 'bg')"
              :style="timeSlotStyle(evt)">
              <div class="text-[9px] sm:text-[11px] font-medium truncate leading-tight">{{ evt.title }}</div>
              <div class="text-[9px] opacity-75 truncate">{{ evt.start_time }}{{ evt.end_time ? '-' + evt.end_time : '' }}</div>
            </div>
          </div>
        </template>

        <!-- 日视图：单列 -->
        <template v-if="currentView === 'day'">
          <div class="flex-1 relative" style="height: 1152px;">
            <div v-for="evt in dayTimelineEvents" :key="evt.id"
              @click="editEvent(evt)"
              class="absolute left-1 right-1 rounded px-2 py-1 cursor-pointer hover:opacity-80 transition-opacity overflow-hidden z-10"
              :class="categoryColor(evt.category, 'bg')"
              :style="timeSlotStyle(evt)">
              <div class="text-sm font-medium truncate">{{ evt.title }}</div>
              <div class="text-xs opacity-75">{{ evt.start_time }}{{ evt.end_time ? ' - ' + evt.end_time : '' }}</div>
              <div v-if="evt.location" class="text-xs opacity-75">📍 {{ evt.location }}</div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 选中日期的日程列表 -->
    <div v-if="selectedDate" class="mt-6 bg-white rounded-lg shadow p-4 sm:p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-gray-800">📋 {{ selectedDate }} 日程</h3>
        <button @click="openAddForDate" class="text-sm text-blue-500 hover:text-blue-600">+ 添加</button>
      </div>
      <div v-if="selectedEvents.length === 0" class="text-center py-8 text-gray-400">
        当天暂无日程安排
      </div>
      <div v-else class="space-y-3">
        <div v-for="evt in selectedEvents" :key="evt.id"
          class="flex items-start gap-3 p-3 rounded-lg border border-gray-100 hover:shadow transition-shadow cursor-pointer"
          @click="editEvent(evt)">
          <div class="w-2 h-full min-h-[40px] rounded-full flex-shrink-0" :class="categoryColor(evt.category, 'dot')"></div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-gray-800">{{ evt.title }}</div>
            <div class="flex flex-wrap items-center gap-2 mt-1 text-xs text-gray-500">
              <span v-if="evt.start_time">🕐 {{ evt.start_time }}{{ evt.end_time ? ' - ' + evt.end_time : '' }}</span>
              <span v-if="evt.location">📍 {{ evt.location }}</span>
              <span :class="categoryColor(evt.category, 'text')">{{ categoryLabel(evt.category) }}</span>
            </div>
            <div v-if="evt.description" class="mt-1.5 text-xs sm:text-sm text-gray-600">{{ evt.description }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 状态
const events = ref([])
const currentView = ref('month')
const currentDate = ref(new Date())
const selectedDate = ref(null)
const showEventModal = ref(false)
const editingEvent = ref({})
const isEditing = ref(false)

// 分类定义
const categories = [
  { value: '教学', label: '教学', emoji: '📖', dot: 'bg-blue-400', bg: 'bg-blue-50', text: 'text-blue-600' },
  { value: '科研', label: '科研', emoji: '🔬', dot: 'bg-purple-400', bg: 'bg-purple-50', text: 'text-purple-600' },
  { value: '行政', label: '行政', emoji: '📋', dot: 'bg-orange-400', bg: 'bg-orange-50', text: 'text-orange-600' },
  { value: '个人', label: '个人', emoji: '👤', dot: 'bg-green-400', bg: 'bg-green-50', text: 'text-green-600' },
  { value: '其他', label: '其他', emoji: '📌', dot: 'bg-gray-400', bg: 'bg-gray-50', text: 'text-gray-600' }
]

const views = [
  { value: 'month', label: '月' },
  { value: 'week', label: '周' },
  { value: 'day', label: '日' }
]

const dayHeaders = ['一', '二', '三', '四', '五', '六', '日']

// 分类颜色辅助
const catMap = {}
categories.forEach(c => { catMap[c.value] = c })

const categoryColor = (cat, key) => {
  const c = catMap[cat] || catMap['其他']
  return c[key] || ''
}

const categoryLabel = (cat) => {
  const c = catMap[cat] || catMap['其他']
  return c.emoji + ' ' + c.label
}

// 加载数据：优先 localStorage，首次从 JSON 导入
onMounted(async () => {
  const saved = localStorage.getItem('life-os-events')
  if (saved) {
    events.value = JSON.parse(saved)
  } else {
    try {
      const res = await fetch('/life-os/data/events.json')
      if (res.ok) events.value = await res.json()
    } catch (e) {
      console.error('加载日程数据失败', e)
    }
  }
})

// 格式化日期
const fmtDate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const isToday = (dateStr) => {
  const today = new Date()
  return dateStr === fmtDate(today)
}

const today = computed(() => fmtDate(new Date()))

// 月视图数据
const periodLabel = computed(() => {
  const d = new Date(currentDate.value)
  if (currentView.value === 'month') {
    return `${d.getFullYear()}年 ${d.getMonth() + 1}月`
  } else if (currentView.value === 'week') {
    const weekStart = getWeekStart(d)
    const weekEnd = addDays(weekStart, 6)
    return `${weekStart.getMonth() + 1}月${weekStart.getDate()}日 - ${weekEnd.getMonth() + 1}月${weekEnd.getDate()}日 ${d.getFullYear()}`
  } else {
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
  }
})

const addDays = (d, n) => {
  const r = new Date(d)
  r.setDate(r.getDate() + n)
  return r
}

const getWeekStart = (d) => {
  const r = new Date(d)
  const day = r.getDay()
  const diff = day === 0 ? -6 : 1 - day
  r.setDate(r.getDate() + diff)
  return r
}

const monthDays = computed(() => {
  const d = new Date(currentDate.value)
  const year = d.getFullYear()
  const month = d.getMonth()

  // 本月第一天
  const firstDay = new Date(year, month, 1)
  // 第一天是周几 (0=日, 1=一...)
  let startDayOfWeek = firstDay.getDay()
  startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1 // 转周一=0

  // 上月最后几天
  const prevMonth = new Date(year, month, 0)
  const prevDaysCount = prevMonth.getDate()

  const result = []
  const dayCount = new Date(year, month + 1, 0).getDate()

  // 建立事件索引
  const evtByDate = {}
  events.value.forEach(evt => {
    if (!evtByDate[evt.date]) evtByDate[evt.date] = []
    evtByDate[evt.date].push(evt)
  })

  // 填充上月日期
  for (let i = 0; i < startDayOfWeek; i++) {
    const day = prevDaysCount - startDayOfWeek + i + 1
    const date = fmtDate(new Date(year, month - 1, day))
    result.push({
      day, date, isCurrentMonth: false, key: `prev-${day}`,
      events: [],
      moreCount: 0
    })
  }

  // 本月日期
  for (let day = 1; day <= dayCount; day++) {
    const dateStr = fmtDate(new Date(year, month, day))
    const dayEvts = evtByDate[dateStr] || []
    result.push({
      day, date: dateStr, isCurrentMonth: true, key: `curr-${day}`,
      events: dayEvts.slice(0, 3),
      moreCount: Math.max(0, dayEvts.length - 3)
    })
  }

  // 补齐下月
  while (result.length < 42) {
    const day = result.length - (startDayOfWeek + dayCount) + 1
    const date = fmtDate(new Date(year, month + 1, day))
    result.push({
      day, date, isCurrentMonth: false, key: `next-${day}`,
      events: [],
      moreCount: 0
    })
  }

  return result
})

// 周视图数据
const weekDays = computed(() => {
  const weekStart = getWeekStart(new Date(currentDate.value))
  const evtByDate = {}
  events.value.forEach(evt => {
    if (!evtByDate[evt.date]) evtByDate[evt.date] = []
    evtByDate[evt.date].push(evt)
  })
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = addDays(weekStart, i)
    const date = fmtDate(d)
    days.push({
      day: d.getDate(),
      date,
      weekDay: ['一','二','三','四','五','六','日'][i],
      key: date,
      events: evtByDate[date] || []
    })
  }
  return days
})

// 日视图事件
const dayTimelineEvents = computed(() => {
  const date = fmtDate(currentDate.value)
  const evtByDate = {}
  events.value.forEach(evt => {
    if (evt.date === date) {
      if (!evtByDate[evt.date]) evtByDate[evt.date] = []
      evtByDate[evt.date].push(evt)
    }
  })
  return evtByDate[date] || []
})

// 选中日期的日程
const selectedEvents = computed(() => {
  if (!selectedDate.value) return []
  return events.value.filter(e => e.date === selectedDate.value)
})

// 时间槽样式
const timeSlotStyle = (evt) => {
  if (!evt.start_time) return { top: '0', height: '24px' }
  const [h, m] = (evt.start_time || '00:00').split(':').map(Number)
  const startMinutes = h * 60 + m
  let endMinutes = startMinutes + 60
  if (evt.end_time) {
    const [eh, em] = evt.end_time.split(':').map(Number)
    endMinutes = eh * 60 + em
  }
  const topPx = (startMinutes / 60) * 48
  const heightPx = Math.max(24, ((endMinutes - startMinutes) / 60) * 48)
  return { top: `${topPx}px`, height: `${heightPx}px` }
}

// 导航
const prevPeriod = () => {
  const d = new Date(currentDate.value)
  if (currentView.value === 'month') d.setMonth(d.getMonth() - 1)
  else if (currentView.value === 'week') d.setDate(d.getDate() - 7)
  else d.setDate(d.getDate() - 1)
  currentDate.value = d
}

const nextPeriod = () => {
  const d = new Date(currentDate.value)
  if (currentView.value === 'month') d.setMonth(d.getMonth() + 1)
  else if (currentView.value === 'week') d.setDate(d.getDate() + 7)
  else d.setDate(d.getDate() + 1)
  currentDate.value = d
}

const goToToday = () => {
  currentDate.value = new Date()
  selectedDate.value = fmtDate(new Date())
}

// 选择日期
const selectDay = (day) => {
  selectedDate.value = day.date
  // 如果点击的是其他月份，切换到该月
  if (!day.isCurrentMonth && currentView.value === 'month') {
    const [y, m] = day.date.split('-').map(Number)
    currentDate.value = new Date(y, m - 1, 1)
  }
}

// 弹窗管理
const openAddModal = () => {
  editingEvent.value = {
    id: null,
    title: '',
    date: selectedDate.value || today.value,
    category: '其他',
    start_time: '',
    end_time: '',
    location: '',
    description: ''
  }
  isEditing.value = false
  showEventModal.value = true
}

const openAddForDate = () => {
  editingEvent.value = {
    id: null,
    title: '',
    date: selectedDate.value,
    category: '其他',
    start_time: '',
    end_time: '',
    location: '',
    description: ''
  }
  isEditing.value = false
  showEventModal.value = true
}

const editEvent = (evt) => {
  editingEvent.value = { ...evt }
  isEditing.value = true
  showEventModal.value = true
}

const saveEvent = () => {
  if (!editingEvent.value.title.trim()) {
    alert('请输入日程标题')
    return
  }
  if (!editingEvent.value.date) {
    alert('请选择日期')
    return
  }
  if (isEditing.value) {
    const idx = events.value.findIndex(e => e.id === editingEvent.value.id)
    if (idx !== -1) events.value[idx] = { ...editingEvent.value }
  } else {
    const maxId = Math.max(...events.value.map(e => e.id), 0)
    events.value.push({ ...editingEvent.value, id: maxId + 1 })
  }
  showEventModal.value = false
  localStorage.setItem('life-os-events', JSON.stringify(events.value))
}

const deleteEvent = (id) => {
  if (!id) return
  if (confirm('确定删除此日程？')) {
    events.value = events.value.filter(e => e.id !== id)
    showEventModal.value = false
    localStorage.setItem('life-os-events', JSON.stringify(events.value))
  }
}
</script>
