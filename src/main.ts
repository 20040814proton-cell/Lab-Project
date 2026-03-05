import dayjs from 'dayjs'
import LocalizedFormat from 'dayjs/plugin/localizedFormat.js'
import FloatingVue from 'floating-vue'
import NProgress from 'nprogress'
import { createPinia } from 'pinia'
import { ViteSSG } from 'vite-ssg'
import { setupRouterScroller } from 'vue-router-better-scroller'
import { routes } from 'vue-router/auto-routes'
import { useUserStore } from './stores/user'
import App from './App.vue'
import '@unocss/reset/tailwind.css'

import 'floating-vue/dist/style.css';
import 'md-editor-v3/lib/style.css';

import 'markdown-it-github-alerts/styles/github-colors-light.css'
import 'markdown-it-github-alerts/styles/github-colors-dark-class.css'
import 'markdown-it-github-alerts/styles/github-base.css'
import '@shikijs/twoslash/style-rich.css'
import 'shiki-magic-move/style.css'
import './styles/main.css'
import './styles/prose.css'
import './styles/markdown.css'
import 'uno.css'

export const createApp = ViteSSG(
  App,
  {
    routes,
  },
  ({ router, app, isClient }) => {
    dayjs.extend(LocalizedFormat)

    app.use(FloatingVue)
    app.use(createPinia())

    if (isClient) {
      const html = document.querySelector('html')!
      setupRouterScroller(router, {
        selectors: {
          html(ctx) {
            // only do the sliding transition when the scroll position is not 0
            // Disable sliding transition on Dev Mode
            if (ctx.savedPosition?.top || import.meta.hot)
              html.classList.add('no-sliding')
            else
              html.classList.remove('no-sliding')
            return true
          },
        },
        behavior: 'auto',
      })

      const userStore = useUserStore()
      userStore.init()

      router.beforeEach((to, from, next) => {
        NProgress.start()
        
        // Auth Guard with Whitelist
        const publicRoutes = ['/', '/login', '/register', '/about']
        const publicPrefixes = ['/news', '/posts', '/forum', '/u']
        
        if (publicRoutes.includes(to.path) || publicPrefixes.some(p => to.path.startsWith(p))) {
           next()
           return
        }

        if (!userStore.isTokenValid()) {
           if (userStore.token)
             userStore.logout()
           next('/login')
           return
        }
        
        next()
     })
      router.afterEach(() => {
        NProgress.done()
      })
    }
  },
)
