<template>
  <div class="ai-assistant-container">
    <!-- 机器人悬浮球 -->
    <div
      ref="robotRef"
      class="robot-bubble fixed z-[9999] cursor-pointer touch-none select-none transition-all duration-300 ease-out"
      :class="{
        'is-hidden-left': isIdle && snapSide === 'left',
        'is-hidden-right': isIdle && snapSide === 'right',
        'is-dragging': isDragging,
      }"
      :style="bubbleStyle"
      @mousedown="startDrag"
      @touchstart="startDrag"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      @dblclick="openChat"
    >
      <!-- 问候气泡 -->
      <div
        v-if="showGreeting && !isOpen"
        class="absolute -top-16 left-1/2 -translate-x-1/2 w-48 bg-white rounded-xl shadow-lg p-3 text-xs text-gray-700 border border-blue-100 animate-bounce-in pointer-events-none"
      >
        <div class="relative text-center font-medium">
          双击一下我，我能给你专业的用药指导哦~
          <div
            class="absolute -bottom-5 left-1/2 -translate-x-1/2 border-8 border-transparent border-t-white"
          ></div>
        </div>
      </div>

      <!-- 机器人形象 SVG -->
      <div
        class="robot-avatar w-20 h-28 drop-shadow-xl relative hover:scale-110 transition-transform"
      >
        <svg
          viewBox="0 -40 100 140"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          class="w-full h-full"
        >
          <!-- 身体/白大褂 -->
          <path
            d="M20 70C20 60 30 55 50 55C70 55 80 60 80 70V90C80 95.5 75.5 100 70 100H30C24.5 100 20 95.5 20 90V70Z"
            fill="#F0F9FF"
          />
          <path d="M50 55V100" stroke="#BFDBFE" stroke-width="2" />
          <path
            d="M35 70L40 80"
            stroke="#BFDBFE"
            stroke-width="2"
            stroke-linecap="round"
          />
          <path
            d="M65 70L60 80"
            stroke="#BFDBFE"
            stroke-width="2"
            stroke-linecap="round"
          />

          <!-- 头部 -->
          <rect
            x="25"
            y="15"
            width="50"
            height="40"
            rx="12"
            fill="white"
            stroke="#3B82F6"
            stroke-width="3"
          />
          <!-- 脸部屏幕 -->
          <rect x="32" y="22" width="36" height="26" rx="6" fill="#1E293B" />
          <!-- 眼睛 (眨眼动画) -->
          <g class="robot-eyes">
            <circle cx="42" cy="35" r="3" fill="#60A5FA">
              <animate
                attributeName="ry"
                values="3;0.5;3"
                dur="3s"
                repeatCount="indefinite"
              />
            </circle>
            <circle cx="58" cy="35" r="3" fill="#60A5FA">
              <animate
                attributeName="ry"
                values="3;0.5;3"
                dur="3s"
                repeatCount="indefinite"
              />
            </circle>
          </g>
          <!-- 天线 -->
          <line
            x1="50"
            y1="15"
            x2="50"
            y2="5"
            stroke="#3B82F6"
            stroke-width="3"
          />
          <circle cx="50" cy="5" r="3" fill="#EF4444">
            <animate
              attributeName="opacity"
              values="1;0.3;1"
              dur="1.5s"
              repeatCount="indefinite"
            />
          </circle>

          <!-- 头部“AI”字样 (翠绿色立体效果) -->
          <g transform="translate(14, -26) scale(1.2)">
            <!-- 阴影层 -->
            <text
              x="10"
              y="30"
              font-family="Arial, sans-serif"
              font-weight="900"
              font-size="32"
              fill="#064E3B"
              opacity="0.3"
              transform="translate(2, 2)"
            >
              AI
            </text>
            <!-- 立体侧面 -->
            <text
              x="10"
              y="30"
              font-family="Arial, sans-serif"
              font-weight="900"
              font-size="32"
              fill="#059669"
              transform="translate(1, 1)"
            >
              AI
            </text>
            <!-- 顶面 (翠绿色) -->
            <text
              x="10"
              y="30"
              font-family="Arial, sans-serif"
              font-weight="900"
              font-size="32"
              fill="#10B981"
            >
              AI
            </text>
            <!-- 高光 -->
            <path d="M12 10 L18 10 L15 20 Z" fill="white" opacity="0.3" />
          </g>

          <!-- 听诊器 -->
          <path
            d="M30 55V65C30 75 40 80 50 80C60 80 70 75 70 65V55"
            stroke="#475569"
            stroke-width="2"
            stroke-linecap="round"
          />
          <circle cx="50" cy="85" r="5" fill="#F59E0B" />
        </svg>
      </div>
    </div>

    <!-- 对话框 Modal -->
    <Transition name="dialog-fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-[10000] flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm"
      >
        <div
          class="bg-white w-full max-w-lg h-[600px] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-blue-100 transform transition-all"
        >
          <!-- Header -->
          <div
            class="bg-gradient-to-r from-blue-500 to-blue-600 p-4 flex items-center justify-between text-white"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  class="w-6 h-6"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 class="font-bold text-lg">{{ currentModeTitle }}</h3>
                <p class="text-xs text-blue-100 opacity-90">
                  {{ currentModeSubtitle }}
                </p>
              </div>
            </div>
            <button
              @click="closeChat"
              class="hover:bg-white/20 p-2 rounded-full transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M18 6 6 18" />
                <path d="m6 6 18 18" />
              </svg>
            </button>
          </div>
          <div class="px-4 py-3 bg-white border-b border-slate-100">
            <div class="flex gap-2 items-center">
              <button
                @click="switchMode('medication')"
                class="px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
                :class="
                  currentMode === 'medication'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                "
              >
                用药问答
              </button>
              <button
                @click="switchMode('page-agent')"
                class="px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
                :class="
                  currentMode === 'page-agent'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                "
              >
                页面助手
              </button>
              <button
                @click="clearCurrentModeMessages"
                :disabled="isLoading || !currentMessages.length"
                class="ml-auto px-3 py-1.5 rounded-full text-sm font-medium transition-colors bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                清空对话
              </button>
            </div>
            <p
              v-if="currentMode === 'page-agent'"
              class="mt-2 text-xs text-slate-500"
            >
              {{ pageAgentScopeHint }}
            </p>
          </div>

          <!-- Chat Area -->
          <div
            class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 scroll-smooth"
            ref="chatContainer"
          >
            <!-- 欢迎消息 -->
            <div class="flex gap-3">
              <div
                class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 text-lg"
              >
                🤖
              </div>
              <div
                class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 text-sm text-slate-700 max-w-[85%]"
              >
                {{ welcomeText }}
                <ul
                  class="mt-2 space-y-1 list-disc list-inside text-blue-600 cursor-pointer"
                >
                  <li
                    v-for="action in quickActions"
                    :key="action"
                    @click="quickAsk(action)"
                  >
                    {{ action }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- 消息列表 -->
            <template v-for="(msg, index) in currentMessages" :key="index">
              <!-- 用户消息 -->
              <div
                v-if="msg.role === 'user'"
                class="flex gap-3 flex-row-reverse"
              >
                <div
                  class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0 overflow-hidden"
                >
                  <svg
                    class="w-5 h-5 text-gray-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div
                  class="bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none shadow-md text-sm max-w-[85%] whitespace-pre-wrap"
                >
                  {{ msg.content }}
                </div>
              </div>

              <!-- AI 消息 -->
              <div v-else class="flex gap-3">
                <div
                  class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 text-lg"
                >
                  🤖
                </div>
                <div
                  class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 text-sm text-slate-700 max-w-[85%]"
                >
                  <div v-if="msg.loading" class="flex gap-1 items-center h-5">
                    <span
                      class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"
                      style="animation-delay: 0ms"
                    ></span>
                    <span
                      class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"
                      style="animation-delay: 150ms"
                    ></span>
                    <span
                      class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"
                      style="animation-delay: 300ms"
                    ></span>
                  </div>
                  <div
                    v-else
                    class="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1"
                  >
                    <div
                      v-if="msg.mode === 'page-agent'"
                      class="mb-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      页面助手
                    </div>
                    <div
                      v-if="msg.fallbackUsed"
                      class="mb-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800"
                    >
                      系统兜底
                    </div>
                    <button
                      v-if="canSpeakMessage(msg)"
                      @click="speakAssistantMessage(msg.content)"
                      class="mb-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 hover:bg-emerald-200 transition-colors"
                    >
                      {{ isSpeechEnabled ? '重新朗读' : '朗读结果' }}
                    </button>
                    <div v-html="formatMarkdown(msg.content)"></div>
                    <div
                      v-if="msg.proposal"
                      class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3"
                    >
                      <div class="flex items-center justify-between gap-3">
                        <div class="text-xs font-medium text-slate-600">
                          {{ getProposalStatusText(msg) }}
                        </div>
                        <div class="text-xs text-slate-500">
                          {{ msg.proposal.targetLabel }}
                        </div>
                      </div>
                      <div
                        v-if="msg.proposal.summary?.length"
                        class="mt-2 text-xs text-slate-600 whitespace-pre-wrap"
                      >
                        {{ msg.proposal.summary.join(' / ') }}
                      </div>
                      <div
                        v-if="canConfirmProposal(msg)"
                        class="mt-3 flex items-center gap-2"
                      >
                        <button
                      @click="confirmProposal(index)"
                          class="inline-flex items-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 transition-colors"
                        >
                          {{ msg.proposal.buttonLabel }}
                        </button>
                        <button
                      @click="cancelProposal(index)"
                          class="inline-flex items-center rounded-lg bg-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-300 transition-colors"
                        >
                          取消
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- 错误重试 -->
                  <div v-if="msg.error" class="mt-2">
                    <button
                      @click="retryLast"
                      class="text-xs text-red-500 underline hover:text-red-600"
                    >
                      重试
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- Input Area -->
          <div class="p-4 bg-white border-t border-slate-100">
            <div class="flex gap-2">
              <input
                v-model="inputText"
                @keyup.enter="sendMessage"
                type="text"
                :placeholder="inputPlaceholder"
                class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                :disabled="isLoading"
              />
              <button
                @click="sendMessage"
                :disabled="!inputText.trim() || isLoading"
                class="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white px-4 rounded-xl transition-colors flex items-center justify-center"
              >
                <svg
                  v-if="!isLoading"
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="m22 2-7 20-4-9-9-4Z" />
                  <path d="M22 2 11 13" />
                </svg>
                <svg
                  v-else
                  class="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              </button>
            </div>
            <p class="text-xs text-slate-400 mt-2 text-center">
              {{ footerText }}
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  executePageAgentTask,
  getCurrentPageAgentScopeDescription,
  getPageAgentQuickActions,
  type PageAgentActionProposal,
  type PageAgentMode,
} from '@/services/pageAgentService'
import { useSpeech } from '@/composables/useSpeech'
import { useToast } from '@/composables/useToast'
import { api, logApiErrorEvent } from '@/utils/api'

