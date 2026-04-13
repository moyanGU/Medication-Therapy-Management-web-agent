/**
 * useSpeech.ts - 语音播报可访问性支持
 * 功能：
 * 1. 提供 isSpeechEnabled 全局状态（localStorage 持久化）
 * 2. 检测浏览器是否支持 SpeechSynthesis
 * 3. 提供 speak(text) 播报接口，自动选择中文语音或默认语音
 * 4. 提供 enableSpeech / disableSpeech / toggleSpeech 切换接口
 * 5. 初始化时尝试预加载可用语音列表
 */
import { ref, computed, onMounted } from 'vue'

const STORAGE_KEY = 'mtm.speech.enabled'
const DEFAULT_PREFER_LANGS = ['zh-CN', 'zh', 'zh-TW']
const PRIORITY_MAP = {
  low: 1,
  normal: 2,
  high: 3,
} as const

type SpeechPriority = keyof typeof PRIORITY_MAP

export interface SpeakOptions {
  rate?: number
  pitch?: number
  volume?: number
  lang?: string
  preferLangs?: string[]
  category?: 'route' | 'assistant' | 'reminder' | 'system'
  priority?: SpeechPriority
  dedupeWindowMs?: number
  interrupt?: boolean
  maxSegmentLength?: number
  throttleKey?: string
  throttleWindowMs?: number
}

// 单例缓存，避免在多个组件中重复初始化
let _initialized = false
const isSpeechEnabled = ref(false)
const voices = ref<SpeechSynthesisVoice[]>([])
let activeSpeakToken = 0
let activePriority: number = PRIORITY_MAP.normal
let lastSpeechSignature = ''
let lastSpeechAt = 0
const throttledSpeechTimers = new Map<string, ReturnType<typeof setTimeout>>()
const throttledSpeechAt = new Map<string, number>()

/**
 * 获取浏览器是否支持 speechSynthesis
 */
export const isSpeechSupported = computed(() => {
  return (
    typeof window !== 'undefined' &&
    'speechSynthesis' in window &&
    'SpeechSynthesisUtterance' in window
  )
})

/**
 * 从 localStorage 读取语音播报开关
 */
function getPreferredSpeechEnabled(): boolean {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw === '1'
  } catch (e) {
    console.warn('[useSpeech] 读取本地语音播报开关失败:', e)
    return false
  }
}

/**
 * 持久化语音播报开关
 */
function persistSpeechEnabled(value: boolean) {
  try {
    localStorage.setItem(STORAGE_KEY, value ? '1' : '0')
  } catch (e) {
    console.warn('[useSpeech] 持久化语音播报开关失败:', e)
  }
}

/**
 * 预加载语音列表（部分浏览器需要调用一次获取）
 */
function loadVoices() {
  try {
    if (!isSpeechSupported.value) return
    const synth = window.speechSynthesis
    const list = synth.getVoices()
    if (list && list.length) {
      voices.value = list
      console.log(
        '[useSpeech] 已加载语音列表:',
        list.map(v => `${v.name}(${v.lang})`)
      )
    } else {
      // 部分浏览器需要监听 voiceschanged 事件
      synth.onvoiceschanged = () => {
        voices.value = synth.getVoices()
        console.log(
          '[useSpeech] voiceschanged 触发，语音列表:',
          voices.value.map(v => `${v.name}(${v.lang})`)
        )
      }
    }
  } catch (e) {
    console.warn('[useSpeech] 加载语音列表失败:', e)
  }
}

/**
 * 选择一个最合适的语音（优先中文）
 */
function pickVoice(
  preferLangs: string[] = DEFAULT_PREFER_LANGS
): SpeechSynthesisVoice | null {
  if (!voices.value.length) return null
  for (const lang of preferLangs) {
    const match = voices.value.find(v =>
      v.lang?.toLowerCase().startsWith(lang.toLowerCase())
    )
    if (match) return match
  }
  // 退化为第一个语音
  return voices.value[0] ?? null
}

function normalizeSpeechText(text: string): string {
  return text.replace(/\s+/g, ' ').trim()
}

