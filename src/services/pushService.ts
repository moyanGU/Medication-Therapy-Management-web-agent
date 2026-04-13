/**
 * pushService
 * 提供浏览器端 Push 订阅/取消订阅与后端保存订阅的能力。
 * 注意：需要在 .env 中配置 VITE_VAPID_PUBLIC_KEY（仅公钥）。
 */

import { api } from '@/utils/api'

const isDebug = import.meta.env.MODE !== 'production'

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

function arrayBufferToBase64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '')
}

/**
 * 检查当前环境是否支持 Service Worker 与 PushManager
 */
export function isPushSupported(): boolean {
  const supported = 'serviceWorker' in navigator && 'PushManager' in window
  if (!supported) {
    console.warn('[pushService] Push not supported in this browser')
  }
  return supported
}

/**
 * 获取已就绪的 Service Worker Registration
 */
export async function getSWRegistration(): Promise<ServiceWorkerRegistration | null> {
  try {
    const reg = (await Promise.race([
      navigator.serviceWorker.ready
        .then(readyReg => readyReg)
        .catch(() => null),
      new Promise<null>(resolve => {
        window.setTimeout(() => resolve(null), 5000)
      }),
    ])) as ServiceWorkerRegistration | null
    if (reg) {
      return reg
    }
    const fallbackReg = await navigator.serviceWorker.getRegistration()
    if (fallbackReg) {
      return fallbackReg
    }
    console.warn('[pushService] Service Worker ready timeout')
    return null
  } catch (error) {
    if (isDebug) {
      console.error('[pushService] getSWRegistration failed', error)
    } else {
      console.error('[pushService] getSWRegistration failed')
    }
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
    if (isDebug) {
      console.log('[pushService] current subscription exists', !!sub)
    }
    return sub
  } catch (error) {
    if (isDebug) {
      console.error('[pushService] getSubscription error', error)
    } else {
      console.error('[pushService] getSubscription error')
    }
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
      const existingSubscription = await reg.pushManager.getSubscription()
      if (existingSubscription) {
        if (isDebug) {
          console.log('[pushService] reuse existing subscription', {
            endpointLength: existingSubscription.endpoint?.length ?? 0,
          })
        }
        await saveSubscription(existingSubscription)
        return existingSubscription
      }

      const appServerKey = urlBase64ToUint8Array(vapidPublicKey)

      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: appServerKey as unknown as BufferSource,
      })
      if (isDebug) {
        console.log('[pushService] subscribed', {
          endpointLength: sub.endpoint?.length ?? 0,
        })
      }

      await saveSubscription(sub)

      return sub
    } catch (err) {
      retry++
      if (isDebug) {
        console.error(`[pushService] subscribe failed (attempt ${retry})`, err)
      } else {
        console.error(`[pushService] subscribe failed (attempt ${retry})`)
      }
      if (retry >= maxRetry) throw err
    }
  }

  throw new Error('订阅失败')
}

async function saveSubscription(subscription: PushSubscription): Promise<void> {
  const json = subscription.toJSON() as any
  const keys = {
    ...(json.keys || {}),
  } as Record<string, string>
  if (!keys.p256dh) {
    const p256dh = subscription.getKey('p256dh')
    if (p256dh) {
      keys.p256dh = arrayBufferToBase64Url(p256dh)
    }
  }
  if (!keys.auth) {
    const auth = subscription.getKey('auth')
    if (auth) {
      keys.auth = arrayBufferToBase64Url(auth)
    }
  }
  const payload = {
    endpoint: json.endpoint,
    keys,
    ua: navigator.userAgent,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    app: import.meta.env.VITE_APP_NAME || 'mtm-helper',
  }
  const resp = await api.post('/user/push-subscriptions/', payload)
  if (isDebug) {
    console.log('[pushService] save subscription resp', {
      success: resp.success,
    })
  }
  if (!resp.success) {
    throw new Error(resp.message || '保存推送订阅失败')
  }
}

/**
 * 取消订阅并尝试通知后端清理（如果有接口）
 */
export async function unsubscribeAndCleanup(): Promise<boolean> {
  const sub = await getCurrentSubscription()
  if (!sub) return false
  try {
    const ok = await sub.unsubscribe()
    if (isDebug) {
      console.log('[pushService] unsubscribed', ok)
    }
    // 可选：通知后端删除订阅（API 四要素）
    // Method: DELETE
    // URL: /api/users/push-subscriptions/
    // Body: { endpoint }
    // Response: { success: true, data: {} }
    try {
      const json = sub.toJSON() as any
      const resp = await api.delete('/user/push-subscriptions/', {
        endpoint: json.endpoint,
      })
      if (isDebug) {
        console.log('[pushService] delete subscription resp', {
          success: resp.success,
        })
      }
    } catch (delErr) {
      if (isDebug) {
        console.warn('[pushService] 后端删除订阅接口不可用或失败', delErr)
      } else {
        console.warn('[pushService] 后端删除订阅接口不可用或失败')
      }
    }
    return ok
  } catch (error) {
    if (isDebug) {
      console.error('[pushService] unsubscribe failed', error)
    } else {
      console.error('[pushService] unsubscribe failed')
    }
    return false
  }
}

/**
 * 本地测试通知（无需后端），用于确认权限与 SW 整体链路可用。
 */
export async function showLocalTestNotification(): Promise<{
  triggered: boolean
  channel: 'sw' | 'window'
}> {
  if (!('Notification' in window)) {
    throw new Error('当前浏览器不支持通知功能')
  }
  let perm = Notification.permission
  if (perm === 'default') {
    perm = await Notification.requestPermission()
  }
  if (perm !== 'granted') {
    if (isDebug) {
      console.warn('[pushService] Notification permission not granted:', perm)
    } else {
      console.warn('[pushService] Notification permission not granted')
    }
    throw new Error('通知权限未开启，请先允许通知')
  }

  const options: NotificationOptions = {
    body: '这是一个本地通知测试，用于验证权限与 SW 展示能力',
    icon: '/icons/app-icon-192.png',
    badge: '/icons/app-icon-192.png',
    data: { url: '/' },
  }

  const reg = await getSWRegistration()
  if (reg) {
    await reg.showNotification('用药提醒（本地测试）', options)
    return { triggered: true, channel: 'sw' }
  }

  if (isDebug) {
    console.warn(
      '[pushService] Service Worker not ready, fallback to window Notification'
    )
  }
  new Notification('用药提醒（本地测试）', options)
  return { triggered: true, channel: 'window' }
}
