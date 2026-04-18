with open("src/router/index.ts", "r") as f:
    content = f.read()

import re
if "MtmPlanFormPage" not in content:
    content = content.replace(
        "import MtmAssessmentFormPage from '@/pages/MtmAssessmentFormPage.vue'",
        "import MtmAssessmentFormPage from '@/pages/MtmAssessmentFormPage.vue'\nimport MtmPlanFormPage from '@/pages/MtmPlanFormPage.vue'"
    )
    
    route_addition = """
  {
    path: '/mtm/service-cases/:id/plan',
    name: 'MtmPlanForm',
    component: MtmPlanFormPage,
    meta: { requiresAuth: true },
    props: true,
  },"""
    
    content = content.replace(
        "    props: true,\n  },\n  {\n    path: '/medicines',",
        "    props: true,\n  }," + route_addition + "\n  {\n    path: '/medicines',"
    )
    
    with open("src/router/index.ts", "w") as f:
        f.write(content)
