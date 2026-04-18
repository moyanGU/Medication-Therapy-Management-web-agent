with open("src/router/index.ts", "r") as f:
    content = f.read()

content = content.replace(
    "const MtmAssessmentFormPage = () => import('@/pages/MtmAssessmentFormPage.vue')",
    "const MtmAssessmentFormPage = () => import('@/pages/MtmAssessmentFormPage.vue')\nconst MtmPlanFormPage = () => import('@/pages/MtmPlanFormPage.vue')"
)

with open("src/router/index.ts", "w") as f:
    f.write(content)
