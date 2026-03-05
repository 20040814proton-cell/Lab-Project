<script setup lang="ts">
import { useHead } from '@unhead/vue'

useHead({
  title: 'Lab Ecosystem',
  meta: [
    { name: 'description', content: 'Laboratory Ecosystem & Personal Space' },
    { name: 'theme-color', content: '#ffffff' },
  ],
})
</script>

<template>
  <NavBar />
  
  <main class="px-7 py-10 of-x-hidden">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <div :key="route.path">
          <component :is="Component" />
        </div>
      </Transition>
    </RouterView>
  </main>
  
  <Footer />
  
  <ArtPlum />
</template>

<style>
/* --- Global Overrides --- */

/* 1. Transparency */
html, body, #app, main {
  background-color: transparent !important;
}

/* 2. Z-Index Safety */
main {
  position: relative;
  z-index: 10;
}

/* 3. Typography: Songti (Serif) for Titles */
/* Beautifies all H1 headers with Songti font */
.prose h1 {
  font-family: "Noto Serif SC", "Songti SC", "SimSun", "STSong", serif !important;
  font-weight: 700 !important;
  letter-spacing: 0.15em !important;
  margin-bottom: 1.5rem !important;
  opacity: 0.9;
  background: linear-gradient(to right, #1f2937, #4b5563);
  -webkit-background-clip: text;
  background-clip: text;
}
.dark .prose h1 {
  background: linear-gradient(to right, #e5e7eb, #9ca3af);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.prose h2, .prose h3 {
  font-family: "Noto Serif SC", "Songti SC", "SimSun", serif !important;
  letter-spacing: 0.05em;
  opacity: 0.8;
}

/* 4. Utility Cleanups */
.no-underline { text-decoration: none !important; }

/* --- ✨ MIST TRANSITION ANIMATION ✨ --- */
/* --- ✨ PAGE TRANSITION ANIMATION ✨ --- */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
