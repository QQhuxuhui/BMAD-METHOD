# Story 1.9: 实时工作流监控面板MVP

**Epic**: Epic 1 - Phase 1轻量级集成
**优先级**: P0
**状态**: Draft
**创建日期**: 2025-11-09
**预估工时**: 2-3天
**Story类型**: Frontend Feature

---

## 📋 User Story

**作为一个** BMAD系统用户
**我希望** 能够实时看到智能体工作流的执行过程和状态
**以便于** 直观了解系统运行情况，监控任务进度，及时发现问题

---

## 🎯 Story目标

实现前端工作流监控面板的MVP版本，采用**Mock First**策略，在后端SSE端点完成前即可开发和演示前端功能。

### 核心价值

1. **价值可见化** - 让后端智能体工作流的执行过程对用户可见
2. **快速反馈** - 开发过程中实时看到系统效果，加速迭代
3. **独立开发** - 前端使用Mock数据，不依赖后端完成进度
4. **演示能力** - 可向干系人展示系统界面和交互效果

---

## ✅ 验收标准

### AC1: 工作流状态实时显示

- [ ] 显示工作流整体状态：运行中/完成/失败/暂停
- [ ] 显示开始时间、已运行时长
- [ ] 支持工作流状态的实时更新（基于SSE事件流）
- [ ] 状态变化时有视觉反馈（颜色变化、动画效果）

### AC2: 智能体执行可视化

- [ ] 展示当前活跃的智能体（高亮显示）
- [ ] 显示智能体执行顺序和依赖关系
- [ ] 已完成的智能体显示为成功/失败状态
- [ ] 支持展开查看单个智能体的详细信息

### AC3: 进度跟踪

- [ ] 显示整体进度百分比
- [ ] 显示Phase 0-4的当前执行阶段
- [ ] 提供进度条或Timeline视图
- [ ] 实时更新当前执行步骤

### AC4: 输出流显示

- [ ] 实时展示智能体的输出内容
- [ ] 支持Markdown格式渲染
- [ ] 支持代码块的语法高亮
- [ ] 提供滚动查看历史输出
- [ ] 支持输出内容的搜索和过滤

### AC5: Mock数据模拟

- [ ] 实现Mock SSE服务器，模拟完整的工作流事件流
- [ ] 支持多种场景：成功完成、执行失败、人工中断
- [ ] 可配置的事件生成速度（快速演示/真实模拟）
- [ ] Mock数据结构与真实SSE端点保持一致

### AC6: 基础交互功能

- [ ] 支持启动新的工作流（调用Mock API）
- [ ] 提供刷新和清除历史记录功能
- [ ] 响应式设计，支持不同屏幕尺寸
- [ ] 良好的加载状态和错误处理

---

## 🎨 UI/UX设计要点

### 布局结构

```
┌─────────────────────────────────────────────────────┐
│  Header: 工作流监控面板                              │
├──────────────┬──────────────────────────────────────┤
│              │  WorkflowStatusCard                  │
│  WorkflowGraph│  - 状态: 运行中                      │
│              │  - 进度: 65% (Phase 2/4)             │
│  (拓扑图)    │  - 用时: 00:03:45                    │
│              ├──────────────────────────────────────┤
│              │  ActiveAgentsPanel                   │
│              │  □ Orchestrator (已完成)             │
│              │  ■ Algorithm Expert (执行中...)      │
│              │  □ Constraint Expert (待执行)        │
├──────────────┴──────────────────────────────────────┤
│  OutputStreamPanel (输出流)                         │
│  [算法专家] 分析问题域特征...                        │
│  - 问题类型: 智能路径规划                            │
│  - 推荐算法: A* 搜索算法                             │
└─────────────────────────────────────────────────────┘
```

### 视觉设计原则

