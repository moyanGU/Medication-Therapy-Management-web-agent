import assert from 'node:assert/strict'
import test from 'node:test'
import {
  buildMedicineDraftPayload,
  buildReminderDraftPayload,
} from '../services/pageAgentDraftParser.ts'

test('解析早晚各一次与长期草稿', () => {
  const result = buildReminderDraftPayload(
    '帮我创建阿莫西林早晚各一次1粒餐后提醒，长期服用',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '阿莫西林')
  assert.equal(result.query.dosage, '1')
  assert.equal(result.query.dosage_unit, 'capsule')
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.custom_times, '08:00,20:00')
  assert.equal(result.query.reminder_time, '08:00')
  assert.equal(result.query.meal_timing, 'after_meal')
  assert.equal(result.query.no_end_date, '1')
})

test('解析周频提醒与明确结束日期', () => {
  const result = buildReminderDraftPayload(
    '新建二甲双胍周一周三周五晚上8点1片的提醒草稿，到2026-04-01结束',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '二甲双胍')
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '1,3,5')
  assert.equal(result.query.reminder_time, '20:00')
  assert.equal(result.query.end_date, '2026-04-01')
})

test('解析三餐后与中文时长', () => {
  const result = buildReminderDraftPayload(
    '创建维生素D三餐后1粒提醒，持续七天',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.custom_times, '08:00,13:00,19:00')
  assert.equal(result.query.meal_timing, 'after_meal')
  assert.equal(result.query.end_date, '2026-03-31')
})

