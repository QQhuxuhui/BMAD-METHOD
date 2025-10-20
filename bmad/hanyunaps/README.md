# Hanyun APS Scheduling Agents (Installed)

This folder contains the installed BMAD artifacts for the Hanyun APS extension module:

- `agents/` – Executable agent definitions (MD with XML)
- `workflows/` – Executable workflows (YAML + instructions + templates)
- `config.yaml` – Module configuration and knowledge roots

Activate the agent via your IDE integration and run:

- `*team-overview`
- `*knowledge-index`
- `*phase-0-todo`
- `*assemble-solution`

Specialized agents are available as separate entries:

- `bmad/hanyunaps/agents/qe-aggregator.md` → `*validate` (QE report)
- `bmad/hanyunaps/agents/kb-expansion-guide.md` → `*assess` (KB expansion plan)

All workflows respect Phase-0 Todo and Human-in-the-Loop triggers defined in the docs under `{project-root}/hanyunaps/docs`.
