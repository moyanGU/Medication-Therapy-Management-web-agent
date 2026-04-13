/**
 * 页面元数据工具：标题与主要作用
 * - 提供 getPageTitle(name) 返回中文标题
 * - 提供 getPagePurpose(name) 返回页面主要作用描述
 * 说明：
 * - 为避免大小写差异造成匹配失败，映射中包含常见大小写变体（login/Login, register/Register）。
 * - 作为单一事实来源，供路由与组件共用，避免重复代码。
 */

/**
 * 根据路由名称返回页面中文标题
 * @param routeName 路由名称（如 'Dashboard'、'login'）
 * @returns 中文标题字符串，如果未匹配则返回空字符串
 */
export function getPageTitle(routeName: string): string {
  const key = String(routeName || '').trim()
  const titleMap: Record<string, string> = {
    Home: '首页',
    Welcome: '欢迎',
    Login: '登录',
    login: '登录',
    Register: '注册',
    register: '注册',
    Dashboard: '仪表板',
    Medicines: '药品管理',
    MedicineDetail: '药品详情',
    Records: '用药记录',
    RecordStats: '用药统计',
    Reminders: '用药提醒',
    ReminderCreate: '新建提醒',
    ReminderDetail: '提醒详情',
    ReminderEdit: '编辑提醒',
    Plans: '用药计划',
    MedicalRecords: '病历管理',
    MedicalRecordCreate: '新增病历',
    MedicalRecordDetail: '病历详情',
    MedicalRecordEdit: '编辑病历',
    MedicalRecordStatistics: '病历统计',
    Settings: '设置',
  }
  return titleMap[key] || ''
}

/**
 * 根据路由名称返回页面主要作用描述
 * @param routeName 路由名称
 * @returns 主要作用中文描述，如果未匹配则返回空字符串
 */
export function getPagePurpose(routeName: string): string {
  const key = String(routeName || '').trim()
  const purposeMap: Record<string, string> = {
    Home: '浏览应用首页并进入相关功能',
    Welcome: '欢迎页与新手引导',
    Login: '用户登录与找回密码',
    login: '用户登录与找回密码',
    Register: '新用户注册与账号创建',
    register: '新用户注册与账号创建',
    Dashboard: '总览用药计划、提醒与统计信息',
    Medicines: '管理药品信息、库存与有效期',
    MedicineDetail: '查看并编辑单个药品详细信息',
    Records: '查看与管理用药记录',
    RecordStats: '查看用药统计与趋势分析',
    Reminders: '管理每日用药提醒与时间点',
    ReminderCreate: '创建新的用药提醒',
    ReminderDetail: '查看某条提醒的详细内容',
    ReminderEdit: '编辑已有的用药提醒',
    Plans: '管理用药计划与长期方案',
    MedicalRecords: '管理病历资料与就诊记录',
    MedicalRecordCreate: '新增病历与就诊条目',
    MedicalRecordDetail: '查看单条病历详情',
    MedicalRecordEdit: '编辑病历记录',
    MedicalRecordStatistics: '查看病历统计与分析',
    Settings: '个人设置与辅助功能开关',
  }
  return purposeMap[key] || ''
}
