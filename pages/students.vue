<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '~/stores/user'
import { apiFetch } from '~/logics/api'

const userStore = useUserStore()
const students = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedGrade = ref('All')

// Mock Grades - in real app, derive from data or config
const grades = ['All', '2025', '2024', '2023']

const fetchStudents = async () => {
    loading.value = true
    try {
        const res = await apiFetch('/api/students')
        if (res.ok) {
            students.value = await res.json()
        }
    } catch(e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const deleteStudent = async (id: string) => {
    if (!confirm('确认删除该学生吗？此操作不可恢复。')) return
    
    try {
        const res = await apiFetch(`/api/students/${id}`, {
            method: 'DELETE',
        })
        if (res.ok) {
            // Optimistic update
            students.value = students.value.filter(s => (s.id || s._id) !== id && s.username !== id)
        } else {
            const err = await res.json()
            alert(err.detail || '删除失败，权限不足？')
        }
    } catch (e) {
        console.error(e)
        alert('网络错误')
    }
}

const filteredStudents = computed(() => {
    return students.value.filter(s => {
        // Filter by Grade
        if (selectedGrade.value !== 'All' && String(s.grade) !== selectedGrade.value) return false
        
        // Filter by Search
        if (searchQuery.value) {
            const q = searchQuery.value.toLowerCase()
            return s.name.toLowerCase().includes(q) || 
                   s.username.toLowerCase().includes(q) ||
                   (s.major || '').toLowerCase().includes(q)
        }
        return true
    })
})

onMounted(fetchStudents)
</script>

<template>
  <div class="prose m-auto p-10 max-w-6xl">
    <div class="flex flex-col md:flex-row justify-between items-center mb-10 gap-6">
        <h1 class="text-3xl font-serif m-0">学生管理</h1>
        
        <!-- Controls -->
        <div class="flex flex-col md:flex-row gap-4 items-center w-full md:w-auto">
            <!-- Grade Filter -->
            <div class="flex bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
                <button v-for="g in grades" :key="g"
                    @click="selectedGrade = g"
                    class="px-4 py-1.5 rounded-md text-sm font-medium transition-all"
                    :class="selectedGrade === g ? 'bg-white dark:bg-gray-700 shadow text-teal-600 dark:text-teal-400' : 'text-gray-500 hover:text-gray-700'">
                    {{ g }}
                </button>
            </div>
            
            <!-- Search -->
            <div class="relative">
                <input v-model="searchQuery" type="text" placeholder="Search students..." 
                       class="pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white/50 dark:bg-black/20 focus:border-teal-500 outline-none w-full md:w-64 backdrop-blur-sm" />
                <div class="i-carbon-search absolute left-3 top-2.5 text-gray-400" />
            </div>

            <!-- Add Button (Teacher only) -->
             <!-- TODO: Check role strictly. For now just show logic placeholder or relying on backend generic error if student tries -->
             <!-- <button class="p-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition"><div class="i-carbon-add" /></button> -->
        </div>
    </div>
    
    <div v-if="loading" class="text-center opacity-50 py-10">
        <div class="animate-spin i-carbon-circle-dash text-4xl mb-2 mx-auto" />
        Loading...
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="s in filteredStudents" :key="s._id" 
             class="group p-6 border border-gray-100 dark:border-gray-800 rounded-xl bg-white dark:bg-gray-900 shadow-sm hover:shadow-lg transition-all duration-300 relative overflow-hidden">
            
            <!-- Header -->
            <div class="flex items-center gap-5 mb-5 px-1 relative z-10">
                <!-- Avatar -->
                <div class="w-16 h-16 rounded-full bg-gray-50 dark:bg-gray-800 border-2 border-white dark:border-gray-700 shadow-md overflow-hidden flex-shrink-0">
                    <img v-if="s.avatar" :src="s.avatar" class="w-full h-full object-cover transition transform group-hover:scale-110" />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-300 i-carbon-user text-3xl" />
                </div>
                
                <div class="flex-1 min-w-0 flex flex-col justify-center">
                    <div class="flex justify-between items-center w-full">
                        <h3 class="font-bold text-xl text-gray-900 dark:text-gray-100 truncate leading-none mb-1">{{ s.name }}</h3>
                        
                        <!-- Delete Action (Teacher Only visual hint) -->
                        <button v-if="userStore.hasRole('teacher', 'superadmin')" @click.stop="deleteStudent(s.id)" class="text-gray-300 hover:text-red-500 transition opacity-0 group-hover:opacity-100 p-1" title="删除">
                             <div class="i-carbon-trash-can text-lg" />
                        </button>
                    </div>
                    <p class="text-sm text-gray-400 font-medium truncate">{{ s.role || 'PhD Student' }}</p>
                    <p class="text-xs text-teal-600 dark:text-teal-400 mt-1 truncate font-mono opacity-80">{{ s.major || 'Major: Undeclared' }}</p>
                </div>
            </div>
            
            <!-- Body: Interests -->
            <div class="mb-4">
                <div class="flex flex-wrap gap-1.5 h-16 content-start overflow-hidden">
                     <span v-for="tag in (s.interests || [])" :key="tag" class="px-2 py-0.5 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-xs rounded border border-gray-100 dark:border-gray-700">
                         {{ tag }}
                     </span>
                     <span v-if="!s.interests || s.interests.length === 0" class="text-xs text-gray-300 italic">No public interests</span>
                </div>
            </div>

            <!-- Footer -->
            <div class="pt-4 border-t border-gray-50 dark:border-gray-800 flex justify-between items-center text-xs text-gray-400">
                <span>Joined {{ new Date().getFullYear() }}</span> <!-- Mock join date if missing -->
                <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{{ s.grade || 'N/A' }}</span>
            </div>
        </div>
    </div>
  </div>
</template>
