with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

btn_group_old = """          <div class="flex flex-wrap items-center gap-3 self-start">
            <button
              v-if="serviceCase?.status === 'completed'"
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-violet-700 shadow-sm ring-1 ring-inset ring-violet-200 transition hover:bg-violet-50"
              @click="goToReport"
            >
              <FileText class="h-4 w-4" />
              查看专业报告 (PMR/MAP)
            </button>"""

btn_group_new = """          <div class="flex flex-wrap items-center gap-3 self-start">
            <button
              v-if="serviceCase?.status === 'completed' || serviceCase?.status === 'intervening' || serviceCase?.status === 'following_up'"
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-amber-700 shadow-sm ring-1 ring-inset ring-amber-200 transition hover:bg-amber-50"
              @click="goToSoapNotes"
            >
              <Sparkles class="h-4 w-4" />
              撰写/查看 SOAP 药历
            </button>
            <button
              v-if="serviceCase?.status === 'completed'"
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-violet-700 shadow-sm ring-1 ring-inset ring-violet-200 transition hover:bg-violet-50"
              @click="goToReport"
            >
              <FileText class="h-4 w-4" />
              查看专业报告 (PMR/MAP)
            </button>"""

if "撰写/查看 SOAP" not in content:
    content = content.replace(btn_group_old, btn_group_new)
    
    if "Sparkles," not in content:
        content = content.replace("RefreshCw,", "RefreshCw,\n  Sparkles,")
        
    script_add = """
const goToSoapNotes = () => {
  if (!serviceCase.value) return
  router.push({
    name: 'MtmSoapNotes',
    params: { id: serviceCase.value.id.toString() },
  })
}
"""
    content = content.replace("const goToReport = () => {", script_add + "\nconst goToReport = () => {")
    
    with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
        f.write(content)
