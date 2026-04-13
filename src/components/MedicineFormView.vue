<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div
      class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
    >
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"></div>

      <div
        class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg"
      >
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">
            {{ medicine ? '编辑药品' : '添加药品' }}
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <X class="w-6 h-6" />
          </button>
        </div>

        <form @submit.prevent="$emit('submit')" class="space-y-6">
          <div
            v-if="
              assistiveSummaryLines.length ||
              assistiveMissingFields.length ||
              validationPriorityLines.length
            "
            class="rounded-lg border border-blue-200 bg-blue-50 px-4 py-4"
          >
            <h4 class="text-base font-semibold text-blue-900">辅助填写提示</h4>
            <p class="mt-2 text-sm text-blue-800">
              系统会先帮你整理药品信息，你只需要重点确认名称、类型和库存数量。
            </p>
            <p v-if="assistiveSummaryLines.length" class="mt-3 text-sm text-blue-900">
              已识别内容：{{ assistiveSummaryLines.join('；') }}
            </p>
            <p
              v-for="line in validationPriorityLines"
              :key="line"
              class="mt-2 text-sm font-medium text-red-700"
            >
              {{ line }}
            </p>
            <p
              v-if="assistiveMissingFields.length"
              class="mt-2 text-sm font-medium text-amber-700"
            >
              还需要确认：{{ assistiveMissingFields.join('、') }}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.name }"
                data-field="name"
                placeholder="请输入药品名称"
                @focus="$emit('focusField', 'name')"
                @blur="$emit('blurField', 'name')"
              />
              <p v-if="errors.name" class="mt-1 text-sm text-red-600">
                {{ errors.name }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品规格
              </label>
              <input
                v-model="formData.specification"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="如：100mg*30片"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                生产厂商
              </label>
              <input
                v-model="formData.manufacturer"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入生产厂商"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品类型 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="formData.medicine_type"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.medicine_type }"
                data-field="medicine_type"
                @focus="$emit('focusField', 'medicine_type')"
                @blur="$emit('blurField', 'medicine_type')"
              >
                <option value="">请选择药品类型</option>
                <option value="tablet">片剂</option>
                <option value="capsule">胶囊</option>
                <option value="liquid">液体</option>
                <option value="injection">注射剂</option>
                <option value="ointment">软膏</option>
                <option value="drops">滴剂</option>
                <option value="other">其他</option>
              </select>
              <p v-if="errors.medicine_type" class="mt-1 text-sm text-red-600">
                {{ errors.medicine_type }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                库存数量 <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="formData.quantity"
                type="number"
                min="0"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.quantity }"
                data-field="quantity"
                placeholder="请输入库存数量"
                @focus="$emit('focusField', 'quantity')"
                @blur="$emit('blurField', 'quantity')"
              />
              <p v-if="errors.quantity" class="mt-1 text-sm text-red-600">
                {{ errors.quantity }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品分类
              </label>
              <div class="flex items-center space-x-4">
                <label class="flex items-center">
                  <input
                    v-model="formData.is_prescription"
                    type="radio"
                    :value="true"
                    class="mr-2 text-blue-600 focus:ring-blue-500"
                  />
                  处方药
                </label>
                <label class="flex items-center">
                  <input
                    v-model="formData.is_prescription"
                    type="radio"
                    :value="false"
                    class="mr-2 text-blue-600 focus:ring-blue-500"
                  />
                  非处方药
                </label>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                有效期
              </label>
              <input
                v-model="formData.expiry_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                采购日期
              </label>
              <input
                v-model="formData.purchase_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                采购价格
              </label>
              <input
                v-model.number="formData.purchase_price"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.purchase_price }"
                data-field="purchase_price"
                placeholder="请输入采购价格"
              />
              <p v-if="errors.purchase_price" class="mt-1 text-sm text-red-600">
                {{ errors.purchase_price }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                批号
              </label>
              <input
                v-model="formData.batch_number"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入批号"
              />
            </div>
          </div>

          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                存储条件
              </label>
              <input
                v-model="formData.storage_conditions"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="如：阴凉干燥处保存，温度不超过25℃"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品图片
              </label>
              <div class="flex items-center space-x-4">
                <button
                  type="button"
                  @click="$emit('uploadImage')"
                  class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
                >
                  <Upload class="w-4 h-4 mr-2" />
                  上传图片
                </button>
                <span v-if="formData.image_path" class="text-sm text-gray-600">
                  已选择图片
                </span>
              </div>
              <div v-if="formData.image_path" class="mt-2">
                <img
                  :src="imagePreviewUrl"
                  alt="药品图片预览"
                  class="w-20 h-20 object-cover rounded-lg border border-gray-200"
                  @error="$emit('imageError')"
                />
                <button
                  type="button"
                  @click="$emit('removeImage')"
                  class="mt-1 text-sm text-red-600 hover:text-red-800"
                >
                  删除图片
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品描述
              </label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入药品描述、用法用量等信息"
              ></textarea>
            </div>

            <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
              <button
                type="button"
                @click="$emit('close')"
                class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                <span
                  v-if="loading"
                  class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
                ></span>
                {{ loading ? '保存中...' : medicine ? '更新药品' : '添加药品' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from 'vue'
import { X, Upload } from 'lucide-vue-next'
import type { Medicine, MedicineCreateData } from '@/types/medicine'

interface Props {
  visible: boolean
  medicine?: Medicine | null
  formData: MedicineCreateData
  errors: Record<string, string>
  loading: boolean
  imagePreviewUrl: string
  assistiveSummaryLines: string[]
  assistiveMissingFields: string[]
  validationPriorityLines: string[]
}

const props = withDefaults(defineProps<Props>(), {
  medicine: null,
})

defineEmits<{
  close: []
  submit: []
  uploadImage: []
  removeImage: []
  imageError: []
  focusField: [field: string]
  blurField: [field: string]
}>()

const {
  visible,
  medicine,
  formData,
  errors,
  loading,
  imagePreviewUrl,
  validationPriorityLines,
} = toRefs(props)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.border-red-500 {
  border-color: #ef4444;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
