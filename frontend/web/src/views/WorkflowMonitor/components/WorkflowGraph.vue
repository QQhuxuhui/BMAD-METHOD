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
 * 注册自定义智能体节点（现代化卡片式设计）
 */
const registerAgentNode = () => {
  G6.registerNode('agent-node', {
    draw(cfg, group) {
      const { id, nameCn, icon, status = 'pending' } = cfg as any

      // 节点状态渐变色配置（使用线性渐变）
      const gradientMap = {
        pending: {
          color1: '#e0e0e0',
          color2: '#bdbdbd',
          shadowColor: 'rgba(0, 0, 0, 0.15)',
          glowColor: 'rgba(189, 189, 189, 0.3)',
        },
        running: {
          color1: '#42a5f5',
          color2: '#1976d2',
          shadowColor: 'rgba(25, 118, 210, 0.3)',
          glowColor: 'rgba(66, 165, 245, 0.5)',
        },
        completed: {
          color1: '#66bb6a',
          color2: '#388e3c',
          shadowColor: 'rgba(56, 142, 60, 0.25)',
          glowColor: 'rgba(102, 187, 106, 0.4)',
        },
        failed: {
          color1: '#ef5350',
          color2: '#c62828',
          shadowColor: 'rgba(198, 40, 40, 0.3)',
          glowColor: 'rgba(239, 83, 80, 0.4)',
        },
      }

      const gradient = gradientMap[status as keyof typeof gradientMap] || gradientMap.pending

      // 外层光晕（仅running状态）
      if (status === 'running') {
        group!.addShape('circle', {
          attrs: {
            x: 0,
            y: 0,
            r: 58,
            fill: gradient.glowColor,
            opacity: 0.6,
          },
          name: 'glow-outer',
        })
      }

      // 外阴影圆（增加层次感）
      group!.addShape('circle', {
        attrs: {
          x: 0,
          y: 2,
          r: 52,
          fill: 'rgba(0, 0, 0, 0.1)',
          opacity: 0.3,
        },
        name: 'shadow-circle',
      })

      // 主圆形背景（使用径向渐变）
      const circle = group!.addShape('circle', {
        attrs: {
          x: 0,
          y: 0,
          r: 50,
          fill: `l(45) 0:${gradient.color1} 1:${gradient.color2}`, // G6渐变语法：l(角度) 位置:颜色
          stroke: '#fff',
          lineWidth: 4,
          shadowColor: gradient.shadowColor,
          shadowBlur: 12,
          shadowOffsetX: 0,
          shadowOffsetY: 4,
          cursor: 'pointer',
        },
        name: 'circle-shape',
      })

      // 高光效果（顶部半透明白色）
      group!.addShape('circle', {
        attrs: {
          x: 0,
          y: -15,
          r: 20,
          fill: 'rgba(255, 255, 255, 0.25)',
          opacity: 0.8,
        },
        name: 'highlight',
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
          textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)', // 图标阴影
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
          textShadow: '0 1px 3px rgba(0, 0, 0, 0.3)', // 文字阴影增强可读性
        },
        name: 'name-shape',
      })

      // ID标签（小字，用于调试）
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: 62,
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

    // 节点状态更新（支持渐变色和光晕）
    setState(name, value, item) {
      const group = item!.getContainer()
      const children = group!.get('children')

      // 节点状态渐变色配置
      const gradientMap = {
        pending: {
          color1: '#e0e0e0',
          color2: '#bdbdbd',
          glowColor: 'rgba(189, 189, 189, 0.3)',
        },
        running: {
          color1: '#42a5f5',
          color2: '#1976d2',
          glowColor: 'rgba(66, 165, 245, 0.5)',
        },
        completed: {
          color1: '#66bb6a',
          color2: '#388e3c',
          glowColor: 'rgba(102, 187, 106, 0.4)',
        },
        failed: {
          color1: '#ef5350',
          color2: '#c62828',
          glowColor: 'rgba(239, 83, 80, 0.4)',
        },
      }

      // 找到主圆形（名称为circle-shape）
      let circleShape = null
      let glowShape = null
      for (let i = 0; i < children.length; i++) {
        const child = children[i]
        if (child.get('name') === 'circle-shape') {
          circleShape = child
        }
        if (child.get('name') === 'glow-outer') {
          glowShape = child
        }
      }

      if (name === 'pending' && value) {
        const gradient = gradientMap.pending
        circleShape?.attr('fill', `l(45) 0:${gradient.color1} 1:${gradient.color2}`)
        circleShape?.stopAnimate()
        // 移除光晕
        if (glowShape) {
          glowShape.attr('opacity', 0)
        }
      } else if (name === 'running' && value) {
        const gradient = gradientMap.running
        circleShape?.attr('fill', `l(45) 0:${gradient.color1} 1:${gradient.color2}`)

        // 添加光晕（如果不存在）
        if (!glowShape) {
          glowShape = group!.addShape('circle', {
            attrs: {
              x: 0,
              y: 0,
              r: 58,
              fill: gradient.glowColor,
              opacity: 0.6,
            },
            name: 'glow-outer',
          })
          // 将光晕移到最底层
          glowShape.toBack()
        } else {
          glowShape.attr({
            fill: gradient.glowColor,
            opacity: 0.6,
          })
        }

        // 光晕呼吸动画
        glowShape?.animate(
          (ratio: number) => {
            const scale = 1 + Math.sin(ratio * Math.PI * 2) * 0.1
            return {
              r: 58 * scale,
              opacity: 0.4 + Math.sin(ratio * Math.PI * 2) * 0.2,
            }
          },
          {
            duration: 2000,
            repeat: true,
          }
        )

        // 主圆形轻微呼吸
        circleShape?.animate(
          (ratio: number) => {
            const opacity = 0.9 + Math.sin(ratio * Math.PI * 2) * 0.1
            return { opacity }
          },
          {
            duration: 1500,
            repeat: true,
          }
        )
      } else if (name === 'completed' && value) {
        const gradient = gradientMap.completed
        circleShape?.attr('fill', `l(45) 0:${gradient.color1} 1:${gradient.color2}`)
        circleShape?.stopAnimate()
        glowShape?.stopAnimate()
        if (glowShape) {
          glowShape.attr('opacity', 0)
        }
      } else if (name === 'failed' && value) {
        const gradient = gradientMap.failed
        circleShape?.attr('fill', `l(45) 0:${gradient.color1} 1:${gradient.color2}`)
        circleShape?.stopAnimate()
        glowShape?.stopAnimate()
        if (glowShape) {
          glowShape.attr('opacity', 0)
        }
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
        stroke: 'l(0) 0:#a0a0a0 1:#7a7a7a', // 渐变灰色连线
        lineWidth: 3,
        opacity: 0.8,
        endArrow: {
          path: G6.Arrow.triangle(12, 15, 0), // 更大更明显的箭头
          fill: 'l(0) 0:#7a7a7a 1:#5a5a5a', // 箭头渐变
          opacity: 0.9,
        },
        radius: 15, // 更圆滑的转角
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        shadowBlur: 4,
        lineDash: [8, 4], // 虚线效果（流动感）
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

  // 连线流动动画
  const edges = graph.getEdges()
  edges.forEach((edge) => {
    edge.toFront() // 将边移到节点前面，避免被节点遮挡
    const edgeShape = edge.get('keyShape')
    edgeShape.animate(
      (ratio: number) => {
        // lineDashOffset循环从0到12（8+4=12是lineDash的周期）
        const offset = ratio * 12
        return {
          lineDashOffset: -offset, // 负值让虚线向前流动
        }
      },
      {
        duration: 2000, // 2秒一个循环
        repeat: true,
        // 不使用easing，默认线性动画
      }
    )
  })

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
