with open("src/router/index.ts", "r") as f:
    content = f.read()

import re

if "MtmReportPreviewPage" not in content:
    content = content.replace(
        "const MtmPlanFormPage = () => import('@/pages/MtmPlanFormPage.vue')",
        "const MtmPlanFormPage = () => import('@/pages/MtmPlanFormPage.vue')\nconst MtmReportPreviewPage = () => import('@/pages/MtmReportPreviewPage.vue')"
    )
    
    route_addition = """
  {
    path: '/mtm/service-cases/:id/report',
    name: 'MtmReportPreview',
    component: MtmReportPreviewPage,
    meta: { requiresAuth: true },
    props: true,
  },"""
    
    content = content.replace(
        "    path: '/medicines',",
        "    path: '/medicines'," + route_addition + "\n  {\n    path: '/dummy',"
    )
    
    # fix the dummy path
    content = content.replace("    path: '/medicines',\n  {\n    path: '/dummy',", route_addition + "\n  {\n    path: '/medicines',")
    
    with open("src/router/index.ts", "w") as f:
        f.write(content)
