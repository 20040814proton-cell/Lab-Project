<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '~/stores/user'
import { apiFetch, withApiBase } from '~/logics/api'

const userStore = useUserStore()
const loading = ref(false)
const list = ref<any[]>([])
const search = ref('')
const currentTab = ref('全部')

const tabs = ['全部', '工具软件', '开发套件', '开发库', '其他']

const showModal = ref(false)
const saving = ref(false)
const form = ref({
    name: '',
    version: '',
    category: '工具软件',
    size: '',
    description: '',
    download_url: '',
    cover_image: ''
})

const fileInput = ref<HTMLInputElement | null>(null)

const canEdit = computed(() => userStore.hasRole('teacher', 'superadmin'))

const fetchList = async () => {
    loading.value = true
    try {
        const res = await apiFetch('/api/software/')
        if (res.ok) {
            list.value = await res.json()
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const filteredList = computed(() => {
    let res = list.value
    if (currentTab.value !== '全部') {
        res = res.filter(i => i.category === currentTab.value)
    }
    if (search.value) {
        const q = search.value.toLowerCase()
        res = res.filter(i => i.name.toLowerCase().includes(q) || i.description.toLowerCase().includes(q))
    }
    return res
})

const openCreateModal = () => {
    form.value = {
        name: '',
        version: '',
        category: '工具软件',
        size: '',
        description: '',
        download_url: '',
        cover_image: ''
    }
    showModal.value = true
}

const triggerUpload = () => fileInput.value?.click()

const handleUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement
    if (input.files && input.files[0]) {
        const file = input.files[0]
        const formData = new FormData()
        formData.append('file', file)
        
        try {
            const res = await apiFetch('/api/upload/', {
                method: 'POST',
                body: formData
            })
            if (res.ok) {
                const data = await res.json()
                form.value.cover_image = withApiBase(data.url)
            }
        } catch (e) {
            alert('Upload failed')
        }
    }
}

const submitSoftware = async () => {
    if (!form.value.name || !form.value.download_url) {
        return alert('请填写必要及下载链接')
    }
    saving.value = true
    try {
        const res = await apiFetch('/api/software/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(form.value)
        })
        
        if (res.ok) {
            showModal.value = false
            fetchList()
        } else {
            alert('Failed to create')
        }
    } catch(e) {
         console.error(e)
    } finally {
        saving.value = false
    }
}

const deleteItem = async (id: string) => {
    if(!confirm('确定删除?')) return
    try {
        const res = await apiFetch(`/api/software/${id}`, {
            method: 'DELETE',
        })
        if(res.ok) fetchList()
    } catch(e) { console.error(e) }
}

const handleDownload = async (item: any) => {
    // 1. Open immediately
    window.open(item.download_url, '_blank')
    
    // 2. Count in background
    try {
        await apiFetch(`/api/software/${item.id}/download`, { method: 'POST' }, { auth: false })
        // 3. Optimistic update
        item.download_count++
    } catch(e) { console.error(e) }
}

onMounted(fetchList)
</script>

<template>
<div class="min-h-screen pt-24 px-6 pb-20 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between mb-10 gap-6">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-800 dark:text-gray-100 flex items-center gap-3">
                 <span class="border-l-4 border-teal-500 pl-4">软件资源</span>
                 <span class="text-sm font-normal text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Software & Tools</span>
            </h1>
            <p class="mt-2 text-gray-500 pl-5">实验室常用工具、SDK及开发库下载</p>
        </div>
        
        <div class="flex items-center gap-4">
             <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="i-carbon-search text-gray-400"></span>
                </div>
                <input v-model="search" type="text" placeholder="搜索资源..." 
                       class="pl-10 pr-4 py-2 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none transition w-64 shadow-sm" />
            </div>
            
            <button v-if="canEdit" @click="openCreateModal" 
                class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-full flex items-center gap-2 shadow-lg shadow-teal-500/30 transition transform hover:-translate-y-0.5 active:translate-y-0">
                <span class="i-carbon-add text-lg"></span>
                <span>添加资源</span>
            </button>
        </div>
    </div>
    
    <!-- Tabs -->
    <div class="flex flex-wrap gap-2 mb-8">
        <button v-for="tab in tabs" :key="tab" 
                @click="currentTab = tab"
                :class="[
                    'px-4 py-1.5 rounded-full text-sm font-medium transition border',
                    currentTab === tab 
                        ? 'bg-teal-600 text-white border-teal-600 shadow-md shadow-teal-500/20' 
                        : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-teal-300'
                ]">
            {{ tab }}
        </button>
    </div>
    
    <!-- Grid -->
    <div v-if="loading" class="py-20 text-center text-gray-400">Loading...</div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="item in filteredList" :key="item.id" 
             class="group bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-xl hover:shadow-teal-500/5 transition duration-300 flex flex-col overflow-hidden">
            
            <!-- Cover -->
            <div class="aspect-video bg-gray-100 dark:bg-gray-900 relative overflow-hidden">
                 <img v-if="item.cover_image" :src="item.cover_image" class="w-full h-full object-cover transition duration-500 group-hover:scale-105"/>
                 <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
                     <span class="i-carbon-application text-4xl"></span>
                 </div>
                 
                 <!-- Admin Delete -->
                 <button v-if="canEdit" @click.stop="deleteItem(item.id)" 
                    class="absolute top-2 right-2 p-1.5 bg-white/90 text-red-500 rounded-full opacity-0 group-hover:opacity-100 transition hover:bg-red-50">
                     <span class="i-carbon-trash-can text-lg"></span>
                 </button>
            </div>
            
            <!-- Content -->
            <div class="p-5 flex-1 flex flex-col">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-bold text-lg text-gray-800 dark:text-gray-100 line-clamp-1" :title="item.name">{{ item.name }}</h3>
                    <span class="text-xs font-mono bg-gray-100 dark:bg-gray-700 text-gray-500 px-2 py-0.5 rounded ml-2 shrink-0">{{ item.version }}</span>
                </div>
                
                <div class="flex items-center gap-3 text-xs text-gray-400 mb-3">
                    <span class="flex items-center gap-1"><i class="i-carbon-data-class text-teal-500"></i> {{ item.category }}</span>
                    <span class="w-px h-3 bg-gray-200 dark:bg-gray-700"></span>
                    <span>{{ item.size }}</span>
                </div>
                
                <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-4 flex-1">{{ item.description }}</p>
                
                <div class="mt-auto pt-4 border-t border-gray-50 dark:border-gray-700/50 flex items-center justify-between">
                    <div class="text-xs text-gray-400">
                        <div class="flex items-center gap-1 mb-0.5">
                            <span class="i-carbon-download"></span> {{ item.download_count }} 次下载
                        </div>
                    </div>
                    
                    <button @click="handleDownload(item)" 
                            class="px-4 py-1.5 bg-teal-50 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 text-sm font-bold rounded-lg hover:bg-teal-600 hover:text-white transition-colors">
                        立即下载
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="showModal = false">
        <div class="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-fade-in-up">
            <div class="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
                <h3 class="text-lg font-bold">添加软件资源</h3>
                <button @click="showModal = false" class="text-gray-400 hover:text-gray-600"><span class="i-carbon-close text-xl"></span></button>
            </div>
            
            <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-500 mb-1">软件名称 *</label>
                        <input v-model="form.name" class="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 focus:border-teal-500 outline-none" />
                    </div>
                     <div>
                        <label class="block text-xs font-bold text-gray-500 mb-1">版本 *</label>
                        <input v-model="form.version" placeholder="v1.0" class="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 focus:border-teal-500 outline-none" />
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                     <div>
                        <label class="block text-xs font-bold text-gray-500 mb-1">分类</label>
                        <select v-model="form.category" class="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 focus:border-teal-500 outline-none">
                            <option v-for="t in tabs.slice(1)" :key="t" :value="t">{{ t }}</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-500 mb-1">大小 (手动填写)</label>
                        <input v-model="form.size" placeholder="e.g. 50 MB" class="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 focus:border-teal-500 outline-none" />
                    </div>
                </div>
                
                 <div>
                    <label class="block text-xs font-bold text-gray-500 mb-1">下载链接 *</label>
                    <input v-model="form.download_url" placeholder="https://..." class="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 focus:border-teal-500 outline-none" />
                </div>
                
                 <div>
                    <label class="block text-xs font-bold text-gray-500 mb-1">简介</label>
                    <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 focus:border-teal-500 outline-none"></textarea>
                </div>
                
                 <!-- Image Upload -->
                <div>
                   <label class="block text-xs font-bold text-gray-500 mb-1">封面图片</label> 
                   <div @click="triggerUpload" class="w-full h-32 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-teal-500 hover:bg-teal-50 transition relative overflow-hidden">
                       <img v-if="form.cover_image" :src="form.cover_image" class="absolute inset-0 w-full h-full object-cover" />
                       <div v-else class="text-gray-400 flex flex-col items-center">
                           <span class="i-carbon-image text-2xl mb-1"></span>
                           <span class="text-xs">点击上传封面 (16:9)</span>
                       </div>
                   </div>
                   <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleUpload" />
                </div>

            </div>
            
            <div class="p-6 pt-2 flex justify-end">
                <button @click="submitSoftware" :disabled="saving" class="px-6 py-2 bg-teal-600 text-white rounded-lg font-bold hover:bg-teal-700 transition disabled:opacity-50">
                    {{ saving ? '提交中...' : '发布资源' }}
                </button>
            </div>
        </div>
    </div>
</div>
</template>
