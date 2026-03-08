<script setup lang="ts">
import { MdEditor } from 'md-editor-v3'
import { apiFetch, withApiBase } from '~/logics/api'
import { compactMarkdownToolbars } from '~/logics/markdown-editor'

const props = withDefaults(defineProps<{
  modelValue: string
  submitting?: boolean
  editorHeight?: number
}>(), {
  submitting: false,
  editorHeight: 180,
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void
  (e: 'submit'): void
}>()

async function onUploadImg(files: File[], callback: (urls: string[]) => void) {
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
  }
  catch (error: any) {
    alert(error?.message || '图片上传失败')
  }
}
</script>

<template>
  <div class="space-y-3">
    <div class="text-xs text-gray-500">
      评论支持 Markdown（加粗、代码、链接、图片等）
    </div>
    <div class="border rounded overflow-hidden">
      <MdEditor
        :model-value="modelValue"
        language="zh-CN"
        :toolbars="compactMarkdownToolbars"
        :style="{ height: `${props.editorHeight}px` }"
        :preview="false"
        :on-upload-img="onUploadImg"
        @update:model-value="emit('update:modelValue', $event)"
      />
    </div>
    <div class="flex justify-end">
      <button class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition" :disabled="submitting" @click="emit('submit')">
        {{ submitting ? '提交中...' : '发表评论' }}
      </button>
    </div>
  </div>
</template>
