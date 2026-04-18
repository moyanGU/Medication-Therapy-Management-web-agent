import re

with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

old_btn = """          <button
            type="button"
            class="inline-flex items-center gap-2 self-start rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
            :disabled="loading || transitioning"
            @click="fetchServiceCaseDetail"
          >
            <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
            刷新详情
          </button>"""

new_btn = """          <div class="flex flex-wrap items-center gap-3 self-start">
            <button
              v-if="serviceCase?.status === 'completed'"
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-violet-700 shadow-sm ring-1 ring-inset ring-violet-200 transition hover:bg-violet-50"
              @click="goToReport"
            >
              <FileText class="h-4 w-4" />
              查看专业报告 (PMR/MAP)
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
              :disabled="loading || transitioning"
              @click="fetchServiceCaseDetail"
            >
              <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
              刷新详情
            </button>
          </div>"""

if "查看专业报告" not in content:
    content = content.replace(old_btn, new_btn)
    
    if "FileText," not in content:
        content = content.replace("ClipboardList,", "ClipboardList,\n  FileText,")
        
    script_add = """
const goToReport = () => {
  if (!serviceCase.value) return
  router.push({
    name: 'MtmReportPreview',
    params: { id: serviceCase.value.id.toString() },
  })
}
"""
    content = content.replace("const goBack = () => {", script_add + "\nconst goBack = () => {")
    
    with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
        f.write(content)
