with open("src/pages/DashboardPage.vue", "r") as f:
    content = f.read()

content = content.replace("  DashboardRiskAlert,\n", "")

with open("src/pages/DashboardPage.vue", "w") as f:
    f.write(content)
