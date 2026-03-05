<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiFetch } from '~/logics/api'
import { useUserStore } from '~/stores/user'
import NewsPostEditorModal from '~/components/news/NewsPostEditorModal.vue'

const userStore = useUserStore()
const loading = ref(false)
const list = ref<any[]>([])
const query = ref('')
const page = ref(1)
const pageSize = 10
const hasMore = ref(true)
const showPostModal = ref(false)

const fetchNews = async (reset = false) => {
  if (reset) {
    page.value = 1
    list.value = []
    hasMore.value = true
  }
  if (!hasMore.value)
    return
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize),
    })
    if (query.value.trim())
      params.set('q', query.value.trim())

    const res = await apiFetch(`/api/posts/?${params.toString()}`, {}, { auth: false })
    if (res.ok) {
      const data = await res.json()
      list.value = [...list.value, ...data]
      if (data.length < pageSize)
        hasMore.value = false
      else
        page.value += 1
    }
  } finally {
    loading.value = false
  }
}

const onSearch = () => fetchNews(true)

const handleSaved = () => {
  showPostModal.value = false
  fetchNews(true)
}

onMounted(() => fetchNews(true))
</script>

<template>
  <div class="min-h-screen pt-24 px-6 pb-20 max-w-6xl mx-auto">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-serif font-bold">实验室动态</h1>
        <p class="text-sm text-gray-400 mt-2">Lab News & Updates</p>
      </div>
      <button
        v-if="userStore.hasRole('teacher', 'superadmin')"
        class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition"
        @click="showPostModal = true"
      >
        + 发布动态
      </button>
    </div>

    <div class="mb-6 flex flex-col md:flex-row gap-3">
      <input v-model="query" placeholder="搜索动态" class="flex-1 p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" @keyup.enter="onSearch">
      <div class="flex gap-3">
        <button class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg" @click="onSearch">搜索</button>
        <button class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg" @click="() => { query = ''; onSearch() }">重置</button>
      </div>
    </div>

    <div v-if="loading && list.length === 0" class="text-center py-20 text-gray-400">
      <div class="i-carbon-circle-dash animate-spin text-3xl mb-2 mx-auto" />
      Loading...
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <RouterLink
        v-for="post in list"
        :key="post.id"
        :to="`/news/${post.id}`"
        class="group rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm hover:shadow-md transition overflow-hidden"
      >
        <div class="aspect-video bg-gray-100 dark:bg-gray-800 relative">
          <img v-if="post.cover_image" :src="post.cover_image" class="w-full h-full object-cover">
        </div>
        <div class="p-5">
          <div class="text-xs text-gray-400 mb-2">{{ new Date(post.date).toLocaleDateString('zh-CN') }}</div>
          <h3 class="text-lg font-bold mb-2 group-hover:text-teal-600 transition">{{ post.title }}</h3>
          <p class="text-sm text-gray-500 line-clamp-2">{{ post.summary || '暂无摘要' }}</p>
        </div>
      </RouterLink>
    </div>

    <div class="pt-6 flex justify-center">
      <button
        v-if="hasMore"
        class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg"
        :disabled="loading"
        @click="fetchNews()"
      >
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
      <div v-else class="text-xs text-gray-400">没有更多了</div>
    </div>

    <NewsPostEditorModal v-model="showPostModal" @saved="handleSaved" />
  </div>
</template>