1. **状态即视觉** - 用颜色和动画直观表达状态
   - 🟢 绿色：成功/完成
   - 🔵 蓝色：运行中（脉冲动画）
   - 🟡 黄色：等待/暂停
   - 🔴 红色：失败/错误

2. **信息层次** - 重要信息突出，细节可展开
   - 第一层：工作流整体状态
   - 第二层：当前执行阶段和智能体
   - 第三层：详细输出和日志

3. **实时反馈** - 所有状态变化都有即时视觉反馈
   - 智能体启动：淡入动画
   - 状态更新：颜色过渡
   - 新输出：滚动到最新内容

---

## 🛠️ 技术实现方案

### 技术栈

**前端框架**（已有）：

- Vue 3.5.22 (Composition API)
- TypeScript 5.9.3
- Ant Design Vue 4.2.6
- Pinia 2.3.1 (状态管理)
- @vueuse/core 14.0 (工具库)

**新增依赖**：

```json
{
  "@antv/g6": "^5.0.0", // 可选：工作流拓扑可视化
  "marked": "^12.0.0", // Markdown渲染
  "highlight.js": "^11.9.0" // 代码高亮
}
```

### 核心组件结构

```typescript
frontend/web/src/
├── views/
│   └── WorkflowMonitor/
│       ├── WorkflowMonitor.vue          // 主监控面板
│       ├── components/
│       │   ├── WorkflowStatusCard.vue    // 工作流状态卡片
│       │   ├── WorkflowGraph.vue         // 工作流拓扑图（简化版）
│       │   ├── AgentStatusList.vue       // 智能体状态列表
│       │   ├── ProgressTimeline.vue      // 进度时间线
│       │   └── OutputStream.vue          // 输出流显示
│       └── hooks/
│           ├── useSSE.ts                 // SSE流式接收Hook
│           └── useWorkflowState.ts       // 工作流状态管理Hook
│
├── stores/
│   └── workflow.ts                       // Pinia工作流状态Store
│
├── mocks/
│   ├── workflow-events.ts                // Mock事件数据
│   └── mock-sse-server.ts                // Mock SSE服务器
│
├── types/
│   └── workflow.ts                       // TypeScript类型定义
│
└── utils/
    ├── markdown-renderer.ts              // Markdown渲染工具
    └── event-stream-parser.ts            // SSE事件解析器
```

### 核心技术要点

#### 1. SSE流式接收Hook

```typescript
// hooks/useSSE.ts
import { ref, onUnmounted } from 'vue';

export interface SSEEvent {
  type: 'agent_start' | 'agent_output' | 'agent_complete' | 'workflow_complete' | 'error';
  agent?: string;
  content?: string;
  timestamp: number;
  metadata?: any;
}

export function useSSE(url: string) {
  const events = ref<SSEEvent[]>([]);
  const status = ref<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');
  const error = ref<Error | null>(null);

  let eventSource: EventSource | null = null;

  const connect = () => {
    eventSource = new EventSource(url);

    eventSource.onopen = () => {
      status.value = 'connected';
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as SSEEvent;
        events.value.push(data);
      } catch (e) {
        console.error('Failed to parse SSE event:', e);
      }
    };

    eventSource.onerror = (e) => {
      status.value = 'error';
      error.value = new Error('SSE connection failed');
      eventSource?.close();
    };
  };

  const disconnect = () => {
    eventSource?.close();
    status.value = 'disconnected';
  };

  onUnmounted(() => {
    disconnect();
  });

  return {
    events,
    status,
    error,
    connect,
    disconnect,
  };
}
```

#### 2. Mock SSE服务器

