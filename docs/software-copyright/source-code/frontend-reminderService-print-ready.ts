// =============================================================================
// MTM-用药助手 - 前端核心服务代码
// 文件: src/services/reminderService.ts
// 页码: 1-7/60
// =============================================================================

/**
 * 用药提醒服务 - 核心业务逻辑
 * 负责用药提醒的创建、管理、调度和通知发送
 */

// API响应分页接口定义
interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// API响应基础接口
interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}

// 模拟API客户端
const api = {
  get: async <T>(url: string, config?: any): Promise<{ data: T }> => {
    return { data: {} as T }
  },
  post: async <T>(url: string, data?: any): Promise<{ data: T }> => {
    return { data: {} as T }
  },
  patch: async <T>(url: string, data?: any): Promise<{ data: T }> => {
    return { data: {} as T }
  },
  delete: async (url: string): Promise<void> => {}
}

// ==================== 接口定义 ====================

/**
 * 提醒实体接口
 * 包含用药提醒的所有业务属性
 */
export interface Reminder {
  id: number
  user: number
  
  /**
   * 药品信息 - 智能类型处理
   * 后端在不同序列化器下返回不同格式
   */
  medicine: number | {
    id: number
    name?: string
    medicine_type?: string
    specification?: string
  }
  
  /** 药品名称（派生字段） */
  medicine_name?: string
  
  /** 药品图片 */
  medicine_image?: string
  
  /** 提醒时间 */
  reminder_time: string
  
  /** 用药频率 */
  frequency: 'daily' | 'twice_daily' | 'three_times_daily' | 
            'four_times_daily' | 'weekly' | 'every_other_day' | 'custom'
  
  /** 剂量 */
  dosage: number
  
  /** 剂量单位 */
  dosage_unit: 'tablet' | 'capsule' | 'ml' | 'mg' | 'g' | 
               'drop' | 'spray' | 'patch' | 'injection'
  
  /** 是否激活 */
  is_active: boolean
  
  /** 提醒标题 */
  title?: string
  
  /** 提醒消息 */
  message?: string
  
  /** 通知类型 */
  notification_types: string[]
  
  /** 提前分钟数 */
  advance_minutes: number
  
  /** 重复间隔 */
  repeat_interval: number
  
  /** 最大重复次数 */
  max_repeats: number
  
  /** 开始日期 */
  start_date: string
  
  /** 结束日期 */
  end_date?: string
  
  /** 星期几 */
  weekdays: number[]
  
  /** 用餐时间 */
  meal_timing: 'before_meal' | 'after_meal' | 'with_meal' | 'anytime'
  
  /** 特殊说明 */
  special_instructions?: string
  
  /** 最后提醒时间 */
  last_reminded_at?: string
  
  /** 提醒次数统计 */
  reminder_count: number
  
  /** 响应次数统计 */
  response_count: number
  
  /** 创建时间 */
  created_at: string
  
  /** 更新时间 */
  updated_at: string
}

/**
 * 创建提醒接口
 */
export interface ReminderCreate {
  medicine: number
  reminder_time: string
  frequency: string
  dosage: number
  dosage_unit: string
  is_active?: boolean
  title?: string
  message?: string
  notification_types?: string[]
  advance_minutes?: number
  repeat_interval?: number
  max_repeats?: number
  start_date: string
  end_date?: string
  weekdays?: number[]
  meal_timing?: string
  special_instructions?: string
}

/**
 * 更新提醒接口
 */
export interface ReminderUpdate extends Partial<ReminderCreate> {
  id: number
}

/**
 * 提醒统计接口
 */
export interface ReminderStats {
  total: number
  active: number
  completed_today: number
  pending_today: number
  adherence_rate: number
}

// ==================== 服务类实现 ====================

/**
 * 用药提醒服务类
 * 封装所有提醒相关的API调用和业务逻辑
 */
class ReminderService {
  
  /**
   * 获取用户的所有提醒
   */
  async getReminders(params?: {
    page?: number
    page_size?: number
    is_active?: boolean
  }): Promise<PaginatedResponse<Reminder>> {
    try {
      const response = await api.get<PaginatedResponse<Reminder>>('/reminders/', { params })
      return response.data
    } catch (error) {
      console.error('获取提醒列表失败:', error)
      throw error
    }
  }
  
