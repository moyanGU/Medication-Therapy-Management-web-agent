import { ref, computed } from 'vue'

export const useNotification = () => {
  const permission = ref<NotificationPermission>('default')
  const isSupported = computed(() => 'Notification' in window)

  const requestPermission = async () => {
    if (!isSupported.value) return 'denied'
    const result = await Notification.requestPermission()
    permission.value = result
    return result
  }

  const showNotification = (title: string, options?: NotificationOptions) => {
    if (!isSupported.value || permission.value !== 'granted') return null
    return new Notification(title, { icon: '/favicon.svg', ...options })
  }

  return { permission, isSupported, requestPermission, showNotification }
}

export const getGlobalNotification = () => useNotification()
