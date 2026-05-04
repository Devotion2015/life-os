<template>
  <div>
    <!-- ===== 影视编辑弹窗 ===== -->
    <div v-if="showMediaModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[8vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-4 sm:p-6 max-h-[85vh] overflow-y-auto">
        <h3 class="text-lg font-bold mb-4">{{ editingMedia.id ? '编辑影视' : '新增影视' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题 <span class="text-red-500">*</span></label>
            <input v-model="editingMedia.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="片名..." />
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">类型</label>
              <select v-model="editingMedia.type" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option value="tv">📺 电视剧</option>
                <option value="movie">🎬 电影</option>
                <option value="anime">🥷 动漫</option>
                <option value="documentary">📽️ 纪录片</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="editingMedia.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option value="want_to_watch">📌 想看</option>
                <option value="watching">▶️ 在看</option>
                <option value="completed">✅ 已看</option>
                <option value="dropped">❌ 弃了</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">评分</label>
              <select v-model.number="editingMedia.rating" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option :value="0">未评</option>
                <option v-for="n in 10" :key="n" :value="n">{{ '⭐'.repeat(Math.min(n, 5)) }} {{ n }}</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">进度</label>
              <input v-model="editingMedia.progress" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="如 E05/30 或 已看完" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">标签（逗号分隔）</label>
              <input v-model="mediaTagsStr" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="科幻, 国产, ..." />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
              <input v-model="editingMedia.startDate" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">完成日期</label>
              <input v-model="editingMedia.completedDate" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <textarea v-model="editingMedia.notes" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="观后感..."></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showMediaModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveMedia" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 爱好记录弹窗 ===== -->
    <div v-if="showHobbyLogModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[15vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-sm p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">🏃 打卡「{{ activeHobby?.name }}」</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">时长（分钟）</label>
            <input v-model.number="newHobbyLog.duration" type="number" min="1" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">心情</label>
            <div class="flex gap-2">
              <button
                v-for="mood in moods" :key="mood.key"
                @click="newHobbyLog.mood = mood.key"
                class="flex-1 py-2 rounded-lg text-lg transition-all text-center"
                :class="newHobbyLog.mood === mood.key ? 'ring-2 ring-blue-500 bg-blue-50' : 'bg-gray-100 hover:bg-gray-200'"
              >{{ mood.emoji }}</button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <input v-model="newHobbyLog.notes" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="做了什么..." />
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showHobbyLogModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveHobbyLog" class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">💪 打卡</button>
        </div>
      </div>
    </div>

    <!-- ===== 目标编辑弹窗 ===== -->
    <div v-if="showGoalModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[10vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingGoal.id ? '编辑目标' : '新增目标' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">目标 <span class="text-red-500">*</span></label>
            <input v-model="editingGoal.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="小目标..." />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
              <select v-model="editingGoal.category" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option value="media">📺 影视</option>
                <option value="fitness">🏃 运动</option>
                <option value="learning">📚 学习</option>
                <option value="travel">✈️ 旅行</option>
                <option value="other">🎯 其他</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
              <input v-model="editingGoal.deadline" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">当前进度</label>
              <input v-model.number="editingGoal.progress" type="number" min="0" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">目标总量</label>
              <input v-model.number="editingGoal.total" type="number" min="1" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showGoalModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveGoal" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 主内容 ===== -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">🎮 娱乐生活</h2>
      <div class="flex gap-2 flex-wrap">
        <button @click="openNewMedia" class="px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 text-sm whitespace-nowrap">+ 新影视</button>
        <button @click="openNewGoal" class="px-3 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 text-sm whitespace-nowrap">+ 新目标</button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-gray-800">{{ media.length }}</div>
        <div class="text-xs text-gray-500">影视记录</div>
      </div>
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-purple-600">{{ watchingCount }}</div>
        <div class="text-xs text-gray-500">正在追</div>
      </div>
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-green-600">{{ totalLogsThisWeek }}</div>
        <div class="text-xs text-gray-500">本周打卡</div>
      </div>
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-orange-600">{{ maxStreak }}</div>
        <div class="text-xs text-gray-500">最长连续</div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex border-b border-gray-200 mb-6 gap-1 overflow-x-auto">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors"
        :class="activeTab === tab.key ? 'border-purple-500 text-purple-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
      >{{ tab.icon }} {{ tab.label }}</button>
    </div>

    <!-- ===== Tab 1: 影视追剧 ===== -->
    <div v-if="activeTab === 'media'">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- 想看 -->
        <div class="bg-yellow-50 rounded-lg p-3 sm:p-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📌</span> 想看 <span class="text-sm text-gray-400 ml-auto">{{ mediaByStatus('want_to_watch').length }}</span>
          </h3>
          <div class="space-y-3">
            <div v-for="item in mediaByStatus('want_to_watch')" :key="item.id" class="bg-white rounded-lg shadow p-3 hover:shadow-md transition-shadow group">
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-gray-800 text-sm leading-snug pr-2">{{ item.title }}</h4>
                <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                  <button @click="editMedia(item)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
                  <button @click="deleteMedia(item.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
                </div>
              </div>
              <div class="flex items-center gap-1.5 text-xs text-gray-500">
                <span class="bg-gray-100 px-1.5 py-0.5 rounded">{{ typeLabel(item.type) }}</span>
                <span v-if="item.notes" class="truncate" :title="item.notes">{{ item.notes }}</span>
              </div>
            </div>
            <div v-if="mediaByStatus('want_to_watch').length === 0" class="text-center py-4 text-gray-400 text-xs">暂无</div>
          </div>
        </div>

        <!-- 在看 -->
        <div class="bg-purple-50 rounded-lg p-3 sm:p-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>▶️</span> 在看 <span class="text-sm text-gray-400 ml-auto">{{ mediaByStatus('watching').length }}</span>
          </h3>
          <div class="space-y-3">
            <div v-for="item in mediaByStatus('watching')" :key="item.id" class="bg-white rounded-lg shadow p-3 hover:shadow-md transition-shadow group">
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-gray-800 text-sm leading-snug pr-2">{{ item.title }}</h4>
                <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                  <button @click="editMedia(item)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
                  <button @click="deleteMedia(item.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
                </div>
              </div>
              <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-1">
                <span class="bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">{{ typeLabel(item.type) }}</span>
                <span v-if="item.progress" class="text-purple-600 font-medium">{{ item.progress }}</span>
              </div>
              <div v-if="item.notes" class="text-xs text-gray-500 line-clamp-1">{{ item.notes }}</div>
            </div>
            <div v-if="mediaByStatus('watching').length === 0" class="text-center py-4 text-gray-400 text-xs">暂无</div>
          </div>
        </div>

        <!-- 已看 / 弃了 -->
        <div class="bg-green-50 rounded-lg p-3 sm:p-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>✅</span> 已看/弃了 <span class="text-sm text-gray-400 ml-auto">{{ mediaByStatus('completed').length + mediaByStatus('dropped').length }}</span>
          </h3>
          <div class="space-y-3">
            <div v-for="item in [...mediaByStatus('completed'), ...mediaByStatus('dropped')]" :key="item.id" class="bg-white rounded-lg shadow p-3 hover:shadow-md transition-shadow group" :class="{ 'opacity-75': item.status === 'dropped' }">
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-gray-800 text-sm leading-snug pr-2" :class="{ 'line-through text-gray-400': item.status === 'dropped' }">{{ item.title }}</h4>
                <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                  <button @click="editMedia(item)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
                  <button @click="deleteMedia(item.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
                </div>
              </div>
              <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-1">
                <span class="bg-gray-100 px-1.5 py-0.5 rounded">{{ typeLabel(item.type) }}</span>
                <span v-if="item.status === 'dropped'" class="text-red-500">弃了</span>
                <span v-if="item.rating > 0" class="text-yellow-500">{{ '⭐'.repeat(Math.min(item.rating, 5)) }} {{ item.rating }}</span>
              </div>
              <div v-if="item.notes" class="text-xs text-gray-500 line-clamp-1">{{ item.notes }}</div>
            </div>
            <div v-if="mediaByStatus('completed').length + mediaByStatus('dropped').length === 0" class="text-center py-4 text-gray-400 text-xs">暂无</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== Tab 2: 爱好打卡 ===== -->
    <div v-if="activeTab === 'hobbies'">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="hobby in hobbies" :key="hobby.id" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ hobbyCategoryEmoji(hobby.category) }}</span>
              <div>
                <h4 class="font-semibold text-gray-800 text-sm">{{ hobby.name }}</h4>
                <p class="text-xs text-gray-500">{{ hobby.frequency }}</p>
              </div>
            </div>
            <button @click="openHobbyLog(hobby)" class="text-2xl hover:scale-110 transition-transform active:scale-95" title="打卡">💪</button>
          </div>

          <!-- 连续打卡 -->
          <div class="flex items-center gap-2 mb-3">
            <span class="text-lg">🔥</span>
            <span class="text-sm font-medium text-orange-600">{{ hobby.streak }} 天连续</span>
          </div>

          <!-- 最近记录 -->
          <div v-if="hobby.log.length > 0" class="border-t pt-3 space-y-2">
            <div class="text-xs font-medium text-gray-500 mb-1">最近动态</div>
            <div v-for="(l, idx) in hobby.log.slice(0, 3)" :key="idx" class="flex items-center gap-2 text-xs">
              <span>{{ l.date }}</span>
              <span class="text-gray-500">{{ l.duration }}分钟</span>
              <span>{{ moodEmoji(l.mood) }}</span>
              <span class="text-gray-400 truncate flex-1" v-if="l.notes">{{ l.notes }}</span>
            </div>
          </div>

          <div v-if="hobby.notes" class="mt-3 pt-3 border-t text-xs text-gray-400">{{ hobby.notes }}</div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="hobbies.length === 0" class="text-center py-12 text-gray-400">
        <div class="text-4xl mb-3">🏃</div>
        <p>还没有添加爱好</p>
      </div>
    </div>

    <!-- ===== Tab 3: 生活目标 ===== -->
    <div v-if="activeTab === 'goals'">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="goal in goals" :key="goal.id" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow group">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0 pr-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-base">{{ goalCategoryEmoji(goal.category) }}</span>
                <h4 class="font-medium text-gray-800 text-sm">{{ goal.title }}</h4>
              </div>
              <div v-if="goal.deadline" class="text-xs text-gray-400 mt-1">📅 {{ goal.deadline }}</div>
            </div>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
              <button @click="editGoal(goal)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
              <button @click="deleteGoal(goal.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
            </div>
          </div>
          <!-- 进度 -->
          <div class="space-y-1">
            <div class="flex items-center justify-between text-xs text-gray-500">
              <span>{{ goal.progress }} / {{ goal.total }}</span>
              <span>{{ goalPct(goal) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all"
                :class="goal.completed ? 'bg-green-500' : goalPct(goal) >= 80 ? 'bg-green-500' : goalPct(goal) >= 50 ? 'bg-blue-500' : 'bg-yellow-500'"
                :style="{ width: goalPct(goal) + '%' }"
              ></div>
            </div>
          </div>
          <!-- 操作 -->
          <div class="flex gap-2 mt-3">
            <button
              @click="goalProgress(goal, -1)"
              class="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
              title="减少进度"
            >-</button>
            <button
              @click="goalProgress(goal, 1)"
              class="flex-1 py-1 text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition-colors font-medium"
            >+1 进度</button>
            <button
              @click="toggleGoal(goal)"
              class="px-2 py-1 text-xs rounded transition-colors"
              :class="goal.completed ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-gray-100 hover:bg-gray-200 text-gray-500'"
              :title="goal.completed ? '标记未完成' : '标记完成'"
            >{{ goal.completed ? '✓' : '○' }}</button>
          </div>
        </div>
      </div>
      <div v-if="goals.length === 0" class="text-center py-12 text-gray-400">
        <div class="text-4xl mb-3">🎯</div>
        <p>还没有生活目标</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// ===== 数据 =====
const media = ref([])
const hobbies = ref([])
const goals = ref([])

// ===== UI 状态 =====
const tabs = [
  { key: 'media', label: '影视追剧', icon: '📺' },
  { key: 'hobbies', label: '爱好打卡', icon: '🏃' },
  { key: 'goals', label: '生活目标', icon: '🎯' },
]
const activeTab = ref('media')

// ===== 弹窗 =====
const showMediaModal = ref(false)
const editingMedia = ref({})
const mediaTagsStr = ref('')
const isEditingMedia = ref(false)

const showHobbyLogModal = ref(false)
const activeHobby = ref(null)
const newHobbyLog = ref({ duration: 30, mood: 'good', notes: '' })

const showGoalModal = ref(false)
const editingGoal = ref({})
const isEditingGoal = ref(false)

// ===== 初始化 =====
onMounted(async () => {
  try {
    const res = await fetch('/life-os/data/life.json')
    if (res.ok) {
      const data = await res.json()
      media.value = data.media || []
      hobbies.value = data.hobbies || []
      goals.value = data.goals || []
      return
    }
  } catch (e) {}
  const saved = localStorage.getItem('life-os-entertainment')
  if (saved) {
    const d = JSON.parse(saved)
    media.value = d.media || []
    hobbies.value = d.hobbies || []
    goals.value = d.goals || []
  }
})

function save() {
  localStorage.setItem('life-os-entertainment', JSON.stringify({ media: media.value, hobbies: hobbies.value, goals: goals.value }))
}

// ===== 计算 =====
const watchingCount = computed(() => media.value.filter(m => m.status === 'watching').length)
const maxStreak = computed(() => Math.max(...hobbies.value.map(h => h.streak), 0))

const totalLogsThisWeek = computed(() => {
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7*24*60*60*1000).toISOString().split('T')[0]
  return hobbies.value.reduce((sum, h) => sum + h.log.filter(l => l.date >= weekAgo).length, 0)
})

// ===== 影视 =====
function mediaByStatus(st) { return media.value.filter(m => m.status === st) }

const typeLabels = { tv: '📺 剧', movie: '🎬 电影', anime: '🥷 动漫', documentary: '📽️ 纪录' }
function typeLabel(t) { return typeLabels[t] || t }

function openNewMedia() {
  editingMedia.value = { id: null, title: '', type: 'movie', status: 'want_to_watch', progress: '', rating: 0, notes: '', tags: [], startDate: null, completedDate: null }
  mediaTagsStr.value = ''
  isEditingMedia.value = false
  showMediaModal.value = true
}

function editMedia(item) {
  editingMedia.value = { ...item, tags: [...(item.tags || [])] }
  mediaTagsStr.value = (item.tags || []).join(', ')
  isEditingMedia.value = true
  showMediaModal.value = true
}

function saveMedia() {
  if (!editingMedia.value.title.trim()) { alert('请输入片名'); return }
  editingMedia.value.tags = mediaTagsStr.value.split(',').map(t => t.trim()).filter(Boolean)
  if (editingMedia.value.status === 'completed' && !editingMedia.value.completedDate) {
    editingMedia.value.completedDate = new Date().toISOString().split('T')[0]
  }

  if (isEditingMedia.value) {
    const idx = media.value.findIndex(m => m.id === editingMedia.value.id)
    if (idx !== -1) media.value[idx] = { ...editingMedia.value }
  } else {
    const maxN = Math.max(...media.value.map(m => parseInt(m.id.slice(1))), 0)
    media.value.push({ ...editingMedia.value, id: 'M' + String(maxN + 1).padStart(3, '0') })
  }
  showMediaModal.value = false
  save()
}

function deleteMedia(id) {
  if (!confirm('确定删除这个影视记录吗？')) return
  media.value = media.value.filter(m => m.id !== id)
  save()
}

// ===== 爱好 =====
function hobbyCategoryEmoji(c) { return { fitness: '🏃', learning: '📖', art: '🎸', gaming: '🎮', cooking: '🍳', travel: '✈️' }[c] || '⭐' }

const moodMap = { great: '😆', good: '😊', ok: '😐', bad: '😞' }
function moodEmoji(m) { return moodMap[m] || '' }

const moods = [
  { key: 'great', emoji: '😆' },
  { key: 'good', emoji: '😊' },
  { key: 'ok', emoji: '😐' },
  { key: 'bad', emoji: '😞' },
]

function openHobbyLog(hobby) {
  activeHobby.value = hobby
  newHobbyLog.value = { duration: hobby.category === 'fitness' ? 35 : 30, mood: 'good', notes: '' }
  showHobbyLogModal.value = true
}

function saveHobbyLog() {
  const hobby = activeHobby.value
  const today = new Date().toISOString().split('T')[0]
  hobby.log.unshift({ date: today, duration: newHobbyLog.value.duration, notes: newHobbyLog.value.notes, mood: newHobbyLog.value.mood })

  // 计算连续天数
  const dates = [...new Set(hobby.log.map(l => l.date))].sort().reverse()
  let streak = 0
  const check = new Date(today)
  for (const d of dates) {
    const expected = check.toISOString().split('T')[0]
    if (d === expected) { streak++; check.setDate(check.getDate() - 1) }
    else if (streak === 0) { check.setDate(check.getDate() - 1) }
    else break
  }
  hobby.streak = streak
  showHobbyLogModal.value = false
  save()
}

// ===== 目标 =====
function goalPct(g) { return g.total > 0 ? Math.round((g.progress / g.total) * 100) : 0 }

function goalCategoryEmoji(c) { return { media: '📺', fitness: '🏃', learning: '📚', travel: '✈️', other: '🎯' }[c] || '🎯' }

function openNewGoal() {
  editingGoal.value = { id: null, title: '', category: 'other', progress: 0, total: 1, deadline: null, completed: false }
  isEditingGoal.value = false
  showGoalModal.value = true
}

function editGoal(g) {
  editingGoal.value = { ...g }
  isEditingGoal.value = true
  showGoalModal.value = true
}

function saveGoal() {
  if (!editingGoal.value.title.trim()) { alert('请输入目标'); return }
  if (editingGoal.value.progress >= editingGoal.value.total) editingGoal.value.completed = true

  if (isEditingGoal.value) {
    const idx = goals.value.findIndex(g => g.id === editingGoal.value.id)
    if (idx !== -1) goals.value[idx] = { ...editingGoal.value }
  } else {
    const maxN = Math.max(...goals.value.map(g => parseInt(g.id.slice(1))), 0)
    goals.value.push({ ...editingGoal.value, id: 'G' + String(maxN + 1).padStart(3, '0') })
  }
  showGoalModal.value = false
  save()
}

function goalProgress(goal, delta) {
  goal.progress = Math.max(0, Math.min(goal.total, goal.progress + delta))
  goal.completed = goal.progress >= goal.total
  save()
}

function toggleGoal(goal) {
  goal.completed = !goal.completed
  if (goal.completed) goal.progress = goal.total
  save()
}

function deleteGoal(id) {
  if (!confirm('确定删除这个目标吗？')) return
  goals.value = goals.value.filter(g => g.id !== id)
  save()
}
</script>

<style scoped>
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}
</style>
