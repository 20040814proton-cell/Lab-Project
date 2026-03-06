<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ForumPostEditorModal from '~/components/forum/ForumPostEditorModal.vue'
import { apiFetch } from '~/logics/api'
import { buildSummaryFromMarkdown } from '~/logics/markdown-editor'
import { useUserStore } from '~/stores/user'

type ForumMode = 'all' | 'my_posts' | 'my_comments'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const errorMessage = ref('')
const currentMode = ref<ForumMode>('all')

const postList = ref<any[]>([])
const commentList = ref<any[]>([])

const showModal = ref(false)
const submitting = ref(false)
const query = ref('')
const tag = ref('')
const tagOptions = ref<string[]>([])
const page = ref(1)
const pageSize = 10
const hasMore = ref(true)
const moderating = ref(false)

const canModerate = computed(() => userStore.hasRole('teacher', 'superadmin'))
const isLoggedIn = computed(() => userStore.isTokenValid())
const currentUsername = computed(() => userStore.userInfo?.username || '')
const isCommentMode = computed(() => currentMode.value === 'my_comments')

const summary = (markdown: string, max = 180) =>
  buildSummaryFromMarkdown(markdown || '', max) || '暂无内容摘要'

function ensureLogin(actionText: string) {
  if (isLoggedIn.value)
    return true
  alert(`${actionText}需要先登录`)
  router.push('/login')
  return false
}

async function fetchTags() {
  try {
    const res = await apiFetch('/api/forum/tags', {}, { auth: false })
    if (res.ok)
      tagOptions.value = await res.json()
  } catch (error) {
    console.error(error)
  }
}

async function fetchData(reset = false) {
  if (reset) {
    page.value = 1
    hasMore.value = true
    postList.value = []
    commentList.value = []
  }

  if (!hasMore.value)
    return

  loading.value = true
  errorMessage.value = ''
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize),
    })
    if (query.value.trim())
      params.set('q', query.value.trim())
    if (!isCommentMode.value && tag.value.trim())
      params.set('tag', tag.value.trim())

    let url = `/api/forum?${params.toString()}`
    if (currentMode.value !== 'all') {
      if (!ensureLogin('查看个人内容')) {
        currentMode.value = 'all'
        return fetchData(true)
      }
      if (!currentUsername.value) {
        errorMessage.value = '无法识别当前账号，请重新登录'
        return
      }
      const username = encodeURIComponent(currentUsername.value)
      url = currentMode.value === 'my_posts'
        ? `/api/forum/users/${username}/posts?${params.toString()}`
        : `/api/forum/users/${username}/comments?${params.toString()}`
    }

    const res = await apiFetch(url, {}, { auth: false })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      errorMessage.value = err.detail || '加载失败，请稍后重试'
      return
    }

    const data = await res.json()
    if (currentMode.value === 'my_comments')
      commentList.value = [...commentList.value, ...data]
    else
      postList.value = [...postList.value, ...data]

    if (data.length < pageSize)
      hasMore.value = false
    else
      page.value += 1
  } catch (error) {
    console.error(error)
    errorMessage.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

function switchMode(mode: ForumMode) {
  if (mode !== 'all' && !ensureLogin('查看个人内容'))
    return
  currentMode.value = mode
  if (mode === 'my_comments')
    tag.value = ''
  fetchData(true)
}

function onSearch() {
  fetchData(true)
}

function applyTag(t: string) {
  tag.value = t
  fetchData(true)
}

function openCreate() {
  if (!ensureLogin('发帖'))
    return
  showModal.value = true
}

async function submit(payload: { title: string, content: string, tags: string[] }) {
  if (!ensureLogin('发帖'))
    return
  submitting.value = true
  try {
    const res = await apiFetch('/api/forum', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) {
      showModal.value = false
      await fetchData(true)
      await fetchTags()
    } else {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '发布失败')
    }
  } finally {
    submitting.value = false
  }
}

async function togglePinned(post: any) {
  if (!canModerate.value || moderating.value)
    return
  moderating.value = true
  try {
    await apiFetch(`/api/forum/${post.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_pinned: !post.is_pinned }),
    })
    await fetchData(true)
  } finally {
    moderating.value = false
  }
}

async function toggleFeatured(post: any) {
  if (!canModerate.value || moderating.value)
    return
  moderating.value = true
  try {
    await apiFetch(`/api/forum/${post.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_featured: !post.is_featured }),
    })
    await fetchData(true)
  } finally {
    moderating.value = false
  }
}

onMounted(async () => {
  await fetchTags()
  await fetchData(true)
})
</script>

