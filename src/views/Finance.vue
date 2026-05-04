<template>
  <div>
    <!-- ===== 交易编辑弹窗 ===== -->
    <div v-if="showTxModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[8vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingTx.id ? '编辑记录' : '新增记录' }}</h3>
        <div class="space-y-4">
          <div class="flex gap-2">
            <button
              @click="editingTx.type = 'expense'"
              class="flex-1 py-2 rounded-lg text-sm font-medium transition-all"
              :class="editingTx.type === 'expense' ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-500'"
            >🔴 支出</button>
            <button
              @click="editingTx.type = 'income'"
              class="flex-1 py-2 rounded-lg text-sm font-medium transition-all"
              :class="editingTx.type === 'income' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-500'"
            >🟢 收入</button>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">金额 <span class="text-red-500">*</span></label>
              <input v-model.number="editingTx.amount" type="number" step="0.01" min="0" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="0.00" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">日期</label>
              <input v-model="editingTx.date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
              <select v-model="editingTx.category" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option v-for="(c, k) in cats" :key="k" :value="k">{{ c.icon }} {{ c.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">月份</label>
              <input v-model="editingTx.month" type="month" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <input v-model="editingTx.description" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="描述..." />
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showTxModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveTx" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 预算编辑弹窗 ===== -->
    <div v-if="showBudgetModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 p-4 pt-[12vh]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-sm p-4 sm:p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingBudget.id ? '编辑预算' : '新增预算' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
            <select v-model="editingBudget.category" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option v-for="(c, k) in expenseCats" :key="k" :value="k">{{ c.icon }} {{ c.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">月度预算 <span class="text-red-500">*</span></label>
            <input v-model.number="editingBudget.monthly" type="number" min="0" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="如 1500" />
          </div>
        </div>
        <div class="flex gap-3 mt-6 justify-end border-t pt-4">
          <button @click="showBudgetModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="saveBudget" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">保存</button>
        </div>
      </div>
    </div>

    <!-- ===== 主内容 ===== -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
      <h2 class="text-xl sm:text-2xl font-bold text-gray-800">💰 财务管理</h2>
      <div class="flex gap-2">
        <button @click="openNewTx('expense')" class="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 text-sm whitespace-nowrap">- 记支出</button>
        <button @click="openNewTx('income')" class="px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm whitespace-nowrap">+ 记收入</button>
      </div>
    </div>

    <!-- 月度概览卡片 -->
    <div class="bg-white rounded-lg shadow p-4 sm:p-5 mb-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <h3 class="font-semibold text-gray-700">{{ viewMonth }} 月度概览</h3>
          <button @click="changeMonth(-1)" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&lt;</button>
          <button @click="changeMonth(1)" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&gt;</button>
          <button @click="viewMonth = currentMonth" class="text-xs text-blue-500 hover:underline">本月</button>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="text-center p-3 bg-green-50 rounded-lg">
          <div class="text-lg sm:text-xl font-bold text-green-600">¥{{ fmt(monthIncome) }}</div>
          <div class="text-xs text-gray-500">本月收入</div>
        </div>
        <div class="text-center p-3 bg-red-50 rounded-lg">
          <div class="text-lg sm:text-xl font-bold text-red-600">¥{{ fmt(monthExpense) }}</div>
          <div class="text-xs text-gray-500">本月支出</div>
        </div>
        <div class="text-center p-3 rounded-lg" :class="monthBalance >= 0 ? 'bg-blue-50' : 'bg-orange-50'">
          <div class="text-lg sm:text-xl font-bold" :class="monthBalance >= 0 ? 'text-blue-600' : 'text-orange-600'">¥{{ fmt(Math.abs(monthBalance)) }}</div>
          <div class="text-xs text-gray-500">{{ monthBalance >= 0 ? '本月结余' : '本月超支' }}</div>
        </div>
        <div class="text-center p-3 rounded-lg" :class="budgetUsagePct >= 100 ? 'bg-red-50' : budgetUsagePct >= 80 ? 'bg-yellow-50' : 'bg-gray-50'">
          <div class="text-lg sm:text-xl font-bold" :class="budgetUsagePct >= 100 ? 'text-red-600' : budgetUsagePct >= 80 ? 'text-yellow-600' : 'text-gray-600'">{{ budgetUsagePct }}%</div>
          <div class="text-xs text-gray-500">预算使用率</div>
        </div>
      </div>
    </div>

    <!-- 分类支出分布条 -->
    <div class="bg-white rounded-lg shadow p-3 sm:p-4 mb-6">
      <div class="text-sm font-medium text-gray-600 mb-3">📊 {{ viewMonth }} 支出分布</div>
      <div v-if="catBreakdown.length > 0">
        <div class="flex h-6 rounded-full overflow-hidden mb-2">
          <div
            v-for="cb in catBreakdown" :key="cb.key"
            :style="{ width: (cb.amount / monthExpense * 100) + '%', minWidth: cb.amount > 0 ? '2px' : '0' }"
            class="h-full transition-all"
            :class="catBarColor(cb.key)"
            :title="cats[cb.key]?.label + ': ¥' + fmt(cb.amount)"
          ></div>
        </div>
        <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs">
          <div v-for="cb in catBreakdown.slice(0, 6)" :key="cb.key" class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full" :class="catDotColor(cb.key)"></span>
            <span class="text-gray-600">{{ cats[cb.key]?.label }}</span>
            <span class="text-gray-400">¥{{ fmt(cb.amount) }}</span>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-2 text-gray-400 text-xs">暂无支出记录</div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex border-b border-gray-200 mb-6 gap-1 overflow-x-auto">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors"
        :class="activeTab === tab.key ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
      >{{ tab.icon }} {{ tab.label }}</button>
    </div>

    <!-- ===== Tab 1: 收支记录 ===== -->
    <div v-if="activeTab === 'transactions'">
      <!-- 筛选 -->
      <div class="bg-white rounded-lg shadow p-3 mb-4">
        <div class="flex flex-wrap gap-2">
          <select v-model="txFilter" class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm">
            <option value="all">全部类型</option>
            <option value="expense">🔴 支出</option>
            <option value="income">🟢 收入</option>
          </select>
          <select v-model="txCatFilter" class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm">
            <option value="all">全部分类</option>
            <option v-for="(c, k) in cats" :key="k" :value="k">{{ c.icon }} {{ c.label }}</option>
          </select>
        </div>
      </div>

      <!-- 交易列表 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4">
        <div class="space-y-2">
          <div
            v-for="tx in filteredTxs" :key="tx.id"
            class="flex items-center gap-3 py-2.5 border-b border-gray-100 last:border-0 group"
          >
            <span class="text-lg flex-shrink-0">{{ cats[tx.category]?.icon || '💰' }}</span>
            <div class="flex-1 min-w-0">
              <div class="text-sm text-gray-700 truncate">{{ tx.description || cats[tx.category]?.label }}</div>
              <div class="text-xs text-gray-400">{{ tx.date }} · {{ cats[tx.category]?.label }}</div>
            </div>
            <span class="font-semibold text-sm whitespace-nowrap" :class="tx.type === 'expense' ? 'text-red-600' : 'text-green-600'">
              {{ tx.type === 'expense' ? '-' : '+' }}{{ fmt(tx.amount) }}
            </span>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all">
              <button @click="editTx(tx)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
              <button @click="deleteTx(tx.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
            </div>
          </div>
        </div>
        <div v-if="filteredTxs.length === 0" class="text-center py-8 text-gray-400 text-sm">暂无记录</div>
      </div>
    </div>

    <!-- ===== Tab 2: 预算管理 ===== -->
    <div v-if="activeTab === 'budgets'">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="b in budgets" :key="b.id" class="bg-white rounded-lg shadow p-4 group hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ cats[b.category]?.icon || '💰' }}</span>
              <div>
                <h4 class="font-medium text-gray-800 text-sm">{{ cats[b.category]?.label }}</h4>
                <p class="text-xs text-gray-500">预算 ¥{{ fmt(b.monthly) }}/月</p>
              </div>
            </div>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-all">
              <button @click="editBudget(b)" class="text-gray-400 hover:text-blue-500 text-xs">✏️</button>
              <button @click="deleteBudget(b.id)" class="text-gray-400 hover:text-red-500 text-xs">🗑️</button>
            </div>
          </div>

          <!-- 花费 vs 预算 -->
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">已花</span>
              <span class="font-medium" :class="budgetSpent(b) > b.monthly ? 'text-red-600' : 'text-gray-700'">¥{{ fmt(budgetSpent(b)) }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="budgetPercent(b) >= 100 ? 'bg-red-500' : budgetPercent(b) >= 80 ? 'bg-yellow-500' : 'bg-blue-500'"
                :style="{ width: Math.min(budgetPercent(b), 100) + '%' }"
              ></div>
            </div>
            <div class="flex justify-between text-xs">
              <span :class="budgetPercent(b) >= 100 ? 'text-red-500' : budgetPercent(b) >= 80 ? 'text-yellow-600' : 'text-gray-400'">{{ budgetPercent(b) }}%</span>
              <span :class="budgetRemain(b) < 0 ? 'text-red-500' : 'text-green-600'">
                {{ budgetRemain(b) < 0 ? '超' : '剩' }}{{ fmt(Math.abs(budgetRemain(b))) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 新增预算 -->
        <div @click="openNewBudget" class="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-4 flex items-center justify-center cursor-pointer hover:bg-gray-100 transition-colors min-h-[160px]">
          <div class="text-center text-gray-400">
            <div class="text-2xl mb-1">+</div>
            <div class="text-sm">添加预算分类</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// ===== Category definitions =====
const cats = {
  salary: { icon: '💼', label: '工资' },
  dining: { icon: '🍜', label: '餐饮' },
  transport: { icon: '🚗', label: '交通' },
  housing: { icon: '🏠', label: '住房' },
  entertainment: { icon: '🎬', label: '娱乐' },
  shopping: { icon: '🛒', label: '购物' },
  digital: { icon: '💻', label: '数码' },
  books: { icon: '📚', label: '书籍' },
  office: { icon: '🖨️', label: '办公' },
  medical: { icon: '💊', label: '医疗' },
  other: { icon: '📦', label: '其他' }
}

const expenseCats = computed(() => {
  const e = {}
  for (const [k, v] of Object.entries(cats)) {
    if (k !== 'salary') e[k] = v
  }
  return e
})

// ===== Data =====
const transactions = ref([])
const budgets = ref([])

// ===== Tab =====
const tabs = [
  { key: 'transactions', label: '收支记录', icon: '💰' },
  { key: 'budgets', label: '预算管理', icon: '📊' },
]
const activeTab = ref('transactions')

// ===== UI =====
const showTxModal = ref(false)
const editingTx = ref({})
const isEditingTx = ref(false)

const showBudgetModal = ref(false)
const editingBudget = ref({})
const isEditingBudget = ref(false)

const viewMonth = ref(new Date().toISOString().slice(0, 7))
const currentMonth = ref(new Date().toISOString().slice(0, 7))

const txFilter = ref('all')
const txCatFilter = ref('all')

// ===== Init =====
onMounted(async () => {
  try {
    const res = await fetch('/life-os/data/finance.json')
    if (res.ok) {
      const data = await res.json()
      transactions.value = data.transactions || []
      budgets.value = data.budgets || []
      return
    }
  } catch (e) {}
  const saved = localStorage.getItem('life-os-finance')
  if (saved) {
    const d = JSON.parse(saved)
    transactions.value = d.transactions || []
    budgets.value = d.budgets || []
  }
})

function save() {
  localStorage.setItem('life-os-finance', JSON.stringify({
    transactions: transactions.value,
    budgets: budgets.value
  }))
}

// ===== Helpers =====
function fmt(n) { return Number(n || 0).toFixed(2) }

function changeMonth(delta) {
  const [y, m] = viewMonth.value.split('-').map(Number)
  const d = new Date(y, m - 1 + delta, 1)
  viewMonth.value = d.toISOString().slice(0, 7)
}

// ===== Monthly stats =====
const monthTxs = computed(() => transactions.value.filter(t => t.month === viewMonth.value))

const monthIncome = computed(() =>
  monthTxs.value.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0)
)

const monthExpense = computed(() =>
  monthTxs.value.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0)
)

const monthBalance = computed(() => monthIncome.value - monthExpense.value)

const totalBudget = computed(() => budgets.value.reduce((s, b) => s + b.monthly, 0))
const budgetUsagePct = computed(() =>
  totalBudget.value > 0 ? Math.round(monthExpense.value / totalBudget.value * 100) : 0
)

// ===== Category breakdown =====
const catBreakdown = computed(() => {
  const map = {}
  monthTxs.value.filter(t => t.type === 'expense').forEach(t => {
    map[t.category] = (map[t.category] || 0) + t.amount
  })
  return Object.entries(map)
    .map(([key, amount]) => ({ key, amount }))
    .sort((a, b) => b.amount - a.amount)
})

const catBarColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-teal-500', 'bg-indigo-500', 'bg-gray-500']
const catDotColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-teal-500', 'bg-indigo-500', 'bg-gray-500']

function catBarColor(cat) {
  const idx = Object.keys(cats).indexOf(cat)
  return catBarColors[idx % catBarColors.length]
}

function catDotColor(cat) {
  const idx = Object.keys(cats).indexOf(cat)
  return catDotColors[idx % catDotColors.length]
}

// ===== Transactions =====
const filteredTxs = computed(() => {
  return monthTxs.value.filter(t => {
    if (txFilter.value !== 'all' && t.type !== txFilter.value) return false
    if (txCatFilter.value !== 'all' && t.category !== txCatFilter.value) return false
    return true
  }).sort((a, b) => b.date.localeCompare(a.date))
})

function openNewTx(type) {
  editingTx.value = {
    id: null, date: new Date().toISOString().split('T')[0], type,
    category: type === 'income' ? 'salary' : 'dining',
    amount: 0, description: '', month: currentMonth.value
  }
  isEditingTx.value = false
  showTxModal.value = true
}

function editTx(tx) {
  editingTx.value = { ...tx }
  isEditingTx.value = true
  showTxModal.value = true
}

function saveTx() {
  if (!editingTx.value.amount || editingTx.value.amount <= 0) { alert('请输入有效金额'); return }
  editingTx.value.month = editingTx.value.date.substring(0, 7)

  if (isEditingTx.value) {
    const idx = transactions.value.findIndex(t => t.id === editingTx.value.id)
    if (idx !== -1) transactions.value[idx] = { ...editingTx.value }
  } else {
    const maxN = Math.max(...transactions.value.map(t => parseInt(t.id.slice(2))), 0)
    transactions.value.push({ ...editingTx.value, id: 'TR' + String(maxN + 1).padStart(3, '0') })
  }
  showTxModal.value = false
  save()
}

function deleteTx(id) {
  if (!confirm('确定删除这条记录吗？')) return
  transactions.value = transactions.value.filter(t => t.id !== id)
  save()
}

// ===== Budgets =====
function budgetSpent(b) {
  return transactions.value
    .filter(t => t.type === 'expense' && t.category === b.category && t.month === viewMonth.value)
    .reduce((s, t) => s + t.amount, 0)
}
function budgetPercent(b) { return b.monthly > 0 ? Math.round(budgetSpent(b) / b.monthly * 100) : 0 }
function budgetRemain(b) { return b.monthly - budgetSpent(b) }

function openNewBudget() {
  editingBudget.value = { id: null, category: 'dining', monthly: 0 }
  isEditingBudget.value = false
  showBudgetModal.value = true
}

function editBudget(b) {
  editingBudget.value = { ...b }
  isEditingBudget.value = true
  showBudgetModal.value = true
}

function saveBudget() {
  if (!editingBudget.value.monthly || editingBudget.value.monthly <= 0) { alert('请输入预算金额'); return }
  if (isEditingBudget.value) {
    const idx = budgets.value.findIndex(b => b.id === editingBudget.value.id)
    if (idx !== -1) budgets.value[idx] = { ...editingBudget.value }
  } else {
    const maxN = Math.max(...budgets.value.map(b => parseInt(b.id.slice(1))), 0)
    budgets.value.push({ ...editingBudget.value, id: 'B' + String(maxN + 1).padStart(3, '0') })
  }
  showBudgetModal.value = false
  save()
}

function deleteBudget(id) {
  if (!confirm('确定删除这个预算吗？')) return
  budgets.value = budgets.value.filter(b => b.id !== id)
  save()
}
</script>
