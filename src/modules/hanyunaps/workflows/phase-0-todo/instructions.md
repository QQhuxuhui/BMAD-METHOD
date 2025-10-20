# Hanyun APS Phase-0 Todo – Instructions (source)

<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project_root}/bmad/hanyunaps/workflows/phase-0-todo/workflow.yaml</critical>

<workflow>

<step n="1" goal="Collect request and constraints">
If data is provided, summarize it as the initial request. Otherwise, ask the user to state the goal, constraints, and desired outcomes. Keep it short and structured.

Capture:

- Problem / Goal
- Constraints (time window, capacity, etc.)
- Objectives and priority
- Known domain context

<template-output>request_summary</template-output>
</step>

<step n="2" goal="Generate Todo plan and checkpoints">
Based on Hanyun APS V4.2 design (Todo + HITL), generate a Phase-0 execution contract:

**IMPORTANT**: Introduce the expert team (canonical names) and output to `expert_team_intro`:

```markdown
## 👥 您的专家团队

本次任务将由以下智能体专家团队为您服务：

- 🏭 **领域应用专家** (@领域应用专家智能体)
  - 职责: 识别业务场景、匹配行业最佳实践
  - 专家库: 车辆调度、生产调度、服务调度、供应链等5大领域
  - 您将与此专家确认: 场景类型、领域特征、业务规则

- 🔧 **约束模式专家** (@约束模式专家智能体)
  - 职责: 建模约束条件、验证可行性
  - 专家库: 时间约束、容量约束、逻辑约束、空间约束、业务规则
  - 您将与此专家确认: 约束类型、约束参数、优先级

- 🎯 **目标优化专家** (@目标优化专家智能体)
  - 职责: 设计目标函数、平衡多目标冲突
  - 专家库: 时间目标、成本目标、质量目标、效率目标、可持续性目标
  - 您将与此专家确认: 目标权重、优化方向、评估标准

- 💡 **调度算法专家** (@调度算法专家智能体)
  - 职责: 推荐算法、配置参数、生成代码
  - 专家库: 精确算法、启发式算法、元启发式算法
  - 您将与此专家确认: 算法选择、参数配置、性能要求

- 🛡️ **质量与评测智能体** (@质量与评测智能体)
  - 职责: 统一验证与评测、质量门禁（QE聚合）
  - 专家库: 验证评估专家库（语法/逻辑/约束一致性/基准评测/报告聚合）
  - 您将与此专家确认: Gate状态、修复优先级、放行/回退决策

- 🤖 **系统编排协调智能体** (总指挥)
  - 职责: 任务规划、专家协调、方案集成、质量保证
```

<template-output>expert_team_intro</template-output>

Then generate the execution contract:

- A numbered Todo list with clear steps, **owners (specific expert names from the team above)**, and expected outputs
- HITL checkpoints with triggers:
  - P0: Todo mandatory confirmations
  - P1: confidence &lt; 0.70
  - P2: conflicts detected across experts
  - P3: ability gap identified
  - P4: user pause
- Deviation detection approach (similarity threshold 0.60): how to detect and recover

<template-output>todo_list</template-output>
<template-output>hitl_checkpoints</template-output>
<template-output>deviation_detection</template-output>
</step>

<note>
If any Todo owner names are not from the canonical team set above, validate/fix them using the Node tool:
`hanyunaps/tools/validation/validate-todo-owners.js --file {output_folder}/hanyunaps-phase-0-todo.md [--fix]`.
</note>
</step>

<step n="3" goal="Confirm with user">
Ask the user to confirm or edit the Todo plan. If confirmed, proceed to save. If not, iterate until agreement.
</step>

</workflow>
