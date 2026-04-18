with open("src/components/AiAssistant.vue", "r") as f:
    content = f.read()

bad = """function getQaScenarioFromRoute() {
  if (!import.meta.env.DEV) {
    return null
  }"""

good = """function getQaScenarioFromRoute() {
  // Allow production usage for proactive guiding
  // if (!import.meta.env.DEV) {
  //   return null
  // }"""

content = content.replace(bad, good)
with open("src/components/AiAssistant.vue", "w") as f:
    f.write(content)
