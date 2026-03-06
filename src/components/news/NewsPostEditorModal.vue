<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { MdEditor } from 'md-editor-v3'
import { apiFetch, withApiBase } from '~/logics/api'
import { buildSummaryFromMarkdown, fullMarkdownToolbars } from '~/logics/markdown-editor'

interface NewsPostForm {
  title: string
  summary: string
  content: string
  cover_image: string
}

const props = withDefaults(defineProps<{
  modelValue: boolean
  postId?: string | null
  initialPost?: Partial<NewsPostForm> | null
}>(), {
  postId: null,
  initialPost: null,
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved'): void
}>()

const form = ref<NewsPostForm>({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
})

const submitting = ref(false)
const uploadingCover = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const editorHeight = '500px'

const isEditing = computed(() => Boolean(props.postId))
const modalTitle = computed(() => isEditing.value ? '编辑动态' : '发布动态')

watch(
  () => props.modelValue,
  (visible) => {
    if (!visible)
      return
    form.value = {
      title: props.initialPost?.title ?? '',
      summary: props.initialPost?.summary ?? '',
      content: props.initialPost?.content ?? '',
      cover_image: props.initialPost?.cover_image ?? '',
    }
  },
)

const close = () => emit('update:modelValue', false)

const triggerUpload = () => fileInput.value?.click()

const uploadFile = async (file: File) => {
  const data = new FormData()
  data.append('file', file)
  const res = await apiFetch('/api/upload/', {
    method: 'POST',
    body: data,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || '上传失败')
  }
  const body = await res.json()
  return withApiBase(body.url)
}

const handleCoverUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file)
    return
  uploadingCover.value = true
  try {
    form.value.cover_image = await uploadFile(file)
  } catch (error: any) {
    alert(error?.message || '封面上传失败')
  } finally {
    uploadingCover.value = false
    input.value = ''
  }
}

const onUploadImg = async (files: File[], callback: (urls: string[]) => void) => {
  try {
    const urls = await Promise.all(files.map(uploadFile))
    callback(urls)
  } catch (error: any) {
    alert(error?.message || '图片上传失败')
  }
}

const submit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) {
    alert('请填写标题和正文')
    return
  }
  submitting.value = true
  try {
    const summary = form.value.summary.trim() || buildSummaryFromMarkdown(form.value.content, 100)
    const payload = {
      title: form.value.title.trim(),
      summary,
      content: form.value.content,
      cover_image: form.value.cover_image || undefined,
    }
    const url = isEditing.value ? `/api/posts/${props.postId}` : '/api/posts/'
    const method = isEditing.value ? 'PUT' : 'POST'
    const res = await apiFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || '提交失败')
    }
    emit('saved')
    close()
  } catch (error: any) {
    alert(error?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="close" />

    <div class="relative w-full max-w-5xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-800 flex flex-col max-h-[90vh]">
      <div class="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
        <div>
          <h3 class="text-lg font-bold">{{ modalTitle }}</h3>
          <p class="text-xs text-gray-500 mt-1">
            支持 Markdown：标题、表格、代码块、图片、链接、预览/全屏。
          </p>
        </div>
        <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" @click="close">
          <div class="i-carbon-close text-xl" />
        </button>
      </div>

      <div class="p-6 overflow-y-auto space-y-4">
        <div
          class="w-full h-40 bg-gray-100 dark:bg-gray-800 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center cursor-pointer hover:border-teal-500 transition group overflow-hidden relative"
          @click="triggerUpload"
        >
          <img v-if="form.cover_image" :src="form.cover_image" class="absolute inset-0 w-full h-full object-cover" />
          <div v-else class="flex flex-col items-center text-gray-400 group-hover:text-teal-500 transition">
            <div class="i-carbon-image text-4xl mb-2" />
            <span class="text-sm">{{ uploadingCover ? '上传中...' : '点击上传封面图' }}</span>
          </div>
        </div>
        <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="handleCoverUpload">

        <div>
          <label class="block text-sm font-bold mb-1 text-gray-700 dark:text-gray-200">标题</label>
          <input
            v-model="form.title"
            placeholder="请输入标题..."
            class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 rounded-lg outline-none focus:ring-2 ring-teal-500/50 transition font-bold text-lg"
          >
        </div>

        <div>
          <label class="block text-sm font-bold mb-1 text-gray-700 dark:text-gray-200">
            摘要
            <span class="text-xs font-normal text-gray-400">(选填，留空自动生成)</span>
          </label>
          <input
            v-model="form.summary"
            placeholder="一句话描述..."
            class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 rounded-lg outline-none focus:ring-2 ring-teal-500/50 transition text-sm text-gray-600"
          >
        </div>

        <div>
          <label class="block text-sm font-bold mb-1 text-gray-700 dark:text-gray-200">正文内容</label>
          <div class="border rounded overflow-hidden">
            <MdEditor
              v-model="form.content"
              language="zh-CN"
              :toolbars="fullMarkdownToolbars"
              :on-upload-img="onUploadImg"
              :style="{ height: editorHeight }"
            />
          </div>
        </div>
      </div>

      <div class="p-6 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50 flex justify-end gap-3">
        <button class="px-5 py-2 text-gray-500 hover:text-gray-700" @click="close">取消</button>
        <button
          class="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition shadow-lg shadow-teal-500/20 disabled:opacity-50 flex items-center gap-2"
          :disabled="submitting"
          @click="submit"
        >
          <div v-if="submitting" class="i-carbon-circle-dash animate-spin" />
          {{ submitting ? '提交中...' : '确认提交' }}
        </button>
      </div>
    </div>
  </div>
</template>

