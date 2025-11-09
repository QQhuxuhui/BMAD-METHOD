<template>
  <div class="workflow-graph-container">
    <!-- 工具栏 -->
    <div class="graph-toolbar">
      <a-space>
        <a-tooltip title="适应画布">
          <a-button size="small" @click="handleFitView">
            <template #icon>
              <FullscreenOutlined />
            </template>
          </a-button>
        </a-tooltip>

        <a-tooltip title="放大">
          <a-button size="small" @click="handleZoomIn">
            <template #icon>
              <ZoomInOutlined />
            </template>
          </a-button>
        </a-tooltip>

        <a-tooltip title="缩小">
          <a-button size="small" @click="handleZoomOut">
            <template #icon>
              <ZoomOutOutlined />
            </template>
          </a-button>
        </a-tooltip>

        <a-tooltip title="重置视图">
          <a-button size="small" @click="handleReset">
            <template #icon>
              <ReloadOutlined />
            </template>
          </a-button>
        </a-tooltip>
      </a-space>
    </div>

    <!-- G6图形容器 -->
    <div ref="graphContainer" class="graph-canvas"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  FullscreenOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  ReloadOutlined,
} from '@ant-design/icons-vue'
import G6, { Graph } from '@antv/g6'
import { useWorkflowStore } from '@/stores/workflow'
import { AGENTS_CONFIG, getAgentDependencies } from '@/config/agents'
import type { AgentStatus } from '@/types/workflow'

// Props
interface Props {
  /** 图形高度 */
  height?: number
  /** 是否横向布局 */
  horizontal?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 600,
  horizontal: false,
})

// Emits
const emit = defineEmits<{
  nodeClick: [agentId: string]
  phaseClick: [phaseId: number]
}>()

// Store
const workflowStore = useWorkflowStore()

// Refs
const graphContainer = ref<HTMLDivElement>()
let graph: Graph | null = null

/**
 * 注册自定义智能体节点
 */
const registerAgentNode = () => {
  G6.registerNode('agent-node', {
    draw(cfg, group) {
      const { id, nameCn, icon, status = 'pending' } = cfg as any

      // 节点状态颜色配置
      const colorMap = {
        pending: '#d9d9d9',
        running: '#1890ff',
        completed: '#52c41a',
        failed: '#ff4d4f',
      }

      const fillColor = colorMap[status as keyof typeof colorMap] || colorMap.pending

      // 圆形背景
      const circle = group!.addShape('circle', {
        attrs: {
          x: 0,
          y: 0,
          r: 50,
          fill: fillColor,
          stroke: '#fff',
          lineWidth: 3,
          shadowColor: 'rgba(0, 0, 0, 0.15)',
          shadowBlur: 8,
          shadowOffsetX: 2,
          shadowOffsetY: 2,
          cursor: 'pointer',
        },
        name: 'circle-shape',
      })

      // Emoji图标
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: -10,
          text: icon,
          fontSize: 32,
          textAlign: 'center',
          textBaseline: 'middle',
          fontFamily: 'Arial',
          cursor: 'pointer',
        },
        name: 'icon-shape',
      })

      // 中文名称
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: 22,
          text: nameCn,
          fontSize: 14,
          fontWeight: 'bold',
          textAlign: 'center',
          textBaseline: 'middle',
          fill: '#fff',
          cursor: 'pointer',
        },
        name: 'name-shape',
      })

      // ID标签（小字，用于调试）
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: 60,
          text: id,
          fontSize: 10,
          textAlign: 'center',
          textBaseline: 'top',
          fill: '#999',
        },
        name: 'id-shape',
      })

      return circle
    },

    // 节点状态更新
    setState(name, value, item) {
      const group = item!.getContainer()
      const shape = group!.get('children')[0] // circle

      const colorMap = {
        pending: '#d9d9d9',
        running: '#1890ff',
        completed: '#52c41a',
        failed: '#ff4d4f',
      }

      if (name === 'pending' && value) {
        shape.attr('fill', colorMap.pending)
        shape.stopAnimate()
      } else if (name === 'running' && value) {
        shape.attr('fill', colorMap.running)
        // 呼吸灯动画
        shape.animate(
          (ratio: number) => {
            const opacity = 0.6 + Math.sin(ratio * Math.PI * 2) * 0.4
            return { opacity }
          },
          {
            duration: 1500,
            repeat: true,
            easing: 'easeCubic',
          }
        )
      } else if (name === 'completed' && value) {
        shape.attr('fill', colorMap.completed)
        shape.stopAnimate()
      } else if (name === 'failed' && value) {
        shape.attr('fill', colorMap.failed)
        shape.stopAnimate()
      }
    },

    // 节点更新
    update(cfg, item) {
      const group = item!.getContainer()
      const { status } = cfg as any

      // 更新状态
      if (status) {
        // 重置所有状态
        item!.setState('pending', false)
        item!.setState('running', false)
        item!.setState('completed', false)
        item!.setState('failed', false)

        // 设置新状态
        item!.setState(status, true)
      }
    },
  })
}

