<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch, withApiBase } from '~/logics/api'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const route = useRoute()

const loading = ref(false)
const list = ref<any[]>([])
const search = ref('')
const currentTab = ref('全部')

const tabs = ['全部', '工具软件', '开发套件', '开发库', '其他']

const showModal = ref(false)
const saving = ref(false)
const editingId = ref<string | null>(null)
const form = ref({
  name: '',
  version: '',
  category: '工具软件',
  size: '',
  description: '',
  download_url: '',
  cover_image: '',
})

const fileInput = ref<HTMLInputElement | null>(null)

const isLoggedIn = computed(() => userStore.isTokenValid())
const isManager = computed(() => userStore.hasRole('teacher', 'superadmin'))
const currentUsername = computed(() => userStore.userInfo?.username || '')
const creatorFilter = computed(() => typeof route.query.creator === 'string' ? route.query.creator.trim() : '')

const isOwner = (item: any) => Boolean(currentUsername.value && item?.created_by_username === currentUsername.value)
const canManage = (item: any) => isManager.value || isOwner(item)

const filteredList = computed(() => {
  let result = list.value
  if (currentTab.value !== '全部')
    result = result.filter(item => item.category === currentTab.value)

  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    result = result.filter(item =>
      String(item.name || '').toLowerCase().includes(q)
      || String(item.description || '').toLowerCase().includes(q),
    )
  }

  return result
})

async function fetchList() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (creatorFilter.value)
      params.set('creator', creatorFilter.value)

    const url = params.toString() ? `/api/software/?${params.toString()}` : '/api/software/'
    const res = await apiFetch(url, {}, { auth: false })
    if (res.ok)
      list.value = await res.json()
  }
  catch (error) {
    console.error(error)
  }
  finally {
    loading.value = false
  }
}

function openCreateModal() {
  if (!isLoggedIn.value) {
    alert('请先登录')
    return
  }
  editingId.value = null
  form.value = {
    name: '',
    version: '',
    category: '工具软件',
    size: '',
    description: '',
    download_url: '',
    cover_image: '',
  }
  showModal.value = true
}

function openEditModal(item: any) {
  if (!canManage(item)) {
    alert('无权限编辑该资源')
    return
  }
  editingId.value = item.id
  form.value = {
    name: item.name || '',
    version: item.version || '',
    category: item.category || '工具软件',
    size: item.size || '',
    description: item.description || '',
    download_url: item.download_url || '',
    cover_image: item.cover_image || '',
  }
  showModal.value = true
}

function triggerUpload() {
  fileInput.value?.click()
}

async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.[0])
    return

  const formData = new FormData()
  formData.append('file', input.files[0])

  try {
    const res = await apiFetch('/api/upload/', {
      method: 'POST',
      body: formData,
    })
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

async function submitSoftware() {
  if (!form.value.name || !form.value.download_url) {
    alert('请填写名称与下载链接')
    return
  }

  saving.value = true
  try {
    const url = editingId.value ? `/api/software/${editingId.value}` : '/api/software/'
    const method = editingId.value ? 'PUT' : 'POST'

    const res = await apiFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '操作失败')
      return
    }

    showModal.value = false
    editingId.value = null
    await fetchList()
  }
  catch (error) {
    console.error(error)
  }
  finally {
    saving.value = false
  }
}

async function deleteItem(item: any) {
  if (!canManage(item)) {
    alert('无权限删除该资源')
    return
  }
  if (!confirm('确认删除？'))
    return

  try {
    const res = await apiFetch(`/api/software/${item.id}`, { method: 'DELETE' })
    if (res.ok)
      await fetchList()
  }
  catch (error) {
    console.error(error)
  }
}

async function handleDownload(item: any) {
  window.open(item.download_url, '_blank')

  try {
    await apiFetch(`/api/software/${item.id}/download`, { method: 'POST' }, { auth: false })
    item.download_count = (item.download_count || 0) + 1
  }
  catch (error) {
    console.error(error)
  }
}

watch(() => route.query.creator, fetchList)
onMounted(fetchList)
</script>

