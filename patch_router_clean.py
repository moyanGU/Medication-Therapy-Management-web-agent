with open("src/router/index.ts", "r") as f:
    content = f.read()

bad = """  {
    path: '/medicines',
  {
    path: '/dummy',
    name: 'Medicines',
    component: MedicinesPage,"""

good = """  {
    path: '/medicines',
    name: 'Medicines',
    component: MedicinesPage,"""

content = content.replace(bad, good)
with open("src/router/index.ts", "w") as f:
    f.write(content)
