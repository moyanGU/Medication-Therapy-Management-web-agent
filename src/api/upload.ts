import { http } from '@/utils/http'

/**
 * 图片上传API
 */
export const uploadApi = {
  /**
   * 上传药品图片
   */
  uploadMedicineImage(file: File) {
    const formData = new FormData()
    formData.append('image', file)
    
    return http.post('/api/medicines/upload-image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}