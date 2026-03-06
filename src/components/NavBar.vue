<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const router = useRouter()

const baseNavItems = [
  { label: '首页', path: '/dashboard', icon: 'i-carbon-home' },
  { label: '学生管理', path: '/students', icon: 'i-carbon-user-multiple' },
  { label: '教师团队', path: '/teachers', icon: 'i-carbon-education' },
  { label: '项目记录', path: '/projects', icon: 'i-carbon-folder' },
  { label: '学术活动', path: '/activities', icon: 'i-carbon-notebook' },
  { label: '软件下载', path: '/downloads', icon: 'i-carbon-download' },
  { label: '论坛', path: '/forum', icon: 'i-carbon-chat' },
]

const superAdminItems = [
  { label: '邀请码', path: '/invites', icon: 'i-carbon-ticket' },
]

const visibleNavItems = computed(() => (
  userStore.hasRole('superadmin')
    ? [...baseNavItems, ...superAdminItems]
    : baseNavItems
))

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="header z-40">
    <RouterLink
      class="w-12 h-12 absolute xl:fixed m-5 select-none outline-none"
      to="/"
      focusable="false"
    >
      <Logo />
    </RouterLink>

    <nav class="nav">
      <div class="spacer" />
      <div class="right" print:op0>
        <Transition name="fade" mode="out-in">
          <div v-if="userStore.token" key="user" class="flex gap-4 items-center">
            <RouterLink v-for="item in visibleNavItems" :key="item.path" :to="item.path" :title="item.label">
              <span class="lt-md:hidden">{{ item.label }}</span>
              <div :class="item.icon" class="md:hidden" />
            </RouterLink>

            <div class="border-l border-gray-200 dark:border-gray-700 h-6 mx-2" />

            <RouterLink to="/profile" title="个人资料" class="flex gap-2 items-center opacity-60 hover:opacity-100 transition">
              <div class="i-carbon-user-avatar" />
            </RouterLink>

            <button title="退出登录" class="flex gap-2 items-center opacity-60 hover:opacity-100 transition" @click="handleLogout">
              <div class="i-carbon-logout" />
            </button>
          </div>

          <div v-else key="guest" class="flex gap-4 items-center">
            <RouterLink to="/" title="首页" class="mr-2">
              <span class="lt-md:hidden">首页</span>
              <div class="i-carbon-home md:hidden" />
            </RouterLink>
            <RouterLink to="/forum" title="论坛" class="mr-2">
              <span class="lt-md:hidden">论坛</span>
              <div class="i-carbon-chat md:hidden" />
            </RouterLink>
            <RouterLink to="/login" title="登录" class="px-4 py-1.5 bg-teal-600 text-white rounded-full hover:bg-teal-700 transition shadow-lg shadow-teal-500/30 flex items-center gap-2 !opacity-100">
              <span class="lt-md:hidden font-medium">登录</span>
              <div class="i-carbon-login md:hidden" />
            </RouterLink>
          </div>
        </Transition>

        <ToggleTheme />
      </div>
    </nav>
  </header>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.header h1 {
  margin-bottom: 0;
}

.logo {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
}

.nav {
  padding: 2rem;
  width: 100%;
  display: grid;
  grid-template-columns: auto max-content;
  box-sizing: border-box;
}

.nav > * {
  margin: auto;
}

.nav a {
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s ease;
  opacity: 0.6;
  outline: none;
}

.nav a:hover {
  opacity: 1;
  text-decoration-color: inherit;
}

.nav .right {
  display: grid;
  grid-gap: 1.2rem;
  grid-auto-flow: column;
  align-items: center;
}
</style>
