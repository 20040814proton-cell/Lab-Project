<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '~/logics/api'
import { isDark } from '~/logics'
import { goBackOr } from '~/logics/navigation'

interface AdjacentPostItem {
  id: string
  title: string
  date: string
}

interface AdjacentPostPayload {
  previous: AdjacentPostItem | null
  next: AdjacentPostItem | null
}

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const post = ref<any>(null)
const adjacent = ref<AdjacentPostPayload>({ previous: null, next: null })
const loadError = ref('')
const mdTheme = computed(() => (isDark.value ? 'dark' : 'light'))

function goBack() {
  goBackOr(router, '/news')
}

function getPostId() {
  const idParam = route.params.id as string | string[]
  return Array.isArray(idParam) ? idParam[0] : idParam
}

async function fetchAdjacent(postId: string) {
  const res = await apiFetch(`/api/posts/${postId}/adjacent`, {}, { auth: false })
  if (res.ok) {
    adjacent.value = await res.json()
    return
  }
  adjacent.value = { previous: null, next: null }
}

async function fetchPost() {
  loading.value = true
  loadError.value = ''
  post.value = null
  adjacent.value = { previous: null, next: null }

  const postId = getPostId()
  if (!postId) {
    loadError.value = '文章不存在'
    loading.value = false
    return
  }

  try {
    const res = await apiFetch(`/api/posts/${postId}`, {}, { auth: false })
    if (!res.ok) {
      loadError.value = res.status === 404 ? '文章不存在或已删除' : '加载失败，请稍后重试'
      return
    }

    post.value = await res.json()
    await fetchAdjacent(postId)
  }
  finally {
    loading.value = false
  }
}

watch(() => route.params.id, fetchPost)
onMounted(fetchPost)
</script>

<template>
  <div class="reader-page news-detail-page min-h-screen pt-24 px-6 pb-20 max-w-4xl mx-auto">
    <button class="reader-back-button mb-4 text-sm transition flex items-center gap-1.5" @click="goBack">
      <span class="i-carbon-arrow-left" />
      返回上一个页面
    </button>

    <div v-if="loading" class="py-20 text-center text-gray-400">
      <div class="i-carbon-circle-dash animate-spin text-3xl mb-2 mx-auto" />
      Loading...
    </div>

    <div v-else-if="loadError" class="py-20 text-center">
      <p class="text-red-500 mb-4">{{ loadError }}</p>
      <RouterLink to="/news" class="text-teal-600 hover:underline">返回动态列表</RouterLink>
    </div>

    <div v-else-if="post" class="news-detail-shell">
      <div class="reader-motion-enter">
        <div class="reader-meta mb-3">{{ new Date(post.date).toLocaleDateString('zh-CN') }}</div>
        <h1 class="reader-title text-3xl font-serif font-bold mb-6">{{ post.title }}</h1>
      </div>
      <div v-if="post.cover_image" class="reader-cover reader-cover--media mb-8 rounded-xl overflow-hidden reader-motion-enter reader-motion-enter--delay-1">
        <img :src="post.cover_image" class="reader-cover-media" />
      </div>
      <div class="reader-surface reader-surface--primary rounded-2xl p-5 md:p-7 reader-motion-enter reader-motion-enter--delay-1">
        <MdPreview :editor-id="'news-preview'" :model-value="post.content" :theme="mdTheme" class="reader-md" />
      </div>

      <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4 reader-motion-enter reader-motion-enter--delay-2">
        <RouterLink
          v-if="adjacent.previous"
          :to="`/news/${adjacent.previous.id}`"
          class="reader-adjacent-card news-adjacent-card block rounded-xl p-4 transition"
        >
          <div class="reader-meta text-xs mb-2">上一篇</div>
          <div class="reader-adjacent-title font-medium line-clamp-2 mb-2">{{ adjacent.previous.title }}</div>
          <div class="reader-meta text-xs">{{ new Date(adjacent.previous.date).toLocaleDateString('zh-CN') }}</div>
        </RouterLink>
        <div v-else class="reader-adjacent-empty rounded-xl p-4 text-sm">
          没有上一篇
        </div>

        <RouterLink
          v-if="adjacent.next"
          :to="`/news/${adjacent.next.id}`"
          class="reader-adjacent-card news-adjacent-card block rounded-xl p-4 transition"
        >
          <div class="reader-meta text-xs mb-2">下一篇</div>
          <div class="reader-adjacent-title font-medium line-clamp-2 mb-2">{{ adjacent.next.title }}</div>
          <div class="reader-meta text-xs">{{ new Date(adjacent.next.date).toLocaleDateString('zh-CN') }}</div>
        </RouterLink>
        <div v-else class="reader-adjacent-empty rounded-xl p-4 text-sm">
          没有下一篇
        </div>
      </div>
    </div>
  </div>
</template>
