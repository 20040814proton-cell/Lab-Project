<script setup lang="ts">
import { ref, watch } from 'vue'
import { MdEditor } from 'md-editor-v3'
import { apiFetch, withApiBase } from '~/logics/api'
import { fullMarkdownToolbars } from '~/logics/markdown-editor'

const props = withDefaults(defineProps<{
  modelValue: boolean
  title?: string
  submitText?: string
  submitting?: boolean
  initialData?: {
    title?: string
    content?: string
    tags?: string[]
  } | null
}>(), {
  title: '发布帖子',
  submitText: '发布',
  submitting: false,
  initialData: null,
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'submit', payload: { title: string, content: string, tags: string[] }): void
}>()

const form = ref({
  title: '',
  content: '',
  tags: '',
})

watch(
  () => props.modelValue,
  (visible) => {
    if (!visible)
      return
    form.value = {
      title: props.initialData?.title ?? '',
      content: props.initialData?.content ?? '',
      tags: Array.isArray(props.initialData?.tags) ? props.initialData!.tags!.join(', ') : '',
    }
  },
)

const close = () => emit('update:modelValue', false)

const onUploadImg = async (files: File[], callback: (urls: string[]) => void) => {
  try {
    const urls = await Promise.all(files.map(async (file) => {
      const data = new FormData()
      data.append('file', file)
      const res = await apiFetch('/api/upload/', {
        method: 'POST',
        body: data,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || '图片上传失败')
      }
      const body = await res.json()
      return withApiBase(body.url)
    }))
    callback(urls)
  } catch (error: any) {
    alert(error?.message || '图片上传失败')
  }
}

const submit = () => {
  if (!form.value.title.trim() || !form.value.content.trim()) {
    alert('请填写标题和内容')
    return
  }
  const tags = form.value.tags
    ? form.value.tags.split(/[,，]/).map(s => s.trim()).filter(Boolean)
    : []
  emit('submit', {
    title: form.value.title.trim(),
    content: form.value.content,
    tags,
  })
}
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="close" />

    <div class="relative w-full max-w-3xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-100 dark:border-gray-800">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-xl font-bold">{{ title }}</h3>
        <span class="text-xs text-gray-400">支持 Markdown / 标题 / 标签 / 图片上传</span>
      </div>
      <div class="text-xs text-gray-500 mb-4">
        建议：标题清晰、标签用逗号分隔；正文可用标题、表格、代码块、引用与链接。
      </div>

      <div class="space-y-4">
        <input v-model="form.title" placeholder="标题" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none">
        <input v-model="form.tags" placeholder="标签（逗号分隔，可选）" class="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded outline-none">
        <div class="border rounded overflow-hidden">
          <MdEditor
            v-model="form.content"
            language="zh-CN"
            :toolbars="fullMarkdownToolbars"
            :on-upload-img="onUploadImg"
            :style="{ height: '360px' }"
          />
        </div>
      </div>

      <div class="mt-6 flex justify-end gap-3">
        <button class="px-4 py-2 text-gray-500" @click="close">取消</button>
        <button class="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition" :disabled="submitting" @click="submit">
          {{ submitting ? '提交中...' : submitText }}
        </button>
      </div>
    </div>
  </div>
</template>

