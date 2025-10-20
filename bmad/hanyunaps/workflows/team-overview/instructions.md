# Hanyun APS Team Overview – Workflow Instructions

<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project_root}/bmad/hanyunaps/workflows/team-overview/workflow.yaml</critical>

<workflow>

<step n="1" goal="Load core docs and outline the team">
Read and synthesize the following sources (if present):

- {docs_root}/README.md
- {docs_root}/agents/README.md
- {docs_root}/agents/智能体团队/README.md

Extract:

- Agent roster and roles
- Knowledge libraries (算法/约束/目标/领域) and mapping
- Phase-0 Todo + Human-in-the-Loop (P0–P4) mechanisms

<template-output>executive_summary</template-output>
<template-output>agent_roster</template-output>
<template-output>knowledge_libraries</template-output>
<template-output>hitl_triggers</template-output>
</step>

<step n="2" goal="Produce overview document">
Using the template, produce a concise overview with links/paths to key documents under {docs_root}. Keep output in {communication_language}.
</step>

</workflow>