type ChatMessage = {
  role: 'user' | 'ai'
  content: string
  mode?: PageAgentMode
  loading?: boolean
  error?: boolean
  fallbackUsed?: boolean
  proposal?: PageAgentActionProposal | null
  actionState?: 'pending' | 'confirmed' | 'cancelled' | 'failed'
}

// --- 状态 ---
const isOpen = ref(false)
const showGreeting = ref(false)
const inputText = ref('')
const isLoading = ref(false)
const currentMode = ref<PageAgentMode>('medication')
const route = useRoute()
const router = useRouter()
const { success: showSuccess, error: showError } = useToast()
const modeMessages = reactive<Record<PageAgentMode, ChatMessage[]>>({
  medication: [],
  'page-agent': [],
})
const currentMessages = computed(() => modeMessages[currentMode.value])
const chatContainer = ref<HTMLElement | null>(null)
const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()
const currentModeTitle = computed(() =>
  currentMode.value === 'page-agent' ? '页面助手' : '百川医疗助手'
)
const currentModeSubtitle = computed(() =>
  currentMode.value === 'page-agent'
    ? '当前页面分析与辅助填写'
    : '专业的用药指导顾问'
)
const welcomeText = computed(() =>
  currentMode.value === 'page-agent'
    ? '你好！我是页面助手。我会结合当前页面内容做保守分析；在提醒表单和病历表单页，我还可以帮你整理必填项并生成待确认草稿，但不会自动提交。你可以直接让我总结页面信息、指出异常状态，或者帮你补全表单，例如：'
    : '你好！我是您的专属用药助手。为获得更准确的答案，请输入明确药名，并询问该药的用法、用量或禁忌，例如：'
)
const quickActions = computed(() =>
  currentMode.value === 'page-agent'
    ? getPageAgentQuickActions()
    : ['阿莫西林饭前还是饭后吃？']
)
const inputPlaceholder = computed(() =>
  currentMode.value === 'page-agent'
    ? '输入页面分析任务，例如：总结当前提醒页的异常状态'
    : '输入您的用药问题...'
)
const pageAgentScopeHint = computed(() => getCurrentPageAgentScopeDescription())
const footerText = computed(() =>
  currentMode.value === 'page-agent'
    ? '页面助手会先分析，再辅助预填，但仍需要你确认后才会提交'
    : 'AI 回答仅供参考，不可替代专业医疗诊断'
)

