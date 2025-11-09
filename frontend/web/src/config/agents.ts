/**
 * 智能体配置文件
 * Story 1.10: 智能体协作可视化增强
 */

export interface AgentConfig {
  /** 智能体ID（与后端保持一致） */
  id: string
  /** 英文名称 */
  nameEn: string
  /** 中文名称（用于UI显示） */
  nameCn: string
  /** 图标（Emoji） */
  icon: string
  /** 描述 */
  description: string
  /** 所属Phase */
  phase: number
  /** 依赖的智能体ID列表 */
  dependencies: string[]
  /** 节点颜色（可选，用于自定义） */
  color?: string
}

/**
 * 8个智能体配置
 * 按执行顺序和依赖关系组织
 */
export const AGENTS_CONFIG: AgentConfig[] = [
  {
    id: 'orchestrator',
    nameEn: 'Orchestrator',
    nameCn: '总指挥',
    icon: '🎯',
    description: '统筹整体工作流程，协调各专家协作',
    phase: 0,
    dependencies: [],
  },
  {
    id: 'algorithm',
    nameEn: 'Algorithm Expert',
    nameCn: '算法专家',
    icon: '🧮',
    description: '负责算法选择和设计',
    phase: 1,
    dependencies: ['orchestrator'],
  },
  {
    id: 'constraint',
    nameEn: 'Constraint Expert',
    nameCn: '约束专家',
    icon: '⚖️',
    description: '定义和管理问题约束条件',
    phase: 2,
    dependencies: ['algorithm'],
  },
  {
    id: 'objective',
    nameEn: 'Objective Expert',
    nameCn: '目标专家',
    icon: '🎯',
    description: '制定优化目标函数',
    phase: 2,
    dependencies: ['algorithm'],
  },
  {
    id: 'domain',
    nameEn: 'Domain Expert',
    nameCn: '领域专家',
    icon: '🏢',
    description: '提供领域知识和业务规则',
    phase: 2,
    dependencies: ['orchestrator'],
  },
  {
    id: 'python',
    nameEn: 'Code Implementation Expert',
    nameCn: 'Python专家',
    icon: '🐍',
    description: '实现Python代码和算法逻辑',
    phase: 3,
    dependencies: ['constraint', 'objective'],
  },
  {
    id: 'extension',
    nameEn: 'Extension Expert',
    nameCn: '扩展专家',
    icon: '🔌',
    description: '处理扩展功能和集成',
    phase: 3,
    dependencies: ['python'],
  },
  {
    id: 'quality',
    nameEn: 'Quality Expert',
    nameCn: '质量专家',
    icon: '✅',
    description: '质量保证和验证',
    phase: 4,
    dependencies: ['python', 'extension'],
  },
]

/**
 * 智能体名称映射（英文 → 中文）
 */
export const AGENT_NAME_MAP: Record<string, string> = {
  Orchestrator: '总指挥',
  'Algorithm Expert': '算法专家',
  'Constraint Expert': '约束专家',
  'Objective Expert': '目标专家',
  'Domain Expert': '领域专家',
  'Code Implementation Expert': 'Python专家',
  'Extension Expert': '扩展专家',
  'Quality Expert': '质量专家',
}

/**
 * 智能体图标映射（ID → Emoji）
 */
export const AGENT_ICONS: Record<string, string> = {
  orchestrator: '🎯',
  algorithm: '🧮',
  constraint: '⚖️',
  objective: '🎯',
  domain: '🏢',
  python: '🐍',
  extension: '🔌',
  quality: '✅',
}

/**
 * 根据智能体ID获取配置
 */
export function getAgentConfig(id: string): AgentConfig | undefined {
  return AGENTS_CONFIG.find((agent) => agent.id === id)
}

/**
 * 根据英文名称获取中文名称
 */
export function getAgentNameCn(nameEn: string): string {
  return AGENT_NAME_MAP[nameEn] || nameEn
}

/**
 * 根据智能体ID获取图标
 */
export function getAgentIcon(id: string): string {
  return AGENT_ICONS[id] || '❓'
}

/**
 * 获取所有智能体ID列表
 */
export function getAllAgentIds(): string[] {
  return AGENTS_CONFIG.map((agent) => agent.id)
}

/**
 * 获取智能体的依赖关系（用于生成图的边）
 */
export function getAgentDependencies(): Array<{ source: string; target: string }> {
  const edges: Array<{ source: string; target: string }> = []

  AGENTS_CONFIG.forEach((agent) => {
    agent.dependencies.forEach((depId) => {
      edges.push({
        source: depId,
        target: agent.id,
      })
    })
  })

  return edges
}
