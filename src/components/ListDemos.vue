<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiFetch, withApiBase } from '~/logics/api'

const items = ref<any[]>([])
const showForm = ref(false)
const newItem = ref({ title: '', desc: '', link: '' })
const selectedFile = ref<File | null>(null)
const uploading = ref(false)

const fetchItems = async () => {
  try {
    const res = await apiFetch('/api/showcase/', {}, { auth: false })
    if (res.ok) items.value = await res.json()
  } catch (e) { console.error(e) }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

const submitItem = async () => {
  if (!newItem.value.title) return alert('标题不能为空')
  uploading.value = true
  
  try {
    let coverUrl = ''
    if (selectedFile.value) {
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      const uploadRes = await apiFetch('/api/upload/', {
        method: 'POST',
        body: formData
      }, { auth: false })
      if (uploadRes.ok) {
        const data = await uploadRes.json()
        coverUrl = data.url || data.filename
        coverUrl = withApiBase(coverUrl)
      }
    }

    await apiFetch('/api/showcase/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        ...newItem.value, 
        cover: coverUrl,
        date: new Date().toISOString() 
      })
    }, { auth: false })

    newItem.value = { title: '', desc: '', link: '' }
    selectedFile.value = null
    showForm.value = false
    await fetchItems()
  } catch (e) {
    console.error(e)
    alert('Failed')
  } finally {
    uploading.value = false
  }
}

onMounted(fetchItems)
</script>

<template>
  <div class="py-8">
    <div class="flex justify-end mb-8">
      <button @click="showForm = !showForm" class="px-4 py-2 border rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition text-sm flex items-center gap-2">
        <span class="i-carbon-add"/> 新增成果
      </button>
    </div>

    <div v-if="showForm" class="mb-8 p-6 border rounded-xl bg-gray-50 dark:bg-gray-800">
       <input v-model="newItem.title" placeholder="项目名称" class="w-full mb-3 px-3 py-2 border rounded bg-transparent" />
       <input v-model="newItem.link" placeholder="链接 (Link)" class="w-full mb-3 px-3 py-2 border rounded bg-transparent" />
       <textarea v-model="newItem.desc" placeholder="简短描述..." rows="2" class="w-full mb-3 px-3 py-2 border rounded bg-transparent"></textarea>
       
       <div class="flex items-center gap-4 mb-4">
         <span class="text-sm opacity-60">封面图:</span>
         <input type="file" @change="handleFileSelect" class="text-sm" />
       </div>

       <button @click="submitItem" :disabled="uploading" class="px-4 py-2 bg-black text-white dark:bg-white dark:text-black rounded disabled:opacity-50">
         {{ uploading ? '上传中...' : '发布' }}
       </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-if="items.length === 0" class="col-span-full opacity-50 py-10 text-center">暂无成果展示</div>
      
      <a v-for="item in items" :key="item.id" :href="item.link" target="_blank"
           class="group relative border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 rounded-xl overflow-hidden shadow-sm hover:-translate-y-2 hover:shadow-xl transition-all duration-300 block">
        <div v-if="item.cover" class="aspect-video overflow-hidden border-b border-gray-100 dark:border-gray-800/50">
          <img :src="item.cover" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
        </div>
        <div v-else class="aspect-video bg-gray-200 dark:bg-gray-700/50 flex items-center justify-center opacity-30">
          <span class="i-carbon-image text-4xl"/>
        </div>
        
        <div class="p-5">
           <div class="text-lg font-bold mb-2 group-hover:text-primary transition">{{ item.title }}</div>
           <div class="text-sm opacity-70 line-clamp-3">{{ item.desc }}</div>
        </div>
      </a>
    </div>
  </div>
</template>
