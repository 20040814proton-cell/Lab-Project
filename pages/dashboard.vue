<script setup lang="ts">
import { ref } from 'vue'
import ListPosts from '~/components/ListPosts.vue'
import NewsPostEditorModal from '~/components/news/NewsPostEditorModal.vue'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const listPostsRef = ref<InstanceType<typeof ListPosts> | null>(null)
const showPostModal = ref(false)
const editingPost = ref<any | null>(null)

const openCreateModal = () => {
  editingPost.value = null
  showPostModal.value = true
}

const handleEdit = (post: any) => {
  editingPost.value = post
  showPostModal.value = true
}

const handleSaved = () => {
  showPostModal.value = false
  listPostsRef.value?.fetchPosts()
}
</script>

<template>
  <div class="prose m-auto p-4 md:p-10 max-w-6xl">
    <div class="mb-8 flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-serif mb-2">实验室动态面板</h1>
        <p class="opacity-60 text-sm">
          动态发布入口已统一，支持完整 Markdown 编辑、封面上传、草稿式编辑体验。
        </p>
      </div>
      <button
        v-if="userStore.hasRole('teacher', 'superadmin')"
        class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition not-prose"
        @click="openCreateModal"
      >
        + 发布动态
      </button>
    </div>

    <ListPosts ref="listPostsRef" layout="grid" view-base="/news" @edit="handleEdit" />

    <NewsPostEditorModal
      v-model="showPostModal"
      :post-id="editingPost?.id || null"
      :initial-post="editingPost"
      @saved="handleSaved"
    />
  </div>
</template>

