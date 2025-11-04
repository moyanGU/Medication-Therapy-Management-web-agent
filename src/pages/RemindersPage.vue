<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">用药提醒</h1>
            <p class="text-gray-600 mt-1">设置和管理您的用药提醒</p>
          </div>
          <button class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加提醒
          </button>
        </div>
      </div>

      <!-- 今日提醒概览 -->
      <div class="bg-white rounded-lg shadow mb-6 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">今日提醒</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">5</div>
            <div class="text-sm text-gray-600">总提醒数</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">3</div>
            <div class="text-sm text-gray-600">已完成</div>
          </div>
          <div class="text-center p-4 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-600">2</div>
            <div class="text-sm text-gray-600">待服用</div>
          </div>
        </div>
      </div>

      <!-- 提醒列表 -->
      <div class="space-y-6">
        <!-- 活跃提醒 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">活跃提醒</h3>
          </div>
          <div class="divide-y divide-gray-200">
            <!-- 提醒项 -->
            <div class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="flex-shrink-0">
                    <img
                      src="/icons/app-icon.svg"
                      alt="药品图片"
                      class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                    />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">阿司匹林肠溶片</h4>
                    <p class="text-sm text-gray-600">100mg × 1片</p>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-xs text-gray-500">每天 08:30</span>
                      <span class="text-xs text-gray-500">饭后服用</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">下次提醒</div>
                    <div class="text-sm text-gray-600">明天 08:30</div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" checked class="sr-only peer">
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                    <button class="text-gray-400 hover:text-gray-500">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="flex-shrink-0">
                    <img
                      src="/icons/app-icon.svg"
                      alt="药品图片"
                      class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                    />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">降压药</h4>
                    <p class="text-sm text-gray-600">5mg × 1片</p>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-xs text-gray-500">每天 07:00, 19:00</span>
                      <span class="text-xs text-gray-500">空腹服用</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">下次提醒</div>
                    <div class="text-sm text-orange-600">今天 19:00</div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" checked class="sr-only peer">
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                    <button class="text-gray-400 hover:text-gray-500">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="flex-shrink-0">
                    <img
                      src="/icons/app-icon.svg"
                      alt="药品图片"
                      class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                    />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">维生素C片</h4>
                    <p class="text-sm text-gray-600">100mg × 2片</p>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-xs text-gray-500">每天 20:00</span>
                      <span class="text-xs text-gray-500">饭后服用</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">下次提醒</div>
                    <div class="text-sm text-red-600">今天 20:00 (即将过期)</div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" class="sr-only peer">
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                    <button class="text-gray-400 hover:text-gray-500">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 已暂停的提醒 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">已暂停的提醒</h3>
          </div>
          <div class="divide-y divide-gray-200">
            <div class="px-6 py-4 opacity-60">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="flex-shrink-0">
                    <img
                      src="/icons/app-icon.svg"
                      alt="药品图片"
                      class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                    />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">钙片</h4>
                    <p class="text-sm text-gray-600">600mg × 1片</p>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-xs text-gray-500">每天 21:00</span>
                      <span class="text-xs text-gray-500">睡前服用</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-500">已暂停</div>
                    <div class="text-sm text-gray-400">暂停于 2025-01-10</div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" class="sr-only peer">
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                    <button class="text-gray-400 hover:text-gray-500">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 依从性统计 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">依从性统计</h3>
          </div>
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">本周依从性</h4>
                <div class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <span>按时服用</span>
                    <span class="font-medium text-green-600">85%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-green-600 h-2 rounded-full" style="width: 85%"></div>
                  </div>
                </div>
                <div class="space-y-2 mt-4">
                  <div class="flex justify-between text-sm">
                    <span>延迟服用</span>
                    <span class="font-medium text-yellow-600">10%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-yellow-600 h-2 rounded-full" style="width: 10%"></div>
                  </div>
                </div>
                <div class="space-y-2 mt-4">
                  <div class="flex justify-between text-sm">
                    <span>漏服</span>
                    <span class="font-medium text-red-600">5%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-red-600 h-2 rounded-full" style="width: 5%"></div>
                  </div>
                </div>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">提醒响应时间</h4>
                <div class="text-center">
                  <div class="text-3xl font-bold text-blue-600">2.5</div>
                  <div class="text-sm text-gray-600">分钟</div>
                  <div class="text-xs text-gray-500 mt-1">平均响应时间</div>
                </div>
                <div class="mt-4 space-y-2">
                  <div class="flex justify-between text-sm">
                    <span>立即响应 (&lt;1分钟)</span>
                    <span class="font-medium">60%</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span>5分钟内响应</span>
                    <span class="font-medium">25%</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span>超过5分钟</span>
                    <span class="font-medium">15%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 用药提醒页面组件
 * 管理用药提醒设置和查看依从性统计
 */
</script>