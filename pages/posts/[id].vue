<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MdPreview, MdCatalog } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { apiFetch } from '~/logics/api'
import { isDark } from '~/logics'

const route = useRoute()
const router = useRouter()
const post = ref<any>(null)
const loading = ref(true)

const editorId = 'preview-only'
const scrollElement = document.documentElement

const fetchPost = async () => {
    try {
        const idParam = route.params.id as string | string[]
        const id = Array.isArray(idParam) ? idParam[0] : idParam
        const res = await apiFetch(`/api/posts/${id}`, {}, { auth: false })
        if (res.ok) {
            post.value = await res.json()
        } else {
           // Handle 404 or redirect
        }
    } catch (e) { console.error(e) }
    finally { loading.value = false }
}



const readingTime = computed(() => {
    if (!post.value?.content) return 0
    const words = post.value.content.trim().split(/\s+/).length
    return Math.ceil(words / 200) // Rough estimation
})
const mdTheme = computed(() => (isDark.value ? 'dark' : 'light'))

onMounted(fetchPost)
</script>

<template>
<div class="reader-page min-h-screen pt-24 pb-20 px-6 max-w-4xl mx-auto">
    <!-- Back Button -->
    <button @click="router.back()" class="reader-back-button mb-8 flex items-center gap-2 transition group">
        <span class="i-carbon-arrow-left group-hover:-translate-x-1 transition-transform"></span>
        <span class="font-serif">返回列表</span>
    </button>

    <div v-if="loading" class="py-20 flex justify-center text-gray-400">
        <span class="i-carbon-circle-dash animate-spin text-3xl"></span>
    </div>

    <div v-else-if="post" class="animate-enter">
        <!-- Header -->
        <header class="mb-10 text-center">
             <div class="reader-meta text-sm font-mono mb-3 uppercase tracking-wider flex items-center justify-center gap-2">
                 <span>{{ new Date(post.date).toLocaleDateString() }}</span>
                 <span class="w-1 h-1 rounded-full bg-teal-300"></span>
                 <span>{{ readingTime }} min read</span>
             </div>
             <h1 class="reader-title text-3xl md:text-5xl font-serif font-bold leading-tight mb-6">
                 {{ post.title }}
             </h1>
             <div class="reader-meta flex items-center justify-center gap-3 text-sm">
                  <span v-if="post.author" class="flex items-center gap-2">
                      <span class="w-6 h-6 rounded-full bg-gray-200 block"></span> {{ post.author }}
                  </span>
             </div>
        </header>

        <!-- Cover -->
        <div v-if="post.cover_image" class="reader-cover mb-12 aspect-video rounded-2xl overflow-hidden">
            <img :src="post.cover_image" class="w-full h-full object-cover" />
        </div>

        <!-- Content -->
        <!-- Content -->
        <!-- Two-column layout: Content + Toc -->
        <div class="grid grid-cols-1 lg:grid-cols-[1fr_250px] gap-8 items-start relative">

          <article class="reader-surface reader-surface--primary p-8 rounded-xl min-w-0">
             <MdPreview :editorId="editorId" :modelValue="post.content" :theme="mdTheme" class="reader-md" />
          </article>

          <aside class="hidden lg:block sticky top-24 w-full">
             <div class="reader-panel reader-toc rounded-lg p-4">
                <div class="font-bold text-gray-900 dark:text-gray-100 mb-2 pl-2 border-l-4 border-teal-500">目录</div>
                <MdCatalog :editorId="editorId" :scrollElement="scrollElement" :theme="mdTheme" />
             </div>
          </aside>

        </div>
        
        <!-- Footer / Tags could go here -->
    </div>
    
    <div v-else class="text-center py-20">
        <h2 class="text-2xl font-bold text-gray-300">文章不存在</h2>
    </div>
</div>
</template>

<style scoped>
.animate-enter {
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
    transform: translateY(20px);
}

@keyframes fadeUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
