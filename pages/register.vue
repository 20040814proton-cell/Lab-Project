<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '~/logics/api'

const router = useRouter()

const name = ref('')
const password = ref('')
const role = ref('student') // 'student' | 'teacher'
const grade = ref<number | null>(null)
const inviteCode = ref('')

const gradeOptions = ref<number[]>([])
const gradeOptionsSource = ref<'policy' | 'default' | ''>('')
const gradeOptionsLoading = ref(false)
const gradeOptionsError = ref('')

const loading = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const canSubmitStudent = computed(() => !gradeOptionsLoading.value && gradeOptions.value.length > 0)

async function fetchGradeOptions() {
  gradeOptionsLoading.value = true
  gradeOptionsError.value = ''
  try {
    const res = await apiFetch('/api/register/grade-options', {}, { auth: false })
    if (!res.ok) {
      gradeOptions.value = []
      gradeOptionsSource.value = ''
      gradeOptionsError.value = '无法加载可注册年级，请稍后重试'
      return
    }

    const data = await res.json()
    const grades = Array.isArray(data?.grades)
      ? data.grades
        .map((item: any) => Number(item))
        .filter((item: number) => Number.isInteger(item))
      : []

    gradeOptions.value = grades
    gradeOptionsSource.value = data?.source === 'policy' ? 'policy' : 'default'
    if (grades.length > 0)
      grade.value = grades[0]
  }
  catch (error) {
    console.error(error)
    gradeOptions.value = []
    gradeOptionsSource.value = ''
    gradeOptionsError.value = '网络异常，年级选项加载失败'
  }
  finally {
    gradeOptionsLoading.value = false
  }
}

watch(role, (nextRole) => {
  if (nextRole === 'student') {
    if (gradeOptions.value.length > 0)
      grade.value = gradeOptions.value[0]
  }
  else {
    grade.value = null
  }
})

async function handleRegister() {
  if (!name.value || !password.value) {
    showToast('请输入姓名和密码')
    return
  }
  if (!inviteCode.value) {
    showToast('请输入邀请码')
    return
  }

  if (role.value === 'student') {
    if (!canSubmitStudent.value) {
      showToast(gradeOptionsError.value || '当前无法提交学生注册')
      return
    }
    if (!grade.value || !gradeOptions.value.includes(Number(grade.value))) {
      showToast('请选择有效年级')
      return
    }
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
        grade: role.value === 'student' ? Number(grade.value) : undefined,
        invite_code: inviteCode.value,
      }),
    }, { auth: false })

    if (res.ok) {
      const data = await res.json()
      successMessage.value = `注册成功，您的账号是：${data.username}`
      setTimeout(() => {
        router.push('/login')
      }, 3000)
      return
    }

    const err = await res.json().catch(() => ({}))
    showToast(err.detail || '注册失败')
  }
  catch (e) {
    console.error(e)
    showToast('网络错误')
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

onMounted(fetchGradeOptions)
</script>

<template>
  <div class="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#F5F5F7] dark:bg-[#121212] px-4 py-10">
    <div class="absolute inset-0 opacity-5 pointer-events-none z-0" style="background-image: url('/noise.png');" />
    <div class="absolute top-0 right-0 h-[45vh] w-[45vw] bg-gradient-to-b from-teal-500/10 to-transparent blur-3xl pointer-events-none" />

    <div class="relative z-10 w-full max-w-md rounded-2xl border border-gray-200/50 bg-white/85 p-8 shadow-xl backdrop-blur-xl dark:border-gray-800/60 dark:bg-black/60 md:p-10">
      <div v-if="successMessage" class="py-8 text-center">
        <div class="i-carbon-checkmark-filled mx-auto mb-3 text-4xl text-teal-500" />
        <h2 class="mb-2 text-xl font-bold">注册成功</h2>
        <p class="mb-6 text-sm text-gray-500">{{ successMessage }}</p>
        <button class="rounded-full bg-teal-500 px-6 py-2 text-white" @click="router.push('/login')">
          前往登录
        </button>
      </div>

      <div v-else>
        <div class="mb-8 text-center">
          <h1 class="mb-2 text-4xl font-serif font-bold tracking-[0.2em] text-gray-900 dark:text-gray-100">入驻</h1>
          <div class="text-xs uppercase tracking-[0.35em] text-gray-400">Apply Account</div>
        </div>

        <div class="mb-6 grid grid-cols-2 rounded-lg bg-gray-100 p-1 dark:bg-gray-800/50">
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
        </div>

        <div class="space-y-5">
          <input
            v-model="name"
            type="text"
            placeholder="姓名 / Name"
            class="w-full border-b border-gray-300 bg-transparent px-3 py-2 outline-none transition-colors placeholder:text-gray-400 focus:border-teal-500 dark:border-gray-700"
          >

          <input
            v-model="password"
            type="password"
            placeholder="设置密码 / Password"
            class="w-full border-b border-gray-300 bg-transparent px-3 py-2 outline-none transition-colors placeholder:text-gray-400 focus:border-teal-500 dark:border-gray-700"
          >

          <div v-if="role === 'student'" class="space-y-2">
            <label class="block text-xs text-gray-500">年级 / Grade</label>
            <select
              v-model.number="grade"
              class="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 outline-none dark:border-gray-700"
              :disabled="gradeOptionsLoading || gradeOptions.length === 0"
            >
              <option v-if="gradeOptionsLoading" :value="null">加载中...</option>
              <option v-else-if="gradeOptions.length === 0" :value="null">暂无可选年级</option>
              <option v-for="item in gradeOptions" :key="item" :value="item">
                {{ item }} 级
              </option>
            </select>
            <p class="text-xs" :class="gradeOptionsError ? 'text-red-500' : 'text-gray-500'">
              <template v-if="gradeOptionsError">{{ gradeOptionsError }}</template>
              <template v-else-if="gradeOptionsSource === 'policy'">当前年级由超级管理员策略控制</template>
              <template v-else>当前使用默认年级范围</template>
            </p>
          </div>

          <input
            v-model="inviteCode"
            type="text"
            placeholder="邀请码 / Invite Code"
            class="w-full border-b border-gray-300 bg-transparent px-3 py-2 outline-none transition-colors placeholder:text-gray-400 focus:border-teal-500 dark:border-gray-700"
          >

          <button
            class="mt-2 w-full rounded-lg bg-teal-600 py-3 font-medium tracking-wide text-white shadow-lg shadow-teal-500/30 transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="loading || (role === 'student' && !canSubmitStudent)"
            @click="handleRegister"
          >
            <span v-if="loading" class="i-carbon-circle-dash mr-2 animate-spin" />
            提交申请
          </button>

          <div class="pt-1 text-center text-xs text-gray-500">
            已有账号？
            <span class="cursor-pointer text-teal-600 hover:underline" @click="router.push('/login')">直接登录</span>
          </div>
        </div>
      </div>
    </div>

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
        class="fixed bottom-10 z-50 flex items-center gap-2 rounded-full bg-red-500/90 px-6 py-3 text-sm text-white shadow-lg backdrop-blur"
      >
        <span class="i-carbon-warning-filled" />
        {{ errorMessage }}
      </div>
    </Transition>
  </div>
</template>