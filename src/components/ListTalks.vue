<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import { apiFetch } from '~/logics/api'

const md = new MarkdownIt()
const items = ref([])
const showForm = ref(false)
const newItem = ref({ title: '', content: '' })

const fetchItems = async () => {
  try {
    const res = await apiFetch('/api/life/', {}, { auth: false })
    if (res.ok) items.value = await res.json()
  } catch (e) { console.error(e) }
}

const submitItem = async () => {
  if (!newItem.value.title) return
  await apiFetch('/api/life/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...newItem.value, date: new Date().toISOString() })
  }, { auth: false })
  newItem.value = { title: '', content: '' }
  showForm.value = false
  await fetchItems()
}

onMounted(fetchItems)
</script>

<template>
  <div class="py-4">
    <div class="flex justify-end mb-6">
      <button @click="showForm = !showForm" class="px-4 py-2 border border-gray-200/50 rounded-lg hover:bg-white/50 transition backdrop-blur-md text-sm flex items-center gap-2">
        <span class="i-carbon-add" /> {{ showForm ? '取消' : '发布动态' }}
      </button>
    </div>

    <div v-if="showForm" class="mb-8 p-6 rounded-xl border border-gray-200/50 bg-white/60 dark:bg-gray-900/60 backdrop-blur-md shadow-inner">
       <input v-model="newItem.title" placeholder="发生了什么？" class="w-full mb-3 px-3 py-2 border border-gray-200/50 rounded bg-transparent focus:bg-white/50 transition outline-none" />
       <textarea v-model="newItem.content" placeholder="详细说说 (支持 Markdown)..." rows="3" class="w-full mb-3 px-3 py-2 border border-gray-200/50 rounded bg-transparent focus:bg-white/50 transition outline-none font-mono text-sm"></textarea>
       <button @click="submitItem" class="px-4 py-2 bg-black/80 text-white dark:bg-white/90 dark:text-black rounded hover:shadow-lg transition">发布</button>
    </div>

    <div class="space-y-4">
      <div v-for="item in items" :key="item.id" 
           class="p-6 rounded-xl border border-gray-200/50 dark:border-gray-700/50 
                  bg-white/60 dark:bg-gray-900/60 backdrop-blur-md shadow-sm
                  hover:-translate-y-1 hover:shadow-lg transition-all duration-300">
        <div class="flex justify-between items-center mb-3">
          <div class="text-lg font-bold">{{ item.title }}</div>
          <div class="text-xs opacity-50 font-mono">{{ new Date(item.date).toLocaleDateString('zh-CN') }}</div>
        </div>
        <div class="prose dark:prose-invert opacity-80 text-sm max-w-none" v-html="md.render(item.content || '')"></div>
      </div>
    </div>
  </div>
</template>