// --- 拖拽与吸附逻辑 ---
const robotRef = ref<HTMLElement | null>(null)
const position = reactive({
  x: window.innerWidth - 80,
  y: window.innerHeight - 150,
})
const isDragging = ref(false)
const isIdle = ref(false)
const snapSide = ref<'left' | 'right'>('right')
let idleTimer: number | null = null
let dragOffset = { x: 0, y: 0 }
const lastQaQueryKey = ref('')

// 初始化
onMounted(() => {
  resetIdleTimer()
  window.addEventListener('resize', handleResize)
  // 初始位置吸附
  snapToEdge()
  void runQaScenarioFromRoute()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (idleTimer) clearTimeout(idleTimer)
})

watch(
  () => route.fullPath,
  () => {
    void runQaScenarioFromRoute()
  }
)

const bubbleStyle = computed(() => {
  if (isDragging.value) {
    return {
      left: `${position.x}px`,
      top: `${position.y}px`,
      transform: 'scale(1.1)',
      transition: 'none', // 拖拽时移除过渡以保证跟手
    }
  }
  return {
    left: `${position.x}px`,
    top: `${position.y}px`,
  }
})

// 拖拽开始
const startDrag = (e: MouseEvent | TouchEvent) => {
  if (isOpen.value) return // 打开对话框时禁止拖拽
  isDragging.value = true
  isIdle.value = false
  if (idleTimer) clearTimeout(idleTimer)

  const clientX = e instanceof MouseEvent ? e.clientX : e.touches[0].clientX
  const clientY = e instanceof MouseEvent ? e.clientY : e.touches[0].clientY

  // 计算鼠标在元素内的偏移
  const rect = robotRef.value!.getBoundingClientRect()
  dragOffset.x = clientX - rect.left
  dragOffset.y = clientY - rect.top

  // 添加全局移动和松开事件
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
  window.addEventListener('touchmove', onDrag, { passive: false })
  window.addEventListener('touchend', stopDrag)
}

