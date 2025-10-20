# Hanyun APS QE Validate – Workflow Instructions

<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project_root}/bmad/hanyunaps/workflows/qe-validate/workflow.yaml</critical>

<workflow>

<step n="1" goal="Collect target and context">
If data path is provided, load the content; otherwise, ask the user to paste or summarize the target solution/doc. Capture intended goals and constraints for evaluation scope.

<template-output>target_summary</template-output>
</step>

<step n="2" goal="Syntax & structural checks">
Verify basic structure (headings, sections, required fields), broken references, and template alignment. List violations with precise location suggestions.

<template-output>syntax_checks</template-output>
</step>

<step n="3" goal="Logic & consistency checks">
Check internal consistency (requirements→design→validation traceability), assumptions, and reasoning gaps. Highlight contradictions and propose fixes.

<template-output>logic_checks</template-output>
</step>

<step n="4" goal="Constraint alignment">
Map constraints (e.g., 时间窗、容量) and objectives to the proposed solution. Identify mismatches or missing validations.

<template-output>constraint_checks</template-output>
</step>

<step n="5" goal="Baseline & quality gate">
Determine gate status (pass/warn/fail) with rationale. Provide prioritized remediation checklist (quick wins → structural changes).

<template-output>gate_status</template-output>
<template-output>remediation_plan</template-output>
</step>

</workflow>
