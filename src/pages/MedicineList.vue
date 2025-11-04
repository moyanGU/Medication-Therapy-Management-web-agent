<template>
  <div class="medicine-list-page">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">药品管理</h1>
        <p class="page-subtitle">管理药品信息，监控库存状态</p>
      </div>
      <div class="header-right">
        <button 
          @click="showAddDialog = true"
          class="btn-primary"
        >
          <Plus class="w-4 h-4 mr-2" />
          添加药品
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon bg-blue-100">
          <Package class="w-6 h-6 text-blue-600" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_medicines }}</div>
          <div class="stat-label">总药品数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-red-100">
          <AlertTriangle class="w-6 h-6 text-red-600" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.expired_count }}</div>
          <div class="stat-label">已过期</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-yellow-100">
          <Clock class="w-6 h-6 text-yellow-600" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.expiring_soon_count }}</div>
          <div class="stat-label">即将过期</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-orange-100">
          <TrendingDown class="w-6 h-6 text-orange-600" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.low_stock_count }}</div>
          <div class="stat-label">库存不足</div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filter-section">
      <div class="search-box">
        <Search class="w-5 h-5 text-gray-400" />
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="搜索药品名称、规格、厂商..."
          class="search-input"
        />
      </div>
      <div class="filter-controls">
        <select v-model="filters.dosage_form" @change="handleFilter" class="filter-select">
          <option value="">所有剂型</option>
          <option value="tablet">片剂</option>
          <option value="capsule">胶囊</option>
          <option value="liquid">液体</option>
          <option value="injection">注射剂</option>
          <option value="ointment">软膏</option>
          <option value="drops">滴剂</option>
          <option value="other">其他</option>
        </select>
        <select v-model="filters.prescription_required" @change="handleFilter" class="filter-select">
          <option value="">所有药品</option>
          <option value="true">处方药</option>
          <option value="false">非处方药</option>
        </select>
        <select v-model="filters.status" @change="handleFilter" class="filter-select">
          <option value="">所有状态</option>
          <option value="expired">已过期</option>
          <option value="low_stock">库存不足</option>
        </select>
        <select v-model="sortBy" @change="handleSort" class="filter-select">
          <option value="-created_at">最新添加</option>
          <option value="name">名称升序</option>
          <option value="-name">名称降序</option>
          <option value="expiry_date">过期日期升序</option>
          <option value="-expiry_date">过期日期降序</option>
          <option value="quantity">库存升序</option>
          <option value="-quantity">库存降序</option>
        </select>
      </div>
    </div>

    <!-- 药品列表 -->
    <div class="medicine-list">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="medicines.length === 0" class="empty-state">
        <Package class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">暂无药品</h3>
        <p class="text-gray-500 mb-4">开始添加您的第一个药品吧</p>
        <button @click="showAddDialog = true" class="btn-primary">
          添加药品
        </button>
      </div>

      <div v-else class="medicine-grid">
        <div 
          v-for="medicine in medicines" 
          :key="medicine.id" 
          class="medicine-card"
          :class="{
            'expired': medicine.is_expired,
            'low-stock': medicine.is_low_stock
          }"
        >
          <!-- 药品图片 -->
          <div class="medicine-image">
            <img 
              v-if="medicine.image_path" 
              :src="getImageUrl(medicine.image_path)" 
              :alt="medicine.name"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <div v-else class="image-placeholder">
              <Package class="w-8 h-8 text-gray-400" />
            </div>
          </div>

          <!-- 药品信息 -->
          <div class="medicine-info">
            <div class="medicine-header">
              <h3 class="medicine-name">{{ medicine.name }}</h3>
              <div class="medicine-badges">
                <span v-if="medicine.is_prescription" class="badge badge-prescription">
                  处方药
                </span>
                <span v-if="medicine.is_expired" class="badge badge-expired">
                  已过期
                </span>
                <span v-else-if="medicine.days_until_expiry !== undefined && medicine.days_until_expiry <= 30" class="badge badge-expiring">
                  {{ medicine.days_until_expiry }}天后过期
                </span>
                <span v-if="medicine.is_low_stock" class="badge badge-low-stock">
                  库存不足
                </span>
              </div>
            </div>
            
            <div class="medicine-details">
              <p v-if="medicine.specification" class="detail-item">
                <span class="detail-label">规格:</span>
                <span class="detail-value">{{ medicine.specification }}</span>
              </p>
              <p v-if="medicine.manufacturer" class="detail-item">
                <span class="detail-label">厂商:</span>
                <span class="detail-value">{{ medicine.manufacturer }}</span>
              </p>
              <p class="detail-item">
                <span class="detail-label">库存:</span>
                <span class="detail-value">{{ medicine.quantity }}</span>
              </p>
              <p v-if="medicine.expiry_date" class="detail-item">
                <span class="detail-label">有效期:</span>
                <span class="detail-value">{{ formatDate(medicine.expiry_date) }}</span>
              </p>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="medicine-actions">
            <button 
              @click="viewMedicine(medicine)"
              class="action-btn action-btn-view"
              title="查看详情"
            >
              <Eye class="w-4 h-4" />
            </button>
            <button 
              @click="editMedicine(medicine)"
              class="action-btn action-btn-edit"
              title="编辑"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button 
              @click="showQuantityDialog(medicine)"
              class="action-btn action-btn-quantity"
              title="调整库存"
            >
              <Package class="w-4 h-4" />
            </button>
            <button 
              @click="deleteMedicine(medicine)"
              class="action-btn action-btn-delete"
              title="删除"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > 0" class="pagination">
      <button 
        @click="changePage(pagination.current - 1)"
        :disabled="pagination.current <= 1"
        class="pagination-btn"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      
      <span class="pagination-info">
        第 {{ pagination.current }} 页，共 {{ pagination.totalPages }} 页
      </span>
      
      <button 
        @click="changePage(pagination.current + 1)"
        :disabled="pagination.current >= pagination.totalPages"
        class="pagination-btn"
      >
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>

    <!-- 添加/编辑药品对话框 -->
    <MedicineForm
      v-if="showAddDialog || showEditDialog"
      :visible="showAddDialog || showEditDialog"
      :medicine="editingMedicine"
      @close="closeDialog"
      @success="handleFormSuccess"
    />

    <!-- 库存调整对话框 -->
    <QuantityDialog
      v-if="showQuantityDialogVisible"
      :visible="showQuantityDialogVisible"
      :medicine="selectedMedicine"
      @close="showQuantityDialogVisible = false"
      @success="handleQuantityUpdate"
    />

    <!-- 药品详情对话框 -->
    <MedicineDetail
      v-if="showDetailDialog"
      :visible="showDetailDialog"
      :medicine="selectedMedicine"
      @close="showDetailDialog = false"
      @edit="editMedicine"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useMedicineStore } from '@/stores/medicine'
