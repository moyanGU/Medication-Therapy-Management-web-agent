/**
 * useSpeech.ts - 语音播报可访问性支持
 * 功能：
 * 1. 提供 isSpeechEnabled 全局状态（localStorage 持久化）
 * 2. 检测浏览器是否支持 SpeechSynthesis
 * 3. 提供 speak(text) 播报接口，自动选择中文语音或默认语音
 * 4. 提供 enableSpeech / disableSpeech / toggleSpeech 切换接口
 * 5. 初始化时尝试预加载可用语音列表
 */
import { ref, computed, onMounted } from 'vue';

const STORAGE_KEY = 'mtm.speech.enabled';

// 单例缓存，避免在多个组件中重复初始化
let _initialized = false;
const isSpeechEnabled = ref(false);
const voices = ref<SpeechSynthesisVoice[]>([]);

/**
 * 获取浏览器是否支持 speechSynthesis
 */
export const isSpeechSupported = computed(() => {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
});

/**
 * 从 localStorage 读取语音播报开关
 */
function getPreferredSpeechEnabled(): boolean {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw === '1';
  } catch (e) {
    console.warn('[useSpeech] 读取本地语音播报开关失败:', e);
    return false;
  }
}

/**
 * 持久化语音播报开关
 */
function persistSpeechEnabled(value: boolean) {
  try {
    localStorage.setItem(STORAGE_KEY, value ? '1' : '0');
  } catch (e) {
    console.warn('[useSpeech] 持久化语音播报开关失败:', e);
  }
}

/**
 * 预加载语音列表（部分浏览器需要调用一次获取）
 */
function loadVoices() {
  try {
    if (!isSpeechSupported.value) return;
    const synth = window.speechSynthesis;
    const list = synth.getVoices();
    if (list && list.length) {
      voices.value = list;
      console.log('[useSpeech] 已加载语音列表:', list.map(v => `${v.name}(${v.lang})`));
    } else {
      // 部分浏览器需要监听 voiceschanged 事件
      synth.onvoiceschanged = () => {
        voices.value = synth.getVoices();
        console.log('[useSpeech] voiceschanged 触发，语音列表:', voices.value.map(v => `${v.name}(${v.lang})`));
      };
    }
  } catch (e) {
    console.warn('[useSpeech] 加载语音列表失败:', e);
  }
}

/**
 * 选择一个最合适的语音（优先中文）
 */
function pickVoice(preferLangs: string[] = ['zh-CN', 'zh', 'zh-TW']): SpeechSynthesisVoice | null {
  if (!voices.value.length) return null;
  for (const lang of preferLangs) {
    const match = voices.value.find(v => v.lang?.toLowerCase().startsWith(lang.toLowerCase()));
    if (match) return match;
  }
  // 退化为第一个语音
  return voices.value[0] ?? null;
}

/**
 * 播报文本
 */
export function speak(text: string, rate = 0.8) {
  if (!isSpeechSupported.value) {
    console.warn('[useSpeech] 当前浏览器不支持 SpeechSynthesis');
    return;
  }
  if (!isSpeechEnabled.value) {
    console.log('[useSpeech] 语音播报未开启，忽略 speak');
    return;
  }
  try {
    const utter = new SpeechSynthesisUtterance(text);
    const voice = pickVoice();
    if (voice) utter.voice = voice;
    utter.rate = rate; // 语速默认 1.0，可调慢一些以便老年用户理解
    console.log('[useSpeech] speak:', { text, voice: voice?.name, lang: voice?.lang, rate });
    window.speechSynthesis.cancel(); // 先取消队列，避免叠加
    window.speechSynthesis.speak(utter);
  } catch (e) {
    console.error('[useSpeech] speak 调用失败:', e);
  }
}

export function enableSpeech() {
  isSpeechEnabled.value = true;
  persistSpeechEnabled(true);
}

export function disableSpeech() {
  isSpeechEnabled.value = false;
  persistSpeechEnabled(false);
}

export function toggleSpeech() {
  if (isSpeechEnabled.value) disableSpeech(); else enableSpeech();
}

/**
 * 供组件使用的入口：初始化、提供状态与操作
 */
export function useSpeech() {
  onMounted(() => {
    if (_initialized) return;
    _initialized = true;
    isSpeechEnabled.value = getPreferredSpeechEnabled();
    console.log('[useSpeech] 初始化 isSpeechEnabled=', isSpeechEnabled.value);
    loadVoices();
  });

  return {
    isSpeechEnabled,
    isSpeechSupported,
    speak,
    enableSpeech,
    disableSpeech,
    toggleSpeech,
  };
}

export default useSpeech;