<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, withApiBase } from '~/logics/api'
import { useUserStore } from '~/stores/user'

interface StudentItem {
  id?: string
  _id?: string
  username?: string
  name: string
  role?: string
  grade?: number
  avatar?: string
  major?: string
  interests?: string[]
  public_email?: string
}

const router = useRouter()
const userStore = useUserStore()

const students = ref<StudentItem[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedGrade = ref('All')
const grades = ['All', '2026', '2025', '2024', '2023']

const normalizeAvatar = (avatar?: string) => avatar ? withApiBase(avatar) : ''

function hasProfile(student: StudentItem) {
  return Boolean(student.username)
}

function openProfile(student: StudentItem) {
  if (!student.username)
    return
  router.push(`/u/${encodeURIComponent(student.username)}`)
}

const filteredStudents = computed(() => {
  return students.value.filter((student) => {
    if (selectedGrade.value !== 'All' && String(student.grade || '') !== selectedGrade.value)
      return false

    if (!searchQuery.value.trim())
      return true

    const q = searchQuery.value.trim().toLowerCase()
    return [
      student.name,
      student.username || '',
      student.major || '',
      student.public_email || '',
    ].some(part => part.toLowerCase().includes(q))
  })
})

async function fetchStudents() {
  loading.value = true
  try {
    const res = await apiFetch('/api/students', {}, { auth: false })
    if (!res.ok)
      return
    students.value = await res.json()
  }
  catch (error) {
    console.error(error)
  }
  finally {
    loading.value = false
  }
}

async function deleteStudent(id: string) {
  if (!confirm('确认删除该学生？此操作不可恢复。'))
    return

  try {
    const res = await apiFetch(`/api/students/${id}`, { method: 'DELETE' })
    if (res.ok) {
      students.value = students.value.filter(s => (s.id || s._id) !== id && s.username !== id)
      return
    }
    const err = await res.json().catch(() => ({}))
    alert(err.detail || '删除失败，权限不足？')
  }
  catch (error) {
    console.error(error)
    alert('网络错误')
  }
}

onMounted(fetchStudents)
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-3xl font-serif font-bold text-gray-900 dark:text-gray-100">学生管理</h1>
        <p class="mt-2 text-sm text-gray-500">Student Directory</p>
      </div>

      <div class="flex w-full flex-col gap-3 md:w-auto md:flex-row md:items-center">
        <div class="flex rounded-xl border border-gray-200 bg-white p-1 dark:border-gray-700 dark:bg-gray-800">
          <button
            v-for="grade in grades"
            :key="grade"
            class="rounded-lg px-3 py-1.5 text-sm transition"
            :class="selectedGrade === grade
              ? 'bg-teal-600 text-white shadow'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100'"
            @click="selectedGrade = grade"
          >
            {{ grade }}
          </button>
        </div>

        <div class="relative w-full md:w-72">
          <div class="i-carbon-search pointer-events-none absolute left-3 top-2.5 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索姓名 / 用户名 / 邮箱"
            class="w-full rounded-xl border border-gray-200 bg-white py-2 pl-9 pr-3 text-sm outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-800"
          >
        </div>
      </div>
    </div>

    <div v-if="loading" class="py-14 text-center text-gray-400">
      <div class="i-carbon-circle-dash mx-auto mb-2 animate-spin text-3xl" />
      Loading...
    </div>

    <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="student in filteredStudents"
        :key="student.id || student._id || student.username"
        class="group relative rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
        :class="hasProfile(student) ? 'cursor-pointer' : ''"
        @click="hasProfile(student) && openProfile(student)"
      >
        <div class="mb-4 flex items-start gap-4">
          <div class="h-24 w-24 shrink-0 overflow-hidden rounded-full border-4 border-teal-50 bg-gray-100 shadow-sm dark:border-teal-900/30 dark:bg-gray-800">
            <img
              v-if="student.avatar"
              :src="normalizeAvatar(student.avatar)"
              class="h-full w-full object-cover object-center"
            >
            <div v-else class="i-carbon-user flex h-full w-full items-center justify-center text-3xl text-gray-300" />
          </div>

          <div class="min-w-0 flex-1">
            <div class="flex items-start justify-between gap-2">
              <h3 class="truncate text-xl font-bold text-gray-900 dark:text-gray-100">{{ student.name }}</h3>
              <button
                v-if="userStore.hasRole('teacher', 'superadmin')"
                class="i-carbon-trash-can shrink-0 text-gray-300 transition hover:text-red-500"
                title="删除"
                @click.stop="deleteStudent(student.id || student._id || student.username || '')"
              />
            </div>
            <p v-if="student.username" class="mt-1 text-xs text-gray-500">@{{ student.username }}</p>
            <p class="mt-1 text-sm text-gray-500">{{ student.role || 'Student' }}</p>
            <p class="mt-1 truncate text-xs text-teal-600 dark:text-teal-400">
              {{ student.major || 'Major: Undeclared' }}
            </p>
          </div>
        </div>

        <div class="mb-4 min-h-[3.5rem] rounded-lg bg-gray-50 p-3 dark:bg-gray-800/60">
          <p v-if="student.public_email" class="truncate text-xs text-gray-600 dark:text-gray-300">
            <span class="font-medium">Email:</span> {{ student.public_email }}
          </p>
          <p v-else class="text-xs text-gray-400">No public email</p>

          <div class="mt-2 flex flex-wrap gap-1.5">
            <span
              v-for="tag in (student.interests || []).slice(0, 3)"
              :key="tag"
              class="rounded-md border border-teal-100 bg-teal-50 px-2 py-0.5 text-xs text-teal-700 dark:border-teal-900/40 dark:bg-teal-900/20 dark:text-teal-300"
            >
              {{ tag }}
            </span>
            <span v-if="!student.interests || student.interests.length === 0" class="text-xs italic text-gray-400">No public interests</span>
          </div>
        </div>

        <div class="flex items-center justify-between border-t border-gray-100 pt-3 text-xs text-gray-500 dark:border-gray-800">
          <span>Grade {{ student.grade || 'N/A' }}</span>
          <button
            v-if="hasProfile(student)"
            class="rounded-md border border-gray-200 px-2.5 py-1 text-xs font-medium text-gray-600 transition hover:border-teal-400 hover:text-teal-600 dark:border-gray-700 dark:text-gray-300"
            @click.stop="openProfile(student)"
          >
            查看主页
          </button>
          <span v-else class="text-gray-400">No profile</span>
        </div>
      </article>
    </div>
  </div>
</template>
