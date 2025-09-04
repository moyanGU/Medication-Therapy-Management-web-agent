/**
 * 药品类型枚举
 */
export enum MedicineType {
  PRESCRIPTION = 'prescription',
  OTC = 'otc',
  SUPPLEMENT = 'supplement',
  HERBAL = 'herbal'
}

/**
 * 药品剂型枚举
 */
export enum DosageForm {
  TABLET = 'tablet',
  CAPSULE = 'capsule',
  LIQUID = 'liquid',
  INJECTION = 'injection',
  CREAM = 'cream',
  OINTMENT = 'ointment',
  DROPS = 'drops',
  SPRAY = 'spray',
  POWDER = 'powder',
  PATCH = 'patch'
}

/**
 * 药品基础信息接口
 */
export interface Medicine {
  id: number
  name: string
  specification?: string
  manufacturer?: string
  medicine_type: string
  quantity: number
  purchase_price?: number
  purchase_date?: string
  expiry_date?: string
  batch_number?: string
  storage_conditions?: string
  description?: string
  image_path?: string
  is_prescription: boolean
  created_at: string
  updated_at: string
  is_expired: boolean
  is_low_stock: boolean
  days_until_expiry?: number
}

/**
 * 创建药品数据接口
 */
export interface MedicineCreateData {
  name: string
  specification?: string
  manufacturer?: string
  medicine_type: string
  quantity: number
  purchase_price?: number
  purchase_date?: string
  expiry_date?: string
  batch_number?: string
  storage_conditions?: string
  description?: string
  image_path?: string
  is_prescription?: boolean
}

/**
 * 更新药品数据接口
 */
export interface MedicineUpdateData {
  name?: string
  specification?: string
  manufacturer?: string
  medicine_type?: string
  quantity?: number
  purchase_price?: number
  purchase_date?: string
  expiry_date?: string
  batch_number?: string
  storage_conditions?: string
  description?: string
  image_path?: string
  is_prescription?: boolean
}

/**
 * 药品列表查询参数接口
 */
export interface MedicineListParams {
  page?: number
  page_size?: number
  search?: string
  type?: MedicineType
  dosage_form?: DosageForm
  manufacturer?: string
  prescription_required?: boolean
  is_expired?: boolean
  is_low_stock?: boolean
  ordering?: string
}

/**
 * 药品统计信息接口
 */
export interface MedicineStatistics {
  total_medicines: number
  total_value: number
  expired_count: number
  expiring_soon_count: number
  low_stock_count: number
  prescription_count: number
  otc_count: number
  by_type: Record<MedicineType, number>
  by_dosage_form: Record<DosageForm, number>
}

/**
 * 药品类型选项接口
 */
export interface MedicineTypeOption {
  value: MedicineType
  label: string
}

/**
 * 剂型选项接口
 */
export interface DosageFormOption {
  value: DosageForm
  label: string
}

/**
 * 分页响应接口
 */
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
  page_size: number
  current_page: number
  total_pages: number
}

/**
 * API响应接口
 */
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  errors?: Record<string, string[]>
}