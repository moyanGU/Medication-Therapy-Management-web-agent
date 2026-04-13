<template>
  <div class="notification-permission">
    <!-- 权限状态卡片 -->
    <div class="permission-card" :class="permissionStatusClass">
      <div class="permission-header">
        <div class="permission-icon">
          <component :is="permissionIcon" class="w-6 h-6" />
        </div>
        <div class="permission-info">
          <h3 class="permission-title">通知权限</h3>
          <p class="permission-status">{{ permissionStatusText }}</p>
        </div>
        <div class="permission-actions">
          <button
            v-if="canRequestPermission"
            @click="requestPermission"
            :disabled="requesting"
            class="btn btn-primary btn-sm"
          >
            <Loader2 v-if="requesting" class="w-4 h-4 mr-2 animate-spin" />
            {{ requesting ? '申请中...' : '申请权限' }}
          </button>

          <!-- 启用推送订阅 -->
          <button
            v-if="permission === 'granted' && pushSupported && !isSubscribed"
            @click="enablePushSubscription"
            :disabled="subscribing"
            class="btn btn-primary btn-sm"
            title="启用浏览器推送订阅"
          >
            <Loader2 v-if="subscribing" class="w-4 h-4 mr-2 animate-spin" />
            {{ subscribing ? '订阅中...' : '启用推送订阅' }}
          </button>

          <!-- 取消推送订阅 -->
          <button
            v-if="permission === 'granted' && pushSupported && isSubscribed"
            @click="disablePushSubscription"
            :disabled="subscribing"
            class="btn btn-outline btn-sm"
            title="取消浏览器推送订阅"
          >
            {{ subscribing ? '处理中...' : '取消订阅' }}
          </button>

          <button
            v-if="permission === 'granted'"
            @click="testNotification"
            :disabled="testing"
            class="btn btn-outline btn-sm"
          >
            <Loader2 v-if="testing" class="w-4 h-4 mr-2 animate-spin" />
            {{ testing ? '测试中...' : '测试通知' }}
          </button>

          <button
            @click="refreshStatus"
            class="btn btn-ghost btn-sm"
            title="刷新状态"
          >
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- 详细信息 -->
      <div v-if="showDetails" class="permission-details">
        <div class="detail-item">
          <span class="detail-label">浏览器支持:</span>
          <span
            class="detail-value"
            :class="supported ? 'text-green-600' : 'text-red-600'"
          >
            {{ supported ? '支持' : '不支持' }}
          </span>
        </div>

        <div class="detail-item">
          <span class="detail-label">推送支持:</span>
          <span
            class="detail-value"
            :class="pushSupported ? 'text-green-600' : 'text-red-600'"
          >
            {{ pushSupported ? '支持' : '不支持' }}
          </span>
        </div>

        <div class="detail-item">
          <span class="detail-label">权限状态:</span>
          <span class="detail-value">
            <span class="status-badge" :class="permissionBadgeClass">
              {{ permissionStatusText }}
            </span>
          </span>
        </div>

        <div class="detail-item">
          <span class="detail-label">订阅状态:</span>
          <span
            class="detail-value"
            :class="isSubscribed ? 'text-green-600' : 'text-gray-900'"
          >
            {{ isSubscribed ? '已订阅' : '未订阅' }}
          </span>
        </div>

        <div class="detail-item">
          <span class="detail-label">活跃通知:</span>
          <span class="detail-value">{{ activeNotificationCount }} 个</span>
        </div>

        <div v-if="isQuietTime" class="detail-item">
          <span class="detail-label">安静时间:</span>
          <span class="detail-value text-yellow-600">当前处于安静时间</span>
        </div>
      </div>

      <!-- 建议和帮助 -->
      <div v-if="recommendations.length > 0" class="permission-recommendations">
        <h4 class="recommendations-title">
          <Info class="w-4 h-4 mr-1" />
          建议
        </h4>
        <ul class="recommendations-list">
          <li v-for="(recommendation, index) in recommendations" :key="index">
            {{ recommendation }}
          </li>
        </ul>
      </div>

      <!-- 手动设置指南 -->
      <div v-if="permission === 'denied'" class="permission-guide">
        <h4 class="guide-title">
          <HelpCircle class="w-4 h-4 mr-1" />
          如何手动开启通知权限
        </h4>
        <div class="guide-steps">
          <div class="guide-step">
            <span class="step-number">1</span>
            <span class="step-text">点击地址栏左侧的锁图标或信息图标</span>
          </div>
          <div class="guide-step">
            <span class="step-number">2</span>
            <span class="step-text">在弹出菜单中找到"通知"选项</span>
          </div>
          <div class="guide-step">
            <span class="step-number">3</span>
            <span class="step-text">将通知设置改为"允许"</span>
          </div>
          <div class="guide-step">
            <span class="step-number">4</span>
            <span class="step-text">刷新页面使设置生效</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 展开/收起按钮 -->
    <button @click="toggleDetails" class="toggle-details-btn">
      <component
        :is="showDetails ? ChevronUp : ChevronDown"
        class="w-4 h-4 mr-1"
      />
      {{ showDetails ? '收起详情' : '查看详情' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw,
  Info,
  HelpCircle,
  ChevronUp,
  ChevronDown,
} from 'lucide-vue-next'
import { notificationService } from '@/services/notificationService'
import { useToast } from '@/composables/useToast'
import {
  isPushSupported as checkPushSupported,
  subscribeAndSave,
  unsubscribeAndCleanup,
  getCurrentSubscription,
  showLocalTestNotification,
} from '@/services/pushService'

interface Props {
  autoRefresh?: boolean
  showTestButton?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  showTestButton: true,
  compact: false,
})

