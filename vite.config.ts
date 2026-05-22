import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import Inspector from 'unplugin-vue-dev-locator/vite'
import traeBadgePlugin from 'vite-plugin-trae-solo-badge'
import { VitePWA } from 'vite-plugin-pwa'

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

export default defineConfig({
  build: {
    sourcemap: 'hidden',
    outDir: 'dist',
    emptyOutDir: true,
    copyPublicDir: true,
    rollupOptions: {
      output: {
        manualChunks: createManualChunks,
      },
    },
  },
  publicDir: 'public',
  base: '/',
  plugins: [
    vue({
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
      '@': path.resolve(__dirname, './src'),
      '@page-agent/core': path.resolve(
        __dirname,
        './page-agent-main/packages/core/src/PageAgentCore.ts'
      ),
      '@page-agent/page-controller': path.resolve(
        __dirname,
        './page-agent-main/packages/page-controller/src/PageController.ts'
      ),
    },
  },
  optimizeDeps: {
    exclude: ['wouter', 'lucide-react', 'simple-icons', 'motion/react', 'page-agent', 'rough-notation'],
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      ignored: ['**/backend/venv/**', '**/backend/.venv/**'],
    },
  },
})
