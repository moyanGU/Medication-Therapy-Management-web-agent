<div align="center">
  <img src="public/images/mtm-cover-logo.svg" alt="MTM-Helper Logo" width="120" height="120" />
  <h1>💊 MTM-Helper 3.0：基于 Agent 架构的智能用药生态池</h1>
  <p>一个以“龙虾（AI Agent）与养虾池（业务底座）”为核心架构理念的双轨制药物治疗管理平台</p>
</div>

## 📖 项目定位：从“套壳 LLM”到“Agent 生态”

MTM-Helper 3.0 是一次彻底的架构蜕变。我们摒弃了传统的“对话框式”大模型接入，将 AI 拆解为多个具备感知、分析、行动能力的领域专家（Sub-Agents），并将它们无缝植入到真实的医疗业务流水线中。
- **面向大众用户**：提供用药打卡、过期预警、语音播报等日常健康守护（链路A）。
- **面向专业药师**：提供全流程的 MTM（药物治疗管理）服务，包括自动问诊、五维度评估、SOAP 药历生成与 PMR/MAP 医疗文书导出（链路B）。

---

## ✨ 3.0 架构核心特性 (The "Lobster" Engine)

### 1. 🦞 多领域子代理集群 (Sub-Agent Orchestration)
不再依赖臃肿的单一 Prompt。我们将 MTM 业务流拆解，在后端实现了专职的 `BaseAgent` 专家群：
- **`MedicationAgent`**：专攻药物相互作用、禁忌症与五维度适宜性评估。
- **`SoapAgent`**：负责将离散的问诊和评估数据，自动聚合为医疗标准的 SOAP 药历。
- **`MemoryAgent`**：负责提取、压缩和持久化患者的长期记忆。

### 2. 🌊 跨路由上下文串联 (Cross-Route Context Reasoning)
彻底治愈 AI 的“页面失忆症”。前端 `assistantEngine.ts` 与 Vue Router 深度绑定，当用户在 MTM 列表页进行筛选、排序或进入详情页时，系统会实时将这些环境数据捕获为 `globalContextMemory`。AI 的感知触角真正扎入了业务流的活水中。

### 3. ⚡ 流式输出与步骤回显 (Streaming & Steps)
从阻塞式 API 全面升级为基于 Server-Sent Events (SSE) 的 NDJSON 块流式传输。结合前端的 `onStep` 钩子，AI “思考、调用、生成”的每一步都在用户面前透明回显，彻底消除等待焦虑。

### 4. 🔊 适老化与无障碍原生支持 (Elderly-Friendly)
- **全局语音交互 (TTS & STT)**：前端原生打通 Web Speech API。用户说话即可提问，系统原生语音播报回复，实现真正的“零打字”。
- **高对比度大字模式**：遵循 WCAG 标准，专为老年人与视障人群设计。

### 5. 🛡️ 离线优先与 Air-gapped 部署
专为医院内网与数据敏感场景设计：
- **大模型私有化接入**：完全兼容 OpenAI 接口规范，一键接入本地部署的 Ollama / vLLM（如 Qwen2-7B、百川医疗大模型）。
- **纯本地 TTS/STT**：语音合成不依赖云端 API。
- **离线轮询兜底**：当 APNs/FCM 消息推送因断网失败时，前端 Service Worker 配合本地轮询触发浏览器原生弹窗提醒。

---

## 🛠 技术栈 (Tech Stack)

**前端生态 (Frontend)**
- Vue 3.4+ (Composition API) + TypeScript 5.0+ + Vite 5.0+
- 状态管理：Pinia + Vue Router
- 流式解析：Fetch API + TextDecoder (原生支持 SSE 规范)
- 样式组件：TailwindCSS 3.4+ + Lucide Icons
- 文书渲染：jspdf + html2canvas

**后端生态 (Backend)**
- 框架：Django 4.2+ & Django REST Framework (DRF)
- Agent 调度：纯 Python 原生生成器 (`yield`) 实现非阻塞流式编排
- 数据库：MySQL 8.0+ (核心业务) & Redis 7.0+ (缓存与 Celery 任务队列)

---

## 🚀 开发者指南 (Quick Start)

### 环境依赖
- Node.js 20.0+
- Python 3.11+
- MySQL 8.0+ / Redis 7.0+ (推荐使用 Docker 部署基础设施)

### 1. 前端服务启动
```bash
# 1. 安装依赖并排除冲突的三方子模块
npm install

# 2. 启动 Vite 开发服务器 (已配置 host 暴露与依赖优化)
npm run dev
```

### 2. 后端服务启动
```bash
cd backend
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows 运行 .\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库配置
cp .env.example .env
# 必须在 .env 中配置 DB 连接和 BAICHUAN_M3_API_KEY (或本地模型 URL)

# 4. 迁移与启动
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3. Docker 生产级部署 (Production)
项目内置了生产级部署方案（涵盖 Nginx 反代与静态资源挂载）：
```bash
docker compose -f docker-compose.production.yml up -d --build
```

---

## 🤝 参与贡献
MTM-Helper 目前处于 Phase 3（AI 深度增强）冲刺阶段，正在探索基于 MCP (Model Context Protocol) 的工具链解耦。
欢迎对**医疗 Agent 架构**、**适老化设计**感兴趣的开发者提交 PR 或 Issue。

## 📄 许可证
本项目基于 [MIT License](LICENSE) 开源。

---
*MTM-Helper — 科技让关爱更智能。*
