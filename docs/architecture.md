# BMAD-METHOD LangGraph集成方案 - 全栈架构文档

**项目名称**: BMAD-METHOD LangGraph集成方案
**架构版本**: v1.0
**创建日期**: 2025-11-04
**架构师**: Winston (Architect)
**基于PRD**: docs/langgraph集成方案.md

---

## 目录

1. [Introduction](#1-introduction)
2. [High Level Architecture](#2-high-level-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Data Models](#4-data-models)
5. [API Specification](#5-api-specification)
6. [Components](#6-components)
7. [External APIs](#7-external-apis)
8. [Core Workflows](#8-core-workflows)
9. [Database Schema](#9-database-schema)
10. [Unified Project Structure](#10-unified-project-structure)
11. [Development Workflow](#11-development-workflow)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Security and Performance](#13-security-and-performance)
14. [Testing Strategy](#14-testing-strategy)
15. [Coding Standards](#15-coding-standards)
16. [Error Handling Strategy](#16-error-handling-strategy)
17. [Monitoring and Observability](#17-monitoring-and-observability)

---

## 1. Introduction

本文档概述了**BMAD-METHOD LangGraph集成方案**的完整全栈架构，包括后端智能体编排系统、前端监控界面及其集成方式。本文档作为AI驱动开发的唯一真实来源，确保整个技术栈的一致性。

本架构采用**分阶段实施策略**（Phase 1-3），支持从轻量级模型适配（2-3周）到完整企业级智能体工厂（18-26周）的渐进式演进。核心目标是实现国产大模型（Qwen/GLM/DeepSeek）的即插即用支持，并通过LangGraph 1.0的持久化和人机协作特性，将智能体开发效率提升3-5倍。

### 1.1 Starter Template

**项目类型**: 棕地增强项目（Brownfield Enhancement）

**现有基础**: BMAD-METHOD V4.4.1，具备完整的八大智能体协作系统（Orchestrator、Algorithm、Constraint、Objective、Domain、Code Implementation、Extension、Quality）

**集成方式**:

- 基于现有BMAD架构进行LangGraph 1.0集成
- 保持与现有workflow.yaml配置的兼容性
- 采用LangServe提供RESTful API自动生成
- 前端使用SSE（Server-Sent Events）流式传输实时监控智能体执行

**关键约束**:

- 必须兼容Python 3.11+（LangGraph CLI硬性要求）
- 需向后兼容现有智能体配置
- 架构变更应最小化，优先考虑轻量级适配器模式

### 1.2 Change Log

| 日期       | 版本 | 描述                                     | 作者                |
| ---------- | ---- | ---------------------------------------- | ------------------- |
| 2025-11-04 | v1.0 | 基于LangGraph集成方案PRD创建初始架构文档 | Winston (Architect) |

---

## 2. High Level Architecture

### 2.1 Technical Summary

本架构采用**基于LangGraph 1.0的微服务架构**，结合LangServe实现自动化API生成。后端使用Python 3.11+构建智能体编排服务，通过LangGraph的StateGraph管理八大智能体的工作流执行。前端采用Vue 3构建监控界面，使用SSE（Server-Sent Events）实现实时流式传输。数据持久化基于PostgreSQL和Redis，支持工作流状态的自动保存和恢复。部署采用Docker容器化方案，支持本地开发、预生产和生产环境的统一管理。整体架构遵循"轻量级适配器"原则，最小化对现有BMAD V4.4.1架构的侵入性变更。

### 2.2 Platform and Infrastructure Choice

**选定平台**: Docker容器化 + 自托管

**核心服务**:

- **LangGraph工作流服务**: Python 3.11 + LangServe + FastAPI
- **国产模型适配服务**: 轻量级抽象层支持多模型切换
- **前端监控界面**: Vue 3 + Ant Design Vue + SSE客户端
- **数据持久化**: PostgreSQL 16+ + Redis 7+
- **反向代理**: Nginx（API网关和前端静态资源）

**部署区域**:

- 开发环境: 本地Docker Compose
- 生产环境: 私有云/IDC自托管

**选择理由**：

1. PRD明确要求支持本地部署（vLLM/Ollama）和云端API两种模式
2. 棕地项目已有基础设施，增量投入最小
3. 数据本地化需求和成本控制是核心关切
4. Docker Compose可快速搭建开发环境

### 2.3 Repository Structure

**结构选择**: Monorepo（不使用专门工具，保持简单）

**包组织策略**:

```
BMAD-METHOD/                      # Monorepo根目录
├── backend/                      # 后端服务（Python）
│   ├── langgraph_service/        # LangGraph工作流服务
│   ├── model_adapters/           # 国产模型适配器
│   └── shared/                   # 后端共享代码
├── frontend/                     # 前端应用（Vue）
│   ├── web/                      # 监控界面
│   └── shared/                   # 前端共享组件
├── shared/                       # 全栈共享（类型定义、常量）
├── docs/                         # 文档
├── scripts/                      # 部署和构建脚本
└── docker/                       # Docker配置文件
```

### 2.4 High Level Architecture Diagram

```mermaid
graph TB
    subgraph "用户层"
        User[用户/开发者]
        Browser[浏览器]
    end

    subgraph "前端层 (Frontend)"
        WebUI[Web监控界面<br/>Vue 3 + Ant Design Vue]
        SSE[SSE客户端<br/>实时流式接收]
    end

    subgraph "API网关层"
        Nginx[Nginx<br/>反向代理]
    end

    subgraph "应用层 (Backend)"
        LangServe[LangServe API<br/>FastAPI]
        WorkflowEngine[LangGraph工作流引擎<br/>StateGraph]

        subgraph "八大智能体"
            Orchestrator[Orchestrator<br/>编排者]
            Algorithm[Algorithm Expert<br/>算法专家]
            Constraint[Constraint Expert<br/>约束专家]
            Objective[Objective Expert<br/>目标专家]
            Domain[Domain Expert<br/>领域专家]
            CodeImpl[Code Implementation<br/>代码实现专家]
            Extension[Extension Expert<br/>扩展专家]
            Quality[Quality Expert<br/>质量专家]
        end

        ModelAdapter[国产模型适配器]
    end

    subgraph "模型层"
        Qwen[通义千问 Qwen<br/>vLLM/API]
        GLM[智谱GLM<br/>vLLM/API]
        DeepSeek[DeepSeek<br/>vLLM/API]
    end

    subgraph "数据层"
        PostgreSQL[(PostgreSQL<br/>持久化存储)]
        Redis[(Redis<br/>缓存/会话)]
    end

    subgraph "外部集成"
        GitHub[GitHub<br/>代码仓库]
        Monitoring[监控系统<br/>Prometheus/Grafana]
    end

    User --> Browser
    Browser --> WebUI
    WebUI <--> SSE
    SSE <--> Nginx
    Nginx --> LangServe

    LangServe --> WorkflowEngine
    WorkflowEngine --> Orchestrator
    Orchestrator --> Algorithm
    Orchestrator --> Constraint
    Orchestrator --> Objective
    Algorithm --> Domain
    Constraint --> Domain
    Objective --> Domain
    Domain --> CodeImpl
    CodeImpl --> Extension
    CodeImpl --> Quality

    WorkflowEngine --> ModelAdapter
    ModelAdapter --> Qwen
    ModelAdapter --> GLM
    ModelAdapter --> DeepSeek

    WorkflowEngine --> PostgreSQL
    WorkflowEngine --> Redis

    WorkflowEngine --> GitHub
    WorkflowEngine --> Monitoring

    style WebUI fill:#e1f5ff
    style LangServe fill:#fff4e1
    style WorkflowEngine fill:#ffe1e1
    style ModelAdapter fill:#f0e1ff
    style PostgreSQL fill:#e1ffe1
    style Redis fill:#e1ffe1
```

### 2.5 Architectural Patterns

**1. 微服务架构（Microservices）**

- **描述**: LangGraph工作流服务、模型适配服务、前端界面作为独立服务部署
- **理由**: 支持独立扩展和部署，服务间通过HTTP/SSE通信，降低耦合度

**2. 事件驱动架构（Event-Driven）**

- **描述**: LangGraph的StateGraph基于状态转换事件驱动智能体执行
- **理由**: 天然支持异步执行和并行处理，符合智能体协作场景

**3. 适配器模式（Adapter Pattern）**

- **描述**: 国产模型适配器提供统一接口，屏蔽不同模型API差异
- **理由**: 支持模型热切换，降低模型替换成本，Phase 1核心模式

**4. 仓储模式（Repository Pattern）**

- **描述**: 数据访问层抽象，统一管理PostgreSQL和Redis的数据操作
- **理由**: 便于未来数据库迁移，提供清晰的数据访问接口

**5. BFF模式（Backend For Frontend）**

- **描述**: LangServe API专门为前端监控界面设计，提供优化的数据格式
- **理由**: 前端SSE流式传输需要特定的数据格式和事件流

**6. Human-in-the-Loop模式**

- **描述**: 利用LangGraph 1.0的interrupt机制实现人工确认点（P1/P2/P2.5）
- **理由**: 关键决策需要人工介入，提高智能体输出的可控性和质量

**7. 持久化状态模式（Durable State）**

- **描述**: LangGraph 1.0内置的checkpoint机制自动保存工作流状态
- **理由**: 支持工作流中断和恢复，服务器重启不丢失进度

**8. 组件化UI模式（Component-Based UI）**

- **描述**: Vue 3组件化开发，智能体状态和输出作为独立组件
- **理由**: 提高前端可维护性，支持智能体界面的复用和定制

---

## 3. Tech Stack

这是项目的**唯一技术真实来源**。所有开发必须使用这些确切的技术和版本。

| 类别             | 技术                 | 版本     | 用途                       | 选择理由                                                |
| ---------------- | -------------------- | -------- | -------------------------- | ------------------------------------------------------- |
| **后端语言**     | Python               | 3.11+    | 后端智能体服务开发         | LangGraph CLI硬性要求3.11+；支持最新类型注解和性能优化  |
| **后端框架**     | FastAPI              | 0.115.0+ | RESTful API和LangServe集成 | 原生async支持；自动OpenAPI文档生成；与LangServe无缝集成 |
| **智能体编排**   | LangGraph            | 1.0.2    | 智能体工作流StateGraph编排 | 稳定版本；内置持久化和Human-in-Loop；生产级特性完整     |
| **智能体工具**   | LangChain Core       | 0.2.38+  | 智能体工具链和提示管理     | LangGraph 1.0核心依赖；提供agent创建工具                |
| **智能体SDK**    | LangGraph SDK        | 1.0.0+   | LangGraph客户端和工具      | 官方SDK；支持远程调用和监控                             |
| **Checkpoint**   | LangGraph Checkpoint | 2.0.23+  | 工作流状态持久化           | 内置checkpoint机制；自动状态保存和恢复                  |
| **API服务**      | LangServe            | 0.3.0+   | 自动API端点生成            | 一行代码生成/invoke、/stream等端点；SSE流式传输支持     |
| **HTTP服务器**   | Uvicorn              | 0.26.0+  | ASGI服务器                 | 高性能async服务器；FastAPI官方推荐                      |
| **流式传输**     | sse-starlette        | 2.1.0    | Server-Sent Events实现     | 与FastAPI集成；实时流式数据推送                         |
| **HTTP客户端**   | httpx                | 0.25.0+  | 异步HTTP请求               | 支持async/await；用于模型API调用                        |
| **前端语言**     | TypeScript           | 5.3+     | 前端类型安全开发           | 类型安全；与后端类型共享；减少运行时错误                |
| **前端框架**     | Vue                  | 3.4+     | 监控界面UI开发             | 组合式API；TypeScript支持好；团队更熟悉；性能优秀       |
| **UI组件库**     | Ant Design Vue       | 4.1+     | 企业级UI组件               | 完整的Vue 3组件体系；中文文档友好；适合管理后台         |
| **状态管理**     | Pinia                | 2.1+     | Vue状态管理                | Vue 3官方推荐；TypeScript友好；轻量级；直观的API        |
| **路由**         | Vue Router           | 4.2+     | 前端路由管理               | Vue 3官方路由；支持TypeScript                           |
| **API风格**      | REST + SSE           | -        | 前后端通信协议             | LangServe原生支持REST；SSE实现实时流式传输              |
| **数据库**       | PostgreSQL           | 16+      | 工作流状态和数据持久化     | LangGraph checkpoint后端；ACID事务保证；JSON支持        |
| **缓存**         | Redis                | 7+       | 会话缓存和任务队列         | 高性能；支持发布订阅；持久化选项                        |
| **文件存储**     | 本地文件系统         | -        | 代码生成和知识库存储       | Phase 1简化方案；避免引入云存储依赖                     |
| **认证**         | JWT                  | -        | API访问认证                | 无状态；易于扩展；LangServe支持中间件集成               |
| **前端测试**     | Vitest               | 1.0+     | Vue组件单元测试            | Vite生态原生集成；快速；Vue Test Utils支持              |
| **后端测试**     | Pytest               | 7.4+     | Python单元和集成测试       | Python标准测试框架；丰富的插件生态                      |
| **E2E测试**      | Playwright           | 1.40+    | 端到端自动化测试           | 跨浏览器；录制功能；与TypeScript集成                    |
| **构建工具**     | Vite                 | 5.0+     | 前端构建和开发服务器       | Vue官方推荐；极快的HMR；原生ESM                         |
| **打包工具**     | Rollup               | -        | 前端生产构建               | Vite底层依赖；Tree-shaking优化                          |
| **IaC工具**      | Docker Compose       | 2.23+    | 本地和生产环境编排         | 简单易用；统一开发和部署环境                            |
| **CI/CD**        | GitHub Actions       | -        | 持续集成和部署             | 与GitHub深度集成；免费额度充足；YAML配置                |
| **监控**         | Prometheus           | 2.48+    | 指标收集和告警             | 开源标准；丰富的exporter生态                            |
| **日志**         | structlog            | 24.1.0+  | 结构化日志                 | JSON格式；易于解析和查询；Python原生支持                |
| **CSS框架**      | Tailwind CSS         | 3.4+     | 实用优先的CSS框架          | 快速开发；与Vue组件结合好；构建时优化                   |
| **Python包管理** | Conda                | Latest   | Python环境和依赖管理       | 宿主机已配置；科学计算包支持好                          |
| **Node包管理**   | npm                  | 10+      | Node.js依赖管理            | 标准工具；与nvm配合使用                                 |
| **序列化**       | orjson               | 3.9.7+   | 高性能JSON序列化           | 比标准库快；LangGraph推荐                               |
| **重试机制**     | tenacity             | 8.0.0+   | 智能重试和容错             | 灵活的重试策略；装饰器语法简洁                          |
| **数据库连接**   | psycopg              | 3.2.0+   | PostgreSQL Python驱动      | 最新版本；连接池支持；async支持                         |
| **序列化工具**   | cloudpickle          | 3.0.0+   | Python对象序列化           | LangGraph checkpoint依赖；支持复杂对象                  |
| **数据验证**     | Pydantic             | 2.10.0+  | 数据模型和验证             | FastAPI核心依赖；类型安全；自动文档生成                 |
| **可观测性**     | LangSmith            | 0.1.63+  | LangGraph工作流追踪        | 官方可观测性工具；调试和性能分析                        |

---

## 4. Data Models

基于PRD的功能需求和LangGraph 1.0工作流特性，定义核心数据模型。这些模型将在前后端共享，使用TypeScript接口定义。

### 4.1 WorkflowExecution（工作流执行）

**目的**: 记录完整的APS工作流执行实例，跟踪从Phase 0到Phase 4的整个智能体协作过程

```typescript
// shared/types/workflow.ts
export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  PAUSED = 'paused', // Human-in-Loop暂停
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum Phase {
  P0 = 'P0', // 问题理解
  P1 = 'P1', // 算法推荐
  P2 = 'P2', // 约束和目标分析
  P2_5 = 'P2.5', // 代码实现
  P3 = 'P3', // 扩展和质量保证
  P4 = 'P4', // 最终交付
}

export interface WorkflowConfig {
  modelProvider: 'qwen' | 'glm' | 'deepseek';
  modelName: string;
  temperature: number;
  maxTokens: number;
  enableHumanInLoop: boolean;
}

export interface ErrorInfo {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: Date;
}

export interface WorkflowExecution {
  id: string;
  userId: string;
  status: WorkflowStatus;
  currentPhase: Phase;
  config: WorkflowConfig;
  checkpointId: string | null;
  humanConfirmationRequired: boolean;
  startedAt: Date;
  completedAt: Date | null;
  error: ErrorInfo | null;
  metadata: Record<string, any>;
}
```

**关系**:

- **一对多** → `AgentExecution`: 一个工作流包含多个智能体执行
- **一对多** → `HumanConfirmation`: 一个工作流可能有多个人工确认点
- **一对一** → `WorkflowCheckpoint`: LangGraph管理的持久化状态

### 4.2 AgentExecution（智能体执行）

**目的**: 记录单个智能体的执行过程和输出结果，支持八大智能体的独立追踪

```typescript
// shared/types/agent.ts
export enum AgentType {
  ORCHESTRATOR = 'orchestrator',
  ALGORITHM = 'algorithm',
  CONSTRAINT = 'constraint',
  OBJECTIVE = 'objective',
  DOMAIN = 'domain',
  CODE_IMPLEMENTATION = 'code_implementation',
  EXTENSION = 'extension',
  QUALITY = 'quality',
}

export enum AgentStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped',
}

export interface AgentInput {
  prompt: string;
  context: Record<string, any>;
  previousOutputs?: Record<AgentType, any>;
}

export interface AgentOutput {
  content: string;
  structured?: Record<string, any>;
  confidence?: number;
  reasoning?: string[];
}

export interface TokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  cost?: number;
}

export interface AgentExecution {
  id: string;
  workflowId: string;
  agentType: AgentType;
  status: AgentStatus;
  input: AgentInput;
  output: AgentOutput | null;
  startedAt: Date;
  completedAt: Date | null;
  duration: number | null;
  tokenUsage: TokenUsage | null;
  error: ErrorInfo | null;
}
```

### 4.3 AgentMessage（智能体消息）

**目的**: 记录智能体执行过程中的流式输出消息，支持SSE实时传输到前端

```typescript
// shared/types/message.ts
export enum MessageType {
  TEXT = 'text',
  THOUGHT = 'thought',
  RESULT = 'result',
  ERROR = 'error',
  SYSTEM = 'system',
}

export interface AgentMessage {
  id: string;
  agentExecutionId: string;
  workflowId: string;
  type: MessageType;
  content: string;
  sequence: number;
  timestamp: Date;
  metadata?: Record<string, any>;
}
```

### 4.4 HumanConfirmation（人工确认）

**目的**: 记录Human-in-Loop触发点的人工确认和决策过程（P1/P2/P2.5）

```typescript
// shared/types/confirmation.ts
export enum TriggerPoint {
  P1 = 'P1',
  P2 = 'P2',
  P2_5 = 'P2.5',
}

export enum ConfirmationStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  MODIFIED = 'modified',
  TIMEOUT = 'timeout',
}

export interface ConfirmationContext {
  title: string;
  description: string;
  options: ConfirmationOption[];
  data: Record<string, any>;
}

export interface ConfirmationOption {
  id: string;
  label: string;
  description?: string;
  risk?: 'low' | 'medium' | 'high';
}

export interface Decision {
  action: 'approve' | 'reject' | 'modify' | 'regenerate';
  selectedOptionId?: string;
  feedback?: string;
  modifications?: Record<string, any>;
}

export interface HumanConfirmation {
  id: string;
  workflowId: string;
  triggerPoint: TriggerPoint;
  status: ConfirmationStatus;
  context: ConfirmationContext;
  decision: Decision | null;
  requestedAt: Date;
  respondedAt: Date | null;
  timeout: number;
}
```

### 4.5 ModelConfig（模型配置）

**目的**: 管理国产大模型的配置信息，支持模型热切换

```typescript
// shared/types/model.ts
export enum ModelProvider {
  QWEN = 'qwen',
  GLM = 'glm',
  DEEPSEEK = 'deepseek',
}

export enum DeploymentType {
  LOCAL_VLLM = 'local_vllm',
  LOCAL_OLLAMA = 'local_ollama',
  CLOUD_API = 'cloud_api',
}

export interface ModelConfig {
  id: string;
  provider: ModelProvider;
  modelName: string;
  deploymentType: DeploymentType;
  endpoint: string;
  apiKey: string | null;
  enabled: boolean;
  priority: number;
  config: ModelParameters;
  createdAt: Date;
  updatedAt: Date;
}

export interface ModelParameters {
  temperature: number;
  topP: number;
  maxTokens: number;
  timeout: number;
  retryAttempts: number;
}
```

### 4.6 Data Model Relationships

```mermaid
erDiagram
    WorkflowExecution ||--o{ AgentExecution : contains
    WorkflowExecution ||--o{ HumanConfirmation : requires
    WorkflowExecution ||--|| WorkflowCheckpoint : has
    AgentExecution ||--o{ AgentMessage : produces
    WorkflowExecution }o--|| ModelConfig : uses

    WorkflowExecution {
        string id PK
        string userId
        WorkflowStatus status
        Phase currentPhase
        WorkflowConfig config
        string checkpointId FK
        boolean humanConfirmationRequired
        Date startedAt
        Date completedAt
    }

    AgentExecution {
        string id PK
        string workflowId FK
        AgentType agentType
        AgentStatus status
        AgentInput input
        AgentOutput output
        Date startedAt
        Date completedAt
        number duration
        TokenUsage tokenUsage
    }

    AgentMessage {
        string id PK
        string agentExecutionId FK
        string workflowId FK
        MessageType type
        string content
        number sequence
        Date timestamp
    }

    HumanConfirmation {
        string id PK
        string workflowId FK
        TriggerPoint triggerPoint
        ConfirmationStatus status
        ConfirmationContext context
        Decision decision
        Date requestedAt
        Date respondedAt
    }

    ModelConfig {
        string id PK
        ModelProvider provider
        string modelName
        DeploymentType deploymentType
        string endpoint
        boolean enabled
        number priority
    }

    WorkflowCheckpoint {
        string checkpoint_id PK
        string thread_id
        Record checkpoint
        Date created_at
    }
```

---

由于文档非常长，我会继续在下一条消息中完成剩余部分。让我先保存这部分内容。

## 5. API Specification

完整的OpenAPI 3.0规范请参考PRD文档。以下是关键端点概述：

### 5.1 LangServe自动生成端点

- `POST /langgraph/invoke` - 同步调用工作流
- `POST /langgraph/stream` - SSE流式调用工作流
- `POST /langgraph/batch` - 批量调用工作流
- `POST /langgraph/stream_events` - 详细事件流（调试）

### 5.2 工作流管理API

- `GET /api/v1/workflows` - 获取工作流列表
- `POST /api/v1/workflows` - 创建新工作流
- `GET /api/v1/workflows/{workflowId}` - 获取工作流详情
- `DELETE /api/v1/workflows/{workflowId}` - 取消工作流
- `POST /api/v1/workflows/{workflowId}/resume` - 恢复暂停的工作流

### 5.3 人工确认API

- `GET /api/v1/confirmations/pending` - 获取待确认列表
- `GET /api/v1/confirmations/{confirmationId}` - 获取确认详情
- `POST /api/v1/confirmations/{confirmationId}/respond` - 响应人工确认

### 5.4 模型配置API

- `GET /api/v1/models` - 获取模型配置列表
- `POST /api/v1/models` - 添加模型配置
- `PUT /api/v1/models/{modelId}` - 更新模型配置
- `DELETE /api/v1/models/{modelId}` - 删除模型配置
- `POST /api/v1/models/{modelId}/test` - 测试模型连接

### 5.5 认证API

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新Token

### 5.6 健康检查

- `GET /api/v1/health` - 服务健康状态

---

## 6. Components

### 6.1 核心组件列表

**LangGraph Workflow Engine（工作流引擎）**

- 管理八大智能体的StateGraph编排和执行
- 处理Phase 0-4的状态转换
- 实现Human-in-Loop的interrupt/resume机制
- 依赖：LangGraph SDK、ModelAdapterService、DatabaseService

**LangServe API Gateway（API网关）**

- 自动生成RESTful API端点
- 提供SSE流式传输支持
- 集成OpenAPI文档和Playground UI
- 依赖：FastAPI、WorkflowEngine、AuthMiddleware

**Model Adapter Service（模型适配器）**

- 统一的模型调用接口
- 支持Qwen、GLM、DeepSeek的本地和云端API
- 实现模型热切换和降级策略
- 提供重试、超时、限流等容错机制

**Agent Node Implementations（智能体节点）**

- 实现八大智能体的具体逻辑
- 处理智能体的输入输出转换
- 集成Prompt模板和知识库引用

**Database Service（数据库服务）**

- 管理PostgreSQL和Redis的连接和操作
- 提供Repository模式的数据访问接口
- 实现LangGraph Checkpoint的PostgreSQL后端

**Frontend Vue Application（前端应用）**

- 工作流监控的用户界面
- 实时展示智能体执行状态和输出
- 处理人工确认交互
- 管理用户认证和会话

**SSE Client Service（SSE客户端）**

- 建立和维护SSE长连接
- 解析SSE事件流
- 实现自动重连和心跳检测

**Human Confirmation Component（人工确认组件）**

- 展示待确认的上下文信息
- 处理用户决策输入
- 提供直观的决策界面

---

## 7. External APIs

### 7.1 国产大模型API

**Qwen（通义千问）API**

- Base URL: `https://dashscope.aliyuncs.com/api/v1` (云端) 或 `http://localhost:8000/v1` (本地)
- 认证: API Key
- 关键端点: `POST /chat/completions`

**GLM（智谱AI）API**

- Base URL: `https://open.bigmodel.cn/api/paas/v4` (云端) 或 `http://localhost:8001/v1` (本地)
- 认证: API Key
- 关键端点: `POST /chat/completions`

**DeepSeek API**

- Base URL: `https://api.deepseek.com/v1` (云端) 或 `http://localhost:8002/v1` (本地)
- 认证: API Key
- 关键端点: `POST /chat/completions`

### 7.2 GitHub API（Phase 2.5）

- Base URL: `https://api.github.com`
- 认证: Personal Access Token
- 用途: 代码生成后的仓库操作

---

## 8. Core Workflows

### 8.1 完整APS工作流执行（含Human-in-Loop）

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as Vue前端
    participant API as LangServe API
    participant WF as WorkflowEngine
    participant Orch as Orchestrator
    participant Algo as Algorithm
    participant Code as Code Implementation
    participant DB as PostgreSQL
    participant Model as 国产模型

    User->>Frontend: 提交问题描述
    Frontend->>API: POST /workflows
    API->>DB: 创建WorkflowExecution
    API->>WF: 启动工作流

    Note over WF: Phase 0: 问题理解
    WF->>Orch: 执行Orchestrator
    Orch->>Model: 调用Qwen模型
    Model-->>Orch: 返回算法推荐
    Orch->>DB: 保存AgentExecution

    Note over WF: Phase 1: 人工确认触发点
    WF->>DB: 创建HumanConfirmation(P1)
    WF->>DB: 保存Checkpoint
    WF-->>API: interrupt(等待人工确认)
    API-->>Frontend: SSE事件: workflow_paused

    Frontend->>User: 显示确认界面
    User->>Frontend: 批准算法推荐
    Frontend->>API: POST /confirmations/{id}/respond
    API->>WF: resume(decision)

    Note over WF: Phase 2: 约束和目标分析
    WF->>Algo: 执行Algorithm
    Algo->>Model: 调用模型
    Model-->>Algo: 返回分析结果

    Note over WF: Phase 2.5: 代码实现
    WF->>Code: 执行Code Implementation
    Code->>Model: 调用模型生成代码
    Model-->>Code: 返回代码
    Code->>DB: 保存代码输出

    Note over WF: 工作流完成
    WF->>DB: 更新status=completed
    WF-->>API: 返回最终结果
    API-->>Frontend: SSE事件: workflow_complete
    Frontend->>User: 展示完整结果
```

---

## 9. Database Schema

### 9.1 PostgreSQL表结构

```sql
-- workflows表
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed')),
    current_phase VARCHAR(10) CHECK (current_phase IN ('P0', 'P1', 'P2', 'P2.5', 'P3', 'P4')),
    config JSONB NOT NULL,
    checkpoint_id VARCHAR(255),
    human_confirmation_required BOOLEAN DEFAULT false,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_started_at ON workflows(started_at DESC);

-- agent_executions表
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN (
        'orchestrator', 'algorithm', 'constraint', 'objective',
        'domain', 'code_implementation', 'extension', 'quality'
    )),
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    input JSONB NOT NULL,
    output JSONB,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration NUMERIC(10, 2),
    token_usage JSONB,
    error JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_executions_workflow_id ON agent_executions(workflow_id);
CREATE INDEX idx_agent_executions_agent_type ON agent_executions(agent_type);

-- agent_messages表
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_execution_id UUID NOT NULL REFERENCES agent_executions(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('text', 'thought', 'result', 'error', 'system')),
    content TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_agent_messages_agent_execution_id ON agent_messages(agent_execution_id);
CREATE INDEX idx_agent_messages_workflow_id ON agent_messages(workflow_id);

-- human_confirmations表
CREATE TABLE human_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    trigger_point VARCHAR(10) NOT NULL CHECK (trigger_point IN ('P1', 'P2', 'P2.5')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'modified', 'timeout')),
    context JSONB NOT NULL,
    decision JSONB,
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMP WITH TIME ZONE,
    timeout INTEGER NOT NULL DEFAULT 3600,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_human_confirmations_workflow_id ON human_confirmations(workflow_id);
CREATE INDEX idx_human_confirmations_status ON human_confirmations(status);

-- model_configs表
CREATE TABLE model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('qwen', 'glm', 'deepseek')),
    model_name VARCHAR(255) NOT NULL,
    deployment_type VARCHAR(50) NOT NULL CHECK (deployment_type IN ('local_vllm', 'local_ollama', 'cloud_api')),
    endpoint TEXT NOT NULL,
    api_key TEXT,
    enabled BOOLEAN DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 0,
    config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(provider, model_name)
);

CREATE INDEX idx_model_configs_enabled ON model_configs(enabled);
CREATE INDEX idx_model_configs_priority ON model_configs(priority DESC);
```

---

## 10. Unified Project Structure

```
BMAD-METHOD/
├── .github/workflows/          # CI/CD
├── backend/                    # 后端（Python）
│   ├── langgraph_service/      # 工作流服务
│   │   ├── main.py
│   │   ├── workflow_engine.py
│   │   ├── api_gateway.py
│   │   ├── middleware/
│   │   ├── agents/             # 八大智能体
│   │   └── services/
│   ├── model_adapters/         # 模型适配器
│   ├── shared/                 # 后端共享
│   │   ├── database/
│   │   └── utils/
│   └── tests/
├── frontend/web/               # 前端（Vue）
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── composables/
│   │   ├── stores/             # Pinia
│   │   ├── router/
│   │   ├── services/
│   │   └── main.ts
│   ├── tests/
│   └── package.json
├── shared/types/               # 共享类型定义
├── docker/                     # Docker配置
├── docs/                       # 文档
└── scripts/                    # 脚本
```

---

## 11. Development Workflow

### 11.1 环境搭建

```bash
# 1. Python环境（conda）
conda create -n bmad-langgraph python=3.11
conda activate bmad-langgraph

# 2. 安装依赖
cd backend
pip install -r requirements.txt

cd ../frontend/web
npm install

# 3. 启动数据库
cd ../../docker
docker-compose -f docker-compose.dev.yml up -d postgres redis

# 4. 配置环境变量
cp ../.env.example .env
# 编辑.env配置数据库和API密钥
```

### 11.2 开发命令

```bash
# 启动后端
cd backend
uvicorn langgraph_service.main:app --reload --port 8000

# 启动前端
cd frontend/web
npm run dev

# 运行测试
cd backend && pytest tests/
cd frontend/web && npm run test
```

---

## 12. Deployment Architecture

### 12.1 部署环境

| 环境        | 前端URL                          | 后端URL                              | 用途     |
| ----------- | -------------------------------- | ------------------------------------ | -------- |
| Development | http://localhost:5173            | http://localhost:8000                | 本地开发 |
| Staging     | https://staging.bmad.example.com | https://staging-api.bmad.example.com | 预生产   |
| Production  | https://bmad.example.com         | https://api.bmad.example.com         | 生产     |

### 12.2 Docker Compose部署

```yaml
# docker/docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.frontend

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

---

## 13. Security and Performance

### 13.1 安全要求

**前端安全**:

- CSP Headers配置
- XSS防护（Vue自动转义）
- JWT存储在httpOnly cookie

**后端安全**:

- Pydantic输入验证
- SQL参数化查询
- API限流（10/minute）
- CORS策略配置

**认证安全**:

- JWT Token（24小时过期）
- Refresh Token（7天）

### 13.2 性能优化

**前端**:

- Bundle大小 < 500KB (gzipped)
- 路由懒加载
- API响应缓存（Redis，5分钟）

**后端**:

- API响应 < 2秒
- 模型调用 < 10秒
- 数据库连接池（5-20）
- Redis缓存热点数据

---

## 14. Testing Strategy

### 14.1 测试金字塔

```
        E2E (5%)
       /        \
  Integration (25%)
     /            \
Frontend Unit  Backend Unit
  (35%)          (35%)
```

### 14.2 测试覆盖率目标

- 后端单元测试: >80%
- 前端组件测试: >70%
- 集成测试: 关键路径100%
- E2E测试: 核心用户流程

---

## 15. Coding Standards

### 15.1 关键规则

1. **类型共享**: 始终在`shared/types/`定义类型
2. **API调用**: 前端必须通过service层
3. **环境变量**: 通过config对象访问
4. **错误处理**: 使用标准错误处理器
5. **状态管理**: 使用Pinia actions修改state

### 15.2 命名约定

| 元素        | 前端                 | 后端       | 示例                  |
| ----------- | -------------------- | ---------- | --------------------- |
| 组件        | PascalCase           | -          | `WorkflowMonitor.vue` |
| Composables | camelCase with 'use' | -          | `useWorkflow.ts`      |
| API路由     | -                    | kebab-case | `/api/user-profile`   |
| 数据库表    | -                    | snake_case | `agent_executions`    |

---

## 16. Error Handling Strategy

### 16.1 统一错误格式

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}
```

### 16.2 错误处理流程

1. 后端抛出BMadException
2. 中间件捕获并格式化
3. 返回统一JSON错误响应
4. 前端拦截器显示用户友好消息
5. structlog记录详细错误日志

---

## 17. Monitoring and Observability

### 17.1 监控栈

- **前端**: Console + Performance API
- **后端**: Prometheus + Grafana (Phase 2)
- **错误追踪**: structlog
- **性能监控**: LangSmith (可选)

### 17.2 关键指标

**前端**:

- Core Web Vitals
- JavaScript错误率
- API响应时间

**后端**:

- 请求速率 (RPM)
- 错误率 (%)
- 响应时间 (P50, P95, P99)
- 模型调用延迟

---

## 附录

### A. 参考文档

- [LangGraph 1.0 Documentation](https://langchain-ai.github.io/langgraph/)
- [LangServe Documentation](https://python.langchain.com/docs/langserve)
- [Vue 3 Documentation](https://vuejs.org/)
- [Ant Design Vue Documentation](https://antdv.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### B. 联系方式

- **架构师**: Winston
- **产品经理**: John
- **项目仓库**: https://github.com/QQhuxuhui/BMAD-METHOD

---

**文档版本**: v1.0  
**最后更新**: 2025-11-04  
**状态**: ✅ 已完成，准备实施
