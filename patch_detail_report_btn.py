with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

import re

# Add button
old_buttons = """        <div class="mt-4 flex items-center justify-between sm:mt-0">
          <button
            type="button"
            class="inline-flex items-center gap-2 self-start rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
            :disabled="loading || transitioning"
            @click="fetchServiceCaseDetail"
          >
            <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
            刷新详情
          </button>
        </div>"""

new_buttons = """        <div class="mt-4 flex flex-wrap items-center gap-3 sm:mt-0">
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
    content = content.replace(old_buttons, new_buttons)
    
    # Import FileText
    if "FileText," not in content:
        content = content.replace("ClipboardList,", "ClipboardList,\n  FileText,")
        
    # Add goToReport method
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
