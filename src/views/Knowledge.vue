<template>
  <div>
    <!-- ===== 条目编辑弹窗 ===== -->
    <div v-if="showEntryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[6vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl p-4 sm:p-6 max-h-[85vh] overflow-y-auto">
        <h3 class="text-lg font-bold mb-4">{{ editingEntry.id ? '编辑知识条目' : '新建知识条目' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题 <span class="text-red-500">*</span></label>
            <input v-model="editingEntry.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="知识条目标题..." />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
              <select v-model="editingEntry.category" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="programming">💻 编程技术</option>
                <option value="gis">🗺️ 测绘/GIS</option>
                <option value="teaching">📖 教学</option>
                <option value="content">📝 内容创作</option>
                <option value="reading">📚 读书笔记</option>
                <option value="life">🎁 生活</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="editingEntry.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="draft">📝 草稿</option>
                <option value="published">✅ 已发布</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标签（逗号分隔）</label>
            <input v-model="tagsStr" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如: Vue, 前端, JavaScript" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">来源信息</label>
            <div class="grid grid-cols-3 gap-2">
              <select v-model="editingEntry.source.type" class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option value="article">📄 文章</option>
                <option value="book">📚 书籍</option>
                <option value="course">🎓 课程</option>
                <option value="note">📝 笔记</option>
              </select>
              <input v-model="editingEntry.source.title" type="text" class="col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="来源名称/标题" />
            </div>
            <input v-model="editingEntry.source.url" type="text" class="w-full mt-2 px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="来源链接（可选）" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容（Markdown）</label>
            <textarea v-model="editingEntry.content" rows="10" class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500" placeholder="支持 Markdown 格式..."></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showEntryModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveEntry" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 条目详情弹窗 ===== -->
    <div v-if="detailEntry" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[6vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl p-4 sm:p-6 max-h-[85vh] overflow-y-auto">
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1 min-w-0 mr-4">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="text-xl font-bold text-gray-800">{{ detailEntry.title }}</h3>
              <span class="text-xs px-2 py-0.5 rounded text-white" :class="categoryColor(detailEntry.category)">{{ categoryLabel(detailEntry.category) }}</span>
              <span v-if="detailEntry.status === 'draft'" class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">草稿</span>
            </div>
          </div>
          <button @click="detailEntry = null" class="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>
        <!-- 来源 -->
        <div v-if="detailEntry.source?.title" class="text-sm text-gray-500 mb-3">
          📌 来源：{{ sourceTypeLabel(detailEntry.source.type) }}「{{ detailEntry.source.title }}」
          <a v-if="detailEntry.source.url" :href="detailEntry.source.url" target="_blank" class="text-blue-500 hover:underline ml-1">🔗</a>
        </div>
        <!-- 标签 -->
        <div class="flex flex-wrap gap-1.5 mb-4">
          <span v-for="tag in detailEntry.tags" :key="tag" class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{{ tag }}</span>
          <span class="text-xs text-gray-400">🕐 {{ detailEntry.updatedAt || detailEntry.createdAt }}</span>
        </div>
        <!-- 正文 - 简单 Markdown 渲染 -->
        <div class="prose prose-sm max-w-none border-t pt-4" v-html="renderMarkdown(detailEntry.content)"></div>
        <!-- 相关条目 -->
        <div v-if="detailEntry.relatedEntries?.length > 0" class="border-t pt-4 mt-4">
          <div class="text-sm font-medium text-gray-700 mb-2">🔗 相关条目</div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="rid in detailEntry.relatedEntries" :key="rid"
              @click="viewRelatedEntry(rid)"
              class="text-sm text-blue-600 hover:underline bg-blue-50 px-2 py-1 rounded"
            >
              {{ getEntryTitle(rid) }}
            </button>
          </div>
        </div>
        <!-- 操作 -->
        <div class="flex gap-2 mt-4 border-t pt-4">
          <button @click="editEntry(detailEntry); detailEntry = null" class="px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600">✏️ 编辑</button>
          <button @click="detailEntry = null" class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded">关闭</button>
        </div>
      </div>
    </div>

    <!-- ===== 阅读项编辑弹窗 ===== -->
    <div v-if="showReadingModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[10vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingReading.id ? '编辑阅读项' : '新增阅读项' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">书名/标题 <span class="text-red-500">*</span></label>
            <input v-model="editingReading.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="书或文章标题..." />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">作者</label>
              <input v-model="editingReading.author" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="作者" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">类型</label>
              <select v-model="editingReading.type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="book">📚 书</option>
                <option value="article">📄 文章</option>
                <option value="paper">📃 论文</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="editingReading.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="want_to_read">📌 想读</option>
                <option value="reading">📖 在读</option>
                <option value="completed">✅ 已读</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">进度 (%)</label>
              <input v-model.number="editingReading.progress" type="number" min="0" max="100" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">评分</label>
              <select v-model.number="editingReading.rating" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option :value="0">未评分</option>
                <option :value="1">⭐</option>
                <option :value="2">⭐⭐</option>
                <option :value="3">⭐⭐⭐</option>
                <option :value="4">⭐⭐⭐⭐</option>
                <option :value="5">⭐⭐⭐⭐⭐</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">阅读笔记</label>
              <input v-model="editingReading.notes" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="关联条目 ID（可选）" />
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showReadingModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveReading" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 主内容 ===== -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">📚 知识管理</h2>
      <div class="flex gap-2">
        <button @click="openNewEntry" class="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm">+ 新条目</button>
        <button @click="openNewReading" class="px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm">+ 新阅读</button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 sm:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-gray-800">{{ entries.length }}</div>
        <div class="text-xs text-gray-500">知识条目</div>
      </div>
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-purple-600">{{ readingList.length }}</div>
        <div class="text-xs text-gray-500">在读书目</div>
      </div>
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-green-600">{{ readCount }}</div>
        <div class="text-xs text-gray-500">已读完</div>
      </div>
      <div class="bg-white rounded-lg shadow px-3 py-3 text-center">
        <div class="text-lg sm:text-xl font-bold text-orange-600">{{ categories.length }}</div>
        <div class="text-xs text-gray-500">知识分类</div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex border-b border-gray-200 mb-6 gap-1 overflow-x-auto">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors"
        :class="activeTab === tab.key ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
      >
        {{ tab.icon }} {{ tab.label }}
        <span v-if="tab.key === 'wiki'" class="ml-1 text-xs bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded-full">{{ entries.length }}</span>
        <span v-if="tab.key === 'reading'" class="ml-1 text-xs bg-green-100 text-green-600 px-1.5 py-0.5 rounded-full">{{ readingList.length }}</span>
      </button>
    </div>

    <!-- ===== Tab 1: 知识库 ===== -->
    <div v-if="activeTab === 'wiki'">
      <!-- 搜索栏 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-3">
          <select v-model="filterCategory" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="all">全部分类</option>
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.icon }} {{ cat.label }}</option>
          </select>
          <select v-model="filterStatus" class="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="all">全部状态</option>
            <option value="published">✅ 已发布</option>
            <option value="draft">📝 草稿</option>
          </select>
          <input v-model="searchText" type="text" placeholder="搜索知识条目..." class="w-full sm:flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
        </div>
      </div>

      <!-- 条目卡片网格 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="entry in filteredEntries" :key="entry.id"
          class="bg-white rounded-lg shadow p-3 sm:p-4 hover:shadow-md transition-all cursor-pointer group"
          @click="viewEntry(entry)"
        >
          <div class="flex items-start gap-2 mb-2">
            <span class="text-xs px-1.5 py-0.5 rounded text-white flex-shrink-0" :class="categoryColor(entry.category)">{{ categoryLabelShort(entry.category) }}</span>
            <h4 class="font-medium text-gray-800 text-sm leading-snug flex-1 min-w-0 line-clamp-2">{{ entry.title }}</h4>
          </div>
          <p class="text-xs text-gray-500 mb-3 line-clamp-2">
            {{ stripMarkdown(entry.content).substring(0, 80) }}
          </p>
          <div class="flex flex-wrap items-center gap-1 mb-2">
            <span v-for="tag in entry.tags.slice(0, 3)" :key="tag" class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">{{ tag }}</span>
            <span v-if="entry.tags.length > 3" class="text-xs text-gray-400">+{{ entry.tags.length - 3 }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-400">🕐 {{ entry.updatedAt || entry.createdAt }}</span>
            <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-all" @click.stop>
              <button @click="editEntry(entry)" class="text-gray-400 hover:text-blue-500 text-xs" title="编辑">✏️</button>
              <button @click="deleteEntry(entry.id)" class="text-gray-400 hover:text-red-500 text-xs" title="删除">🗑️</button>
            </div>
          </div>
        </div>
        <!-- 空状态 -->
        <div v-if="filteredEntries.length === 0" class="col-span-full text-center py-10 text-gray-400">
          <div class="text-4xl mb-3">📭</div>
          <p>暂无匹配的知识条目</p>
          <button @click="openNewEntry" class="mt-3 text-blue-500 hover:underline text-sm">+ 创建第一条知识</button>
        </div>
      </div>
    </div>

    <!-- ===== Tab 2: 书架 ===== -->
    <div v-if="activeTab === 'reading'">
      <!-- 三列：想读 / 在读 / 已读 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- 想读 -->
        <div class="bg-yellow-50 rounded-lg p-3 sm:p-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📌</span> 想读
            <span class="text-sm text-gray-400 ml-auto">{{ readingByStatus('want_to_read').length }}</span>
          </h3>
          <div class="space-y-3">
            <div v-for="item in readingByStatus('want_to_read')" :key="item.id" class="bg-white rounded-lg shadow p-3 group">
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-gray-800 text-sm leading-snug pr-2">{{ item.title }}</h4>
                <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                  <button @click="editReading(item)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
                  <button @click="deleteReading(item.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
                </div>
              </div>
              <p class="text-xs text-gray-500">{{ item.author }}</p>
            </div>
            <div v-if="readingByStatus('want_to_read').length === 0" class="text-center py-4 text-gray-400 text-xs">暂无</div>
          </div>
        </div>

        <!-- 在读 -->
        <div class="bg-blue-50 rounded-lg p-3 sm:p-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📖</span> 在读
            <span class="text-sm text-gray-400 ml-auto">{{ readingByStatus('reading').length }}</span>
          </h3>
          <div class="space-y-3">
            <div v-for="item in readingByStatus('reading')" :key="item.id" class="bg-white rounded-lg shadow p-3 group">
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-gray-800 text-sm leading-snug pr-2">{{ item.title }}</h4>
                <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                  <button @click="editReading(item)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
                  <button @click="deleteReading(item.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
                </div>
              </div>
              <p class="text-xs text-gray-500 mb-2">{{ item.author }}</p>
              <!-- 进度条 -->
              <div class="flex items-center gap-2 mb-1">
                <div class="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div class="bg-blue-500 h-1.5 rounded-full transition-all" :style="{ width: item.progress + '%' }"></div>
                </div>
                <span class="text-xs text-gray-500">{{ item.progress }}%</span>
              </div>
              <div v-if="item.startDate" class="text-xs text-gray-400">📅 {{ item.startDate }}</div>
            </div>
            <div v-if="readingByStatus('reading').length === 0" class="text-center py-4 text-gray-400 text-xs">暂无</div>
          </div>
        </div>

        <!-- 已读 -->
        <div class="bg-green-50 rounded-lg p-3 sm:p-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>✅</span> 已读
            <span class="text-sm text-gray-400 ml-auto">{{ readingByStatus('completed').length }}</span>
          </h3>
          <div class="space-y-3">
            <div v-for="item in readingByStatus('completed')" :key="item.id" class="bg-white rounded-lg shadow p-3 group opacity-80">
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-gray-800 text-sm leading-snug pr-2">{{ item.title }}</h4>
                <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0">
                  <button @click="editReading(item)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
                  <button @click="deleteReading(item.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
                </div>
              </div>
              <p class="text-xs text-gray-500 mb-1">{{ item.author }}</p>
              <div class="flex items-center gap-1 text-xs">
                <span v-if="item.rating > 0" class="text-yellow-500">{{ '⭐'.repeat(item.rating) }}</span>
                <span v-if="item.completedDate" class="text-gray-400 ml-auto">{{ item.completedDate }}</span>
              </div>
            </div>
            <div v-if="readingByStatus('completed').length === 0" class="text-center py-4 text-gray-400 text-xs">暂无</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== Tab 3: 日志 ===== -->
    <div v-if="activeTab === 'log'">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="space-y-3">
          <div v-for="(item, idx) in log" :key="idx" class="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0 last:pb-0">
            <span
              class="text-xs px-1.5 py-0.5 rounded flex-shrink-0 text-white"
              :class="{
                'bg-green-500': item.action === 'create',
                'bg-blue-500': item.action === 'update',
                'bg-purple-500': item.action === 'ingest',
                'bg-orange-500': item.action === 'query',
              }"
            >
              {{ actionLabel(item.action) }}
            </span>
            <div class="flex-1 min-w-0">
              <div class="text-sm text-gray-700">{{ item.description }}</div>
              <div class="text-xs text-gray-400 mt-0.5">{{ item.date }}</div>
            </div>
            <button
              v-if="item.entryId"
              @click="viewEntryById(item.entryId)"
              class="text-xs text-blue-500 hover:underline flex-shrink-0"
            >查看</button>
          </div>
        </div>
        <div v-if="log.length === 0" class="text-center py-8 text-gray-400 text-sm">暂无日志记录</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// ===== 数据 =====
const entries = ref([])
const readingList = ref([])
const log = ref([])

// ===== Tab =====
const tabs = [
  { key: 'wiki', label: '知识库', icon: '📝' },
  { key: 'reading', label: '书架', icon: '📚' },
  { key: 'log', label: '日志', icon: '📋' },
]
const activeTab = ref('wiki')

// ===== 筛选状态 =====
const filterCategory = ref('all')
const filterStatus = ref('all')
const searchText = ref('')

// ===== 弹窗状态 =====
const showEntryModal = ref(false)
const editingEntry = ref({})
const showReadingModal = ref(false)
const editingReading = ref({})
const isEditing = ref(false)
const detailEntry = ref(null)
const tagsStr = ref('')

// ===== 初始化 =====
onMounted(async () => {
  // 尝试从 JSON 文件加载
  try {
    const res = await fetch('/life-os/data/knowledge.json')
    if (res.ok) {
      const data = await res.json()
      entries.value = data.entries || []
      readingList.value = data.readingList || []
      log.value = data.log || []
      return
    }
  } catch (e) { console.warn('knowledge.json 加载失败，尝试 localStorage', e) }

  // fallback: localStorage
  const saved = localStorage.getItem('life-os-knowledge')
  if (saved) {
    const data = JSON.parse(saved)
    entries.value = data.entries || []
    readingList.value = data.readingList || []
    log.value = data.log || []
  }
})

// ===== 持久化 =====
function saveToStorage() {
  localStorage.setItem('life-os-knowledge', JSON.stringify({
    entries: entries.value,
    readingList: readingList.value,
    log: log.value,
  }))
}

// ===== 计算属性 =====
const readCount = computed(() => readingList.value.filter(r => r.status === 'completed').length)
const categories = computed(() => {
  const cats = [...new Set(entries.value.map(e => e.category))]
  return cats.map(c => ({ value: c, icon: categoryEmoji(c), label: categoryLabel(c) }))
})

// ===== 知识库筛选 =====
const filteredEntries = computed(() => {
  return entries.value.filter(e => {
    if (filterCategory.value !== 'all' && e.category !== filterCategory.value) return false
    if (filterStatus.value !== 'all' && e.status !== filterStatus.value) return false
    if (searchText.value) {
      const s = searchText.value.toLowerCase()
      if (!e.title.toLowerCase().includes(s) &&
          !e.tags.some(t => t.toLowerCase().includes(s)) &&
          !e.content.toLowerCase().includes(s)) return false
    }
    return true
  })
})

// ===== 书架筛选 =====
function readingByStatus(status) {
  return readingList.value.filter(r => r.status === status)
}

// ===== 分类标签 =====
const catMap = {
  programming: '💻 编程',
  gis: '🗺️ GIS',
  teaching: '📖 教学',
  content: '📝 创作',
  reading: '📚 读书',
  life: '🎁 生活',
}
const catColorMap = {
  programming: 'bg-blue-500',
  gis: 'bg-green-600',
  teaching: 'bg-orange-500',
  content: 'bg-purple-500',
  reading: 'bg-yellow-600',
  life: 'bg-pink-500',
}

function categoryLabel(c) { return catMap[c] || c }
function categoryEmoji(c) { return catMap[c]?.split(' ')[0] || '📄' }
function categoryLabelShort(c) { return catMap[c]?.replace(/^./, '').trim() || c }
function categoryColor(c) { return catColorMap[c] || 'bg-gray-500' }

const sourceTypeMap = { article: '📄 文章', book: '📚 书籍', course: '🎓 课程', note: '📝 笔记' }
function sourceTypeLabel(t) { return sourceTypeMap[t] || t }

const actionMap = { create: '创建', update: '更新', ingest: '收录', query: '查询' }
function actionLabel(a) { return actionMap[a] || a }

// ===== Markdown 简单渲染 =====
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/###\s+(.+)/g, '<h4 class="text-md font-semibold text-gray-800 mt-4 mb-2">$1</h4>')
    .replace(/##\s+(.+)/g, '<h3 class="text-lg font-semibold text-gray-800 mt-5 mb-2 border-b pb-1">$1</h3>')
    .replace(/#\s+(.+)/g, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="bg-gray-100 rounded-lg p-3 my-3 overflow-x-auto text-xs"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-xs">$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)/gm, '<li class="ml-4 text-sm text-gray-700">$1</li>')
    .replace(/\n/g, '<br/>')
  return html
}

function stripMarkdown(text) {
  return text.replace(/[#*`>\-\[\]\(\)!_|~\n]/g, ' ').replace(/\s+/g, ' ').trim()
}

// ===== 条目 CRUD =====
function openNewEntry() {
  editingEntry.value = {
    id: null, title: '', category: 'programming', tags: [],
    content: '', source: { type: 'article', title: '', url: '' },
    relatedEntries: [], status: 'published',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0],
  }
  tagsStr.value = ''
  showEntryModal.value = true
}

function editEntry(entry) {
  editingEntry.value = { ...entry, source: { ...entry.source }, tags: [...entry.tags], relatedEntries: [...entry.relatedEntries] }
  tagsStr.value = entry.tags.join(', ')
  isEditing.value = true
  showEntryModal.value = true
}

function saveEntry() {
  if (!editingEntry.value.title.trim()) { alert('请输入标题'); return }
  editingEntry.value.tags = tagsStr.value.split(',').map(t => t.trim()).filter(Boolean)
  editingEntry.value.updatedAt = new Date().toISOString().split('T')[0]

  if (isEditing.value) {
    const idx = entries.value.findIndex(e => e.id === editingEntry.value.id)
    if (idx !== -1) entries.value[idx] = { ...editingEntry.value }
    addLog('update', '更新了「' + editingEntry.value.title + '」', editingEntry.value.id)
  } else {
    const maxN = Math.max(...entries.value.map(e => parseInt(e.id.slice(1))), 0)
    const newEntry = { ...editingEntry.value, id: 'K' + String(maxN + 1).padStart(3, '0') }
    entries.value.push(newEntry)
    addLog('create', '新建了「' + newEntry.title + '」', newEntry.id)
  }

  showEntryModal.value = false
  saveToStorage()
}

function deleteEntry(id) {
  if (!confirm('确定删除该知识条目吗？')) return
  const entry = entries.value.find(e => e.id === id)
  entries.value = entries.value.filter(e => e.id !== id)
  addLog('delete', '删除了「' + entry?.title + '」', id)
  saveToStorage()
}

function viewEntry(entry) { detailEntry.value = entry }
function viewEntryById(id) {
  const entry = entries.value.find(e => e.id === id)
  if (entry) detailEntry.value = entry
}

function viewRelatedEntry(id) {
  const entry = entries.value.find(e => e.id === id)
  if (entry) detailEntry.value = entry
}

function getEntryTitle(id) {
  const entry = entries.value.find(e => e.id === id)
  return entry ? entry.title : id
}

// ===== 阅读 CRUD =====
function openNewReading() {
  editingReading.value = { id: null, title: '', author: '', type: 'book', status: 'want_to_read', progress: 0, rating: 0, notes: '', startDate: null, completedDate: null }
  isEditing.value = false
  showReadingModal.value = true
}

function editReading(item) {
  editingReading.value = { ...item }
  isEditing.value = true
  showReadingModal.value = true
}

function saveReading() {
  if (!editingReading.value.title.trim()) { alert('请输入书名'); return }

  const now = new Date().toISOString().split('T')[0]
  const item = { ...editingReading.value }

  if (item.status === 'completed' && !item.completedDate) item.completedDate = now
  if (item.status !== 'completed') item.completedDate = null
  if (item.status === 'reading' && !item.startDate) item.startDate = now

  if (isEditing.value) {
    const idx = readingList.value.findIndex(r => r.id === item.id)
    if (idx !== -1) readingList.value[idx] = item
  } else {
    const maxN = Math.max(...readingList.value.map(r => parseInt(r.id.slice(1))), 0)
    readingList.value.push({ ...item, id: 'R' + String(maxN + 1).padStart(3, '0') })
  }

  showReadingModal.value = false
  saveToStorage()
}

function deleteReading(id) {
  if (!confirm('确定删除吗？')) return
  readingList.value = readingList.value.filter(r => r.id !== id)
  saveToStorage()
}

// ===== 日志 =====
function addLog(action, description, entryId) {
  const today = new Date().toISOString().split('T')[0]
  log.value.unshift({ date: today, action, description, entryId })
  // keep last 50 entries
  if (log.value.length > 50) log.value = log.value.slice(0, 50)
}
</script>
