with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

bad = """
,
  })
}

const goBack = () => {"""

good = """

const goBack = () => {"""

content = content.replace(bad, good)
with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
    f.write(content)
