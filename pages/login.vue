<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '~/stores/user'
import { apiFetch } from '~/logics/api'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const role = ref('student') // 'student' | 'teacher' | 'superadmin'
const loading = ref(false)
const showError = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    showToast('请输入账号和密码')
    return
  }

  loading.value = true
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
    }
    else {
      const err = await res.json()
      showToast(err.detail || '登录失败')
    }
  }
  catch (e) {
    showToast('网络错误，请稍后重试')
    console.error(e)
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
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#F5F5F7] dark:bg-[#121212]">
    <!-- Background Texture -->
    <div class="absolute inset-0 opacity-5 pointer-events-none z-0" style="background-image: url('/noise.png');" />
    <div class="absolute top-0 right-0 w-[50vw] h-[50vh] bg-gradient-to-b from-teal-500/10 to-transparent blur-3xl pointer-events-none" />

    <!-- Login Card -->
    <div class="relative z-10 w-full max-w-md p-8 md:p-12 bg-white/80 dark:bg-black/60 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-800/50">
      <!-- Title -->
      <div class="text-center mb-10">
        <h1 class="text-5xl font-serif font-bold mb-2 tracking-widest text-gray-900 dark:text-gray-100">
          墨 枢
        </h1>
        <div class="text-xs uppercase tracking-[0.4em] opacity-60 font-sans">
          Laboratory System
        </div>
      </div>

      <!-- Role Switcher -->
      <div class="flex p-1 mb-8 bg-gray-100 dark:bg-gray-800/50 rounded-lg">
        <button
          class="flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300"
          :class="role === 'student' ? 'bg-white dark:bg-gray-700 shadow-sm text-teal-600 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="role = 'student'"
        >
          登入学生
        </button>
        <button
          class="flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300"
          :class="role === 'teacher' ? 'bg-white dark:bg-gray-700 shadow-sm text-teal-600 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="role = 'teacher'"
        >
          登入教师
        </button>
        <button
          class="flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300"
          :class="role === 'superadmin' ? 'bg-white dark:bg-gray-700 shadow-sm text-teal-600 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="role = 'superadmin'"
        >
          超级账号
        </button>
      </div>

      <!-- Form -->
      <div class="space-y-6">
        <div class="relative group">
          <input
            v-model="username"
            type="text"
            placeholder="账号 / ID"
            class="w-full px-4 py-3 bg-transparent border-b border-gray-300 dark:border-gray-700 focus:border-teal-500 dark:focus:border-teal-400 outline-none transition-colors placeholder:text-gray-400"
            @keyup.enter="handleLogin"
          >
          <div class="absolute right-0 top-3 text-gray-400">
            <div class="i-carbon-user text-xl" />
          </div>
        </div>

        <div class="relative group">
          <input
            v-model="password"
            type="password"
            placeholder="密码"
            class="w-full px-4 py-3 bg-transparent border-b border-gray-300 dark:border-gray-700 focus:border-teal-500 dark:focus:border-teal-400 outline-none transition-colors placeholder:text-gray-400"
            @keyup.enter="handleLogin"
          >
          <div class="absolute right-0 top-3 text-gray-400">
            <div class="i-carbon-password text-xl" />
          </div>
        </div>

        <button
          class="w-full py-3 mt-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg shadow-lg shadow-teal-500/30 transition-all duration-300 font-medium tracking-wide disabled:opacity-70 disabled:cursor-not-allowed"
          :disabled="loading"
          @click="handleLogin"
        >
          <span v-if="loading" class="i-carbon-circle-dash animate-spin mr-2" />
          {{ loading ? '验证中...' : '立即入境' }}
        </button>
      </div>

      <!-- Footer -->
      <div class="mt-8 text-center text-xs text-gray-400">
        <span class="hover:text-teal-600 cursor-pointer transition" @click="router.push('/register')">申请入驻</span>
        <span class="mx-2">|</span>
        <span class="hover:text-teal-600 cursor-pointer transition">忘记密码?</span>
      </div>
    </div>

    <!-- Toast Notification -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-10 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-10 opacity-0"
    >
      <div
        v-if="showError"
        class="fixed bottom-10 px-6 py-3 bg-red-500/90 backdrop-blur text-white rounded-full shadow-lg text-sm flex items-center gap-2 z-50"
      >
        <span class="i-carbon-warning-filled" />
        {{ errorMessage }}
      </div>
    </Transition>
  </div>
</template>