/**
 * 创建图数据
 */
const createGraphData = () => {
  // 节点：8个智能体
  const nodes = AGENTS_CONFIG.map((agent) => {
    // 从Store获取对应的状态
    const storeAgent = workflowStore.agents.find((a) => a.id === agent.id)
    const status = storeAgent?.status || 'pending'

    return {
      id: agent.id,
      nameEn: agent.nameEn,
      nameCn: agent.nameCn,
      icon: agent.icon,
      status,
      type: 'agent-node',
      phase: agent.phase,
    }
  })

  // 边：依赖关系
  const edges = getAgentDependencies().map((dep) => ({
    source: dep.source,
    target: dep.target,
  }))

  return { nodes, edges }
}

/**
 * 初始化图形
 */
const initGraph = () => {
  if (!graphContainer.value) return

  registerAgentNode()

  const width = graphContainer.value.offsetWidth
  const height = props.height

  graph = new G6.Graph({
    container: graphContainer.value,
    width,
    height,
    layout: {
      type: 'dagre',
      rankdir: props.horizontal ? 'LR' : 'TB', // 横向：从左到右 | 竖向：从上到下
      nodesep: props.horizontal ? 60 : 90, // 横向时节点间距更紧凑
      ranksep: props.horizontal ? 120 : 140, // 横向时层级间距
      align: props.horizontal ? 'UL' : 'DL', // 横向：上对齐 | 竖向：左对齐
    },
    defaultNode: {
      type: 'agent-node',
      size: props.horizontal ? 80 : 100, // 横向时节点更小以节省空间
    },
    defaultEdge: {
      type: 'polyline',
      style: {
        stroke: '#999',
        lineWidth: 2,
        endArrow: {
          path: G6.Arrow.triangle(10, 12, 0),
          fill: '#999',
        },
        radius: 12,
      },
    },
    modes: {
      default: ['drag-canvas', 'zoom-canvas', 'drag-node'],
    },
    fitView: true,
    fitViewPadding: props.horizontal ? [10, 30, 10, 30] : [20, 50, 20, 50], // 横向时减小padding
  })

  const data = createGraphData()
  graph.data(data)
  graph.render()

  // 节点点击事件
  graph.on('node:click', (evt) => {
    const { item } = evt
    if (item) {
      const model = item.getModel()
      const agentId = model.id as string
      emit('nodeClick', agentId)
    }
  })

  console.log('[WorkflowGraph] 图初始化完成', {
    nodes: data.nodes.length,
    edges: data.edges.length,
  })
}

/**
 * 更新节点状态
 */
const updateNodeStatus = (agentId: string, status: AgentStatus) => {
  if (!graph) return

  const node = graph.findById(agentId)
  if (node) {
    graph.updateItem(node, { status })
  }
}

/**
 * 监听Store中agents的状态变化
 */
watch(
  () => workflowStore.agents,
  (newAgents) => {
    newAgents.forEach((agent) => {
      updateNodeStatus(agent.id, agent.status)
    })
  },
  { deep: true }
)

/**
 * 工具栏功能
 */
const handleFitView = () => {
  if (graph) {
    const padding = props.horizontal ? [10, 30, 10, 30] : [20, 50, 20, 50]
    graph.fitView(padding)
    message.success('已适应画布')
  }
}

const handleZoomIn = () => {
  if (graph) {
    const currentZoom = graph.getZoom()
    graph.zoomTo(currentZoom * 1.2, undefined, true)
  }
}

const handleZoomOut = () => {
  if (graph) {
    const currentZoom = graph.getZoom()
    graph.zoomTo(currentZoom / 1.2, undefined, true)
  }
}

const handleReset = () => {
  if (graph) {
    graph.zoomTo(1)
    graph.fitCenter()
    message.info('视图已重置')
  }
}

/**
 * 生命周期
 */
onMounted(() => {
  setTimeout(() => {
    initGraph()
  }, 100)
})

onBeforeUnmount(() => {
  if (graph) {
    graph.destroy()
  }
})
</script>

<style scoped lang="scss">
.workflow-graph-container {
  position: relative;
  width: 100%;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #e8e8e8;

  .graph-toolbar {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 10;
    padding: 8px;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .graph-canvas {
    width: 100%;
    height: 100%;
  }
}
</style>
