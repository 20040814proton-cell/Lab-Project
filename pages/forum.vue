<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ForumListPage from './forum/index.vue'

const route = useRoute()
const showForumList = computed(() => /^\/forum\/?$/.test(route.path))
</script>

<template>
  <ForumListPage v-if="showForumList" />
  <RouterView v-else />
</template>
