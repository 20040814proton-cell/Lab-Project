<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch, withApiBase } from '~/logics/api'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const route = useRoute()

const activities = ref<any[]>([])
const stats = ref<Record<string, number>>({})
const loading = ref(false)
const showModal = ref(false)
const submitting = ref(false)
const viewMode = ref<'upcoming' | 'past'>('upcoming')
const editingId = ref<string | null>(null)

const isLoggedIn = computed(() => userStore.isTokenValid())
const isManager = computed(() => userStore.hasRole('teacher', 'superadmin'))
const currentUsername = computed(() => userStore.userInfo?.username || '')
const creatorFilter = computed(() => typeof route.query.creator === 'string' ? route.query.creator.trim() : '')

const isOwner = (activity: any) => Boolean(currentUsername.value && activity?.created_by_username === currentUsername.value)
const canManage = (activity: any) => isManager.value || isOwner(activity)

const form = ref({
  title: '',
  type: '研讨会',
  date: '',
  location: '',
  participants: 0,
  summary: '',
  content: '',
  cover_image: '',
})

const activityTypes = ['研讨会', '工作坊', '开放日', '讲座', '其他']

const upcomingActivities = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return activities.value
    .filter(item => new Date(item.date) >= today)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const pastActivities = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return activities.value
    .filter(item => new Date(item.date) < today)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

async function fetchActivities() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (creatorFilter.value)
      params.set('creator', creatorFilter.value)

    const url = params.toString() ? `/api/activities/?${params.toString()}` : '/api/activities/'
    const res = await apiFetch(url, {}, { auth: false })
    if (res.ok)
      activities.value = await res.json()

    const statsRes = await apiFetch('/api/activities/stats', {}, { auth: false })
    if (statsRes.ok)
      stats.value = await statsRes.json()
  }
  catch (error) {
    console.error(error)
  }
  finally {
    loading.value = false
  }
}

function triggerUpload() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (event: any) => {
    const file = event.target.files?.[0]
    if (!file)
      return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await apiFetch('/api/upload/', {
        method: 'POST',
        body: formData,
      })
      if (!res.ok)
        return
      const data = await res.json()
      form.value.cover_image = withApiBase(data.url)
    }
    catch (error) {
      console.error(error)
      alert('Upload failed')
    }
  }
  input.click()
}

function openCreateModal() {
  if (!isLoggedIn.value) {
    alert('请先登录')
    return
  }
  editingId.value = null
  form.value = {
    title: '',
    type: '研讨会',
    date: '',
    location: '',
    participants: 0,
    summary: '',
    content: '',
    cover_image: '',
  }
  showModal.value = true
}

function openEditModal(activity: any) {
  if (!canManage(activity)) {
    alert('无权限编辑该活动')
    return
  }

  editingId.value = activity.id
  form.value = {
    ...activity,
    date: String(activity.date || '').split('T')[0],
  }
  showModal.value = true
}

async function submitActivity() {
  if (!form.value.title || !form.value.date) {
    alert('请填写必填项')
    return
  }

  submitting.value = true
  try {
    const payload = {
      ...form.value,
      participants: parseInt(String(form.value.participants || 0), 10) || 0,
    }

    const url = editingId.value ? `/api/activities/${editingId.value}` : '/api/activities/'
    const method = editingId.value ? 'PUT' : 'POST'

    const res = await apiFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '操作失败')
      return
    }

    showModal.value = false
    await fetchActivities()
    alert(editingId.value ? '活动修改成功' : '活动发布成功')
  }
  catch (error: any) {
    console.error(error)
    alert(error.message || '操作失败')
  }
  finally {
    submitting.value = false
  }
}

async function deleteActivity(activity: any) {
  if (!canManage(activity)) {
    alert('无权限删除该活动')
    return
  }
  if (!confirm('确认删除该活动？'))
    return

  try {
    const res = await apiFetch(`/api/activities/${activity.id}`, { method: 'DELETE' })
    if (res.ok)
      await fetchActivities()
  }
  catch (error) {
    console.error(error)
  }
}

watch(() => route.query.creator, fetchActivities)
onMounted(fetchActivities)
</script>

