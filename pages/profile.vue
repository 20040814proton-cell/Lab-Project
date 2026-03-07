<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { apiFetch, withApiBase } from '~/logics/api'
import { useUserStore } from '~/stores/user'

interface ContributionPayload {
  counts: {
    forum_posts: number
    forum_comments: number
    activities: number
    projects: number
    software: number
  }
  recent_forum_posts: Array<{ id: string, title: string, created_at: string }>
  recent_forum_comments: Array<{ id: string, post_id: string, post_title: string, created_at: string, content_preview: string }>
  recent_activities: Array<{ id: string, title: string, date: string, type: string }>
  recent_projects: Array<{ id: string, title: string, status: string, created_at: string }>
  recent_software: Array<{ id: string, name: string, version: string, upload_date: string }>
}

const userStore = useUserStore()

const loading = ref(false)
const saving = ref(false)
const contributionLoading = ref(false)
const contributions = ref<ContributionPayload | null>(null)

const form = ref({
  avatar: '',
  major: '',
  interests: [] as string[],
  bio: '',
  public_email: '',
  title: '',
  office: '',
  research_areas_str: '',
})

const fileInput = ref<HTMLInputElement | null>(null)
const tagInput = ref('')

const isTeacher = computed(() => userStore.hasRole('teacher', 'superadmin'))
const isSuperadmin = computed(() => userStore.hasRole('superadmin'))
const profileUsername = computed(() => String(userStore.userInfo?.username || ''))

function triggerUpload() {
  fileInput.value?.click()
}

async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.[0])
    return

  const formData = new FormData()
  formData.append('file', input.files[0])

  loading.value = true
  try {
    const res = await apiFetch('/api/upload/', {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      alert('Upload failed')
      return
    }
    const data = await res.json()
    form.value.avatar = withApiBase(data.url)
  }
  catch (error) {
    console.error(error)
    alert('Upload error')
  }
  finally {
    loading.value = false
  }
}

function addTag() {
  const value = tagInput.value.trim()
  if (!value)
    return
  if (!form.value.interests.includes(value))
    form.value.interests.push(value)
  tagInput.value = ''
}

function removeTag(tag: string) {
  form.value.interests = form.value.interests.filter(item => item !== tag)
}

async function fetchContributions(username: string) {
  if (!username)
    return

  contributionLoading.value = true
  try {
    const res = await apiFetch(`/api/users/public/${encodeURIComponent(username)}/contributions`, {}, { auth: false })
    if (res.ok)
      contributions.value = await res.json()
  }
  catch (error) {
    console.error(error)
  }
  finally {
    contributionLoading.value = false
  }
}

async function fetchProfile() {
  loading.value = true
  try {
    const res = await apiFetch('/api/users/me')
    if (!res.ok)
      return

    const data = await res.json()
    userStore.setUserInfo(data)

    form.value.avatar = data.avatar ? withApiBase(data.avatar) : ''
    form.value.major = data.major || ''
    form.value.interests = data.interests || []
    form.value.bio = data.bio || ''
    form.value.public_email = data.public_email || ''

    if (isTeacher.value) {
      form.value.title = data.title || ''
      form.value.office = data.office || ''
      form.value.research_areas_str = (data.research_areas || []).join(', ')
    }

    await fetchContributions(String(data.username || ''))
  }
  catch (error) {
    console.error('Failed to fetch profile', error)
  }
  finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  try {
    const payload: any = {
      avatar: form.value.avatar,
      major: form.value.major,
      interests: form.value.interests,
      bio: form.value.bio,
    }

    if (!isSuperadmin.value)
      payload.public_email = form.value.public_email

    if (isTeacher.value) {
      payload.title = form.value.title
      payload.office = form.value.office
      payload.research_areas = form.value.research_areas_str
        ? form.value.research_areas_str.split(/[,，]/).map((item: string) => item.trim()).filter(Boolean)
        : []
    }

    const res = await apiFetch('/api/users/me', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || 'Failed to save')
      return
    }

    const data = await res.json()
    userStore.setUserInfo(data)
    await fetchProfile()
    alert('保存成功')
  }
  catch (error) {
    console.error(error)
    alert('Failed to save')
  }
  finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>

