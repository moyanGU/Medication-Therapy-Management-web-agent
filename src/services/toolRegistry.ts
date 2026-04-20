import type { ZodTypeAny } from 'zod/v4'

export interface AgentTool<T = any> {
  name: string
  description: string
  inputSchema: ZodTypeAny
  execute: (args: T) => Promise<any> | any
}

class ToolRegistry {
  private tools: Map<string, AgentTool> = new Map()

  register(tool: AgentTool) {
    if (this.tools.has(tool.name)) {
      console.warn(`[ToolRegistry] Tool ${tool.name} is already registered. Overwriting.`)
    }
    this.tools.set(tool.name, tool)
  }

  getTool(name: string) {
    return this.tools.get(name)
  }

  getAllTools() {
    return Array.from(this.tools.values())
  }
}

export const globalToolRegistry = new ToolRegistry()
