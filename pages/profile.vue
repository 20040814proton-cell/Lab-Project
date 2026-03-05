<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useUserStore } from '~/stores/user'
import { apiFetch, withApiBase } from '~/logics/api'

const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)
const canEditTeacher = computed(() => userStore.hasRole('teacher', 'superadmin'))

// Form State
const form = ref({
  avatar: '',
  major: '',
  interests: [] as string[],
  bio: '',
  // Teacher Fields
  title: '',
  office: '',
  public_email: '',
  research_areas_str: '' // For input
})

const fileInput = ref<HTMLInputElement | null>(null)

const triggerUpload = () => {
    fileInput.value?.click()
}

const handleUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement
    if (input.files && input.files[0]) {
        const file = input.files[0]
        const formData = new FormData()
        formData.append('file', file)
        
        loading.value = true
        try {
            const res = await apiFetch('/api/upload/', {
                method: 'POST',
                body: formData
            })
            if (res.ok) {
                const data = await res.json()
                // Update form state immediately for preview
                form.value.avatar = withApiBase(data.url)
            } else {
                alert('Upload failed')
            }
        } catch (e) {
            console.error(e)
            alert('Upload error')
        } finally {
            loading.value = false
        }
    }
}

const fetchProfile = async () => {
    loading.value = true
    try {
        const res = await apiFetch('/api/users/me')
        if (res.ok) {
            const data = await res.json()
            userStore.setUserInfo(data)
            const isTeacher = userStore.hasRole('teacher', 'superadmin')
            // Map response to form
            form.value.avatar = data.avatar || ''
            form.value.major = data.major || ''
            form.value.interests = data.interests || []
            form.value.bio = data.bio || ''
            
            // Teacher fields
            if (isTeacher) {
                form.value.title = data.title || ''
                form.value.office = data.office || ''
                form.value.public_email = data.public_email || ''
                form.value.research_areas_str = (data.research_areas || []).join(', ')
            }
        }
    } catch(e) {
        console.error('Failed to fetch profile', e)
    } finally {
        loading.value = false
    }
}

const tagInput = ref('')

const addTag = () => {
    const val = tagInput.value.trim()
    if (val && !form.value.interests.includes(val)) {
        form.value.interests.push(val)
    }
    tagInput.value = ''
}

const removeTag = (tag: string) => {
    form.value.interests = form.value.interests.filter(t => t !== tag)
}

