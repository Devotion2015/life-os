<template>
  <!-- 同步状态栏 -->
  <div class="bg-white rounded-lg shadow p-3 mb-6 border transition-colors"
    :class="hasUpdate ? 'border-blue-300 bg-blue-50/30' : 'border-gray-200'">
    <div class="flex items-center gap-3 flex-wrap">
      <!-- 状态图标 -->
      <div class="flex items-center gap-2" :title="statusTitle">
        <span v-if="syncing" class="animate-spin inline-block text-lg">⏳</span>
        <span v-else-if="syncResult === 'ok'" class="text-lg">✅</span>
        <span v-else-if="syncResult === 'err'" class="text-lg">❌</span>
        <span v-else-if="hasUpdate" class="animate-pulse text-lg">🔔</span>
        <span v-else class="text-lg">🟢</span>
        <span class="text-sm font-medium"
          :class="hasUpdate ? 'text-blue-700' : 'text-gray-600'">
          {{ statusText }}
        </span>
      </div>

      <!-- 来源标签 -->
      <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full flex-shrink-0">
        {{ status.source || '—' }}
      </span>

      <!-- 上次同步时间 -->
      <span class="text-xs text-gray-400">
        {{ status.lastSync ? '上次 ' + fmtTime(status.lastSync) : '尚未同步' }}
      </span>

      <!-- 版本号 -->
      <span class="text-[10px] text-gray-300 font-mono">v{{ status.dataVersion || 0 }}</span>

      <!-- 操作按钮组 -->
      <div class="ml-auto flex items-center gap-2">
        <!-- 有更新时：刷新按钮 -->
        <button
          v-if="hasUpdate"
          @click="$emit('refresh')"
          class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg transition-colors font-medium"
        >
          🔄 刷新数据
        </button>

        <!-- 同步方向选择 -->
        <select v-model="syncMode"
          class="text-[10px] border border-gray-200 rounded px-1.5 py-1 bg-white text-gray-500 cursor-pointer"
          :disabled="syncing">
          <option value="sync">⇅ 双向</option>
          <option value="push">↑ 推送</option>
          <option value="pull">↓ 拉取</option>
        </select>

        <!-- 一键同步按钮 -->
        <button
          @click="triggerSync"
          class="text-xs px-3 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1"
          :class="syncing
            ? 'bg-gray-100 text-gray-400 cursor-wait'
            : hasToken
              ? 'bg-indigo-500 hover:bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
          :disabled="syncing || !hasToken"
          :title="hasToken ? '点击立即触发同步' : '请先点击 ⚙️ 配置 Token'"
        >
          <span v-if="syncing" class="inline-block animate-spin">⏳</span>
          <span v-else>🔄</span>
          {{ syncing ? '同步中…' : (hasToken ? '立即同步' : '先配置') }}
        </button>

        <!-- 设置齿轮 -->
        <button @click="showSettings = !showSettings"
          class="text-xs text-gray-300 hover:text-gray-500 transition-colors relative"
          :class="{ 'text-indigo-400': showSettings }"
          title="设置 GitHub Token">
          ⚙️
        </button>

        <!-- Notion 入口 -->
        <a
          href="https://www.notion.so/Life-OS-3574fad8114a80489668d29ddc8a3eb4"
          target="_blank" rel="noopener"
          class="text-xs text-gray-400 hover:text-gray-600 transition-colors ml-1"
          title="在 Notion 中打开 Life OS"
        >📝 Notion →</a>
      </div>
    </div>

    <!-- Token 设置面板（展开时） -->
    <div v-if="showSettings" class="mt-2 pt-2 border-t border-gray-100">
      <div class="flex items-center gap-2">
        <input
          v-model="tokenInput"
          type="password"
          placeholder="粘贴 GitHub Fine-grained PAT…"
          class="flex-1 text-xs border border-gray-200 rounded px-2 py-1.5 focus:outline-none focus:border-indigo-300"
          @keyup.enter="saveToken"
        />
        <button
          @click="saveToken"
          class="text-xs bg-green-500 hover:bg-green-600 text-white px-3 py-1.5 rounded transition-colors font-medium"
        >保存</button>
        <button
          v-if="hasToken"
          @click="clearToken"
          class="text-xs text-red-400 hover:text-red-600 px-2 py-1 transition-colors"
        >清除</button>
      </div>
      <p class="text-[10px] text-gray-400 mt-1.5 leading-relaxed">
        💡 创建 GitHub Fine-grained PAT →
        <a href="https://github.com/settings/tokens?type=beta" target="_blank"
           class="text-indigo-400 hover:underline">Settings → Developer settings → Fine-grained tokens</a><br>
        权限仅需：<b>Repository access: Devotion2015/life-os</b> + <b>Permissions: Actions → Read and Write</b>
      </p>
    </div>

    <!-- 同步触发成功提示 -->
    <div v-if="syncResult === 'ok' && status.updated" class="mt-2 pt-2 border-t border-green-100">
      <div class="flex flex-wrap gap-1.5">
        <span v-for="cat in status.updated" :key="cat"
          class="text-[11px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
          {{ cat }}
        </span>
      </div>
    </div>

    <!-- 有新数据（Notion 侧拉回） -->
    <div v-else-if="hasUpdate && status.updated" class="mt-2 pt-2 border-t border-blue-100">
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

