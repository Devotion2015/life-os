<template>
  <!-- 同步状态栏：无更新时精简，有更新时醒目 -->
  <div class="bg-white rounded-lg shadow p-3 mb-6 border transition-colors"
    :class="hasUpdate ? 'border-blue-300 bg-blue-50/30' : 'border-gray-200'">
    <div class="flex items-center gap-3 flex-wrap">
      <!-- 状态图标 -->
      <div class="flex items-center gap-2" :title="hasUpdate ? '有新数据可用！' : '数据已是最新'">
        <span v-if="hasUpdate" class="animate-pulse text-lg">🔔</span>
        <span v-else class="text-lg">🟢</span>
        <span class="text-sm font-medium" :class="hasUpdate ? 'text-blue-700' : 'text-gray-600'">
          {{ hasUpdate ? '有新数据可用' : '数据已同步' }}
        </span>
      </div>

      <!-- 来源 -->
      <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full flex-shrink-0">
        {{ status.source || '—' }}
      </span>

      <!-- 时间 -->
      <span class="text-xs text-gray-400">
        {{ status.lastSync ? '上次 ' + fmtTime(status.lastSync) : '尚未同步' }}
      </span>

      <!-- 版本号 -->
      <span class="text-[10px] text-gray-300 font-mono">v{{ status.dataVersion || 0 }}</span>

      <!-- 操作按钮 -->
      <div class="ml-auto flex items-center gap-2">
        <button
          v-if="hasUpdate"
          @click="$emit('refresh')"
          class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg transition-colors font-medium"
        >
          🔄 刷新数据
        </button>
        <button
          @click="triggerSync"
          class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1"
          :disabled="syncing"
          title="触发云端双向同步"
        >
          <span v-if="syncing" class="inline-block animate-spin">⏳</span>
          <span v-else>🔄</span>
          {{ syncing ? '同步中…' : '立即同步' }}
        </button>
        <a
          href="https://www.notion.so/Life-OS-3574fad8114a80489668d29ddc8a3eb4"
          target="_blank"
          rel="noopener"
          class="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          title="在 Notion 中打开 Life OS"
        >
          📝 Notion →
        </a>
      </div>
    </div>

    <!-- 新数据详情（展开时） -->
    <div v-if="hasUpdate && status.updated" class="mt-2 pt-2 border-t border-blue-100">
      <div class="flex flex-wrap gap-1.5">
        <span v-for="cat in status.updated" :key="cat"
          class="text-[11px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
          {{ cat }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  /** localStorage 记录的版本号 */
  localVersion: { type: Number, default: 0 }
})

defineEmits(['refresh'])

const status = ref({ lastSync: null, dataVersion: 0, source: '—' })
const syncing = ref(false)

const GITHUB_ACTIONS_URL = 'https://github.com/Devotion2015/life-os/actions/workflows/sync-notion.yml'

// 版本号大于本地 = 有新数据
const hasUpdate = computed(() =>
  status.value.dataVersion > props.localVersion
)

onMounted(async () => {
  try {
    const r = await fetch('/life-os/data/sync-status.json')
    if (r.ok) status.value = await r.json()
  } catch (e) {
    // sync-status 不存在则保持默认
  }
})

function triggerSync() {
  syncing.value = true
  // 打开 GitHub Actions 手动触发页面
  window.open(GITHUB_ACTIONS_URL, '_blank', 'noopener')
  // 3秒后恢复按钮状态
  setTimeout(() => { syncing.value = false }, 3000)
}

function fmtTime(iso) {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    const now = new Date()
    const diffMs = now - d
    const diffMin = Math.floor(diffMs / 60000)
    if (diffMin < 1) return '刚刚'
    if (diffMin < 60) return `${diffMin} 分钟前`
    if (diffMin < 1440) return `${Math.floor(diffMin / 60)} 小时前`
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch {
    return iso.slice(0, 16)
  }
}
</script>
