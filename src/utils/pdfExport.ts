import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import type { MedicalRecord } from '@/types/medicalRecord'

/**
 * 病历PDF导出工具类
 */
export class MedicalRecordPDFExporter {
  private doc: jsPDF
  private pageWidth: number
  private pageHeight: number
  private margin: number
  private currentY: number
  private lineHeight: number

  constructor() {
    this.doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })
    this.pageWidth = this.doc.internal.pageSize.getWidth()
    this.pageHeight = this.doc.internal.pageSize.getHeight()
    this.margin = 20
    this.currentY = this.margin
    this.lineHeight = 6
  }

  /**
   * 导出单个病历记录为PDF
   */
  async exportRecord(record: MedicalRecord): Promise<void> {
    try {
      // 设置中文字体
      this.setupChineseFont()

      // 添加标题
      this.addTitle('病历记录')

      // 添加基本信息
      this.addSection('基本信息', [
        {
          label: '就诊日期',
          value:
            this.formatDate(record.visit_date) +
            (record.visit_time ? ` ${record.visit_time}` : ''),
        },
        { label: '医院名称', value: record.hospital },
        { label: '医院地址', value: record.hospital_address || '-' },
        { label: '科室', value: record.department || '-' },
        {
          label: '医生',
          value: record.doctor
            ? `${record.doctor}${record.doctor_title ? `（${record.doctor_title}）` : ''}`
            : '-',
        },
        { label: '就诊类型', value: this.getVisitTypeLabel(record.visit_type) },
        { label: '就医状态', value: this.getStatusLabel(record.status) },
        { label: '紧急程度', value: this.getUrgencyLabel(record.urgency) },
      ])

      // 添加病情信息
      this.addSection('病情信息', [
        {
          label: '主诉',
          value: record.chief_complaint || '-',
          multiline: true,
        },
        {
          label: '现病史',
          value: record.present_illness || '-',
          multiline: true,
        },
        {
          label: '诊断结果',
          value: record.diagnosis
            ? `${record.diagnosis}${record.diagnosis_code ? ` (${record.diagnosis_code})` : ''}`
            : '-',
          multiline: true,
        },
        { label: '治疗方案', value: record.treatment || '-', multiline: true },
      ])

      // 添加处方药品
      if (
        record.prescribed_medicines &&
        record.prescribed_medicines.length > 0
      ) {
        this.addMedicinesSection(record.prescribed_medicines)
      }

      // 添加检查项目
      if (record.examinations && record.examinations.length > 0) {
        this.addExaminationsSection(record.examinations)
      }

      // 添加检查结果总结
      if (record.examination_results) {
        this.addSection('检查结果总结', [
          { label: '', value: record.examination_results, multiline: true },
        ])
      }

      // 添加费用信息
      this.addCostSection(record)

      // 添加复诊信息
      if (record.follow_up_date || record.follow_up_notes) {
        this.addSection('复诊信息', [
          {
            label: '复诊日期',
            value: record.follow_up_date
              ? this.formatDate(record.follow_up_date)
              : '-',
          },
          {
            label: '复诊说明',
            value: record.follow_up_notes || '-',
            multiline: true,
          },
        ])
      }

      // 添加评分信息
      if (
        record.satisfaction_score ||
        record.symptom_score_before ||
        record.symptom_score_after
      ) {
        this.addScoreSection(record)
      }

      // 添加医嘱和备注
      if (record.medical_orders || record.notes) {
        this.addSection('医嘱和备注', [
          {
            label: '医嘱',
            value: record.medical_orders || '-',
            multiline: true,
          },
          { label: '备注', value: record.notes || '-', multiline: true },
        ])
      }

      // 添加页脚
      this.addFooter()

      // 下载PDF
      const fileName = `病历记录_${record.hospital}_${this.formatDate(record.visit_date)}.pdf`
      this.doc.save(fileName)
    } catch (error) {
      console.error('导出PDF失败:', error)
      throw new Error('导出PDF失败，请重试')
    }
  }

  /**
   * 导出多个病历记录为PDF
   */
  async exportRecords(records: MedicalRecord[]): Promise<void> {
    try {
      this.setupChineseFont()

      // 添加标题
      this.addTitle('病历记录汇总')

      // 添加汇总信息
      this.addSummarySection(records)

      // 逐个添加病历记录
      for (let i = 0; i < records.length; i++) {
        const record = records[i]

        // 检查是否需要新页面
        if (this.currentY > this.pageHeight - 50) {
          this.doc.addPage()
          this.currentY = this.margin
        }

        // 添加分隔线
        if (i > 0) {
          this.addSeparator()
        }

        // 添加病历记录
        this.addRecordSummary(record, i + 1)
      }

      // 添加页脚
      this.addFooter()

      // 下载PDF
      const fileName = `病历记录汇总_${new Date().toISOString().split('T')[0]}.pdf`
      this.doc.save(fileName)
    } catch (error) {
      console.error('导出PDF失败:', error)
      throw new Error('导出PDF失败，请重试')
    }
  }

  /**
   * 设置中文字体
   */
  private setupChineseFont(): void {
    // 注意：这里需要添加中文字体支持
    // 可以使用 jsPDF 的字体插件或者自定义字体
    this.doc.setFont('helvetica')
  }

  /**
   * 添加标题
   */
  private addTitle(title: string): void {
    this.doc.setFontSize(20)
    this.doc.setFont('helvetica', 'bold')
    const titleWidth = this.doc.getTextWidth(title)
    const x = (this.pageWidth - titleWidth) / 2
    this.doc.text(title, x, this.currentY)
    this.currentY += 15
  }

  /**
   * 添加章节
   */
  private addSection(
    title: string,
    items: Array<{ label: string; value: string; multiline?: boolean }>
  ): void {
    // 检查是否需要新页面
    if (this.currentY > this.pageHeight - 40) {
      this.doc.addPage()
      this.currentY = this.margin
    }

    // 添加章节标题
    this.doc.setFontSize(14)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text(title, this.margin, this.currentY)
    this.currentY += 8

    // 添加内容
    this.doc.setFontSize(10)
    this.doc.setFont('helvetica', 'normal')

    for (const item of items) {
      if (item.label) {
        const labelText = `${item.label}：`
        this.doc.setFont('helvetica', 'bold')
        this.doc.text(labelText, this.margin, this.currentY)

        const labelWidth = this.doc.getTextWidth(labelText)
        this.doc.setFont('helvetica', 'normal')

        if (item.multiline) {
          // 多行文本处理
          const lines = this.doc.splitTextToSize(
            item.value,
            this.pageWidth - this.margin * 2 - labelWidth
          )
          this.doc.text(lines, this.margin + labelWidth, this.currentY)
          this.currentY += lines.length * this.lineHeight
        } else {
          this.doc.text(item.value, this.margin + labelWidth, this.currentY)
          this.currentY += this.lineHeight
        }
      } else {
        // 无标签的内容
        if (item.multiline) {
          const lines = this.doc.splitTextToSize(
            item.value,
            this.pageWidth - this.margin * 2
          )
          this.doc.text(lines, this.margin, this.currentY)
          this.currentY += lines.length * this.lineHeight
        } else {
          this.doc.text(item.value, this.margin, this.currentY)
          this.currentY += this.lineHeight
        }
      }
    }

    this.currentY += 5
  }

  /**
   * 添加处方药品章节
   */
  private addMedicinesSection(medicines: any[]): void {
    this.doc.setFontSize(14)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text('处方药品', this.margin, this.currentY)
    this.currentY += 8

    this.doc.setFontSize(10)
    this.doc.setFont('helvetica', 'normal')

    for (let i = 0; i < medicines.length; i++) {
      const medicine = medicines[i]

      // 检查是否需要新页面
      if (this.currentY > this.pageHeight - 30) {
        this.doc.addPage()
        this.currentY = this.margin
      }

      this.doc.setFont('helvetica', 'bold')
      this.doc.text(`${i + 1}. ${medicine.name}`, this.margin, this.currentY)
      this.currentY += this.lineHeight

      this.doc.setFont('helvetica', 'normal')
      if (medicine.dosage) {
        this.doc.text(
          `   用法用量：${medicine.dosage}`,
          this.margin,
          this.currentY
        )
        this.currentY += this.lineHeight
      }
      if (medicine.frequency) {
        this.doc.text(
          `   服用频次：${medicine.frequency}`,
          this.margin,
          this.currentY
        )
        this.currentY += this.lineHeight
      }
      if (medicine.duration) {
        this.doc.text(
          `   服用时长：${medicine.duration}`,
          this.margin,
          this.currentY
        )
        this.currentY += this.lineHeight
      }
      if (medicine.instructions) {
        this.doc.text(
          `   用药说明：${medicine.instructions}`,
          this.margin,
          this.currentY
        )
        this.currentY += this.lineHeight
      }

      this.currentY += 3
    }

    this.currentY += 5
  }

  /**
   * 添加检查项目章节
   */
  private addExaminationsSection(examinations: any[]): void {
    this.doc.setFontSize(14)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text('检查项目', this.margin, this.currentY)
    this.currentY += 8

    this.doc.setFontSize(10)
    this.doc.setFont('helvetica', 'normal')

    for (let i = 0; i < examinations.length; i++) {
      const exam = examinations[i]

      // 检查是否需要新页面
      if (this.currentY > this.pageHeight - 30) {
        this.doc.addPage()
        this.currentY = this.margin
      }

      this.doc.setFont('helvetica', 'bold')
      this.doc.text(`${i + 1}. ${exam.name}`, this.margin, this.currentY)
      this.currentY += this.lineHeight

      this.doc.setFont('helvetica', 'normal')
      if (exam.type) {
        this.doc.text(`   检查类型：${exam.type}`, this.margin, this.currentY)
        this.currentY += this.lineHeight
      }
      if (exam.result) {
        const lines = this.doc.splitTextToSize(
          `   检查结果：${exam.result}`,
          this.pageWidth - this.margin * 2
        )
        this.doc.text(lines, this.margin, this.currentY)
        this.currentY += lines.length * this.lineHeight
      }

      this.currentY += 3
    }

    this.currentY += 5
  }

  /**
   * 添加费用信息章节
   */
  private addCostSection(record: MedicalRecord): void {
    const costItems = []

    if (record.total_cost) {
      costItems.push({
        label: '总费用',
        value: `¥${record.total_cost.toLocaleString()}`,
      })
    }
    if (record.insurance_coverage) {
      costItems.push({
        label: '医保报销',
        value: `¥${record.insurance_coverage.toLocaleString()}`,
      })
    }
    if (record.self_pay_amount) {
      costItems.push({
        label: '自费金额',
        value: `¥${record.self_pay_amount.toLocaleString()}`,
      })
    }

    if (costItems.length > 0) {
      this.addSection('费用信息', costItems)
    }
  }

  /**
   * 添加评分信息章节
   */
  private addScoreSection(record: MedicalRecord): void {
    const scoreItems = []

    if (record.satisfaction_score) {
      scoreItems.push({
        label: '满意度评分',
        value: `${record.satisfaction_score}/5分`,
      })
    }
    if (record.symptom_score_before) {
      scoreItems.push({
        label: '就诊前症状评分',
        value: `${record.symptom_score_before}/10分`,
      })
    }
    if (record.symptom_score_after) {
      scoreItems.push({
        label: '就诊后症状评分',
        value: `${record.symptom_score_after}/10分`,
      })
    }

    if (record.symptom_score_before && record.symptom_score_after) {
      const improvement =
        record.symptom_score_before - record.symptom_score_after
      let improvementText = ''
      if (improvement > 0) {
        improvementText = `改善${improvement}分`
      } else if (improvement < 0) {
        improvementText = `恶化${Math.abs(improvement)}分`
      } else {
        improvementText = '无变化'
      }
      scoreItems.push({ label: '症状变化', value: improvementText })
    }

    if (scoreItems.length > 0) {
      this.addSection('评分信息', scoreItems)
    }
  }

  /**
   * 添加汇总信息章节
   */
  private addSummarySection(records: MedicalRecord[]): void {
    const totalCost = records.reduce(
      (sum, record) => sum + (record.total_cost ?? 0),
      0
    )
    const uniqueHospitals = new Set(records.map(record => record.hospital)).size
    const uniqueDepartments = new Set(
      records.map(record => record.department).filter(Boolean)
    ).size

    this.addSection('汇总信息', [
      { label: '总就诊次数', value: `${records.length}次` },
      { label: '就诊医院数', value: `${uniqueHospitals}家` },
      { label: '就诊科室数', value: `${uniqueDepartments}个` },
      { label: '总费用', value: `¥${totalCost.toLocaleString()}` },
      {
        label: '平均费用',
        value: `¥${Math.round(totalCost / records.length).toLocaleString()}`,
      },
      { label: '导出时间', value: new Date().toLocaleString('zh-CN') },
    ])
  }

  /**
   * 添加病历记录摘要
   */
  private addRecordSummary(record: MedicalRecord, index: number): void {
    this.doc.setFontSize(12)
    this.doc.setFont('helvetica', 'bold')
    this.doc.text(
      `${index}. ${record.hospital} - ${this.formatDate(record.visit_date)}`,
      this.margin,
      this.currentY
    )
    this.currentY += 8

    this.doc.setFontSize(10)
    this.doc.setFont('helvetica', 'normal')

    const items = [
      { label: '科室', value: record.department || '-' },
      { label: '医生', value: record.doctor || '-' },
      { label: '诊断', value: record.diagnosis || '-' },
      {
        label: '费用',
        value: record.total_cost
          ? `¥${record.total_cost.toLocaleString()}`
          : '-',
      },
    ]

    for (const item of items) {
      this.doc.text(
        `${item.label}：${item.value}`,
        this.margin + 5,
        this.currentY
      )
      this.currentY += this.lineHeight
    }

    this.currentY += 5
  }

  /**
   * 添加分隔线
   */
  private addSeparator(): void {
    this.doc.setDrawColor(200, 200, 200)
    this.doc.line(
      this.margin,
      this.currentY,
      this.pageWidth - this.margin,
      this.currentY
    )
    this.currentY += 8
  }

  /**
   * 添加页脚
   */
  private addFooter(): void {
    const pageCount = this.doc.getNumberOfPages()

    for (let i = 1; i <= pageCount; i++) {
      this.doc.setPage(i)
      this.doc.setFontSize(8)
      this.doc.setFont('helvetica', 'normal')

      // 页码
      const pageText = `第 ${i} 页，共 ${pageCount} 页`
      const pageTextWidth = this.doc.getTextWidth(pageText)
      this.doc.text(
        pageText,
        this.pageWidth - this.margin - pageTextWidth,
        this.pageHeight - 10
      )

      // 生成时间
      const timeText = `生成时间：${new Date().toLocaleString('zh-CN')}`
      this.doc.text(timeText, this.margin, this.pageHeight - 10)
    }
  }

  /**
   * 格式化日期
   */
  private formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('zh-CN')
  }

  /**
   * 获取就诊类型标签
   */
  private getVisitTypeLabel(visitType: string): string {
    const types: Record<string, string> = {
      outpatient: '门诊',
      emergency: '急诊',
      inpatient: '住院',
      physical_exam: '体检',
    }
    return types[visitType] || visitType
  }

  /**
   * 获取状态标签
   */
  private getStatusLabel(status: string): string {
    const statuses: Record<string, string> = {
      completed: '已完成',
      scheduled: '已预约',
      cancelled: '已取消',
      no_show: '未到诊',
      rescheduled: '已改期',
    }
    return statuses[status] || status
  }

  /**
   * 获取紧急程度标签
   */
  private getUrgencyLabel(urgency: string): string {
    const urgencies: Record<string, string> = {
      routine: '常规',
      urgent: '紧急',
      emergency: '急诊',
      critical: '危重',
    }
    return urgencies[urgency] || urgency
  }
}

/**
 * 导出单个病历记录为PDF
 */
export const exportMedicalRecordToPDF = async (
  record: MedicalRecord
): Promise<void> => {
  const exporter = new MedicalRecordPDFExporter()
  await exporter.exportRecord(record)
}

/**
 * 导出多个病历记录为PDF
 */
export const exportMedicalRecordsToPDF = async (
  records: MedicalRecord[]
): Promise<void> => {
  const exporter = new MedicalRecordPDFExporter()
  await exporter.exportRecords(records)
}

/**
 * 从HTML元素导出PDF
 */
export const exportElementToPDF = async (
  element: HTMLElement,
  filename: string
): Promise<void> => {
  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

    const imgWidth = 210
    const pageHeight = 295
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight

    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    pdf.save(filename)
  } catch (error) {
    console.error('导出PDF失败:', error)
    throw new Error('导出PDF失败，请重试')
  }
}
