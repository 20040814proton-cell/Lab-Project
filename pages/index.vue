<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ListPosts from '~/components/ListPosts.vue'
import NewsPostEditorModal from '~/components/news/NewsPostEditorModal.vue'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const showPostModal = ref(false)
const listPostsRef = ref<InstanceType<typeof ListPosts> | null>(null)
const showHero = ref(false)
const editingPost = ref<any | null>(null)

const openCreateModal = () => {
  editingPost.value = null
  showPostModal.value = true
}

const handleEdit = (post: any) => {
  editingPost.value = post
  showPostModal.value = true
}

const handlePostSaved = () => {
  showPostModal.value = false
  listPostsRef.value?.fetchPosts()
}

onMounted(() => {
  const enable = () => { showHero.value = true }
  if ('requestIdleCallback' in window)
    (window as any).requestIdleCallback(enable)
  else
    setTimeout(enable, 0)
})

const features = [
  { label: '学生管理', path: '/students', icon: 'i-carbon-user-multiple', desc: '学生档案与培养信息维护' },
  { label: '教师团队', path: '/teachers', icon: 'i-carbon-education', desc: '导师信息与研究方向展示' },
  { label: '项目记录', path: '/projects', icon: 'i-carbon-folder', desc: '科研项目进展与成果追踪' },
  { label: '学术活动', path: '/activities', icon: 'i-carbon-notebook', desc: '研讨会、讲座与活动管理' },
  { label: '软件下载', path: '/downloads', icon: 'i-carbon-download', desc: '实验室常用工具与资源下载' },
  { label: '关于我们', path: '/about', icon: 'i-carbon-information', desc: '实验室简介、方向与愿景' },
]
</script>

<template>
  <div class="min-h-screen relative flex flex-col items-center overflow-x-hidden">
    <div class="absolute inset-0 z-0 opacity-80 pointer-events-none">
      <HeroAnimation v-if="showHero" />
    </div>

    <div class="relative z-10 w-full px-6 pt-32 pb-20 text-center">
      <div class="backdrop-blur-xl bg-white/60 dark:bg-black/40 border border-white/50 dark:border-white/10 rounded-2xl shadow-lg p-10 max-w-5xl mx-auto">
        <h1 class="text-4xl md:text-6xl font-bold mb-4 text-gray-900 dark:text-white font-serif tracking-wider">
          数据智能与嵌入式技术实验室
        </h1>
        <p class="text-xl md:text-2xl text-teal-600 dark:text-teal-400 font-light mb-8">
          数据智能，嵌入未来
        </p>
        <p class="text-base text-gray-500 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
          聚焦数据挖掘、智能系统与嵌入式技术融合，构建“科研 + 实践 + 交流”一体化平台。
        </p>
      </div>
    </div>

    <div class="relative z-10 w-full max-w-5xl px-6 mb-24" style="background-image: radial-gradient(#0d9488 1px, transparent 1px); background-size: 24px 24px; opacity: 0.9;">
      <div class="flex items-center gap-4 mb-10">
        <div class="h-px bg-gray-200 dark:bg-gray-800 flex-1" />
        <h2 class="text-2xl font-serif opacity-80 bg-white/80 dark:bg-black/80 px-4 rounded-full backdrop-blur-sm">功能导航</h2>
        <div class="h-px bg-gray-200 dark:bg-gray-800 flex-1" />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <RouterLink
          v-for="item in features"
          :key="item.path"
          :to="item.path"
          class="group relative p-6 rounded-xl bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border border-gray-100 dark:border-gray-800 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden"
        >
          <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-teal-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-teal-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-teal-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-teal-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

          <div class="flex items-start justify-between mb-4">
            <div :class="item.icon" class="text-3xl text-teal-600 dark:text-teal-400 opacity-80 group-hover:opacity-100 transition" />
            <div class="i-carbon-arrow-up-right text-gray-300 group-hover:text-teal-500 transition" />
          </div>
          <h3 class="text-lg font-bold mb-2 group-hover:text-teal-700 dark:group-hover:text-teal-300 transition">{{ item.label }}</h3>
          <p class="text-sm text-gray-500 leading-relaxed">{{ item.desc }}</p>
        </RouterLink>
      </div>
    </div>

    <div class="relative z-10 w-full max-w-5xl px-6 mb-20">
      <div class="flex items-center gap-4 mb-10">
        <div class="h-px bg-gray-200 dark:bg-gray-800 flex-1" />
        <h2 class="text-2xl font-serif opacity-80">实验室动态</h2>
        <div v-if="userStore.hasRole('teacher', 'superadmin')" class="ml-4">
          <button class="px-3 py-1 bg-teal-600 text-white text-xs rounded hover:shadow transition" @click="openCreateModal">
            + 发布动态
          </button>
        </div>
        <div class="h-px bg-gray-200 dark:bg-gray-800 flex-1" />
      </div>

      <ListPosts ref="listPostsRef" layout="grid" view-base="/news" @edit="handleEdit" />
      <div class="mt-6 flex flex-wrap justify-center gap-4">
        <RouterLink to="/news" class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-sm transition">
          查看更多动态
        </RouterLink>
        <RouterLink to="/forum" class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-sm transition">
          进入论坛
        </RouterLink>
      </div>
    </div>

    <NewsPostEditorModal
      v-model="showPostModal"
      :post-id="editingPost?.id || null"
      :initial-post="editingPost"
      @saved="handlePostSaved"
    />

    <div class="relative z-10 pb-8 text-center text-xs text-gray-400">
      © {{ new Date().getFullYear() }} Data Intelligence & Embedded Technology Lab
    </div>
  </div>
</template>

