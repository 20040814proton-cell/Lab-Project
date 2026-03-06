---
title: ''
wrapperClass: 'prose m-auto h-[85vh] flex flex-col justify-center items-center'
---

<div class="w-full max-w-4xl flex flex-col items-center justify-center text-center relative z-20 px-4">

<HeroAnimation class="mb-12" />

<h1 class="text-4xl md:text-6xl font-bold mb-4 text-gray-900 dark:text-white tracking-wider font-serif">
实验室生态
</h1>

<p class="text-lg md:text-xl opacity-60 max-w-xl mx-auto leading-relaxed font-light mb-12 font-serif">
<span class="text-sm tracking-[0.3em] opacity-80 block mb-3 text-teal-600 dark:text-teal-400 uppercase">Explore · Record · Create</span>
格物致知 · 编码未来
</p>

<div class="flex gap-6 justify-center items-center w-full">

<a href="/login" class="no-underline px-10 py-3 rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 text-white font-serif tracking-widest shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-2">
<span class="i-carbon-login text-lg"></span>
<span>入 境</span>
</a>

<a href="/demos" class="no-underline px-10 py-3 rounded-full border border-stone-300 dark:border-stone-600 bg-white/50 dark:bg-stone-800/50 backdrop-blur-sm hover:bg-stone-50 dark:hover:bg-stone-800 transition-all duration-300 flex items-center gap-2 font-serif tracking-widest text-stone-600 dark:text-stone-300">
<span class="i-carbon-cube text-lg"></span>
<span>观 象</span>
</a>

</div>

</div>

<div class="w-full max-w-5xl mt-20 px-4 text-left">
  <div class="flex items-center gap-4 mb-8">
     <div class="h-px bg-gray-200 dark:bg-gray-800 flex-1"></div>
     <h2 class="text-2xl font-serif opacity-80">实验室动态</h2>
     <div class="h-px bg-gray-200 dark:bg-gray-800 flex-1"></div>
  </div>
  
  <ListPosts />
</div>
