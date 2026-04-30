import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import Inspector from 'unplugin-vue-dev-locator/vite'
import traeBadgePlugin from 'vite-plugin-trae-solo-badge'
import { VitePWA } from 'vite-plugin-pwa'

/**
 * 仅按少量重依赖组做最小拆包，优先缓解大 chunk warning。
 */
function createManualChunks(id: string): string | undefined {
  if (!id.includes('node_modules')) {
    return undefined
  }

  if (id.includes('jspdf')) {
    return 'vendor-jspdf'
  }

  if (id.includes('html2canvas')) {
    return 'vendor-html2canvas'
  }

  if (id.includes('@page-agent/core') || id.includes('@page-agent/page-controller')) {
    return 'vendor-page-agent'
  }

  if (id.includes('sonner') || id.includes('vue-sonner')) {
    return 'vendor-toast'
  }

  return undefined
}

// https://vite.dev/config/
export default defineConfig({
  build: {
    sourcemap: 'hidden',
    outDir: 'dist',
    emptyOutDir: true,
    // 强制复制 public 目录到构建产物，避免某些环境下未拷贝导致 /icons/* 等资源缺失
    copyPublicDir: true,
    rollupOptions: {
      output: {
        manualChunks: createManualChunks,
      },
    },
  },
  // 明确声明 public 目录，确保 Vite 在不同环境下行为一致
  publicDir: 'public',
  base: '/',
  plugins: [
    vue({
      // Ensure absolute URLs like "/icons/app-icon.svg" in Vue SFC templates
      // are preserved as-is and not transformed into Rollup imports.
      // This keeps references to assets in /public working in production builds.
      template: {
        transformAssetUrls: {
          includeAbsolute: false,
        },
      },
    }),
    Inspector(),
    traeBadgePlugin({
      variant: 'dark',
      position: 'bottom-right',
      prodOnly: true,
      clickable: true,
      clickUrl: 'https://www.trae.ai/solo?showJoin=1',
      autoTheme: true,
      autoThemeTarget: '#app',
    }),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: null,
      strategies: 'injectManifest',
      srcDir: 'src',
      filename: 'sw.ts',
      devOptions: {
        enabled: true,
        type: 'module',
      },
      includeAssets: ['favicon.svg', 'icons/app-icon.svg', 'icons/maskable-icon.svg', 'icons/app-icon-192.png', 'icons/app-icon-512.png'],
      manifest: {
        name: 'MTM-用药助手',
        short_name: 'MTM',
        description: '用药管理与提醒助手',
        theme_color: '#0ea5e9',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        lang: 'zh-CN',
        id: '/',
        scope: '/',
        icons: [
          { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
          { src: '/icons/app-icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
          { src: '/icons/maskable-icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'maskable' },
          { src: '/icons/app-icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/icons/app-icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
        ],
        categories: ['health', 'medical'],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // ✅ 定义 @ = src
    },
  },
  optimizeDeps: {
    exclude: [
      'wouter',
      'lucide-react',
      'simple-icons',
      'motion/react',
      'page-agent',
      'rough-notation'
    ]
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      ignored: ['**/backend/venv/**', '**/backend/.venv/**', '**/page-agent-main/**']
    }
  }
  // 已移除 server.proxy，避免使用代理，所有请求应直接指向后端基地址
})
