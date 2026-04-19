with open("README.md", "r") as f:
    content = f.read()

# Replace the AI section
old_ai = """### 2. 🤖 AI 智能体管家 (AI Copilot)
基于 Baichuan M3 大模型集成的全局悬浮式页面助手：
- **用药问答**：随时解答用户的药品适应症、禁忌、相互作用等疑问。
- **智能引导**：针对不同角色（药师/患者），在首次进入仪表板时主动弹出并进行自然语言引导。
- **语音交互 (TTS & STT)**：完全打通了全局语音播报（TTS）与语音识别（STT）。老年人只需点击麦克风说话，AI 的回复也会自动通过语音播报，实现真正的“零打字”适老化交互。"""

new_ai = """### 2. 🤖 AI 智能体管家 (AI Copilot)
基于大模型集成的全局悬浮式页面助手（支持公网 API 与内网本地模型）：
- **用药问答**：随时解答用户的药品适应症、禁忌、相互作用等疑问。
- **智能引导**：针对不同角色（药师/患者），在首次进入仪表板时主动弹出并进行自然语言引导。
- **语音交互 (TTS & STT)**：完全打通了全局语音播报（TTS）与语音识别（STT）。老年人只需点击麦克风说话，AI 的回复也会自动通过系统原生的语音引擎播报，实现真正的“零打字”适老化交互。"""

# Insert Offline section
offline_section = """
### 6. 🛡️ 私有化与离线环境支持 (Air-gapped 友好)
系统在架构设计上充分考虑了外部网络依赖的“优雅降级”，支持在物理隔离的内网环境中完全离线运行：
- **本地 LLM 接入**：后端代码兼容标准的 OpenAI 接口规范，只需在 `.env` 中将 `BAICHUAN_M3_API_BASE_URL` 指向局域网内使用 Ollama、vLLM 等部署的开源大模型（如 Qwen2-7B），即可实现完全离线的 AI 对话与药历生成，确保敏感医疗数据不出网。
- **本地语音播报**：TTS (Text-to-Speech) 模块调用的是浏览器底层的 Web Speech API，直接利用操作系统的本地语音合成引擎发声，**不依赖任何外部云端 API**。
- **断网提醒兜底**：当内网环境无法连接 Apple APNs 或 Google FCM 导致 PWA 消息推送失败时，前端独创的“离线轮询机制”会接管提醒功能，在服药时间点直接通过浏览器本地弹窗与 TTS 语音大声提醒患者。
"""

content = content.replace(old_ai, new_ai)
content = content.replace("### 5. 🏥 基础药品与数据管理\n- 支持药品信息快速录入与管理。\n- 动态服药历史记录追踪，生成用药依从性（Adherence）统计与可视化图表。", "### 5. 🏥 基础药品与数据管理\n- 支持药品信息快速录入与管理。\n- 动态服药历史记录追踪，生成用药依从性（Adherence）统计与可视化图表。\n" + offline_section)

with open("README.md", "w") as f:
    f.write(content)