<template>
  <div class="mx-auto min-h-screen max-w-7xl px-6 py-10">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 class="text-4xl font-serif font-bold text-gray-900 dark:text-gray-100">学术活动</h1>
        <p class="mt-2 text-sm text-gray-500">Laboratory Learning Activities</p>
      </div>
      <button
        v-if="isLoggedIn"
        class="rounded-lg bg-teal-600 px-4 py-2 text-white transition hover:bg-teal-700"
        @click="openCreateModal"
      >
        发布活动
      </button>
    </div>

    <div v-if="creatorFilter" class="mb-6 flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50 px-4 py-2 text-sm text-teal-700">
      <span>当前仅展示 @{{ creatorFilter }} 的活动</span>
      <RouterLink to="/activities" class="hover:underline">清除筛选</RouterLink>
    </div>

    <div class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-gray-200 bg-white p-5 text-center dark:border-gray-800 dark:bg-gray-900">
        <p class="text-xs uppercase tracking-wider text-gray-500">开放日</p>
        <p class="mt-2 text-4xl font-serif text-teal-600">{{ stats['开放日'] || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-gray-200 bg-white p-5 text-center dark:border-gray-800 dark:bg-gray-900">
        <p class="text-xs uppercase tracking-wider text-gray-500">研讨会</p>
        <p class="mt-2 text-4xl font-serif text-indigo-600">{{ stats['研讨会'] || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-gray-200 bg-white p-5 text-center dark:border-gray-800 dark:bg-gray-900">
        <p class="text-xs uppercase tracking-wider text-gray-500">工作坊</p>
        <p class="mt-2 text-4xl font-serif text-amber-600">{{ stats['工作坊'] || 0 }}</p>
      </div>
    </div>

    <div class="mb-6 flex items-center gap-3">
      <button class="rounded-full px-4 py-1.5 text-sm" :class="viewMode === 'upcoming' ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-500'" @click="viewMode = 'upcoming'">
        近期活动
      </button>
      <button class="rounded-full px-4 py-1.5 text-sm" :class="viewMode === 'past' ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-500'" @click="viewMode = 'past'">
        往期回顾
      </button>
    </div>

    <div v-if="loading" class="py-16 text-center text-gray-400">
      <div class="i-carbon-circle-dash mx-auto mb-2 animate-spin text-3xl" />
      Loading...
    </div>

    <div v-else-if="viewMode === 'upcoming'">
      <div v-if="upcomingActivities.length === 0" class="rounded-xl border border-dashed border-gray-300 py-16 text-center text-gray-400">
        暂无近期活动
      </div>
      <div v-else class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="activity in upcomingActivities"
          :key="activity.id"
          class="group cursor-pointer overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
          @click="$router.push(`/activities/${activity.id}`)"
        >
          <div class="relative h-44 overflow-hidden">
            <img
              :src="activity.cover_image || 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?q=80&w=2070&auto=format&fit=crop'"
              class="h-full w-full object-cover transition duration-500 group-hover:scale-105"
            >
            <div v-if="canManage(activity)" class="absolute right-3 top-3 flex gap-2" @click.stop>
              <button class="rounded-full bg-white/90 p-2 text-teal-600" @click="openEditModal(activity)">
                <div class="i-carbon-edit" />
              </button>
              <button class="rounded-full bg-white/90 p-2 text-red-500" @click="deleteActivity(activity)">
                <div class="i-carbon-trash-can" />
              </button>
            </div>
          </div>

          <div class="p-5">
            <div class="mb-2 flex items-center gap-2 text-xs text-teal-600">
              <span class="rounded border border-teal-200 px-2 py-0.5">{{ activity.type }}</span>
              <span>{{ activity.date }}</span>
            </div>
            <h3 class="mb-2 line-clamp-1 text-lg font-bold">{{ activity.title }}</h3>
            <p class="mb-3 line-clamp-2 text-sm text-gray-500">{{ activity.summary }}</p>
            <div class="flex items-center justify-between border-t border-gray-100 pt-3 text-xs text-gray-500 dark:border-gray-800">
              <span>{{ activity.location }} · {{ activity.participants }}人</span>
              <RouterLink
                v-if="activity.created_by_username"
                :to="`/u/${encodeURIComponent(activity.created_by_username)}`"
                class="text-teal-600 hover:underline"
                @click.stop
              >
                @{{ activity.created_by_username }}
              </RouterLink>
            </div>
          </div>
        </article>
      </div>
    </div>

    <div v-else>
      <div v-if="pastActivities.length === 0" class="rounded-xl border border-dashed border-gray-300 py-16 text-center text-gray-400">
        暂无往期活动
      </div>
      <div v-else class="space-y-4">
        <article
          v-for="activity in pastActivities"
          :key="activity.id"
          class="cursor-pointer rounded-xl border border-gray-200 bg-white p-4 transition hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
          @click="$router.push(`/activities/${activity.id}`)"
        >
          <div class="mb-1 text-xs text-gray-400">{{ activity.date }}</div>
          <h3 class="mb-2 text-lg font-semibold">{{ activity.title }}</h3>
          <p class="mb-2 text-sm text-gray-500 line-clamp-2">{{ activity.summary }}</p>
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>{{ activity.type }}</span>
            <RouterLink
              v-if="activity.created_by_username"
              :to="`/u/${encodeURIComponent(activity.created_by_username)}`"
              class="text-teal-600 hover:underline"
              @click.stop
            >
              @{{ activity.created_by_username }}
            </RouterLink>
          </div>
        </article>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModal = false" />
      <div class="relative max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl dark:border-gray-800 dark:bg-gray-900">
        <h3 class="mb-6 text-xl font-semibold">{{ editingId ? '编辑活动' : '发布活动' }}</h3>

        <div class="space-y-4">
          <div class="h-32 cursor-pointer overflow-hidden rounded-lg border-2 border-dashed border-gray-300 bg-gray-50" @click="triggerUpload">
            <img v-if="form.cover_image" :src="form.cover_image" class="h-full w-full object-cover">
            <div v-else class="flex h-full items-center justify-center text-gray-400">上传封面图</div>
          </div>

          <input v-model="form.title" placeholder="活动名称" class="w-full rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">

          <div class="grid grid-cols-2 gap-3">
            <select v-model="form.type" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
              <option v-for="type in activityTypes" :key="type">{{ type }}</option>
            </select>
            <input v-model="form.date" type="date" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <div class="grid grid-cols-2 gap-3">
            <input v-model="form.location" placeholder="地点" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
            <input v-model.number="form.participants" type="number" placeholder="人数" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <textarea v-model="form.summary" rows="2" placeholder="活动简介" class="w-full rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500" />
          <textarea v-model="form.content" rows="4" placeholder="详细内容（支持 Markdown）" class="w-full rounded-lg border border-gray-200 px-3 py-2 font-mono text-sm outline-none focus:border-teal-500" />
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="px-4 py-2 text-gray-500" @click="showModal = false">取消</button>
          <button class="rounded-lg bg-teal-600 px-5 py-2 text-white disabled:opacity-60" :disabled="submitting" @click="submitActivity">
            {{ submitting ? '提交中...' : (editingId ? '保存修改' : '确认发布') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
