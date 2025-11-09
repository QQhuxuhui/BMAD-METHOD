<template>
  <div class="workflow-graph-poc">
    <a-card title="AntV G6 POC - 智能体协作流程图" :bordered="false">
      <template #extra>
        <a-space>
          <a-tag color="blue">POC测试</a-tag>
          <a-button size="small" @click="handleStartSimulation">
            <template #icon>
              <PlayCircleOutlined />
            </template>
            模拟执行
          </a-button>
          <a-button size="small" @click="handleReset">
            <template #icon>
              <ReloadOutlined />
            </template>
            重置
          </a-button>
        </a-space>
      </template>

      <div ref="graphContainer" class="graph-container"></div>

      <a-divider />

      <div class="info-panel">
        <a-descriptions title="POC验证目标" :column="2" size="small">
          <a-descriptions-item label="验证点1">
            ✅ G6基础渲染
          </a-descriptions-item>
          <a-descriptions-item label="验证点2">
            ✅ 自定义节点样式
          </a-descriptions-item>
          <a-descriptions-item label="验证点3">
            ✅ 智能体中文化
          </a-descriptions-item>
          <a-descriptions-item label="验证点4">
            ✅ 状态动态更新
          </a-descriptions-item>
        </a-descriptions>

        <a-alert
          v-if="currentAgent"
          type="info"
          :message="`当前执行: ${currentAgent.nameCn}`"
          :description="`${currentAgent.nameEn} - ${currentAgent.icon}`"
          show-icon
          style="margin-top: 16px"
        />
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { message } from 'ant-design-vue'
import { PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import G6, { Graph } from '@antv/g6'

// 智能体配置
interface AgentConfig {
  id: string
  nameEn: string
  nameCn: string
  icon: string
  phase: number
  dependencies: string[]
}

const AGENTS_CONFIG: AgentConfig[] = [
  { id: 'orchestrator', nameEn: 'Orchestrator', nameCn: '总指挥', icon: '🎯', phase: 0, dependencies: [] },
  { id: 'algorithm', nameEn: 'Algorithm Expert', nameCn: '算法专家', icon: '🧮', phase: 1, dependencies: ['orchestrator'] },
  { id: 'constraint', nameEn: 'Constraint Expert', nameCn: '约束专家', icon: '⚖️', phase: 2, dependencies: ['algorithm'] },
  { id: 'objective', nameEn: 'Objective Expert', nameCn: '目标专家', icon: '🎯', phase: 2, dependencies: ['algorithm'] },
  { id: 'domain', nameEn: 'Domain Expert', nameCn: '领域专家', icon: '🏢', phase: 2, dependencies: ['orchestrator'] },
  { id: 'python', nameEn: 'Code Implementation Expert', nameCn: 'Python专家', icon: '🐍', phase: 3, dependencies: ['constraint', 'objective'] },
  { id: 'extension', nameEn: 'Extension Expert', nameCn: '扩展专家', icon: '🔌', phase: 3, dependencies: ['python'] },
  { id: 'quality', nameEn: 'Quality Expert', nameCn: '质量专家', icon: '✅', phase: 4, dependencies: ['python', 'extension'] }
]

// Refs
const graphContainer = ref<HTMLDivElement>()
const currentAgent = ref<AgentConfig | null>(null)
let graph: Graph | null = null
let simulationTimer: number | null = null

/**
 * 注册自定义智能体节点
 */
const registerAgentNode = () => {
  G6.registerNode('agent-node', {
    draw(cfg, group) {
      const { id, nameCn, icon, status = 'pending' } = cfg as any

      // 节点状态颜色
      const colors = {
        pending: '#d9d9d9',
        running: '#1890ff',
        completed: '#52c41a',
        failed: '#ff4d4f'
      }

      const fillColor = colors[status as keyof typeof colors] || colors.pending

      // 圆形背景
      const circle = group!.addShape('circle', {
        attrs: {
          x: 0,
          y: 0,
          r: 45,
          fill: fillColor,
          stroke: '#fff',
          lineWidth: 3,
          shadowColor: 'rgba(0, 0, 0, 0.2)',
          shadowBlur: 10,
          shadowOffsetX: 2,
          shadowOffsetY: 2
        },
        name: 'circle-shape'
      })

      // Emoji图标
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: -8,
          text: icon,
          fontSize: 28,
          textAlign: 'center',
          textBaseline: 'middle',
          fontFamily: 'Arial'
        },
        name: 'icon-shape'
      })

      // 中文名称
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: 18,
          text: nameCn,
          fontSize: 13,
          fontWeight: 'bold',
          textAlign: 'center',
          textBaseline: 'middle',
          fill: '#fff'
        },
        name: 'name-shape'
      })

      // ID标签（调试用）
      group!.addShape('text', {
        attrs: {
          x: 0,
          y: 55,
          text: id,
          fontSize: 10,
          textAlign: 'center',
          textBaseline: 'top',
          fill: '#999'
        },
        name: 'id-shape'
      })

      return circle
    },

    // 节点状态更新
    setState(name, value, item) {
      const group = item!.getContainer()
      const shape = group!.get('children')[0]

      const colors = {
        pending: '#d9d9d9',
        running: '#1890ff',
        completed: '#52c41a',
        failed: '#ff4d4f'
      }

      if (name === 'pending' && value) {
        shape.attr('fill', colors.pending)
        shape.stopAnimate()
      } else if (name === 'running' && value) {
        shape.attr('fill', colors.running)
        // 呼吸灯动画
        shape.animate(
          (ratio: number) => {
            const opacity = 0.6 + Math.sin(ratio * Math.PI * 2) * 0.4
            return { opacity }
          },
          {
            duration: 1500,
            repeat: true,
            easing: 'easeCubic'
          }
        )
      } else if (name === 'completed' && value) {
        shape.attr('fill', colors.completed)
        shape.stopAnimate()
      } else if (name === 'failed' && value) {
        shape.attr('fill', colors.failed)
        shape.stopAnimate()
      }
    }
  })
}