```typescript
// mocks/mock-sse-server.ts
import type { SSEEvent } from '@/hooks/useSSE';

export class MockSSEServer {
  private events: SSEEvent[] = [
    {
      type: 'agent_start',
      agent: 'Orchestrator',
      timestamp: Date.now(),
      metadata: { phase: 0 },
    },
    {
      type: 'agent_output',
      agent: 'Orchestrator',
      content: '# 问题分析\n\n分析用户请求：实现智能路径规划系统',
      timestamp: Date.now() + 1000,
    },
    {
      type: 'agent_complete',
      agent: 'Orchestrator',
      timestamp: Date.now() + 2000,
      metadata: {
        recommendation: '推荐使用A*算法',
        confidence: 0.95,
      },
    },
    {
      type: 'agent_start',
      agent: 'Algorithm Expert',
      timestamp: Date.now() + 3000,
      metadata: { phase: 1 },
    },
    // ... 更多事件
  ];

  private eventIndex = 0;
  private intervalId: number | null = null;
  private listeners: Array<(event: SSEEvent) => void> = [];

  start(intervalMs: number = 1500) {
    this.intervalId = window.setInterval(() => {
      if (this.eventIndex < this.events.length) {
        const event = this.events[this.eventIndex];
        this.listeners.forEach((listener) => listener(event));
        this.eventIndex++;
      } else {
        this.stop();
      }
    }, intervalMs);
  }

  stop() {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  onEvent(listener: (event: SSEEvent) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  reset() {
    this.stop();
    this.eventIndex = 0;
    this.listeners = [];
  }
}

export const mockSSEServer = new MockSSEServer();
```

#### 3. Pinia状态管理

```typescript
// stores/workflow.ts
import { defineStore } from 'pinia';
import type { SSEEvent } from '@/hooks/useSSE';

export interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: number;
  endTime?: number;
  output?: string;
}

export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    workflowId: '' as string,
    status: 'idle' as 'idle' | 'running' | 'paused' | 'completed' | 'failed',
    currentPhase: 0,
    progress: 0,
    startTime: 0,
    endTime: 0,
    agents: [] as AgentStatus[],
    events: [] as SSEEvent[],
  }),

  getters: {
    duration: (state) => {
      if (!state.startTime) return 0;
      const end = state.endTime || Date.now();
      return Math.floor((end - state.startTime) / 1000);
    },

    activeAgent: (state) => {
      return state.agents.find((a) => a.status === 'running');
    },

    completedAgents: (state) => {
      return state.agents.filter((a) => a.status === 'completed');
    },
  },

  actions: {
    processEvent(event: SSEEvent) {
      this.events.push(event);

      switch (event.type) {
        case 'agent_start':
          this.handleAgentStart(event);
          break;
        case 'agent_output':
          this.handleAgentOutput(event);
          break;
        case 'agent_complete':
          this.handleAgentComplete(event);
          break;
        case 'workflow_complete':
          this.handleWorkflowComplete(event);
          break;
      }
    },

    handleAgentStart(event: SSEEvent) {
      const agent = this.agents.find((a) => a.name === event.agent);
      if (agent) {
        agent.status = 'running';
        agent.startTime = event.timestamp;
      }
    },

    handleAgentOutput(event: SSEEvent) {
      const agent = this.agents.find((a) => a.name === event.agent);
      if (agent && event.content) {
        agent.output = (agent.output || '') + event.content;
      }
    },

    handleAgentComplete(event: SSEEvent) {
      const agent = this.agents.find((a) => a.name === event.agent);
      if (agent) {
        agent.status = 'completed';
        agent.endTime = event.timestamp;
      }
      this.updateProgress();
    },

    handleWorkflowComplete(event: SSEEvent) {
      this.status = 'completed';
      this.endTime = event.timestamp;
      this.progress = 100;
    },

    updateProgress() {
      const completed = this.completedAgents.length;
      const total = this.agents.length;
      this.progress = total > 0 ? Math.floor((completed / total) * 100) : 0;
    },

    reset() {
      this.$reset();
    },
  },
});
```

---

## 📝 实施计划

### Day 1: 核心基础设施（6-8小时）

#### 任务

