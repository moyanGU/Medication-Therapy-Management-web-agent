import { toast } from 'sonner'

/**
 * Toast 通知工具
 */
export const useToast = () => {
  const success = (message: string, options?: any) => {
    toast.success(message, options)
  }

  const error = (message: string, options?: any) => {
    toast.error(message, options)
  }

  const warning = (message: string, options?: any) => {
    toast.warning(message, options)
  }

  const info = (message: string, options?: any) => {
    toast.info(message, options)
  }

  const loading = (message: string, options?: any) => {
    return toast.loading(message, options)
  }

  const dismiss = (toastId?: string | number) => {
    toast.dismiss(toastId)
  }

  return {
    success,
    error,
    warning,
    info,
    loading,
    dismiss
  }
}