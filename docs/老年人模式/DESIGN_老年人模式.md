# 老年人模式 - 设计文档

## 总体架构（Mermaid）
```mermaid
flowchart TD
  A[用户交互] --> B[AppHeader 开关]
  A --> C[SettingsPage 开关]
  B --> D[useTheme composable]
  C --> D
  D --> E[localStorage: seniorMode]
  D --> F[document.documentElement.classList.toggle('senior')]
  F --> G[全局样式 style.css]
```

## 分层与模块
- 视图层：AppHeader.vue、SettingsPage.vue
- 逻辑层：useTheme.ts（新增老年人模式状态与应用逻辑）
- 样式层：style.css（`.senior` 根选择器，覆盖文本对比、点击目标、焦点样式等）

## 接口契约
- 前端本地存储键：`seniorMode`（string: 'true' | 'false'）
- 公开方法：
  - `useTheme().isSenior: Ref<boolean>`
  - `useTheme().toggleSenior(): void`
  - 主题相关原有方法保持不变

## 数据流向
1. 用户点击开关（Header / Settings）
2. 调用 `toggleSenior()` 更新状态
3. watchEffect 中应用 `.senior` 类到 html 根元素，并持久化到 localStorage
4. 样式层根据 `.senior` 启用增强样式

## 异常处理策略
- 状态应用时打印日志；出现异常时不中断页面渲染，仅回退为普通模式。
- 选择器与样式尽可能使用保守覆盖（!important 仅对于文本灰度增强使用），避免破坏原布局。