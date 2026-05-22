export interface ReminderDraftPayload {
  query: Record<string, string>
  summary: string[]
}

export interface PageAgentDraftPayload {
  query: Record<string, string>
  summary: string[]
}

const DOSAGE_UNIT_MAP: Record<string, string> = {
  片: 'tablet',
  粒: 'capsule',
  毫升: 'ml',
  ml: 'ml',
  ML: 'ml',
  毫克: 'mg',
  mg: 'mg',
  MG: 'mg',
  克: 'g',
  g: 'g',
  G: 'g',
  滴: 'drop',
  喷: 'spray',
  贴: 'patch',
  针: 'injection',
}

const DOSAGE_UNIT_LABELS: Record<string, string> = {
  tablet: '片',
  capsule: '粒',
  ml: '毫升',
  mg: '毫克',
  g: '克',
  drop: '滴',
  spray: '喷',
  patch: '贴',
  injection: '针',
}

const FREQUENCY_LABELS: Record<string, string> = {
  daily: '每日一次',
  twice_daily: '每日两次',
  three_times_daily: '每日三次',
  four_times_daily: '每日四次',
  weekly: '每周',
  every_other_day: '隔日一次',
  custom: '自定义多时点',
}

const MEAL_TIMING_LABELS: Record<string, string> = {
  before_meal: '餐前',
  with_meal: '餐中',
  after_meal: '餐后',
  anytime: '任意时间',
  before_breakfast: '早饭前',
  after_dinner: '晚饭后',
  before_bed: '睡前',
}

const WEEKDAY_TOKEN_MAP: Array<{ pattern: RegExp; value: number; label: string }> = [
  { pattern: /(周日|周天|星期日|星期天)/, value: 0, label: '周日' },
  { pattern: /(周一|星期一)/, value: 1, label: '周一' },
  { pattern: /(周二|星期二)/, value: 2, label: '周二' },
  { pattern: /(周三|星期三)/, value: 3, label: '周三' },
  { pattern: /(周四|星期四)/, value: 4, label: '周四' },
  { pattern: /(周五|星期五)/, value: 5, label: '周五' },
  { pattern: /(周六|星期六)/, value: 6, label: '周六' },
]
const SHORT_WEEKDAY_MAP: Record<string, number> = {
  日: 0,
  天: 0,
  一: 1,
  二: 2,
  三: 3,
  四: 4,
  五: 5,
  六: 6,
}

const SEMANTIC_TIME_PATTERNS: Array<{ pattern: RegExp; times: string[] }> = [
  { pattern: /(早晚饭后各一次|早晚餐后各一次)/, times: ['08:30', '18:30'] },
  { pattern: /(早晚饭前各一次|早晚餐前各一次)/, times: ['07:30', '17:30'] },
  { pattern: /(早中晚饭后各一次|早中晚餐后各一次)/, times: ['08:30', '12:30', '18:30'] },
  { pattern: /(早中晚饭前各一次|早中晚餐前各一次)/, times: ['07:30', '11:30', '17:30'] },
  { pattern: /(早晚各一次|早晚一次)/, times: ['08:00', '20:00'] },
  { pattern: /(早中晚各一次|早中晚一次|三餐后|三餐前)/, times: ['08:00', '13:00', '19:00'] },
  { pattern: /(早餐前半小时|早饭前半小时)/, times: ['07:00'] },
  { pattern: /(早餐后半小时|早饭后半小时)/, times: ['09:00'] },
  { pattern: /(早餐前|早饭前)/, times: ['07:30'] },
  { pattern: /(早餐后|早饭后)/, times: ['08:30'] },
  { pattern: /(午饭前半小时|午餐前半小时)/, times: ['11:00'] },
  { pattern: /(午饭前|午餐前)/, times: ['11:30'] },
  { pattern: /(午饭后半小时|午餐后半小时)/, times: ['13:00'] },
  { pattern: /(午饭后|午餐后)/, times: ['12:30'] },
  { pattern: /(晚饭前半小时|晚餐前半小时)/, times: ['17:00'] },
  { pattern: /(晚饭前|晚餐前)/, times: ['17:30'] },
  { pattern: /(晚饭后半小时|晚餐后半小时)/, times: ['19:00'] },
  { pattern: /(晚饭后|晚餐后)/, times: ['18:30'] },
  { pattern: /(睡前半小时)/, times: ['20:30'] },
  { pattern: /(睡前)/, times: ['21:00'] },
  { pattern: /(每晚|每夜|每日晚间|每天晚间)/, times: ['20:00'] },
  { pattern: /(每早|每晨|每日早晨|每天早晨)/, times: ['08:00'] },
  { pattern: /(每中午|每日中午|每天中午)/, times: ['12:00'] },
  { pattern: /(早上|清晨|早晨|晨起)/, times: ['08:00'] },
  { pattern: /(上午)/, times: ['09:00'] },
  { pattern: /(中午)/, times: ['12:00'] },
  { pattern: /(下午)/, times: ['15:00'] },
  { pattern: /(晚上|晚间|傍晚)/, times: ['20:00'] },
  { pattern: /(凌晨)/, times: ['06:00'] },
]

