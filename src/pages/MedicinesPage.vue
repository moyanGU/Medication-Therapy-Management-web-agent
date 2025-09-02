<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">药品管理</h1>
            <p class="text-gray-600 mt-1">管理您的药品信息和库存</p>
          </div>
          <router-link
            to="/medicines/add"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加药品
          </router-link>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow mb-6 p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">搜索药品</label>
            <input
              type="text"
              placeholder="输入药品名称或拼音首字母"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">状态筛选</label>
            <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="">全部状态</option>
              <option value="normal">正常</option>
              <option value="low-stock">库存不足</option>
              <option value="expired">即将过期</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">排序方式</label>
            <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="name">按名称</option>
              <option value="expiry">按有效期</option>
              <option value="quantity">按库存</option>
              <option value="created">按添加时间</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 药品列表 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 药品卡片示例 -->
        <div class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200">
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">阿司匹林肠溶片</h3>
                <p class="text-sm text-gray-600">100mg × 30片</p>
                <p class="text-sm text-gray-500">拜耳医药</p>
              </div>
              <div class="ml-4">
                <img
                  src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20pill%20bottle&image_size=square"
                  alt="药品图片"
                  class="w-16 h-16 rounded-lg object-cover bg-gray-100"
                />
              </div>
            </div>

            <div class="space-y-2 mb-4">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">剩余数量:</span>
                <span class="font-medium text-gray-900">25片</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">有效期:</span>
                <span class="font-medium text-gray-900">2025-12-31</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">存储条件:</span>
                <span class="font-medium text-gray-900">阴凉干燥处</span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                正常
              </span>
              <div class="flex space-x-2">
                <router-link
                  :to="`/medicines/1`"
                  class="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  查看详情
                </router-link>
                <button class="text-gray-400 hover:text-gray-500">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 库存不足示例 -->
        <div class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200">
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">降压药</h3>
                <p class="text-sm text-gray-600">5mg × 28片</p>
                <p class="text-sm text-gray-500">诺华制药</p>
              </div>
              <div class="ml-4">
                <img
                  src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20capsule%20pills&image_size=square"
                  alt="药品图片"
                  class="w-16 h-16 rounded-lg object-cover bg-gray-100"
                />
              </div>
            </div>

            <div class="space-y-2 mb-4">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">剩余数量:</span>
                <span class="font-medium text-orange-600">3片</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">有效期:</span>
                <span class="font-medium text-gray-900">2025-06-30</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">存储条件:</span>
                <span class="font-medium text-gray-900">室温保存</span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                库存不足
              </span>
              <div class="flex space-x-2">
                <router-link
                  :to="`/medicines/2`"
                  class="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  查看详情
                </router-link>
                <button class="text-gray-400 hover:text-gray-500">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 即将过期示例 -->
        <div class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200">
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">维生素C片</h3>
                <p class="text-sm text-gray-600">100mg × 60片</p>
                <p class="text-sm text-gray-500">汤臣倍健</p>
              </div>
              <div class="ml-4">
                <img
                  src="https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20tablet%20pills&image_size=square"
                  alt="药品图片"
                  class="w-16 h-16 rounded-lg object-cover bg-gray-100"
                />
              </div>
            </div>

            <div class="space-y-2 mb-4">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">剩余数量:</span>
                <span class="font-medium text-gray-900">45片</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">有效期:</span>
                <span class="font-medium text-red-600">2025-02-15</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">存储条件:</span>
                <span class="font-medium text-gray-900">避光保存</span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                即将过期
              </span>
              <div class="flex space-x-2">
                <router-link
                  :to="`/medicines/3`"
                  class="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  查看详情
                </router-link>
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

      <!-- 空状态 -->
      <!-- <div class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">暂无药品</h3>
        <p class="mt-1 text-sm text-gray-500">开始添加您的第一个药品吧</p>
        <div class="mt-6">
          <router-link
            to="/medicines/add"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加药品
          </router-link>
        </div>
      </div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 药品管理页面组件
 * 显示药品列表，支持搜索、筛选和管理功能
 */
</script>