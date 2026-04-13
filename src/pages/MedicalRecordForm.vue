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
      <div
        v-if="
          assistiveSummaryLines.length ||
          assistiveMissingFields.length ||
          validationPriorityLines.length
        "
        class="mb-6 rounded-lg border border-blue-200 bg-blue-50 px-4 py-4"
      >
        <h3 class="text-base font-semibold text-blue-900">辅助填写提示</h3>
        <p class="mt-2 text-sm text-blue-800">
          系统会先帮你整理就医信息，你只需要重点确认必填项和识别结果。
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
                  data-field="visit_date"
                  @focus="handleFieldFocus('visit_date')"
                  @blur="handleFieldBlur('visit_date')"
                />
                <p v-if="errors.visit_date" class="mt-1 text-sm text-red-600">
                  {{ errors.visit_date }}
                </p>
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
                />
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
                  data-field="hospital"
                  @focus="handleFieldFocus('hospital')"
                  @blur="handleFieldBlur('hospital')"
                />
                <p v-if="errors.hospital" class="mt-1 text-sm text-red-600">
                  {{ errors.hospital }}
                </p>
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
                />
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
                />
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
                />
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
                />
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
                  data-field="visit_type"
                  @focus="handleFieldFocus('visit_type')"
                  @blur="handleFieldBlur('visit_type')"
                >
                  <option value="">请选择就诊类型</option>
                  <option
                    v-for="option in VISIT_TYPE_OPTIONS"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="errors.visit_type" class="mt-1 text-sm text-red-600">
                  {{ errors.visit_type }}
                </p>
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
                />
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
            <div
              v-if="form.prescribed_medicines.length === 0"
              class="text-center py-8 text-gray-500"
            >
              暂无处方药品，点击上方按钮添加
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="(medicine, index) in form.prescribed_medicines"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-start justify-between mb-4">
                  <h4 class="text-sm font-medium text-gray-900">
                    药品 {{ index + 1 }}
                  </h4>
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
                      :class="{ 'border-red-500': errors[`medicine_${index}_name`] }"
                      :data-field="`medicine_${index}_name`"
                      @focus="handleFieldFocus(`prescribed_medicine_name_${index}`)"
                      @blur="handleFieldBlur(`prescribed_medicine_name_${index}`)"
                    />
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
                    />
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
                    />
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
                    />
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
            <div
              v-if="form.examinations.length === 0"
              class="text-center py-8 text-gray-500"
            >
              暂无检查项目，点击上方按钮添加
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="(exam, index) in form.examinations"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-start justify-between mb-4">
                  <h4 class="text-sm font-medium text-gray-900">
                    检查 {{ index + 1 }}
                  </h4>
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
                      :class="{ 'border-red-500': errors[`exam_${index}_name`] }"
                      :data-field="`exam_${index}_name`"
                      @focus="handleFieldFocus(`exam_name_${index}`)"
                      @blur="handleFieldBlur(`exam_name_${index}`)"
                    />
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
                    />
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
                />
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
                />
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
                />
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
                />
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
                  data-field="status"
                  @focus="handleFieldFocus('status')"
                  @blur="handleFieldBlur('status')"
                >
                  <option value="">请选择状态</option>
                  <option
                    v-for="option in STATUS_OPTIONS"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="errors.status" class="mt-1 text-sm text-red-600">
                  {{ errors.status }}
                </p>
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
                  data-field="urgency"
                  @focus="handleFieldFocus('urgency')"
                  @blur="handleFieldBlur('urgency')"
                >
                  <option value="">请选择程度</option>
                  <option
                    v-for="option in URGENCY_OPTIONS"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="errors.urgency" class="mt-1 text-sm text-red-600">
                  {{ errors.urgency }}
                </p>
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
              <svg
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
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
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSpeech } from '@/composables/useSpeech'
import { useMedicalRecordStore } from '@/stores/medicalRecords'
import { isRequestCancelledError } from '@/utils/api'
import { ArrowLeft, Plus, X } from 'lucide-vue-next'
import {
  VISIT_TYPE_OPTIONS,
  STATUS_OPTIONS,
  URGENCY_OPTIONS,
  type MedicalRecordCreate,
  type MedicalRecordUpdate,
} from '@/types/medicalRecord'
import { toast } from 'vue-sonner'
import {
  createSubmissionTraceContext,
  createTraceId,
  extractApiValidationErrors,
  logApiErrorEvent,
  logClientTraceEvent,
} from '@/utils/api'

