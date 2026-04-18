import re

# Fix src/api/mtm.ts
with open("src/api/mtm.ts", "r") as f:
    content = f.read()

content = content.replace(
    "MtmAssessmentSummary,",
    "MtmAssessmentSummary,\n  MtmPlanSummary,\n  MtmFollowUpSummary,"
)

with open("src/api/mtm.ts", "w") as f:
    f.write(content)

# Fix src/router/index.ts (if MtmPlanFormPage is not imported correctly)
with open("src/router/index.ts", "r") as f:
    router_content = f.read()

if "import MtmPlanFormPage from" not in router_content:
    router_content = router_content.replace(
        "import MtmAssessmentFormPage from '@/pages/MtmAssessmentFormPage.vue'",
        "import MtmAssessmentFormPage from '@/pages/MtmAssessmentFormPage.vue'\nimport MtmPlanFormPage from '@/pages/MtmPlanFormPage.vue'"
    )
    with open("src/router/index.ts", "w") as f:
        f.write(router_content)

