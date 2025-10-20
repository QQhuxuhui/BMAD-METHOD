# Hanyun APS Scheduling Agents (BMAD v6 Module)

This module integrates the Hanyun APS intelligent agent team into BMAD Method v6 as an extension module. It follows BMAD-CORE conventions (agents + workflows + installer + config) and maps the Agent-as-Doc knowledge system into executable BMAD workflows.

## Contents

- `agents/` – Orchestrator and supporting agents (YAML source)
- `workflows/` – Knowledge-driven workflows (YAML + instructions + templates)
- `_module-installer/` – Installer menu config for BMAD CLI
- `tasks/` – Reserved for future task helpers
- `sub-modules/` – Reserved (IDE-specific sub agents)

## Primary Agent

- Orchestrator: `hanyunaps-orchestrator` – loads Hanyun APS knowledge and exposes menu actions:
  - `team-overview` – Summarize the agent team and knowledge libraries
  - `knowledge-index` – Build a cross-library index from docs
  - `phase-0-todo` – Generate Phase 0 Todo plan and HITL checkpoints
  - `assemble-solution` – Run five-phase solution assembly using the knowledge modules

## Specialized Agents

- QE Aggregator: `qe-aggregator` – Unified quality gate with report output
  - Menu: `validate` → `bmad/hanyunaps/workflows/qe-validate/workflow.yaml`
- KB Expansion Guide: `kb-expansion-guide` – Assess and plan knowledgebase expansion/migration
  - Menu: `assess` → `bmad/hanyunaps/workflows/kb-expansion-assess/workflow.yaml`

## Install

Run BMAD installer (optional):

```
npm run install:bmad
```

Then activate the orchestrator agent from your IDE integration, or run a workflow via the master agent and select the installed workflows.

## Config

Module config: `bmad/hanyunaps/config.yaml`

- `user_name`, `communication_language`, `output_folder` are injected from Core
- `docs_root` defaults to `{project-root}/hanyunaps/docs`