  /**
   * 获取单个提醒详情
   */
  async getReminder(id: number): Promise<Reminder> {
    try {
      const response = await api.get<Reminder>(`/reminders/${id}/`)
      return response.data
    } catch (error) {
      console.error('获取提醒详情失败:', error)
      throw error
    }
  }
  
  /**
   * 创建新提醒
   * 核心业务方法，包含完整的验证逻辑
   */
  async createReminder(reminderData: ReminderCreate): Promise<Reminder> {
    try {
      // 数据验证
      this.validateReminderData(reminderData)
      
      const response = await api.post<Reminder>('/reminders/', reminderData)
      return response.data
    } catch (error) {
      console.error('创建提醒失败:', error)
      throw error
    }
  }
  
  /**
   * 更新提醒
   */
  async updateReminder(id: number, updateData: Partial<ReminderCreate>): Promise<Reminder> {
    try {
      const response = await api.patch<Reminder>(`/reminders/${id}/`, updateData)
      return response.data
    } catch (error) {
      console.error('更新提醒失败:', error)
      throw error
    }
  }
  
  /**
   * 删除提醒
   */
  async deleteReminder(id: number): Promise<void> {
    try {
      await api.delete(`/reminders/${id}/`)
    } catch (error) {
      console.error('删除提醒失败:', error)
      throw error
    }
  }
  
  /**
   * 获取提醒统计信息
   * 用于仪表盘显示
   */
  async getReminderStats(): Promise<ReminderStats> {
    try {
      const response = await api.get<ReminderStats>('/reminders/stats/')
      return response.data
    } catch (error) {
      console.error('获取提醒统计失败:', error)
      throw error
    }
  }
  
  /**
   * 标记提醒为已完成
   */
  async markAsCompleted(id: number): Promise<Reminder> {
    try {
      const response = await api.post<Reminder>(`/reminders/${id}/complete/`)
      return response.data
    } catch (error) {
      console.error('标记提醒完成失败:', error)
      throw error
    }
  }
  
  /**
   * 跳过本次提醒
   */
  async skipReminder(id: number): Promise<Reminder> {
    try {
      const response = await api.post<Reminder>(`/reminders/${id}/skip/`)
      return response.data
    } catch (error) {
      console.error('跳过提醒失败:', error)
      throw error
    }
  }
  
  // ==================== 工具方法 ====================
  
  /**
   * 验证提醒数据
   * 核心验证逻辑，确保数据完整性
   */
  private validateReminderData(data: ReminderCreate): void {
    if (!data.medicine) {
      throw new Error('药品不能为空')
    }
    
    if (!data.reminder_time) {
      throw new Error('提醒时间不能为空')
    }
    
    if (!data.dosage || data.dosage <= 0) {
      throw new Error('剂量必须大于0')
    }
    
    if (!data.dosage_unit) {
      throw new Error('剂量单位不能为空')
    }
    
    // 验证时间格式
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/
    if (!timeRegex.test(data.reminder_time)) {
      throw new Error('提醒时间格式不正确')
    }
    
    // 验证日期范围
    if (data.start_date && data.end_date) {
      const startDate = new Date(data.start_date)
      const endDate = new Date(data.end_date)
      
      if (startDate > endDate) {
        throw new Error('开始日期不能晚于结束日期')
      }
    }
  }
  
  /**
   * 计算下次提醒时间
   * 基于频率设置的智能计算算法
   */
  calculateNextReminderTime(
    frequency: string,
    lastReminderTime: Date,
    weekdays?: number[]
  ): Date {
    const nextTime = new Date(lastReminderTime)
    
    switch (frequency) {
      case 'daily':
        nextTime.setDate(nextTime.getDate() + 1)
        break
        
      case 'twice_daily':
        nextTime.setHours(nextTime.getHours() + 12)
        break
        
      case 'three_times_daily':
        nextTime.setHours(nextTime.getHours() + 8)
        break
        
      case 'weekly':
        nextTime.setDate(nextTime.getDate() + 7)
        break
        
      case 'every_other_day':
        nextTime.setDate(nextTime.getDate() + 2)
        break
        
      case 'custom':
        if (weekdays && weekdays.length > 0) {
          // 计算下一个指定星期几
          const currentDay = nextTime.getDay()
          const nextDay = this.findNextWeekday(currentDay, weekdays)
          nextTime.setDate(nextTime.getDate() + (nextDay - currentDay + 7) % 7)
        }
        break
        
      default:
        nextTime.setDate(nextTime.getDate() + 1)
    }
    
    return nextTime
  }
  
