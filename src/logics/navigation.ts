import type { Router } from 'vue-router'

export function goBackOr(router: Router, fallbackPath: string) {
  if (typeof window !== 'undefined' && window.history.length > 1) {
    router.back()
    return
  }
  router.push(fallbackPath)
}
