<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import { useUserStore } from '~/stores/user'
import { apiFetch } from '~/logics/api'

const userStore = useUserStore()
const emit = defineEmits<{
  (e: 'edit', post: any): void
}>()

const props = defineProps<{
  layout?: 'list' | 'grid'
  viewBase?: string
}>()

const md = new MarkdownIt()
const posts = ref<any[]>([])

const fetchPosts = async () => {
  try {
    const res = await apiFetch('/api/posts/', {}, { auth: false })
    if (res.ok)
      posts.value = await res.json()
  } catch (error) {
    console.error(error)
  }
}

defineExpose({
  fetchPosts,
})

const deletePost = async (id: string) => {
  if (!confirm('确定要删除这条动态吗？'))
    return
  try {
    const res = await apiFetch(`/api/posts/${id}`, {
      method: 'DELETE',
    })
    if (res.ok)
      await fetchPosts()
    else
      alert('删除失败')
  } catch (error) {
    console.error(error)
  }
}

const getViewPath = (id: string) => {
  const base = props.viewBase || '/news'
  return `${base.replace(/\/$/, '')}/${id}`
}

onMounted(fetchPosts)
</script>

<template>
  <div class="py-4">
    <div :class="layout === 'grid' ? 'grid grid-cols-1 md:grid-cols-3 gap-6' : 'space-y-4'">
      <div
        v-for="post in posts"
        :key="post.id"
        class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden"
        :class="layout === 'grid' ? 'flex flex-col h-full' : 'p-6 bg-white/60 backdrop-blur-md'"
      >
        <div
          v-if="layout === 'grid'"
          class="w-full aspect-video bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center relative overflow-hidden group cursor-pointer"
          @click="$router.push(getViewPath(post.id))"
        >
          <template v-if="post.cover_image">
            <img :src="post.cover_image" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105">
          </template>
          <template v-else>
            <div class="i-carbon-image text-4xl opacity-10 dark:opacity-20 text-gray-500" />
          </template>

          <div
            v-if="userStore.hasRole('teacher', 'superadmin')"
            class="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <button class="p-1.5 bg-white/90 dark:bg-gray-800/90 rounded-full hover:bg-teal-500 hover:text-white transition shadow-sm" @click.stop="emit('edit', post)">
              <div class="i-carbon-edit" />
            </button>
            <button class="p-1.5 bg-white/90 dark:bg-gray-800/90 rounded-full hover:bg-red-500 hover:text-white transition shadow-sm" @click.stop="deletePost(post.id)">
              <div class="i-carbon-trash-can" />
            </button>
          </div>
        </div>

        <div :class="layout === 'grid' ? 'p-5 flex flex-col flex-1' : ''">
          <div
            class="text-xl font-bold mb-2 font-serif text-gray-900 dark:text-gray-100 line-clamp-2 leading-snug"
            :class="{ 'cursor-pointer hover:text-teal-600 transition-colors': layout === 'grid' }"
            @click="layout === 'grid' && $router.push(getViewPath(post.id))"
          >
            {{ post.title }}
          </div>

          <div v-if="layout === 'grid'" class="text-sm text-gray-500 mb-4 line-clamp-2 leading-relaxed">
            {{ post.summary || '暂无简介' }}
          </div>

          <div class="text-xs text-gray-400 mb-3 flex items-center gap-2">
            <span>{{ new Date(post.date).toLocaleDateString('zh-CN') }}</span>
            <span v-if="post.author" class="w-1 h-1 rounded-full bg-gray-300" />
            <span v-if="post.author">{{ post.author }}</span>
          </div>

          <div v-if="layout !== 'grid'" class="prose dark:prose-invert opacity-90 leading-relaxed text-sm max-w-none" v-html="md.render(post.content || '')" />

          <div v-if="layout === 'grid'" class="flex-1" />

          <div v-if="layout === 'grid'" class="mt-4 flex justify-between items-center text-sm">
            <span class="text-teal-600 dark:text-teal-400 font-medium hover:underline cursor-pointer" @click.stop="$router.push(getViewPath(post.id))">阅读更多</span>
            <div class="i-carbon-arrow-right text-teal-600 dark:text-teal-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