import type { Medicine, MedicineListParams } from '@/types/medicine'
import { 
  Plus, Package, AlertTriangle, Clock, TrendingDown, 
  Search, Eye, Edit, Trash2, ChevronLeft, ChevronRight 
} from 'lucide-vue-next'
import MedicineForm from '@/components/MedicineForm.vue'
import MedicineDetail from '@/components/MedicineDetail.vue'
import QuantityDialog from '@/components/QuantityDialog.vue'
import { getBackendOrigin } from '@/utils/api'

// Store
const medicineStore = useMedicineStore()

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref('-created_at')
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const showQuantityDialogVisible = ref(false)
const editingMedicine = ref<Medicine | null>(null)
const selectedMedicine = ref<Medicine | null>(null)

// 筛选条件
const filters = reactive({
  dosage_form: '',
  prescription_required: '',
  status: ''
})

// 计算属性
const medicines = computed(() => medicineStore.medicines)
const statistics = computed(() => medicineStore.statistics)
const pagination = computed(() => medicineStore.pagination)

// 方法
const loadMedicines = async () => {
  loading.value = true
  try {
    const params: MedicineListParams = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize,
      ordering: sortBy.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    if (filters.dosage_form) {
      params.dosage_form = filters.dosage_form as any
    }

    if (filters.prescription_required) {
      params.prescription_required = filters.prescription_required === 'true'
    }

    if (filters.status === 'expired') {
      params.is_expired = true
    } else if (filters.status === 'low_stock') {
      params.is_low_stock = true
    }

    await medicineStore.fetchMedicines(params)
  } catch (error) {
    console.error('加载药品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    await medicineStore.fetchStatistics()
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const handleSearch = () => {
  loadMedicines()
}

const handleFilter = () => {
  loadMedicines()
}

const handleSort = () => {
  loadMedicines()
}

const changePage = (page: number) => {
  medicineStore.pagination.current = page
  loadMedicines()
}

const viewMedicine = (medicine: Medicine) => {
  selectedMedicine.value = medicine
  showDetailDialog.value = true
}

const editMedicine = (medicine: Medicine) => {
  editingMedicine.value = medicine
  showEditDialog.value = true
}

const showQuantityDialog = (medicine: Medicine) => {
  console.log('🟡 [MedicineList] 打开库存调整对话框: ', medicine?.id, medicine?.name)
  selectedMedicine.value = medicine
  showQuantityDialogVisible.value = true
}

const deleteMedicine = async (medicine: Medicine) => {
  if (confirm(`确定要删除药品 "${medicine.name}" 吗？`)) {
    try {
      await medicineStore.deleteMedicine(medicine.id)
      await loadMedicines()
      await loadStatistics()
    } catch (error) {
      console.error('删除药品失败:', error)
    }
  }
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  editingMedicine.value = null
}

const handleFormSuccess = async () => {
  closeDialog()
  await loadMedicines()
  await loadStatistics()
}

const handleQuantityUpdate = async () => {
  showQuantityDialogVisible.value = false
  await loadMedicines()
  await loadStatistics()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

/**
 * 根据后端返回的 image_path 构建完整的图片 URL
 * - 若为 http/https 绝对地址，直接返回
 * - 否则拼接后端基地址 + /media + 相对路径
 */
const getImageUrl = (imagePath?: string | null) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  const baseURL = getBackendOrigin()
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`
  return `${baseURL}/media${path}`
}

/**
 * 图片加载失败时回退到占位图
 */
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/icons/app-icon.svg'
}

// 生命周期
onMounted(() => {
  loadMedicines()
  loadStatistics()
})
</script>

<style scoped>
.medicine-list-page {
  @apply p-6 max-w-7xl mx-auto;
}

.page-header {
  @apply flex justify-between items-start mb-8;
}

.header-left {
  @apply flex-1;
}

.page-title {
  @apply text-3xl font-bold text-gray-900 mb-2;
}

.page-subtitle {
  @apply text-gray-600;
}

.header-right {
  @apply flex gap-3;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center;
}

.stats-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8;
}

.stat-card {
  @apply bg-white rounded-lg p-6 shadow-sm border border-gray-200 flex items-center;
}

.stat-icon {
  @apply w-12 h-12 rounded-lg flex items-center justify-center mr-4;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.search-filter-section {
  @apply bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-6;
}

.search-box {
  @apply relative mb-4;
}

.search-box svg {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2;
}

.search-input {
  @apply w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.filter-controls {
  @apply flex flex-wrap gap-4;
}

.filter-select {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.medicine-list {
  @apply mb-8;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-12;
}

.loading-spinner {
  @apply w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4;
}

.empty-state {
  @apply text-center py-12;
}

.medicine-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6;
}

.medicine-card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow;
}

.medicine-card.expired {
  @apply border-red-300 bg-red-50;
}

.medicine-card.low-stock {
  @apply border-orange-300 bg-orange-50;
}

.medicine-image {
  @apply h-48 bg-gray-100 flex items-center justify-center;
}

.image-placeholder {
  @apply flex items-center justify-center w-full h-full;
}

.medicine-info {
  @apply p-4;
}

.medicine-header {
  @apply mb-3;
}

.medicine-name {
  @apply text-lg font-semibold text-gray-900 mb-2;
}

.medicine-badges {
  @apply flex flex-wrap gap-2;
}

.badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;
}

.badge-prescription {
  @apply bg-purple-100 text-purple-800;
}

.badge-expired {
  @apply bg-red-100 text-red-800;
}

.badge-expiring {
  @apply bg-yellow-100 text-yellow-800;
}

.badge-low-stock {
  @apply bg-orange-100 text-orange-800;
}

.medicine-details {
  @apply space-y-1;
}

.detail-item {
  @apply text-sm;
}

.detail-label {
  @apply text-gray-600;
}

.detail-value {
  @apply text-gray-900 font-medium;
}

.medicine-actions {
  @apply flex justify-end gap-2 p-4 pt-0;
}

.action-btn {
  @apply p-2 rounded-lg transition-colors;
}

.action-btn-view {
  @apply text-blue-600 hover:bg-blue-100;
}

.action-btn-edit {
  @apply text-green-600 hover:bg-green-100;
}

.action-btn-quantity {
  @apply text-purple-600 hover:bg-purple-100;
}

.action-btn-delete {
  @apply text-red-600 hover:bg-red-100;
}

.pagination {
  @apply flex items-center justify-center gap-4;
}

.pagination-btn {
  @apply p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed;
}

.pagination-info {
  @apply text-sm text-gray-600;
}
</style>