test('解析睡前半小时语义时间', () => {
  const result = buildReminderDraftPayload(
    '帮我新建钙片睡前半小时1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.reminder_time, '20:30')
  assert.equal(result.query.meal_timing, 'before_bed')
})

test('解析饭前半小时与隔日时长', () => {
  const result = buildReminderDraftPayload(
    '创建奥美拉唑隔日一次1粒饭前半小时提醒，持续两周',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '奥美拉唑')
  assert.equal(result.query.frequency, 'every_other_day')
  assert.equal(result.query.meal_timing, 'before_meal')
  assert.equal(result.query.end_date, '2026-04-07')
})

test('解析一日四次表达', () => {
  const result = buildReminderDraftPayload(
    '新增布洛芬一日四次1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'four_times_daily')
  assert.equal(result.query.dosage, '1')
  assert.equal(result.query.dosage_unit, 'tablet')
})

test('解析自定义多时间点草稿', () => {
  const result = buildReminderDraftPayload(
    '帮我生成维生素C自定义08:00/14:00/20:00 1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '维生素C')
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.custom_times, '08:00,14:00,20:00')
  assert.equal(result.query.reminder_time, '08:00')
})

test('解析每周一三五简写', () => {
  const result = buildReminderDraftPayload(
    '创建氯雷他定每周一三五晚上8点1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '氯雷他定')
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '1,3,5')
  assert.equal(result.query.reminder_time, '20:00')
})

test('解析早餐前半小时表达', () => {
  const result = buildReminderDraftPayload(
    '新增叶酸早餐前半小时1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.reminder_time, '07:00')
  assert.equal(result.query.meal_timing, 'before_breakfast')
})

test('解析早中晚饭后各一次与一个月时长', () => {
  const result = buildReminderDraftPayload(
    '帮我创建维生素B早中晚饭后各一次1片提醒，持续一个月',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '维生素B')
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.custom_times, '08:30,12:30,18:30')
  assert.equal(result.query.meal_timing, 'after_meal')
  assert.equal(result.query.end_date, '2026-04-23')
})

test('解析工作日提醒', () => {
  const result = buildReminderDraftPayload(
    '新增鱼油工作日晚上8点1粒提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '1,2,3,4,5')
  assert.equal(result.query.reminder_time, '20:00')
})

test('解析周末提醒', () => {
  const result = buildReminderDraftPayload(
    '创建维生素D周末早上8点1粒提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '0,6')
  assert.equal(result.query.reminder_time, '08:00')
})

test('解析早晚饭后各一次表达', () => {
  const result = buildReminderDraftPayload(
    '帮我创建阿司匹林早晚饭后各一次1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '阿司匹林')
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.custom_times, '08:30,18:30')
  assert.equal(result.query.meal_timing, 'after_meal')
})

test('解析早餐后半小时与备注说明', () => {
  const result = buildReminderDraftPayload(
    '新增辅酶Q10早餐后半小时1粒提醒，持续三个月，备注饭后多喝水',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '辅酶Q10')
  assert.equal(result.query.reminder_time, '09:00')
  assert.equal(result.query.meal_timing, 'after_meal')
  assert.equal(result.query.end_date, '2026-06-22')
  assert.equal(result.query.special_instructions, '饭后多喝水')
})

test('解析工作日早晚各一次', () => {
  const result = buildReminderDraftPayload(
    '新增二甲双胍工作日早晚各一次1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '1,2,3,4,5')
  assert.equal(result.query.custom_times, '08:00,20:00')
  assert.equal(result.query.reminder_time, '08:00')
})

test('解析周末睡前表达', () => {
  const result = buildReminderDraftPayload(
    '帮我创建褪黑素周末睡前1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '0,6')
  assert.equal(result.query.reminder_time, '21:00')
  assert.equal(result.query.meal_timing, 'before_bed')
})

test('解析每星期二四六与中文绝对日期', () => {
  const result = buildReminderDraftPayload(
    '创建钙片每星期二四六晚上8点1片提醒，截止到2026年6月30号',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.frequency, 'custom')
  assert.equal(result.query.weekdays, '2,4,6')
  assert.equal(result.query.reminder_time, '20:00')
  assert.equal(result.query.end_date, '2026-06-30')
})

test('解析饭后1小时与必要时服用', () => {
  const result = buildReminderDraftPayload(
    '新增布洛芬饭后1小时必要时服用1片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '布洛芬')
  assert.equal(result.query.meal_timing, 'after_meal')
  assert.equal(result.query.special_instructions, '必要时服用；饭后1小时')
})

test('解析随餐表达', () => {
  const result = buildReminderDraftPayload(
    '新增益生菌随餐1袋提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '益生菌')
  assert.equal(result.query.meal_timing, 'with_meal')
})

test('解析提醒后置药品名与每晚中文剂量', () => {
  const result = buildReminderDraftPayload(
    '给爷爷创建一个用药提醒，阿司匹林肠溶片，每晚一片，饭前服用',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '阿司匹林肠溶片')
  assert.equal(result.query.dosage, '1')
  assert.equal(result.query.dosage_unit, 'tablet')
  assert.equal(result.query.frequency, 'daily')
  assert.equal(result.query.reminder_time, '20:00')
  assert.equal(result.query.meal_timing, 'before_meal')
})

test('解析每晚睡前避免双时间点', () => {
  const result = buildReminderDraftPayload(
    '帮我创建褪黑素每晚睡前一片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '褪黑素')
  assert.equal(result.query.frequency, 'daily')
  assert.equal(result.query.reminder_time, '21:00')
  assert.equal(result.query.custom_times, undefined)
  assert.equal(result.query.dosage, '1')
  assert.equal(result.query.dosage_unit, 'tablet')
})

test('解析中文半片剂量', () => {
  const result = buildReminderDraftPayload(
    '新增阿司匹林每晚半片提醒',
    '2026-03-26'
  )

  assert.ok(result)
  assert.equal(result.query.medicine_name, '阿司匹林')
  assert.equal(result.query.dosage, '0.5')
  assert.equal(result.query.dosage_unit, 'tablet')
  assert.equal(result.query.reminder_time, '20:00')
})

test('非提醒创建意图不返回草稿', () => {
  const result = buildReminderDraftPayload('帮我看看今天的提醒情况', '2026-03-26')
  assert.equal(result, null)
})
test('medicine draft parses add-new-medicine request with usage summary', () => {
  const result = buildMedicineDraftPayload(
    '添加一个新药，维生素B1片，10毫克，100片。用药时间是每天3次，一次1片',
    '2026-05-21'
  )

  assert.ok(result)
  assert.equal(result.query.name, '维生素B1片')
  assert.equal(result.query.medicine_type, 'tablet')
  assert.equal(result.query.specification, '10毫克')
  assert.equal(result.query.quantity, '100')
  assert.equal(result.query.description, '用法用量：每天3次；一次1片')
  assert.equal(result.query.open_dialog, '1')
})
