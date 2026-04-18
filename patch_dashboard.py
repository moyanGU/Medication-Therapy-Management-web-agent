import re

with open("src/pages/DashboardPage.vue", "r") as f:
    content = f.read()

# Check if router is already imported
if "import { useRouter } from 'vue-router'" not in content:
    content = content.replace("import { useAuthStore } from '@/stores/auth'", "import { useAuthStore } from '@/stores/auth'\nimport { useRouter, useRoute } from 'vue-router'")

# Add router setup
if "const router = useRouter()" not in content:
    content = content.replace("const authStore = useAuthStore()", "const authStore = useAuthStore()\nconst router = useRouter()\nconst route = useRoute()")


guide_code = """
// Check if we should trigger the proactive guide
const checkProactiveGuide = () => {
  // Use localStorage to only guide once per device/browser
  const hasGuided = localStorage.getItem('mtm_proactive_guide_done')
  
  // Also check if we are already opening it from url to avoid loops
  if (route.query.assistant === 'open') return
  
  if (!hasGuided && !loading.value) {
    localStorage.setItem('mtm_proactive_guide_done', 'true')
    
    // Add a small delay to let the user see the dashboard first
    setTimeout(() => {
      let task = ''
      if (isPharmacist.value) {
        task = '您好！我是您的 AI 助理。这里是 MTM 工作台。您可以从【服务单】开始接单，并进行患者的五维用药评估，随后我会协助您一键生成 SOAP 药历和 PMR/MAP 报告。有什么我可以帮您的吗？'
      } else {
        task = '爷爷奶奶您好！我是您的专属用药助手。看您有很多药要吃，别担心，我会按时提醒您。您可以先去【用药记录】添加您正在吃的药，或者直接对我说“我要添加药品”哦。'
      }
      
      // Trigger the AiAssistant via route query
      router.replace({
        query: {
          ...route.query,
          assistant: 'open',
          assistantMode: 'page-agent',
          assistantTask: task
        }
      })
    }, 1500)
  }
}
"""

if "const checkProactiveGuide" not in content:
    content = content.replace("onMounted(() => {", guide_code + "\n\nonMounted(() => {")
    content = content.replace("fetchMtmServiceCases()", "fetchMtmServiceCases()\n  checkProactiveGuide()")

with open("src/pages/DashboardPage.vue", "w") as f:
    f.write(content)