const emit = defineEmits<{
  permissionChange: [permission: NotificationPermission]
  notificationTest: [success: boolean]
}>()

const {
  success: showSuccess,
  error: showError,
  warning: showWarning,
  info: showInfo,
} = useToast()

// 响应式数据
const permission = ref<NotificationPermission>('default')
const supported = ref(false)
const message = ref('')
const recommendations = ref<string[]>([])
const requesting = ref(false)
const testing = ref(false)
const showDetails = ref(false)
const activeNotificationCount = ref(0)
const isQuietTime = ref(false)
// 推送相关
const pushSupported = ref(false)
const isSubscribed = ref(false)
const subscribing = ref(false)

// 计算属性
const canRequestPermission = computed(() => {
  return supported.value && permission.value === 'default'
})

const permissionIcon = computed(() => {
  switch (permission.value) {
    case 'granted':
      return CheckCircle
    case 'denied':
      return XCircle
    default:
      return AlertTriangle
  }
})

const permissionStatusClass = computed(() => {
  switch (permission.value) {
    case 'granted':
      return 'permission-granted'
    case 'denied':
      return 'permission-denied'
    default:
      return 'permission-default'
  }
})

const permissionBadgeClass = computed(() => {
  switch (permission.value) {
    case 'granted':
      return 'badge-success'
    case 'denied':
      return 'badge-error'
    default:
      return 'badge-warning'
  }
})

const permissionStatusText = computed(() => {
  switch (permission.value) {
    case 'granted':
      return '已授权'
    case 'denied':
      return '已拒绝'
    default:
      return '未设置'
  }
})

// 权限变化回调
const handlePermissionChange = (newPermission: NotificationPermission) => {
  permission.value = newPermission
  emit('permissionChange', newPermission)
  updateStatus()
}

// 更新状态
const updateStatus = () => {
  const result = notificationService.getNotificationSettings()

  permission.value = result.permission.permission
  supported.value = result.permission.supported
  message.value = result.permission.message
  recommendations.value = result.recommendations

  activeNotificationCount.value =
    notificationService.getActiveNotificationCount()
  isQuietTime.value = notificationService.isQuietTime()
}

// 刷新状态
const refreshStatus = () => {
  updateStatus()
  showInfo('状态已刷新')
}

// 申请权限
const requestPermission = async () => {
  if (!supported.value) {
    showError('您的浏览器不支持通知功能')
    return
  }

  try {
    requesting.value = true
    const result = await notificationService.requestPermission()

    permission.value = result.permission
    message.value = result.message

    if (result.permission === 'granted') {
      showSuccess('通知权限申请成功')
    } else if (result.permission === 'denied') {
      showError('通知权限被拒绝')
    } else {
      showWarning('通知权限申请被忽略')
    }

    emit('permissionChange', result.permission)
    updateStatus()
  } catch (error) {
    console.error('申请通知权限失败:', error)
    showError('申请通知权限失败')
  } finally {
    requesting.value = false
  }
}

// 测试通知
const testNotification = async () => {
  if (permission.value !== 'granted') {
    showWarning('请先授权通知权限')
    return
  }

  try {
    testing.value = true
    const result = await notificationService.showTestNotification()
    // 额外：本地 SW 测试通知（无需后端）
    await showLocalTestNotification()

    if (result.success) {
      showSuccess('测试通知发送成功')
      emit('notificationTest', true)
    } else {
      showError(result.error || '测试通知发送失败')
      emit('notificationTest', false)
    }

    updateStatus()
  } catch (error) {
    console.error('测试通知失败:', error)
    showError('测试通知失败')
    emit('notificationTest', false)
  } finally {
    testing.value = false
  }
}