  /**
   * 查找下一个指定的星期几
   */
  private findNextWeekday(currentDay: number, weekdays: number[]): number {
    const sortedDays = [...weekdays].sort((a, b) => a - b)
    
    for (const day of sortedDays) {
      if (day > currentDay) {
        return day
      }
    }
    
    // 如果当前日期已经过了所有指定日期，返回第一个
    return sortedDays[0]
  }
  
  /**
   * 生成提醒消息内容
   * 根据用药信息智能生成提醒文本
   */
  generateReminderMessage(reminder: Reminder): string {
    const medicineName = typeof reminder.medicine === 'object' 
      ? reminder.medicine.name 
      : reminder.medicine_name || '药品'
    
    const dosageInfo = `${reminder.dosage}${this.getDosageUnitText(reminder.dosage_unit)}`
    
    let message = `用药时间到了！请服用${medicineName}，剂量：${dosageInfo}`
    
    if (reminder.meal_timing && reminder.meal_timing !== 'anytime') {
      const timingMap: Record<string, string> = {
        'before_meal': '餐前',
        'after_meal': '餐后', 
        'with_meal': '随餐'
      }
      message += `，${timingMap[reminder.meal_timing]}`
    }
    
    if (reminder.special_instructions) {
      message += `。特别说明：${reminder.special_instructions}`
    }
    
    return message
  }
  
  /**
   * 获取剂量单位的中文描述
   */
  private getDosageUnitText(unit: string): string {
    const unitMap: Record<string, string> = {
      'tablet': '片',
      'capsule': '粒',
      'ml': '毫升',
      'mg': '毫克',
      'g': '克',
      'drop': '滴',
      'spray': '喷',
      'patch': '贴',
      'injection': '支'
    }
    
    return unitMap[unit] || unit
  }
  
  /**
   * 检查用药冲突
   * 基于药品类型和用法的简单冲突检测
   */
  checkMedicationConflict(reminders: Reminder[]): string[] {
    const conflicts: string[] = []
    const now = new Date()
    
    // 按药品分组
    const medicineGroups = new Map<number, Reminder[]>()
    
    reminders.forEach(reminder => {
      if (reminder.is_active) {
        const medicineId = typeof reminder.medicine === 'object' 
          ? reminder.medicine.id 
          : reminder.medicine
        
        if (!medicineGroups.has(medicineId)) {
          medicineGroups.set(medicineId, [])
        }
        medicineGroups.get(medicineId)!.push(reminder)
      }
    })
    
    // 检查同一药品的重复用药
    medicineGroups.forEach((groupReminders, medicineId) => {
      if (groupReminders.length > 1) {
        const activeReminders = groupReminders.filter(r => 
          this.isReminderActive(r, now)
        )
        
        if (activeReminders.length > 1) {
          const medicineName = typeof activeReminders[0].medicine === 'object'
            ? activeReminders[0].medicine.name
            : '该药品'
          
          conflicts.push(`检测到${medicineName}的重复用药提醒`)
        }
      }
    })
    
    return conflicts
  }
  
  /**
   * 检查提醒是否处于活跃状态
   */
  private isReminderActive(reminder: Reminder, currentTime: Date): boolean {
    if (!reminder.is_active) return false
    
    const startDate = new Date(reminder.start_date)
    if (currentTime < startDate) return false
    
    if (reminder.end_date) {
      const endDate = new Date(reminder.end_date)
      if (currentTime > endDate) return false
    }
    
    return true
  }
}

// 创建单例实例
export const reminderService = new ReminderService()

export default reminderService