function buildSpeechSegments(text: string, maxSegmentLength: number): string[] {
  const normalized = normalizeSpeechText(text)
  if (!normalized) {
    return []
  }

  const segments: string[] = []
  const sentences = normalized
    .split(/(?<=[。！？!?；;])/)
    .map(item => item.trim())
    .filter(Boolean)

  let current = ''
  const pushCurrent = () => {
    if (current) {
      segments.push(current)
      current = ''
    }
  }

  const appendChunk = (chunk: string) => {
    if (!chunk) {
      return
    }
    if (!current) {
      current = chunk
      return
    }
    if (`${current}${chunk}`.length <= maxSegmentLength) {
      current += chunk
      return
    }
    pushCurrent()
    current = chunk
  }

  for (const sentence of sentences) {
    if (sentence.length <= maxSegmentLength) {
      appendChunk(sentence)
      continue
    }
    pushCurrent()
    for (let index = 0; index < sentence.length; index += maxSegmentLength) {
      segments.push(sentence.slice(index, index + maxSegmentLength))
    }
  }

  pushCurrent()
  return segments
}

function resolveSpeakOptions(options?: number | SpeakOptions): Required<SpeakOptions> {
  if (typeof options === 'number') {
    return {
      rate: options,
      pitch: 1,
      volume: 1,
      lang: 'zh-CN',
      preferLangs: DEFAULT_PREFER_LANGS,
      category: 'system',
      priority: 'normal',
      dedupeWindowMs: 2000,
      interrupt: false,
      maxSegmentLength: 60,
      throttleKey: '',
      throttleWindowMs: 0,
    }
  }

  return {
    rate: options?.rate ?? 0.8,
    pitch: options?.pitch ?? 1,
    volume: options?.volume ?? 1,
    lang: options?.lang ?? 'zh-CN',
    preferLangs: options?.preferLangs ?? DEFAULT_PREFER_LANGS,
    category: options?.category ?? 'system',
    priority: options?.priority ?? 'normal',
    dedupeWindowMs: options?.dedupeWindowMs ?? 2000,
    interrupt: options?.interrupt ?? false,
    maxSegmentLength: options?.maxSegmentLength ?? 60,
    throttleKey: options?.throttleKey ?? '',
    throttleWindowMs: options?.throttleWindowMs ?? 0,
  }
}

function createSpeechSignature(text: string, options: Required<SpeakOptions>): string {
  return [
    options.category,
    options.priority,
    options.rate,
    options.pitch,
    options.volume,
    normalizeSpeechText(text),
  ].join('::')
}

function resetSpeechState(token: number) {
  if (token !== activeSpeakToken) {
    return
  }
  activePriority = PRIORITY_MAP.normal
}

function clearScheduledSpeech(throttleKey: string) {
  const timer = throttledSpeechTimers.get(throttleKey)
  if (timer) {
    clearTimeout(timer)
    throttledSpeechTimers.delete(throttleKey)
  }
}

function scheduleThrottledSpeech(
  text: string,
  options: Required<SpeakOptions>,
  waitMs: number
) {
  if (!options.throttleKey) {
    return
  }

  clearScheduledSpeech(options.throttleKey)
  const nextOptions: SpeakOptions = {
    ...options,
    throttleWindowMs: 0,
  }

  const timer = setTimeout(() => {
    throttledSpeechTimers.delete(options.throttleKey)
    speak(text, nextOptions)
  }, waitMs)

  throttledSpeechTimers.set(options.throttleKey, timer)
  console.log('[useSpeech] 语音节流生效，已延后播报', {
    category: options.category,
    throttleKey: options.throttleKey,
    waitMs,
  })
}

function speakSegments(
  synth: SpeechSynthesis,
  segments: string[],
  options: Required<SpeakOptions>,
  token: number,
  index = 0
) {
  if (token !== activeSpeakToken || index >= segments.length) {
    resetSpeechState(token)
    return
  }

  const utter = new SpeechSynthesisUtterance(segments[index])
  const voice = pickVoice(options.preferLangs)
  if (voice) {
    utter.voice = voice
    utter.lang = voice.lang || options.lang
  } else {
    utter.lang = options.lang
  }
  utter.rate = options.rate
  utter.pitch = options.pitch
  utter.volume = options.volume
  utter.onend = () => {
    if (index === segments.length - 1) {
      resetSpeechState(token)
      return
    }
    speakSegments(synth, segments, options, token, index + 1)
  }
  utter.onerror = event => {
    if (!['canceled', 'interrupted'].includes(event.error)) {
      console.warn('[useSpeech] 语音播报失败:', {
        error: event.error,
        text: segments[index],
        category: options.category,
      })
    }
    resetSpeechState(token)
  }
  synth.speak(utter)
}

