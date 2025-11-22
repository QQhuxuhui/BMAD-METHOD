# Project Context

## Purpose

**BMAD-METHOD (Breakthrough Method of Agile AI-driven Development)** 是一个通用的AI Agent协作框架，旨在通过结构化的AI Agent团队协作，完成软件项目从规划到开发的全生命周期。

核心目标：

- 提供一套完整的AI辅助软件工程方法论
- 通过专业化的AI Agent（Analyst、PM、Architect、PO、SM、Dev、QA、UX Expert）实现角色协作
- 支持从PRD创建、架构设计到代码实现、质量保证的端到端流程
- 适用于Greenfield（新项目）和Brownfield（既有项目）场景

## Tech Stack

### 核心技术栈

- **语言**: JavaScript (Node.js >=20.0.0)
- **模块系统**: ESM (ECMAScript Modules)
- **CLI框架**: Commander.js
- **配置格式**: YAML + Markdown
- **包管理**: npm

### 开发工具

- **代码质量**: ESLint, Prettier
- **Git Hooks**: Husky, lint-staged
- **测试框架**: Jest, Playwright
- **构建工具**: 自定义bundler系统

### IDE支持

支持15+种AI IDE集成：

- Claude Code
- Cursor
- Windsurf
- Cline
- GitHub Copilot
- 等等

## Project Conventions

### Code Style

**JavaScript**:

- 使用ESM模块系统
- ESLint配置：`@eslint/js`, `eslint-plugin-n`, `eslint-plugin-unicorn`
- Prettier自动格式化
- 最大警告数：0（严格模式）

**文件命名**:

- kebab-case用于文件名和目录名
- Agent定义：`{agent-id}.md`
- Task定义：`{task-name}.md`

### Architecture Patterns

**核心架构创新**:

1. **Agent-as-Document模式**
   - Agent定义是Markdown文件，包含YAML配置块
   - 支持动态转换（Orchestrator可以变成任何Agent）
   - 按需加载依赖（tasks、templates、checklists）

2. **模块化架构**
   - 每个模块独立安装：`src/modules/{module-name}/`
   - 模块安装器：`_module-installer/installer.js`
   - 松耦合设计，模块间无强依赖

3. **工作流驱动**
   - Planning Workflow（Web UI或强大IDE）
   - Core Development Cycle（IDE中）
   - 结构化的Story → Development → QA流程

4. **文档驱动开发**
   - PRD (Product Requirements Document)
   - Architecture Document
   - Story Sharding机制
   - QA Assessments & Gates

5. **命令系统**
   - 所有命令以`*`前缀（如`*help`、`*agent`、`*task`）
   - 支持命令别名和灵活匹配
   - YOLO模式（跳过确认）

### Testing Strategy

**测试层次**:

- **单元测试**: Jest测试框架
- **集成测试**: CLI命令功能测试
- **E2E测试**: IDE安装和工作流测试（Playwright）

**测试约定**:

- 遵循BMAD测试框架（Test Levels Framework）
- 优先级矩阵：P0（关键）、P1（重要）、P2（一般）
- Given-When-Then格式的测试场景
- Risk-based testing策略

**质量要求**:

- 所有新功能必须包含测试
- PR前运行lint和format检查
- Husky pre-commit hooks强制执行

### Git Workflow

**分支策略**:

- **主分支**: `main`
- **功能分支**: `feature/{description}`
- **修复分支**: `fix/{description}`
- **发布分支**: `release/{version}`

**提交信息格式**:

```
类型: 简短描述

类型包括:
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- chore: 其他改动（依赖、配置等）
- refactor: 重构
- test: 测试相关
- perf: 性能优化
```

**工作流程**:

1. 从`main`创建功能分支
2. 开发并提交（通过pre-commit hooks）
3. 创建PR
4. Review通过后合并到`main`

## Domain Context

**AI辅助软件工程领域**:

BMAD-METHOD的核心领域是将传统软件工程实践与AI Agent协作相结合：

1. **敏捷开发方法论**
   - Epic → Story → Task分解层次
   - Sprint迭代开发
   - Story DoD (Definition of Done)
   - Planning → Execution循环

2. **需求工程**
   - PRD创建和维护
   - Functional Requirements (FRs)
   - Non-Functional Requirements (NFRs)
   - Acceptance Criteria定义

3. **软件架构**
   - 架构决策记录
   - Tech Stack选型指导
   - Coding Standards制定
   - Project Structure规划

4. **质量保证**
   - Risk Profiling（风险评估）
   - Test Design（测试设计）
   - Requirements Tracing（需求追溯）
   - NFR Assessment（非功能需求评估）
   - QA Gates（质量门禁）

5. **项目管理**
   - Brownfield vs Greenfield项目处理
   - Document Sharding（文档分片）
   - Workflow Orchestration（工作流编排）

6. **AI Agent协作**
   - 多Agent角色定义
   - Agent间通信协议
   - Party Mode（群聊模式）
   - 上下文管理

## Important Constraints

**技术约束**:

1. **Node.js版本**:
   - 必须 >=20.0.0
   - 建议使用nvm管理版本

2. **模块架构要求**:
   - 每个模块必须包含`_module-installer/installer.js`
   - 模块配置必须遵循标准格式
   - 支持多IDE平台的installer变体

3. **Agent定义规范**:
   - 必须是Markdown文件
   - 必须包含YAML配置块
   - 必须定义activation-instructions

4. **文档路径约定**:
   - PRD: `docs/prd.md`
   - Architecture: `docs/architecture.md`
   - Epics: `docs/epics/`
   - Stories: `docs/stories/`
   - QA: `docs/qa/`

5. **命令系统约束**:
   - 所有命令必须以`*`开头
   - 依赖文件路径格式：`.bmad-core/{type}/{name}`

**业务约束**:

- 框架设计为跨项目、跨语言使用
- 不绑定特定IDE或LLM提供商
- 支持离线使用（CLI工具）

## External Dependencies

**无运行时外部服务**:
BMAD-METHOD是一个自包含的CLI工具框架，不依赖外部API或数据库。

**开发依赖**:

- npm packages（详见package.json）
- Node.js运行时
- Git版本控制

**可选集成**:

- AI IDE（Claude Code、Cursor等）作为使用环境
- LLM服务（用户自行配置API密钥）
- 各种开发工具（根据项目技术栈）

**关键npm依赖**:

- `commander`: CLI命令解析
- `inquirer`: 交互式提示
- `js-yaml`: YAML解析
- `chalk`, `boxen`, `ora`: CLI美化
- `glob`, `fs-extra`: 文件操作
- `playwright`: 浏览器自动化测试
