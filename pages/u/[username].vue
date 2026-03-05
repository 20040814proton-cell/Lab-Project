<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch } from '~/logics/api'
import { buildSummaryFromMarkdown } from '~/logics/markdown-editor'

const route = useRoute()
const username = computed(() => String(route.params.username || ''))

const loadingProfile = ref(true)
const profileError = ref('')
const profile = ref<any>(null)

const posts = ref<any[]>([])
const comments = ref<any[]>([])

const postsLoading = ref(false)
const commentsLoading = ref(false)

const postPage = ref(1)
const commentPage = ref(1)
const pageSize = 5
const postHasMore = ref(true)
const commentHasMore = ref(true)

const roleLabelMap: Record<string, string> = {
  student: '学生',
  teacher: '教师',
  superadmin: '超级管理员',
}

const userRoleLabel = computed(() => {
  const rawRole = String(profile.value?.user_role || '').toLowerCase()
  return roleLabelMap[rawRole] || rawRole || '用户'
})

const summary = (markdown: string, max = 120) =>
  buildSummaryFromMarkdown(markdown || '', max) || '暂无内容'

async function fetchProfile() {
  loadingProfile.value = true
  profileError.value = ''
  profile.value = null
  try {
    const res = await apiFetch(`/api/users/public/${encodeURIComponent(username.value)}`, {}, { auth: false })
    if (res.ok)
      profile.value = await res.json()
    else if (res.status === 404)
      profileError.value = '用户不存在'
    else
      profileError.value = '加载用户信息失败'
  } catch (error) {
    console.error(error)
    profileError.value = '网络异常，请稍后重试'
  } finally {
    loadingProfile.value = false
  }
}

async function fetchPosts(reset = false) {
  if (reset) {
    posts.value = []
    postPage.value = 1
    postHasMore.value = true
  }
  if (!postHasMore.value)
    return
  postsLoading.value = true
  try {
    const params = new URLSearchParams({
      page: String(postPage.value),
      page_size: String(pageSize),
    })
    const res = await apiFetch(`/api/forum/users/${encodeURIComponent(username.value)}/posts?${params.toString()}`, {}, { auth: false })
    if (!res.ok) {
      postHasMore.value = false
      return
    }
    const data = await res.json()
    posts.value = [...posts.value, ...data]
    if (data.length < pageSize)
      postHasMore.value = false
    else
      postPage.value += 1
  } finally {
    postsLoading.value = false
  }
}

async function fetchComments(reset = false) {
  if (reset) {
    comments.value = []
    commentPage.value = 1
    commentHasMore.value = true
  }
  if (!commentHasMore.value)
    return
  commentsLoading.value = true
  try {
    const params = new URLSearchParams({
      page: String(commentPage.value),
      page_size: String(pageSize),
    })
    const res = await apiFetch(`/api/forum/users/${encodeURIComponent(username.value)}/comments?${params.toString()}`, {}, { auth: false })
    if (!res.ok) {
      commentHasMore.value = false
      return
    }
    const data = await res.json()
    comments.value = [...comments.value, ...data]
    if (data.length < pageSize)
      commentHasMore.value = false
    else
      commentPage.value += 1
  } finally {
    commentsLoading.value = false
  }
}

async function bootstrap() {
  await fetchProfile()
  if (!profileError.value) {
    await Promise.all([
      fetchPosts(true),
      fetchComments(true),
    ])
  }
}

watch(() => route.params.username, () => {
  bootstrap()
})

onMounted(() => {
  bootstrap()
})
</script>

