<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '~/stores/user'
import { apiFetch, withApiBase } from '~/logics/api'

const userStore = useUserStore()
const activities = ref<any[]>([])
const stats = ref<any>({})
const loading = ref(false)
const showModal = ref(false)
const submitting = ref(false)
const viewMode = ref<'upcoming' | 'past'>('upcoming')


const form = ref({
    title: '',
    type: '研讨会',
    date: '',
    location: '',
    participants: 0,
    summary: '',
    content: '',
    cover_image: ''
})


const activityTypes = ['研讨会', '工作坊', '开放日', '讲座', '其他']


const fetchActivities = async () => {
    loading.value = true
    try {
        const res = await apiFetch('/api/activities/')
        if (res.ok) {
            const data = await res.json()
            // Client-side sorting/filtering could happen here, or computed
            activities.value = data
        }
        
        const sRes = await apiFetch('/api/activities/stats')
        if (sRes.ok) stats.value = await sRes.json()
    } catch (e) { console.error(e) } 
    finally { loading.value = false }
}

const upcomingActivities = computed(() => {
    const today = new Date()
    today.setHours(0,0,0,0)
    return activities.value.filter(a => new Date(a.date) >= today).sort((a,b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const pastActivities = computed(() => {
    const today = new Date()
    today.setHours(0,0,0,0)
    return activities.value.filter(a => new Date(a.date) < today).sort((a,b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

const triggerUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = async (e: any) => {
        const file = e.target.files[0]
        if (!file) return
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
        } catch(e) { alert("Upload failed") }
    }
    input.click()
}

const editingId = ref<string | null>(null)

const openCreateModal = () => {
    editingId.value = null
    form.value = { title: '', type: '研讨会', date: '', location: '', participants: 0, summary: '', content: '', cover_image: '' }
    showModal.value = true
}

const openEditModal = (act: any) => {
    editingId.value = act.id
    form.value = { ...act, date: act.date.split('T')[0] } // Fix date format
    showModal.value = true
}

const submitActivity = async () => {
    if (!form.value.title || !form.value.date) return alert("请填写必要信息")
    submitting.value = true
    try {
        // Ensure participants is an integer
        const payload = {
            ...form.value,
            participants: parseInt(form.value.participants as any) || 0
        }
        
        const url = editingId.value 
            ? `/api/activities/${editingId.value}`
            : '/api/activities/'
            
        const method = editingId.value ? 'PUT' : 'POST'
        
        const res = await apiFetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })

        if (res.ok) {
            showModal.value = false
            fetchActivities()
            alert(editingId.value ? '活动修改成功！' : '活动发布成功！')
        } else {
            const err = await res.json()
            alert('操作失败: ' + (err.detail || 'Unknown error'))
        }
    } catch(e: any) { 
        console.error(e) 
        alert('操作失败: ' + e.message)
    }
    finally { submitting.value = false }
}

const deleteActivity = async (id: string) => {
    if(!confirm("删除此活动？")) return
    try {
        const res = await apiFetch(`/api/activities/${id}`, {
            method: 'DELETE',
        })
        if(res.ok) fetchActivities()
    } catch(e) { console.error(e) }
}

onMounted(fetchActivities)
</script>

<template>
  <div class="min-h-screen p-6 md:p-10 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-10 text-center relative z-10">
          <h1 class="text-4xl font-serif font-bold text-gray-900 dark:text-white mb-2">学习活动</h1>
          <p class="text-gray-500 font-light">Laboratory Learning Activities</p>
      </div>
      
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 relative z-10">
          <div class="p-8 rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-md border border-white/50 dark:border-gray-700 shadow-lg text-center relative overflow-hidden group">
              <div class="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">开放日</div>
              <div class="text-6xl font-serif text-teal-600 dark:text-teal-400 group-hover:scale-110 transition duration-500">{{ stats['开放日'] || 0 }}</div>
              <div class="absolute -right-10 -bottom-10 opacity-5 i-carbon-events text-9xl"></div>
          </div>
          <div class="p-8 rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-md border border-white/50 dark:border-gray-700 shadow-lg text-center relative overflow-hidden group">
              <div class="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">近期研讨</div>
              <div class="text-6xl font-serif text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition duration-500">{{ stats['研讨会'] || 0 }}</div>
              <div class="absolute -right-10 -bottom-10 opacity-5 i-carbon-forum text-9xl"></div>
          </div>
          <div class="p-8 rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-md border border-white/50 dark:border-gray-700 shadow-lg text-center relative overflow-hidden group">
              <div class="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">工作坊</div>
              <div class="text-6xl font-serif text-amber-600 dark:text-amber-400 group-hover:scale-110 transition duration-500">{{ stats['工作坊'] || 0 }}</div>
              <div class="absolute -right-10 -bottom-10 opacity-5 i-carbon-tools text-9xl"></div>
          </div>
      </div>
      
      <!-- Actions & Switcher -->
      <div class="flex flex-col md:flex-row justify-between items-center mb-8 relative z-10 gap-4">
          <div class="flex items-center gap-4">
              <h2 class="text-2xl font-serif font-bold border-l-4 border-teal-500 pl-4">活动列表</h2>
              
              <!-- View Toggle -->
              <div class="bg-gray-100 dark:bg-gray-800 p-1 rounded-full flex text-sm font-medium">
                  <button @click="viewMode = 'upcoming'" class="px-4 py-1.5 rounded-full transition-all" :class="viewMode === 'upcoming' ? 'bg-teal-600 text-white shadow' : 'text-gray-500 hover:text-gray-900'">近期预告</button>
                  <button @click="viewMode = 'past'" class="px-4 py-1.5 rounded-full transition-all" :class="viewMode === 'past' ? 'bg-teal-600 text-white shadow' : 'text-gray-500 hover:text-gray-900'">往期回顾</button>
              </div>
          </div>
          
          <button v-if="userStore.hasRole('teacher', 'superadmin')" @click="openCreateModal" class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition flex items-center gap-2 shadow-lg hover:shadow-teal-500/30">
              <div class="i-carbon-add" /> 发布活动
          </button>
      </div>
      
      <!-- List: Upcoming (Grid) -->
      <div v-if="viewMode === 'upcoming'">
          <div v-if="upcomingActivities.length === 0" class="text-center py-20 text-gray-400">
              <div class="i-carbon-sleep text-4xl mb-2 mx-auto" />
              <p>暂无近期活动</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 relative z-10">
              <div v-for="act in upcomingActivities" :key="act.id" @click="$router.push('/activities/' + act.id)" class="group bg-white dark:bg-gray-900 rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-800 relative cursor-pointer">
                  
                  <!-- Image & Badge -->
                  <div class="h-48 relative overflow-hidden">
                       <img :src="act.cover_image || 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?q=80&w=2070&auto=format&fit=crop'" class="w-full h-full object-cover group-hover:scale-105 transition duration-700" />
                       <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60"></div>
                       
                       <!-- Ink Date Badge -->
                       <div class="absolute top-4 left-4 w-14 h-14 bg-white dark:bg-gray-900 border-2 border-teal-600 dark:border-teal-500 shadow-lg flex flex-col items-center justify-center font-serif leading-none z-10">
                           <span class="text-xs text-gray-500 font-bold uppercase border-b border-gray-200 w-full text-center pb-0.5">{{ act.date ? act.date.split('-')[1] + '月' : '??' }}</span>
                           <span class="text-xl font-bold text-teal-700 dark:text-teal-400 pt-0.5">{{ act.date ? act.date.split('-')[2] : '??' }}</span>
                       </div>
                       
                        <!-- Actions (Teacher) -->
                        <div v-if="userStore.hasRole('teacher', 'superadmin')" class="absolute top-4 right-4 z-20 flex gap-2 opacity-0 group-hover:opacity-100 transition duration-300">
                             <button @click.stop="openEditModal(act)" class="p-2 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-teal-500 hover:text-white transition">
                                <div class="i-carbon-edit" />
                             </button>
                             <button @click.stop="deleteActivity(act.id)" class="p-2 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-red-500 hover:text-white transition">
                                <div class="i-carbon-trash-can" />
                             </button>
                        </div>
                  </div>
                  
                  <!-- Content -->
                  <div class="p-6">
                      <div class="flex items-center gap-2 mb-3 text-xs font-medium text-teal-600 dark:text-teal-400 uppercase tracking-widest">
                          <span class="px-2 py-0.5 border border-teal-200 dark:border-teal-800 rounded">{{ act.type }}</span>
                      </div>
                      
                      <h3 class="text-xl font-serif font-bold text-gray-900 dark:text-white mb-2 line-clamp-1 group-hover:text-teal-600 transition">{{ act.title }}</h3>
                      
                      <div class="flex items-center gap-4 text-sm text-gray-400 mb-4">
                          <div class="flex items-center gap-1"><div class="i-carbon-location" /> {{ act.location }}</div>
                          <div class="flex items-center gap-1"><div class="i-carbon-user" /> {{ act.participants }} 人</div>
                      </div>
                      
                      <p class="text-gray-500 dark:text-gray-400 text-sm line-clamp-2 leading-relaxed h-10 mb-4">{{ act.summary }}</p>
    
                      <div class="pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center text-xs text-gray-400">
                           <span class="text-teal-600 font-medium opacity-0 group-hover:opacity-100 transition transform translate-x-[-10px] group-hover:translate-x-0">Read details -></span>
                      </div>
                  </div>
              </div>
          </div>
      </div>

      <!-- List: Past (Timeline) -->
      <div v-else class="relative py-10">
          <div v-if="pastActivities.length === 0" class="text-center py-20 text-gray-400">
              <p>暂无往期回顾</p>
          </div>
          <!-- Line -->
          <div v-else class="absolute left-4 md:left-1/2 top-0 bottom-0 w-0.5 bg-teal-200 dark:bg-teal-900/50"></div>
          
          <div v-for="(act, index) in pastActivities" :key="act.id" 
               class="relative flex flex-col md:flex-row items-center mb-12 md:mb-20 cursor-pointer group"
               :class="index % 2 === 0 ? 'md:flex-row-reverse' : ''"
               @click="$router.push('/activities/' + act.id)"
          >
              <!-- Node -->
              <div class="absolute left-4 md:left-1/2 w-4 h-4 bg-teal-500 rounded-full border-4 border-white dark:border-gray-900 z-10 transform -translate-x-1.5 md:-translate-x-2"></div>
              
              <!-- Spacer -->
              <div class="w-full md:w-1/2"></div>
              
              <!-- Content Card -->
              <div class="w-[calc(100%-3rem)] md:w-1/2 ml-12 md:ml-0 md:px-10">
                   <div class="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition relative">
                       <span class="text-xs text-gray-400 mb-1 block">{{ act.date }}</span>
                       <h3 class="text-lg font-bold mb-2 group-hover:text-teal-600 transition">{{ act.title }}</h3>
                       <div class="flex items-center gap-2 mb-3">
                           <span class="px-2 py-0.5 bg-teal-50 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 text-xs rounded border border-teal-100 dark:border-teal-800">{{ act.type }}</span>
                           <span class="px-2 py-0.5 bg-gray-50 dark:bg-gray-700 text-gray-500 text-xs rounded">Successfully Held</span>
                       </div>
                       <p class="text-sm text-gray-500 line-clamp-2">{{ act.summary }}</p>
                   </div>
              </div>
          </div>
      </div>
      
      <!-- Modal -->
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModal = false"></div>
          <div class="relative w-full max-w-lg bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-100 dark:border-gray-800 max-h-[90vh] overflow-y-auto">
               <h3 class="text-xl font-bold mb-6">{{ editingId ? '编辑学习活动' : '发布新活动' }}</h3>
              
              <div class="space-y-4">
                  <div @click="triggerUpload" class="w-full h-32 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center cursor-pointer hover:border-teal-500 transition relative overflow-hidden group">
                      <img v-if="form.cover_image" :src="form.cover_image" class="absolute inset-0 w-full h-full object-cover" />
                      <div v-else class="text-gray-400 flex flex-col items-center group-hover:text-teal-500 transition"><div class="i-carbon-image text-2xl"/><span>上传封面图</span></div>
                  </div>
                  
                  <div>
                      <label class="block text-xs font-medium text-gray-400 mb-1">活动名称</label>
                      <input v-model="form.title" placeholder="输入活动标题..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none focus:ring-1 ring-teal-500" />
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                       <div>
                           <label class="block text-xs font-medium text-gray-400 mb-1">活动类型</label>
                           <select v-model="form.type" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none">
                               <option v-for="t in activityTypes" :key="t">{{ t }}</option>
                           </select>
                       </div>
                       <div>
                           <label class="block text-xs font-medium text-gray-400 mb-1">活动日期</label>
                           <input v-model="form.date" type="date" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                       </div>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">举办地点</label>
                          <input v-model="form.location" placeholder="例如：302会议室" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                      </div>
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">预计人数</label>
                          <input v-model.number="form.participants" type="number" placeholder="0" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                      </div>
                  </div>
                  
                  <div>
                      <label class="block text-xs font-medium text-gray-400 mb-1">活动简介</label>
                      <textarea v-model="form.summary" rows="2" placeholder="简要描述活动内容..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none"></textarea>
                  </div>
                  
                  <div>
                      <label class="block text-xs font-medium text-gray-400 mb-1">详细内容 (Markdown)</label>
                      <textarea v-model="form.content" rows="4" placeholder="支持 Markdown 格式..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none font-mono text-sm"></textarea>
                  </div>
              </div>
              
              <div class="mt-8 flex justify-end gap-3">
                  <button @click="showModal = false" class="px-4 py-2 text-gray-500 hover:text-gray-700">取消</button>
                  <button @click="submitActivity" class="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition shadow-lg shadow-teal-500/30" :disabled="submitting">{{ submitting ? '提交中...' : (editingId ? '保存修改' : '确认发布') }}</button>
              </div>
          </div>
      </div>
  </div>
</template>