const route = useRoute()
const router = useRouter()
const medicalRecordStore = useMedicalRecordStore()
const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()

// 响应式数据
const loading = ref(false)
const errors = ref<Record<string, string>>({})
const assistiveSummaryLines = ref<string[]>([])
const lastAppliedDraftSignature = ref('')

// 计算属性
const isEdit = computed(() => !!route.params.id)
const recordId = computed(() =>
  route.params.id ? Number(route.params.id) : null
)
const assistiveMissingFields = computed(() => {
  const missing: string[] = []

  if (!form.visit_date) {
    missing.push('就诊日期')
  }
  if (!form.hospital) {
    missing.push('医院名称')
  }
  if (!form.visit_type) {
    missing.push('就诊类型')
  }
  if (!form.status) {
    missing.push('就医状态')
  }
  if (!form.urgency) {
    missing.push('紧急程度')
  }

  form.prescribed_medicines.forEach((item, index) => {
    if (!item.name?.trim()) {
      missing.push(`处方药品${index + 1}名称`)
    }
  })

  form.examinations.forEach((item, index) => {
    if (!item.name?.trim()) {
      missing.push(`检查项目${index + 1}名称`)
    }
  })

  return missing
})
const assistiveGuidanceEnabled = ref(false)
const lastFieldGuidanceKey = ref('')
const lastAssistiveInteractionAt = ref(0)
const assistiveInteractionTick = ref(0)
const FIELD_GUIDANCE_THROTTLE_KEY = 'medical-record-form-field-guidance'
const CONTINUOUS_INTERACTION_WINDOW_MS = 4000
const IDLE_REMINDER_DELAY_MS = 12000

const assistiveRequiredFieldCount = computed(() => {
  return 5 + form.prescribed_medicines.length + form.examinations.length
})

const buildFieldGuidanceKey = () => assistiveMissingFields.value.join('|') || 'completed'

const formatAssistiveFieldLabel = (field: string) => {
  const prescribedMedicineMatch = field.match(/^处方药品(\d+)名称$/)
  if (prescribedMedicineMatch) {
    return `第${prescribedMedicineMatch[1]}个处方药名称`
  }

  const examinationMatch = field.match(/^检查项目(\d+)名称$/)
  if (examinationMatch) {
    return `第${examinationMatch[1]}个检查项目名称`
  }

  const fieldLabelMap: Record<string, string> = {
    就诊日期: '就诊日期',
    医院名称: '医院名称',
    就诊类型: '就诊类型',
    就医状态: '就医状态',
    紧急程度: '紧急程度',
  }
  return fieldLabelMap[field] || field
}

const buildFinalActionGuidance = () => {
  return '病历表单关键项已经补齐，请检查一遍就诊信息，确认无误后手动提交，不会自动提交。'
}

const markAssistiveInteraction = () => {
  lastAssistiveInteractionAt.value = Date.now()
  assistiveInteractionTick.value += 1
}

const isContinuousInteraction = () => {
  return Date.now() - lastAssistiveInteractionAt.value < CONTINUOUS_INTERACTION_WINDOW_MS
}

const buildFieldCorrectionGuidance = (field: string) => {
  const prescribedMedicineMatch = field.match(/^prescribed_medicine_name_(\d+)$/)
  if (prescribedMedicineMatch) {
    return `第${Number(prescribedMedicineMatch[1]) + 1}个处方药名称还没填好，请再确认。`
  }

  const examinationMatch = field.match(/^exam_name_(\d+)$/)
  if (examinationMatch) {
    return `第${Number(examinationMatch[1]) + 1}个检查项目名称还没填好，请再确认。`
  }

  const messageMap: Record<string, string> = {
    visit_date: '就诊日期还没选好，请再确认。',
    hospital: '医院名称还没填好，请再确认。',
    visit_type: '就诊类型还没选好，请再确认。',
    status: '就医状态还没选好，请再确认。',
    urgency: '紧急程度还没选好，请再确认。',
  }
  return messageMap[field] || '这个字段还没填好，请再确认。'
}

