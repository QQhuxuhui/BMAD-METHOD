<template>
  <div class="workflow-topology-view">
    <a-card title="工作流拓扑图" :loading="loading">
      <template #extra>
        <a-space>
          <a-button size="small" @click="handleFitView">适应画布</a-button>
          <a-button size="small" @click="handleZoomIn">放大</a-button>
          <a-button size="small" @click="handleZoomOut">缩小</a-button>
          <a-button size="small" @click="handleReset">重置</a-button>
        </a-space>
      </template>

      <div ref="containerRef" class="topology-container"></div>

      <!-- 图例 -->
      <div class="topology-legend">
        <a-space>
          <div class="legend-item">
            <div class="legend-dot" style="background: #d9d9d9"></div>
            <span>等待中</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: #1890ff"></div>
            <span>执行中</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: #52c41a"></div>
            <span>已完成</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: #ff4d4f"></div>
            <span>失败</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: #faad14"></div>
            <span>需审批</span>
          </div>
        </a-space>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
// @ts-ignore - G6 v5 types may not match exactly
import { Graph } from '@antv/g6'
import type { AgentExecution, WorkflowPhase } from '@/types/workflow'

interface Props {
  currentPhase?: WorkflowPhase
  currentAgent?: string | null
  agentExecutions?: AgentExecution[]
  isApprovalRequired?: boolean
  approvalPoint?: 'P1' | 'P2' | 'P2.5' | null
}

const props = withDefaults(defineProps<Props>(), {
  currentPhase: 'P0',
  currentAgent: null,
  agentExecutions: () => [],
  isApprovalRequired: false,
  approvalPoint: null,
})

// State
const containerRef = ref<HTMLElement>()
const loading = ref(false)
let graph: Graph | null = null

// 节点数据定义（11个节点：8 agents + 3 approvals）
const nodes = [
  { id: 'orchestrator', label: 'Orchestrator', type: 'agent', phase: 'P0' },
  { id: 'algorithm', label: 'Algorithm Expert', type: 'agent', phase: 'P1' },
  { id: 'constraint', label: 'Constraint Expert', type: 'agent', phase: 'P1' },
  { id: 'objective', label: 'Objective Expert', type: 'agent', phase: 'P1' },
  { id: 'p1_approval', label: 'P1 Approval', type: 'approval', phase: 'P1' },
  { id: 'domain', label: 'Domain Expert', type: 'agent', phase: 'P2' },
  { id: 'p2_approval', label: 'P2 Approval', type: 'approval', phase: 'P2' },
  { id: 'code_impl', label: 'Code Implementation', type: 'agent', phase: 'P2.5' },
  { id: 'p25_approval', label: 'P2.5 Approval', type: 'approval', phase: 'P2.5' },
  { id: 'extension', label: 'Extension Expert', type: 'agent', phase: 'P3' },
  { id: 'quality', label: 'Quality Expert', type: 'agent', phase: 'P4' },
]

// 边数据定义
const edges = [
  { source: 'orchestrator', target: 'algorithm' },
  { source: 'orchestrator', target: 'constraint' },
  { source: 'orchestrator', target: 'objective' },
  { source: 'algorithm', target: 'p1_approval' },
  { source: 'constraint', target: 'p1_approval' },
  { source: 'objective', target: 'p1_approval' },
  { source: 'p1_approval', target: 'domain', style: { lineDash: [5, 5] } },
  { source: 'domain', target: 'p2_approval' },
  { source: 'p2_approval', target: 'code_impl', style: { lineDash: [5, 5] } },
  { source: 'code_impl', target: 'p25_approval' },
  { source: 'p25_approval', target: 'extension', style: { lineDash: [5, 5] } },
  { source: 'extension', target: 'quality' },
]

// 注意: 状态样式将在图形更新时动态应用

// 初始化图形
const initGraph = () => {
  if (!containerRef.value) return

  try {
    // @ts-ignore - G6 v5 API
    graph = new Graph({
      container: containerRef.value,
      width: containerRef.value.offsetWidth,
      height: 600,
      // G6 v5 使用不同的配置格式
      node: {
        style: {
          size: 70,
          fill: '#d9d9d9',
          stroke: '#aaa',
          lineWidth: 2,
        },
      },
      edge: {
        style: {
          stroke: '#aaa',
          lineWidth: 2,
        },
      },
      layout: {
        type: 'dagre',
        rankdir: 'TB',
        nodesep: 60,
        ranksep: 80,
      },
    })

    // 设置数据并渲染
    // @ts-ignore
    graph.read({ nodes, edges })

    // 适应画布
    // @ts-ignore
    graph.fitView()
  } catch (error) {
    console.error('Failed to initialize graph:', error)
  }
}