// 拖拽中
const onDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  e.preventDefault() // 防止触摸滚动

  const clientX = e instanceof MouseEvent ? e.clientX : e.touches[0].clientX
  const clientY = e instanceof MouseEvent ? e.clientY : e.touches[0].clientY

  let newX = clientX - dragOffset.x
  let newY = clientY - dragOffset.y

  // 边界限制
  const maxX = window.innerWidth - 80 // 80是元素宽度 (w-20)
  const maxY = window.innerHeight - 112 // 112是元素高度 (h-28)

  position.x = Math.max(0, Math.min(newX, maxX))
  position.y = Math.max(0, Math.min(newY, maxY))
}

// 拖拽结束
const stopDrag = () => {
  isDragging.value = false
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
  window.removeEventListener('touchmove', onDrag)
  window.removeEventListener('touchend', stopDrag)

  snapToEdge()
  resetIdleTimer()
}

// 吸附边缘
const snapToEdge = () => {
  const windowWidth = window.innerWidth
  const centerX = windowWidth / 2
  const elementWidth = 80 // 80px

  if (position.x + elementWidth / 2 < centerX) {
    position.x = 0 // 吸附左侧
    snapSide.value = 'left'
  } else {
    position.x = windowWidth - elementWidth // 吸附右侧
    snapSide.value = 'right'
  }
}

