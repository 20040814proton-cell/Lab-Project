<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { MdCatalog, MdPreview } from 'md-editor-v3'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ForumCommentEditor from '~/components/forum/ForumCommentEditor.vue'
import ForumPostEditorModal from '~/components/forum/ForumPostEditorModal.vue'
import { isDark } from '~/logics'
import { apiFetch } from '~/logics/api'
import { goBackOr } from '~/logics/navigation'
import { useUserStore } from '~/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const md = new MarkdownIt()

const loading = ref(true)
const loadError = ref('')
const post = ref<any>(null)
const comments = ref<any[]>([])

const submitting = ref(false)
const newComment = ref('')
const commentLoading = ref(false)
const commentPage = ref(1)
const commentPageSize = 20
const commentHasMore = ref(true)

const editModal = ref(false)
const editing = ref(false)
const moderating = ref(false)
const mobileTocOpen = ref(false)
const likingPost = ref(false)
const likingCommentIds = ref<Set<string>>(new Set())

const editorId = 'forum-preview'
const scrollElement = typeof document !== 'undefined' ? document.documentElement : undefined
const mdTheme = computed(() => (isDark.value ? 'dark' : 'light'))

const isLoggedIn = computed(() => userStore.isTokenValid())
const isAuthor = computed(() => {
  const username = userStore.userInfo?.username
  return Boolean(username && (post.value?.author_name === username || String(post.value?.author_id || '') === username))
})
const canModerate = computed(() => userStore.hasRole('teacher', 'superadmin'))
const canEditPost = computed(() => isAuthor.value || canModerate.value)

function normalizeAuthorText(value: unknown) {
  if (typeof value !== 'string')
    return ''
  return value.trim()
}

function isOpaqueAuthor(value: string) {
  if (!value)
    return true
  const isMongoObjectId = /^[a-f0-9]{24}$/i.test(value)
  const isUuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(value)
  const isLongDigits = /^\d{6,}$/.test(value)
  return isMongoObjectId || isUuid || isLongDigits
}

function displayAuthor(item: any) {
  const username = normalizeAuthorText(item?.author_name)
  const displayName = normalizeAuthorText(item?.author_display_name)
  const authorId = normalizeAuthorText(item?.author_id)

  if (displayName && !isOpaqueAuthor(displayName))
    return displayName
  if (username)
    return username
  if (displayName)
    return displayName
  if (authorId && !isOpaqueAuthor(authorId))
    return authorId
  return 'Unknown user'
}

function authorUsername(item: any) {
  const username = normalizeAuthorText(item?.author_name)
  return username && !isOpaqueAuthor(username) ? username : ''
}

const editInitialData = computed(() => {
  if (!post.value)
    return null
  return {
    title: post.value.title || '',
    content: post.value.content || '',
    tags: Array.isArray(post.value.tags) ? post.value.tags : [],
  }
})

function canDeleteComment(comment: any) {
  const username = userStore.userInfo?.username
  return Boolean((username && (comment.author_name === username || String(comment.author_id || '') === username)) || canModerate.value)
}

const renderComment = (content: string) => md.render(content || '')
const commentCollapseThreshold = 220
const expandedCommentIds = ref<Set<string>>(new Set())

