<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">
                {{ isEdit ? '编辑病历' : '新增病历' }}
              </h1>
              <p class="mt-1 text-sm text-gray-500">
                {{ isEdit ? '修改病历记录信息' : '添加新的病历记录' }}
              </p>
            </div>
            <button
              @click="$router.back()"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowLeft class="-ml-1 mr-2 h-4 w-4" />
              返回
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <form @submit.prevent="handleSubmit" class="space-y-8">
        <!-- 基本信息 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">基本信息</h3>
          </div>
          <div class="px-6 py-6 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 就诊日期 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  就诊日期 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.visit_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  :class="{ 'border-red-500': errors.visit_date }"
                >
                <p v-if="errors.visit_date" class="mt-1 text-sm text-red-600">{{ errors.visit_date }}</p>
              </div>

              <!-- 就诊时间 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  就诊时间
                </label>
                <input
                  v-model="form.visit_time"
                  type="time"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 医院名称 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医院名称 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.hospital"
                  type="text"
                  required
                  placeholder="请输入医院名称"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  :class="{ 'border-red-500': errors.hospital }"
                >
                <p v-if="errors.hospital" class="mt-1 text-sm text-red-600">{{ errors.hospital }}</p>
              </div>

              <!-- 医院地址 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医院地址
                </label>
                <input
                  v-model="form.hospital_address"
                  type="text"
                  placeholder="请输入医院地址"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 科室 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  科室
                </label>
                <input
                  v-model="form.department"
                  type="text"
                  placeholder="请输入科室名称"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>

              <!-- 医生姓名 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医生姓名
                </label>
                <input
                  v-model="form.doctor"
                  type="text"
                  placeholder="请输入医生姓名"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 医生职称 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医生职称
                </label>
                <input
                  v-model="form.doctor_title"
                  type="text"
                  placeholder="如：主任医师、副主任医师等"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>

              <!-- 就诊类型 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  就诊类型 <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.visit_type"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  :class="{ 'border-red-500': errors.visit_type }"
                >
                  <option value="">请选择就诊类型</option>
                  <option v-for="option in VISIT_TYPE_OPTIONS" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="errors.visit_type" class="mt-1 text-sm text-red-600">{{ errors.visit_type }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 症状和诊断 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">症状和诊断</h3>
          </div>
          <div class="px-6 py-6 space-y-6">
            <!-- 主诉 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                主诉
              </label>
              <textarea
                v-model="form.chief_complaint"
                rows="3"
                placeholder="请描述主要症状和不适"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- 现病史 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                现病史
              </label>
              <textarea
                v-model="form.present_illness"
                rows="3"
                placeholder="请描述当前疾病的发展过程"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 诊断结果 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  诊断结果
                </label>
                <textarea
                  v-model="form.diagnosis"
                  rows="3"
                  placeholder="请输入医生的诊断结果"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>

              <!-- 诊断代码 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  诊断代码（ICD-10）
                </label>
                <input
                  v-model="form.diagnosis_code"
                  type="text"
                  placeholder="请输入ICD-10诊断代码"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>
            </div>

            <!-- 治疗方案 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                治疗方案
              </label>
              <textarea
                v-model="form.treatment"
                rows="3"
                placeholder="请描述医生制定的治疗方案"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 处方药品 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">处方药品</h3>
              <button
                type="button"
                @click="addMedicine"
                class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
              >
                <Plus class="-ml-1 mr-1 h-4 w-4" />
                添加药品
              </button>
            </div>
          </div>
          <div class="px-6 py-6">
            <div v-if="form.prescribed_medicines.length === 0" class="text-center py-8 text-gray-500">
              暂无处方药品，点击上方按钮添加
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="(medicine, index) in form.prescribed_medicines"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-start justify-between mb-4">
                  <h4 class="text-sm font-medium text-gray-900">药品 {{ index + 1 }}</h4>
                  <button
                    type="button"
                    @click="removeMedicine(index)"
                    class="text-red-600 hover:text-red-800"
                  >
                    <X class="h-4 w-4" />
                  </button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      药品名称 <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="medicine.name"
                      type="text"
                      required
                      placeholder="请输入药品名称"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      用法用量
                    </label>
                    <input
                      v-model="medicine.dosage"
                      type="text"
                      placeholder="如：每次1片"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      服用频次
                    </label>
                    <input
                      v-model="medicine.frequency"
                      type="text"
                      placeholder="如：每日3次"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      服用时长
                    </label>
                    <input
                      v-model="medicine.duration"
                      type="text"
                      placeholder="如：7天"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                </div>
                <div class="mt-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    用药说明
                  </label>
                  <textarea
                    v-model="medicine.instructions"
                    rows="2"
                    placeholder="请输入用药注意事项和说明"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 检查项目 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">检查项目</h3>
              <button
                type="button"
                @click="addExamination"
                class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
              >
                <Plus class="-ml-1 mr-1 h-4 w-4" />
                添加检查
              </button>
            </div>
          </div>
          <div class="px-6 py-6">
            <div v-if="form.examinations.length === 0" class="text-center py-8 text-gray-500">
              暂无检查项目，点击上方按钮添加
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="(exam, index) in form.examinations"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-start justify-between mb-4">
                  <h4 class="text-sm font-medium text-gray-900">检查 {{ index + 1 }}</h4>
                  <button
                    type="button"
                    @click="removeExamination(index)"
                    class="text-red-600 hover:text-red-800"
                  >
                    <X class="h-4 w-4" />
                  </button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      检查项目 <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="exam.name"
                      type="text"
                      required
                      placeholder="请输入检查项目名称"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      检查类型
                    </label>
                    <input
                      v-model="exam.type"
                      type="text"
                      placeholder="如：血常规、X光等"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 费用信息 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">费用信息</h3>
          </div>
          <div class="px-6 py-6 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- 总费用 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  总费用（元）
                </label>
                <input
                  v-model.number="form.total_cost"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>

              <!-- 医保报销 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医保报销（元）
                </label>
                <input
                  v-model.number="form.insurance_coverage"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>

              <!-- 自费金额 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  自费金额（元）
                </label>
                <input
                  v-model.number="form.self_pay_amount"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 复诊和评分 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">复诊和评分</h3>
          </div>
          <div class="px-6 py-6 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 复诊日期 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  复诊日期
                </label>
                <input
                  v-model="form.follow_up_date"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
              </div>

              <!-- 满意度评分 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  满意度评分（1-5分）
                </label>
                <select
                  v-model.number="form.satisfaction_score"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">请选择评分</option>
                  <option :value="1">1分 - 很不满意</option>
                  <option :value="2">2分 - 不满意</option>
                  <option :value="3">3分 - 一般</option>
                  <option :value="4">4分 - 满意</option>
                  <option :value="5">5分 - 很满意</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 症状评分（就诊前） -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  就诊前症状评分（1-10分）
                </label>
                <select
                  v-model.number="form.symptom_score_before"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">请选择评分</option>
                  <option v-for="score in 10" :key="score" :value="score">
                    {{ score }}分
                  </option>
                </select>
              </div>

              <!-- 症状评分（就诊后） -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  就诊后症状评分（1-10分）
                </label>
                <select
                  v-model.number="form.symptom_score_after"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">请选择评分</option>
                  <option v-for="score in 10" :key="score" :value="score">
                    {{ score }}分
                  </option>
                </select>
              </div>
            </div>

            <!-- 复诊说明 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                复诊说明
              </label>
              <textarea
                v-model="form.follow_up_notes"
                rows="3"
                placeholder="请输入复诊相关说明"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 其他信息 -->
        <div class="bg-white shadow-sm rounded-lg border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">其他信息</h3>
          </div>
          <div class="px-6 py-6 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- 就医状态 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  就医状态 <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.status"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  :class="{ 'border-red-500': errors.status }"
                >
                  <option value="">请选择状态</option>
                  <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="errors.status" class="mt-1 text-sm text-red-600">{{ errors.status }}</p>
              </div>

              <!-- 紧急程度 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  紧急程度 <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="form.urgency"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  :class="{ 'border-red-500': errors.urgency }"
                >
                  <option value="">请选择程度</option>
                  <option v-for="option in URGENCY_OPTIONS" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="errors.urgency" class="mt-1 text-sm text-red-600">{{ errors.urgency }}</p>
              </div>
            </div>

            <!-- 检查结果 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                检查结果
              </label>
              <textarea
                v-model="form.examination_results"
                rows="3"
                placeholder="请输入各项检查的结果"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- 医嘱 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                医嘱
              </label>
              <textarea
                v-model="form.medical_orders"
                rows="3"
                placeholder="请输入医生的医嘱和建议"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- 备注 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                备注
              </label>
              <textarea
                v-model="form.notes"
                rows="3"
                placeholder="请输入其他备注信息"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="flex justify-end space-x-4">
          <button
            type="button"
            @click="$router.back()"
            class="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isEdit ? '更新中...' : '保存中...' }}
            </span>
            <span v-else>
              {{ isEdit ? '更新病历' : '保存病历' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMedicalRecordStore } from '@/stores/medicalRecords'
import {
  ArrowLeft,
  Plus,
  X
} from 'lucide-vue-next'
import {
  VISIT_TYPE_OPTIONS,
  STATUS_OPTIONS,
  URGENCY_OPTIONS,
  type MedicalRecordCreate,
  type MedicalRecordUpdate,
  type PrescribedMedicine,
  type Examination
} from '@/types/medicalRecord'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const medicalRecordStore = useMedicalRecordStore()

// 响应式数据
const loading = ref(false)
const errors = ref<Record<string, string>>({})

// 计算属性
const isEdit = computed(() => !!route.params.id)
const recordId = computed(() => route.params.id ? Number(route.params.id) : null)

// 表单数据
const form = reactive<MedicalRecordCreate>({
  visit_date: '',
  visit_time: '',
  hospital: '',
  hospital_address: '',
  department: '',
  doctor: '',
  doctor_title: '',
  visit_type: 'outpatient',
  chief_complaint: '',
  present_illness: '',
  diagnosis: '',
  diagnosis_code: '',
  treatment: '',
  prescribed_medicines: [],
  examinations: [],
  examination_results: '',
  lab_results: {},
  medical_orders: '',
  notes: '',
  total_cost: undefined,
  insurance_coverage: undefined,
  self_pay_amount: undefined,
  follow_up_date: '',
  follow_up_notes: '',
  symptom_score_before: undefined,
  symptom_score_after: undefined,
  satisfaction_score: undefined,
  status: 'completed',
  urgency: 'routine',
  attachments: []
})

// 方法
const addMedicine = () => {
  form.prescribed_medicines.push({
    name: '',
    dosage: '',
    frequency: '',
    duration: '',
    instructions: ''
  })
}

const removeMedicine = (index: number) => {
  form.prescribed_medicines.splice(index, 1)
}

const addExamination = () => {
  form.examinations.push({
    name: '',
    type: ''
  })
}

const removeExamination = (index: number) => {
  form.examinations.splice(index, 1)
}

const validateForm = (): boolean => {
  errors.value = {}
  
  if (!form.visit_date) {
    errors.value.visit_date = '请选择就诊日期'
  }
  
  if (!form.hospital) {
    errors.value.hospital = '请输入医院名称'
  }
  
  if (!form.visit_type) {
    errors.value.visit_type = '请选择就诊类型'
  }
  
  if (!form.status) {
    errors.value.status = '请选择就医状态'
  }
  
  if (!form.urgency) {
    errors.value.urgency = '请选择紧急程度'
  }
  
  // 验证处方药品
  for (let i = 0; i < form.prescribed_medicines.length; i++) {
    if (!form.prescribed_medicines[i].name) {
      errors.value[`medicine_${i}_name`] = '请输入药品名称'
    }
  }
  
  // 验证检查项目
  for (let i = 0; i < form.examinations.length; i++) {
    if (!form.examinations[i].name) {
      errors.value[`exam_${i}_name`] = '请输入检查项目名称'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    toast.error('请检查表单填写是否完整')
    return
  }
  
  try {
    loading.value = true
    
    if (isEdit.value && recordId.value) {
      // 更新病历
      await medicalRecordStore.updateRecord(recordId.value, form as MedicalRecordUpdate)
      toast.success('病历更新成功')
    } else {
      // 创建病历
      await medicalRecordStore.createRecord(form)
      toast.success('病历创建成功')
    }
    
    router.push('/medical-records')
  } catch (error: any) {
    console.error('保存病历失败:', error)
    toast.error(error.message || '保存失败，请重试')
  } finally {
    loading.value = false
  }
}

const loadRecord = async () => {
  if (!recordId.value) return
  
  try {
    loading.value = true
    const record = await medicalRecordStore.fetchRecord(recordId.value)
    
    // 填充表单数据
    Object.assign(form, {
      visit_date: record.visit_date,
      visit_time: record.visit_time || '',
      hospital: record.hospital,
      hospital_address: record.hospital_address || '',
      department: record.department || '',
      doctor: record.doctor || '',
      doctor_title: record.doctor_title || '',
      visit_type: record.visit_type,
      chief_complaint: record.chief_complaint || '',
      present_illness: record.present_illness || '',
      diagnosis: record.diagnosis || '',
      diagnosis_code: record.diagnosis_code || '',
      treatment: record.treatment || '',
      prescribed_medicines: record.prescribed_medicines || [],
      examinations: record.examinations || [],
      examination_results: record.examination_results || '',
      lab_results: record.lab_results || {},
      medical_orders: record.medical_orders || '',
      notes: record.notes || '',
      total_cost: record.total_cost,
      insurance_coverage: record.insurance_coverage,
      self_pay_amount: record.self_pay_amount,
      follow_up_date: record.follow_up_date || '',
      follow_up_notes: record.follow_up_notes || '',
      symptom_score_before: record.symptom_score_before,
      symptom_score_after: record.symptom_score_after,
      satisfaction_score: record.satisfaction_score,
      status: record.status,
      urgency: record.urgency,
      attachments: record.attachments || []
    })
  } catch (error: any) {
    console.error('加载病历失败:', error)
    toast.error('加载病历失败，请重试')
    router.push('/medical-records')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  if (isEdit.value) {
    loadRecord()
  }
})
</script>