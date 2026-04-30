with open("src/api/mtm.ts", "r") as f:
    content = f.read()

api_additions = """
  // ============================
  // 干预计划 (Plan)
  // ============================

  async getPlan(serviceCaseId: number | string): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] getPlan called with id =', serviceCaseId)
    const response = await api.get<MtmPlanSummary>(`/mtm/service-cases/${serviceCaseId}/plan/`)
    log('🟢 [mtmApi] getPlan response =', response.data)
    return response.data
  },

  async savePlanDraft(
    serviceCaseId: number | string,
    payload: Partial<MtmPlanSummary>
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] savePlanDraft payload =', { serviceCaseId, ...payload })
    const response = await api.put<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/`,
      payload
    )
    log('🟢 [mtmApi] savePlanDraft response =', response.data)
    return response.data
  },

  async completePlan(
    serviceCaseId: number | string,
    payload: Partial<MtmPlanSummary>
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] completePlan payload =', { serviceCaseId, ...payload })
    const response = await api.post<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/complete/`,
      payload
    )
    log('🟢 [mtmApi] completePlan response =', response.data)
    return response.data
  },

  // ============================
  // 随访记录 (Follow-up)
  // ============================

  async getFollowUps(serviceCaseId: number | string): Promise<MtmFollowUpSummary[]> {
    log('🔵 [mtmApi] getFollowUps called with id =', serviceCaseId)
    const response = await api.get<MtmFollowUpSummary[]>(`/mtm/service-cases/${serviceCaseId}/follow-ups/`)
    log('🟢 [mtmApi] getFollowUps response =', response.data)
    return response.data
  },

  async addFollowUp(
    serviceCaseId: number | string,
    payload: Partial<MtmFollowUpSummary>
  ): Promise<MtmFollowUpSummary> {
    log('🔵 [mtmApi] addFollowUp payload =', { serviceCaseId, ...payload })
    const response = await api.post<MtmFollowUpSummary>(
      `/mtm/service-cases/${serviceCaseId}/follow-ups/`,
      payload
    )
    log('🟢 [mtmApi] addFollowUp response =', response.data)
    return response.data
  },
"""

if "async getPlan" not in content:
    content = content.replace("  /**\n   * 认领服务单 (仅药师)\n   */", api_additions + "\n  /**\n   * 认领服务单 (仅药师)\n   */")
    
    with open("src/api/mtm.ts", "w") as f:
        f.write(content)
