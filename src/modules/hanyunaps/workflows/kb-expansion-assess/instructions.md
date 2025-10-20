# Hanyun APS KB Expansion Assess – Instructions (source)

<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project_root}/bmad/hanyunaps/workflows/kb-expansion-assess/workflow.yaml</critical>

<workflow>

<step n="1" goal="Inventory and structure">
Scan {expert_lib_root} for existing modules (skip files containing "模板"). Map to four libraries: 算法/约束/目标/领域. Summarize coverage and gaps.

<template-output>inventory_summary</template-output>
</step>

<step n="2" goal="Compatibility analysis with BMAD v6">
Evaluate module metadata, IDs, and folder layout against BMAD v6 conventions (workflow/template/instructions separation where applicable). Identify changes required for smooth integration.

<template-output>compatibility_analysis</template-output>
</step>

<step n="3" goal="Expansion & migration plan">
Propose prioritized expansion plan: new modules, refactors, deprecations. Include milestones, risks, and traceability requirements.

<template-output>expansion_plan</template-output>
<template-output>migration_roadmap</template-output>
</step>

</workflow>
