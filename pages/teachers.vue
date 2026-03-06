<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiFetch } from '~/logics/api'

const teachers = ref<any[]>([])
const loading = ref(true)

const fetchTeachers = async () => {
    loading.value = true
    try {
        const res = await apiFetch('/api/users/?role=teacher', {}, { auth: false })
        if (res.ok) {
            const data = await res.json()
            // Optional: Sort by name or predefined order? 
            // For now just raw list
            teachers.value = data
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

onMounted(fetchTeachers)
</script>

<template>
<div class="min-h-screen p-6 md:p-10 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-12 text-center relative z-10">
          <h1 class="text-4xl font-serif font-bold text-gray-900 dark:text-white mb-2">师资团队</h1>
          <p class="text-gray-500 font-light">Laboratory Faculty & Research Team</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-20 text-gray-400">
          <div class="i-carbon-circle-dash animate-spin text-4xl mb-2 mx-auto" />
          <p>Loading team...</p>
      </div>

      <!-- Empty -->
      <div v-else-if="teachers.length === 0" class="text-center py-20 text-gray-400">
           <p>暂无师资信息</p>
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div v-for="t in teachers" :key="t.id" class="group bg-white dark:bg-gray-800 rounded-xl p-6 border border-teal-100/50 dark:border-teal-900/30 shadow-sm hover:shadow-xl hover:border-teal-200 transition-all duration-300 flex items-start gap-6 relative overflow-hidden">
              
              <!-- Subtle Background Decoration -->
              <div class="absolute top-0 right-0 w-24 h-24 bg-teal-500/5 rounded-bl-full z-0 transition group-hover:bg-teal-500/10"></div>

              <!-- Avatar -->
              <div class="shrink-0 relative z-10">
                  <div class="w-24 h-24 rounded-full bg-gray-100 border-2 border-white dark:border-gray-700 shadow-lg overflow-hidden">
                      <img :src="t.avatar || 'https://api.dicebear.com/7.x/notionists/svg?seed=' + t.name" class="w-full h-full object-cover" />
                  </div>
              </div>

              <!-- Info -->
              <div class="flex-1 relative z-10">
                  <div class="flex items-center gap-3 mb-1">
                      <h3 class="text-xl font-bold font-serif text-gray-900 dark:text-white">{{ t.name }}</h3>
                      <span v-if="t.title" class="px-2 py-0.5 rounded text-xs font-medium bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 border border-teal-100 dark:border-teal-800">{{ t.title }}</span>
                  </div>
                  
                  <p class="text-sm text-gray-500 dark:text-gray-400 mb-3 leading-relaxed line-clamp-2 min-h-[2.5em]">{{ t.bio || '暂无简介' }}</p>

                  <!-- Contact Tags -->
                  <div class="flex flex-wrap gap-y-2 gap-x-4 mb-4 text-xs text-gray-400 font-mono">
                      <div v-if="t.office" class="flex items-center gap-1 hover:text-teal-600 transition">
                          <div class="i-carbon-building" /> {{ t.office }}
                      </div>
                      <div v-if="t.public_email" class="flex items-center gap-1 hover:text-teal-600 transition">
                          <div class="i-carbon-email" /> {{ t.public_email }}
                      </div>
                  </div>

                  <!-- Research Areas -->
                  <div class="flex flex-wrap gap-2">
                       <span v-for="area in t.research_areas" :key="area" class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700/50 text-gray-600 dark:text-gray-300 text-xs rounded-full group-hover:bg-teal-50 dark:group-hover:bg-teal-900/20 group-hover:text-teal-600 transition duration-500">
                           #{{ area }}
                       </span>
                  </div>
              </div>
          </div>
      </div>
</div>
</template>
