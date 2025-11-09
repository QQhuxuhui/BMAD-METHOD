# Story 1.10: 智能体协作可视化增强与UI体验优化

**Epic**: Epic 1 - Phase 1轻量级集成
**优先级**: P1
**状态**: Draft
**创建日期**: 2025-11-09
**预估工时**: 3-4天
**Story类型**: Frontend Feature Enhancement

---

## 📋 User Story

**作为一个** BMAD系统用户
**我希望** 通过图形化的方式直观地看到智能体的协作关系和执行状态
**以便于** 更清晰地理解工作流程、快速定位问题，并查看各阶段的交付物

---

## 🎯 Story目标

在Story 1.9 MVP基础上，进行UI/UX的重大升级，从列表式展示升级为图形化可视化展示，提升系统的专业性和易用性。

### 核心价值

1. **可视化协作关系** - 用图形直观展示8个智能体的协作流程和依赖关系
2. **交付物快速访问** - 在可视化图上标记Phase交付物，点击即可查看
3. **拟人化体验** - 中文名称+头像让智能体更友好、更易理解
4. **专业视觉呈现** - 提升整体UI质感，增强产品的专业度

---

## ✅ 验收标准

### AC1: 智能体协作流程图可视化

- [ ] 使用AntV G6实现智能体协作流程图
- [ ] 8个智能体节点清晰展示，包含：
  - [ ] 智能体中文名称
  - [ ] 智能体头像/图标
  - [ ] 当前执行状态（待执行/执行中/已完成/失败）
- [ ] 节点之间的连线展示执行顺序和依赖关系
- [ ] 支持5个Phase (P0-P4)的阶段标记
- [ ] 图形布局清晰，易于理解工作流结构

### AC2: 实时状态更新与视觉反馈

- [ ] 节点状态随工作流执行实时更新
- [ ] 不同状态有明显的视觉区分：
  - [ ] 待执行：灰色/默认样式
  - [ ] 执行中：蓝色/动画效果（呼吸灯、loading动画等）
  - [ ] 已完成：绿色/完成图标
  - [ ] 失败：红色/错误图标
- [ ] 状态切换有流畅的过渡动画
- [ ] 当前执行的智能体高亮显示

### AC3: Phase交付物标记与查看

- [ ] 在流程图上标记5个Phase的位置
- [ ] 每个Phase节点显示交付物数量或图标
- [ ] 点击Phase节点可查看该阶段的交付物列表
- [ ] 交付物Modal展示：
  - [ ] 交付物名称
  - [ ] 交付物描述
  - [ ] 交付物内容（支持Markdown）
  - [ ] 相关智能体信息

### AC4: 智能体拟人化与中文化

- [ ] 所有智能体使用中文名称：
  - [ ] Orchestrator → 🎯 总指挥
  - [ ] Algorithm Expert → 🧮 算法专家
  - [ ] Constraint Expert → ⚖️ 约束专家
  - [ ] Objective Expert → 🎯 目标专家
  - [ ] Domain Expert → 🏢 领域专家
  - [ ] Code Implementation Expert → 🐍 Python专家
  - [ ] Extension Expert → 🔌 扩展专家
  - [ ] Quality Expert → ✅ 质量专家
- [ ] 每个智能体有独特的头像/图标
- [ ] 头像支持动态变化（可选：执行中时有动画效果）

### AC5: 智能体输出优化

- [ ] AgentStatusList中的输出预览支持Markdown渲染
- [ ] Modal中的智能体输出支持Markdown渲染（修复Story 1.9遗留问题）
- [ ] 代码块支持语法高亮
- [ ] 长文本内容自动折叠，可展开查看

### AC6: 交互体验优化

- [ ] 流程图支持缩放和平移
- [ ] 点击智能体节点可查看详细信息（复用现有Modal）
- [ ] 支持键盘快捷键（可选）：
  - [ ] Space: 播放/暂停
  - [ ] +/-: 缩放
  - [ ] 方向键: 平移