function normalizeTaskText(task: string): string {
  return task.replace(/\s+/g, '').trim()
}

function sanitizeMedicineName(raw: string): string {
  return raw
    .replace(/^(帮我|请|给我|为我|把|新增|添加|创建|新建|生成|填写|准备|一个|一条)+/, '')
    .replace(
      /(每天|每日|早上|上午|中午|下午|晚上|凌晨|餐前|餐中|餐后|任意时间|睡前|随餐|长期|一次|两次|三次|四次|隔日|每周|每星期|工作日|周末|自定义|必要时服用|必要时使用|按需服用|按需使用|饭后(?:1|一)小时|餐后(?:1|一)小时|周[一二三四五六日天末]|星期[一二三四五六日天]|早晚各|早晚饭前各|早晚饭后各|早晚餐前各|早晚餐后各|早中晚各|早中晚饭前各|早中晚饭后各|早中晚餐前各|早中晚餐后各|三餐前|三餐后|早餐前|早餐后|早饭前|早饭后|午饭前|午饭后|晚饭前|晚饭后|\d{1,2}[点时:：]|提醒|草稿).*$/,
      ''
    )
    .replace(/[，。！、,.]+$/g, '')
    .trim()
    .slice(0, 32)
}

function extractMedicineName(task: string): string {
  const fromDosage = task.match(
    /([一-龥A-Za-z0-9·()（）-]{2,32})(?=\s*(?:\d+(?:\.\d+)?|[一二两三四五六七八九十半])\s*(?:片|粒|毫升|ml|ML|毫克|mg|MG|克|g|G|滴|喷|贴|针))/
  )?.[1]
  if (fromDosage) {
    const sanitizedFromDosage = sanitizeMedicineName(fromDosage)
    if (/[一-龥A-Za-z]/.test(sanitizedFromDosage) && sanitizedFromDosage.length >= 2) {
      return sanitizedFromDosage
    }
  }

  const candidateSegments = task
    .split(/[，,。；;、]/)
    .map((segment) => segment.trim())
    .filter(Boolean)
  for (const segment of candidateSegments) {
    if (
      /(创建|新建|生成|填写|准备|新增|添加|提醒|草稿|每天|每日|每晚|每早|每晨|每周|每星期|餐前|餐后|饭前|饭后|随餐|睡前|服用|一次|两次|三次|四次|隔日|周末|工作日)/.test(
        segment
      )
    ) {
      continue
    }
    const sanitizedSegment = sanitizeMedicineName(segment)
    if (/[一-龥A-Za-z]/.test(sanitizedSegment) && sanitizedSegment.length >= 2) {
      return sanitizedSegment
    }
  }

  const aroundIntent = task.match(
    /(?:创建|新建|生成|填写|准备|新增|添加)(.+?)(?:提醒|草稿)/
  )?.[1]
  return sanitizeMedicineName(aroundIntent || '')
}