const saveProfile = async () => {
    saving.value = true
    try {
        const payload: any = { ...form.value }
        delete payload.research_areas_str

        if (canEditTeacher.value) {
             payload.research_areas = form.value.research_areas_str
                ? form.value.research_areas_str.split(/[,\uFF0C]/).map(s => s.trim()).filter(Boolean)
                : []
        } else {
             delete payload.title
             delete payload.office
             delete payload.public_email
             delete payload.research_areas
        }

        const res = await apiFetch('/api/users/me', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        if (res.ok) {
            const data = await res.json()
            // Sync Store immediately
            userStore.setUserInfo(data)
            // Re-fetch to be safe (optional but good)
            await fetchProfile()
            alert('\u4fdd\u5b58\u6210\u529f\uff01')
        }
    } catch(e) {
        console.error(e)
        alert('Failed to save')
    } finally {
        saving.value = false
    }
}

onMounted(() => {
    fetchProfile()
})


</script>

<template>
  <div class="min-h-screen pt-24 px-6 pb-20 max-w-6xl mx-auto">
      <h1 class="text-3xl font-serif font-bold mb-10 text-gray-800 dark:text-gray-100">
          <span class="border-l-4 border-teal-500 pl-4">个人资料</span>
      </h1>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
          <!-- LEFT: Preview Card -->
          <div class="md:col-span-1">
              <h2 class="text-lg font-bold text-gray-400 mb-4 uppercase tracking-wider text-xs">名片预览</h2>
              
              <div class="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 shadow-lg flex flex-col items-center text-center">
                  <!-- Avatar -->
                  <div @click="triggerUpload" class="group relative w-24 h-24 rounded-full bg-gray-100 mb-4 overflow-hidden border-4 border-teal-50 dark:border-teal-900/30 cursor-pointer">
                      <img v-if="form.avatar || userStore.userInfo?.avatar" :src="form.avatar || userStore.userInfo?.avatar" class="w-full h-full object-cover" />
                      <div v-else class="w-full h-full flex items-center justify-center text-4xl text-gray-300 i-carbon-user"></div>
                      
                      <!-- Overlay -->
                      <div class="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                          <div class="i-carbon-camera text-white text-2xl" />
                      </div>
                  </div>
                  <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleUpload" />
                  
                  <h3 class="text-xl font-bold mb-1">{{ userStore.userInfo?.name || '用户名' }}</h3>
                  <p class="text-sm text-gray-400 mb-4">{{ userStore.userInfo?.username || 'ID: 2025xxx' }}</p>
                  
                  <div class="w-full h-px bg-gray-100 dark:bg-gray-700 mb-4"></div>
                  
                  <div class="text-teal-600 dark:text-teal-400 font-medium mb-4">
                      {{ form.major || '专业: 未填写' }}
                  </div>
                  
                  <!-- Tags -->
                  <div class="flex flex-wrap gap-2 justify-center">
                      <span v-for="tag in form.interests" :key="tag" 
                            class="px-2 py-0.5 rounded-full bg-teal-50 dark:bg-teal-900/30 text-teal-600 dark:text-teal-300 text-xs border border-teal-100 dark:border-teal-800">
                          {{ tag }}
                      </span>
                      <span v-if="form.interests.length === 0" class="text-xs text-gray-400 italic">暂无标签</span>
                  </div>
              </div>
          </div>

          <!-- RIGHT: Edit Form -->
          <div class="md:col-span-2">
              <div class="bg-white/60 dark:bg-gray-900/60 backdrop-blur-xl rounded-2xl p-8 border border-white/50 shadow-sm">
                  <h2 class="text-xl font-bold mb-6">编辑信息</h2>
                  
                  <!-- Major -->
                  <div class="mb-6">
                      <label class="block text-sm font-bold text-gray-500 mb-2">专业 / 研究方向</label>
                      <input v-model="form.major" type="text" placeholder="例如：计算机科学与技术" class="w-full px-4 py-2 rounded-lg bg-white/50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none transition" />
                  </div>
                  
                  <!-- Bio -->
                  <div class="mb-6">
                      <label class="block text-sm font-bold text-gray-500 mb-2">个人简介</label>
                      <textarea v-model="form.bio" rows="3" placeholder="一句话介绍你自己..." class="w-full px-4 py-2 rounded-lg bg-white/50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none transition"></textarea>
                  </div>

                  <!-- Teacher Specific Fields -->
                  <div v-if="canEditTeacher" class="mb-8 p-6 bg-teal-50/50 dark:bg-teal-900/10 rounded-xl border border-teal-100 dark:border-teal-800/30">
                      <h3 class="text-xs font-bold text-teal-600 dark:text-teal-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                        <div class="i-carbon-education" /> 教师信息
                      </h3>
                      
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div>
                              <label class="block text-xs font-medium text-gray-500 mb-1">职称</label>
                              <input v-model="form.title" placeholder="例如：教授" class="w-full px-3 py-2 rounded bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none" />
                          </div>
                           <div>
                              <label class="block text-xs font-medium text-gray-500 mb-1">办公室</label>
                              <input v-model="form.office" placeholder="例如：理科楼 302" class="w-full px-3 py-2 rounded bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none" />
                          </div>
                      </div>
                      
                      <div class="mb-4">
                          <label class="block text-xs font-medium text-gray-500 mb-1">公开邮箱</label>
                          <input v-model="form.public_email" placeholder="public@example.com" class="w-full px-3 py-2 rounded bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none" />
                      </div>
                      
                      <div>
                          <label class="block text-xs font-medium text-gray-500 mb-1">研究方向 (逗号分隔)</label>
                          <input v-model="form.research_areas_str" placeholder="AI, IoT, 数据挖掘..." class="w-full px-3 py-2 rounded bg-white dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none" />
                      </div>
                  </div>

                  <!-- Interests Tag Input -->
                  <div class="mb-8">
                      <label class="block text-sm font-bold text-gray-500 mb-2">兴趣标签 (回车添加)</label>
                      <div class="flex flex-wrap gap-2 mb-3">
                          <span v-for="tag in form.interests" :key="tag" 
                                @click="removeTag(tag)"
                                class="cursor-pointer hover:bg-red-100 hover:text-red-500 hover:border-red-200 transition px-3 py-1 rounded-full bg-teal-50 text-teal-700 text-sm border border-teal-100 flex items-center gap-1 group">
                              {{ tag }} <span class="i-carbon-close text-xs opacity-50 group-hover:opacity-100"/>
                          </span>
                      </div>
                      <input v-model="tagInput" @keydown.enter.prevent="addTag" type="text" placeholder="输入标签..." class="w-full px-4 py-2 rounded-lg bg-white/50 dark:bg-black/20 border border-gray-200 dark:border-gray-700 focus:border-teal-500 outline-none transition" />
                  </div>

                  <div class="flex justify-end">
                      <button @click="saveProfile" :disabled="saving" class="px-8 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-bold shadow-lg shadow-teal-500/30 transition transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50">
                          {{ saving ? '保存中...' : '保存修改' }}
                      </button>
                  </div>

              </div>
          </div>
      </div>
  </div>
</template>
