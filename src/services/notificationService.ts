/**
 * 通知服务 - 处理浏览器通知权限和通知显示
 */

export interface NotificationOptions {
  title: string
  body: string
  icon?: string
  badge?: string
  tag?: string
  requireInteraction?: boolean
  silent?: boolean
  vibrate?: number[]
  actions?: NotificationAction[]
  data?: any
}

export interface NotificationAction {
  action: string
  title: string
  icon?: string
}

export interface NotificationPermissionResult {
  permission: NotificationPermission
  supported: boolean
  message: string
}

export interface NotificationResult {
  success: boolean
  notification?: Notification
  error?: string
}

class NotificationService {
  private static instance: NotificationService
  private activeNotifications: Map<string, Notification> = new Map()
  private permissionCallbacks: Array<(permission: NotificationPermission) => void> = []

  private constructor() {
    this.init()
  }

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService()
    }
    return NotificationService.instance
  }

  /**
   * 初始化通知服务
   */
  private init(): void {
    // 监听通知权限变化
    if (this.isSupported()) {
      // 某些浏览器支持权限变化监听
      if ('permissions' in navigator) {
        navigator.permissions.query({ name: 'notifications' as PermissionName })
          .then(permissionStatus => {
            permissionStatus.addEventListener('change', () => {
              this.notifyPermissionChange(permissionStatus.state as NotificationPermission)
            })
          })
          .catch(() => {
            // 忽略不支持的浏览器
          })
      }
    }
  }

  /**
   * 检查浏览器是否支持通知
   */
  public isSupported(): boolean {
    return 'Notification' in window
  }

  /**
   * 获取当前通知权限状态
   */
  public getPermission(): NotificationPermission {
    if (!this.isSupported()) {
      return 'denied'
    }
    return Notification.permission
  }

  /**
   * 检查通知权限状态
   */
  public checkPermission(): NotificationPermissionResult {
    if (!this.isSupported()) {
      return {
        permission: 'denied',
        supported: false,
        message: '您的浏览器不支持通知功能'
      }
    }

    const permission = this.getPermission()
    let message = ''

    switch (permission) {
      case 'granted':
        message = '通知权限已授予'
        break
      case 'denied':
        message = '通知权限被拒绝，请在浏览器设置中手动开启'
        break
      case 'default':
        message = '需要申请通知权限'
        break
    }

    return {
      permission,
      supported: true,
      message
    }
  }

  /**
   * 请求通知权限
   */
  public async requestPermission(): Promise<NotificationPermissionResult> {
    if (!this.isSupported()) {
      return {
        permission: 'denied',
        supported: false,
        message: '您的浏览器不支持通知功能'
      }
    }

    try {
      const permission = await Notification.requestPermission()
      this.notifyPermissionChange(permission)
      
      let message = ''
      switch (permission) {
        case 'granted':
          message = '通知权限申请成功'
          break
        case 'denied':
          message = '通知权限被拒绝'
          break
        case 'default':
          message = '通知权限申请被忽略'
          break
      }

      return {
        permission,
        supported: true,
        message
      }
    } catch (error) {
      console.error('申请通知权限失败:', error)
      return {
        permission: 'denied',
        supported: true,
        message: '申请通知权限失败'
      }
    }
  }

  /**
   * 显示通知
   */
  public async showNotification(options: NotificationOptions): Promise<NotificationResult> {
    // 检查权限
    const permissionResult = this.checkPermission()
    if (!permissionResult.supported) {
      return {
        success: false,
        error: permissionResult.message
      }
    }

    if (permissionResult.permission !== 'granted') {
      // 尝试申请权限
      const requestResult = await this.requestPermission()
      if (requestResult.permission !== 'granted') {
        return {
          success: false,
          error: requestResult.message
        }
      }
    }

    try {
      // 创建通知
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon || this.getDefaultIcon(),
        badge: options.badge,
        tag: options.tag,
        requireInteraction: options.requireInteraction || false,
        silent: options.silent || false,
        vibrate: options.vibrate,
        actions: options.actions,
        data: options.data
      })

      // 设置事件监听器
      this.setupNotificationEvents(notification, options)

      // 存储活跃通知
      if (options.tag) {
        // 如果有相同tag的通知，先关闭
        this.closeNotificationByTag(options.tag)
        this.activeNotifications.set(options.tag, notification)
      }

      return {
        success: true,
        notification
      }
    } catch (error) {
      console.error('显示通知失败:', error)
      return {
        success: false,
        error: '显示通知失败'
      }
    }
  }

  /**
   * 显示用药提醒通知
   */
  public async showMedicationReminder(data: {
    medicationName: string
    dosage: string
    time: string
    reminderId: number
  }): Promise<NotificationResult> {
    const options: NotificationOptions = {
      title: '用药提醒',
      body: `该服用 ${data.medicationName} 了\n剂量：${data.dosage}\n时间：${data.time}`,
      icon: this.getMedicationIcon(),
      tag: `medication-${data.reminderId}`,
      requireInteraction: true,
      vibrate: [200, 100, 200],
      actions: [
        {
          action: 'taken',
          title: '已服用',
          icon: '/icons/check.png'
        },
        {
          action: 'snooze',
          title: '稍后提醒',
          icon: '/icons/clock.png'
        },
        {
          action: 'skip',
          title: '跳过',
          icon: '/icons/x.png'
        }
      ],
      data: {
        type: 'medication-reminder',
        reminderId: data.reminderId,
        medicationName: data.medicationName
      }
    }

    return this.showNotification(options)
  }

  /**
   * 显示测试通知
   */
  public async showTestNotification(): Promise<NotificationResult> {
    const options: NotificationOptions = {
      title: '测试通知',
      body: '这是一个测试通知，用于验证通知功能是否正常工作。',
      icon: this.getDefaultIcon(),
      tag: 'test-notification',
      requireInteraction: false,
      data: {
        type: 'test'
      }
    }

    return this.showNotification(options)
  }

  /**
   * 关闭指定tag的通知
   */
  public closeNotificationByTag(tag: string): void {
    const notification = this.activeNotifications.get(tag)
    if (notification) {
      notification.close()
      this.activeNotifications.delete(tag)
    }
  }

  /**
   * 关闭所有通知
   */
  public closeAllNotifications(): void {
    this.activeNotifications.forEach(notification => {
      notification.close()
    })
    this.activeNotifications.clear()
  }

  /**
   * 获取活跃通知数量
   */
  public getActiveNotificationCount(): number {
    return this.activeNotifications.size
  }

  /**
   * 注册权限变化回调
   */
  public onPermissionChange(callback: (permission: NotificationPermission) => void): void {
    this.permissionCallbacks.push(callback)
  }

  /**
   * 移除权限变化回调
   */
  public offPermissionChange(callback: (permission: NotificationPermission) => void): void {
    const index = this.permissionCallbacks.indexOf(callback)
    if (index > -1) {
      this.permissionCallbacks.splice(index, 1)
    }
  }

  /**
   * 设置通知事件监听器
   */
  private setupNotificationEvents(notification: Notification, options: NotificationOptions): void {
    notification.addEventListener('show', () => {
      console.log('通知已显示:', options.title)
    })

    notification.addEventListener('click', (event) => {
      console.log('通知被点击:', options.title)
      
      // 处理通知点击事件
      this.handleNotificationClick(notification, options)
      
      // 关闭通知
      notification.close()
    })

    notification.addEventListener('close', () => {
      console.log('通知已关闭:', options.title)
      
      // 从活跃通知中移除
      if (options.tag) {
        this.activeNotifications.delete(options.tag)
      }
    })

    notification.addEventListener('error', (error) => {
      console.error('通知错误:', error)
    })

    // 自动关闭通知（如果不需要交互）
    if (!options.requireInteraction) {
      setTimeout(() => {
        if (notification) {
          notification.close()
        }
      }, 5000) // 5秒后自动关闭
    }
  }

  /**
   * 处理通知点击事件
   */
  private handleNotificationClick(notification: Notification, options: NotificationOptions): void {
    // 聚焦到窗口
    if (window.focus) {
      window.focus()
    }

    // 根据通知类型处理
    if (options.data?.type === 'medication-reminder') {
      // 跳转到提醒详情页面
      const reminderId = options.data.reminderId
      if (reminderId) {
        window.location.href = `/reminders/${reminderId}`
      }
    }
  }

  /**
   * 通知权限变化
   */
  private notifyPermissionChange(permission: NotificationPermission): void {
    this.permissionCallbacks.forEach(callback => {
      try {
        callback(permission)
      } catch (error) {
        console.error('权限变化回调执行失败:', error)
      }
    })
  }

  /**
   * 获取默认图标
   */
  private getDefaultIcon(): string {
    return '/icons/notification-default.png'
  }

  /**
   * 获取用药图标
   */
  private getMedicationIcon(): string {
    return '/icons/medication.png'
  }

  /**
   * 检查是否在安静时间
   */
  public isQuietTime(): boolean {
    const now = new Date()
    const hour = now.getHours()
    
    // 默认安静时间：22:00 - 08:00
    return hour >= 22 || hour < 8
  }

  /**
   * 获取通知设置建议
   */
  public getNotificationSettings(): {
    permission: NotificationPermissionResult
    recommendations: string[]
  } {
    const permission = this.checkPermission()
    const recommendations: string[] = []

    if (!permission.supported) {
      recommendations.push('建议使用支持通知功能的现代浏览器')
    } else if (permission.permission === 'denied') {
      recommendations.push('请在浏览器设置中允许通知权限')
      recommendations.push('在地址栏左侧点击锁图标，允许通知')
    } else if (permission.permission === 'default') {
      recommendations.push('建议允许通知权限以获得最佳体验')
    } else {
      recommendations.push('通知功能已正常启用')
      if (this.isQuietTime()) {
        recommendations.push('当前处于安静时间，通知可能会被静音')
      }
    }

    return {
      permission,
      recommendations
    }
  }
}

// 导出单例实例
export const notificationService = NotificationService.getInstance()

// 导出类型
export type { NotificationService }

// 默认导出
export default notificationService