function commentToPlainText(content: string) {
  return (content || '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[[^\]]+\]\([^)]*\)/g, '$1')
    .replace(/[`*_>#-]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function isLongComment(content: string) {
  return commentToPlainText(content).length > commentCollapseThreshold
}

function isCommentExpanded(commentId: string) {
  return expandedCommentIds.value.has(commentId)
}

function toggleCommentExpanded(commentId: string) {
  const next = new Set(expandedCommentIds.value)
  if (next.has(commentId))
    next.delete(commentId)
  else
    next.add(commentId)
  expandedCommentIds.value = next
}

function ensureLogin(actionText: string) {
  if (isLoggedIn.value)
    return true
  alert(`${actionText}需要先登录`)
  router.push('/login')
  return false
}

function goBack() {
  goBackOr(router, '/forum')
}

function setCommentLiking(commentId: string, value: boolean) {
  const next = new Set(likingCommentIds.value)
  if (value)
    next.add(commentId)
  else
    next.delete(commentId)
  likingCommentIds.value = next
}

function isCommentLiking(commentId: string) {
  return likingCommentIds.value.has(commentId)
}

async function fetchPost() {
  const res = await apiFetch(`/api/forum/${route.params.id}`)
  if (res.ok) {
    post.value = await res.json()
    mobileTocOpen.value = false
    loadError.value = ''
    return
  }
  if (res.status === 404)
    loadError.value = '帖子不存在或已删除'
  else
    loadError.value = '加载帖子失败，请稍后重试'
}

async function fetchComments(reset = false) {
  if (reset) {
    commentPage.value = 1
    comments.value = []
    commentHasMore.value = true
    expandedCommentIds.value = new Set()
  }
  if (!commentHasMore.value)
    return

  commentLoading.value = true
  try {
    const res = await apiFetch(`/api/forum/${route.params.id}/comments?page=${commentPage.value}&page_size=${commentPageSize}`)
    if (res.ok) {
      const data = await res.json()
      comments.value = [...comments.value, ...data]
      if (data.length < commentPageSize)
        commentHasMore.value = false
      else
        commentPage.value += 1
    }
  }
  finally {
    commentLoading.value = false
  }
}

async function togglePostLike() {
  if (!post.value || likingPost.value)
    return
  if (!ensureLogin('点赞'))
    return

  likingPost.value = true
  try {
    const res = await apiFetch(`/api/forum/${route.params.id}/like`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '点赞失败')
      return
    }
    const data = await res.json()
    post.value.like_count = data.like_count
    post.value.liked_by_me = data.liked_by_me
  }
  finally {
    likingPost.value = false
  }
}

async function toggleCommentLike(comment: any) {
  if (!comment?.id || isCommentLiking(comment.id))
    return
  if (!ensureLogin('点赞'))
    return

  setCommentLiking(comment.id, true)
  try {
    const res = await apiFetch(`/api/forum/comments/${comment.id}/like`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '点赞失败')
      return
    }
    const data = await res.json()
    comment.like_count = data.like_count
    comment.liked_by_me = data.liked_by_me
  }
  finally {
    setCommentLiking(comment.id, false)
  }
}

async function submitComment() {
  if (!ensureLogin('发表评论'))
    return
  if (!newComment.value.trim())
    return

  submitting.value = true
  try {
    const res = await apiFetch(`/api/forum/${route.params.id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: newComment.value }),
    })
    if (res.ok) {
      newComment.value = ''
      await fetchComments(true)
    }
    else {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '评论发布失败')
    }
  }
  finally {
    submitting.value = false
  }
}

function openEdit() {
  if (!post.value)
    return
  editModal.value = true
}

async function updatePost(payload: { title: string, content: string, tags: string[] }) {
  editing.value = true
  try {
    const res = await apiFetch(`/api/forum/${route.params.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) {
      editModal.value = false
      await fetchPost()
    }
    else {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '更新失败')
    }
  }
  finally {
    editing.value = false
  }
}

async function deletePost() {
  if (!confirm('确认删除此帖子？'))
    return
  const res = await apiFetch(`/api/forum/${route.params.id}`, { method: 'DELETE' })
  if (res.ok)
    router.push('/forum')
  else
    alert('删除失败')
}

async function deleteComment(id: string) {
  if (!confirm('确认删除该评论？'))
    return
  const res = await apiFetch(`/api/forum/comments/${id}`, { method: 'DELETE' })
  if (res.ok)
    await fetchComments(true)
  else
    alert('删除失败')
}

async function togglePinned() {
  if (!canModerate.value || moderating.value || !post.value)
    return
  moderating.value = true
  try {
    await apiFetch(`/api/forum/${route.params.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_pinned: !post.value.is_pinned }),
    })
    await fetchPost()
  }
  finally {
    moderating.value = false
  }
}

