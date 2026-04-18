import re

with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

plan_meta_str = """
const planEntryMeta = computed(() => {
  const currentAssessment = serviceCase.value?.assessment
  const currentPlan = serviceCase.value?.plan

  if (!currentAssessment?.completed_at) {
    return {
      badgeText: '待评估完成',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '暂不能制定计划',
      description: '建议先完成评估，再进入计划页制定具体的干预措施。',
      disabled: true,
    }
  }

  if (!currentPlan) {
    return {
      badgeText: '未开始',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '开始制定计划',
      description: '评估已经完成，可以进入计划页制定干预措施和行动计划。',
      disabled: false,
    }
  }

  if (!currentPlan.confirmed_at) {
    return {
      badgeText: '草稿',
      badgeClass: 'bg-amber-100 text-amber-700',
      buttonText: '继续制定计划',
      description: '干预计划草稿已保存，可以继续编辑或完成确认。',
      disabled: false,
    }
  }

  return {
    badgeText: '已完成',
    badgeClass: 'bg-emerald-100 text-emerald-700',
    buttonText: '查看计划',
    description: '干预计划已完成制定，可以随时回看详情。',
    disabled: false,
  }
})

const goToPlanForm = () => {
  if (!serviceCase.value) return
  router.push({
    name: 'MtmPlanForm',
    params: { id: serviceCase.value.id.toString() },
  })
}
"""

if "const planEntryMeta" not in content:
    content = content.replace("const goToAssessmentForm = () => {", plan_meta_str + "\nconst goToAssessmentForm = () => {")
    with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
        f.write(content)
