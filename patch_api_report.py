with open("src/api/mtm.ts", "r") as f:
    content = f.read()

report_method = """
  // ============================
  // PMR / MAP 报告 (Report)
  // ============================

  async getReport(serviceCaseId: number | string): Promise<any> {
    log('🔵 [mtmApi] getReport called with id =', serviceCaseId)
    const response = await api.get<any>(`/mtm/service-cases/${serviceCaseId}/report/`)
    log('🟢 [mtmApi] getReport response =', response.data)
    return response.data
  },
"""

if "async getReport" not in content:
    content = content.replace(
        "  /**\n   * 认领服务单 (仅药师)\n   */",
        report_method + "\n  /**\n   * 认领服务单 (仅药师)\n   */"
    )
    with open("src/api/mtm.ts", "w") as f:
        f.write(content)
