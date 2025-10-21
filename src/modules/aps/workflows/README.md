# APS Workflows

APS模块的工作流定义目录，实现Phase 0-4完整调度求解流程。

## 工作流架构

### 主编排流程

**scheduling-orchestration/** - Phase 0-4完整流程

- 入口：`workflow.yaml`
- 描述：调度优化端到端求解，包含双模式交互和Todo List追踪
- 预计时间：70-130分钟（取决于模式）
- 使用场景：完整调度问题求解

### 支撑工作流

**todo-management/** - Todo List管理

- 入口：`workflow.yaml`
- 描述：任务规划、追踪、偏离检测
- Phase：Phase 0核心机制
- 使用场景：所有需要任务规划的流程

**interaction-modes/** - 双模式交互

- 模式A：集中确认模式（20-25分钟）
- 模式B：增量确认模式（30-40分钟）
- 使用场景：Phase 0.5模式选择

### Phase专属工作流

**phase-1-requirements/** - 需求分析

- Phase：Phase 1
- 描述：深入理解用户需求，偏离检测
- 预计时间：10-15分钟

**phase-1.5-modeling/** - 十要素建模

- Phase：Phase 1.5
- 描述：构建TenElementModel统一真相源
- 预计时间：5-15分钟（取决于模式）
- 特性：双模式确认支持

**phase-2-coordination/** - 专家协调

- Phase：Phase 2
- 描述：调用4位专家并行/串行分析
- 预计时间：10-48分钟（取决于模式）
- 特性：条件流程（mode_a并行 vs mode_b串行）

**consistency-check/** - 一致性校验

- 使用场景：Phase 2专家协调后、Phase 3集成前
- 描述：跨专家建议一致性验证

**phase-3-integration/** - 方案集成

- Phase：Phase 3
- 描述：融合专家建议，生成可执行代码
- 预计时间：15-20分钟

**phase-4-quality/** - 质量保证

- Phase：Phase 4
- 描述：质量门禁验证，确保可交付
- 预计时间：9-12分钟

## 工作流调用模式

### 1. 命令行调用（通过agent menu）

```bash
bmad aps
# 选择命令: *start-scheduling
```

### 2. 程序化调用（workflow引用）

```yaml
- step_id: '2.1'
  name: '调用专家协调'
  action: 'run-workflow'
  target: 'bmad/aps/workflows/phase-2-coordination/workflow.yaml'
  inputs:
    - ten_element_model
```

### 3. 任务调用（task exec）

```yaml
- step_id: '1.1'
  name: '生成Todo List'
  action: 'exec'
  target: 'bmad/aps/tasks/generate-todo-list.md'
```

## Workflow YAML结构

### 基本结构

```yaml
workflow_id: 'unique-workflow-id'
workflow_name: '工作流名称'
version: '4.3'
description: '工作流描述'

metadata:
  author: 'APS Team'
  created: '2025-10-20'
  bmad_version: 'v6-alpha'

config:
  # 配置参数

steps:
  - step_id: 'step-1'
    name: '步骤名称'
    action: 'exec|run-workflow|human_confirmation'
    target: '目标文件路径'
    inputs: [...]
    outputs: [...]

outputs:
  # 输出定义

error_handling:
  # 错误处理
```

### Action类型

| Action               | 描述         | 使用场景               |
| -------------------- | ------------ | ---------------------- |
| `exec`               | 执行单一任务 | 调用tasks/\*.md文件    |
| `run-workflow`       | 调用子工作流 | 调用其他workflow.yaml  |
| `human_confirmation` | 人机交互     | P0-P4级别确认          |
| `conditional`        | 条件分支     | 基于条件选择执行路径   |
| `parallel_exec`      | 并行执行     | 同时调用多个agent/task |
| `sequential_exec`    | 串行执行     | 顺序调用               |
| `continuous`         | 持续监控     | 实时追踪               |

### 双模式支持

```yaml
conditional_flow:
  mode_a:
    steps: [...] # 集中确认模式步骤

  mode_b:
    steps: [...] # 增量确认模式步骤
```

### Human-in-the-Loop

```yaml
- step_id: 'confirm-1'
  action: 'human_confirmation'
  trigger_level: 'P0' # P0-P4
  confirmation_type: 'todo_contract|model|conflict|capability_gap'
  template: '@交互对话模板库/模板名称.md'
  inputs: [...]
  outputs: [...]
```

### 质量门禁

```yaml
validation:
  quality_gates:
    - name: 'Citation Compliance'
      check: 'all elements cite sources'
      severity: 'critical'
```

## 工作流开发指南

### 创建新工作流

1. **创建目录**

```bash
mkdir bmad/aps/workflows/your-workflow-name/
```

2. **创建workflow.yaml**

```yaml
workflow_id: 'aps-your-workflow'
workflow_name: 'Your Workflow Name'
# ... 按照上述结构定义
```

3. **定义steps**

- 使用清晰的step_id
- 明确inputs和outputs
- 选择合适的action类型

4. **添加错误处理**

```yaml
error_handling:
  on_error_condition:
    action: 'handle_action'
```

5. **定义outputs**

```yaml
outputs:
  primary: [...]
  metadata: [...]
```

### 工作流命名规范

- 使用kebab-case：`phase-1-requirements`
- 功能明确：`todo-management`
- 包含版本：在metadata中标注

### 集成checklist

- [ ] workflow.yaml语法正确
- [ ] 所有referenced tasks/workflows存在
- [ ] inputs/outputs定义完整
- [ ] error_handling覆盖关键场景
- [ ] 添加到主编排workflow（如需要）
- [ ] 更新本README

## 工作流示例

### 示例1: 简单任务执行

```yaml
steps:
  - step_id: '1'
    name: '分析代码'
    action: 'exec'
    target: 'bmad/aps/tasks/analyze-code.md'
    inputs:
      - code_string
    outputs:
      - analysis_result
```

### 示例2: 条件人机交互

```yaml
steps:
  - step_id: '2'
    name: '需求澄清'
    action: 'conditional_human_confirmation'
    condition: 'confidence < 0.70'
    trigger_level: 'P1'
    template: '@交互对话模板库/需求澄清模板.md'
    inputs:
      - unclear_requirements
    outputs:
      - clarified_requirements
```

### 示例3: 并行专家调用

```yaml
steps:
  - step_id: '3'
    name: '并行专家分析'
    action: 'parallel_exec'
    agents:
      - 'bmad/aps/agents/domain-expert.md'
      - 'bmad/aps/agents/constraint-expert.md'
    inputs:
      - ten_element_model
    outputs:
      - domain_analysis
      - constraint_analysis
```

## 工作流指标追踪

所有workflow自动追踪：

- 执行时间
- 步骤成功率
- 人机交互次数
- 偏离事件
- 质量门禁通过率

## 参考资源

- [BMAD Workflows Guide](../../bmm/workflows/README.md)
- [APS Module README](../README.md)
- [调度产品设计草稿](../../../调度产品设计草稿/)

---

**版本**: V4.3
**最后更新**: 2025-10-20
**维护**: APS Team
