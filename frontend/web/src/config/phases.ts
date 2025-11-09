/**
 * Phase交付物配置文件
 * Story 1.10: Phase交付物标记与查看
 */

export interface PhaseConfig {
  /** Phase编号 */
  id: number
  /** Phase名称 */
  name: string
  /** Phase描述 */
  description: string
  /** 相关智能体ID列表 */
  relatedAgents: string[]
}

export interface PhaseDeliverable {
  /** 所属Phase */
  phase: number
  /** 交付物名称 */
  name: string
  /** 交付物描述 */
  description: string
  /** 交付物内容（Markdown格式） */
  content: string
  /** 相关智能体ID列表 */
  relatedAgents: string[]
}

/**
 * 5个Phase配置 (P0-P4)
 */
export const PHASES_CONFIG: PhaseConfig[] = [
  {
    id: 0,
    name: 'P0',
    description: '问题理解与分解',
    relatedAgents: ['orchestrator'],
  },
  {
    id: 1,
    name: 'P1',
    description: '算法设计',
    relatedAgents: ['orchestrator', 'algorithm'],
  },
  {
    id: 2,
    name: 'P2',
    description: '约束与目标建模',
    relatedAgents: ['constraint', 'objective', 'domain'],
  },
  {
    id: 3,
    name: 'P3',
    description: '代码实现',
    relatedAgents: ['python', 'extension'],
  },
  {
    id: 4,
    name: 'P4',
    description: '质量验证',
    relatedAgents: ['quality'],
  },
]

/**
 * Phase交付物配置（Mock数据）
 * 实际使用时，这些数据应该从后端API获取
 */
