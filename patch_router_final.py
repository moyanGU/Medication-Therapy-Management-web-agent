with open("src/router/index.ts", "r") as f:
    content = f.read()

bad = """  {
    path: '/medicines',
  {
    path: '/mtm/service-cases/:id/soap',
    name: 'MtmSoapNotes',
    component: MtmSoapNotesPage,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/dummy',
    name: 'Medicines',"""

good = """  {
    path: '/mtm/service-cases/:id/soap',
    name: 'MtmSoapNotes',
    component: MtmSoapNotesPage,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/medicines',
    name: 'Medicines',"""

content = content.replace(bad, good)
with open("src/router/index.ts", "w") as f:
    f.write(content)
