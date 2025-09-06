import { api } from '@/utils/api'

/**
 * 图片上传API
 */
export const uploadApi = {
  /**
   * 上传药品图片
   * @param file 选择的图片文件
   * @returns ApiResponse<{ url: string }>
   */
  uploadMedicineImage: async (file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('image', file)
    console.log('[uploadApi] 上传药品图片 - 开始')
    const res = await api.post('/medicines/upload-image/', formData, { isFormData: true })
    console.log('[uploadApi] 上传药品图片 - 响应', res)
    return res
  }
}