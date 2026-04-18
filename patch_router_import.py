import re

with open("src/router/index.ts", "r") as f:
    content = f.read()

if "import MtmPlanFormPage from" not in content:
    content = content.replace(
        "import MtmAssessmentFormPage from '@/pages/MtmAssessmentFormPage.vue'",
        "import MtmAssessmentFormPage from '@/pages/MtmAssessmentFormPage.vue'\nimport MtmPlanFormPage from '@/pages/MtmPlanFormPage.vue'"
    )
    with open("src/router/index.ts", "w") as f:
        f.write(content)