<template>
  <div class="min-h-screen pt-24 px-6 pb-20 max-w-6xl mx-auto">
    <div v-if="loadingProfile" class="py-20 text-center text-gray-400">
      <div class="i-carbon-circle-dash animate-spin text-3xl mb-2 mx-auto" />
      加载中...
    </div>

    <div v-else-if="profileError" class="py-20 text-center">
      <p class="text-red-500 mb-3">{{ profileError }}</p>
      <RouterLink to="/forum" class="text-teal-600 hover:underline">返回论坛</RouterLink>
    </div>

    <template v-else>
      <div class="mb-8 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div class="flex items-start gap-5">
          <div class="w-18 h-18 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden flex items-center justify-center">
            <img v-if="profile?.avatar" :src="profile.avatar" class="w-full h-full object-cover">
            <div v-else class="i-carbon-user text-3xl text-gray-400" />
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-2xl font-bold">{{ profile?.name || profile?.username }}</h1>
              <span class="text-xs px-2 py-0.5 rounded bg-teal-50 text-teal-700">{{ userRoleLabel }}</span>
            </div>
            <p class="text-sm text-gray-400 mt-1">@{{ profile?.username }}</p>
            <p v-if="profile?.bio" class="mt-3 text-sm text-gray-600 dark:text-gray-300">
              {{ profile.bio }}
            </p>
            <p v-if="profile?.major" class="mt-2 text-sm text-gray-500">
              研究/专业：{{ profile.major }}
            </p>
            <div v-if="profile?.interests?.length" class="mt-3 flex flex-wrap gap-2">
              <span v-for="item in profile.interests" :key="item" class="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">
                {{ item }}
              </span>
            </div>
            <div v-if="profile?.research_areas?.length" class="mt-3 flex flex-wrap gap-2">
              <span v-for="item in profile.research_areas" :key="item" class="text-xs px-2 py-0.5 rounded bg-amber-50 text-amber-700">
                {{ item }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section class="rounded-2xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
          <h2 class="text-lg font-bold mb-4">最近帖子</h2>
          <div v-if="posts.length === 0" class="text-sm text-gray-400 py-4">暂无帖子</div>
          <div v-else class="space-y-4">
            <article v-for="item in posts" :key="item.id" class="pb-4 border-b border-gray-100 dark:border-gray-800 last:border-0 last:pb-0">
              <div class="text-xs text-gray-400 mb-1">
                {{ new Date(item.created_at).toLocaleDateString('zh-CN') }}
              </div>
              <RouterLink :to="`/forum/${item.id}`" class="font-semibold hover:text-teal-600">
                {{ item.title }}
              </RouterLink>
              <p class="text-sm text-gray-500 mt-2 line-clamp-2">{{ summary(item.content) }}</p>
            </article>
          </div>
          <div class="mt-4 flex justify-center">
            <button
              v-if="postHasMore"
              class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg"
              :disabled="postsLoading"
              @click="fetchPosts()"
            >
              {{ postsLoading ? '加载中...' : '加载更多帖子' }}
            </button>
            <span v-else class="text-xs text-gray-400">没有更多了</span>
          </div>
        </section>

        <section class="rounded-2xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
          <h2 class="text-lg font-bold mb-4">最近评论</h2>
          <div v-if="comments.length === 0" class="text-sm text-gray-400 py-4">暂无评论</div>
          <div v-else class="space-y-4">
            <article v-for="item in comments" :key="item.id" class="pb-4 border-b border-gray-100 dark:border-gray-800 last:border-0 last:pb-0">
              <div class="text-xs text-gray-400 mb-1">
                {{ new Date(item.created_at).toLocaleString('zh-CN') }}
              </div>
              <RouterLink :to="`/forum/${item.post_id}`" class="font-semibold hover:text-teal-600">
                {{ item.post_title }}
              </RouterLink>
              <p class="text-sm text-gray-500 mt-2 line-clamp-3">{{ summary(item.content, 180) }}</p>
            </article>
          </div>
          <div class="mt-4 flex justify-center">
            <button
              v-if="commentHasMore"
              class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg"
              :disabled="commentsLoading"
              @click="fetchComments()"
            >
              {{ commentsLoading ? '加载中...' : '加载更多评论' }}
            </button>
            <span v-else class="text-xs text-gray-400">没有更多了</span>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