1. ✅ 创建组件目录结构
2. ✅ 定义TypeScript类型
3. ✅ 实现useSSE Hook
4. ✅ 创建Mock SSE服务器
5. ✅ 建立Pinia状态管理

#### 交付物

- 完整的组件骨架
- 可运行的Mock数据模拟
- 基础状态管理逻辑

### Day 2: UI组件实现（8-10小时）

#### 任务

1. ✅ 实现WorkflowStatusCard（工作流状态卡片）
2. ✅ 实现AgentStatusList（智能体状态列表）
3. ✅ 实现OutputStream（输出流显示）
4. ✅ 实现ProgressTimeline（进度时间线）
5. ✅ 实现WorkflowMonitor主面板（整合所有组件）

#### 交付物

- 所有核心UI组件
- 组件之间的数据流通
- 基础样式和布局

### Day 3: 交互优化和测试（6-8小时）

#### 任务

1. ✅ 添加状态变化动画和视觉反馈
2. ✅ 实现Markdown渲染和代码高亮
3. ✅ 优化响应式布局
4. ✅ 添加错误处理和边界情况
5. ✅ 端到端测试和用户体验优化

#### 交付物

- 完整可演示的前端监控面板
- 流畅的交互体验
- 测试报告和使用文档

---

## 🧪 测试策略

### 功能测试

1. **Mock数据场景测试**
   - 成功完成的工作流
   - 执行失败的工作流
   - 中途暂停的工作流
   - 长时间运行的工作流

2. **UI交互测试**
   - 状态实时更新
   - 输出流滚动和搜索
   - 响应式布局适配
   - 错误状态显示

3. **性能测试**
   - 大量事件处理（1000+ events）
   - 长时间运行稳定性
   - 内存泄漏检测

### 用户体验测试

1. **可用性测试**
   - 首次使用者能否理解界面
   - 关键信息是否突出
   - 操作流程是否流畅

2. **视觉一致性**
   - 与Ant Design Vue设计语言一致
   - 颜色和图标语义清晰
   - 动画效果自然

---

## 🔄 后续集成计划

### 与Story 1.7集成

当后端SSE端点（Story 1.7）完成后：

1. **替换Mock服务器**
   - 将Mock SSE URL替换为真实API端点
   - 验证事件格式兼容性

2. **数据格式对齐**
   - 确保前后端事件结构一致
   - 处理任何格式差异

3. **端到端测试**
   - 前后端联调测试
   - 验证完整工作流

### 预留扩展点

- 支持多个工作流并发监控
- 工作流历史记录查询
- 导出工作流执行报告
- Human-in-Loop确认界面（Story 1.10）

---

## 📊 成功指标

### 功能完整性

- ✅ 所有验收标准100%通过
- ✅ Mock数据模拟覆盖所有场景

### 开发效率

- ✅ 2-3天完成MVP交付
- ✅ 无阻塞等待后端依赖

### 用户价值

- ✅ 系统效果可见可演示
- ✅ 干系人能够直观理解系统运行

### 代码质量

- ✅ TypeScript类型覆盖100%
- ✅ ESLint零警告
- ✅ 组件单元测试覆盖>80%

---

## 📎 参考资料

- [PRD: LangGraph集成方案](/docs/langgraph集成方案.md)
- [Story 1.7: SSE流式传输前端集成](/docs/langgraph集成方案.md#故事-17实现sse流式传输前端集成)
- [Vue 3 Composition API文档](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Ant Design Vue组件库](https://antdv.com/components/overview)
- [Server-Sent Events (SSE) MDN文档](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

## 📝 变更日志

| 日期       | 版本 | 描述              | 作者                    |
| ---------- | ---- | ----------------- | ----------------------- |
| 2025-11-09 | v1.0 | 创建Story 1.9文档 | Mary (Business Analyst) |

---

## ✅ Story签署

**Product Owner**: _待签署_
**Scrum Master**: _待签署_
**Development Team**: _待签署_

---

**状态**: Draft → 待审查