async function toggleFeatured() {
  if (!canModerate.value || moderating.value || !post.value)
    return
  moderating.value = true
  try {
    await apiFetch(`/api/forum/${route.params.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_featured: !post.value.is_featured }),
    })
    await fetchPost()
  }
  finally {
    moderating.value = false
  }
}

onMounted(async () => {
  loading.value = true
  await fetchPost()
  if (!loadError.value)
    await fetchComments(true)
  loading.value = false
})
</script>

<template>
  <div class="reader-page forum-detail-page min-h-screen pt-24 px-6 pb-20 max-w-4xl mx-auto">
    <div v-if="loading" class="py-20 text-center text-gray-400">
      <div class="i-carbon-circle-dash animate-spin text-3xl mb-2 mx-auto" />
      加载中...
    </div>

    <div v-else-if="loadError" class="py-20 text-center">
      <p class="text-red-500 mb-4">
        {{ loadError }}
      </p>
      <RouterLink to="/forum" class="text-teal-600 hover:underline">
        返回论坛
      </RouterLink>
    </div>

    <div v-else-if="post">
      <button class="reader-back-button mb-4 text-sm transition flex items-center gap-1.5" @click="goBack">
        <span class="i-carbon-arrow-left" />
        返回上一个页面
      </button>

      <header class="reader-surface reader-surface--primary rounded-2xl px-5 py-6 md:px-7 mb-6 reader-motion-enter">
        <div class="reader-meta text-xs mb-2 flex flex-wrap items-center gap-x-1.5 gap-y-1">
          <span>{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</span>
          <span>·</span>
          <RouterLink
            v-if="authorUsername(post)"
            class="text-teal-600 hover:underline"
            :to="`/u/${encodeURIComponent(authorUsername(post))}`"
          >
            <span>{{ displayAuthor(post) }}</span>
            <span v-if="displayAuthor(post) !== authorUsername(post)" class="ml-1 text-gray-400">
              @{{ authorUsername(post) }}
            </span>
          </RouterLink>
          <span v-else>{{ displayAuthor(post) }}</span>
          <span v-if="post.is_pinned" class="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-500/30">置顶</span>
          <span v-if="post.is_featured" class="px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200 dark:bg-teal-500/15 dark:text-teal-300 dark:border-teal-500/30">加精</span>
        </div>

        <h1 class="reader-title text-2xl md:text-3xl font-bold leading-tight mb-3">
          {{ post.title }}
        </h1>

        <div v-if="post.tags?.length" class="mb-4 flex flex-wrap gap-2">
          <span v-for="t in post.tags" :key="t" class="text-xs px-2 py-0.5 rounded bg-teal-50 text-teal-600 dark:bg-teal-500/12 dark:text-teal-300">{{ t }}</span>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            class="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg inline-flex items-center gap-1.5 disabled:opacity-60"
            :class="post.liked_by_me ? 'text-teal-600 border-teal-300 bg-teal-50/60 dark:bg-teal-500/10' : ''"
            :disabled="likingPost"
            @click="togglePostLike"
          >
            <span class="i-carbon-thumbs-up" />
            <span>{{ post.like_count || 0 }}</span>
          </button>
          <button v-if="canModerate" class="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg" @click="togglePinned">
            {{ post.is_pinned ? '取消置顶' : '置顶' }}
          </button>
          <button v-if="canModerate" class="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg" @click="toggleFeatured">
            {{ post.is_featured ? '取消加精' : '加精' }}
          </button>
          <button v-if="canEditPost" class="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg" @click="openEdit">
            编辑
          </button>
          <button v-if="canEditPost" class="px-3 py-1.5 border border-red-200 text-red-600 rounded-lg" @click="deletePost">
            删除
          </button>
        </div>
      </header>

      <div class="lg:hidden mb-3">
        <button
          class="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg flex items-center justify-between"
          @click="mobileTocOpen = !mobileTocOpen"
        >
          <span>目录</span>
          <span :class="mobileTocOpen ? 'i-carbon-chevron-up' : 'i-carbon-chevron-down'" />
        </button>
        <div v-if="mobileTocOpen" class="reader-panel reader-toc mt-2 rounded-xl p-3">
          <MdCatalog :editor-id="editorId" :scroll-element="scrollElement" :theme="mdTheme" />
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[1fr_250px] gap-6 items-start mt-4 reader-motion-enter reader-motion-enter--delay-1">
        <div class="reader-surface reader-surface--primary rounded-xl p-5">
          <MdPreview :editor-id="editorId" :model-value="post.content" :theme="mdTheme" class="reader-md" />
        </div>
        <aside class="hidden lg:block sticky top-24">
          <div class="reader-panel reader-toc rounded-xl p-4">
            <div class="text-sm font-semibold mb-2">
              目录
            </div>
            <MdCatalog :editor-id="editorId" :scroll-element="scrollElement" :theme="mdTheme" />
          </div>
        </aside>
      </div>

      <div class="mt-10 reader-motion-enter reader-motion-enter--delay-2">
        <h3 class="text-lg font-bold mb-4">
          评论
        </h3>

        <div class="space-y-4">
          <div v-for="comment in comments" :key="comment.id" class="reader-panel forum-comment-card p-3 md:p-4 rounded-xl">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0 flex-1">
                <div class="text-xs text-gray-400 mb-1 flex items-center gap-1.5">
                  <span>{{ new Date(comment.created_at).toLocaleString('zh-CN') }}</span>
                  <span>·</span>
                  <RouterLink
                    v-if="authorUsername(comment)"
                    class="text-teal-600 hover:underline"
                    :to="`/u/${encodeURIComponent(authorUsername(comment))}`"
                  >
                    <span>{{ displayAuthor(comment) }}</span>
                    <span v-if="displayAuthor(comment) !== authorUsername(comment)" class="ml-1 text-gray-400">
                      @{{ authorUsername(comment) }}
                    </span>
                  </RouterLink>
                  <span v-else>{{ displayAuthor(comment) }}</span>
                </div>
                <div class="relative">
                  <div
                    :id="`comment-content-${comment.id}`"
                    class="reader-comment-body prose prose-sm dark:prose-invert max-w-none transition-all"
                    :class="!isCommentExpanded(comment.id) && isLongComment(comment.content) ? 'max-h-36 overflow-hidden' : ''"
                    v-html="renderComment(comment.content)"
                  />
                  <div
                    v-if="!isCommentExpanded(comment.id) && isLongComment(comment.content)"
                    class="reader-fade-mask pointer-events-none absolute inset-x-0 bottom-0 h-12"
                  />
                </div>
                <button
                  v-if="isLongComment(comment.content)"
                  class="mt-2 text-xs text-teal-600 hover:underline"
                  :aria-expanded="String(isCommentExpanded(comment.id))"
                  :aria-controls="`comment-content-${comment.id}`"
                  @click="toggleCommentExpanded(comment.id)"
                >
                  {{ isCommentExpanded(comment.id) ? '收起' : '展开' }}
                </button>
              </div>
              <div class="flex flex-col items-end gap-2">
                <button
                  class="text-xs px-2 py-1 rounded border border-gray-200 dark:border-gray-700 inline-flex items-center gap-1 disabled:opacity-60"
                  :class="comment.liked_by_me ? 'text-teal-600 border-teal-300 bg-teal-50/60 dark:bg-teal-500/10' : ''"
                  :disabled="isCommentLiking(comment.id)"
                  @click="toggleCommentLike(comment)"
                >
                  <span class="i-carbon-thumbs-up" />
                  <span>{{ comment.like_count || 0 }}</span>
                </button>
                <button v-if="canDeleteComment(comment)" class="text-xs text-red-500" @click="deleteComment(comment.id)">
                  删除
                </button>
              </div>
            </div>
          </div>
          <div v-if="comments.length === 0" class="text-sm text-gray-400">
            暂无评论
          </div>
        </div>

        <div class="mt-4 flex justify-center">
          <button
            v-if="commentHasMore"
            class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg"
            :disabled="commentLoading"
            @click="fetchComments()"
          >
            {{ commentLoading ? '加载中...' : '加载更多评论' }}
          </button>
          <div v-else class="text-xs text-gray-400">
            没有更多评论了
          </div>
        </div>

        <div v-if="isLoggedIn" class="mt-6">
          <ForumCommentEditor
            v-model="newComment"
            :editor-height="180"
            :submitting="submitting"
            @submit="submitComment"
          />
        </div>
        <div v-else class="mt-6 p-4 rounded-xl border border-teal-200 bg-teal-50 text-sm text-teal-700 dark:border-teal-500/30 dark:bg-teal-500/10 dark:text-teal-200">
          登录后可参与评论
          <button class="ml-3 underline" @click="router.push('/login')">
            前往登录
          </button>
        </div>
      </div>
    </div>

    <ForumPostEditorModal
      v-model="editModal"
      title="编辑帖子"
      submit-text="保存"
      :submitting="editing"
      :initial-data="editInitialData"
      @submit="updatePost"
    />
  </div>
</template>
