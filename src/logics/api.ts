import { useUserStore } from '~/stores/user'

export const API_BASE = import.meta.env.VITE_API_BASE || '/api'

function isHttpUrl(value: string) {
  return /^https?:\/\//i.test(value)
}

function normalizeBase(base: string) {
  if (!base)
    return ''
  return base.endsWith('/') ? base.slice(0, -1) : base
}

function getApiOrigin() {
  if (!isHttpUrl(API_BASE))
    return ''
  try {
    return new URL(API_BASE).origin
  }
  catch {
    return ''
  }
}

function buildUrl(path: string) {
  if (isHttpUrl(path))
    return path

  const base = normalizeBase(API_BASE)
  const suffix = path.startsWith('/') ? path : `/${path}`

  if (!base)
    return suffix

  // Avoid duplicating prefix when callers already pass '/api/...'.
  if (!isHttpUrl(base) && (suffix === base || suffix.startsWith(`${base}/`)))
    return suffix

  return `${base}${suffix}`
}

export function withApiBase(url: string) {
  if (!url)
    return url
  if (isHttpUrl(url))
    return url

  // Backend often returns '/static/...'; keep same-origin in production.
  if (url.startsWith('/static/')) {
    const origin = getApiOrigin()
    return origin ? `${origin}${url}` : url
  }

  return buildUrl(url)
}

function withAuthHeader(headers: HeadersInit | undefined, token: string | null) {
  const merged = new Headers(headers || {})
  if (token)
    merged.set('Authorization', `Bearer ${token}`)
  return merged
}

function handleUnauthorized() {
  const userStore = useUserStore()
  if (userStore.token)
    userStore.logout()
  if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login'))
    window.location.href = '/login'
}

export async function apiFetch(path: string, init: RequestInit = {}, options: { auth?: boolean } = {}) {
  const userStore = useUserStore()
  const useAuth = options.auth !== false
  const headers = useAuth ? withAuthHeader(init.headers, userStore.token) : init.headers
  const res = await fetch(buildUrl(path), { ...init, headers })

  if (res.status === 401)
    handleUnauthorized()

  return res
}
