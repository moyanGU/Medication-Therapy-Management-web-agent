import { api } from '@/utils/api'
import type { ApiResponse } from '@/utils/api'

/**
 * 图片上传API
 */
export const uploadApi = {
  /**
   * 上传药品图片
   * @param file 选择的图片文件
   * @returns ApiResponse<{ image_path: string }>
   */
  uploadMedicineImage: async (file: File): Promise<ApiResponse<{ image_path: string }>> => {
    // 构造表单数据并发起上传请求
    const formData = new FormData()
    formData.append('image', file)
    console.log('[uploadApi] 上传药品图片 - 开始', { name: file?.name, size: file?.size })

    // 使用 ApiClient 统一处理响应格式与错误
    const res = await api.post<{ image_path: string }>(
      '/medicines/upload-image/',
      formData,
      { isFormData: true }
    )

    console.log('[uploadApi] 上传药品图片 - 响应', res)
    return res
  }
}