<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiFetch, withApiBase } from '~/logics/api'

const students = ref<any[]>([])
const loading = ref(true)
const showForm = ref(false) // Toggle form visibility
const errorMsg = ref('')

// Form State
const newMember = ref({ name: '', role: '', desc: '', link: '' })
const selectedFile = ref<File | null>(null)
const uploading = ref(false)

// Fetch Logic
const fetchStudents = async () => {
  try {
    const res = await apiFetch('/api/students/', {}, { auth: false })
    if (!res.ok) throw new Error('Failed to fetch')
    students.value = await res.json()
  } catch (e: any) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

// File Handler
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

// Submit Logic
const submitForm = async () => {
  if (!newMember.value.name) return alert('请输入姓名')
  uploading.value = true
  
  try {
    let iconUrl = 'i-carbon-user-avatar-filled' // Default
    
    // 1. Upload Image
    if (selectedFile.value) {
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      const uploadRes = await apiFetch('/api/upload/', {
        method: 'POST',
        body: formData
      }, { auth: false })
      if (uploadRes.ok) {
        const data = await uploadRes.json()
        // Ensure we handle the full URL if backend returns relative path
        iconUrl = data.url || data.filename
        iconUrl = withApiBase(iconUrl)
      }
    }

    // 2. Create Member
    const payload = { ...newMember.value, icon: iconUrl }
    const createRes = await apiFetch('/api/students/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (createRes.ok) {
      // Reset and Refresh
      newMember.value = { name: '', role: '', desc: '', link: '' }
      selectedFile.value = null
      showForm.value = false
      await fetchStudents()
    } else {
      alert('创建失败')
    }
  } catch (e) {
    console.error(e)
    alert('提交出错')
  } finally {
    uploading.value = false
  }
}

onMounted(fetchStudents)

// Simplified Computed (No Categories needed if redundant)
const list = computed(() => students.value)
</script>

<template>
  <div class="py-8">
    <div class="flex justify-end mb-6">
      <button 
        @click="showForm = !showForm"
        class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition flex items-center gap-2 cursor-pointer"
      >
        <div class="i-carbon-add text-lg" />
        {{ showForm ? '取消 (Cancel)' : '新增成员 (Add Member)' }}
      </button>
    </div>

    <div v-if="showForm" class="p-6 mb-8 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm bg-gray-50/50 dark:bg-gray-800/50 transition-all duration-300 ease-in-out">
      <h3 class="font-bold text-lg mb-4">填写新成员信息</h3>
      <div class="grid gap-4 max-w-lg">
        <input v-model="newMember.name" placeholder="姓名 (Name)" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-transparent focus:outline-none focus:border-gray-500" />
        <input v-model="newMember.role" placeholder="职位/身份 (Role)" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-transparent focus:outline-none focus:border-gray-500" />
        <textarea v-model="newMember.desc" placeholder="简介 (Bio)" rows="2" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-transparent focus:outline-none focus:border-gray-500" />
        
        <div class="flex items-center gap-4">
          <span class="text-sm opacity-70">上传头像:</span>
          <input type="file" @change="handleFileSelect" class="text-sm" />
        </div>

        <button 
          @click="submitForm" 
          :disabled="uploading"
          class="mt-2 px-4 py-2 bg-black text-white dark:bg-white dark:text-black rounded hover:opacity-80 transition disabled:opacity-50 cursor-pointer"
        >
          {{ uploading ? '提交中...' : '确认添加' }}
        </button>
      </div>
    </div>

    <div v-if="list.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <a 
        v-for="item in list" 
        :key="item.id"
        :href="item.link" 
        target="_blank"
        class="group relative flex items-start gap-4 p-4 rounded-xl border border-transparent hover:border-gray-200 dark:hover:border-gray-700 hover:-translate-y-1 hover:shadow-lg hover:bg-gray-50/80 transition-all duration-300 ease-in-out"
      >
        <div class="shrink-0">
            <img 
              v-if="item.icon && item.icon.includes('/')" 
              :src="item.icon" 
              class="w-16 h-16 rounded-full object-cover border border-gray-200 dark:border-gray-700" 
            />
            <div 
              v-else 
              :class="item.icon || 'i-carbon-user'" 
              class="w-16 h-16 text-4xl bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center opacity-80" 
            />
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
             <div class="font-bold text-lg truncate">{{ item.name }}</div>
             <div class="i-carbon-arrow-up-right opacity-0 group-hover:opacity-100 transition text-sm" />
          </div>
          <div class="text-sm opacity-75 mb-1">{{ item.role }}</div>
          <div class="text-sm opacity-60 leading-relaxed line-clamp-2">{{ item.desc }}</div>
        </div>
      </a>
    </div>

    <div v-else-if="!loading" class="text-center py-10 opacity-50">
      暂无成员，点击上方按钮添加。
    </div>
  </div>
</template>
