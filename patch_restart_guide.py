with open("src/pages/DashboardPage.vue", "r") as f:
    content = f.read()

# 1. Add "Restart Guide" button to the welcome section
old_buttons = """            <span
              class="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-sm text-white"
            >
              今日待处理 {{ dashboard.today_tasks.pending }} 项
            </span>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-sky-700 shadow-sm transition hover:bg-sky-50"
              :disabled="loading"
              @click="fetchDashboardSummary"
            >
              <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
              刷新首页
            </button>"""

new_buttons = """            <span
              class="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-sm text-white"
            >
              今日待处理 {{ dashboard.today_tasks.pending }} 项
            </span>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white/20 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-white/30 backdrop-blur-sm"
              @click="restartGuide"
            >
              <Sparkles class="h-4 w-4" />
              重启 AI 向导
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-sky-700 shadow-sm transition hover:bg-sky-50"
              :disabled="loading"
              @click="fetchDashboardSummary"
            >
              <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
              刷新首页
            </button>"""

content = content.replace(old_buttons, new_buttons)

# 2. Add Sparkles to imports
if "Sparkles," not in content:
    content = content.replace("Stethoscope,", "Stethoscope,\n  Sparkles,")

# 3. Add restartGuide function
restart_func = """
// Restart the proactive guide with a confirmation prompt
const restartGuide = () => {
  if (confirm('是否需要让 AI 机器人重新为您介绍一次系统功能？')) {
    localStorage.removeItem('mtm_proactive_guide_done')
    checkProactiveGuide()
  }
}
"""

content = content.replace("const checkProactiveGuide = () => {", restart_func + "\n// Check if we should trigger the proactive guide\nconst checkProactiveGuide = () => {")

with open("src/pages/DashboardPage.vue", "w") as f:
    f.write(content)