- [ ] 响应式设计，适配不同屏幕尺寸
- [ ] 流畅的加载和错误处理
- [ ] 性能优化：大量节点时保持流畅

---

## 🎨 UI/UX设计要点

### 布局调整

**当前布局** (Story 1.9):

```
┌─────────────────────────────────────────────────────┐
│  Header: 工作流监控面板                              │
├──────────────┬──────────────────────────────────────┤
│  WorkflowStatus │  OutputStreamPanel                │
│  AgentList      │                                    │
└──────────────┴──────────────────────────────────────┘
```

**新布局** (Story 1.10):

```
┌─────────────────────────────────────────────────────┐
│  Header: 工作流监控面板 + 工具栏（缩放、重置等）      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  WorkflowGraph (AntV G6)                             │
│  ┌───────┐     ┌───────┐     ┌───────┐              │
│  │总指挥│────→│算法  │────→│约束  │              │
│  │  🎯  │     │专家🧮│     │专家⚖️│              │
│  └───────┘     └───────┘     └───────┘              │
│       │             │             │                   │
│       ↓        [P1交付物]        ↓                   │
│  ┌───────┐                  ┌───────┐               │
│  │Python│                  │目标  │               │
│  │专家🐍│                  │专家🎯│               │
│  └───────┘                  └───────┘               │
│                                                       │
├─────────────────┬───────────────────────────────────┤
│ WorkflowStatus  │  OutputStreamPanel                │
│ (简化版)        │  (保持现有功能)                   │
└─────────────────┴───────────────────────────────────┘
```

### 视觉设计原则

1. **图形优先** - 主要信息通过可视化图形传达
2. **状态即颜色** - 用颜色编码快速识别状态
3. **层次清晰** - 主要流程图 + 辅助信息面板
4. **交互友好** - 支持点击、缩放、平移等交互
5. **性能优先** - 确保动画流畅，无卡顿

---

## 🛠️ 技术方案

### 核心技术栈

**AntV G6 集成**:

```bash
npm install @antv/g6
```

**特性使用**:

- Graph实例管理
- 自定义节点（智能体节点、Phase节点）
- 自定义边（带箭头的连线）
- 布局算法（Dagre有向图布局）
- 状态管理（节点状态切换）
- 事件监听（点击、hover等）

**组件结构**:

```
views/WorkflowMonitor/
├── WorkflowMonitor.vue (主容器，布局调整)
├── components/
│   ├── WorkflowGraph.vue (NEW - G6流程图)
│   ├── WorkflowStatusCard.vue (简化版)
│   ├── AgentStatusList.vue (可选保留或移除)
│   ├── OutputStream.vue (保持)
│   └── PhaseDeliverableModal.vue (NEW - 交付物查看)
```

### 数据结构设计

**智能体配置**:

```typescript
interface AgentConfig {
  id: string;
  nameEn: string;
  nameCn: string;
  icon: string; // Emoji或图标
  description: string;
  phase: number; // 所属Phase
  dependencies: string[]; // 依赖的智能体ID
}

// 8个智能体配置
const AGENTS_CONFIG: AgentConfig[] = [
  { id: 'orchestrator', nameEn: 'Orchestrator', nameCn: '总指挥', icon: '🎯', phase: 0, dependencies: [] },
  { id: 'algorithm', nameEn: 'Algorithm Expert', nameCn: '算法专家', icon: '🧮', phase: 1, dependencies: ['orchestrator'] },
  // ...
];
```

**Phase交付物配置**:

```typescript
interface PhaseDeliverable {
  phase: number;
  name: string;
  description: string;
  content: string; // Markdown内容
  relatedAgents: string[];
}

const PHASE_DELIVERABLES: PhaseDeliverable[] = [
  {
    phase: 1,
    name: 'P1交付物：问题分析报告',
    description: '总指挥和算法专家的分析成果',
    content: '# 问题分析报告\n...',
    relatedAgents: ['orchestrator', 'algorithm'],
  },
  // ...
];
```

### G6图配置

**节点定义**:

```javascript
// 智能体节点
G6.registerNode('agent-node', {
  draw(cfg, group) {
    // 圆形背景
    const circle = group.addShape('circle', {
      attrs: {
        r: 40,
        fill: cfg.style.fill,
        stroke: cfg.style.stroke,
        lineWidth: 3,
      },
    });

    // 头像/图标
    const icon = group.addShape('text', {
      attrs: {
        text: cfg.icon,
        fontSize: 24,
        textAlign: 'center',
        textBaseline: 'middle',
        y: -5,
      },
    });

    // 中文名称
    const label = group.addShape('text', {
      attrs: {
        text: cfg.nameCn,
        fontSize: 12,
        textAlign: 'center',
        textBaseline: 'middle',
        y: 20,
        fill: '#333',
      },
    });

    return circle;
  },

  setState(name, value, item) {
    const group = item.getContainer();
    const shape = group.get('children')[0];

    if (name === 'running') {
      shape.animate(
        {
          r: 45,
          opacity: 0.8,
        },
        {
          duration: 500,
          easing: 'easeCubic',
          repeat: true,
        },
      );
    }
  },
});

// Phase节点
G6.registerNode('phase-node', {
  // 矩形节点，显示Phase信息和交付物数量
});
```

**布局配置**:

```javascript
const graph = new G6.Graph({
  container: 'graph-container',
  width: 1200,
  height: 800,
  layout: {
    type: 'dagre', // 有向图布局
    rankdir: 'TB', // 从上到下
    nodesep: 60,
    ranksep: 100,
  },
  defaultNode: {
    type: 'agent-node',
    size: 80,
  },
  defaultEdge: {
    type: 'polyline',
    style: {
      endArrow: true,
      lineWidth: 2,
      stroke: '#999',
    },
  },
  modes: {
    default: ['drag-canvas', 'zoom-canvas', 'click-select'],
  },
});
```

---

## 📋 任务分解

### Phase 1: 环境搭建与基础集成 (Day 1)

- [ ] **Task 1.1**: 安装和配置AntV G6 (AC1)
  - [ ] 安装 @antv/g6 依赖
  - [ ] 创建 WorkflowGraph.vue 组件
  - [ ] 验证G6基础渲染功能

- [ ] **Task 1.2**: 智能体数据配置 (AC4)
  - [ ] 创建智能体配置文件 (AGENTS_CONFIG)
  - [ ] 定义8个智能体的中文名称和图标
  - [ ] 创建依赖关系映射

- [ ] **Task 1.3**: G6自定义节点实现 (AC1, AC4)
  - [ ] 注册 agent-node 节点类型
  - [ ] 实现节点渲染（圆形+图标+中文名称）
  - [ ] 注册 phase-node 节点类型（可选）

- [ ] **Task 1.4**: 基础图形渲染 (AC1)
  - [ ] 根据AGENTS_CONFIG生成节点和边数据
  - [ ] 配置Dagre布局算法
  - [ ] 渲染8个智能体节点
  - [ ] 渲染节点间的连接线

### Phase 2: 状态管理与实时更新 (Day 2)

- [ ] **Task 2.1**: 节点状态系统 (AC2)
  - [ ] 定义节点状态样式（pending/running/completed/failed）
  - [ ] 实现状态切换动画
  - [ ] 为running状态添加呼吸灯效果

- [ ] **Task 2.2**: 与Pinia Store集成 (AC2)
  - [ ] 监听workflowStore的agents状态变化
  - [ ] 实时更新G6节点状态
  - [ ] 高亮当前执行的智能体

- [ ] **Task 2.3**: Phase交付物数据准备 (AC3)
  - [ ] 创建PHASE_DELIVERABLES配置
  - [ ] 定义5个Phase的交付物内容（Mock数据）
  - [ ] 在图上添加Phase标记节点或区域

### Phase 3: 交互功能实现 (Day 3)

- [ ] **Task 3.1**: 节点点击交互 (AC6)
  - [ ] 监听智能体节点点击事件
  - [ ] 复用现有的智能体详情Modal
  - [ ] 传递正确的智能体数据

