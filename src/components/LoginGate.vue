<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl p-8 max-w-sm w-full">
      <!-- 标题 -->
      <div class="text-center mb-6">
        <div class="text-4xl mb-3">🚪</div>
        <h1 class="text-2xl font-bold text-gray-800">阿财的任意门</h1>
        <p class="text-sm text-gray-500 mt-1">私人空间 · 请登录</p>
      </div>

      <!-- 二维码扫码登录 -->
      <div class="flex justify-center mb-4">
        <div class="bg-gray-100 rounded-xl p-3">
          <img
            :src="qrUrl"
            alt="扫码登录"
            class="w-48 h-48"
            @error="qrError = true"
          />
        </div>
      </div>
      <p class="text-center text-sm text-gray-400 mb-6">
        <template v-if="!qrError">📱 微信扫一扫直接登录</template>
        <template v-else>二维码加载失败，请使用密码登录</template>
      </p>

      <!-- 分隔线 + 密码登录 -->
      <div class="border-t border-gray-200 pt-6">
        <p class="text-sm text-gray-400 mb-3 text-center">或输入密码登录</p>
        <div class="relative">
          <input
            ref="pwdInput"
            v-model="password"
            :type="showPwd ? 'text' : 'password'"
            placeholder="输入密码"
            class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
            :class="{ 'border-red-400 ring-2 ring-red-200': error }"
            @keyup.enter="login"
            @input="error = ''"
          />
          <button
            @click="showPwd = !showPwd"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            tabindex="-1"
          >
            <svg v-if="!showPwd" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
        <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
        <button
          @click="login"
          :disabled="loading"
          class="w-full mt-3 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors font-medium"
        >
          {{ loading ? '验证中...' : '登 录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { AUTH_KEY, hashKey } from '../config.js'

const password = ref('')
const error = ref('')
const loading = ref(false)
const showPwd = ref(false)
const qrError = ref(false)
const pwdInput = ref(null)

const emit = defineEmits(['login'])

// 扫码登录 URL
const loginUrl = computed(() => {
  const origin = window.location.origin
  const path = window.location.pathname.replace(/\/$/, '')
  return `${origin}${path}?key=${encodeURIComponent(AUTH_KEY)}`
})

const qrUrl = computed(() =>
  `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(loginUrl.value)}&margin=10`
)

onMounted(() => {
  pwdInput.value?.focus()
})

async function login() {
  error.value = ''
  if (!password.value.trim()) {
    error.value = '请输入密码'
    return
  }
  loading.value = true
  try {
    const inputHash = await hashKey(password.value.trim())
    const expectedHash = await hashKey(AUTH_KEY)
    if (inputHash === expectedHash) {
      localStorage.setItem('life-os-auth', expectedHash)
      emit('login')
    } else {
      error.value = '密码错误，请重试'
      password.value = ''
      pwdInput.value?.focus()
    }
  } catch (e) {
    error.value = '验证失败，请刷新重试'
  } finally {
    loading.value = false
  }
}
</script>