const formatValidationIssueLabel = (field: string) => {
  const prescribedMedicineMatch = field.match(/^medicine_(\d+)_name$/)
  if (prescribedMedicineMatch) {
    return `第${Number(prescribedMedicineMatch[1]) + 1}个处方药名称`
  }

  const examinationMatch = field.match(/^exam_(\d+)_name$/)
  if (examinationMatch) {
    return `第${Number(examinationMatch[1]) + 1}个检查项目名称`
  }

  const labelMap: Record<string, string> = {
    visit_date: '就诊日期',
    hospital: '医院名称',
    visit_type: '就诊类型',
    status: '就医状态',
    urgency: '紧急程度',
    follow_up_date: '复诊日期',
    total_cost: '总费用',
    insurance_coverage: '医保报销',
    self_pay_amount: '自费金额',
    out_of_pocket_cost: '自费金额',
    non_field_errors: '整体内容',
  }
  return labelMap[field] || '填写内容'
}

const normalizeAssistiveValidationMessage = (field: string, message: string) => {
  const normalized = message
    .replace(/^[A-Za-z0-9_]+:\s*/, '')
    .replace('This field is required.', `${formatValidationIssueLabel(field)}还没填。`)
    .replace('This field may not be blank.', `${formatValidationIssueLabel(field)}还没填。`)
    .replace('A valid number is required.', `${formatValidationIssueLabel(field)}需要填写数字。`)
    .trim()

  return normalized || `${formatValidationIssueLabel(field)}还需要再确认。`
}

const getValidationIssueEntries = () =>
  Object.entries(errors.value).filter(([, message]) => Boolean(message))

const getValidationIssueFields = () => getValidationIssueEntries().map(([field]) => field)

const getValidationIssueDescriptions = () =>
  getValidationIssueEntries().map(([field, message]) =>
    normalizeAssistiveValidationMessage(field, message)
  )

const getFirstValidationIssueField = () => getValidationIssueFields()[0]

const validationPriorityLines = computed(() => {
  const issueDescriptions = getValidationIssueDescriptions()
  if (issueDescriptions.length === 0) {
    return []
  }
  if (issueDescriptions.length === 1) {
    return [`请先处理：${issueDescriptions[0]}`]
  }
  return [
    `请先处理：${issueDescriptions[0]}`,
    `然后再检查：${issueDescriptions.slice(1, 2).join('；')}`,
  ]
})

const buildValidationFailureGuidance = () => {
  const issueDescriptions = getValidationIssueDescriptions()
  if (issueDescriptions.length === 0) {
    return '病历表单还不能提交，请先检查关键内容。'
  }
  if (issueDescriptions.length === 1) {
    return `病历表单还不能提交，请先处理：${issueDescriptions[0]}。`
  }
  return `病历表单还不能提交，请先处理：${issueDescriptions[0]}，然后再检查：${issueDescriptions[1]}。`
}

const focusValidationField = async (field?: string) => {
  await nextTick()
  if (field === 'non_field_errors') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  const selector = field ? `[data-field="${field}"]` : '.border-red-500'
  const target =
    document.querySelector<HTMLElement>(selector) ||
    document.querySelector<HTMLElement>('.border-red-500')

  if (!target) {
    return
  }

  target.scrollIntoView({ behavior: 'smooth', block: 'center' })
  target.focus()
}

const applyServerValidationErrors = (
  error: unknown,
  submitSessionId?: string,
  requestId?: string
) => {
  const serverErrors = extractApiValidationErrors(error)
  const mappedEntries = Object.entries(serverErrors)
    .map(([field, message]) => {
      const targetField =
        field === 'out_of_pocket_cost'
          ? 'self_pay_amount'
          : field === 'non_field_errors'
            ? 'non_field_errors'
            : field
      const normalizedMessage = normalizeAssistiveValidationMessage(targetField, message)
      if (!normalizedMessage) {
        return null
      }
      return [targetField, normalizedMessage] as const
    })
    .filter((entry): entry is readonly [string, string] => entry !== null)

  if (mappedEntries.length === 0) {
    return false
  }

  errors.value = Object.fromEntries(mappedEntries)
  logClientTraceEvent(
    'MedicalRecordForm',
    'server_validation_mapped',
    {
      requestId: requestId ?? null,
      submitSessionId: submitSessionId ?? null,
      rawFields: Object.keys(serverErrors),
      mappedFields: Object.keys(errors.value),
      validationErrors: errors.value,
    },
    { severity: 'warn' }
  )
  return true
}

