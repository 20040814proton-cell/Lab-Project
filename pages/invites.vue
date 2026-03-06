<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '~/logics/api'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const list = ref<any[]>([])
const form = ref({
  role: 'student',
  max_uses: 1,
  expires_at: '',
  note: '',
})
const includeInactive = ref(false)
const batchCount = ref(1)
const creating = ref(false)
const copiedCode = ref<string | null>(null)
const selectedIds = ref<string[]>([])

const fetchInvites = async () => {
  loading.value = true
  try {
    const res = await apiFetch(`/api/invites/?include_inactive=${includeInactive.value ? 'true' : 'false'}`)
    if (res.ok)
      list.value = await res.json()
    selectedIds.value = []
  } finally {
    loading.value = false
  }
}

const createInvite = async () => {
  creating.value = true
  try {
    const payload: any = {
      role: form.value.role,
      max_uses: Number(form.value.max_uses || 1),
      note: form.value.note || undefined,
      expires_at: form.value.expires_at ? new Date(form.value.expires_at).toISOString() : undefined,
    }
    const count = Math.max(1, Number(batchCount.value || 1))
    for (let i = 0; i < count; i++) {
      const res = await apiFetch('/api/invites/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        alert(err.detail || '创建失败')
        break
      }
    }
    form.value = { role: 'student', max_uses: 1, expires_at: '', note: '' }
    await fetchInvites()
  } finally {
    creating.value = false
  }
}

const disableInvite = async (id: string) => {
  const res = await apiFetch(`/api/invites/${id}`, { method: 'DELETE' })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    alert(err.detail || '作废失败')
    return
  }
  await fetchInvites()
}

const selectedActiveIds = computed(() => {
  return selectedIds.value.filter((id) => {
    const item = list.value.find(i => i.id === id)
    return item?.is_active
  })
})

const allVisibleIds = computed(() => list.value.map(i => i.id))
const isAllSelected = computed(() => (
  allVisibleIds.value.length > 0
  && allVisibleIds.value.every(id => selectedIds.value.includes(id))
))

const toggleSelectAll = () => {
  if (isAllSelected.value)
    selectedIds.value = []
  else
    selectedIds.value = [...allVisibleIds.value]
}

const batchDisable = async () => {
  if (!selectedActiveIds.value.length)
    return
  for (const id of selectedActiveIds.value) {
    const res = await apiFetch(`/api/invites/${id}`, { method: 'DELETE' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '批量作废失败')
      break
    }
  }
  await fetchInvites()
}

const exportCsv = () => {
  if (!list.value.length)
    return
  const header = ['code', 'role', 'max_uses', 'used_count', 'expires_at', 'is_active', 'note', 'created_by', 'created_at']
  const rows = list.value.map((i) => ([
    i.code,
    i.role,
    i.max_uses,
    i.used_count,
    i.expires_at || '',
    i.is_active ? 'true' : 'false',
    i.note || '',
    i.created_by || '',
    i.created_at || '',
  ]))
  const csv = [header, ...rows]
    .map(row => row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(','))
    .join('\n')
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `invites-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const isExpired = (expiresAt?: string) => {
  if (!expiresAt)
    return false
  return new Date(expiresAt).getTime() < Date.now()
}

const copyInvite = async (code: string) => {
  try {
    await navigator.clipboard?.writeText(code)
    copiedCode.value = code
    setTimeout(() => {
      if (copiedCode.value === code)
        copiedCode.value = null
    }, 1500)
  } catch {
    alert('复制失败')
  }
}

onMounted(fetchInvites)
</script>

<template>
  <div class="min-h-screen pt-24 px-6 pb-20 max-w-5xl mx-auto">
    <h1 class="text-2xl font-serif font-bold mb-6">邀请码管理</h1>

    <div v-if="!userStore.hasRole('superadmin')" class="p-4 rounded-lg bg-red-50 text-red-600 mb-6">
      仅超级账号可访问此页面。    </div>

    <div v-else>
      <div class="mb-8 p-5 rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-gray-400">角色</label>
            <select v-model="form.role" class="w-full p-2 mt-1 bg-gray-50 dark:bg-gray-800 rounded">
              <option value="student">student</option>
              <option value="teacher">teacher</option>
              <option value="superadmin">superadmin</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-gray-400">可用次数</label>
            <input v-model.number="form.max_uses" type="number" min="1" class="w-full p-2 mt-1 bg-gray-50 dark:bg-gray-800 rounded" />
          </div>
          <div>
            <label class="text-xs text-gray-400">过期时间（可选）</label>
            <input v-model="form.expires_at" type="date" class="w-full p-2 mt-1 bg-gray-50 dark:bg-gray-800 rounded" />
          </div>
          <div>
            <label class="text-xs text-gray-400">备注</label>
            <input v-model="form.note" class="w-full p-2 mt-1 bg-gray-50 dark:bg-gray-800 rounded" />
          </div>
          <div>
            <label class="text-xs text-gray-400">批量生成</label>
            <input v-model.number="batchCount" type="number" min="1" class="w-full p-2 mt-1 bg-gray-50 dark:bg-gray-800 rounded" />
          </div>
          <div class="flex items-end">
            <label class="flex items-center gap-2 text-sm text-gray-500">
              <input v-model="includeInactive" type="checkbox" class="accent-teal-600" @change="fetchInvites" />
              显示已作废
            </label>
          </div>
        </div>
        <div class="mt-4 flex flex-wrap gap-3 justify-end">
          <button class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg" @click="exportCsv">
            导出 CSV
          </button>
          <button
            class="px-4 py-2 border border-red-200 text-red-600 rounded-lg disabled:opacity-40"
            :disabled="!selectedActiveIds.length"
            @click="batchDisable"
          >
            批量作废
          </button>
          <button class="px-4 py-2 bg-teal-600 text-white rounded-lg" :disabled="creating" @click="createInvite">
            {{ creating ? '创建中...' : '创建邀请码' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center text-gray-400 py-10">Loading...</div>
      <div v-else class="space-y-3">
        <div class="flex items-center justify-between text-xs text-gray-400 px-1">
          <label class="flex items-center gap-2">
            <input type="checkbox" :checked="isAllSelected" class="accent-teal-600" @change="toggleSelectAll" />
            全选
          </label>
          <div>已选 {{ selectedIds.length }}</div>
        </div>
        <div v-for="i in list" :key="i.id" class="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 flex justify-between items-center">
          <div>
            <div class="font-mono text-sm flex items-center gap-2">
              <span>{{ i.code }}</span>
              <span v-if="!i.is_active" class="text-xs px-1.5 py-0.5 rounded bg-gray-200 text-gray-600">已作废</span>
              <span v-else-if="isExpired(i.expires_at)" class="text-xs px-1.5 py-0.5 rounded bg-amber-100 text-amber-700">已过期</span>
            </div>
            <div class="text-xs text-gray-400 mt-1">
              role: {{ i.role }}, uses: {{ i.used_count }}/{{ i.max_uses }}
              <span v-if="i.expires_at">, expires: {{ new Date(i.expires_at).toLocaleDateString() }}</span>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <input v-model="selectedIds" type="checkbox" :value="i.id" class="accent-teal-600" />
            <button class="text-sm text-teal-600" @click="copyInvite(i.code)">
              {{ copiedCode === i.code ? '已复制' : '复制' }}
            </button>
            <button
              class="text-sm text-red-500 disabled:opacity-40"
              :disabled="!i.is_active"
              @click="disableInvite(i.id)"
            >
              作废
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



