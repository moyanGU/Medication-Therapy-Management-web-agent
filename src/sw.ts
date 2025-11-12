/*
 * 自定义 Service Worker（injectManifest）
 * 功能：
 * 1) 预缓存与运行时缓存策略（Workbox）
 * 2) Push 事件展示通知
 * 3) notificationclick 交互（聚焦/跳转）
 * 4) SKIP_WAITING 消息处理与更新激活
 */

// 说明：本文件由 vite-plugin-pwa 在构建时注入 __WB_MANIFEST，用于 precache。
// 参考官方文档以保持与最新 API 对齐。

import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { CacheFirst, StaleWhileRevalidate } from 'workbox-strategies'
import { clientsClaim } from 'workbox-core'

// 使用 webworker 类型定义，避免手动声明 self 导致类型不一致问题
const swSelf = self as any


// 预缓存构建产物
// @ts-ignore: __WB_MANIFEST 由 Workbox 在构建时注入
precacheAndRoute(self.__WB_MANIFEST)
cleanupOutdatedCaches()
clientsClaim()

// 运行时缓存：构建产物静态资源
registerRoute(
  ({ url }) => url.origin === swSelf.location.origin && url.pathname.startsWith('/assets/'),
  new CacheFirst({
    cacheName: 'assets-cache',
  }),
)

// 运行时缓存：图片资源
registerRoute(
  ({ request }) => request.destination === 'image',
  new StaleWhileRevalidate({
    cacheName: 'image-cache',
  }),
)

// Push 事件：展示通知
// Push 事件：展示通知
// 某些 TS DOM 定义下 PushEvent 类型可能不可用，这里使用 any 增强兼容性
swSelf.addEventListener('push', (event: any) => {
  // 打印关键日志便于调试
  console.log('[SW] push event received', event)

  const payload = (() => {
    try {
      return event.data ? event.data.json() : {}
    } catch (e) {
      console.warn('[SW] push payload parse failed, fallback to text', e)
      return { title: '用药提醒', body: event.data?.text() || '您有新的提醒' }
    }
  })()

  const title = payload.title || '用药提醒'
  const options: NotificationOptions = {
    body: payload.body || '请按计划服药或查看提醒详情',
    icon: '/icons/app-icon-192.png',
    badge: '/icons/app-icon-192.png',
    data: payload.data || {},
    // 声明为高优先级（部分浏览器支持情况不同）
    tag: payload.tag || 'mtm-reminder',
    requireInteraction: false,
  }

  event.waitUntil(swSelf.registration.showNotification(title, options))
})

// 点击通知：聚焦或打开页面
// 点击通知：聚焦或打开页面
swSelf.addEventListener('notificationclick', (event: any) => {
  console.log('[SW] notification click', event)
  event.notification.close()
  const targetUrl: string | undefined = (event.notification as any).data?.url || '/' // 默认首页

  event.waitUntil(
    (async () => {
      const allClients = await swSelf.clients.matchAll({ type: 'window', includeUncontrolled: true })
      for (const client of allClients) {
        const url = new URL(client.url)
        if (url.pathname === '/' || url.pathname === new URL(targetUrl, swSelf.location.origin).pathname) {
          await client.focus()
          return
        }
      }
      await swSelf.clients.openWindow(targetUrl)
    })(),
  )
})

// 立即激活新 SW 的消息处理
// 立即激活新 SW 的消息处理
swSelf.addEventListener('message', (event: any) => {
  const msg = event.data
  if (!msg) return
  console.log('[SW] message', msg)
  if (msg.type === 'SKIP_WAITING') {
    swSelf.skipWaiting()
    console.log('[SW] skipWaiting executed')
  }
})

// 安装阶段日志
// 安装阶段日志
swSelf.addEventListener('install', (event: any) => {
  console.log('[SW] installed at', new Date().toISOString())
})

// 激活阶段：声明控制权
swSelf.addEventListener('activate', (event: any) => {
  console.log('[SW] activated at', new Date().toISOString())
})
/// <reference lib="webworker" />