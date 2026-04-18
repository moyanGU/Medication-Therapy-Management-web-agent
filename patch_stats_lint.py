with open("src/pages/RecordStatsPage.vue", "r") as f:
    content = f.read()

content = content.replace("  MedicationAdherenceTrendItem,\n", "")

with open("src/pages/RecordStatsPage.vue", "w") as f:
    f.write(content)