/**
 * 创建图数据
 */
const createGraphData = () => {
  const nodes = AGENTS_CONFIG.map(agent => ({
    id: agent.id,
    nameEn: agent.nameEn,
    nameCn: agent.nameCn,
    icon: agent.icon,
    status: 'pending',
    type: 'agent-node'
  }))

  const edges: any[] = []
  AGENTS_CONFIG.forEach(agent => {
    agent.dependencies.forEach(depId => {
      edges.push({
        source: depId,
        target: agent.id
      })
    })
  })

  return { nodes, edges }
}

/**
 * 初始化图
 */
const initGraph = () => {
  if (!graphContainer.value) return

  registerAgentNode()

  const width = graphContainer.value.offsetWidth
  const height = 600

  graph = new G6.Graph({
    container: graphContainer.value,
    width,
    height,
    layout: {
      type: 'dagre',
      rankdir: 'TB', // 从上到下
      nodesep: 80,
      ranksep: 120
    },
    defaultNode: {
      type: 'agent-node',
      size: 90
    },
    defaultEdge: {
      type: 'polyline',
      style: {
        stroke: '#999',
        lineWidth: 2,
        endArrow: {
          path: G6.Arrow.triangle(8, 10, 0),
          fill: '#999'
        },
        radius: 10
      }
    },
    modes: {
      default: ['drag-canvas', 'zoom-canvas', 'drag-node']
    },
    fitView: true,
    fitViewPadding: 20
  })

  const data = createGraphData()
  graph.data(data)
  graph.render()

  // 节点点击事件
  graph.on('node:click', (evt) => {
    const { item } = evt
    const model = item!.getModel()
    message.info(`点击智能体: ${model.nameCn}`)
  })

  console.log('[G6 POC] 图初始化完成', { nodes: data.nodes.length, edges: data.edges.length })
}

/**
 * 模拟工作流执行
 */
const handleStartSimulation = () => {
  if (!graph) return

  message.info('开始模拟智能体执行流程...')

  // 重置所有节点状态
  graph.getNodes().forEach(node => {
    graph!.setItemState(node, 'pending', true)
    graph!.setItemState(node, 'running', false)
    graph!.setItemState(node, 'completed', false)
  })

  // 按顺序模拟执行
  let currentIndex = 0

  const executeNext = () => {
    if (currentIndex >= AGENTS_CONFIG.length) {
      message.success('所有智能体执行完成！')
      currentAgent.value = null
      return
    }

    const agent = AGENTS_CONFIG[currentIndex]
    const node = graph!.findById(agent.id)

    if (node) {
      // 设置当前智能体为运行状态
      graph!.setItemState(node, 'pending', false)
      graph!.setItemState(node, 'running', true)
      currentAgent.value = agent

      console.log(`[执行] ${agent.nameCn} (${agent.nameEn})`)

      // 2秒后完成
      setTimeout(() => {
        graph!.setItemState(node, 'running', false)
        graph!.setItemState(node, 'completed', true)

        currentIndex++
        executeNext()
      }, 2000)
    }
  }

  executeNext()
}

/**
 * 重置图
 */
const handleReset = () => {
  if (!graph) return

  graph.getNodes().forEach(node => {
    graph!.setItemState(node, 'pending', true)
    graph!.setItemState(node, 'running', false)
    graph!.setItemState(node, 'completed', false)
  })

  currentAgent.value = null
  message.info('已重置')
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
  if (simulationTimer) {
    clearTimeout(simulationTimer)
  }
  if (graph) {
    graph.destroy()
  }
})
</script>

<style scoped lang="scss">
.workflow-graph-poc {
  .graph-container {
    width: 100%;
    height: 600px;
    background-color: #fafafa;
    border-radius: 4px;
    border: 1px solid #e8e8e8;
  }

  .info-panel {
    margin-top: 16px;
  }
}
</style>
