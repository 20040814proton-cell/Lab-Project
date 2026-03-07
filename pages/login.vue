<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '~/stores/user'
import { apiFetch } from '~/logics/api'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const role = ref('student') // 'student' | 'teacher' | 'superadmin'
const showPassword = ref(false)
const loading = ref(false)
const showError = ref(false)
const errorMessage = ref('')

const roleTitle = computed(() => {
  if (role.value === 'teacher')
    return '教师登录'
  if (role.value === 'superadmin')
    return '超级管理员登录'
  return '学生登录'
})

async function handleLogin() {
  if (!username.value || !password.value) {
    showToast('请输入账号和密码')
    return
  }

  loading.value = true
  showError.value = false
  errorMessage.value = ''

  try {
    const res = await apiFetch('/api/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        role: role.value,
      }),
    }, { auth: false })

    if (res.ok) {
      const data = await res.json()
      userStore.login(data.access_token, {
        username: data.username,
        role: data.role,
        user_role: data.user_role || data.role,
      })
      router.push('/dashboard')
      return
    }

    const err = await res.json().catch(() => ({}))
    showToast(err.detail || '登录失败')
  }
  catch (error) {
    console.error(error)
    showToast('网络错误，请稍后重试')
  }
  finally {
    loading.value = false
  }
}

function showToast(msg: string) {
  errorMessage.value = msg
  showError.value = true
  setTimeout(() => {
    showError.value = false
  }, 3000)
}
</script>

<template>
  <div class="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#F5F5F7] px-4 py-10 dark:bg-[#121212]">
    <div class="absolute inset-0 z-0 opacity-5 pointer-events-none" style="background-image: url('/noise.png');" />
    <div class="absolute top-0 right-0 h-[45vh] w-[45vw] bg-gradient-to-b from-teal-500/10 to-transparent blur-3xl pointer-events-none" />

    <div class="relative z-10 w-full max-w-md rounded-2xl border border-gray-200/50 bg-white/85 p-8 shadow-xl backdrop-blur-xl dark:border-gray-800/60 dark:bg-black/60 md:p-10">
      <div class="mb-8 text-center">
        <h1 class="mb-2 text-4xl font-serif font-bold tracking-[0.2em] text-gray-900 dark:text-gray-100">实验室</h1>
        <p class="text-xs uppercase tracking-[0.35em] text-gray-400">Laboratory System</p>
      </div>

      <div class="mb-2 text-sm font-medium text-gray-600 dark:text-gray-300">{{ roleTitle }}</div>

      <div class="mb-6 grid grid-cols-3 rounded-lg bg-gray-100 p-1 dark:bg-gray-800/50">
        <button
          class="rounded-md py-2 text-sm font-medium transition"
          :class="role === 'student' ? 'bg-white text-teal-600 shadow-sm dark:bg-gray-700 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="role = 'student'"
        >
          学生
        </button>
        <button
          class="rounded-md py-2 text-sm font-medium transition"
          :class="role === 'teacher' ? 'bg-white text-teal-600 shadow-sm dark:bg-gray-700 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="role = 'teacher'"
        >
          教师
        </button>
        <button
          class="rounded-md py-2 text-sm font-medium transition"
          :class="role === 'superadmin' ? 'bg-white text-teal-600 shadow-sm dark:bg-gray-700 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="role = 'superadmin'"
        >
          超管
        </button>
      </div>

      <div v-if="showError" class="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
        {{ errorMessage }}
      </div>

      <div class="space-y-5">
        <div class="relative">
          <input
            v-model="username"
            type="text"
            placeholder="账号 / Username"
            class="w-full border-b border-gray-300 bg-transparent px-3 py-2 pr-9 outline-none transition-colors placeholder:text-gray-400 focus:border-teal-500 dark:border-gray-700"
            @keyup.enter="handleLogin"
          >
          <span class="i-carbon-user absolute right-1 top-2.5 text-xl text-gray-400" />
        </div>

        <div class="relative">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="密码"
            class="w-full border-b border-gray-300 bg-transparent px-3 py-2 pr-20 outline-none transition-colors placeholder:text-gray-400 focus:border-teal-500 dark:border-gray-700"
            @keyup.enter="handleLogin"
          >
          <button
            type="button"
            class="absolute right-1 top-2 text-xs text-gray-500 hover:text-teal-600"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? '隐藏' : '显示' }}
          </button>
        </div>

        <button
          class="mt-2 w-full rounded-lg bg-teal-600 py-3 font-medium tracking-wide text-white shadow-lg shadow-teal-500/30 transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-70"
          :disabled="loading"
          @click="handleLogin"
        >
          <span v-if="loading" class="i-carbon-circle-dash mr-2 animate-spin" />
          {{ loading ? '登录中...' : '立即登录' }}
        </button>
      </div>

      <div class="mt-6 text-center text-xs text-gray-500">
        还没有账号？
        <span class="cursor-pointer text-teal-600 hover:underline" @click="router.push('/register')">申请入驻</span>
      </div>
    </div>
  </div>
</template>