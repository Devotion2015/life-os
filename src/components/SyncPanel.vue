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

      <!-- 当前阶段提示 -->
      <span v-if="syncing && syncPhase" class="text-[11px] text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-full">
        {{ syncPhase }}
      </span>

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
          :title="hasToken ? '先保存本地数据到 GitHub，再触发 Notion 同步' : '请先点击 ⚙️ 配置 Token'"
        >
          <span v-if="syncing" class="inline-block animate-spin">⏳</span>
          <span v-else>🔄</span>
          {{ syncing ? syncPhase || '同步中…' : (hasToken ? '立即同步' : '先配置') }}
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
        权限需要两项：<br>
        <b>Repository access: Devotion2015/life-os</b><br>
        <b>Permissions: Actions → Read and Write</b> + <b>Contents → Read and Write</b>
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
const syncPhase = ref(null)         // 'saving' | 'triggering' | 'polling' | null
const syncMode = ref('sync')        // 'sync' | 'push' | 'pull'
const showSettings = ref(false)
const tokenInput = ref('')

const TOKEN_KEY = 'gh_sync_token'
const POLL_INTERVAL = 5000          // 5s 轮询
const MAX_POLLS = 12                // 最多等 60s（保存 GitHub 也需要时间）

// ── localStorage ↔ JSON 文件映射 ──
const FILE_MAP = {
  'life-os-projects': 'public/data/projects.json',
  'life-os-okrs': 'public/data/okr.json',
  'life-os-todos': 'public/data/todos.json',
  'life-os-events': 'public/data/events.json',
  'life-os-finance': 'public/data/finance.json',
  'life-os-knowledge': 'public/data/knowledge.json',
  'life-os-entertainment': 'public/data/life.json',
}

// ── 计算属性 ──
const hasToken = computed(() => !!localStorage.getItem(TOKEN_KEY))

const hasUpdate = computed(() =>
  status.value.dataVersion > props.localVersion
)

const statusTitle = computed(() => {
  if (syncing.value) return '正在同步…'
  if (syncResult.value === 'ok') return '同步完成'
  if (syncResult.value === 'err') return '同步失败'
  if (hasUpdate.value) return '有新数据可用！点击刷新按钮加载'
  return '数据已是最新'
})

const statusText = computed(() => {
  if (syncing.value) return '同步中…'
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

// ── UTF-8 字符串 → Base64（浏览器标准做法）──
function utf8ToBase64(str) {
  const bytes = new TextEncoder().encode(str)
  let bin = ''
  bytes.forEach(b => bin += String.fromCharCode(b))
  return btoa(bin)
}

// ── 保存 localStorage 到 GitHub JSON 文件 ──
async function saveLocalToGitHub(token) {
  const saveResults = { saved: [], skipped: [], errors: [] }
  const API_BASE = 'https://api.github.com/repos/Devotion2015/life-os/contents'
  const HEADERS = {
    'Authorization': `Bearer ${token}`,
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/json',
  }

  for (const [lsKey, filePath] of Object.entries(FILE_MAP)) {
    const raw = localStorage.getItem(lsKey)
    if (!raw) {
      saveResults.skipped.push(lsKey)
      continue
    }

    try {
      // 获取当前文件 SHA
      const getResp = await fetch(`${API_BASE}/${filePath}`, { headers: HEADERS })
      if (!getResp.ok) {
        saveResults.errors.push({ key: lsKey, status: getResp.status, msg: `获取 ${filePath} 失败` })
        continue
      }
      const fileInfo = await getResp.json()

      // 格式化 JSON（美化输出）
      const parsed = JSON.parse(raw)
      const pretty = JSON.stringify(parsed, null, 2)
      const base64 = utf8ToBase64(pretty)

      // 提交更新
      const putResp = await fetch(`${API_BASE}/${filePath}`, {
        method: 'PUT',
        headers: HEADERS,
        body: JSON.stringify({
          message: `sync: save ${lsKey} from Life OS web`,
          content: base64,
          sha: fileInfo.sha,
          branch: 'main',
        })
      })

      if (putResp.ok) {
        saveResults.saved.push(lsKey)
      } else {
        const err = await putResp.json().catch(() => ({}))
        saveResults.errors.push({ key: lsKey, status: putResp.status, msg: err.message || String(putResp.status) })
      }
    } catch (e) {
      saveResults.errors.push({ key: lsKey, status: 0, msg: e.message })
    }
  }

  return saveResults
}

// ── 一键同步（先存后同步）──
async function triggerSync() {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) {
    showSettings.value = true
    return
  }

  syncing.value = true
  syncResult.value = null

  try {
    // ═══ 第一步：保存 localStorage 到 GitHub JSON 文件 ═══
    syncPhase.value = '正在保存本地数据…'
    const saveResults = await saveLocalToGitHub(token)

    if (saveResults.errors.length > 0 && saveResults.saved.length === 0) {
      // 全都失败了
      throw new Error(`保存失败: ${saveResults.errors.map(e => e.key).join(', ')}`)
    }

    // 等待 GitHub 处理完 commit（避免 race condition）
    await new Promise(r => setTimeout(r, 2000))

    // ═══ 第二步：触发 sync-notion.yml workflow ═══
    syncPhase.value = '正在触发同步…'
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
      if (triggerResp.status === 401) throw new Error('Token 无效，请重新设置')
      if (triggerResp.status === 404) throw new Error('Workflow 文件未找到（sync-notion.yml）')
      throw new Error(`API 错误 ${triggerResp.status}`)
    }

    // ═══ 第三步：轮询等待同步完成 ═══
    syncPhase.value = '等待同步完成…'
    const prevVersion = status.value.dataVersion
    let attempts = 0

    await new Promise((resolve) => {
      const timer = setInterval(async () => {
        attempts++
        await loadStatus()

        if (status.value.dataVersion !== prevVersion) {
          clearInterval(timer)
          resolve()
          return
        }

        if (attempts >= MAX_POLLS) {
          clearInterval(timer)
          resolve() // 超时也算已触发
        }
      }, POLL_INTERVAL)
    })

    syncResult.value = 'ok'
    syncPhase.value = null
    syncing.value = false

    setTimeout(() => { syncResult.value = null }, 8000)

  } catch (e) {
    syncResult.value = 'err'
    syncPhase.value = null
    syncing.value = false
    console.error('Sync failed:', e.message)
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
