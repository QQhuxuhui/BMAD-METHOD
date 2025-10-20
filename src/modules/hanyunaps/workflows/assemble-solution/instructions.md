# Hanyun APS Assemble Solution – Instructions (source)

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
For each expert (算法/约束/目标/领域), identify relevant knowledge modules under {expert_lib_root} and propose selections with rationale. Detect conflicts (P2) and ability gaps (P3). Confirm domain/constraints/objectives (P0).

<template-output>expert_selections</template-output>
<template-output>conflict_notes</template-output>
</step>

<step n="5" goal="Phase 4: 方案集成">
Integrate selected modules into a coherent solution. Document integration strategy, assumptions, and expected performance. Include consistency checks.

<template-output>integrated_solution</template-output>
<template-output>integration_checks</template-output>
</step>

<step n="6" goal="Phase 5: 质量保证">
Apply quality gates via **质量与评测智能体**（QE 聚合能力，参见 {docs_root}/agents/智能体团队/质量与评测智能体.md），prefer `{project-root}/bmad/hanyunaps/workflows/qe-validate/workflow.yaml` when available.
If external tools/workflows are unavailable, perform structured verification (syntax/logic/constraints/baseline) and report gate status. If the gate fails, loop back with prioritized recommendations.

<template-output>qa_results</template-output>
<template-output>final_recommendations</template-output>
</step>

</workflow>
