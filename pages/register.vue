<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '~/logics/api'

const router = useRouter()

const name = ref('')
const password = ref('')
const role = ref('student') // 'student' or 'teacher'
const grade = ref(2025)
const inviteCode = ref('')

const loading = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleRegister = async () => {
  if (!name.value || !password.value) {
    showToast('请输入姓名和密码')
    return
  }
  if (!inviteCode.value) {
     showToast('请输入邀请码')
     return
  }

  loading.value = true
  try {
    const res = await apiFetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value,
        password: password.value,
        role: role.value,
        grade: role.value === 'student' ? grade.value : undefined,
        invite_code: inviteCode.value,
        // username is auto-generated for students, optional for teachers (we use name as default)
      }),
    }, { auth: false })

    if (res.ok) {
      const data = await res.json()
      successMessage.value = `注册成功! 您的ID是: ${data.username}`
      
      // Delay redirect to let user see ID
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }
    else {
      const err = await res.json()
      showToast(err.detail || '注册失败')
    }
  }
  catch (e) {
    showToast('网络错误')
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

    <!-- Card -->
    <div class="relative z-10 w-full max-w-md p-8 md:p-12 bg-white/80 dark:bg-black/60 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-800/50">
      
      <!-- Success View -->
      <div v-if="successMessage" class="text-center py-10">
        <div class="i-carbon-checkmark-filled text-4xl text-teal-500 mb-4 mx-auto" />
        <h2 class="text-xl font-bold mb-2">注册成功</h2>
        <p class="opacity-80 mb-6">{{ successMessage }}</p>
        <button @click="router.push('/login')" class="px-6 py-2 bg-teal-500 text-white rounded-full">
          前往登录
        </button>
      </div>

      <!-- Register Form -->
      <div v-else>
        <!-- Title -->
        <div class="text-center mb-8">
          <h1 class="text-4xl font-serif font-bold mb-2 tracking-widest text-gray-900 dark:text-gray-100">
            入 籍
          </h1>
          <div class="text-xs uppercase tracking-[0.4em] opacity-60 font-sans">
            Apply Account
          </div>
        </div>

        <!-- Role Switcher -->
        <div class="flex p-1 mb-6 bg-gray-100 dark:bg-gray-800/50 rounded-lg">
          <button
            class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all duration-300"
            :class="role === 'student' ? 'bg-white dark:bg-gray-700 shadow-sm text-teal-600 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            @click="role = 'student'"
          >
            学生
          </button>
          <button
            class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all duration-300"
            :class="role === 'teacher' ? 'bg-white dark:bg-gray-700 shadow-sm text-teal-600 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            @click="role = 'teacher'"
          >
            教师
          </button>
        </div>

        <!-- Form -->
        <div class="space-y-5">
          <div class="relative group">
            <input
              v-model="name"
              type="text"
              placeholder="姓名 / Name"
              class="w-full px-4 py-2 bg-transparent border-b border-gray-300 dark:border-gray-700 focus:border-teal-500 dark:focus:border-teal-400 outline-none transition-colors placeholder:text-gray-400"
            >
          </div>

          <div class="relative group">
            <input
              v-model="password"
              type="password"
              placeholder="设置密码 / Password"
              class="w-full px-4 py-2 bg-transparent border-b border-gray-300 dark:border-gray-700 focus:border-teal-500 dark:focus:border-teal-400 outline-none transition-colors placeholder:text-gray-400"
            >
          </div>

          <!-- Student Specific -->
          <div v-if="role === 'student'" class="relative group">
            <label class="text-xs opacity-50 block mb-1">年级 / Grade</label>
            <select v-model="grade" class="w-full px-4 py-2 bg-transparent border border-gray-200 dark:border-gray-700 rounded outline-none">
              <option :value="2026">2026 级</option>
              <option :value="2025">2025 级</option>
              <option :value="2024">2024 级</option>
              <option :value="2023">2023 级</option>
            </select>
          </div>

          <!-- Invite Code (Required) -->
          <div class="relative group">
            <input
              v-model="inviteCode"
              type="text"
              placeholder="邀请码 / Invite Code"
              class="w-full px-4 py-2 bg-transparent border-b border-gray-300 dark:border-gray-700 focus:border-teal-500 dark:focus:border-teal-400 outline-none transition-colors placeholder:text-gray-400"
            >
          </div>

          <button
            class="w-full py-3 mt-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg shadow-lg shadow-teal-500/30 transition-all duration-300 font-medium tracking-wide disabled:opacity-70"
            :disabled="loading"
            @click="handleRegister"
          >
             <span v-if="loading" class="i-carbon-circle-dash animate-spin mr-2" />
             提交申请
          </button>
          
           <div class="text-center mt-4 text-xs opacity-60 hover:opacity-100 cursor-pointer" @click="router.push('/login')">
            已有账号? 直接登录
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-10 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-10 opacity-0"
    >
      <div v-if="showError" class="fixed bottom-10 px-6 py-3 bg-red-500/90 backdrop-blur text-white rounded-full shadow-lg text-sm flex items-center gap-2 z-50">
        <span class="i-carbon-warning-filled" />
        {{ errorMessage }}
      </div>
    </Transition>
  </div>
</template>