<template>
  <div class="mx-auto min-h-screen max-w-7xl px-6 pb-20 pt-24">
    <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 class="text-3xl font-serif font-bold text-gray-900 dark:text-gray-100">软件资源</h1>
        <p class="mt-2 text-sm text-gray-500">Software & Tools</p>
      </div>

      <div class="flex items-center gap-3">
        <div class="relative">
          <div class="i-carbon-search pointer-events-none absolute left-3 top-2.5 text-gray-400" />
          <input
            v-model="search"
            type="text"
            placeholder="搜索资源..."
            class="w-64 rounded-full border border-gray-200 bg-white py-2 pl-9 pr-3 text-sm outline-none transition focus:border-teal-500 dark:border-gray-700 dark:bg-gray-800"
          >
        </div>

        <button v-if="isLoggedIn" class="rounded-full bg-teal-600 px-4 py-2 text-white transition hover:bg-teal-700" @click="openCreateModal">
          添加资源
        </button>
      </div>
    </div>

    <div v-if="creatorFilter" class="mb-6 flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50 px-4 py-2 text-sm text-teal-700">
      <span>当前仅展示 @{{ creatorFilter }} 发布的软件</span>
      <RouterLink to="/downloads" class="hover:underline">清除筛选</RouterLink>
    </div>

    <div class="mb-6 flex flex-wrap gap-2">
      <button
        v-for="tab in tabs"
        :key="tab"
        class="rounded-full border px-4 py-1.5 text-sm"
        :class="currentTab === tab ? 'border-teal-600 bg-teal-600 text-white' : 'border-gray-200 bg-white text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300'"
        @click="currentTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="loading" class="py-16 text-center text-gray-400">
      <div class="i-carbon-circle-dash mx-auto mb-2 animate-spin text-3xl" />
      Loading...
    </div>

    <div v-else class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="item in filteredList"
        :key="item.id"
        class="group overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
      >
        <div class="relative aspect-video overflow-hidden bg-gray-100 dark:bg-gray-800">
          <img v-if="item.cover_image" :src="item.cover_image" class="h-full w-full object-cover transition duration-500 group-hover:scale-105">
          <div v-else class="i-carbon-application flex h-full w-full items-center justify-center text-4xl text-gray-300" />

          <div v-if="canManage(item)" class="absolute right-3 top-3 flex gap-2">
            <button class="rounded-full bg-white/90 p-2 text-teal-600" @click="openEditModal(item)">
              <div class="i-carbon-edit" />
            </button>
            <button class="rounded-full bg-white/90 p-2 text-red-500" @click="deleteItem(item)">
              <div class="i-carbon-trash-can" />
            </button>
          </div>
        </div>

        <div class="p-5">
          <div class="mb-2 flex items-start justify-between gap-2">
            <h3 class="line-clamp-1 text-lg font-semibold">{{ item.name }}</h3>
            <span class="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{{ item.version }}</span>
          </div>

          <div class="mb-3 flex items-center gap-3 text-xs text-gray-500">
            <span>{{ item.category }}</span>
            <span>·</span>
            <span>{{ item.size }}</span>
          </div>

          <p class="mb-4 line-clamp-2 text-sm text-gray-500">{{ item.description }}</p>

          <div class="flex items-center justify-between border-t border-gray-100 pt-3 text-xs text-gray-500 dark:border-gray-800">
            <div>
              <div>{{ item.download_count || 0 }} 次下载</div>
              <RouterLink
                v-if="item.created_by_username"
                :to="`/u/${encodeURIComponent(item.created_by_username)}`"
                class="text-teal-600 hover:underline"
              >
                @{{ item.created_by_username }}
              </RouterLink>
            </div>
            <button class="rounded-md bg-teal-50 px-3 py-1.5 text-sm font-medium text-teal-600 transition hover:bg-teal-600 hover:text-white" @click="handleDownload(item)">
              立即下载
            </button>
          </div>
        </div>
      </article>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showModal = false">
      <div class="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-900">
        <div class="flex items-center justify-between border-b border-gray-100 px-6 py-4 dark:border-gray-800">
          <h3 class="text-lg font-semibold">{{ editingId ? '编辑软件资源' : '添加软件资源' }}</h3>
          <button class="i-carbon-close text-xl text-gray-400" @click="showModal = false" />
        </div>

        <div class="space-y-4 p-6">
          <div class="h-32 cursor-pointer overflow-hidden rounded-lg border-2 border-dashed border-gray-300 bg-gray-50" @click="triggerUpload">
            <img v-if="form.cover_image" :src="form.cover_image" class="h-full w-full object-cover">
            <div v-else class="flex h-full items-center justify-center text-gray-400">点击上传封面</div>
          </div>
          <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="handleUpload">

          <div class="grid grid-cols-2 gap-3">
            <input v-model="form.name" placeholder="软件名称" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
            <input v-model="form.version" placeholder="版本" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <div class="grid grid-cols-2 gap-3">
            <select v-model="form.category" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
              <option v-for="tab in tabs.slice(1)" :key="tab" :value="tab">{{ tab }}</option>
            </select>
            <input v-model="form.size" placeholder="大小" class="rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          </div>

          <input v-model="form.download_url" placeholder="下载链接" class="w-full rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500">
          <textarea v-model="form.description" rows="3" placeholder="简介" class="w-full rounded-lg border border-gray-200 px-3 py-2 outline-none focus:border-teal-500" />
        </div>

        <div class="flex justify-end px-6 pb-6">
          <button class="rounded-lg bg-teal-600 px-6 py-2 text-white disabled:opacity-60" :disabled="saving" @click="submitSoftware">
            {{ saving ? '提交中...' : (editingId ? '保存修改' : '发布资源') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
