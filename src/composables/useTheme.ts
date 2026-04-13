import { ref, watchEffect, computed } from 'vue'

type Theme = 'light' | 'dark'

/**
 * 主题与辅助模式（老年人模式）管理
 * - 管理 light/dark 主题
 * - 管理老年人模式 isSenior（增加字体、对比度、可点击目标大小等）
 * - 将状态持久化到 localStorage，并在挂载时应用到 documentElement
 */
export function useTheme() {
  const getPreferredTheme = (): Theme => {
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved === 'light' || saved === 'dark') return saved
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
  }

  const getPreferredSeniorMode = (): boolean => {
    const saved = localStorage.getItem('seniorMode')
    return saved === 'true'
  }

  const theme = ref<Theme>(getPreferredTheme())
  const isSenior = ref<boolean>(getPreferredSeniorMode())

  /**
   * 应用主题到根元素（html）并持久化
   */
  const applyTheme = (t: Theme) => {
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(t)
    localStorage.setItem('theme', t)
    console.log('[useTheme] 应用主题:', t)
  }

  /**
   * 切换主题（light <-> dark）
   */
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  /**
   * 应用老年人模式样式类到根元素（html）并持久化
   */
  const applySeniorMode = (enabled: boolean) => {
    document.documentElement.classList.toggle('senior', enabled)
    localStorage.setItem('seniorMode', String(enabled))
    console.log('[useTheme] 老年人模式:', enabled ? '开启' : '关闭')
  }

  /**
   * 开启老年人模式
   */
  const enableSenior = () => {
    isSenior.value = true
  }

  /**
   * 关闭老年人模式
   */
  const disableSenior = () => {
    isSenior.value = false
  }

  /**
   * 切换老年人模式
   */
  const toggleSenior = () => {
    isSenior.value = !isSenior.value
  }

  // 响应式监听：主题与老年人模式变化即时应用
  watchEffect(() => {
    applyTheme(theme.value)
    applySeniorMode(isSenior.value)
  })

  return {
    theme,
    toggleTheme,
    isDark: computed(() => theme.value === 'dark'),
    isSenior,
    enableSenior,
    disableSenior,
    toggleSenior,
  }
}
