/// <reference types="vite/client" />
// 添加 PWA 虚拟模块类型定义，修复 TS2307: Cannot find module 'virtual:pwa-register'
/// <reference types="vite-plugin-pwa/client" />

// 为 .vue 单文件组件提供类型声明，解决 TS2307: Cannot find module '*.vue'
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<
    Record<string, never>,
    Record<string, never>,
    any
  >
  export default component
}

// 扩展 ImportMetaEnv，提供环境变量的类型提示，避免在代码中访问 import.meta.env 时出现类型错误
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_APP_NAME?: string
  // PWA Web Push VAPID 公钥（仅前端使用公钥）
  readonly VITE_VAPID_PUBLIC_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
