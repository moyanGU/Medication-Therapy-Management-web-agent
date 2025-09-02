<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">就医记录</h1>
            <p class="text-gray-600 mt-1">记录和管理您的就诊信息</p>
          </div>
          <button class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加记录
          </button>
        </div>
      </div>

      <!-- 筛选和搜索 -->
      <div class="bg-white rounded-lg shadow mb-6 p-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">医院名称</label>
            <input
              type="text"
              placeholder="搜索医院"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">科室</label>
            <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="">全部科室</option>
              <option value="cardiology">心内科</option>
              <option value="endocrinology">内分泌科</option>
              <option value="gastroenterology">消化内科</option>
              <option value="neurology">神经内科</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">就诊时间</label>
            <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="">全部时间</option>
              <option value="month">最近一个月</option>
              <option value="quarter">最近三个月</option>
              <option value="year">最近一年</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">医生姓名</label>
            <input
              type="text"
              placeholder="搜索医生"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <!-- 就医记录列表 -->
      <div class="space-y-6">
        <!-- 记录项 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">北京协和医院</h3>
                <p class="text-sm text-gray-600">心内科 · 2025-01-20</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  复诊
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
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">就诊信息</h4>
                <dl class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">主治医生:</dt>
                    <dd class="font-medium text-gray-900">张主任</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">就诊时间:</dt>
                    <dd class="font-medium text-gray-900">2025-01-20 09:30</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">挂号费:</dt>
                    <dd class="font-medium text-gray-900">¥50</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">总费用:</dt>
                    <dd class="font-medium text-gray-900">¥320</dd>
                  </div>
                </dl>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">诊断结果</h4>
                <div class="space-y-3">
                  <div>
                    <h5 class="text-xs font-medium text-gray-700 uppercase tracking-wide">主要诊断</h5>
                    <p class="text-sm text-gray-900 mt-1">高血压病 2级（中危组）</p>
                  </div>
                  <div>
                    <h5 class="text-xs font-medium text-gray-700 uppercase tracking-wide">次要诊断</h5>
                    <p class="text-sm text-gray-900 mt-1">血脂异常</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-3">治疗方案</h4>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-900 leading-relaxed">
                  1. 继续服用降压药（氨氯地平片 5mg，每日1次）<br>
                  2. 新增阿司匹林肠溶片 100mg，每日1次，饭后服用<br>
                  3. 控制饮食，低盐低脂，适量运动<br>
                  4. 定期监测血压，建议每周测量2-3次<br>
                  5. 3个月后复诊，复查血脂和肝功能
                </p>
              </div>
            </div>
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-3">备注</h4>
              <p class="text-sm text-gray-600">
                患者血压控制良好，建议继续现有治疗方案。注意监测血压变化，如有不适及时就诊。
              </p>
            </div>
          </div>
        </div>

        <!-- 另一条记录 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">北京大学第一医院</h3>
                <p class="text-sm text-gray-600">内分泌科 · 2025-01-10</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  初诊
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
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">就诊信息</h4>
                <dl class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">主治医生:</dt>
                    <dd class="font-medium text-gray-900">李医生</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">就诊时间:</dt>
                    <dd class="font-medium text-gray-900">2025-01-10 14:00</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">挂号费:</dt>
                    <dd class="font-medium text-gray-900">¥30</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">总费用:</dt>
                    <dd class="font-medium text-gray-900">¥180</dd>
                  </div>
                </dl>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">诊断结果</h4>
                <div class="space-y-3">
                  <div>
                    <h5 class="text-xs font-medium text-gray-700 uppercase tracking-wide">主要诊断</h5>
                    <p class="text-sm text-gray-900 mt-1">2型糖尿病</p>
                  </div>
                  <div>
                    <h5 class="text-xs font-medium text-gray-700 uppercase tracking-wide">次要诊断</h5>
                    <p class="text-sm text-gray-900 mt-1">糖尿病前期</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-3">治疗方案</h4>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-900 leading-relaxed">
                  1. 开始二甲双胍缓释片 500mg，每日2次，餐后服用<br>
                  2. 严格控制饮食，减少碳水化合物摄入<br>
                  3. 增加运动量，建议每天步行30分钟以上<br>
                  4. 定期监测血糖，建议每周测量2-3次<br>
                  5. 1个月后复诊，调整用药方案
                </p>
              </div>
            </div>
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-3">备注</h4>
              <p class="text-sm text-gray-600">
                新确诊糖尿病，需要严格控制血糖。建议患者学习糖尿病相关知识，配合治疗。
              </p>
            </div>
          </div>
        </div>

        <!-- 历史记录 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">北京中医医院</h3>
                <p class="text-sm text-gray-600">消化内科 · 2024-12-15</p>
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
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">就诊信息</h4>
                <dl class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">主治医生:</dt>
                    <dd class="font-medium text-gray-900">王医生</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">就诊时间:</dt>
                    <dd class="font-medium text-gray-900">2024-12-15 10:30</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">挂号费:</dt>
                    <dd class="font-medium text-gray-900">¥25</dd>
                  </div>
                  <div class="flex justify-between text-sm">
                    <dt class="text-gray-600">总费用:</dt>
                    <dd class="font-medium text-gray-900">¥150</dd>
                  </div>
                </dl>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">诊断结果</h4>
                <div class="space-y-3">
                  <div>
                    <h5 class="text-xs font-medium text-gray-700 uppercase tracking-wide">主要诊断</h5>
                    <p class="text-sm text-gray-900 mt-1">慢性胃炎</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-3">治疗方案</h4>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-900 leading-relaxed">
                  1. 奥美拉唑肠溶胶囊 20mg，每日1次，早餐前服用，连续14天<br>
                  2. 注意饮食规律，避免辛辣刺激性食物<br>
                  3. 戒烟戒酒，减少咖啡摄入<br>
                  4. 症状缓解后停药，如有复发及时就诊
                </p>
              </div>
            </div>
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-3">治疗结果</h4>
              <p class="text-sm text-green-600">
                治疗效果良好，症状已完全缓解。建议继续保持良好的饮食习惯。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="mt-8 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          显示 <span class="font-medium">1</span> 到 <span class="font-medium">3</span> 条，共 <span class="font-medium">15</span> 条记录
        </div>
        <div class="flex space-x-2">
          <button class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            上一页
          </button>
          <button class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 就医记录页面组件
 * 记录和管理就诊信息、诊断结果和治疗方案
 */
</script>