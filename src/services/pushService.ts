/**
 * pushService
 * 提供浏览器端 Push 订阅/取消订阅与后端保存订阅的能力。
 * 注意：需要在 .env 中配置 VITE_VAPID_PUBLIC_KEY（仅公钥）。
 */

import { api } from '@/utils/api'

/**
 * 将 base64-url 编码的 VAPID 公钥转换为 Uint8Array，供 PushManager.subscribe 使用。
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

/**
 * 检查当前环境是否支持 Service Worker 与 PushManager
 */
export function isPushSupported(): boolean {
  const supported = 'serviceWorker' in navigator && 'PushManager' in window
  if (!supported) console.warn('[pushService] Push not supported in this browser')
  return supported
}

/**
 * 获取已就绪的 Service Worker Registration
 */
export async function getSWRegistration(): Promise<ServiceWorkerRegistration | null> {
  try {
    const reg = await navigator.serviceWorker.ready
    return reg
  } catch (error) {
    console.error('[pushService] getSWRegistration failed', error)
    return null
  }
}

/**
 * 读取环境变量中的 VAPID 公钥
 */
export function getVapidPublicKey(): string | undefined {
  const key = import.meta.env.VITE_VAPID_PUBLIC_KEY as string | undefined
  if (!key) {
    console.warn('[pushService] VITE_VAPID_PUBLIC_KEY is missing in env')
  }
  return key
}

/**
 * 查询当前订阅对象
 */
export async function getCurrentSubscription(): Promise<PushSubscription | null> {
  if (!isPushSupported()) return null
  const reg = await getSWRegistration()
  if (!reg) return null
  try {
    const sub = await reg.pushManager.getSubscription()
    console.log('[pushService] current subscription', sub)
    return sub
  } catch (error) {
    console.error('[pushService] getSubscription error', error)
    return null
  }
}

/**
 * 订阅推送并保存到后端
 * 返回订阅对象；失败时抛出错误。
 */
export async function subscribeAndSave(): Promise<PushSubscription> {
  if (!isPushSupported()) throw new Error('当前浏览器不支持推送')
  const reg = await getSWRegistration()
  if (!reg) throw new Error('Service Worker 未就绪')

  const vapidPublicKey = getVapidPublicKey()
  if (!vapidPublicKey) throw new Error('缺少 VAPID 公钥配置')

  let retry = 0
  const maxRetry = 3
  while (retry < maxRetry) {
    try {
      // applicationServerKey 类型兼容处理：部分 TypeScript DOM 定义要求 ArrayBuffer
      // 将 Uint8Array 的底层 buffer 作为 ArrayBuffer 传入，避免类型不兼容报错
      const keyArray = urlBase64ToUint8Array(vapidPublicKey)
      const appServerKey: ArrayBuffer = keyArray.buffer as ArrayBuffer

      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: appServerKey,
      })
      console.log('[pushService] subscribed', sub)

      // 保存到后端（API 四要素：URL/Method/Body/Response）
      // Method: POST
      // URL: /api/users/push-subscriptions/
      // Body: { endpoint, keys: {p256dh, auth}, ua, timeZone, app }
      // Response: { success: true, data: { id } }
      try {
        const json = sub.toJSON() as any
        const payload = {
          endpoint: json.endpoint,
          keys: json.keys,
          ua: navigator.userAgent,
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          app: import.meta.env.VITE_APP_NAME || 'mtm-helper',
        }
        const resp = await api.post('/users/push-subscriptions/', payload)
        console.log('[pushService] save subscription resp', resp)
      } catch (saveError) {
        console.error('[pushService] 保存订阅到后端失败', saveError)
        // 按规则：不展示模拟数据，记日志并将问题交由后端处理
      }

      return sub
    } catch (err) {
      retry++
      console.error(`[pushService] subscribe failed (attempt ${retry})`, err)
      if (retry >= maxRetry) throw err
    }
  }

  throw new Error('订阅失败')
}

/**
 * 取消订阅并尝试通知后端清理（如果有接口）
 */
export async function unsubscribeAndCleanup(): Promise<boolean> {
  const sub = await getCurrentSubscription()
  if (!sub) return false
  try {
    const ok = await sub.unsubscribe()
    console.log('[pushService] unsubscribed', ok)
    // 可选：通知后端删除订阅（API 四要素）
    // Method: DELETE
    // URL: /api/users/push-subscriptions/
    // Body: { endpoint }
    // Response: { success: true, data: {} }
    try {
      const json = sub.toJSON() as any
      const resp = await api.delete('/users/push-subscriptions/', { endpoint: json.endpoint })
      console.log('[pushService] delete subscription resp', resp)
    } catch (delErr) {
      console.warn('[pushService] 后端删除订阅接口不可用或失败', delErr)
    }
    return ok
  } catch (error) {
    console.error('[pushService] unsubscribe failed', error)
    return false
  }
}

/**
 * 本地测试通知（无需后端），用于确认权限与 SW 整体链路可用。
 */
export async function showLocalTestNotification(): Promise<void> {
  if (!('Notification' in window)) {
    console.warn('[pushService] Notification not available in window')
    return
  }
  const perm = Notification.permission
  if (perm !== 'granted') {
    console.warn('[pushService] Notification permission not granted:', perm)
    return
  }
  const reg = await getSWRegistration()
  if (!reg) {
    console.warn('[pushService] Service Worker not ready')
    return
  }
  await reg.showNotification('用药提醒（本地测试）', {
    body: '这是一个本地通知测试，用于验证权限与 SW 展示能力',
    icon: '/icons/app-icon-192.png',
    badge: '/icons/app-icon-192.png',
    data: { url: '/' },
  })
}