import re
with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

# remove duplicate goToReport
parts = content.split("const goToReport = () => {")
if len(parts) > 2:
    # it was added twice
    # let's rebuild it manually safely
    new_content = parts[0] + "const goToReport = () => {" + parts[1]
    # strip the second declaration and everything up to the next const/function
    rest = parts[2]
    # find the end of the second declaration
    end_idx = rest.find("}")
    if end_idx != -1:
        # the next character should be a newline
        new_content += rest[end_idx+1:]
    with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
        f.write(new_content)