// 闲置检测
const resetIdleTimer = () => {
  isIdle.value = false
  if (idleTimer) clearTimeout(idleTimer)
  idleTimer = setTimeout(() => {
    isIdle.value = true
  }, 3000) as unknown as number
}

// 窗口调整
const handleResize = () => {
  snapToEdge()
  // 确保Y轴不越界
  position.y = Math.min(position.y, window.innerHeight - 80)
}

// 交互
const handleMouseEnter = () => {
  if (!isDragging.value) {
    isIdle.value = false
    showGreeting.value = true
    if (idleTimer) clearTimeout(idleTimer)
  }
}

const handleMouseLeave = () => {
  showGreeting.value = false
  resetIdleTimer()
}

// --- 聊天逻辑 ---
const openChat = () => {
  isOpen.value = true
  showGreeting.value = false
  isIdle.value = false
}

const closeChat = () => {
  isOpen.value = false
  resetIdleTimer()
}

const switchMode = (mode: PageAgentMode) => {
  currentMode.value = mode
  scrollToBottom()
}

/**
 * 解析开发模式下的页面助手 QA 查询参数。
 */
function getQaScenarioFromRoute() {
  const openFlag = route.query.assistant === 'open'
  const task =
    typeof route.query.assistantTask === 'string'
      ? route.query.assistantTask.trim()
      : ''
  const requestedMode =
    route.query.assistantMode === 'page-agent' ? 'page-agent' : null
  const mode: PageAgentMode | null =
    requestedMode || (task ? 'page-agent' : null)

  if (!openFlag && !mode && !task) {
    return null
  }

  return {
    key: `${route.fullPath}::${mode || 'default'}::${task}`,
    mode,
    task,
  }
}

/**
 * 在开发模式下按 URL 参数自动打开助手并执行一次测试任务。
 */
async function runQaScenarioFromRoute() {
  const scenario = getQaScenarioFromRoute()
  if (!scenario || scenario.key === lastQaQueryKey.value) {
    return
  }

  lastQaQueryKey.value = scenario.key

  if (scenario.mode) {
    currentMode.value = scenario.mode
  }

  openChat()
  await nextTick()

  if (!scenario.task || isLoading.value) {
    return
  }

  inputText.value = scenario.task
  await sendMessage()
}

const quickAsk = (text: string) => {
  inputText.value = text
  sendMessage()
}

const isLikelyMedicationQuestion = (text: string) => {
  const compact = text.replace(/\s+/g, '').toLowerCase()
  const keywords = [
    '药',
    '用药',
    '服用',
    '剂量',
    '用法',
    '用量',
    '禁忌',
    '副作用',
    '相互作用',
    '饭前',
    '饭后',
    '阿司匹林',
    '阿莫西林',
    '布洛芬',
    '头孢',
    'aspirin',
    'amoxicillin',
    'ibuprofen',
  ]
  return keywords.some(k => compact.includes(k))
}

