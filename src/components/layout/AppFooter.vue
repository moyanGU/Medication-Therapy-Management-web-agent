<template>
  <footer class="bg-white border-t border-gray-200">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- 公司信息 -->
        <div class="col-span-1 md:col-span-2">
          <div class="flex items-center space-x-3 mb-4">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z"></path>
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900">MTM-用药助手</span>
          </div>
          <p class="text-gray-600 text-sm leading-relaxed mb-4">
            MTM-用药助手是一款专业的药物治疗管理应用，帮助用户科学管理用药，提高用药依从性，保障用药安全。
          </p>
          <div class="flex space-x-4">
            <!-- 社交媒体链接 -->
            <a href="#" class="text-gray-400 hover:text-gray-500 transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
              </svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-gray-500 transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
              </svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-gray-500 transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.746-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001.012.001z"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- 快速链接 -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 tracking-wider uppercase mb-4">快速链接</h3>
          <ul class="space-y-3">
            <li>
              <router-link to="/medicines" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                药品管理
              </router-link>
            </li>
            <li>
              <router-link to="/records" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                用药记录
              </router-link>
            </li>
            <li>
              <router-link to="/reminders" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                用药提醒
              </router-link>
            </li>
            <li>
              <router-link to="/plans" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                用药计划
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 帮助支持 -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 tracking-wider uppercase mb-4">帮助支持</h3>
          <ul class="space-y-3">
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                使用指南
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                常见问题
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                联系我们
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900 text-sm transition-colors">
                意见反馈
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- 分割线 -->
      <div class="mt-8 pt-8 border-t border-gray-200">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <!-- 版权信息 -->
          <div class="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
            <p class="text-gray-500 text-sm">
              &copy; {{ currentYear }} MTM-用药助手. 保留所有权利.
            </p>
            <div class="flex space-x-6">
              <a href="#" class="text-gray-500 hover:text-gray-900 text-sm transition-colors">
                隐私政策
              </a>
              <a href="#" class="text-gray-500 hover:text-gray-900 text-sm transition-colors">
                服务条款
              </a>
              <a href="#" class="text-gray-500 hover:text-gray-900 text-sm transition-colors">
                Cookie政策
              </a>
            </div>
          </div>

          <!-- 版本信息 -->
          <div class="mt-4 md:mt-0">
            <p class="text-gray-400 text-xs">
              版本 {{ version }} | 最后更新: {{ lastUpdated }}
            </p>
          </div>
        </div>
      </div>

      <!-- 备案信息 (如果需要) -->
      <div class="mt-4 text-center">
        <div class="flex flex-col items-center space-y-2">
          <p class="text-gray-400 text-xs">
            <a
              href="https://beian.miit.gov.cn/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="工业和信息化部ICP备案查询"
              class="hover:text-gray-600"
            >
              豫ICP备2025149475号
            </a>
          </p>
          <p class="text-gray-400 text-xs">
            <a
              href="https://beian.mps.gov.cn/#/query/webSearch?code=41020202001040"
              target="_blank"
              rel="noreferrer noopener"
              aria-label="公安机关互联网安全备案查询"
              class="inline-flex items-center hover:text-gray-600"
            >
              <img src="/icons/备案图标.png" alt="公安备案图标" class="inline-block align-[-0.125em] mr-1" width="20" height="20" />
              豫公网安备41020202001040号
            </a>
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * 应用底部组件
 * 包含公司信息、快速链接、帮助支持等
 */

// 计算属性
const currentYear = computed(() => new Date().getFullYear())
const version = '1.0.0'
const lastUpdated = '2025-01-22'
</script>

<style scoped>
/* 自定义样式 */
footer {
  margin-top: auto;
}

/* 链接悬停效果 */
a {
  transition: color 0.2s ease-in-out;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .grid {
    gap: 1.5rem;
  }
}
</style>