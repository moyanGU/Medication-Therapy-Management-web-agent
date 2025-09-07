import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter, Edit, Trash2, AlertTriangle, Calendar, Package } from 'lucide-react'
import { useMedicineStore } from '@/stores/medicine'
import { MedicineType, type MedicineListParams } from '@/types/medicine'
import { toast } from 'sonner'

/**
 * 药品列表页面组件
 */
export default function MedicineList() {
  const {
    medicines,
    loading,
    error,
    pagination,
    fetchMedicines,
    deleteMedicine,
    searchMedicines
  } = useMedicineStore()

  // 搜索和筛选状态
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState<MedicineListParams>({
    page: 1,
    page_size: 20
  })
  const [showFilters, setShowFilters] = useState(false)

  // 页面加载时获取药品列表
  useEffect(() => {
    fetchMedicines(filters)
  }, [filters, fetchMedicines])

  // 处理搜索
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const newFilters = {
      ...filters,
      search: searchTerm,
      page: 1
    }
    setFilters(newFilters)
  }

  // 处理筛选器变化
  const handleFilterChange = (key: keyof MedicineListParams, value: any) => {
    const newFilters = {
      ...filters,
      [key]: value,
      page: 1
    }
    setFilters(newFilters)
  }

  // 处理分页
  const handlePageChange = (page: number) => {
    setFilters({ ...filters, page })
  }

  // 处理删除药品
  const handleDelete = async (id: number, name: string) => {
    if (window.confirm(`确定要删除药品 "${name}" 吗？`)) {
      try {
        await deleteMedicine(id)
        toast.success('药品删除成功')
        fetchMedicines(filters) // 重新加载列表
      } catch (error) {
        toast.error('删除失败，请重试')
      }
    }
  }

  // 清除筛选器
  const clearFilters = () => {
    setFilters({
      page: 1,
      page_size: 20
    })
    setSearchTerm('')
  }

  // 获取药品状态标签
  const getStatusBadges = (medicine: any) => {
    const badges = []
    
    if (medicine.is_expired) {
      badges.push(
        <span key="expired" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertTriangle className="w-3 h-3 mr-1" />
          已过期
        </span>
      )
    } else if (medicine.days_until_expiry !== undefined && medicine.days_until_expiry <= 30) {
      badges.push(
        <span key="expiring" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <Calendar className="w-3 h-3 mr-1" />
          即将过期
        </span>
      )
    }
    
    if (medicine.is_low_stock) {
      badges.push(
        <span key="low-stock" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
          <Package className="w-3 h-3 mr-1" />
          库存不足
        </span>
      )
    }
    
    return badges
  }

  // 渲染药品类型中文标签
  const renderTypeLabel = (medicine_type?: string) => {
    switch (medicine_type) {
      case MedicineType.PRESCRIPTION:
        return '处方药'
      case MedicineType.OTC:
        return '非处方药'
      case MedicineType.SUPPLEMENT:
        return '保健品'
      case MedicineType.HERBAL:
        return '中药'
      default:
        return medicine_type || '-'
    }
  }

  // 生成图片URL（与 Vue 页面保持一致的构建规则）
  const getImageUrl = (image_path?: string | null) => {
    if (!image_path) return null
    if (image_path.startsWith('http://') || image_path.startsWith('https://')) {
      return image_path
    }
    const baseURL = 'http://127.0.0.1:8000'
    const path = image_path.startsWith('/') ? image_path : `/${image_path}`
    return `${baseURL}/media${path}`
  }

  // 图片加载错误兜底：切换为占位图
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const img = e.currentTarget
    img.src = 'https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=medicine%20pill%20bottle&image_size=square'
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-lg mb-2">加载失败</div>
          <div className="text-gray-600 mb-4">{error}</div>
          <button
            onClick={() => fetchMedicines(filters)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            重试
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题和操作按钮 */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">药品管理</h1>
            <p className="mt-2 text-gray-600">管理药品信息、库存和有效期</p>
          </div>
          <Link
            to="/medicines/add"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            添加药品
          </Link>
        </div>

        {/* 搜索和筛选区域 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          {/* 搜索框 */}
          <form onSubmit={handleSearch} className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="搜索药品名称或厂商..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              搜索
            </button>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Filter className="w-5 h-5 mr-2" />
              筛选
            </button>
          </form>

          {/* 筛选器 */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">药品类型</label>
                <select
                  value={filters.type || ''}
                  onChange={(e) => handleFilterChange('type', e.target.value ?? undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">全部类型</option>
                  <option value={MedicineType.PRESCRIPTION}>处方药</option>
                  <option value={MedicineType.OTC}>非处方药</option>
                  <option value={MedicineType.SUPPLEMENT}>保健品</option>
                  <option value={MedicineType.HERBAL}>中药</option>
                </select>
              </div>

              {/* 删除了剂型筛选块，以避免无效筛选参数导致的后端不兼容 */}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">状态</label>
                <select
                  value={filters.is_expired ? 'expired' : filters.is_low_stock ? 'low_stock' : ''}
                  onChange={(e) => {
                    if (e.target.value === 'expired') {
                      handleFilterChange('is_expired', true)
                      handleFilterChange('is_low_stock', undefined)
                    } else if (e.target.value === 'low_stock') {
                      handleFilterChange('is_low_stock', true)
                      handleFilterChange('is_expired', undefined)
                    } else {
                      handleFilterChange('is_expired', undefined)
                      handleFilterChange('is_low_stock', undefined)
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">全部状态</option>
                  <option value="expired">已过期</option>
                  <option value="low_stock">库存不足</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  清除筛选
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 药品列表 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">加载中...</span>
            </div>
          ) : medicines.length === 0 ? (
            <div className="text-center py-12">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">暂无药品</h3>
              <p className="mt-1 text-sm text-gray-500">开始添加您的第一个药品吧</p>
              <div className="mt-6">
                <Link
                  to="/medicines/add"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  添加药品
                </Link>
              </div>
            </div>
          ) : (
            <>
              {/* 表格头部 */}
              <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
                <div className="grid grid-cols-12 gap-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <div className="col-span-3">药品信息</div>
                  <div className="col-span-2">类型/剂型</div>
                  <div className="col-span-2">库存/单位</div>
                  <div className="col-span-2">有效期</div>
                  <div className="col-span-2">状态</div>
                  <div className="col-span-1">操作</div>
                </div>
              </div>

              {/* 表格内容 */}
              <div className="divide-y divide-gray-200">
                {medicines.map((medicine) => (
                  <div key={medicine.id} className="px-6 py-4 hover:bg-gray-50">
                    <div className="grid grid-cols-12 gap-4 items-center">
                      {/* 药品信息 */}
                      <div className="col-span-3">
                        <div className="flex items-center">
                          {medicine.image_path ? (
                            <img
                              src={getImageUrl(medicine.image_path) ?? undefined}
                              alt={medicine.name}
                              className="h-10 w-10 rounded-lg object-cover mr-3"
                              onError={handleImageError}
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-lg bg-gray-200 flex items-center justify-center mr-3">
                              <Package className="h-5 w-5 text-gray-400" />
                            </div>
                          )}
                          <div>
                            <div className="text-sm font-medium text-gray-900">{medicine.name}</div>
                            {medicine.specification && (
                              <div className="text-sm text-gray-500">{medicine.specification}</div>
                            )}
                            {medicine.manufacturer && (
                              <div className="text-xs text-gray-400">{medicine.manufacturer}</div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* 类型/剂型 */}
                      <div className="col-span-2">
                        <div className="text-sm text-gray-900">
                          {renderTypeLabel((medicine as any).medicine_type)}
                        </div>
                        <div className="text-sm text-gray-500">—</div>
                      </div>

                      {/* 库存/单位 */}
                      <div className="col-span-2">
                        <div className="text-sm text-gray-900">
                          {medicine.quantity}
                        </div>
                      </div>

                      {/* 有效期 */}
                      <div className="col-span-2">
                        {medicine.expiry_date ? (
                          <div className="text-sm text-gray-900">
                            {new Date(medicine.expiry_date).toLocaleDateString('zh-CN')}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">未设置</div>
                        )}
                      </div>

                      {/* 状态 */}
                      <div className="col-span-2">
                        <div className="flex flex-wrap gap-1">
                          {getStatusBadges(medicine)}
                        </div>
                      </div>

                      {/* 操作 */}
                      <div className="col-span-1">
                        <div className="flex items-center space-x-2">
                          <Link
                            to={`/medicines/${medicine.id}/edit`}
                            className="text-blue-600 hover:text-blue-900"
                            title="编辑"
                          >
                            <Edit className="h-4 w-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(medicine.id, medicine.name)}
                            className="text-red-600 hover:text-red-900"
                            title="删除"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 分页 */}
              {pagination && (pagination as any).total_pages > 1 && (
                <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-700">
                      显示第 {(((pagination as any).current_page - 1) * (pagination as any).page_size) + 1} - {Math.min((pagination as any).current_page * (pagination as any).page_size, (pagination as any).count)} 条，
                      共 {(pagination as any).count} 条记录
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handlePageChange((pagination as any).current_page - 1)}
                        disabled={(pagination as any).current_page <= 1}
                        className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                      >
                        上一页
                      </button>
                      <span className="text-sm text-gray-700">
                        第 {(pagination as any).current_page} / {(pagination as any).total_pages} 页
                      </span>
                      <button
                        onClick={() => handlePageChange((pagination as any).current_page + 1)}
                        disabled={(pagination as any).current_page >= (pagination as any).total_pages}
                        className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                      >
                        下一页
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}