const clearCurrentModeMessages = () => {
  modeMessages[currentMode.value].splice(0, modeMessages[currentMode.value].length)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const buildSpeechText = (text: string) => {
  const mainText = text.split('执行轨迹：')[0] || text
  return mainText
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/[-•]\s*/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 220)
}

const canSpeakMessage = (msg: {
  role: 'user' | 'ai'
  content: string
  mode?: PageAgentMode
  loading?: boolean
  error?: boolean
}) => {
  return (
    msg.role === 'ai' &&
    msg.mode === 'page-agent' &&
    !msg.loading &&
    !msg.error &&
    isSpeechSupported.value
  )
}

const speakAssistantMessage = (content: string) => {
  const speechText = buildSpeechText(content)
  if (!speechText) {
    return
  }
  console.log('[AiAssistant] speak page-agent answer', {
    enabled: isSpeechEnabled.value,
    textLength: speechText.length,
  })
  speak(speechText, {
    rate: 0.85,
    category: 'assistant',
    priority: 'high',
    interrupt: true,
    dedupeWindowMs: 5000,
    maxSegmentLength: 52,
  })
}

const canConfirmProposal = (msg: {
  role: 'user' | 'ai'
  mode?: PageAgentMode
  proposal?: PageAgentActionProposal | null
  actionState?: 'pending' | 'confirmed' | 'cancelled' | 'failed'
  loading?: boolean
  error?: boolean
}) => {
  return (
    msg.role === 'ai' &&
    msg.mode === 'page-agent' &&
    !msg.loading &&
    !msg.error &&
    !!msg.proposal &&
    (msg.actionState || 'pending') === 'pending'
  )
}

const getProposalStatusText = (msg: {
  proposal?: PageAgentActionProposal | null
  actionState?: 'pending' | 'confirmed' | 'cancelled' | 'failed'
}) => {
  if (!msg.proposal) {
    return ''
  }
  if (msg.actionState === 'confirmed') {
    return `已执行：${msg.proposal.targetLabel}`
  }
  if (msg.actionState === 'cancelled') {
    return '已取消本次操作'
  }
  if (msg.actionState === 'failed') {
    return '执行失败，请重试'
  }
  return '待确认'
}

const confirmProposal = async (index: number) => {
  const message = currentMessages.value[index]
  if (!message?.proposal || !canConfirmProposal(message)) {
    return
  }

  message.actionState = 'confirmed'
  console.log('[AiAssistant] confirm page-agent proposal', message.proposal)

  try {
    await router.push({
      path: message.proposal.targetPath,
      query: message.proposal.query,
    })
    showSuccess(`已前往${message.proposal.targetLabel}`)
  } catch (error) {
    console.error('[AiAssistant] confirm proposal failed', error)
    message.actionState = 'failed'
    showError('页面跳转失败，请稍后重试')
  }
}

const cancelProposal = (index: number) => {
  const message = currentMessages.value[index]
  if (!message?.proposal || !canConfirmProposal(message)) {
    return
  }
  message.actionState = 'cancelled'
  console.log('[AiAssistant] cancel page-agent proposal', message.proposal)
}

// 简单Markdown处理 (加粗、换行)
const formatMarkdown = (text: string) => {
  if (!text) return ''
  // 1. 处理加粗 **text** -> <b>text</b>
  let html = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
  // 2. 处理换行
  html = html.replace(/\n/g, '<br>')
  return html
}

const retryLast = () => {
  const scopedMessages = modeMessages[currentMode.value]
  const lastIdx = scopedMessages.length - 1
  if (lastIdx >= 0 && scopedMessages[lastIdx].error) {
    const userMsg = scopedMessages[lastIdx - 1]
    if (userMsg && userMsg.role === 'user') {
      currentMode.value = userMsg.mode || 'medication'
      scopedMessages.splice(lastIdx, 1)
      scopedMessages.splice(lastIdx - 1, 1)
      inputText.value = userMsg.content
      sendMessage()
    }
  }
}

