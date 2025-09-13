<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">个人设置</h1>
        <p class="text-gray-600 mt-1">管理您的账户信息和应用偏好</p>
      </div>

      <div class="space-y-6">
        <!-- 个人信息 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">个人信息</h2>
          </div>
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                <input
                  type="text"
                  :value="userStore.userInfo?.username || ''"
                  disabled
                  class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500 cursor-not-allowed"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">手机号码</label>
                <input
                  type="tel"
                  :value="userStore.userInfo?.phone || ''"
                  disabled
                  class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500 cursor-not-allowed"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">邮箱地址</label>
                <input
                  type="email"
                  v-model="form.email"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">出生日期</label>
                <input
                  type="date"
                  v-model="form.birthDate"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">性别</label>
                <select
                  v-model="form.gender"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">请选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">紧急联系人</label>
                <input
                  type="text"
                  v-model="form.emergencyContact"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">紧急联系电话</label>
                <input
                  type="tel"
                  v-model="form.emergencyPhone"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <!-- 以下字段暂未对接后端，先隐藏，避免展示模拟数据 -->
              <div v-if="false">
                <label class="block text-sm font-medium text-gray-700 mb-2">身高 (cm)</label>
                <input type="number" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
              </div>
              <div v-if="false">
                <label class="block text-sm font-medium text-gray-700 mb-2">体重 (kg)</label>
                <input type="number" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
              </div>
              <div v-if="false">
                <label class="block text-sm font-medium text-gray-700 mb-2">血型</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="">请选择</option>
                  <option value="A">A型</option>
                  <option value="B">B型</option>
                  <option value="AB">AB型</option>
                  <option value="O">O型</option>
                </select>
              </div>
            </div>
            <div class="mt-6" v-if="false">
              <label class="block text-sm font-medium text-gray-700 mb-2">过敏史</label>
              <textarea rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md"></textarea>
            </div>
            <div class="mt-6" v-if="false">
              <label class="block text-sm font-medium text-gray-700 mb-2">既往病史</label>
              <textarea rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md"></textarea>
            </div>
            <div class="mt-6 flex justify-end">
              <button
                @click="saveUserInfo"
                :disabled="saving"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ saving ? '保存中...' : '保存信息' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 提醒设置 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">提醒设置</h2>
          </div>
          <div class="p-6">
            <div class="space-y-6">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">用药提醒</h3>
                  <p class="text-sm text-gray-600">开启后会在用药时间前提醒您</p>
                </div>
                <button
                  @click="toggleSetting('medicationReminder')"
                  :class="[
                    settings.medicationReminder ? 'bg-blue-600' : 'bg-gray-200',
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  ]"
                >
                  <span
                    :class="[
                      settings.medicationReminder ? 'translate-x-5' : 'translate-x-0',
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">复诊提醒</h3>
                  <p class="text-sm text-gray-600">提醒您按时复诊</p>
                </div>
                <button
                  @click="toggleSetting('appointmentReminder')"
                  :class="[
                    settings.appointmentReminder ? 'bg-blue-600' : 'bg-gray-200',
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  ]"
                >
                  <span
                    :class="[
                      settings.appointmentReminder ? 'translate-x-5' : 'translate-x-0',
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">药品过期提醒</h3>
                  <p class="text-sm text-gray-600">在药品即将过期时提醒您</p>
                </div>
                <button
                  @click="toggleSetting('expiryReminder')"
                  :class="[
                    settings.expiryReminder ? 'bg-blue-600' : 'bg-gray-200',
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  ]"
                >
                  <span
                    :class="[
                      settings.expiryReminder ? 'translate-x-5' : 'translate-x-0',
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  ></span>
                </button>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">提醒提前时间</label>
                <select
                  v-model="settings.reminderAdvanceTime"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="5">5分钟前</option>
                  <option value="10">10分钟前</option>
                  <option value="15">15分钟前</option>
                  <option value="30">30分钟前</option>
                  <option value="60">1小时前</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 隐私设置 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">隐私设置</h2>
          </div>
          <div class="p-6">
            <div class="space-y-6">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">数据同步</h3>
                  <p class="text-sm text-gray-600">允许在多设备间同步数据</p>
                </div>
                <button
                  @click="toggleSetting('dataSync')"
                  :class="[
                    settings.dataSync ? 'bg-blue-600' : 'bg-gray-200',
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  ]"
                >
                  <span
                    :class="[
                      settings.dataSync ? 'translate-x-5' : 'translate-x-0',
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">匿名统计</h3>
                  <p class="text-sm text-gray-600">帮助我们改进产品体验</p>
                </div>
                <button
                  @click="toggleSetting('analytics')"
                  :class="[
                    settings.analytics ? 'bg-blue-600' : 'bg-gray-200',
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  ]"
                >
                  <span
                    :class="[
                      settings.analytics ? 'translate-x-5' : 'translate-x-0',
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  ></span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户安全 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">账户安全</h2>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <button class="w-full text-left px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">修改密码</h3>
                    <p class="text-sm text-gray-600">定期更换密码以保护账户安全</p>
                  </div>
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>
              </button>
              
              <button class="w-full text-left px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">绑定手机</h3>
                    <p class="text-sm text-gray-600">已绑定: {{ maskedPhone }}</p>
                  </div>
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>
              </button>
              
              <button class="w-full text-left px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">登录记录</h3>
                    <p class="text-sm text-gray-600">查看最近的登录活动</p>
                  </div>
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- 数据管理 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">数据管理</h2>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <button class="w-full text-left px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">导出数据</h3>
                    <p class="text-sm text-gray-600">导出您的所有用药记录和健康数据</p>
                  </div>
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
              </button>
              
              <button class="w-full text-left px-4 py-3 border border-red-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 text-red-600">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium">删除账户</h3>
                    <p class="text-sm text-red-500">永久删除您的账户和所有数据</p>
                  </div>
                  <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'

