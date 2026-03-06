<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import { apiFetch } from '~/logics/api'

const route = useRoute()
const activity = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
    try {
        const res = await apiFetch(`/api/activities/${route.params.id}`, {}, { auth: false })
        if (res.ok) {
            activity.value = await res.json()
        }
    } catch(e) { console.error(e) }
    finally { loading.value = false }
})
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 pb-20">
      <div v-if="loading" class="h-screen flex items-center justify-center">
          <div class="i-carbon-circle-dash animate-spin text-4xl text-teal-600" />
      </div>
      
      <div v-else-if="activity">
          <!-- Hero Header "Invitation Style" -->
          <div class="relative h-[60vh] md:h-[70vh] w-full overflow-hidden">
              <img :src="activity.cover_image || 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?q=80&w=2070'" class="w-full h-full object-cover" />
              <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent"></div>
              
              <div class="absolute inset-x-0 bottom-0 p-8 md:p-16 text-center z-10 flex flex-col items-center">
                  <div class="px-4 py-1 border border-teal-400 text-teal-400 rounded-full text-xs uppercase tracking-[0.2em] mb-4 bg-teal-900/30 backdrop-blur-sm">
                      {{ activity.type }}
                  </div>
                  <h1 class="text-4xl md:text-6xl font-serif font-bold text-white mb-4 leading-tight shadow-sm">{{ activity.title }}</h1>
                  <div class="text-xl md:text-2xl font-light text-gray-200 font-serif border-t border-gray-600 pt-4 mt-2 inline-block px-8">
                      {{ activity.date }}
                  </div>
              </div>
          </div>
          
          <!-- Sticky Info Bar -->
          <div class="sticky top-0 z-40 bg-white/90 dark:bg-gray-800/90 backdrop-blur-lg border-b border-gray-100 dark:border-gray-700 shadow-sm py-4 px-6 flex flex-wrap justify-center gap-6 md:gap-12 text-sm md:text-base text-gray-600 dark:text-gray-300">
             <div class="flex items-center gap-2">
                 <div class="i-carbon-time text-teal-600" />
                 <span>{{ new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'}) }} (Est)</span>
             </div>
             <div class="flex items-center gap-2">
                 <div class="i-carbon-location text-teal-600" />
                 <span>{{ activity.location }}</span>
             </div>
             <div class="flex items-center gap-2">
                 <div class="i-carbon-user text-teal-600" />
                 <span>{{ activity.participants }} 席位</span>
             </div>
          </div>
          
          <!-- Content Body -->
          <div class="max-w-5xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-12">
              <div class="md:col-span-2">
                  <div class="prose dark:prose-invert max-w-none">
                      <p class="lead text-lg text-gray-600 dark:text-gray-400 mb-8 border-l-4 border-teal-500 pl-4 italic">
                          {{ activity.summary }}
                      </p>
                      
                      <!-- Markdown Content Render -->
                      <div v-if="activity.content" v-html="activity.content" class="markdown-body"></div>
                      <div v-else class="text-center py-12 text-gray-400 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-dashed border-gray-200 dark:border-gray-700">
                          暂无详细内容
                      </div>
                  </div>
              </div>
              
              <!-- Sidebar -->
              <div class="md:col-span-1 space-y-6">
                  <div class="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-xl border border-teal-100 dark:border-teal-800/30">
                      <h3 class="font-bold text-teal-900 dark:text-teal-100 mb-2">报名参加</h3>
                      <p class="text-sm text-teal-700 dark:text-teal-300 mb-4">感兴趣参加此活动？立即预订您的席位。</p>
                      <button class="w-full py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition shadow-lg shadow-teal-500/20 font-medium">
                          立即报名
                      </button>
                  </div>
                  
                  <div class="border-t border-gray-100 dark:border-gray-800 pt-6">
                      <h4 class="text-sm font-bold text-gray-900 dark:text-gray-100 mb-4 uppercase tracking-wider">Share</h4>
                      <div class="flex gap-4 text-2xl text-gray-400">
                          <button class="hover:text-teal-600 transition"><div class="i-carbon-logo-wechat" /></button>
                          <button class="hover:text-teal-600 transition"><div class="i-carbon-logo-github" /></button>
                          <button class="hover:text-teal-600 transition"><div class="i-carbon-link" /></button>
                      </div>
                  </div>
              </div>
          </div>
      </div>
      
      <div v-else class="min-h-[50vh] flex flex-col items-center justify-center">
          <h1 class="text-2xl font-bold mb-4">Activity Not Found</h1>
          <button @click="$router.push('/activities')" class="text-teal-600 hover:underline">Back to List</button>
      </div>
  </div>
</template>