const buildNextFieldGuidance = () => {
  const nextField = assistiveMissingFields.value[0]
  const remainingCount = assistiveMissingFields.value.length

  if (!nextField) {
    return buildFinalActionGuidance()
  }

  const suffix =
    remainingCount > 1 ? ` 之后还需要确认${remainingCount - 1}项。` : ' 这是最后一步，完成后请手动提交。'

  if (/^处方药品\d+名称$/.test(nextField)) {
    return `现在请补充${formatAssistiveFieldLabel(nextField)}。${suffix}`
  }
  if (/^检查项目\d+名称$/.test(nextField)) {
    return `现在请补充${formatAssistiveFieldLabel(nextField)}。${suffix}`
  }

  const fieldMessageMap: Record<string, string> = {
    就诊日期: '请先确认实际就诊日期。',
    医院名称: '请填写本次就诊医院名称。',
    就诊类型: '请确认这次是门诊、急诊还是住院。',
    就医状态: '请确认当前就医状态。',
    紧急程度: '请确认这次就诊的紧急程度。',
  }

  return `${fieldMessageMap[nextField] || `请补充${nextField}。`}${suffix}`
}

const parseMissingFieldsFromKey = (key?: string) => {
  if (!key || key === 'completed') {
    return []
  }
  return key.split('|').filter(Boolean)
}

const parseMissingCountFromKey = (key?: string) => {
  return parseMissingFieldsFromKey(key).length
}

const buildCompletedFieldSummary = (fields: string[]) => {
  if (fields.length === 0) {
    return ''
  }
  const labels = fields.map(formatAssistiveFieldLabel)
  if (fields.length === 1) {
    return `已完成${labels[0]}。`
  }
  if (fields.length === 2) {
    return `已完成${labels[0]}和${labels[1]}。`
  }
  return `已完成${labels.slice(0, -1).join('、')}和${labels[labels.length - 1]}。`
}

const buildProgressGuidance = (previousKey?: string) => {
  const currentMissingCount = assistiveMissingFields.value.length
  const currentCompletedCount =
    assistiveRequiredFieldCount.value - currentMissingCount
  const previousMissingFields = parseMissingFieldsFromKey(previousKey)
  const completedFields = previousMissingFields.filter(
    field => !assistiveMissingFields.value.includes(field)
  )
  const completedFieldSummary = buildCompletedFieldSummary(completedFields)

  if (currentMissingCount === 0) {
    return `${completedFieldSummary}病历表单关键项已全部完成，共${assistiveRequiredFieldCount.value}项。请检查一遍就诊信息，确认无误后手动提交，不会自动提交。`
  }

  const previousMissingCount = parseMissingCountFromKey(previousKey)
  if (previousKey !== undefined && previousMissingCount > currentMissingCount) {
    return `${completedFieldSummary}已完成${currentCompletedCount}/${assistiveRequiredFieldCount.value}项关键内容。${buildNextFieldGuidance()}`
  }

  return buildNextFieldGuidance()
}

const speakFieldGuidance = (
  text: string,
  options?: {
    priority?: 'low' | 'normal' | 'high'
    interrupt?: boolean
    dedupeWindowMs?: number
    throttleWindowMs?: number
  }
) => {
  speak(text, {
    rate: 0.82,
    category: 'assistant',
    priority: options?.priority ?? 'normal',
    interrupt: options?.interrupt ?? false,
    dedupeWindowMs: options?.dedupeWindowMs ?? 1800,
    maxSegmentLength: 32,
    throttleKey: FIELD_GUIDANCE_THROTTLE_KEY,
    throttleWindowMs: options?.throttleWindowMs ?? 900,
  })
}

const activateFieldGuidance = (
  prefix: string,
  mode: 'prefill' | 'validation' = 'prefill',
  customMessage?: string
) => {
  assistiveGuidanceEnabled.value = true
  lastFieldGuidanceKey.value = buildFieldGuidanceKey()
  markAssistiveInteraction()
  if (!isSpeechEnabled.value || !isSpeechSupported.value) {
    return
  }

  speakFieldGuidance(customMessage || `${prefix}${buildNextFieldGuidance()}`, {
    priority: mode === 'validation' ? 'high' : 'normal',
    interrupt: true,
    dedupeWindowMs: 3000,
    throttleWindowMs: mode === 'validation' ? 0 : 900,
  })
}