- [ ] **Task 3.2**: Phase交付物Modal (AC3)
  - [ ] 创建 PhaseDeliverableModal.vue 组件
  - [ ] 实现交付物列表展示
  - [ ] 支持Markdown内容渲染
  - [ ] 显示相关智能体信息

- [ ] **Task 3.3**: 图形交互优化 (AC6)
  - [ ] 配置缩放和平移功能
  - [ ] 添加工具栏（缩放按钮、重置视图等）
  - [ ] 实现键盘快捷键（可选）

- [ ] **Task 3.4**: Modal Markdown渲染修复 (AC5)
  - [ ] 修复WorkflowMonitor.vue中的智能体输出Modal
  - [ ] 使用formatOutput函数处理Markdown
  - [ ] 应用markdown-body样式
  - [ ] 测试代码高亮效果

### Phase 4: 布局优化与集成 (Day 3-4)

- [ ] **Task 4.1**: WorkflowMonitor布局重构
  - [ ] 调整主布局，给WorkflowGraph预留主要空间
  - [ ] WorkflowStatusCard简化为顶部工具栏
  - [ ] OutputStream保持在底部或侧边
  - [ ] AgentStatusList评估是否保留

- [ ] **Task 4.2**: 响应式适配 (AC6)
  - [ ] 桌面布局（>1200px）
  - [ ] 平板布局（768-1200px）
  - [ ] 手机布局（<768px，可能隐藏图形或简化）

- [ ] **Task 4.3**: 性能优化 (AC6)
  - [ ] 优化G6渲染性能
  - [ ] 减少不必要的重新渲染
  - [ ] 添加loading状态

- [ ] **Task 4.4**: 视觉优化
  - [ ] 调整颜色方案，提升专业感
  - [ ] 优化动画效果
  - [ ] 统一UI风格

### Phase 5: 测试与文档 (Day 4)

- [ ] **Task 5.1**: 端到端测试
  - [ ] 使用Playwright MCP测试流程图渲染
  - [ ] 测试节点状态实时更新
  - [ ] 测试交互功能（点击、缩放、平移）
  - [ ] 测试Phase交付物查看
  - [ ] 测试响应式布局

- [ ] **Task 5.2**: Mock场景测试
  - [ ] 成功场景：完整工作流执行
  - [ ] 失败场景：智能体执行失败
  - [ ] 暂停/恢复场景

- [ ] **Task 5.3**: 文档更新
  - [ ] 更新Story状态为Completed
  - [ ] 记录实际工时
  - [ ] 添加截图到文档
  - [ ] 更新README（如需要）

---

## 📝 Dev Notes

### 相关源代码结构

**当前工作流监控代码位置**:

```
frontend/web/src/
├── views/WorkflowMonitor/
│   ├── WorkflowMonitor.vue (主容器)
│   └── components/
│       ├── WorkflowStatusCard.vue
│       ├── AgentStatusList.vue
│       └── OutputStream.vue
├── stores/workflow.ts (Pinia Store)
├── hooks/useWorkflowStream.ts (SSE Hook)
├── types/workflow.ts (TypeScript类型)
└── mocks/
    ├── mock-sse-server.ts
    └── workflow-events.ts
```

**智能体配置位置**:

```typescript
// frontend/web/src/stores/workflow.ts
const AGENTS = [
  { id: 'orchestrator', name: 'Orchestrator', status: 'pending' },
  { id: 'algorithm_expert', name: 'Algorithm Expert', status: 'pending' },
  // ... 8个智能体
];

const PHASES = [
  { id: 0, name: 'P0', description: '问题理解与分解' },
  { id: 1, name: 'P1', description: '算法设计' },
  // ... 5个Phase
];
```

### AntV G6 文档参考

- 官方文档: https://g6.antv.antgroup.com/
- 快速开始: https://g6.antv.antgroup.com/manual/getting-started
- 自定义节点: https://g6.antv.antgroup.com/manual/middle/elements/nodes/custom-node
- 状态管理: https://g6.antv.antgroup.com/manual/middle/states/state
- 布局算法: https://g6.antv.antgroup.com/manual/middle/layout/graph-layout
- 事件处理: https://g6.antv.antgroup.com/manual/middle/events/event

