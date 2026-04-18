with open("src/router/index.ts", "r") as f:
    content = f.read()

bad_str = """  },
  {
    path: '/medicines',
  {
    path: '/mtm/service-cases/:id/report',
    name: 'MtmReportPreview',
    component: MtmReportPreviewPage,
    meta: { requiresAuth: true },
    props: true,
  },"""

good_str = """  },
  {
    path: '/mtm/service-cases/:id/report',
    name: 'MtmReportPreview',
    component: MtmReportPreviewPage,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/medicines',"""

content = content.replace(bad_str, good_str)
with open("src/router/index.ts", "w") as f:
    f.write(content)
