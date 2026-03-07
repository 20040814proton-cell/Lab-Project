<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch, withApiBase } from '~/logics/api'

interface PublicProfile {
  username: string
  name: string
  user_role: string
  role?: string
  avatar?: string
  bio?: string
  major?: string
  interests?: string[]
  research_areas?: string[]
  public_email?: string
}

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

const route = useRoute()
const username = computed(() => String(route.params.username || ''))

const loading = ref(true)
const errorMessage = ref('')
const profile = ref<PublicProfile | null>(null)
const contributions = ref<ContributionPayload | null>(null)

const roleLabelMap: Record<string, string> = {
  student: '学生',
  teacher: '教师',
  superadmin: '超级管理员',
}

const userRoleLabel = computed(() => {
  const role = String(profile.value?.user_role || '').toLowerCase()
  return roleLabelMap[role] || role || '用户'
})

function normalizeAvatar(url?: string) {
  return url ? withApiBase(url) : ''
}

async function bootstrap() {
  loading.value = true
  errorMessage.value = ''
  profile.value = null
  contributions.value = null

  try {
    const [profileRes, contributionRes] = await Promise.all([
      apiFetch(`/api/users/public/${encodeURIComponent(username.value)}`, {}, { auth: false }),
      apiFetch(`/api/users/public/${encodeURIComponent(username.value)}/contributions`, {}, { auth: false }),
    ])

    if (!profileRes.ok) {
      if (profileRes.status === 404)
        errorMessage.value = '用户不存在'
      else
        errorMessage.value = '加载用户信息失败'
      return
    }

    profile.value = await profileRes.json()

    if (contributionRes.ok)
      contributions.value = await contributionRes.json()
  }
  catch (error) {
    console.error(error)
    errorMessage.value = '网络异常，请稍后重试'
  }
  finally {
    loading.value = false
  }
}

watch(() => route.params.username, bootstrap)
onMounted(bootstrap)
</script>

