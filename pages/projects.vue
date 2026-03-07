<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch, withApiBase } from '~/logics/api'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const route = useRoute()

const projects = ref<any[]>([])
const stats = ref({ ongoing: 0, completed: 0, total: 0 })
const showModal = ref(false)
const submitting = ref(false)
const editingId = ref<string | null>(null)

const isLoggedIn = computed(() => userStore.isTokenValid())
const isManager = computed(() => userStore.hasRole('teacher', 'superadmin'))
const currentUsername = computed(() => userStore.userInfo?.username || '')
const creatorFilter = computed(() => typeof route.query.creator === 'string' ? route.query.creator.trim() : '')

const isOwner = (project: any) => Boolean(currentUsername.value && project?.created_by_username === currentUsername.value)
const canManage = (project: any) => isManager.value || isOwner(project)

const form = ref({
  title: '',
  status: '进行中',
  category: '',
  progress: 0,
  leader: '',
  members: '',
  description: '',
  cover_image: '',
  repo_url: '',
})

function statusBadge(status: string) {
  if (status === '进行中')
    return 'bg-teal-50 text-teal-700 border-teal-200'
  if (status === '已结题')
    return 'bg-gray-100 text-gray-600 border-gray-200'
  if (status === '筹备中')
    return 'bg-indigo-50 text-indigo-700 border-indigo-200'
  return 'bg-gray-100 text-gray-600 border-gray-200'
}

async function fetchProjects() {
  try {
    const params = new URLSearchParams()
    if (creatorFilter.value)
      params.set('creator', creatorFilter.value)

    const url = params.toString() ? `/api/projects/?${params.toString()}` : '/api/projects/'
    const res = await apiFetch(url, {}, { auth: false })
    if (res.ok)
      projects.value = await res.json()

    const statsRes = await apiFetch('/api/projects/stats', {}, { auth: false })
    if (statsRes.ok)
      stats.value = await statsRes.json()
  }
  catch (error) {
    console.error(error)
  }
}

function triggerUpload() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (event: any) => {
    const file = event.target.files?.[0]
    if (!file)
      return
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await apiFetch('/api/upload/', { method: 'POST', body: formData })
      if (!res.ok)
        return
      const data = await res.json()
      form.value.cover_image = withApiBase(data.url)
    }
    catch (error) {
      console.error(error)
      alert('Upload failed')
    }
  }
  input.click()
}

function openCreateModal() {
  if (!isLoggedIn.value) {
    alert('请先登录')
    return
  }
  editingId.value = null
  form.value = {
    title: '',
    status: '进行中',
    category: '',
    progress: 0,
    leader: '',
    members: '',
    description: '',
    cover_image: '',
    repo_url: '',
  }
  showModal.value = true
}

function openEditModal(project: any) {
  if (!canManage(project)) {
    alert('无权限编辑该项目')
    return
  }
  editingId.value = project.id
  form.value = {
    ...project,
    members: Array.isArray(project.members) ? project.members.join(', ') : '',
  }
  showModal.value = true
}

async function submitProject() {
  if (!form.value.title) {
    alert('请输入项目标题')
    return
  }

  submitting.value = true
  try {
    const payload = {
      ...form.value,
      progress: parseInt(String(form.value.progress || 0), 10) || 0,
      members: form.value.members.split(/[,，]/).map(item => item.trim()).filter(Boolean),
    }

    const url = editingId.value ? `/api/projects/${editingId.value}` : '/api/projects/'
    const method = editingId.value ? 'PUT' : 'POST'

    const res = await apiFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '操作失败')
      return
    }

    showModal.value = false
    await fetchProjects()
    alert(editingId.value ? '项目修改成功' : '项目创建成功')
  }
  catch (error) {
    console.error(error)
  }
  finally {
    submitting.value = false
  }
}

async function deleteProject(project: any) {
  if (!canManage(project)) {
    alert('无权限删除该项目')
    return
  }
  if (!confirm('确认删除该项目？'))
    return

  try {
    const res = await apiFetch(`/api/projects/${project.id}`, { method: 'DELETE' })
    if (res.ok)
      await fetchProjects()
  }
  catch (error) {
    console.error(error)
  }
}

watch(() => route.query.creator, fetchProjects)
onMounted(fetchProjects)
</script>

