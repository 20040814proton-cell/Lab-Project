<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '~/stores/user'
import { apiFetch, withApiBase } from '~/logics/api'

const userStore = useUserStore()
const projects = ref<any[]>([])
const stats = ref<any>({ ongoing: 0, completed: 0, total: 0 })
const showModal = ref(false)
const submitting = ref(false)

const form = ref({
    title: '',
    status: '进行中',
    category: '',
    progress: 0,
    leader: '',
    members: '', // Comma separated string for input
    description: '',
    cover_image: '',
    repo_url: ''
})

const fetchProjects = async () => {
    try {
        const res = await apiFetch('/api/projects/')
        if (res.ok) projects.value = await res.json()
        
        const sRes = await apiFetch('/api/projects/stats')
        if (sRes.ok) stats.value = await sRes.json()
    } catch(e) { console.error(e) }
}

const statusColors = (status: string) => {
    switch(status) {
        case '进行中': return 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
        case '已结题': return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
        case '筹备中': return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300'
        default: return 'bg-gray-100 text-gray-500'
    }
}

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
    form.value = { title: '', status: '进行中', category: '', progress: 0, leader: '', members: '', description: '', cover_image: '', repo_url: '' }
    showModal.value = true
}

const openEditModal = (proj: any) => {
    editingId.value = proj.id
    form.value = { ...proj, members: proj.members.join(', ') }
    showModal.value = true
}

const submitProject = async () => {
    if (!form.value.title) return alert("请输入项目标题")
    submitting.value = true
    try {
        // Parse members string to array
        const memberList = form.value.members.split(/[,，]/).map(s => s.trim()).filter(s => s)
        
        const payload = {
            ...form.value,
            progress: parseInt(form.value.progress as any),
            members: memberList
        }
        
        const url = editingId.value 
            ? `/api/projects/${editingId.value}`
            : '/api/projects/'
            
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
            fetchProjects()
            alert(editingId.value ? '项目修改成功' : '项目创建成功')
        } else {
            alert('操作失败')
        }
    } catch(e) { console.error(e) }
    finally { submitting.value = false }
}

const deleteProject = async (id: string) => {
    if(!confirm("确认删除？")) return
    try {
        const res = await apiFetch(`/api/projects/${id}`, {
            method: 'DELETE',
        })
        if(res.ok) fetchProjects()
    } catch(e) { console.error(e) }
}

onMounted(fetchProjects)
</script>