// 更新节点状态
const updateNodeStates = () => {
  if (!graph) return

  try {
    // @ts-ignore - G6 v5 may have different APIs
    // 根据智能体执行状态更新节点样式
    props.agentExecutions.forEach((execution) => {
      const nodeId = getNodeIdByAgentName(execution.name)
      if (nodeId) {
        updateNodeStyle(nodeId, execution.status)
      }
    })

    // 高亮当前执行的智能体
    if (props.currentAgent) {
      const nodeId = getNodeIdByAgentName(props.currentAgent)
      if (nodeId) {
        updateNodeStyle(nodeId, 'running')
      }
    }

    // 高亮审批点
    if (props.isApprovalRequired && props.approvalPoint) {
      const approvalNodeId = getApprovalNodeId(props.approvalPoint)
      if (approvalNodeId) {
        updateNodeStyle(approvalNodeId, 'approval_required')
      }
    }
  } catch (error) {
    console.error('Failed to update node states:', error)
  }
}

// 更新节点样式的辅助函数
const updateNodeStyle = (nodeId: string, status: string) => {
  if (!graph) return

  const styleMap: Record<string, { fill: string; stroke: string }> = {
    pending: { fill: '#d9d9d9', stroke: '#aaa' },
    running: { fill: '#1890ff', stroke: '#096dd9' },
    completed: { fill: '#52c41a', stroke: '#389e0d' },
    failed: { fill: '#ff4d4f', stroke: '#cf1322' },
    approval_required: { fill: '#faad14', stroke: '#d48806' },
  }

  const style = styleMap[status]
  if (style) {
    try {
      // @ts-ignore
      graph.updateNodeData(nodeId, { style })
    } catch (error) {
      console.warn(`Could not update style for node ${nodeId}:`, error)
    }
  }
}

// 根据智能体名称获取节点ID
const getNodeIdByAgentName = (agentName: string): string | null => {
  const mapping: Record<string, string> = {
    'Orchestrator': 'orchestrator',
    'Algorithm Expert': 'algorithm',
    'Constraint Expert': 'constraint',
    'Objective Expert': 'objective',
    'Domain Expert': 'domain',
    'Code Implementation': 'code_impl',
    'Extension Expert': 'extension',
    'Quality Expert': 'quality',
  }
  return mapping[agentName] || null
}

// 根据审批点获取节点ID
const getApprovalNodeId = (point: 'P1' | 'P2' | 'P2.5'): string => {
  const mapping = {
    P1: 'p1_approval',
    P2: 'p2_approval',
    'P2.5': 'p25_approval',
  }
  return mapping[point]
}

// 图形操作方法
const handleFitView = () => {
  try {
    // @ts-ignore
    graph?.fitView()
  } catch (error) {
    console.error('Failed to fit view:', error)
  }
}

const handleZoomIn = () => {
  try {
    // @ts-ignore
    const currentZoom = graph?.getZoom() || 1
    // @ts-ignore
    graph?.zoomTo(currentZoom * 1.2)
  } catch (error) {
    console.error('Failed to zoom in:', error)
  }
}

const handleZoomOut = () => {
  try {
    // @ts-ignore
    const currentZoom = graph?.getZoom() || 1
    // @ts-ignore
    graph?.zoomTo(currentZoom * 0.8)
  } catch (error) {
    console.error('Failed to zoom out:', error)
  }
}

const handleReset = () => {
  try {
    // @ts-ignore
    graph?.zoomTo(1)
    // @ts-ignore
    graph?.fitView()
  } catch (error) {
    console.error('Failed to reset:', error)
  }
}

// 监听props变化，更新节点状态
watch(
  [
    () => props.currentAgent,
    () => props.agentExecutions,
    () => props.isApprovalRequired,
    () => props.approvalPoint,
  ],
  () => {
    updateNodeStates()
  },
  { deep: true },
)

// 生命周期
onMounted(() => {
  initGraph()
  updateNodeStates()

  // 响应式调整画布大小
  window.addEventListener('resize', () => {
    if (graph && containerRef.value) {
      try {
        // @ts-ignore
        graph.changeSize?.(containerRef.value.offsetWidth, 600)
        // @ts-ignore
        graph.fitView?.()
      } catch (error) {
        console.warn('Failed to resize graph:', error)
      }
    }
  })
})

onUnmounted(() => {
  if (graph) {
    graph.destroy()
    graph = null
  }
})
</script>

<style scoped lang="scss">
.workflow-topology-view {
  .topology-container {
    width: 100%;
    height: 600px;
    border: 1px solid #f0f0f0;
    border-radius: 4px;
    background: #fafafa;
  }

  .topology-legend {
    margin-top: 16px;
    padding: 12px;
    background: #f5f5f5;
    border-radius: 4px;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .legend-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid rgba(0, 0, 0, 0.2);
      }

      span {
        font-size: 13px;
        color: rgba(0, 0, 0, 0.65);
      }
    }
  }
}
</style>