<template>
  <div class="mx-auto min-h-screen max-w-7xl px-6 py-10">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 class="text-4xl font-serif font-bold text-gray-900 dark:text-gray-100">项目记录</h1>
        <p class="mt-2 text-sm text-gray-500">Research Project Dashboard</p>
      </div>
      <button v-if="isLoggedIn" class="rounded-lg bg-teal-600 px-4 py-2 text-white transition hover:bg-teal-700" @click="openCreateModal">
        新增项目
      </button>
    </div>

    <div v-if="creatorFilter" class="mb-6 flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50 px-4 py-2 text-sm text-teal-700">
      <span>当前仅展示 @{{ creatorFilter }} 的项目</span>
      <RouterLink to="/projects" class="hover:underline">清除筛选</RouterLink>
    </div>

    <div class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-gray-200 bg-white p-5 text-center dark:border-gray-800 dark:bg-gray-900">
        <p class="text-xs uppercase tracking-wider text-gray-500">进行中</p>
        <p class="mt-2 text-4xl font-serif text-teal-600">{{ stats.ongoing }}</p>
      </div>
      <div class="rounded-2xl border border-gray-200 bg-white p-5 text-center dark:border-gray-800 dark:bg-gray-900">
        <p class="text-xs uppercase tracking-wider text-gray-500">已结题</p>
        <p class="mt-2 text-4xl font-serif text-gray-600">{{ stats.completed }}</p>
      </div>
      <div class="rounded-2xl border border-gray-200 bg-white p-5 text-center dark:border-gray-800 dark:bg-gray-900">
        <p class="text-xs uppercase tracking-wider text-gray-500">总数</p>
        <p class="mt-2 text-4xl font-serif text-amber-600">{{ stats.total }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="project in projects"
        :key="project.id"
        class="group overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
      >
        <div class="relative h-40 overflow-hidden bg-gray-100 dark:bg-gray-800">
          <img v-if="project.cover_image" :src="project.cover_image" class="h-full w-full object-cover transition duration-500 group-hover:scale-105">
          <div v-if="canManage(project)" class="absolute right-3 top-3 flex gap-2">
            <button class="rounded-full bg-white/90 p-2 text-teal-600" @click="openEditModal(project)">
              <div class="i-carbon-edit" />
            </button>
            <button class="rounded-full bg-white/90 p-2 text-red-500" @click="deleteProject(project)">
              <div class="i-carbon-trash-can" />
            </button>
          </div>
        </div>

        <div class="p-5">
          <div class="mb-2 flex flex-wrap items-center gap-2">
            <span class="rounded border px-2 py-0.5 text-xs" :class="statusBadge(project.status)">{{ project.status }}</span>
            <span class="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{{ project.category }}</span>
          </div>

          <h3 class="mb-2 line-clamp-1 text-lg font-semibold">{{ project.title }}</h3>
          <p class="mb-4 line-clamp-2 text-sm text-gray-500">{{ project.description }}</p>

          <div class="mb-4">
            <div class="mb-1 flex items-center justify-between text-xs text-gray-500">
              <span>进度</span>
              <span>{{ project.progress }}%</span>
            </div>
            <div class="h-1.5 rounded-full bg-gray-100">
              <div class="h-full rounded-full bg-teal-500" :style="{ width: `${project.progress || 0}%` }" />
            </div>
          </div>

          <div class="flex items-center justify-between border-t border-gray-100 pt-3 text-xs text-gray-500 dark:border-gray-800">
            <span>{{ project.leader }} · {{ (project.members || []).length }}人</span>
            <RouterLink
              v-if="project.created_by_username"
              :to="`/u/${encodeURIComponent(project.created_by_username)}`"
              class="text-teal-600 hover:underline"
            >
              @{{ project.created_by_username }}
            </RouterLink>
          </div>
        </div>
      </article>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModal = false" />
      <div class="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl dark:border-gray-800 dark:bg-gray-900">
        <h3 class="mb-6 text-xl font-semibold">{{ editingId ? '编辑项目' : '创建项目' }}</h3>

        <div class="space-y-4">
          <div class="h-32 cursor-pointer overflow-hidden rounded-lg border-2 border-dashed border-gray-300 bg-gray-50" @click="triggerUpload">
            <img v-if="form.cover_image" :src="form.cover_image" class="h-full w-full object-cover">
            <div v-else class="flex h-full items-center justify-center text-gray-400">上传封面图</div>
          </div>

          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <input v-model="form.title" placeholder="项目名称" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
            <input v-model="form.category" placeholder="分类" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <select v-model="form.status" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
              <option>进行中</option>
              <option>已结题</option>
              <option>筹备中</option>
            </select>
            <input v-model="form.repo_url" placeholder="仓库地址 (可选)" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <div>
            <label class="mb-1 block text-xs text-gray-500">项目进度 {{ form.progress }}%</label>
            <input v-model.number="form.progress" type="range" min="0" max="100" class="w-full accent-teal-600">
          </div>

          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <input v-model="form.leader" placeholder="负责人" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
            <input v-model="form.members" placeholder="成员（逗号分隔）" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <textarea v-model="form.description" rows="3" placeholder="项目描述" class="w-full rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500" />
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="px-4 py-2 text-gray-500" @click="showModal = false">取消</button>
          <button class="rounded-lg bg-teal-600 px-5 py-2 text-white disabled:opacity-60" :disabled="submitting" @click="submitProject">
            {{ submitting ? '提交中...' : (editingId ? '保存修改' : '确认创建') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
