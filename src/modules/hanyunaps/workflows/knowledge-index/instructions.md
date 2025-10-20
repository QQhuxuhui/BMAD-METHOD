# Hanyun APS Knowledge Index – Instructions (source)

<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project_root}/bmad/hanyunaps/workflows/knowledge-index/workflow.yaml</critical>

<workflow>

<step n="1" goal="Discover modules">
Enumerate all markdown files recursively under {expert_lib_root}. Skip files with "模板" in filename. Group by top-level expert library and subcategory folders.

Produce structured index sections:

- Libraries discovered
- Categories per library
- Modules per category with relative paths from {expert_lib_root}

<template-output>libraries</template-output>
<template-output>categories</template-output>
<template-output>modules</template-output>
</step>

<step n="2" goal="Output index">
Render the result using the template in {communication_language}. If the directory is missing, explain gracefully and suggest running Node tool at `hanyunaps/tools/generate-index.js` as an alternative.
</step>

</workflow>