type MedicationGuidancePayload = {
  blocked: boolean
  answer: string
  reason?: string
  fallback_used?: boolean
}

const resolveMedicationGuidancePayload = (
  resp: {
    data?: unknown
  }
): MedicationGuidancePayload => {
  const primary =
    resp.data && typeof resp.data === 'object' ? (resp.data as Record<string, unknown>) : null
  const nested =
    primary?.data && typeof primary.data === 'object'
      ? (primary.data as Record<string, unknown>)
      : null
  const payload = nested ?? primary ?? {}

  return {
    blocked: Boolean(payload.blocked),
    answer: typeof payload.answer === 'string' ? payload.answer.trim() : '',
    reason: typeof payload.reason === 'string' ? payload.reason.trim() : undefined,
    fallback_used: Boolean(payload.fallback_used),
  }
}

const buildMedicationGuidanceErrorMessage = (error: any) => {
  if (error?.code === 401) {
    return '登录已过期或未登录，请重新登录后再试。'
  }

  const errorCode = error?.details?.error_code
  if (errorCode === 'AI_CONFIG_MISSING') {
    return 'AI 服务配置还没完成，请联系管理员检查后端 .env 里的百川模型配置。'
  }
  if (errorCode === 'AI_DISABLED') {
    return 'AI 服务当前没有开启，请联系管理员开启后再试。'
  }
  if (errorCode === 'AI_GENERATION_FAILED') {
    return 'AI 生成回答失败了，请稍后再试一次。'
  }
  if (errorCode === 'VALIDATION_ERROR') {
    return '请输入具体一点的用药问题，例如“布洛芬饭后吃吗？”。'
  }

  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message.trim()
  }

  return '网络连接失败，请稍后重试。'
}

const buildPageAgentErrorMessage = (error: any) => {
  const message = typeof error?.message === 'string' ? error.message.trim() : ''
  if (/Unexpected token\s*</i.test(message)) {
    return '页面助手请求没有拿到 JSON 结果，通常是后端地址配置或登录态异常。请刷新页面后重试；若仍失败，我会继续用页面规则直接回答。'
  }
  if (/Failed to fetch|NetworkError|网络/i.test(message)) {
    return '页面助手连接失败，请检查后端服务和网络状态后重试。'
  }
  if (message) {
    return message
  }
  return '页面助手执行失败，请稍后重试。'
}

const sendMedicationGuidanceMessage = async (text: string, aiMsgIndex: number) => {
  const scopedMessages = modeMessages.medication
  console.log('[AI] Sending request to /ai/medication-guidance/', {
    question: text,
  })

  try {
    const resp = await api.post<MedicationGuidancePayload>(
      '/ai/medication-guidance/',
      {
        question: text,
        // 全局助手不带 medicine_id，或者后续可扩展传递当前页面上下文
      },
      {
        timeout: 70000,
      }
    )

    console.log('[AI] medication-guidance response', resp)

    if (resp.success) {
      const data = resolveMedicationGuidancePayload(resp)
      console.log('[AI] medication-guidance payload', data)

      if (!data.blocked && !data.answer) {
        throw new Error('AI 暂时没有返回可用内容，请稍后重试。')
      }

      if (data.blocked) {
        if (isLikelyMedicationQuestion(text)) {
          scopedMessages[aiMsgIndex] = {
            role: 'ai',
            mode: 'medication',
            content:
              '你问的是用药相关问题。我可以继续给出通用用药指导：请补充药品规格（如 0.1g/片）、使用者年龄/体重、是否怀孕/哺乳及合并用药，我会按说明书要点给出更准确建议。',
            fallbackUsed: true,
          }
          return
        }
        scopedMessages[aiMsgIndex] = {
          role: 'ai',
          mode: 'medication',
          content: `⚠️ ${data.reason || '抱歉，我只能回答用药相关的问题。'}\n\n请尝试询问具体药品的用法、用量或禁忌。`,
        }
      } else {
        scopedMessages[aiMsgIndex] = {
          role: 'ai',
          mode: 'medication',
          content: data.answer,
          fallbackUsed: !!data.fallback_used,
        }
      }
    } else {
      throw new Error(resp.message || '请求失败')
    }
  } catch (e: any) {
    logApiErrorEvent('AiAssistant.medication-guidance', e, {
      questionLength: text.length,
      mode: 'medication',
    })
    console.error('AI Chat Error:', e)
    const msg = buildMedicationGuidanceErrorMessage(e)
    scopedMessages[aiMsgIndex] = {
      role: 'ai',
      mode: 'medication',
      content: msg,
      error: true,
    }
  }
}

