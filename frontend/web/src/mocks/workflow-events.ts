/**
 * Mock工作流事件数据
 * Story 1.9: 实时工作流监控面板MVP
 */

import type { WorkflowEvent } from '@/types/workflow'

/**
 * 成功场景的Mock事件流
 */
export const successScenarioEvents: WorkflowEvent[] = [
  // 工作流开始
  {
    event: 'workflow_started',
    data: {
      timestamp: new Date().toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P0',
      metadata: {
        userInput: '实现智能路径规划系统',
        config: { enableHumanInLoop: true }
      }
    }
  },

  // Phase 0: Orchestrator开始
  {
    event: 'agent_started',
    data: {
      timestamp: new Date(Date.now() + 1000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P0',
      agent_name: 'Orchestrator',
      metadata: { order: 0 }
    }
  },

  // Orchestrator输出
  {
    event: 'agent_output',
    data: {
      timestamp: new Date(Date.now() + 2000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      agent_name: 'Orchestrator',
      agent_output: {
        type: 'markdown',
        content: `# 问题分析

**用户需求**: 实现智能路径规划系统

## 问题特征分析

1. **问题类型**: 图论/路径搜索问题
2. **核心挑战**:
   - 最短路径计算
   - 动态障碍物处理
   - 实时性要求
3. **约束条件**:
   - 响应时间 < 100ms
   - 支持动态图更新

## 推荐算法

基于以上分析，推荐使用 **A* 搜索算法**：
- ✅ 最优性保证
- ✅ 启发式加速
- ✅ 可扩展性强

**置信度**: 95%`
      }
    }
  },

  // Orchestrator完成
  {
    event: 'agent_completed',
    data: {
      timestamp: new Date(Date.now() + 4000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P0',
      agent_name: 'Orchestrator',
      metadata: {
        recommendation: 'A* 搜索算法',
        confidence: 0.95
      }
    }
  },

  // P1审批点
  {
    event: 'approval_required',
    data: {
      timestamp: new Date(Date.now() + 5000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P1',
      approval_point: 'P1',
      approval_context: {
        recommendation: 'A* 搜索算法',
        alternatives: ['Dijkstra', 'BFS', 'DFS'],
        reason: '需要确认算法选择是否符合预期'
      }
    }
  },

  // 工作流暂停（等待审批）
  {
    event: 'workflow_paused',
    data: {
      timestamp: new Date(Date.now() + 5100).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P1',
      metadata: {
        reason: '等待P1审批'
      }
    }
  },

  // 工作流恢复（审批通过）
  {
    event: 'workflow_resumed',
    data: {
      timestamp: new Date(Date.now() + 8000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P1',
      metadata: {
        decision: 'approved',
        feedback: '算法选择合理，继续执行'
      }
    }
  },

  // Phase 1: Algorithm Expert开始
  {
    event: 'phase_changed',
    data: {
      timestamp: new Date(Date.now() + 8100).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P1'
    }
  },

  {
    event: 'agent_started',
    data: {
      timestamp: new Date(Date.now() + 8200).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P1',
      agent_name: 'Algorithm Expert',
      metadata: { order: 1 }
    }
  },

  // Algorithm Expert输出
  {
    event: 'agent_output',
    data: {
      timestamp: new Date(Date.now() + 9000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      agent_name: 'Algorithm Expert',
      agent_output: {
        type: 'markdown',
        content: `# A* 算法设计方案

## 核心数据结构

\`\`\`python
class Node:
    def __init__(self, position, g=0, h=0):
        self.position = position  # (x, y)坐标
        self.g = g  # 从起点到当前节点的实际代价
        self.h = h  # 从当前节点到终点的启发式估计
        self.f = g + h  # 总评估函数
        self.parent = None
\`\`\`

## 启发式函数

采用 **曼哈顿距离** 作为启发式函数：

\`\`\`python
def heuristic(node, goal):
    return abs(node.x - goal.x) + abs(node.y - goal.y)
\`\`\`

## 时间复杂度

- 最坏情况: O(b^d)
- 平均情况: O(b^(d/2))

其中 b 为分支因子，d 为解的深度。`
      }
    }
  },

  // Algorithm Expert完成
  {
    event: 'agent_completed',
    data: {
      timestamp: new Date(Date.now() + 11000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P1',
      agent_name: 'Algorithm Expert'
    }
  },

  // Phase 2: Constraint Expert开始
  {
    event: 'phase_changed',
    data: {
      timestamp: new Date(Date.now() + 11500).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P2'
    }
  },

  {
    event: 'agent_started',
    data: {
      timestamp: new Date(Date.now() + 11600).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P2',
      agent_name: 'Constraint Expert',
      metadata: { order: 2 }
    }
  },

  // Constraint Expert输出
  {
    event: 'agent_output',
    data: {
      timestamp: new Date(Date.now() + 12500).toISOString(),
      workflow_id: 'wf-mock-success-001',
      agent_name: 'Constraint Expert',
      agent_output: {
        type: 'markdown',
        content: `# 约束条件分析

## 性能约束

- ⚡ **响应时间**: < 100ms
  - 优化策略: 采用优先队列（堆）
  - 预计性能: ~50ms (满足要求)

- 💾 **内存限制**: < 512MB
  - 节点存储优化
  - 访问记录压缩

## 功能约束

- 🚧 **动态障碍物**: 支持
- 🔄 **图动态更新**: 需要增量更新机制
- 📏 **网格大小**: 最大1000x1000

## 风险提示

⚠️ 在超大规模地图（>10000节点）时可能需要考虑分层路径规划。`
      }
    }
  },

  // Constraint Expert完成
  {
    event: 'agent_completed',
    data: {
      timestamp: new Date(Date.now() + 14000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P2',
      agent_name: 'Constraint Expert'
    }
  },

  // 快进到Code Implementation Expert
  {
    event: 'phase_changed',
    data: {
      timestamp: new Date(Date.now() + 15000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P3'
    }
  },

  {
    event: 'agent_started',
    data: {
      timestamp: new Date(Date.now() + 15100).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P3',
      agent_name: 'Code Implementation Expert',
      metadata: { order: 5 }
    }
  },

  {
    event: 'agent_output',
    data: {
      timestamp: new Date(Date.now() + 16000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      agent_name: 'Code Implementation Expert',
      agent_output: {
        type: 'code',
        language: 'python',
        content: `class AStarPathfinder:
    """A* 路径规划算法实现"""

    def __init__(self, grid):
        self.grid = grid
        self.open_list = []
        self.closed_set = set()

    def find_path(self, start, goal):
        """
        查找从start到goal的最短路径

        Args:
            start: 起点坐标 (x, y)
            goal: 终点坐标 (x, y)

        Returns:
            路径列表或None
        """
        start_node = Node(start, g=0, h=self.heuristic(start, goal))
        heapq.heappush(self.open_list, (start_node.f, start_node))

        while self.open_list:
            current = heapq.heappop(self.open_list)[1]

            if current.position == goal:
                return self.reconstruct_path(current)

            self.closed_set.add(current.position)

            for neighbor in self.get_neighbors(current):
                if neighbor.position in self.closed_set:
                    continue

                tentative_g = current.g + 1

                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + neighbor.h
                    heapq.heappush(self.open_list, (neighbor.f, neighbor))

        return None  # 无路径

    def heuristic(self, pos, goal):
        """曼哈顿距离启发式函数"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])`
      }
    }
  },

  {
    event: 'agent_completed',
    data: {
      timestamp: new Date(Date.now() + 18000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P3',
      agent_name: 'Code Implementation Expert'
    }
  },

  // 工作流完成
  {
    event: 'workflow_completed',
    data: {
      timestamp: new Date(Date.now() + 19000).toISOString(),
      workflow_id: 'wf-mock-success-001',
      phase: 'P4',
      metadata: {
        totalDuration: 19000,
        totalAgents: 8,
        successRate: 1.0
      }
    }
  }
]

/**
 * 失败场景的Mock事件流
 */
export const failureScenarioEvents: WorkflowEvent[] = [
  {
    event: 'workflow_started',
    data: {
      timestamp: new Date().toISOString(),
      workflow_id: 'wf-mock-failure-001',
      phase: 'P0'
    }
  },

  {
    event: 'agent_started',
    data: {
      timestamp: new Date(Date.now() + 1000).toISOString(),
      workflow_id: 'wf-mock-failure-001',
      phase: 'P0',
      agent_name: 'Orchestrator'
    }
  },

  {
    event: 'agent_output',
    data: {
      timestamp: new Date(Date.now() + 2000).toISOString(),
      workflow_id: 'wf-mock-failure-001',
      agent_name: 'Orchestrator',
      agent_output: {
        type: 'markdown',
        content: '正在分析问题...'
      }
    }
  },

  {
    event: 'agent_failed',
    data: {
      timestamp: new Date(Date.now() + 3000).toISOString(),
      workflow_id: 'wf-mock-failure-001',
      phase: 'P0',
      agent_name: 'Orchestrator',
      error_message: '模型API调用失败: Connection timeout',
      metadata: {
        errorCode: 'MODEL_API_ERROR',
        details: '连接超时，请检查网络或模型服务状态'
      }
    }
  },

  {
    event: 'workflow_failed',
    data: {
      timestamp: new Date(Date.now() + 3100).toISOString(),
      workflow_id: 'wf-mock-failure-001',
      error_message: '工作流执行失败',
      metadata: {
        failedAgent: 'Orchestrator',
        phase: 'P0',
        reason: '模型API调用失败'
      }
    }
  }
]

/**
 * 根据场景ID获取对应的事件流
 */
export function getScenarioEvents(scenario: 'success' | 'failure' | 'pause' = 'success'): WorkflowEvent[] {
  switch (scenario) {
    case 'success':
      return successScenarioEvents
    case 'failure':
      return failureScenarioEvents
    case 'pause':
      // 暂停场景 = 成功场景的前半部分（到P1审批）
      return successScenarioEvents.slice(0, 7)
    default:
      return successScenarioEvents
  }
}
