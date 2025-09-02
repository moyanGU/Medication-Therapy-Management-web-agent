import { createPinia } from 'pinia'

/**
 * Pinia状态管理配置
 * 创建并导出pinia实例
 */
export const pinia = createPinia()

// 导出所有store
export { useUserStore } from './user'
export { useMedicineStore } from './medicine'
export { useRecordStore } from './record'

// 类型定义
export type { } from './user'
export type { } from './medicine'
export type { } from './record'