const sendPageAgentMessage = async (text: string, aiMsgIndex: number) => {
  const scopedMessages = modeMessages['page-agent']
  console.log('[PageAgent] Sending page analysis request', {
    task: text,
    pathname: window.location.pathname,
  })

  try {
    const result = await executePageAgentTask(text)
    scopedMessages[aiMsgIndex] = {
      role: 'ai',
      mode: 'page-agent',
      content: result.answer,
      proposal: result.proposal || null,
      actionState: result.proposal ? 'pending' : undefined,
    }
    if (isSpeechEnabled.value) {
      speakAssistantMessage(result.answer)
    }
  } catch (e: any) {
    logApiErrorEvent('AiAssistant.page-agent', e, {
      taskLength: text.length,
      pathname: window.location.pathname,
      mode: 'page-agent',
    })
    console.error('Page Agent Error:', e)
    const msg = buildPageAgentErrorMessage(e)
    scopedMessages[aiMsgIndex] = {
      role: 'ai',
      mode: 'page-agent',
      content: msg,
      error: true,
      proposal: null,
    }
  }
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  const mode = currentMode.value
  const scopedMessages = modeMessages[mode]
  if (!text || isLoading.value) return

  scopedMessages.push({ role: 'user', content: text, mode })
  inputText.value = ''
  isLoading.value = true
  scrollToBottom()

  const aiMsgIndex =
    scopedMessages.push({ role: 'ai', content: '', mode, loading: true }) - 1
  scrollToBottom()

  try {
    if (mode === 'page-agent') {
      await sendPageAgentMessage(text, aiMsgIndex)
    } else {
      await sendMedicationGuidanceMessage(text, aiMsgIndex)
    }
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* 悬浮球动画 */
/* .robot-bubble 默认状态由 Tailwind 类控制 */

/* 闲置隐藏动画 - 左侧 */
.is-hidden-left {
  /* 向左移动 30%，同时顺时针旋转 15度，露出整个头部 */
  transform: translateX(-30%) rotate(15deg);
  opacity: 0.9;
}
.is-hidden-left:hover {
  transform: translateX(0) rotate(0deg) scale(1);
  opacity: 1;
}

/* 闲置隐藏动画 - 右侧 */
.is-hidden-right {
  /* 向右移动 30%，同时逆时针旋转 15度，露出整个头部 */
  transform: translateX(30%) rotate(-15deg);
  opacity: 0.9;
}
.is-hidden-right:hover {
  transform: translateX(0) rotate(0deg) scale(1);
  opacity: 1;
}

/* 拖拽中 */
.is-dragging {
  cursor: grabbing;
}

/* 弹窗淡入淡出 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}
.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-active .transform,
.dialog-fade-leave-active .transform {
  transition: transform 0.3s ease;
}
.dialog-fade-enter-from .transform,
.dialog-fade-leave-to .transform {
  transform: scale(0.95);
}

/* 问候语动画 */
.animate-bounce-in {
  animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounceIn {
  0% {
    transform: translate(-50%, 10px) scale(0.8);
    opacity: 0;
  }
  50% {
    transform: translate(-50%, -5px) scale(1.05);
  }
  100% {
    transform: translate(-50%, 0) scale(1);
    opacity: 1;
  }
}
</style>