export const PHASE_DELIVERABLES: PhaseDeliverable[] = [
  {
    phase: 0,
    name: 'P0交付物：问题分析报告',
    description: '总指挥完成的问题分解和分析结果',
    content: `# 问题分析报告

## 问题概述
本次任务的核心是解决**路径规划优化问题**，需要在复杂环境中找到最优路径。

## 问题分解
1. **输入数据分析**
   - 起点和终点坐标
   - 障碍物信息
   - 地图尺寸和约束

2. **核心挑战**
   - 实时性要求高
   - 动态障碍物处理
   - 多目标优化

## 推荐方案
基于问题特征，推荐使用 **A*搜索算法** 或 **Dijkstra算法**。

## 下一步计划
- 交由算法专家进行详细算法设计
- 确定具体的启发式函数
`,
    relatedAgents: ['orchestrator'],
  },
  {
    phase: 1,
    name: 'P1交付物：算法设计方案',
    description: '算法专家完成的算法选择和设计文档',
    content: `# A*算法设计方案

## 算法选择理由
A*算法结合了Dijkstra的最优性和贪心算法的效率，适合本问题场景。

## 核心数据结构
\`\`\`python
class Node:
    def __init__(self, position, g=0, h=0):
        self.position = position
        self.g = g  # 起点到当前节点的实际代价
        self.h = h  # 当前节点到终点的启发式代价
        self.f = g + h  # 总代价
        self.parent = None
\`\`\`

## 启发式函数
使用**曼哈顿距离**作为启发式函数：
\`\`\`python
def heuristic(node, goal):
    return abs(node.x - goal.x) + abs(node.y - goal.y)
\`\`\`

## 算法流程
1. 初始化开放列表和关闭列表
2. 将起点加入开放列表
3. 循环直到找到终点或开放列表为空
4. 回溯路径

## 复杂度分析
- **时间复杂度**: O(b^d)
- **空间复杂度**: O(b^d)
其中b为分支因子，d为解的深度。
`,
    relatedAgents: ['algorithm'],
  },
  {
    phase: 2,
    name: 'P2交付物：约束与目标模型',
    description: '约束专家、目标专家和领域专家完成的建模文档',
    content: `# 约束与目标模型

## 硬约束条件
1. **边界约束**
   - 路径必须在地图边界内
   - 不能穿越障碍物

2. **连通性约束**
   - 路径必须连续
   - 相邻节点必须可达

## 软约束条件
1. **平滑度约束**
   - 尽量减少转弯次数
   - 路径应该相对平滑

2. **安全距离约束**
   - 与障碍物保持最小安全距离

## 优化目标函数
\`\`\`python
def objective_function(path):
    # 多目标加权和
    length_cost = calculate_path_length(path)
    smoothness_cost = calculate_smoothness(path)
    safety_cost = calculate_safety_margin(path)

    return w1 * length_cost + w2 * smoothness_cost + w3 * safety_cost
\`\`\`

## 领域知识整合
- 基于物流配送领域的最佳实践
- 考虑车辆转弯半径
- 优先选择主干道路
`,
    relatedAgents: ['constraint', 'objective', 'domain'],
  },
  {
    phase: 3,
    name: 'P3交付物：Python实现代码',
    description: 'Python专家和扩展专家完成的代码实现',
    content: `# Python代码实现

## 核心算法实现
\`\`\`python
def a_star_search(grid, start, goal):
    """
    A*搜索算法实现

    Args:
        grid: 二维地图数组
        start: 起点坐标 (x, y)
        goal: 终点坐标 (x, y)

    Returns:
        path: 路径列表，从起点到终点
    """
    open_list = PriorityQueue()
    closed_set = set()

    # 创建起点节点
    start_node = Node(start)
    start_node.h = heuristic(start, goal)
    open_list.put(start_node)

    while not open_list.empty():
        current = open_list.get()

        # 找到目标
        if current.position == goal:
            return reconstruct_path(current)

        closed_set.add(current.position)

        # 扩展邻居节点
        for neighbor_pos in get_neighbors(current.position, grid):
            if neighbor_pos in closed_set:
                continue

            neighbor = Node(neighbor_pos)
            neighbor.g = current.g + 1
            neighbor.h = heuristic(neighbor_pos, goal)
            neighbor.parent = current

            open_list.put(neighbor)

    return None  # 无解
\`\`\`

## 工具函数
\`\`\`python
def get_neighbors(position, grid):
    """获取有效邻居节点"""
    x, y = position
    neighbors = [
        (x+1, y), (x-1, y),
        (x, y+1), (x, y-1)
    ]
    return [n for n in neighbors if is_valid(n, grid)]

def is_valid(position, grid):
    """检查位置是否有效"""
    x, y = position
    if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]):
        return False
    return grid[x][y] != 1  # 1表示障碍物
\`\`\`

## 性能优化
- 使用优先队列优化节点选择
- 使用集合加速关闭列表查找
- 预计算启发式值

## 扩展功能
- 支持对角线移动
- 支持动态障碍物
- 提供路径可视化接口
`,
    relatedAgents: ['python', 'extension'],
  },
  {
    phase: 4,
    name: 'P4交付物：测试验证报告',
    description: '质量专家完成的测试和验证结果',
    content: `# 测试验证报告

## 测试覆盖率
- **单元测试覆盖率**: 95%
- **集成测试覆盖率**: 88%
- **端到端测试**: 通过

## 测试用例
### 基础功能测试
\`\`\`python
def test_basic_pathfinding():
    grid = create_simple_grid()
    path = a_star_search(grid, (0, 0), (9, 9))
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (9, 9)
\`\`\`

### 障碍物避让测试
- ✅ 单个障碍物避让
- ✅ 复杂障碍物场景
- ✅ 迷宫式地图测试

### 边界条件测试
- ✅ 起点等于终点
- ✅ 无解场景处理
- ✅ 大规模地图性能

## 性能基准测试
| 地图大小 | 平均耗时 | 内存占用 |
|---------|---------|----------|
| 10x10   | 2ms     | 1.2MB    |
| 50x50   | 45ms    | 8.5MB    |
| 100x100 | 180ms   | 32MB     |

## 质量评估
- ✅ 代码规范: 符合PEP 8
- ✅ 文档完整性: 90%
- ✅ 类型标注: 完整
- ✅ 错误处理: 完善

## 改进建议
1. 对超大地图实施分块处理
2. 添加路径缓存机制
3. 提供更多启发式函数选项
`,
    relatedAgents: ['quality'],
  },
]

/**
 * 根据Phase ID获取配置
 */
export function getPhaseConfig(phaseId: number): PhaseConfig | undefined {
  return PHASES_CONFIG.find((phase) => phase.id === phaseId)
}

/**
 * 根据Phase ID获取交付物
 */
export function getPhaseDeliverables(phaseId: number): PhaseDeliverable[] {
  return PHASE_DELIVERABLES.filter((deliverable) => deliverable.phase === phaseId)
}

/**
 * 获取所有Phase的交付物数量统计
 */
export function getDeliverablesCount(): Record<number, number> {
  const counts: Record<number, number> = {}

  PHASE_DELIVERABLES.forEach((deliverable) => {
    counts[deliverable.phase] = (counts[deliverable.phase] || 0) + 1
  })

  return counts
}