// 启用推送订阅
const enablePushSubscription = async () => {
  if (permission.value !== 'granted') {
    showWarning('请先授权通知权限')
    return
  }
  if (!pushSupported.value) {
    showError('当前浏览器不支持推送订阅')
    return
  }
  try {
    subscribing.value = true
    const sub = await subscribeAndSave()
    isSubscribed.value = !!sub
    showSuccess('推送订阅已启用')
  } catch (error) {
    console.error('[Push] 启用订阅失败:', error)
    showError('启用订阅失败，请检查浏览器设置或网络')
  } finally {
    subscribing.value = false
    await refreshSubscriptionState()
  }
}

// 取消推送订阅
const disablePushSubscription = async () => {
  try {
    subscribing.value = true
    const ok = await unsubscribeAndCleanup()
    isSubscribed.value = !ok ? isSubscribed.value : false
    showSuccess('订阅已取消')
  } catch (error) {
    console.error('[Push] 取消订阅失败:', error)
    showError('取消订阅失败')
  } finally {
    subscribing.value = false
    await refreshSubscriptionState()
  }
}

// 刷新订阅状态
const refreshSubscriptionState = async () => {
  try {
    const sub = await getCurrentSubscription()
    isSubscribed.value = !!sub
  } catch (e) {
    console.warn('[Push] 刷新订阅状态失败', e)
  }
}

// 切换详情显示
const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

// 自动刷新定时器
let refreshTimer: number | null = null

const startAutoRefresh = () => {
  if (props.autoRefresh) {
    refreshTimer = window.setInterval(() => {
      updateStatus()
    }, 30000) // 每30秒刷新一次
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  updateStatus()
  // 推送支持检测与订阅状态刷新
  pushSupported.value = checkPushSupported()
  refreshSubscriptionState()

  // 注册权限变化监听
  notificationService.onPermissionChange(handlePermissionChange)

  // 启动自动刷新
  startAutoRefresh()
})

onUnmounted(() => {
  // 移除权限变化监听
  notificationService.offPermissionChange(handlePermissionChange)

  // 停止自动刷新
  stopAutoRefresh()
})
</script>

<style scoped>
.notification-permission {
  @apply space-y-4;
}

/* 权限卡片 */
.permission-card {
  @apply bg-white rounded-lg border p-4 transition-colors;
}

.permission-card.permission-granted {
  @apply border-green-200 bg-green-50;
}

.permission-card.permission-denied {
  @apply border-red-200 bg-red-50;
}

.permission-card.permission-default {
  @apply border-yellow-200 bg-yellow-50;
}

/* 权限头部 */
.permission-header {
  @apply flex items-center justify-between;
}

.permission-icon {
  @apply flex-shrink-0;
}

.permission-info {
  @apply flex-1 ml-3;
}

.permission-title {
  @apply text-lg font-semibold text-gray-900;
}

.permission-status {
  @apply text-sm text-gray-600 mt-1;
}

.permission-actions {
  @apply flex items-center space-x-2;
}

/* 详细信息 */
.permission-details {
  @apply mt-4 pt-4 border-t border-gray-200 space-y-2;
}

.detail-item {
  @apply flex items-center justify-between text-sm;
}

.detail-label {
  @apply font-medium text-gray-700;
}

.detail-value {
  @apply text-gray-900;
}

/* 状态徽章 */
.status-badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;
}

.badge-success {
  @apply bg-green-100 text-green-800;
}

.badge-error {
  @apply bg-red-100 text-red-800;
}

.badge-warning {
  @apply bg-yellow-100 text-yellow-800;
}

/* 建议 */
.permission-recommendations {
  @apply mt-4 pt-4 border-t border-gray-200;
}

.recommendations-title {
  @apply flex items-center text-sm font-medium text-gray-700 mb-2;
}

.recommendations-list {
  @apply space-y-1 text-sm text-gray-600;
}

.recommendations-list li {
  @apply flex items-start;
}

.recommendations-list li::before {
  content: '•';
  @apply text-gray-400 mr-2 flex-shrink-0;
}

/* 设置指南 */
.permission-guide {
  @apply mt-4 pt-4 border-t border-gray-200;
}

.guide-title {
  @apply flex items-center text-sm font-medium text-gray-700 mb-3;
}

.guide-steps {
  @apply space-y-2;
}

.guide-step {
  @apply flex items-start text-sm text-gray-600;
}

.step-number {
  @apply flex items-center justify-center w-5 h-5 bg-blue-100 text-blue-800 rounded-full text-xs font-medium mr-3 flex-shrink-0;
}

.step-text {
  @apply flex-1;
}

/* 切换按钮 */
.toggle-details-btn {
  @apply flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors;
}

/* 按钮样式 */
.btn {
  @apply inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}

.btn-outline {
  @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-blue-500;
}

.btn-ghost {
  @apply text-gray-600 hover:text-gray-900 hover:bg-gray-100;
}

.btn-sm {
  @apply px-2 py-1 text-xs;
}
</style>
