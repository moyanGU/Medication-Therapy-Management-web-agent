with open("src/router/index.ts", "r") as f:
    content = f.read()

if "MtmSoapNotesPage" not in content:
    content = content.replace(
        "const MtmReportPreviewPage = () => import('@/pages/MtmReportPreviewPage.vue')",
        "const MtmReportPreviewPage = () => import('@/pages/MtmReportPreviewPage.vue')\nconst MtmSoapNotesPage = () => import('@/pages/MtmSoapNotesPage.vue')"
    )
    
    route_addition = """
  {
    path: '/mtm/service-cases/:id/soap',
    name: 'MtmSoapNotes',
    component: MtmSoapNotesPage,
    meta: { requiresAuth: true },
    props: true,
  },"""
    
    content = content.replace(
        "    path: '/medicines',",
        "    path: '/medicines'," + route_addition + "\n  {\n    path: '/dummy',"
    )
    
    content = content.replace("    path: '/medicines',\n  {\n    path: '/dummy',", route_addition + "\n  {\n    path: '/medicines',")
    
    with open("src/router/index.ts", "w") as f:
        f.write(content)