<template>
  <div class="min-h-screen p-6 md:p-10 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-10 text-center relative z-10">
          <h1 class="text-4xl font-serif font-bold text-gray-900 dark:text-white mb-2">科研记录</h1>
          <p class="text-gray-500 font-light">Laboratory Research Dashboard</p>
      </div>
      
      <!-- Host Stats (Glass Cards) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 relative z-10">
          <div class="p-6 rounded-2xl bg-teal-50/60 dark:bg-teal-900/20 backdrop-blur-md border border-teal-100 dark:border-teal-800 shadow-lg relative overflow-hidden group">
              <div class="text-teal-600 dark:text-teal-400 text-sm font-medium uppercase tracking-wider mb-2">进行中项目</div>
              <div class="text-5xl font-serif text-teal-700 dark:text-teal-300">{{ stats.ongoing }}</div>
              <div class="absolute -right-6 -bottom-6 opacity-10 i-carbon-idea text-9xl text-teal-500"></div>
          </div>
          
          <div class="p-6 rounded-2xl bg-gray-50/60 dark:bg-gray-800/40 backdrop-blur-md border border-gray-100 dark:border-gray-700 shadow-lg relative overflow-hidden group">
              <div class="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">已结题项目</div>
              <div class="text-5xl font-serif text-gray-700 dark:text-gray-300">{{ stats.completed }}</div>
              <div class="absolute -right-6 -bottom-6 opacity-10 i-carbon-certificate text-9xl text-gray-500"></div>
          </div>
          
          <div class="p-6 rounded-2xl bg-amber-50/60 dark:bg-amber-900/20 backdrop-blur-md border border-amber-100 dark:border-amber-800 shadow-lg relative overflow-hidden group">
              <div class="text-amber-600 dark:text-amber-400 text-sm font-medium uppercase tracking-wider mb-2">科研成果总数</div>
              <div class="text-5xl font-serif text-amber-700 dark:text-amber-300">{{ stats.total }}</div>
              <div class="absolute -right-6 -bottom-6 opacity-10 i-carbon-trophy text-9xl text-amber-500"></div>
          </div>
      </div>
      
      <!-- Actions -->
      <div class="flex justify-between items-center mb-8 relative z-10">
          <h2 class="text-2xl font-serif font-bold border-l-4 border-teal-500 pl-4">项目列表</h2>
          <button v-if="userStore.hasRole('teacher', 'superadmin')" @click="openCreateModal" class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition flex items-center gap-2 shadow-lg hover:shadow-teal-500/30">
              <div class="i-carbon-add" /> 新增项目
          </button>
      </div>

      <!-- Project Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
          <div v-for="proj in projects" :key="proj.id" class="group bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-xl transition-all duration-300 relative">
              <!-- Delete (Teacher) -->
              <!-- Actions (Teacher) -->
              <div v-if="userStore.hasRole('teacher', 'superadmin')" class="absolute top-4 right-4 z-20 flex gap-2">
                   <button @click.stop="openEditModal(proj)" class="text-gray-300 hover:text-teal-500 transition">
                      <div class="i-carbon-edit" />
                   </button>
                   <button @click.stop="deleteProject(proj.id)" class="text-gray-300 hover:text-red-500 transition">
                      <div class="i-carbon-trash-can" />
                   </button>
              </div>

              <!-- Header -->
              <div class="mb-4 pr-8">
                  <div class="flex items-center gap-2 mb-2">
                      <span :class="statusColors(proj.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">{{ proj.status }}</span>
                      <span class="text-xs bg-gray-100 dark:bg-gray-800 text-gray-500 px-2 py-0.5 rounded">{{ proj.category }}</span>
                  </div>
                  <h3 class="text-xl font-serif font-bold text-gray-900 dark:text-white leading-tight flex items-center gap-2">
                      {{ proj.title }}
                      <!-- Repo Link -->
                      <a v-if="proj.repo_url" :href="proj.repo_url" target="_blank" class="text-gray-400 hover:text-gray-900 dark:hover:text-white transition" @click.stop>
                         <div :class="proj.repo_url.includes('github') ? 'i-carbon-logo-github' : 'i-carbon-link'" />
                      </a>
                  </h3>
              </div>
              
              <!-- Body -->
              <p class="text-gray-500 dark:text-gray-400 text-sm mb-6 line-clamp-3 h-14">{{ proj.description }}</p>
              
              <!-- Progress -->
              <div class="mb-6">
                  <div class="flex justify-between text-xs mb-1">
                      <span class="text-gray-400">项目进度</span>
                      <span class="font-medium text-teal-600 dark:text-teal-400">{{ proj.progress }}%</span>
                  </div>
                  <div class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-1.5 overflow-hidden">
                      <div class="bg-teal-500 h-full rounded-full transition-all duration-1000" :style="{ width: proj.progress + '%' }"></div>
                  </div>
              </div>
              
              <!-- Footer -->
              <div class="pt-4 border-t border-gray-50 dark:border-gray-800 flex items-center justify-between text-xs">
                  <div class="flex items-center gap-1 text-gray-600 dark:text-gray-300 font-medium">
                      <div class="i-carbon-user-filled text-teal-500" />
                      {{ proj.leader }}
                  </div>
                  <div class="text-gray-400">
                      {{ proj.members.length }} 成员
                  </div>
              </div>
          </div>
      </div>
      
      <!-- Create Modal -->
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModal = false"></div>
          <div class="relative w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-100 dark:border-gray-800 max-h-[90vh] overflow-y-auto">
              <h3 class="text-xl font-bold mb-6">{{ editingId ? '编辑科研项目' : '登记科研项目' }}</h3>
              
              <div class="space-y-4">
                  <!-- Cover Image Upload -->
                  <div @click="triggerUpload" class="w-full h-32 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center cursor-pointer hover:border-teal-500 transition relative overflow-hidden group">
                       <img v-if="form.cover_image" :src="form.cover_image" class="absolute inset-0 w-full h-full object-cover" />
                       <div v-else class="text-gray-400 flex flex-col items-center group-hover:text-teal-500 transition"><div class="i-carbon-image text-2xl"/><span>上传项目封面 (可选)</span></div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">项目名称</label>
                          <input v-model="form.title" placeholder="输入项目名称..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none focus:ring-1 ring-teal-500" />
                      </div>
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">所属领域</label>
                          <input v-model="form.category" placeholder="例如：人工智能" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                      </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">当前状态</label>
                          <select v-model="form.status" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none">
                              <option>进行中</option>
                              <option>已结题</option>
                              <option>筹备中</option>
                          </select>
                      </div>
                       <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">代码仓库 (Repo URL)</label>
                          <input v-model="form.repo_url" placeholder="https://github.com/..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                      </div>
                  </div>
                  
                  <div>
                      <label class="block text-xs font-medium text-gray-400 mb-1">项目进度 ({{ form.progress }}%)</label>
                      <input type="range" v-model.number="form.progress" min="0" max="100" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600" />
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">负责人</label>
                          <input v-model="form.leader" placeholder="姓名" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                      </div>
                      <div>
                          <label class="block text-xs font-medium text-gray-400 mb-1">成员列表 (逗号分隔)</label>
                          <input v-model="form.members" placeholder="张三, 李四..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none" />
                      </div>
                  </div>
                  
                  <div>
                      <label class="block text-xs font-medium text-gray-400 mb-1">项目描述</label>
                      <textarea v-model="form.description" rows="3" placeholder="简要描述项目的目标和意义..." class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none"></textarea>
                  </div>
              </div>
              
              <div class="mt-8 flex justify-end gap-3">
                  <button @click="showModal = false" class="px-4 py-2 text-gray-500 hover:text-gray-700">取消</button>
                  <button @click="submitProject" class="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition shadow-lg shadow-teal-500/30" :disabled="submitting">{{ submitting ? '提交中...' : (editingId ? '保存修改' : '确认创建') }}</button>
              </div>
          </div>
      </div>
  </div>
</template>