<template>
  <div class="mx-auto min-h-screen max-w-6xl px-6 pb-20 pt-24">
    <h1 class="mb-8 text-3xl font-serif font-bold text-gray-900 dark:text-gray-100">
      <span class="border-l-4 border-teal-500 pl-4">个人资料</span>
    </h1>

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
        <h2 class="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Profile Preview</h2>

        <div class="mx-auto mb-4 h-24 w-24 cursor-pointer overflow-hidden rounded-full border-4 border-teal-50 bg-gray-100" @click="triggerUpload">
          <img v-if="form.avatar || userStore.userInfo?.avatar" :src="form.avatar || userStore.userInfo?.avatar" class="h-full w-full object-cover">
          <div v-else class="i-carbon-user flex h-full w-full items-center justify-center text-4xl text-gray-300" />
        </div>
        <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="handleUpload">

        <h3 class="text-center text-xl font-bold text-gray-900 dark:text-gray-100">{{ userStore.userInfo?.name || 'User' }}</h3>
        <p class="mt-1 text-center text-sm text-gray-500">@{{ userStore.userInfo?.username || '-' }}</p>

        <div class="my-4 h-px bg-gray-100 dark:bg-gray-800" />

        <p class="text-center text-sm text-teal-600 dark:text-teal-400">{{ form.major || 'Major not set' }}</p>
        <p v-if="form.public_email && !isSuperadmin" class="mt-2 text-center text-xs text-gray-500">{{ form.public_email }}</p>

        <div class="mt-4 flex flex-wrap justify-center gap-2">
          <span v-for="tag in form.interests" :key="tag" class="rounded-full border border-teal-100 bg-teal-50 px-2 py-0.5 text-xs text-teal-700">
            {{ tag }}
          </span>
          <span v-if="form.interests.length === 0" class="text-xs italic text-gray-400">No tags</span>
        </div>
      </section>

      <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900 lg:col-span-2">
        <h2 class="mb-6 text-xl font-semibold">编辑信息</h2>

        <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-medium text-gray-600">专业 / 研究方向</label>
            <input v-model="form.major" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900">
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-medium text-gray-600">个人简介</label>
            <textarea v-model="form.bio" rows="3" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900" />
          </div>

          <div v-if="!isSuperadmin" class="md:col-span-2">
            <label class="mb-2 block text-sm font-medium text-gray-600">公开邮箱</label>
            <input v-model="form.public_email" type="email" placeholder="public@example.com" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900">
          </div>

          <template v-if="isTeacher">
            <div>
              <label class="mb-2 block text-sm font-medium text-gray-600">职称</label>
              <input v-model="form.title" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900">
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-gray-600">办公室</label>
              <input v-model="form.office" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900">
            </div>
            <div class="md:col-span-2">
              <label class="mb-2 block text-sm font-medium text-gray-600">研究方向（逗号分隔）</label>
              <input v-model="form.research_areas_str" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900">
            </div>
          </template>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-medium text-gray-600">兴趣标签（回车添加）</label>
            <div class="mb-2 flex flex-wrap gap-2">
              <button
                v-for="tag in form.interests"
                :key="tag"
                class="rounded-full border border-teal-100 bg-teal-50 px-2.5 py-1 text-xs text-teal-700"
                @click.prevent="removeTag(tag)"
              >
                {{ tag }} ×
              </button>
            </div>
            <input v-model="tagInput" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-900" @keydown.enter.prevent="addTag">
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button class="rounded-lg bg-teal-600 px-6 py-2.5 text-white transition hover:bg-teal-700 disabled:opacity-60" :disabled="saving" @click="saveProfile">
            {{ saving ? 'Saving...' : '保存修改' }}
          </button>
        </div>
      </section>
    </div>

    <section class="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <div class="mb-5 flex items-center justify-between">
        <h2 class="text-xl font-semibold">我的贡献概览</h2>
        <RouterLink v-if="profileUsername" :to="`/u/${encodeURIComponent(profileUsername)}`" class="text-sm text-teal-600 hover:underline">
          查看公开主页
        </RouterLink>
      </div>

      <div v-if="contributionLoading" class="py-8 text-sm text-gray-400">Loading contributions...</div>
      <template v-else-if="contributions">
        <div class="mb-5 grid grid-cols-2 gap-3 md:grid-cols-5">
          <div class="rounded-lg border border-gray-100 bg-gray-50 p-3 text-center dark:border-gray-800 dark:bg-gray-800/60">
            <p class="text-xs text-gray-500">论坛帖子</p>
            <p class="mt-1 text-lg font-bold">{{ contributions.counts.forum_posts }}</p>
          </div>
          <div class="rounded-lg border border-gray-100 bg-gray-50 p-3 text-center dark:border-gray-800 dark:bg-gray-800/60">
            <p class="text-xs text-gray-500">论坛评论</p>
            <p class="mt-1 text-lg font-bold">{{ contributions.counts.forum_comments }}</p>
          </div>
          <div class="rounded-lg border border-gray-100 bg-gray-50 p-3 text-center dark:border-gray-800 dark:bg-gray-800/60">
            <p class="text-xs text-gray-500">学术活动</p>
            <p class="mt-1 text-lg font-bold">{{ contributions.counts.activities }}</p>
          </div>
          <div class="rounded-lg border border-gray-100 bg-gray-50 p-3 text-center dark:border-gray-800 dark:bg-gray-800/60">
            <p class="text-xs text-gray-500">项目记录</p>
            <p class="mt-1 text-lg font-bold">{{ contributions.counts.projects }}</p>
          </div>
          <div class="rounded-lg border border-gray-100 bg-gray-50 p-3 text-center dark:border-gray-800 dark:bg-gray-800/60">
            <p class="text-xs text-gray-500">软件资源</p>
            <p class="mt-1 text-lg font-bold">{{ contributions.counts.software }}</p>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <RouterLink v-if="profileUsername" :to="`/u/${encodeURIComponent(profileUsername)}`" class="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:border-teal-400 hover:text-teal-600">
            公开主页
          </RouterLink>
          <RouterLink v-if="profileUsername" :to="`/forum?creator=${encodeURIComponent(profileUsername)}`" class="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:border-teal-400 hover:text-teal-600">
            论坛帖子
          </RouterLink>
          <RouterLink v-if="profileUsername" :to="`/activities?creator=${encodeURIComponent(profileUsername)}`" class="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:border-teal-400 hover:text-teal-600">
            学术活动
          </RouterLink>
          <RouterLink v-if="profileUsername" :to="`/projects?creator=${encodeURIComponent(profileUsername)}`" class="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:border-teal-400 hover:text-teal-600">
            项目记录
          </RouterLink>
          <RouterLink v-if="profileUsername" :to="`/downloads?creator=${encodeURIComponent(profileUsername)}`" class="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:border-teal-400 hover:text-teal-600">
            软件资源
          </RouterLink>
        </div>
      </template>
      <div v-else class="py-8 text-sm text-gray-400">暂无贡献数据</div>
    </section>
  </div>
</template>
