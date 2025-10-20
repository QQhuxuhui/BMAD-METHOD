# Hanyun APS Assemble Solution – Workflow Instructions

<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project_root}/bmad/hanyunaps/workflows/assemble-solution/workflow.yaml</critical>

<workflow>

<step n="1" goal="Pre-check: enforce Phase-0">
If a Phase-0 Todo contract is not yet agreed, instruct the user to run `*phase-0-todo` first. Otherwise, load its outputs from the most recent file under {output_folder} matching `hanyunaps-phase-0-todo.md` and summarize checkpoints.

<template-output>phase0_summary</template-output>
</step>

<step n="2" goal="Phase 1: 需求分析">
Read:
- {docs_root}/agents/智能体团队/系统编排协调智能体.md (需求理解)
- Any data provided by user

Produce standardized requirement model.

<template-output>requirements_model</template-output>
</step>

<step n="3" goal="Phase 1.5: 十要素建模">
Using the team docs, produce TenElementModel (time, uncertainty included). Trigger HITL P0 to confirm the model.

<template-output>ten_element_model</template-output>
</step>

<step n="4" goal="Phase 2–3: 专家协调 + 知识组装">

**CRITICAL**: Present this phase as a **multi-expert dialogue session**. Each expert should have a distinct "voice" and clearly reference their expert library.

For each expert, format output as:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 切换到: {Expert Icon} **{专家名称}** (@{专家智能体文件})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**专家自我介绍**:
{一句话说明该专家的职责}

**专业分析** (基于 @{expert_lib_root}/{相关模块}):
{分析内容，包含具体的专家库引用}

**需要您确认的问题**:
1. {确认项1}
2. {确认项2}
...

❓ 请输入 1-N 选择，或直接描述您的意见。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Expert sequence** (依次呈现，每个专家单独一轮交互):

1. **🏭 领域应用专家** (@领域应用专家智能体)
   - Read: {docs_root}/agents/智能体团队/领域应用专家智能体.md
   - Library: {expert_lib_root}/领域应用专家库/
   - Task: 识别业务场景、匹配最佳实践
   - Trigger P0: 场景确认

2. **🔧 约束模式专家** (@约束模式专家智能体)
   - Read: {docs_root}/agents/智能体团队/约束模式专家智能体.md
   - Library: {expert_lib_root}/约束模式专家库/
   - Task: 建模约束、验证可行性
   - Trigger P0: 约束确认

3. **🎯 目标优化专家** (@目标优化专家智能体)
   - Read: {docs_root}/agents/智能体团队/目标优化专家智能体.md
   - Library: {expert_lib_root}/目标函数专家库/
   - Task: 设计目标函数、平衡多目标
   - Trigger P0: 目标权重确认

4. **💡 调度算法专家** (@调度算法专家智能体)
   - Read: {docs_root}/agents/智能体团队/调度算法专家智能体.md
   - Library: {expert_lib_root}/调度算法专家库/
   - Task: 推荐算法、配置参数
   - Trigger P0: 算法参数确认

**After all experts**, present a **团队联席会议总结**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 **专家团队联席会议总结**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**参会专家**: 🏭领域 | 🔧约束 | 🎯目标 | 💡算法

**各专家核心结论**:
  🏭 领域专家: {一句话总结}
  🔧 约束专家: {一句话总结}
  🎯 目标专家: {一句话总结}
  💡 算法专家: {一句话总结}

**一致性检查**:
  ✅ 通过 / ❌ 发现{N}处冲突

{如有冲突，触发 P2 冲突仲裁}

**综合方案**: 已准备就绪，进入集成阶段

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Detect conflicts (P2) and ability gaps (P3) during expert analysis.

<template-output>expert_selections</template-output>
<template-output>conflict_notes</template-output>
</step>

<step n="5" goal="Phase 4: 方案集成">
Integrate selected modules into a coherent solution. Document integration strategy, assumptions, and expected performance. Include consistency checks.

<template-output>integrated_solution</template-output>
<template-output>integration_checks</template-output>
</step>

<step n="6" goal="Phase 5: 质量保证">
Apply quality gates via **质量与评测智能体**（QE 聚合能力，参见 {docs_root}/agents/智能体团队/质量与评测智能体.md），优先使用 `{project-root}/bmad/hanyunaps/workflows/qe-validate/workflow.yaml`。
若外部工具/工作流不可用，则执行结构化校验（语法/逻辑/约束一致性/基准）并报告 Gate 状态；若 Gate 失败则回路给出修复建议。

<template-output>qa_results</template-output>
<template-output>final_recommendations</template-output>
</step>

</workflow>
