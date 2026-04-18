with open("src/pages/DashboardPage.vue", "r") as f:
    content = f.read()

bad = """    await Promise.all([fetchMtmServiceCases()
  checkProactiveGuide(), fetchDashboardSummary()])"""

good = """    await Promise.all([fetchMtmServiceCases(), fetchDashboardSummary()])"""

content = content.replace(bad, good)
with open("src/pages/DashboardPage.vue", "w") as f:
    f.write(content)