// ── 状态 ──
const status = ref({ lastSync: null, dataVersion: 0, source: '—', updated: [] })
const syncing = ref(false)
const syncResult = ref(null)        // 'ok' | 'err' | null
const syncMode = ref('sync')        // 'sync' | 'push' | 'pull'
const showSettings = ref(false)
const tokenInput = ref('')

const TOKEN_KEY = 'gh_sync_token'
const POLL_INTERVAL = 5000          // 5s 轮询
const MAX_POLLS = 8                 // 最多等 40s

// ── 计算属性 ──
const hasToken = computed(() => !!localStorage.getItem(TOKEN_KEY))

const hasUpdate = computed(() =>
  status.value.dataVersion > props.localVersion
)

const statusTitle = computed(() => {
  if (syncing.value) return '正在触发同步…'
  if (syncResult.value === 'ok') return '同步已触发，等待完成…'
  if (syncResult.value === 'err') return '同步触发失败'
  if (hasUpdate.value) return '有新数据可用！点击刷新按钮加载'
  return '数据已是最新'
})

const statusText = computed(() => {
  if (syncing.value) return '触发同步…'
  const r = syncResult.value
  if (r === 'ok') return '同步完成 ✅'
  if (r === 'err') return '同步失败，点击重试'
  if (hasUpdate.value) return '有新数据可用'
  return '数据已同步'
})

// ── 生命周期 ──
onMounted(loadStatus)

async function loadStatus() {
  try {
    const r = await fetch('/life-os/data/sync-status.json')
    if (r.ok) status.value = await r.json()
  } catch (_) { /* sync-status 不存在则保持默认 */ }
}

// ── Token 管理 ──
function saveToken() {
  const t = tokenInput.value.trim()
  if (!t) return
  localStorage.setItem(TOKEN_KEY, t)
  tokenInput.value = ''
  showSettings.value = false
  syncResult.value = null
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  tokenInput.value = ''
  syncResult.value = null
}

// ── 一键同步 ──
async function triggerSync() {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) {
    showSettings.value = true
    return
  }

  syncing.value = true
  syncResult.value = null

  try {
    // ① 触发 GitHub Actions workflow_dispatch
    const triggerResp = await fetch(
      'https://api.github.com/repos/Devotion2015/life-os/actions/workflows/sync-notion.yml/dispatches',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.github+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: { mode: syncMode.value }
        })
      }
    )

    if (!triggerResp.ok) {
      const errBody = await triggerResp.text().catch(() => '')
      if (triggerResp.status === 401) {
        throw new Error('Token 无效，请重新设置')
      }
      if (triggerResp.status === 404) {
        throw new Error('Workflow 文件未找到（sync-notion.yml）')
      }
      throw new Error(`API ${triggerResp.status}: ${errBody.slice(0, 80)}`)
    }

    // ② 轮询等待同步完成
    let prevVersion = status.value.dataVersion
    let attempts = 0

    const poll = () => new Promise((resolve) => {
      const timer = setInterval(async () => {
        attempts++
        await loadStatus()

        // 版本号变了 = 同步完成了
        if (status.value.dataVersion !== prevVersion) {
          clearInterval(timer)
          syncResult.value = 'ok'
          // 发事件通知父组件刷新
          if (status.value.dataVersion > props.localVersion) {
            // 让父组件感知；父组件通过 refresh 事件处理
          }
          syncing.value = false
          resolve()
          return
        }

        if (attempts >= MAX_POLLS) {
          clearInterval(timer)
          // 超时也算成功（workflow 可能还在跑，但已经触发了）
          syncResult.value = 'ok'
          syncing.value = false
          resolve()
        }
      }, POLL_INTERVAL)
    })

    await poll()

    // 3s 后清除 ok 状态，回到正常
    setTimeout(() => { syncResult.value = null }, 5000)

  } catch (e) {
    syncResult.value = 'err'
    syncing.value = false
    console.error('Sync trigger failed:', e.message)
  }
}

// ── 时间格式化 ──
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