function parseChineseNumber(raw: string): number {
  const trimmed = raw.trim()
  if (!trimmed) {
    return Number.NaN
  }
  if (trimmed === '半') {
    return 0.5
  }
  if (/^\d+$/.test(trimmed)) {
    return Number(trimmed)
  }

  const singleMap: Record<string, number> = {
    零: 0,
    一: 1,
    二: 2,
    两: 2,
    三: 3,
    四: 4,
    五: 5,
    六: 6,
    七: 7,
    八: 8,
    九: 9,
  }

  if (trimmed === '十') {
    return 10
  }
  if (trimmed.includes('十')) {
    const [tensRaw, onesRaw] = trimmed.split('十')
    const tens = tensRaw ? singleMap[tensRaw] ?? Number.NaN : 1
    const ones = onesRaw ? singleMap[onesRaw] ?? Number.NaN : 0
    if (!Number.isNaN(tens) && !Number.isNaN(ones)) {
      return tens * 10 + ones
    }
  }

  return singleMap[trimmed] ?? Number.NaN
}

function parseReminderTimes(task: string): string[] {
  const matchedTimes: string[] = []
  const explicitPatterns = [
    /(\d{1,2})\s*[:：]\s*(\d{1,2})/g,
    /(\d{1,2})\s*(?:点|时)(?:(\d{1,2})\s*分?)?(?!\s*(?:\d|片|粒|毫升|ml|ML|毫克|mg|MG|克|g|G|滴|喷|贴|针))/g,
  ]

  for (const pattern of explicitPatterns) {
    const explicitMatches = task.matchAll(pattern)
    for (const match of explicitMatches) {
      const hour = Number(match[1])
      const minute = Number(match[2] || '0')
      if (hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59) {
        matchedTimes.push(
          `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
        )
      }
    }
  }

  if (matchedTimes.length > 0) {
    return Array.from(new Set(matchedTimes))
  }

  if (/睡前半小时/.test(task)) {
    return ['20:30']
  }
  if (/睡前/.test(task)) {
    return ['21:00']
  }

  return SEMANTIC_TIME_PATTERNS.flatMap((item) =>
    item.pattern.test(task) ? item.times : []
  ).filter((time, index, array) => array.indexOf(time) === index)
}

function parseReminderWeekdays(task: string): number[] {
  const weekdays = new Set(
    WEEKDAY_TOKEN_MAP.filter((item) => item.pattern.test(task)).map((item) => item.value)
  )

  if (/工作日/.test(task)) {
    ;[1, 2, 3, 4, 5].forEach((weekday) => weekdays.add(weekday))
  }
  if (/周末/.test(task)) {
    ;[0, 6].forEach((weekday) => weekdays.add(weekday))
  }

  const shortMatches = task.matchAll(/(?:每周|每星期)([一二三四五六日天、,，和与]+)/g)
  for (const match of shortMatches) {
    for (const token of match[1].match(/[一二三四五六日天]/g) || []) {
      const weekday = SHORT_WEEKDAY_MAP[token]
      if (weekday !== undefined) {
        weekdays.add(weekday)
      }
    }
  }

  return Array.from(weekdays).sort((left, right) => left - right)
}

function formatWeekdays(weekdays: number[]): string {
  return weekdays
    .map((day) => WEEKDAY_TOKEN_MAP.find((item) => item.value === day)?.label || '')
    .filter(Boolean)
    .join('、')
}

function addDays(dateString: string, days: number): string {
  const date = new Date(`${dateString}T00:00:00`)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

function parseReminderEndDate(task: string, startDate: string): string {
  const absolute = task.match(
    /(?:到|截止(?:到)?|至)\s*(\d{4})[-年/.](\d{1,2})[-月/.](\d{1,2})(?:日|号)?/
  )
  if (absolute) {
    const [, year, month, day] = absolute
    return `${year}-${String(Number(month)).padStart(2, '0')}-${String(Number(day)).padStart(2, '0')}`
  }

  const durationDays = task.match(/(?:持续|服用|用药|共)\s*(\d{1,3}|[一二两三四五六七八九十]+)\s*天/)
  if (durationDays) {
    const days = parseChineseNumber(durationDays[1])
    if (days > 0) {
      return addDays(startDate, days - 1)
    }
  }

  const durationWeeks = task.match(/(?:持续|服用|用药|共)\s*(\d{1,2}|[一二两三四五六七八九十]+)\s*周/)
  if (durationWeeks) {
    const weeks = parseChineseNumber(durationWeeks[1])
    if (weeks > 0) {
      return addDays(startDate, weeks * 7 - 1)
    }
  }

  const durationMonths = task.match(/(?:持续|服用|用药|共)\s*(\d{1,2}|[一二两三四五六七八九十]+)\s*个?月/)
  if (durationMonths) {
    const months = parseChineseNumber(durationMonths[1])
    if (months > 0) {
      return addDays(startDate, months * 30 - 1)
    }
  }

  return ''
}

function parseReminderFrequency(task: string): string {
  if (/早晚饭后各一次|早晚餐后各一次|早晚饭前各一次|早晚餐前各一次/.test(task)) {
    return 'twice_daily'
  }
  if (/早中晚饭后各一次|早中晚餐后各一次|早中晚饭前各一次|早中晚餐前各一次/.test(task)) {
    return 'three_times_daily'
  }
  if (/早中晚各一次|早中晚一次|三餐后|三餐前/.test(task)) {
    return 'three_times_daily'
  }
  if (/早晚各一次|早晚一次/.test(task)) {
    return 'twice_daily'
  }
  if (/每日四次|一天四次|一日四次/.test(task)) {
    return 'four_times_daily'
  }
  if (/每日三次|一天三次|一日三次/.test(task)) {
    return 'three_times_daily'
  }
  if (/每日两次|一天两次|一日两次|早晚各一次/.test(task)) {
    return 'twice_daily'
  }
  if (/隔日|隔天/.test(task)) {
    return 'every_other_day'
  }
  if (/每周|每星期|工作日|周末|周[一二三四五六日天]/.test(task)) {
    return 'weekly'
  }
  if (/自定义/.test(task)) {
    return 'custom'
  }
  if (/每天|每日/.test(task)) {
    return 'daily'
  }
  return ''
}

function parseMealTiming(task: string): string {
  if (/睡前半小时|睡前/.test(task)) {
    return 'before_bed'
  }
  if (/早晚饭前各一次|早晚餐前各一次/.test(task)) {
    return 'before_meal'
  }
  if (/早晚饭后各一次|早晚餐后各一次/.test(task)) {
    return 'after_meal'
  }
  if (/早中晚饭前各一次|早中晚餐前各一次/.test(task)) {
    return 'before_meal'
  }
  if (/早中晚饭后各一次|早中晚餐后各一次/.test(task)) {
    return 'after_meal'
  }
  if (/早餐后半小时|早饭后半小时/.test(task)) {
    return 'after_meal'
  }
  if (/早餐前半小时|早饭前半小时|早餐前|早饭前/.test(task)) {
    return 'before_breakfast'
  }
  if (/饭后(?:1|一)小时|餐后(?:1|一)小时/.test(task)) {
    return 'after_meal'
  }
  if (/晚饭后半小时|晚餐后半小时|晚饭后|晚餐后/.test(task)) {
    return 'after_dinner'
  }
  if (/餐前|饭前/.test(task)) {
    return 'before_meal'
  }
  if (/餐中|随餐/.test(task)) {
    return 'with_meal'
  }
  if (/餐后|饭后/.test(task)) {
    return 'after_meal'
  }
  if (/任意时间|随时/.test(task)) {
    return 'anytime'
  }
  return ''
}

function parseSpecialInstructions(task: string): string {
  const instructions: string[] = []
  const explicitInstruction = task.match(/(?:备注|说明|注意(?:事项)?)[：: ]?(.+)$/)?.[1]?.trim()

  if (explicitInstruction) {
    instructions.push(explicitInstruction)
  }

  for (const pattern of [
    /(必要时服用|必要时使用|按需服用|按需使用)/,
    /(饭后(?:1|一)小时|餐后(?:1|一)小时)/,
  ]) {
    const matched = task.match(pattern)?.[1]
    if (matched && !instructions.includes(matched)) {
      instructions.push(matched)
    }
  }

  return instructions.join('；').slice(0, 120)
}

function parseDosage(task: string): { value: string; unit: string } | null {
  const dosageMatch = task.match(
    /(\d+(?:\.\d+)?|[一二两三四五六七八九十半])\s*(片|粒|毫升|ml|ML|毫克|mg|MG|克|g|G|滴|喷|贴|针)/
  )
  if (!dosageMatch) {
    return null
  }

  const rawValue = dosageMatch[1]
  const unit = DOSAGE_UNIT_MAP[dosageMatch[2]]
  const numericValue = /^\d/.test(rawValue) ? Number(rawValue) : parseChineseNumber(rawValue)
  if (!unit) {
    return null
  }
  if (!Number.isFinite(numericValue) || numericValue <= 0) {
    return null
  }

  return {
    value: Number.isInteger(numericValue) ? String(numericValue) : String(numericValue),
    unit,
  }
}

export function buildReminderDraftPayload(
  task: string,
  startDate: string
): ReminderDraftPayload | null {
  const normalized = normalizeTaskText(task)
  if (!/(提醒|用药提醒)/.test(normalized)) {
    return null
  }
  if (!/(创建|新建|生成|填写|填好|准备|新增|添加|草稿)/.test(normalized)) {
    return null
  }

  const medicineName = extractMedicineName(task)
  const reminderTimes = parseReminderTimes(normalized)
  const weekdays = parseReminderWeekdays(normalized)
  const explicitFrequency = parseReminderFrequency(normalized)
  const frequency =
    weekdays.length > 0 || reminderTimes.length > 1 ? 'custom' : explicitFrequency || 'daily'
  const mealTiming = parseMealTiming(normalized) || 'after_meal'
  const dosage = parseDosage(normalized)
  const endDate = /长期|长期服用/.test(normalized)
    ? ''
    : parseReminderEndDate(normalized, startDate)
  const query: Record<string, string> = {
    source: 'page-agent',
    start_date: startDate,
    frequency,
    meal_timing: mealTiming,
  }
  const summary: string[] = []

  if (medicineName) {
    query.medicine_name = medicineName
    summary.push(`药品：${medicineName}`)
  }
  if (dosage) {
    query.dosage = dosage.value
    query.dosage_unit = dosage.unit
    summary.push(`剂量：${dosage.value}${DOSAGE_UNIT_LABELS[dosage.unit] || dosage.unit}`)
  }
  if (reminderTimes.length === 1) {
    query.reminder_time = reminderTimes[0]
    summary.push(`时间：${reminderTimes[0]}`)
  }
  if (reminderTimes.length > 1) {
    query.custom_times = reminderTimes.join(',')
    query.reminder_time = reminderTimes[0]
    summary.push(`时间：${reminderTimes.join('、')}`)
  }

  summary.push(`频率：${FREQUENCY_LABELS[frequency] || frequency}`)
  summary.push(`时机：${MEAL_TIMING_LABELS[mealTiming] || mealTiming}`)

  if (weekdays.length > 0) {
    query.weekdays = weekdays.join(',')
    summary.push(`重复日：${formatWeekdays(weekdays)}`)
  }

  if (/长期|长期服用/.test(normalized)) {
    query.no_end_date = '1'
    summary.push('有效期：长期')
  } else if (endDate) {
    query.end_date = endDate
    summary.push(`结束日期：${endDate}`)
  }

  const specialInstructions = parseSpecialInstructions(task)
  if (specialInstructions) {
    query.special_instructions = specialInstructions
    summary.push(`说明：${query.special_instructions}`)
  }

  return {
    query,
    summary,
  }
}

function normalizeDateValue(raw: string): string {
  const trimmed = raw.trim()
  if (!trimmed) {
    return ''
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed
  }

  const match = trimmed.match(/^(\d{4})[年/.-](\d{1,2})[月/.-](\d{1,2})日?$/)
  if (!match) {
    return ''
  }

  const [, year, month, day] = match
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}

function parseRelativeDateValue(raw: string, today: string): string {
  if (!raw) {
    return ''
  }

  if (raw === '今天' || raw === '今日') {
    return today
  }
  if (raw === '昨天') {
    return addDays(today, -1)
  }
  if (raw === '前天') {
    return addDays(today, -2)
  }
  if (raw === '明天') {
    return addDays(today, 1)
  }
  if (raw === '后天') {
    return addDays(today, 2)
  }

  return normalizeDateValue(raw)
}

function parseMedicineType(task: string): string {
  if (/胶囊|粒/.test(task)) {
    return 'capsule'
  }
  if (/口服液|糖浆|混悬液|液体|毫升|ml|ML/.test(task)) {
    return 'liquid'
  }
  if (/注射|针剂|安瓿|支/.test(task)) {
    return 'injection'
  }
  if (/软膏|乳膏|药膏/.test(task)) {
    return 'ointment'
  }
  if (/滴眼液|滴耳液|滴鼻液|滴剂|滴/.test(task)) {
    return 'drops'
  }
  if (/片剂|药片|片/.test(task)) {
    return 'tablet'
  }
  if (/其他|器械|耗材/.test(task)) {
    return 'other'
  }
  return ''
}

function parseMedicineTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    tablet: '片剂',
    capsule: '胶囊',
    liquid: '液体',
    injection: '注射剂',
    ointment: '软膏',
    drops: '滴剂',
    other: '其他',
  }
  return labels[type] || type
}

function parseMedicineDraftName(task: string): string {
  const candidates = [
    task.match(/(?:药品名称|药物名称|名称)[：: ]?([一-龥A-Za-z0-9·()（）-]{2,32})/)?.[1],
    task.match(
      /(?:添加|新增|新建|创建|登记|录入)\s*(?:一个|一条)?\s*(?:药品|药物|药)?[：:，, ]*([一-龥A-Za-z0-9·()（）-]{2,32})/
    )?.[1],
    task.match(
      /(?:添加|新增|新建|创建|登记|录入)\s*([^，。；,]{2,32}?)(?:到药品|到药物|到库存|入库|药品|药物|库存|表单|草稿|，|。|；|,|$)/
    )?.[1],
    task.match(
      /(?:把|将)\s*([^，。；,]{2,32}?)(?:加入药品|加入药物|加入库存|记录为药品|记录为药物)/
    )?.[1],
    task.match(/([^，。；,]{2,32}?)(?=\d+(?:盒|瓶|支|片|粒|包|袋|贴))/)?.[1],
  ]

  for (const candidate of candidates) {
    const normalized = sanitizeMedicineName(
      (candidate || '')
        .replace(/\s+/g, '')
        .replace(/^(药品|药物|药)[：:，,]*/, '')
        .replace(/(药品|药物|库存|表单|草稿|提醒)$/g, '')
    ).slice(0, 40)
    if (normalized.length >= 2) {
      return normalized
    }
  }

  return ''
}

function parseQuantityValue(task: string): string {
  const quantityMatches = Array.from(
    task.matchAll(/(\d+(?:\.\d+)?)\s*(盒|瓶|支|片|粒|包|袋|贴|个|毫升|ml|ML)/g)
  )
  for (const match of quantityMatches) {
    const start = match.index ?? 0
    const prevChar = start > 0 ? task[start - 1] : ''
    const prefix = task.slice(Math.max(0, start - 4), start)
    if (/[A-Za-z0-9]/.test(prevChar)) {
      continue
    }
    if (/(一次|每次)$/.test(prefix)) {
      continue
    }
    return match[1]
  }

  const stockMatch = task.match(/(?:库存|剩余|数量|备货)\s*(\d+(?:\.\d+)?)/)
  if (stockMatch) {
    return stockMatch[1]
  }

  return ''
}

function parseMedicineDraftNameFallback(task: string): string {
  const match = task.match(
    /(?:\u6dfb\u52a0|\u65b0\u589e|\u65b0\u5efa|\u521b\u5efa)\s*(?:\u4e00\u4e2a|\u4e00\u79cd)?\s*(?:\u65b0\u836f|\u836f\u54c1|\u836f\u7269)?[\uFF0C,\s]*([\u4e00-\u9fa5A-Za-z0-9()（）-]{2,32})/
  )
  return (match?.[1] || '').trim().slice(0, 40)
}

function parseQuantityValueFallback(task: string): string {
  const packageMatch = task.match(
    /(\d+(?:\.\d+)?)\s*(?:\u76d2|\u74f6|\u652f|\u7247|\u7c92|\u5305|\u888b)(?!\s*(?:\/|\u6bcf\u5929|\u6bcf\u65e5|\u4e00\u6b21|\u6bcf\u6b21))/
  )
  return packageMatch?.[1] || ''
}

function parseMedicineSpecificationFallback(task: string): string {
  const match = task.match(
    /(\d+(?:\.\d+)?)\s*(?:\u6beb\u514b|mg|MG|\u514b|g|G|\u6beb\u5347|ml|ML)/
  )
  return (match?.[0] || '').trim().slice(0, 60)
}

function parseMedicineUsageDescription(task: string): string {
  const frequencyMatch = task.match(
    /(?:\u6bcf\u5929|\u6bcf\u65e5)\s*(\d+(?:\.\d+)?|[\u4e00\u4e8c\u4e24\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u534a]+)\s*\u6b21/
  )
  const doseMatch = task.match(
    /(?:\u4e00\u6b21|\u6bcf\u6b21)\s*(\d+(?:\.\d+)?|[\u4e00\u4e8c\u4e24\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u534a]+)\s*(?:\u7247|\u7c92|\u6beb\u5347|ml|ML|\u6beb\u514b|mg|MG|\u514b|g|G|\u6ef4|\u55b7|\u8d34|\u9488)/
  )
  const segments: string[] = []
  if (frequencyMatch?.[0]) {
    segments.push(frequencyMatch[0].replace(/\s+/g, ''))
  }
  if (doseMatch?.[0]) {
    segments.push(doseMatch[0].replace(/\s+/g, ''))
  }
  if (segments.length === 0) {
    return ''
  }
  return `\u7528\u6cd5\u7528\u91cf\uFF1A${segments.join('\uFF1B')}`.slice(0, 120)
}

function isGenericMedicineDraftName(name: string): boolean {
  return /^(?:\u65b0\u836f|\u836f\u54c1|\u836f\u7269)$/.test(name.trim())
}

export function buildMedicineDraftPayload(
  task: string,
  today: string
): PageAgentDraftPayload | null {
  const normalized = normalizeTaskText(task)
  const isMedicinePage =
    typeof window !== 'undefined' && /^\/medicines(?:\/|$)/.test(window.location.pathname)
  const hasMedicineKeyword = /(药品|药物|库存|药盒|胶囊|片剂|口服液|注射剂|软膏|滴剂)/.test(
    normalized
  )
  const hasMedicineSignal = /(?:\u65b0\u836f|\u836f\u7247|\u6beb\u514b|mg|MG|\u53e3\u670d\u6db2|\u6ce8\u5c04\u5242)/.test(normalized)
  if (!hasMedicineKeyword && !hasMedicineSignal && !isMedicinePage) {
    return null
  }
  if (!/(创建|新建|新增|添加|登记|录入|填写|准备|草稿|补充)/.test(normalized)) {
    return null
  }

  const query: Record<string, string> = {
    source: 'page-agent',
    open_dialog: '1',
  }
  const summary: string[] = []

  const parsedMedicineName = parseMedicineDraftName(task)
  const medicineName =
    parsedMedicineName && !isGenericMedicineDraftName(parsedMedicineName)
      ? parsedMedicineName
      : parseMedicineDraftNameFallback(task)
  if (medicineName) {
    query.name = medicineName
    summary.push(`药品名称：${medicineName}`)
  }

  const medicineType = parseMedicineType(task)
  if (medicineType) {
    query.medicine_type = medicineType
    summary.push(`药品类型：${parseMedicineTypeLabel(medicineType)}`)
  }

  const quantity = parseQuantityValue(task) || parseQuantityValueFallback(task)
  if (quantity) {
    query.quantity = quantity
    summary.push(`库存数量：${quantity}`)
  }

  const specification = task.match(/(?:规格|规格是|规格为)[：: ]?([^，。；,]+)/)?.[1]?.trim()
  if (specification) {
    query.specification = specification.slice(0, 60)
    summary.push(`规格：${query.specification}`)
  }

  const manufacturer =
    task.match(/(?:厂家|厂商|生产厂商|生产厂家)[：: ]?([^，。；,]+)/)?.[1]?.trim() ||
    task.match(/([^，。；,]{2,30}?)(?:生产|出品)/)?.[1]?.trim()
  if (manufacturer) {
    query.manufacturer = manufacturer.slice(0, 60)
    summary.push(`生产厂商：${query.manufacturer}`)
  }

  const purchasePrice = task.match(/(?:价格|采购价|采购价格|单价)[：: ]?(\d+(?:\.\d+)?)/)?.[1]
  if (purchasePrice) {
    query.purchase_price = purchasePrice
    summary.push(`采购价格：${purchasePrice}元`)
  }

  const purchaseDateMatch = task.match(
    /(?:采购日期|购买日期|买于|购于|今天|今日|昨天|前天|明天|后天|于)(今天|今日|昨天|前天|明天|后天|\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?|\d{4}-\d{2}-\d{2})/
  )
  const purchaseDate = parseRelativeDateValue(purchaseDateMatch?.[1] ?? '', today) || today
  if (purchaseDate) {
    query.purchase_date = purchaseDate
    summary.push(`采购日期：${purchaseDate}`)
  }

  const expiryMatch = task.match(
    /(?:有效期(?:到|至)?|过期时间(?:到|至)?|到期(?:时间|日期)?(?:为|是|到)?)(今天|今日|昨天|前天|明天|后天|\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?|\d{4}-\d{2}-\d{2})/
  )
  const expiryDate = parseRelativeDateValue(expiryMatch?.[1] ?? '', today)
  if (expiryDate) {
    query.expiry_date = expiryDate
    summary.push(`有效期：${expiryDate}`)
  }

  const batchNumber = task.match(/(?:批号|批次)[：: ]?([A-Za-z0-9-]{3,40})/)?.[1]
  if (batchNumber) {
    query.batch_number = batchNumber
    summary.push(`批号：${batchNumber}`)
  }

  const storageConditions = task.match(/(?:保存条件|存储条件|储存条件)[：: ]?([^，。；,]+)/)?.[1]?.trim()
  if (storageConditions) {
    query.storage_conditions = storageConditions.slice(0, 80)
    summary.push(`存储条件：${query.storage_conditions}`)
  }

  const description = task.match(/(?:说明|备注|描述)[：: ]?([^。；;]+)/)?.[1]?.trim()
  if (description) {
    query.description = description.slice(0, 120)
    summary.push(`说明：${query.description}`)
  }

  if (/处方药/.test(task)) {
    query.is_prescription = '1'
    summary.push('分类：处方药')
  } else if (/非处方药|OTC|otc/.test(task)) {
    query.is_prescription = '0'
    summary.push('分类：非处方药')
  }

  if (!query.specification) {
    const specificationFallback = parseMedicineSpecificationFallback(task)
    if (specificationFallback) {
      query.specification = specificationFallback
      summary.push(`规格：${query.specification}`)
    }
  }

  if (!query.description) {
    const usageDescription = parseMedicineUsageDescription(task)
    if (usageDescription) {
      query.description = usageDescription
      summary.push(`说明：${query.description}`)
    }
  }

  if (!query.name && !query.quantity && !query.specification && !query.manufacturer) {
    return null
  }

  return {
    query,
    summary,
  }
}