/**
 * 播报文本
 */
export function speak(text: string, options?: number | SpeakOptions) {
  if (!isSpeechSupported.value) {
    console.warn('[useSpeech] 当前浏览器不支持 SpeechSynthesis')
    return
  }
  if (!isSpeechEnabled.value) {
    console.log('[useSpeech] 语音播报未开启，忽略 speak')
    return
  }
  try {
    const resolvedOptions = resolveSpeakOptions(options)
    const normalizedText = normalizeSpeechText(text)
    if (!normalizedText) {
      return
    }

    if (!voices.value.length) {
      loadVoices()
    }

    const signature = createSpeechSignature(normalizedText, resolvedOptions)
    const now = Date.now()
    if (
      signature === lastSpeechSignature &&
      now - lastSpeechAt < resolvedOptions.dedupeWindowMs
    ) {
      console.log('[useSpeech] 命中重复播报保护，已跳过', {
        category: resolvedOptions.category,
        text: normalizedText,
      })
      return
    }

    if (resolvedOptions.throttleKey && resolvedOptions.throttleWindowMs > 0) {
      const lastThrottledAt =
        throttledSpeechAt.get(resolvedOptions.throttleKey) ?? 0
      const elapsed = now - lastThrottledAt
      if (elapsed < resolvedOptions.throttleWindowMs) {
        scheduleThrottledSpeech(
          normalizedText,
          resolvedOptions,
          resolvedOptions.throttleWindowMs - elapsed
        )
        return
      }
    }

    const synth = window.speechSynthesis
    const nextPriority = PRIORITY_MAP[resolvedOptions.priority]
    const isBusy = synth.speaking || synth.pending
    if (isBusy) {
      if (resolvedOptions.interrupt || nextPriority > activePriority) {
        synth.cancel()
      } else {
        console.log('[useSpeech] 当前有更高优先级播报，已跳过', {
          category: resolvedOptions.category,
          priority: resolvedOptions.priority,
          speaking: synth.speaking,
          pending: synth.pending,
        })
        return
      }
    }

    const segments = buildSpeechSegments(
      normalizedText,
      Math.max(20, resolvedOptions.maxSegmentLength)
    )
    if (!segments.length) {
      return
    }

    activeSpeakToken += 1
    activePriority = nextPriority
    lastSpeechSignature = signature
    lastSpeechAt = now
    if (resolvedOptions.throttleKey) {
      clearScheduledSpeech(resolvedOptions.throttleKey)
      throttledSpeechAt.set(resolvedOptions.throttleKey, now)
    }

    console.log('[useSpeech] speak:', {
      category: resolvedOptions.category,
      priority: resolvedOptions.priority,
      segments: segments.length,
      rate: resolvedOptions.rate,
      pitch: resolvedOptions.pitch,
      volume: resolvedOptions.volume,
    })
    speakSegments(synth, segments, resolvedOptions, activeSpeakToken)
  } catch (e) {
    console.error('[useSpeech] speak 调用失败:', e)
  }
}

export function enableSpeech() {
  isSpeechEnabled.value = true
  persistSpeechEnabled(true)
}

export function disableSpeech() {
  isSpeechEnabled.value = false
  persistSpeechEnabled(false)
}

export function toggleSpeech() {
  if (isSpeechEnabled.value) disableSpeech()
  else enableSpeech()
}

/**
 * 供组件使用的入口：初始化、提供状态与操作
 */
export function useSpeech() {
  onMounted(() => {
    if (_initialized) return
    _initialized = true
    isSpeechEnabled.value = getPreferredSpeechEnabled()
    console.log('[useSpeech] 初始化 isSpeechEnabled=', isSpeechEnabled.value)
    loadVoices()
  })

  return {
    isSpeechEnabled,
    isSpeechSupported,
    speak,
    enableSpeech,
    disableSpeech,
    toggleSpeech,
  }
}

export default useSpeech
