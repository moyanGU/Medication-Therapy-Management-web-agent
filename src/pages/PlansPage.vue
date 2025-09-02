<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">用药计划</h1>
            <p class="text-gray-600 mt-1">制定和管理您的用药方案</p>
          </div>
          <button class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            创建计划
          </button>
        </div>
      </div>

      <!-- 冲突检测提醒 -->
      <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-orange-800">用药安全提醒</h3>
            <div class="mt-2 text-sm text-orange-700">
              <p>在制定用药计划时，请注意药物之间的相互作用。如有疑问，请及时咨询您的医生或药师。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 计划分类标签 -->
      <div class="mb-6">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
              全部计划
            </button>
            <button class="border-blue-500 text-blue-600 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
              长期用药
            </button>
            <button class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
              短期用药
            </button>
            <button class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
              已完成
            </button>
          </nav>
        </div>
      </div>

      <!-- 用药计划列表 -->
      <div class="space-y-6">
        <!-- 长期用药计划 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">高血压治疗方案</h3>
                <p class="text-sm text-gray-600">长期用药计划 · 2024-01-01 开始</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  进行中
                </span>
                <button class="text-gray-400 hover:text-gray-500">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <!-- 药品项 -->
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-4">
                  <img
                    src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20tablet&image_size=square"
                    alt="药品图片"
                    class="w-12 h-12 rounded-lg object-cover"
                  />
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">降压药</h4>
                    <p class="text-sm text-gray-600">5mg × 1片</p>
                    <p class="text-xs text-gray-500">每日2次，早晚空腹服用</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium text-gray-900">剩余 25 天</div>
                  <div class="text-xs text-gray-500">预计用完：2025-02-15</div>
                </div>
              </div>

              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-4">
                  <img
                    src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20capsule&image_size=square"
                    alt="药品图片"
                    class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                  />
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">阿司匹林肠溶片</h4>
                    <p class="text-sm text-gray-600">100mg × 1片</p>
                    <p class="text-xs text-gray-500">每日1次，饭后服用</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium text-gray-900">剩余 30 天</div>
                  <div class="text-xs text-gray-500">预计用完：2025-02-20</div>
                </div>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-200">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">计划进度</span>
                <span class="font-medium text-gray-900">第 21 天 / 长期</span>
              </div>
              <div class="mt-2">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full" style="width: 65%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 短期用药计划 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">感冒治疗方案</h3>
                <p class="text-sm text-gray-600">短期用药计划 · 2025-01-15 开始</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  进行中
                </span>
                <button class="text-gray-400 hover:text-gray-500">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-4">
                  <img
                    src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20pill&image_size=square"
                    alt="药品图片"
                    class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                  />
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">感冒灵颗粒</h4>
                    <p class="text-sm text-gray-600">1袋</p>
                    <p class="text-xs text-gray-500">每日3次，饭后温水冲服</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium text-gray-900">剩余 3 天</div>
                  <div class="text-xs text-gray-500">预计用完：2025-01-25</div>
                </div>
              </div>

              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-4">
                  <img
                    src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20injection&image_size=square"
                    alt="药品图片"
                    class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                  />
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">维生素C片</h4>
                    <p class="text-sm text-gray-600">100mg × 2片</p>
                    <p class="text-xs text-gray-500">每日1次，饭后服用</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium text-orange-600">库存不足</div>
                  <div class="text-xs text-gray-500">剩余 2 天</div>
                </div>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-200">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">计划进度</span>
                <span class="font-medium text-gray-900">第 7 天 / 共 10 天</span>
              </div>
              <div class="mt-2">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full" style="width: 70%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 已完成的计划 -->
        <div class="bg-white rounded-lg shadow opacity-75">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">胃炎治疗方案</h3>
                <p class="text-sm text-gray-600">短期用药计划 · 2024-12-01 - 2024-12-14</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  已完成
                </span>
                <button class="text-gray-400 hover:text-gray-500">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-4">
                  <img
                    src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20syrup&image_size=square"
                    alt="药品图片"
                    class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                  />
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">奥美拉唑肠溶胶囊</h4>
                    <p class="text-sm text-gray-600">20mg × 1粒</p>
                    <p class="text-xs text-gray-500">每日1次，早餐前空腹服用</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium text-green-600">已完成</div>
                  <div class="text-xs text-gray-500">14天疗程</div>
                </div>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-200">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">计划进度</span>
                <span class="font-medium text-green-600">已完成 14 天</span>
              </div>
              <div class="mt-2">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-green-600 h-2 rounded-full" style="width: 100%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 冲突检测结果 -->
      <div class="mt-8 bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">药物相互作用检测</h3>
        </div>
        <div class="p-6">
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-900">当前用药方案安全</h4>
              <p class="text-sm text-gray-600 mt-1">未检测到明显的药物相互作用。请继续按照医嘱服用。</p>
              <p class="text-xs text-gray-500 mt-2">最后检测时间：2025-01-22 14:30</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 用药计划页面组件
 * 管理长期和短期用药计划，检测药物冲突
 */
</script>