### 重要实现细节

**1. 智能体中英文映射**:

```typescript
const AGENT_NAME_MAP = {
  Orchestrator: '总指挥',
  'Algorithm Expert': '算法专家',
  'Constraint Expert': '约束专家',
  'Objective Expert': '目标专家',
  'Domain Expert': '领域专家',
  'Code Implementation Expert': 'Python专家',
  'Extension Expert': '扩展专家',
  'Quality Expert': '质量专家',
};
```

**2. 智能体图标配置**:

```typescript
const AGENT_ICONS = {
  orchestrator: '🎯',
  algorithm_expert: '🧮',
  constraint_expert: '⚖️',
  objective_expert: '🎯',
  domain_expert: '🏢',
  code_implementation_expert: '🐍',
  extension_expert: '🔌',
  quality_expert: '✅',
};
```

**3. Phase交付物内容（示例）**:

```typescript
const PHASE_DELIVERABLES = {
  0: {
    name: 'P0交付物：问题分析报告',
    content: `
# 问题分析报告

**问题类型**: 路径规划问题
**核心挑战**: 实时性、动态障碍物
**推荐算法**: A*搜索算法
    `,
  },
  1: {
    name: 'P1交付物：算法设计方案',
    content: `
# A*算法设计方案

## 核心数据结构
\`\`\`python
class Node:
    def __init__(self, position, g=0, h=0):
        self.position = position
        self.g = g
        self.h = h
\`\`\`
    `,
  },
  // ... P2, P3, P4
};
```

**4. G6与Vue响应式集成**:

```typescript
// 监听Store变化，更新G6节点状态
watch(
  () => workflowStore.agents,
  (newAgents) => {
    newAgents.forEach((agent) => {
      const node = graph.findById(agent.id);
      if (node) {
        // 更新节点状态
        graph.setItemState(node, 'running', agent.status === 'running');
        graph.setItemState(node, 'completed', agent.status === 'completed');
        graph.setItemState(node, 'failed', agent.status === 'failed');
      }
    });
  },
  { deep: true },
);
```

### 已知问题和解决方案

**问题1**: Story 1.9的Modal不支持Markdown渲染

- **原因**: WorkflowMonitor.vue中的Modal使用了`<pre>`标签直接显示文本
- **解决**: 将`formatOutput`函数应用到Modal中，使用`v-html`渲染HTML

**问题2**: G6图形可能在容器尺寸变化时显示异常

- **解决**: 监听window resize事件，调用`graph.changeSize(width, height)`

**问题3**: 移动端显示复杂图形可能性能较差

- **解决**: 在小屏幕上可以切换为简化视图或列表视图

### Testing

#### 测试文件位置

- Playwright E2E测试（如需要）

#### 测试标准

- 所有验收标准必须通过测试验证
- 使用Playwright MCP进行端到端测试
- 测试覆盖：
  - 图形正常渲染
  - 节点状态实时更新
  - 交互功能（点击、缩放、平移）
  - Phase交付物查看
  - Markdown渲染
  - 响应式布局

#### 测试场景

1. **基础渲染测试**: 验证8个智能体节点正确显示
2. **状态更新测试**: 启动工作流，验证节点状态实时变化
3. **交互测试**: 点击节点查看详情，缩放平移图形
4. **交付物测试**: 点击Phase标记，查看交付物内容
5. **响应式测试**: 测试桌面/平板/手机三种尺寸

---

## 📊 Change Log

| Date       | Version | Description                   | Author     |
| ---------- | ------- | ----------------------------- | ---------- |
| 2025-11-09 | 1.0     | Story创建，定义需求和验收标准 | Sarah (PO) |

---

## 🚀 Dev Agent Record

_(此部分由开发智能体在实现过程中填写)_

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

## ✅ QA Results

_(此部分由QA智能体在验收测试后填写)_