<template>
  <div class="mx-auto min-h-screen max-w-6xl px-6 pb-20 pt-24">
    <div v-if="loading" class="py-20 text-center text-gray-400">
      <div class="i-carbon-circle-dash mx-auto mb-2 animate-spin text-3xl" />
      Loading...
    </div>

    <div v-else-if="errorMessage" class="py-20 text-center">
      <p class="mb-4 text-red-500">{{ errorMessage }}</p>
      <RouterLink to="/forum" class="text-teal-600 hover:underline">返回论坛</RouterLink>
    </div>

    <template v-else-if="profile">
      <section class="mb-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
        <div class="flex flex-col gap-5 md:flex-row md:items-start">
          <div class="h-24 w-24 overflow-hidden rounded-full border-4 border-teal-50 bg-gray-100 shadow-sm dark:border-teal-900/30 dark:bg-gray-800">
            <img v-if="profile.avatar" :src="normalizeAvatar(profile.avatar)" class="h-full w-full object-cover">
            <div v-else class="i-carbon-user flex h-full w-full items-center justify-center text-4xl text-gray-300" />
          </div>

          <div class="min-w-0 flex-1">
            <div class="mb-1 flex flex-wrap items-center gap-2">
              <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ profile.name || profile.username }}</h1>
              <span class="rounded-md bg-teal-50 px-2 py-0.5 text-xs text-teal-700">{{ userRoleLabel }}</span>
            </div>
            <p class="text-sm text-gray-500">@{{ profile.username }}</p>

            <p v-if="profile.bio" class="mt-3 text-sm text-gray-600 dark:text-gray-300">{{ profile.bio }}</p>

            <div class="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
              <span v-if="profile.major" class="rounded-md border border-gray-200 px-2 py-1">专业: {{ profile.major }}</span>
              <span v-if="profile.public_email" class="rounded-md border border-gray-200 px-2 py-1">邮箱: {{ profile.public_email }}</span>
            </div>

            <div v-if="profile.interests?.length" class="mt-3 flex flex-wrap gap-2">
              <span v-for="tag in profile.interests" :key="tag" class="rounded-full border border-teal-100 bg-teal-50 px-2 py-0.5 text-xs text-teal-700">
                {{ tag }}
              </span>
            </div>

            <div v-if="profile.research_areas?.length" class="mt-3 flex flex-wrap gap-2">
              <span v-for="area in profile.research_areas" :key="area" class="rounded-full border border-amber-100 bg-amber-50 px-2 py-0.5 text-xs text-amber-700">
                {{ area }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section class="mb-6 grid grid-cols-2 gap-3 md:grid-cols-5" v-if="contributions">
        <div class="rounded-lg border border-gray-200 bg-white p-3 text-center dark:border-gray-800 dark:bg-gray-900">
          <p class="text-xs text-gray-500">论坛帖子</p>
          <p class="mt-1 text-lg font-bold">{{ contributions.counts.forum_posts }}</p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-3 text-center dark:border-gray-800 dark:bg-gray-900">
          <p class="text-xs text-gray-500">论坛评论</p>
          <p class="mt-1 text-lg font-bold">{{ contributions.counts.forum_comments }}</p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-3 text-center dark:border-gray-800 dark:bg-gray-900">
          <p class="text-xs text-gray-500">学术活动</p>
          <p class="mt-1 text-lg font-bold">{{ contributions.counts.activities }}</p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-3 text-center dark:border-gray-800 dark:bg-gray-900">
          <p class="text-xs text-gray-500">项目记录</p>
          <p class="mt-1 text-lg font-bold">{{ contributions.counts.projects }}</p>
        </div>
        <div class="rounded-lg border border-gray-200 bg-white p-3 text-center dark:border-gray-800 dark:bg-gray-900">
          <p class="text-xs text-gray-500">软件资源</p>
          <p class="mt-1 text-lg font-bold">{{ contributions.counts.software }}</p>
        </div>
      </section>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2" v-if="contributions">
        <section class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold">论坛帖子</h2>
            <RouterLink :to="`/forum?creator=${encodeURIComponent(username)}`" class="text-sm text-teal-600 hover:underline">查看更多</RouterLink>
          </div>
          <div v-if="contributions.recent_forum_posts.length === 0" class="text-sm text-gray-400">暂无帖子</div>
          <div v-else class="space-y-3">
            <article v-for="item in contributions.recent_forum_posts" :key="item.id" class="border-b border-gray-100 pb-3 last:border-0 last:pb-0 dark:border-gray-800">
              <p class="mb-1 text-xs text-gray-400">{{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</p>
              <RouterLink :to="`/forum/${item.id}`" class="font-medium hover:text-teal-600">{{ item.title }}</RouterLink>
            </article>
          </div>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold">论坛评论</h2>
            <RouterLink :to="`/forum?creator=${encodeURIComponent(username)}`" class="text-sm text-teal-600 hover:underline">查看更多</RouterLink>
          </div>
          <div v-if="contributions.recent_forum_comments.length === 0" class="text-sm text-gray-400">暂无评论</div>
          <div v-else class="space-y-3">
            <article v-for="item in contributions.recent_forum_comments" :key="item.id" class="border-b border-gray-100 pb-3 last:border-0 last:pb-0 dark:border-gray-800">
              <p class="mb-1 text-xs text-gray-400">{{ new Date(item.created_at).toLocaleString('zh-CN') }}</p>
              <RouterLink :to="`/forum/${item.post_id}`" class="font-medium hover:text-teal-600">{{ item.post_title }}</RouterLink>
              <p class="mt-1 line-clamp-2 text-sm text-gray-500">{{ item.content_preview }}</p>
            </article>
          </div>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold">学术活动</h2>
            <RouterLink :to="`/activities?creator=${encodeURIComponent(username)}`" class="text-sm text-teal-600 hover:underline">查看更多</RouterLink>
          </div>
          <div v-if="contributions.recent_activities.length === 0" class="text-sm text-gray-400">暂无活动</div>
          <div v-else class="space-y-3">
            <article v-for="item in contributions.recent_activities" :key="item.id" class="border-b border-gray-100 pb-3 last:border-0 last:pb-0 dark:border-gray-800">
              <p class="mb-1 text-xs text-gray-400">{{ item.date }}</p>
              <RouterLink :to="`/activities/${item.id}`" class="font-medium hover:text-teal-600">{{ item.title }}</RouterLink>
              <p class="mt-1 text-xs text-gray-500">{{ item.type }}</p>
            </article>
          </div>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold">项目与软件</h2>
            <div class="flex gap-3 text-sm">
              <RouterLink :to="`/projects?creator=${encodeURIComponent(username)}`" class="text-teal-600 hover:underline">项目</RouterLink>
              <RouterLink :to="`/downloads?creator=${encodeURIComponent(username)}`" class="text-teal-600 hover:underline">软件</RouterLink>
            </div>
          </div>

          <div>
            <h3 class="mb-2 text-sm font-medium text-gray-600">最近项目</h3>
            <div v-if="contributions.recent_projects.length === 0" class="mb-4 text-sm text-gray-400">暂无项目</div>
            <div v-else class="mb-4 space-y-2">
              <article v-for="item in contributions.recent_projects" :key="item.id" class="border-b border-gray-100 pb-2 last:border-0 last:pb-0 dark:border-gray-800">
                <p class="text-xs text-gray-400">{{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</p>
                <RouterLink :to="`/projects?creator=${encodeURIComponent(username)}`" class="text-sm font-medium hover:text-teal-600">{{ item.title }}</RouterLink>
              </article>
            </div>
          </div>

          <div>
            <h3 class="mb-2 text-sm font-medium text-gray-600">最近软件</h3>
            <div v-if="contributions.recent_software.length === 0" class="text-sm text-gray-400">暂无软件</div>
            <div v-else class="space-y-2">
              <article v-for="item in contributions.recent_software" :key="item.id" class="border-b border-gray-100 pb-2 last:border-0 last:pb-0 dark:border-gray-800">
                <p class="text-xs text-gray-400">{{ new Date(item.upload_date).toLocaleDateString('zh-CN') }}</p>
                <RouterLink :to="`/downloads?creator=${encodeURIComponent(username)}`" class="text-sm font-medium hover:text-teal-600">{{ item.name }} <span class="text-xs text-gray-400">{{ item.version }}</span></RouterLink>
              </article>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
