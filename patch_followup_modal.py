import re

with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

# 1. Import
if "import MtmFollowUpModal from '@/components/mtm/MtmFollowUpModal.vue'" not in content:
    content = content.replace(
        "import { useToast } from '@/composables/useToast'",
        "import { useToast } from '@/composables/useToast'\nimport MtmFollowUpModal from '@/components/mtm/MtmFollowUpModal.vue'"
    )

# 2. Add refs
if "showFollowUpModal" not in content:
    content = content.replace(
        "const loadError = ref('')",
        "const loadError = ref('')\nconst showFollowUpModal = ref(false)"
    )

# 3. Add to UI
ui_to_replace = """          <div class="flex items-center gap-2">
            <CalendarClock class="h-5 w-5 text-indigo-600" />
            <h2 class="text-lg font-semibold text-slate-900">随访记录</h2>
          </div>"""
          
new_ui = """          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-2">
              <CalendarClock class="h-5 w-5 text-indigo-600" />
              <h2 class="text-lg font-semibold text-slate-900">随访记录</h2>
            </div>
            <button
              type="button"
              class="inline-flex items-center gap-2 self-start rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300"
              :disabled="loading || transitioning"
              @click="showFollowUpModal = true"
            >
              <span class="h-4 w-4 flex items-center justify-center font-bold text-lg leading-none">+</span>
              新增随访记录
            </button>
          </div>"""

content = content.replace(ui_to_replace, new_ui)

# 4. Add the modal at the end of the template
modal_tag = """
    </main>
    <MtmFollowUpModal
      v-model="showFollowUpModal"
      :service-case-id="serviceCaseId"
      @success="fetchServiceCaseDetail"
    />
  </div>
</template>"""

content = content.replace("    </main>\n  </div>\n</template>", modal_tag)

with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
    f.write(content)