const getFieldFocusPrompt = (field: string) => {
  const prescribedMedicineMatch = field.match(/^prescribed_medicine_name_(\d+)$/)
  if (prescribedMedicineMatch) {
    return `当前正在填写第${prescribedMedicineMatch[1]}个处方药名称，请写医生开具的药名。`
  }
  const examinationMatch = field.match(/^exam_name_(\d+)$/)
  if (examinationMatch) {
    return `当前正在填写第${examinationMatch[1]}个检查项目名称，请写具体检查项目。`
  }

  const promptMap: Record<string, string> = {
    visit_date: '当前是就诊日期，请确认实际就诊的日期。',
    hospital: '当前是医院名称，请填写本次就诊医院。',
    visit_type: '当前是就诊类型，请选择门诊、急诊或住院。',
    status: '当前是就医状态，请确认本次就诊目前处于什么状态。',
    urgency: '当前是紧急程度，请确认病情紧急程度。',
  }

  return promptMap[field] || ''
}

const isFieldCompleted = (field: string) => {
  if (field === 'visit_date') {
    return !!form.visit_date
  }
  if (field === 'hospital') {
    return !!form.hospital.trim()
  }
  if (field === 'visit_type') {
    return !!form.visit_type
  }
  if (field === 'status') {
    return !!form.status
  }
  if (field === 'urgency') {
    return !!form.urgency
  }
  if (/^prescribed_medicine_name_(\d+)$/.test(field)) {
    const index = Number(field.match(/^prescribed_medicine_name_(\d+)$/)?.[1])
    return !!form.prescribed_medicines[index]?.name?.trim()
  }
  if (/^exam_name_(\d+)$/.test(field)) {
    const index = Number(field.match(/^exam_name_(\d+)$/)?.[1])
    return !!form.examinations[index]?.name?.trim()
  }
  return true
}

const handleFieldFocus = (field: string) => {
  markAssistiveInteraction()
  const prompt = getFieldFocusPrompt(field)
  if (!prompt || !isSpeechEnabled.value || !isSpeechSupported.value) {
    return
  }

  speakFieldGuidance(prompt, {
    priority: 'low',
    dedupeWindowMs: 1200,
    throttleWindowMs: 900,
  })
}

const handleFieldBlur = (field: string) => {
  if (!assistiveGuidanceEnabled.value || !isSpeechEnabled.value || !isSpeechSupported.value) {
    return
  }

  markAssistiveInteraction()
  if (isFieldCompleted(field)) {
    return
  }

  speakFieldGuidance(buildFieldCorrectionGuidance(field), {
    priority: 'low',
    interrupt: false,
    dedupeWindowMs: 1800,
    throttleWindowMs: 600,
  })
}

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
  attachments: [],
})

// 方法
const addMedicine = () => {
  form.prescribed_medicines.push({
    name: '',
    dosage: '',
    frequency: '',
    duration: '',
    instructions: '',
  })
}

const removeMedicine = (index: number) => {
  form.prescribed_medicines.splice(index, 1)
}

const addExamination = () => {
  form.examinations.push({
    name: '',
    type: '',
  })
}

const removeExamination = (index: number) => {
  form.examinations.splice(index, 1)
}

const getQueryValue = (key: string) => {
  const value = route.query[key]
  return Array.isArray(value) ? value[0] || '' : value || ''
}

const parseNameList = (raw: string) => {
  return Array.from(
    new Set(
      raw
        .split(',')
        .map(item => item.trim())
        .filter(item => item.length > 0)
    )
  )
}

