# Graph Report - E:\mtm-helper  (2026-05-11)

## Corpus Check
- Agent graph report is limited to the current auto_agent-related chain, not the whole repo.

## Summary
- 141 nodes · 240 edges · 8 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]

## God Nodes (most connected - your core abstractions)
1. `RestrictedPageController` - 13 edges
2. `BaseAgent` - 13 edges
3. `buildCommonPageSnapshot()` - 12 edges
4. `medication_guidance()` - 12 edges
5. `executePageAgentTask()` - 8 edges
6. `MedicationAgent` - 8 edges
7. `_execute_page_agent_fallback()` - 7 edges
8. `page_agent_chat_completions()` - 7 edges
9. `session_memory_summarize()` - 7 edges
10. `SessionMemoryAgent` - 7 edges

## Surprising Connections (you probably didn't know these)
- `executePageAgentTask()` --calls--> `canUsePageAgentOnCurrentPage()`  [INFERRED]
  src\services\pageAgentRuntime.ts → src\services\pageAgentShared.ts
- `session_memory_summarize()` --calls--> `SessionMemoryAgent`  [INFERRED]
  backend\apps\core\ai_session_memory.py → backend\apps\core\agents\memory_agent.py
- `负责提取和总结 MTM 服务单对话记忆的子代理` --uses--> `BaseAgent`  [INFERRED]
  backend\apps\core\agents\memory_agent.py → backend\apps\core\agents\base.py
- `MedicationAgent` --uses--> `BaseAgent`  [INFERRED]
  backend\apps\core\agents\medication_agent.py → backend\apps\core\agents\base.py
- `专门负责 MTM 服务单 SOAP 药历生成的子代理` --uses--> `BaseAgent`  [INFERRED]
  backend\apps\core\agents\soap_agent.py → backend\apps\core\agents\base.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (24): asPageControllerContract(), buildActionProposal(), buildActionProposalAnswer(), buildLowStockMedicineAnswer(), buildMedicalRecordDraftProposal(), buildMedicineDraftProposal(), buildNavigationProposal(), buildPageAgentAnswer() (+16 more)

### Community 1 - "Community 1"
Cohesion: 0.2
Nodes (18): _apply_page_agent_max_tokens(), _build_page_agent_fallback_instruction(), _build_page_agent_fallback_messages(), _build_page_agent_fallback_response(), _build_page_agent_headers(), _build_page_agent_proxy_payload(), _execute_page_agent_fallback(), _extract_page_agent_tool_meta() (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (10): ABC, BaseAgent, get_system_prompt(), 后端领域专家子代理基类 (Sub-Agent Base), 负责提取和总结 MTM 服务单对话记忆的子代理, SessionMemoryAgent, 接收 MTM 服务单上下文，返回 SOAP 字典, 专门负责 MTM 服务单 SOAP 药历生成的子代理 (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.22
Nodes (15): getPageInstructions(), getCurrentPageAgentScopeDescription(), getCurrentPageKey(), buildCommonPageSnapshot(), buildDashboardSnapshot(), buildMedicineSnapshot(), buildReminderSnapshot(), buildRestrictedBrowserState() (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.2
Nodes (13): MedicationAgent, _blocked_payload(), _check_medication_intent(), _fallback_medication_guidance_answer(), _load_medicine_context(), medication_guidance(), _ndjson_single(), _parse_medication_guidance_request() (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (1): RestrictedPageController

### Community 6 - "Community 6"
Cohesion: 0.36
Nodes (11): _build_session_memory_response(), _handle_session_memory_get(), _handle_session_memory_post(), _normalize_session_id(), _require_ai_enabled(), _require_user_id(), _resolve_summarize_messages(), _sanitize_messages() (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.4
Nodes (1): ToolRegistry

## Knowledge Gaps
- **1 isolated node(s):** `后端领域专家子代理基类 (Sub-Agent Base)`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 5`** (13 nodes): `RestrictedPageController`, `.cleanUpHighlights()`, `.clickElement()`, `.dispose()`, `.executeJavascript()`, `.getBrowserState()`, `.getLastUpdateTime()`, `.hideMask()`, `.inputText()`, `.scroll()`, `.scrollHorizontally()`, `.selectOption()`, `.showMask()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (5 nodes): `ToolRegistry`, `.getAllTools()`, `.getTool()`, `.register()`, `toolRegistry.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseAgent` connect `Community 2` to `Community 4`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `getPageInstructions()` connect `Community 3` to `Community 0`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `BaseAgent` (e.g. with `SessionMemoryAgent` and `负责提取和总结 MTM 服务单对话记忆的子代理`) actually correct?**
  _`BaseAgent` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `buildCommonPageSnapshot()` (e.g. with `getCurrentPageKey()` and `getCurrentPageAgentScopeDescription()`) actually correct?**
  _`buildCommonPageSnapshot()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `后端领域专家子代理基类 (Sub-Agent Base)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._