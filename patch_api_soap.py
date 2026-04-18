with open("src/api/mtm.ts", "r") as f:
    content = f.read()

soap_methods = """
  // ============================
  // SOAP 药历 (SOAP Notes)
  // ============================

  async getSoapNotes(serviceCaseId: number | string): Promise<any> {
    log('🔵 [mtmApi] getSoapNotes called with id =', serviceCaseId)
    const response = await api.get<any>(`/mtm/service-cases/${serviceCaseId}/soap/`)
    log('🟢 [mtmApi] getSoapNotes response =', response.data)
    return response.data
  },

  async saveSoapNotes(
    serviceCaseId: number | string,
    payload: any
  ): Promise<any> {
    log('🔵 [mtmApi] saveSoapNotes payload =', { serviceCaseId, payload })
    const response = await api.put<any>(
      `/mtm/service-cases/${serviceCaseId}/soap/`,
      payload
    )
    log('🟢 [mtmApi] saveSoapNotes response =', response.data)
    return response.data
  },

  async generateSoapNotesByAi(serviceCaseId: number | string): Promise<any> {
    log('🔵 [mtmApi] generateSoapNotesByAi called with id =', serviceCaseId)
    const response = await api.post<any>(`/mtm/service-cases/${serviceCaseId}/soap/generate/`)
    log('🟢 [mtmApi] generateSoapNotesByAi response =', response.data)
    return response.data
  },
"""

if "async getSoapNotes" not in content:
    content = content.replace(
        "  /**\n   * 认领服务单 (仅药师)\n   */",
        soap_methods + "\n  /**\n   * 认领服务单 (仅药师)\n   */"
    )
    with open("src/api/mtm.ts", "w") as f:
        f.write(content)