<template>
  <div class="min-h-screen pt-24 px-6 pb-20 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-serif font-bold">论坛</h1>
        <p class="text-sm text-gray-400 mt-2">Forum & Discussions</p>
      </div>
      <button class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition" @click="openCreate">
        发布帖子
      </button>
    </div>

    <div class="mb-6 flex flex-wrap gap-2">
      <button
        class="text-sm px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700"
        :class="currentMode === 'all' ? 'bg-teal-50 text-teal-700 border-teal-200' : ''"
        @click="switchMode('all')"
      >
        全部
      </button>
      <button
        class="text-sm px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700"
        :class="currentMode === 'my_posts' ? 'bg-teal-50 text-teal-700 border-teal-200' : ''"
        @click="switchMode('my_posts')"
      >
        我的帖子
      </button>
      <button
        class="text-sm px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700"
        :class="currentMode === 'my_comments' ? 'bg-teal-50 text-teal-700 border-teal-200' : ''"
        @click="switchMode('my_comments')"
      >
        我的评论
      </button>
    </div>

    <div class="mb-6 grid grid-cols-1 md:grid-cols-3 gap-3">
      <input
        v-model="query"
        placeholder="搜索标题或内容"
        class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none"
        @keyup.enter="onSearch"
      >
      <input
        v-if="!isCommentMode"
        v-model="tag"
        placeholder="标签（精确匹配）"
        class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none"
        @keyup.enter="onSearch"
      >
      <div v-else class="hidden md:block" />
      <div class="flex gap-3">
        <button class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg" @click="onSearch">
          搜索
        </button>
        <button
          class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg"
          @click="() => { query = ''; tag = ''; onSearch() }"
        >
          重置
        </button>
      </div>
    </div>

    <div v-if="!isCommentMode && tagOptions.length" class="mb-6 flex flex-wrap gap-2">
      <button
        class="text-xs px-2.5 py-1 rounded border border-gray-200 dark:border-gray-700"
        :class="!tag ? 'bg-teal-50 text-teal-700 border-teal-200' : ''"
        @click="applyTag('')"
      >
        全部标签
      </button>
      <button
        v-for="t in tagOptions"
        :key="t"
        class="text-xs px-2.5 py-1 rounded border border-gray-200 dark:border-gray-700"
        :class="tag === t ? 'bg-teal-50 text-teal-700 border-teal-200' : ''"
        @click="applyTag(t)"
      >
        {{ t }}
      </button>
    </div>

    <div v-if="errorMessage" class="mb-6 p-3 rounded-lg border border-red-200 bg-red-50 text-sm text-red-600">
      {{ errorMessage }}
    </div>

    <div v-if="loading && postList.length === 0 && commentList.length === 0" class="text-center py-20 text-gray-400">
      <div class="i-carbon-circle-dash animate-spin text-3xl mb-2 mx-auto" />
      加载中...
    </div>

    <div v-else class="space-y-6">
      <template v-if="isCommentMode">
        <div class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800">
          <div
            v-for="comment in commentList"
            :key="comment.id"
            class="px-4 py-4 md:px-5 md:py-5"
          >
            <div class="flex items-center justify-between text-xs text-gray-400 mb-2">
              <span>{{ new Date(comment.created_at).toLocaleString('zh-CN') }}</span>
              <RouterLink class="text-teal-600 hover:underline" :to="`/forum/${comment.post_id}`">
                查看帖子：{{ comment.post_title }}
              </RouterLink>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
              {{ summary(comment.content, 180) }}
            </p>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800">
          <article
            v-for="post in postList"
            :key="post.id"
            class="group px-4 py-4 md:px-5 md:py-5 hover:bg-gray-50/80 dark:hover:bg-gray-800/40 transition cursor-pointer"
            @click="router.push(`/forum/${post.id}`)"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-gray-400 mb-1.5">
                  <span>{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</span>
                  <span v-if="post.author_name">·</span>
                  <RouterLink
                    v-if="post.author_name"
                    class="text-teal-600 hover:underline"
                    :to="`/u/${post.author_name}`"
                    @click.stop
                  >
                    {{ post.author_name }}
                  </RouterLink>
                  <span v-if="post.is_pinned" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">置顶</span>
                  <span v-if="post.is_featured" class="px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200">加精</span>
                </div>

                <h2 class="text-base md:text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-teal-600 transition line-clamp-2">
                  {{ post.title }}
                </h2>

                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300 line-clamp-3 leading-relaxed">
                  {{ summary(post.content, 180) }}
                </p>

                <div v-if="post.tags?.length" class="mt-3 flex flex-wrap gap-2">
                  <button
                    v-for="t in post.tags"
                    :key="t"
                    class="text-xs px-2 py-0.5 rounded bg-teal-50 text-teal-600 hover:bg-teal-100 transition"
                    @click.stop="applyTag(t)"
                  >
                    {{ t }}
                  </button>
                </div>
              </div>

              <div v-if="canModerate" class="flex items-center gap-2 shrink-0">
                <button
                  class="text-xs px-2.5 py-1 rounded border border-gray-200 dark:border-gray-700 hover:border-teal-400 hover:text-teal-600 transition"
                  @click.stop="togglePinned(post)"
                >
                  {{ post.is_pinned ? '取消置顶' : '置顶' }}
                </button>
                <button
                  class="text-xs px-2.5 py-1 rounded border border-gray-200 dark:border-gray-700 hover:border-teal-400 hover:text-teal-600 transition"
                  @click.stop="toggleFeatured(post)"
                >
                  {{ post.is_featured ? '取消加精' : '加精' }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </template>

      <div v-if="!loading && !isCommentMode && postList.length === 0" class="py-12 text-center text-sm text-gray-400">
        暂无帖子
      </div>
      <div v-if="!loading && isCommentMode && commentList.length === 0" class="py-12 text-center text-sm text-gray-400">
        暂无评论
      </div>

      <div class="pt-4 flex justify-center">
        <button
          v-if="hasMore"
          class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg"
          :disabled="loading"
          @click="fetchData()"
        >
          {{ loading ? '加载中...' : '加载更多' }}
        </button>
        <div v-else class="text-xs text-gray-400">没有更多了</div>
      </div>
    </div>

    <ForumPostEditorModal
      v-model="showModal"
      title="发布帖子"
      submit-text="发布"
      :submitting="submitting"
      @submit="submit"
    />
  </div>
</template>
