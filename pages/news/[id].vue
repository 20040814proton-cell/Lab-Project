<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '~/logics/api'
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
  <div class="min-h-screen pt-24 px-6 pb-20 max-w-4xl mx-auto">
    <button class="mb-4 text-sm text-gray-500 hover:text-teal-600 transition flex items-center gap-1.5" @click="goBack">
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

    <div v-else-if="post">
      <div class="text-xs text-gray-400 mb-3">{{ new Date(post.date).toLocaleDateString('zh-CN') }}</div>
      <h1 class="text-3xl font-serif font-bold mb-6">{{ post.title }}</h1>
      <div v-if="post.cover_image" class="mb-8 rounded-xl overflow-hidden">
        <img :src="post.cover_image" class="w-full h-full object-cover" />
      </div>
      <MdPreview :editor-id="'news-preview'" :model-value="post.content" />

      <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
        <RouterLink
          v-if="adjacent.previous"
          :to="`/news/${adjacent.previous.id}`"
          class="block rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 hover:border-teal-300 hover:shadow-sm transition"
        >
          <div class="text-xs text-gray-400 mb-2">上一篇</div>
          <div class="font-medium text-gray-900 dark:text-gray-100 line-clamp-2 mb-2">{{ adjacent.previous.title }}</div>
          <div class="text-xs text-gray-400">{{ new Date(adjacent.previous.date).toLocaleDateString('zh-CN') }}</div>
        </RouterLink>
        <div v-else class="rounded-xl border border-dashed border-gray-200 dark:border-gray-700 p-4 text-sm text-gray-400">
          没有上一篇
        </div>

        <RouterLink
          v-if="adjacent.next"
          :to="`/news/${adjacent.next.id}`"
          class="block rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 hover:border-teal-300 hover:shadow-sm transition"
        >
          <div class="text-xs text-gray-400 mb-2">下一篇</div>
          <div class="font-medium text-gray-900 dark:text-gray-100 line-clamp-2 mb-2">{{ adjacent.next.title }}</div>
          <div class="text-xs text-gray-400">{{ new Date(adjacent.next.date).toLocaleDateString('zh-CN') }}</div>
        </RouterLink>
        <div v-else class="rounded-xl border border-dashed border-gray-200 dark:border-gray-700 p-4 text-sm text-gray-400">
          没有下一篇
        </div>
      </div>
    </div>
  </div>
</template>