const applyDraftQuery = () => {
  const source = getQueryValue('source')
  if (source && source !== 'page-agent') {
    return
  }

  const visitDate = getQueryValue('visit_date')
  const visitTime = getQueryValue('visit_time')
  const hospital = getQueryValue('hospital')
  const hospitalAddress = getQueryValue('hospital_address')
  const department = getQueryValue('department')
  const doctor = getQueryValue('doctor')
  const doctorTitle = getQueryValue('doctor_title')
  const visitType = getQueryValue('visit_type')
  const chiefComplaint = getQueryValue('chief_complaint')
  const diagnosis = getQueryValue('diagnosis')
  const medicalOrders = getQueryValue('medical_orders')
  const followUpDate = getQueryValue('follow_up_date')
  const status = getQueryValue('status')
  const urgency = getQueryValue('urgency')
  const prescribedMedicines = parseNameList(getQueryValue('prescribed_medicines'))
  const examinations = parseNameList(getQueryValue('examinations'))

  const visitTypeSet = new Set(VISIT_TYPE_OPTIONS.map(option => option.value))
  const statusSet = new Set(STATUS_OPTIONS.map(option => option.value))
  const urgencySet = new Set(URGENCY_OPTIONS.map(option => option.value))

  if (/^\d{4}-\d{2}-\d{2}$/.test(visitDate)) {
    form.visit_date = visitDate
  }
  if (/^\d{2}:\d{2}$/.test(visitTime)) {
    form.visit_time = visitTime
  }
  if (hospital) {
    form.hospital = hospital.slice(0, 100)
  }
  if (hospitalAddress) {
    form.hospital_address = hospitalAddress.slice(0, 200)
  }
  if (department) {
    form.department = department.slice(0, 50)
  }
  if (doctor) {
    form.doctor = doctor.slice(0, 50)
  }
  if (doctorTitle) {
    form.doctor_title = doctorTitle.slice(0, 50)
  }
  if (visitTypeSet.has(visitType as any)) {
    form.visit_type = visitType as MedicalRecordCreate['visit_type']
  }
  if (chiefComplaint) {
    form.chief_complaint = chiefComplaint.slice(0, 500)
  }
  if (diagnosis) {
    form.diagnosis = diagnosis.slice(0, 500)
  }
  if (medicalOrders) {
    form.medical_orders = medicalOrders.slice(0, 500)
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(followUpDate)) {
    form.follow_up_date = followUpDate
  }
  if (statusSet.has(status as any)) {
    form.status = status as MedicalRecordCreate['status']
  }
  if (urgencySet.has(urgency as any)) {
    form.urgency = urgency as MedicalRecordCreate['urgency']
  }
  if (prescribedMedicines.length > 0) {
    form.prescribed_medicines = prescribedMedicines.map(name => ({
      name,
      dosage: '',
      frequency: '',
      duration: '',
      instructions: '',
    }))
  }
  if (examinations.length > 0) {
    form.examinations = examinations.map(name => ({
      name,
      type: '',
    }))
  }

  assistiveSummaryLines.value = [
    form.visit_date ? `就诊日期：${form.visit_date}` : '',
    form.hospital ? `医院：${form.hospital}` : '',
    form.visit_type
      ? `就诊类型：${VISIT_TYPE_OPTIONS.find(item => item.value === form.visit_type)?.label || form.visit_type}`
      : '',
    form.status
      ? `就医状态：${STATUS_OPTIONS.find(item => item.value === form.status)?.label || form.status}`
      : '',
    form.urgency
      ? `紧急程度：${URGENCY_OPTIONS.find(item => item.value === form.urgency)?.label || form.urgency}`
      : '',
    form.diagnosis ? `诊断：${form.diagnosis}` : '',
  ].filter(Boolean)

  if (
    source === 'page-agent' &&
    (form.visit_date ||
      form.hospital ||
      form.diagnosis ||
      form.chief_complaint ||
      form.prescribed_medicines.length > 0)
  ) {
    const signature = JSON.stringify({
      visitDate: form.visit_date,
      visitTime: form.visit_time,
      hospital: form.hospital,
      visitType: form.visit_type,
      status: form.status,
      urgency: form.urgency,
      diagnosis: form.diagnosis,
      chiefComplaint: form.chief_complaint,
      prescribedMedicines: form.prescribed_medicines.map(item => item.name),
      examinations: form.examinations.map(item => item.name),
    })
    if (lastAppliedDraftSignature.value === signature) {
      return
    }
    lastAppliedDraftSignature.value = signature
    console.log('[MedicalRecordForm] 应用页面助手草稿', {
      visitDate: form.visit_date,
      hospital: form.hospital,
      visitType: form.visit_type,
      status: form.status,
      urgency: form.urgency,
      prescribedMedicines: form.prescribed_medicines.length,
      examinations: form.examinations.length,
    })
    toast.success('已载入页面助手草稿，请确认后再提交')
    activateFieldGuidance('已帮你预填病历表单。', 'prefill')
  }
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
  const submitTrace = createSubmissionTraceContext('MedicalRecordForm')
  const requestId = createTraceId('request')
  logClientTraceEvent(
    'MedicalRecordForm',
    'submit_start',
    {
      requestId,
      action: isEdit.value ? 'update' : 'create',
      recordId: recordId.value,
      prescribedMedicineCount: form.prescribed_medicines.length,
      examinationCount: form.examinations.length,
    },
    { traceContext: submitTrace }
  )

  if (!validateForm()) {
    const validationGuidance = buildValidationFailureGuidance()
    const firstValidationField = getFirstValidationIssueField()
    logClientTraceEvent(
      'MedicalRecordForm',
      'client_validation_failed',
      {
        requestId,
        validationErrors: errors.value,
        validationGuidance,
        firstValidationField,
      },
      { traceContext: submitTrace, severity: 'warn' }
    )
    toast.error(validationGuidance)
    activateFieldGuidance('', 'validation', validationGuidance)
    logClientTraceEvent(
      'MedicalRecordForm',
      'focus_validation_field',
      {
        requestId,
        field: firstValidationField,
        source: 'client-validation',
      },
      { traceContext: submitTrace, severity: 'warn' }
    )
    await focusValidationField(firstValidationField)
    return
  }

  try {
    loading.value = true
    logClientTraceEvent(
      'MedicalRecordForm',
      'request_dispatch',
      {
        requestId,
        action: isEdit.value ? 'update' : 'create',
        prescribedMedicineCount: form.prescribed_medicines.length,
        examinationCount: form.examinations.length,
      },
      { traceContext: submitTrace }
    )

    if (isEdit.value && recordId.value) {
      // 更新病历
      // 构造类型安全的更新载荷，显式断言枚举字段，避免 v-model 推断为普通 string
      const updatePayload: MedicalRecordUpdate = {
        visit_date: form.visit_date,
        visit_time: form.visit_time,
        hospital: form.hospital,
        hospital_address: form.hospital_address,
        department: form.department,
        doctor: form.doctor,
        doctor_title: form.doctor_title,
        visit_type:
          form.visit_type as import('@/types/medicalRecord').VisitType,
        chief_complaint: form.chief_complaint,
        present_illness: form.present_illness,
        diagnosis: form.diagnosis,
        diagnosis_code: form.diagnosis_code,
        treatment: form.treatment,
        prescribed_medicines: form.prescribed_medicines,
        examinations: form.examinations,
        examination_results: form.examination_results,
        lab_results: form.lab_results,
        medical_orders: form.medical_orders,
        notes: form.notes,
        total_cost: form.total_cost,
        insurance_coverage: form.insurance_coverage,
        self_pay_amount: form.self_pay_amount,
        follow_up_date: form.follow_up_date,
        follow_up_notes: form.follow_up_notes,
        symptom_score_before: form.symptom_score_before,
        symptom_score_after: form.symptom_score_after,
        satisfaction_score: form.satisfaction_score,
        status: form.status as import('@/types/medicalRecord').MedicalStatus,
        urgency: form.urgency as import('@/types/medicalRecord').UrgencyLevel,
        attachments: form.attachments,
      }
      await medicalRecordStore.updateRecord(recordId.value, updatePayload, {
        requestId,
      })
      logClientTraceEvent(
        'MedicalRecordForm',
        'submit_success',
        {
          requestId,
          action: 'update',
          recordId: recordId.value,
        },
        { traceContext: submitTrace }
      )
      toast.success('病历更新成功')
    } else {
      // 创建病历
      // 构造类型安全的创建载荷，显式断言枚举字段
      const createPayload: import('@/types/medicalRecord').MedicalRecordCreate =
        {
          visit_date: form.visit_date,
          visit_time: form.visit_time,
          hospital: form.hospital,
          hospital_address: form.hospital_address,
          department: form.department,
          doctor: form.doctor,
          doctor_title: form.doctor_title,
          visit_type:
            form.visit_type as import('@/types/medicalRecord').VisitType,
          chief_complaint: form.chief_complaint,
          present_illness: form.present_illness,
          diagnosis: form.diagnosis,
          diagnosis_code: form.diagnosis_code,
          treatment: form.treatment,
          prescribed_medicines: form.prescribed_medicines,
          examinations: form.examinations,
          examination_results: form.examination_results,
          lab_results: form.lab_results,
          medical_orders: form.medical_orders,
          notes: form.notes,
          total_cost: form.total_cost,
          insurance_coverage: form.insurance_coverage,
          self_pay_amount: form.self_pay_amount,
          follow_up_date: form.follow_up_date,
          follow_up_notes: form.follow_up_notes,
          symptom_score_before: form.symptom_score_before,
          symptom_score_after: form.symptom_score_after,
          satisfaction_score: form.satisfaction_score,
          status: form.status as import('@/types/medicalRecord').MedicalStatus,
          urgency: form.urgency as import('@/types/medicalRecord').UrgencyLevel,
          attachments: form.attachments,
        }
      await medicalRecordStore.createRecord(createPayload, { requestId })
      logClientTraceEvent(
        'MedicalRecordForm',
        'submit_success',
        {
          requestId,
          action: 'create',
        },
        { traceContext: submitTrace }
      )
      toast.success('病历创建成功')
    }

    router.push('/medical-records')
  } catch (error: any) {
    logApiErrorEvent('MedicalRecordForm', error, {
      action: isEdit.value ? 'update' : 'create',
      form: 'medical-record',
      recordId: recordId.value,
      prescribedMedicineCount: form.prescribed_medicines.length,
      examinationCount: form.examinations.length,
      submitSessionId: submitTrace.submitSessionId,
      requestId,
    })

    if (applyServerValidationErrors(error, submitTrace.submitSessionId, requestId)) {
      const validationGuidance = buildValidationFailureGuidance()
      const firstValidationField = getFirstValidationIssueField()
      toast.error(validationGuidance)
      activateFieldGuidance('', 'validation', validationGuidance)
      logClientTraceEvent(
        'MedicalRecordForm',
        'focus_validation_field',
        {
          requestId,
          field: firstValidationField,
          source: 'server-validation',
        },
        { traceContext: submitTrace, severity: 'warn' }
      )
      await focusValidationField(firstValidationField)
      return
    }

    const errorMessage = error.message || '保存失败，请重试'
    logClientTraceEvent(
      'MedicalRecordForm',
      'submit_failed',
      {
        requestId,
        errorMessage,
      },
      { traceContext: submitTrace, severity: 'error' }
    )
    toast.error(errorMessage)
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
      prescribed_medicines: record.prescribed_medicines ?? [],
      examinations: record.examinations ?? [],
      examination_results: record.examination_results || '',
      lab_results: record.lab_results ?? {},
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
      attachments: record.attachments ?? [],
    })
  } catch (error: any) {
    if (isRequestCancelledError(error)) {
      console.log('加载病历请求已取消')
      return
    }

    console.error('加载病历失败:', error)
    toast.error('加载病历失败，请重试')
    router.push('/medical-records')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(async () => {
  if (isEdit.value) {
    await loadRecord()
    applyDraftQuery()
    return
  }
  applyDraftQuery()
})

watch(
  () => route.fullPath,
  () => {
    applyDraftQuery()
  }
)

watch(
  () => assistiveMissingFields.value.join('|'),
  (key, oldKey) => {
    if (!assistiveGuidanceEnabled.value || !key || key === lastFieldGuidanceKey.value) {
      return
    }

    lastFieldGuidanceKey.value = key
    if (!isSpeechEnabled.value || !isSpeechSupported.value) {
      return
    }

    const continuous = isContinuousInteraction()
    markAssistiveInteraction()
    speakFieldGuidance(buildProgressGuidance(oldKey), {
      priority: continuous ? 'low' : 'normal',
      interrupt: !continuous,
      dedupeWindowMs: 2500,
      throttleWindowMs: continuous ? 900 : 500,
    })
  }
)

watch(
  () => [
    assistiveGuidanceEnabled.value,
    isSpeechEnabled.value,
    isSpeechSupported.value,
    assistiveMissingFields.value.join('|'),
    assistiveInteractionTick.value,
  ],
  ([enabled, speechEnabled, speechSupported, key], _oldValue, onCleanup) => {
    if (!enabled || !speechEnabled || !speechSupported || !key) {
      return
    }

    const timer = window.setTimeout(() => {
      if (!assistiveGuidanceEnabled.value || !assistiveMissingFields.value.length) {
        return
      }

      speakFieldGuidance(`先不着急，${buildNextFieldGuidance()}`, {
        priority: 'low',
        interrupt: false,
        dedupeWindowMs: 5000,
        throttleWindowMs: 0,
      })
    }, IDLE_REMINDER_DELAY_MS)

    onCleanup(() => window.clearTimeout(timer))
  }
)
</script>
