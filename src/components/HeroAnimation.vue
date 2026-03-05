<script setup lang="ts">
import { onMounted, ref } from 'vue'

const logs = ref<string[]>([])
const prefersReducedMotion = ref(false)
const animationsEnabled = ref(false)
const bootSequence = [
  '[系统] 正在唤醒核心进程...',
  '[加载] 载入墨枢架构 v2.0...',
  '[链接] 正在连接至云端书库...',
  '[网络] 桃花源节点: 已连通',
  '[认证] 阁下，别来无恙',
  '[就绪] 实验室生态系统，待命。',
  '> 等待指令输入_'
]

onMounted(() => {
  prefersReducedMotion.value = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches ?? false

  // Defer animations to avoid blocking first paint
  const start = () => { animationsEnabled.value = !prefersReducedMotion.value }
  if ('requestAnimationFrame' in window)
    requestAnimationFrame(start)
  else
    setTimeout(start, 0)

  if (prefersReducedMotion.value) {
    logs.value = [...bootSequence]
    return
  }

  let lineIndex = 0
  const typeNextLine = () => {
    if (lineIndex < bootSequence.length) {
      logs.value.push(bootSequence[lineIndex])
      lineIndex++
      setTimeout(typeNextLine, Math.random() * 200 + 80)
    }
  }
  setTimeout(typeNextLine, 600)
})
</script>

<template>
  <div class="hero-root relative w-full max-w-3xl mx-auto h-[450px] flex justify-center items-center">
    
    <div class="absolute inset-0 flex justify-center items-center pointer-events-none">
      <div :class="['w-[550px] h-[550px] border-2 border-dashed border-stone-200 dark:border-stone-700 rounded-full opacity-60', animationsEnabled ? 'animate-spin-slow' : '']"></div>
      <div :class="['absolute w-[400px] h-[400px] border border-teal-500/20 dark:border-teal-400/20 rounded-full', animationsEnabled ? 'animate-spin-reverse-slow' : '']"></div>
      <div :class="['absolute w-[400px] h-[400px]', animationsEnabled ? 'animate-spin-reverse-slow' : '']">
         <div class="w-3 h-3 bg-teal-500 rounded-full shadow-lg shadow-teal-500/50 absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
      </div>
      <div class="absolute w-[300px] h-[300px] bg-teal-100/40 dark:bg-teal-900/20 rounded-full blur-3xl mix-blend-multiply dark:mix-blend-screen"></div>
    </div>

    <div :class="['absolute top-16 left-4 md:left-16 p-4 rounded-2xl bg-white dark:bg-stone-800 shadow-xl border border-stone-100 dark:border-stone-700 z-20 flex items-center gap-2', animationsEnabled ? 'animate-float-delayed' : '']">
      <div class="i-carbon-code text-2xl text-teal-600"></div>
      <span class="text-xs font-serif text-stone-500">Core.js</span>
    </div>
    <div :class="['absolute bottom-24 right-4 md:right-16 p-4 rounded-2xl bg-white dark:bg-stone-800 shadow-xl border border-stone-100 dark:border-stone-700 z-20 flex items-center gap-2', animationsEnabled ? 'animate-float' : '']">
      <div class="i-carbon-cloud text-2xl text-cyan-600"></div>
      <span class="text-xs font-serif text-stone-500">Cloud</span>
    </div>
    <div :class="['absolute top-24 right-20 md:right-32 p-3 rounded-xl bg-white/80 dark:bg-stone-800/80 backdrop-blur-md border border-stone-200 shadow-lg z-0', animationsEnabled ? 'animate-float-slower' : '']">
      <div class="i-carbon-data-base text-xl text-stone-400"></div>
    </div>

    <div :class="['relative w-full max-w-xl p-4 z-10', animationsEnabled ? 'animate-float' : '']">
      <div class="
        relative rounded-xl overflow-hidden
        bg-white/80 dark:bg-black/60 
        backdrop-blur-xl
        border border-stone-300/60 dark:border-stone-600/50
        shadow-2xl shadow-teal-900/10
        flex flex-col
        group
      ">
        
        <div :class="['absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent z-30 pointer-events-none', animationsEnabled ? 'animate-shimmer' : '']"></div>

        <div class="h-10 flex items-center px-5 justify-between border-b border-stone-200 dark:border-stone-700 bg-stone-50/50 dark:bg-stone-900/50">
          <div class="flex gap-2">
            <div class="w-3 h-3 rounded-full bg-red-300"></div>
            <div class="w-3 h-3 rounded-full bg-amber-300"></div>
            <div class="w-3 h-3 rounded-full bg-green-300"></div>
          </div>
          <div class="flex items-center gap-2">
             <div class="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse"></div>
             <div class="text-[10px] font-serif text-stone-500 tracking-widest">墨 枢 · SYSTEM</div>
          </div>
        </div>

        <div class="p-6 font-mono text-sm relative z-10 min-h-[200px]">
          <div class="flex flex-col gap-3 leading-relaxed">
            <div v-for="(log, i) in logs" :key="i" 
                 :class="{
                   'transition-colors duration-500': true, 
                   'text-teal-700 dark:text-teal-400 font-bold': log.includes('[就绪]') || log.includes('[认证]'), 
                   'text-stone-700 dark:text-stone-300': !log.includes('>') && !log.includes('[就绪]'),
                   'text-stone-400': log.includes('>')
                 }">
              {{ log }}
            </div>
            <div v-if="logs.length === bootSequence.length" class="animate-pulse text-teal-500 font-bold">_</div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes spin-reverse-slow {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}
@keyframes float-delayed {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16px); }
}
@keyframes float-slower {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(12px); }
}
@keyframes shimmer {
  0% { transform: translateX(-150%) skewX(-20deg); }
  30% { transform: translateX(150%) skewX(-20deg); }
  100% { transform: translateX(150%) skewX(-20deg); }
}

.animate-spin-slow { animation: spin-slow 40s linear infinite; }
.animate-spin-reverse-slow { animation: spin-reverse-slow 30s linear infinite; }
.animate-float { animation: float 5s ease-in-out infinite; }
.animate-float-delayed { animation: float-delayed 6s ease-in-out infinite 1s; }
.animate-float-slower { animation: float-slower 7s ease-in-out infinite 0.5s; }
.animate-shimmer { animation: shimmer 4s infinite; }

.hero-root {
  contain: layout paint;
}

.animate-spin-slow,
.animate-spin-reverse-slow,
.animate-float,
.animate-float-delayed,
.animate-float-slower,
.animate-shimmer {
  will-change: transform;
}
</style>