// 接入用户store
const userStore = useUserStore()

// 本地提醒设置（当前未对接后端）
const settings = reactive({
  medicationReminder: true,
  appointmentReminder: true,
  expiryReminder: true,
  dataSync: true,
  analytics: false,
  reminderAdvanceTime: '15',
})

// 表单仅包含后端可写字段
const form = reactive({
  email: '',
  birthDate: '',
  gender: '',
  emergencyContact: '',
  emergencyPhone: '',
  avatar: ''
})

// 已绑定手机号（脱敏显示）
const maskedPhone = computed(() => {
  const p = userStore.userInfo?.phone || ''
  if (!p) return '未绑定'
  // 将中间四位替换为*，仅在为11位数字时处理
  return /^\d{11}$/.test(p) ? p.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : p
})

const saving = ref(false)

onMounted(async () => {
  console.debug('[SettingsPage] onMounted: fetch user profile')
  await userStore.fetchUserInfo()
  const u = userStore.userInfo
  if (u) {
    form.email = u.email || ''
    form.birthDate = u.birthDate || ''
    form.gender = (u.gender as any) || ''
    form.emergencyContact = u.emergencyContact || ''
    form.emergencyPhone = u.emergencyPhone || ''
    form.avatar = u.avatar || ''
  }
})

/**
 * 保存用户信息：仅提交允许的字段
 */
const saveUserInfo = async () => {
  saving.value = true
  try {
    console.debug('[SettingsPage] 保存用户信息 payload =', { ...form })
    const res = await userStore.updateUserInfo({ ...form })
    if (res.success) {
      console.debug('[SettingsPage] 保存成功')
    } else {
      console.warn('[SettingsPage] 保存失败:', res.message)
    }
  } catch (error) {
    console.error('[SettingsPage] 保存失败:', error)
  } finally {
    saving.value = false
  }
}

/**
 * 切换设置开关（保留原逻辑）
 */
const toggleSetting = (key: keyof typeof settings) => {
  if (typeof settings[key] === 'boolean') {
    ;(settings[key] as boolean) = !(settings[key] as boolean)
  }
}
</script>