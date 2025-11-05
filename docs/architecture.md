# BMAD-METHOD LangGraph集成方案全栈架构文档

**文档版本**: v1.0
**创建日期**: 2025-11-05
**作者**: Winston (Architect)
**状态**: Draft

---

## Introduction

本文档概述了BMAD-METHOD LangGraph集成方案的完整全栈架构，包括后端系统、前端实现及其集成方式。它是AI驱动开发的唯一真实来源，确保整个技术栈的一致性。

这种统一的方法结合了传统上分离的后端和前端架构文档，简化了现代全栈应用的开发流程，因为这些关注点日益交织在一起。

### Starter Template or Existing Project

本项目采用了**混合策略**，结合了成熟模板和从零搭建：

**后端项目（Story 1.2）**：

- 基于 [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)
- 克隆模板后进行BMAD特定适配
- **节省80%开发时间**（3-5天 → 6-8小时）
- 获得生产级特性：
  - Langfuse 3.0.3 (LLM可观测性追踪)
  - Prometheus + Grafana (监控可视化)
  - JWT认证 + slowapi限流
  - structlog结构化日志
  - Docker Compose容器化

**前端项目（Story 1.3）**：

- **从零搭建**，确保完全掌控代码质量
- 参考但不全盘克隆antdv-pro最佳实践
- **开发时间优化**：30小时完成高质量交付
- 优势：
  - 代码简洁精准，无冗余
  - 完全贴合需求（Dashboard、WorkflowMonitor、Settings）
  - 团队深入理解Vue 3生态
  - 长期可维护性强

**架构约束**：

- 必须保留模板中的生产级特性（监控、安全、日志）
- 前端架构需完全适配后端API设计
- 保持Monorepo结构便于共享类型定义

### Change Log

| Date       | Version | Description                            | Author              |
| ---------- | ------- | -------------------------------------- | ------------------- |
| 2025-11-05 | v1.0    | 基于PRD v1.2和实际项目创建初始架构文档 | Winston (Architect) |

---

## High Level Architecture

### Technical Summary

BMAD-METHOD LangGraph集成方案采用**现代化微服务架构**，结合容器化部署和云原生可观测性。后端基于FastAPI 0.115.12和LangGraph 0.4.1构建，利用Python 3.13.2的最新特性实现八大智能体工作流编排，通过PostgreSQL持久化checkpoint状态，Redis提供会话缓存。前端采用Vue 3.5 Composition API + TypeScript 5.9，使用Ant Design Vue 4.2构建响应式监控界面，通过Axios与后端RESTful API通信，Pinia管理全局状态。整个系统通过Docker Compose实现一键启动的本地开发环境，集成Langfuse进行LLM调用追踪，Prometheus + Grafana提供实时监控和告警，支持国产大模型（Qwen/GLM/DeepSeek）的即插即用。架构设计遵循"轻适配器"原则，Phase 1优先实现核心价值（2-3周），为后续YAML编译器（Phase 2）和智能体工厂（Phase 3）预留扩展空间。

### Platform and Infrastructure Choice

经过对比分析，我们选择了**混合云 + 容器化**的基础设施方案：

**推荐方案（已实施）**：

- **主平台**：Docker + Docker Compose（本地开发和生产环境）
- **数据库**：PostgreSQL 16（LangGraph checkpoint后端）+ Redis 7（会话/缓存）
- **监控可观测性**：Langfuse 3.0.3（LLM追踪）+ Prometheus 2.48+（指标收集）+ Grafana 10.0+（可视化）
- **安全认证**：JWT Token + slowapi 0.1.9（API限流）
- **部署方式**：容器化部署，支持私有云和公有云

**最终选择**：

- **平台**：Docker + Docker Compose
- **关键服务**：FastAPI、PostgreSQL、Redis、Langfuse、Prometheus、Grafana
- **部署主机和区域**：支持本地开发环境和私有云部署（具体区域待Phase 1完成后根据实际需求确定）

### Repository Structure

本项目采用**Monorepo**结构，所有代码集中在单一仓库管理：

**结构选择**：Monorepo（单一仓库）
**Monorepo工具**：Git子目录（轻量级，无需额外工具如Nx/Turborepo）
**包组织策略**：按功能模块划分（backend、frontend/web、docs）

**实际仓库结构**：

```
BMAD-METHOD/
├── backend/                    # FastAPI + LangGraph后端
│   ├── app/                   # 应用代码
│   ├── docker-compose.yml     # 本地开发环境
│   ├── pyproject.toml         # Python依赖（uv管理）
│   └── README.md              # 后端文档
├── frontend/web/              # Vue 3前端
│   ├── src/                   # 源代码
│   ├── package.json           # npm依赖
│   └── README.md              # 前端文档
├── docs/                      # 项目文档
│   ├── langgraph集成方案.md   # PRD v1.2
│   ├── stories/               # 用户故事
│   └── architecture.md        # 本架构文档
├── .bmad-core/                # BMAD工具链
└── README.md                  # 项目总览
```

### High Level Architecture Diagram

```mermaid
graph TB
    subgraph "用户层"
        User[用户浏览器]
        Mobile[移动设备<br/>次要支持]
    end

    subgraph "前端层 - Vue 3 SPA"
        VueApp[Vue 3.5 App<br/>Ant Design Vue UI]
        Router[Vue Router<br/>路由管理]
        Store[Pinia Store<br/>状态管理]
        APIClient[Axios Client<br/>API调用层]
    end

    subgraph "后端层 - FastAPI Microservices"
        FastAPI[FastAPI 0.115.12<br/>RESTful API]
        Auth[JWT Auth<br/>slowapi限流]
        LangGraph[LangGraph 0.4.1<br/>工作流引擎]
        ModelAdapter[国产模型适配器<br/>Qwen/GLM/DeepSeek]
    end

    subgraph "智能体层 - BMAD 8 Agents"
        Orchestrator[编排智能体]
        Algorithm[算法智能体]
        Constraint[约束智能体]
        Domain[领域智能体]
        Code[代码实现专家]
    end

    subgraph "数据层"
        PostgreSQL[(PostgreSQL 16<br/>Checkpoint存储)]
        Redis[(Redis 7<br/>Session/Cache)]
    end

    subgraph "监控层"
        Langfuse[Langfuse 3.0.3<br/>LLM追踪]
        Prometheus[Prometheus<br/>指标收集]
        Grafana[Grafana<br/>监控面板]
    end

    subgraph "外部服务"
        LLM[国产大模型服务<br/>vLLM/Ollama]
    end

    User -->|HTTPS| VueApp
    Mobile -.->|响应式支持| VueApp
    VueApp --> Router
    VueApp --> Store
    VueApp --> APIClient

    APIClient -->|REST API| FastAPI
    FastAPI --> Auth
    Auth -->|认证通过| LangGraph

    LangGraph --> ModelAdapter
    LangGraph --> Orchestrator
    Orchestrator --> Algorithm
    Orchestrator --> Constraint
    Orchestrator --> Domain
    Orchestrator --> Code

    ModelAdapter -->|API调用| LLM
    LangGraph -->|持久化| PostgreSQL
    FastAPI -->|缓存| Redis

    FastAPI -.->|追踪| Langfuse
    FastAPI -.->|指标| Prometheus
    Prometheus -.->|可视化| Grafana

    style VueApp fill:#42b883
    style FastAPI fill:#009688
    style LangGraph fill:#ff6b6b
    style PostgreSQL fill:#336791
    style Redis fill:#dc382d
```

### Architectural Patterns

以下是指导全栈开发的关键架构模式：

- **微服务架构（Microservices）**：后端采用FastAPI微服务架构，LangGraph工作流引擎作为独立服务运行，支持水平扩展 - _理由：_ 符合云原生最佳实践，便于未来Phase 3的智能体工厂横向扩展

- **事件驱动架构（Event-Driven）**：LangGraph工作流基于StateGraph的事件驱动模型，智能体间通过状态变更触发执行 - _理由：_ 支持复杂的人机协作和异步工作流，提升系统响应性

- **单页应用（SPA）**：前端采用Vue 3 SPA架构，通过Vue Router实现客户端路由 - _理由：_ 提供流畅的用户体验，减少页面刷新，适合实时监控界面

- **组件化UI（Component-Based UI）**：使用Vue 3 Composition API + Ant Design Vue构建可复用组件 - _理由：_ 提升开发效率，保证UI一致性，便于团队协作和代码维护

- **Repository模式（Repository Pattern）**：后端数据访问通过SQLModel抽象数据库操作 - _理由：_ 解耦业务逻辑和数据访问，便于测试和未来数据库迁移

- **API Gateway模式（API Gateway）**：FastAPI作为单一入口点，集中处理认证、限流、日志 - _理由：_ 统一安全策略，简化前端调用，便于监控和审计

- **断路器模式（Circuit Breaker）**：LLM调用失败时自动降级和重试 - _理由：_ 提升系统韧性，避免外部服务故障影响整体可用性

- **轻适配器模式（Lightweight Adapter）**：国产模型适配器最小化侵入，复用LangChain生态 - _理由：_ 降低维护成本，保持与上游社区同步，快速支持新模型

- **Human-in-the-Loop（HITL）**：基于LangGraph 0.4.1的interrupt机制实现人工确认点（P1/P2/P2.5） - _理由：_ 提升AI决策透明度，在关键节点保留人类控制权

---

## Tech Stack

这是整个项目的**权威技术选型表**，所有开发必须遵循这些确切的版本。以下技术栈基于Story 1.2/1.3实际完成的项目配置。

### Technology Stack Table

| Category                 | Technology                    | Version                              | Purpose               | Rationale                                                            |
| ------------------------ | ----------------------------- | ------------------------------------ | --------------------- | -------------------------------------------------------------------- |
| **Frontend Language**    | TypeScript                    | 5.9.3                                | 前端类型安全编程语言  | 提供编译时类型检查，减少运行时错误，提升大型项目可维护性             |
| **Frontend Framework**   | Vue 3                         | 3.5.22                               | 前端响应式UI框架      | Composition API提供更好的逻辑复用，性能优于Vue 2，社区活跃且文档完善 |
| **UI Component Library** | Ant Design Vue                | 4.2.6                                | 企业级UI组件库        | 提供50+高质量组件，减少70%UI开发时间，中文文档友好                   |
| **State Management**     | Pinia                         | 2.3.1                                | Vue 3官方推荐状态管理 | 比Vuex更轻量（<1KB），TypeScript原生支持，devtools集成完善           |
| **Frontend Router**      | Vue Router                    | 4.6.3                                | Vue 3官方路由         | 支持动态路由、路由守卫、懒加载，与Vue 3深度集成                      |
| **HTTP Client**          | Axios                         | 1.13.2                               | HTTP请求库            | 支持拦截器、请求取消、自动转换JSON，浏览器兼容性好                   |
| **Frontend Utils**       | @vueuse/core                  | 14.0.0                               | Vue组合式工具集       | 提供200+ Composition API工具函数，减少重复代码                       |
| **Date/Time**            | dayjs                         | 1.11.19                              | 轻量级日期处理库      | 仅2KB，API与moment.js兼容，支持国际化和插件扩展                      |
| **Backend Language**     | Python                        | 3.13.2                               | 后端编程语言          | 最新稳定版，性能提升15%，AI生态最完善                                |
| **Backend Framework**    | FastAPI                       | 0.115.12+                            | 现代异步Web框架       | 自动生成OpenAPI文档，原生async/await，性能比Flask快5倍               |
| **API Style**            | RESTful                       | OpenAPI 3.0                          | HTTP API设计风格      | 标准化、易于理解、工具链成熟，满足当前需求（YAGNI原则）              |
| **Workflow Engine**      | LangGraph                     | 0.4.1+                               | AI智能体编排引擎      | 内置checkpoint持久化，支持HITL，图形化工作流控制                     |
| **LLM Framework**        | LangChain                     | 0.3.25+                              | LLM应用框架           | 与LangGraph无缝集成，丰富的工具和链式调用支持                        |
| **Database**             | PostgreSQL                    | 16+                                  | 关系型数据库          | LangGraph checkpoint官方推荐，ACID保证，JSON支持                     |
| **Cache**                | Redis                         | 7+                                   | 内存数据库            | 支持会话存储、分布式锁、Pub/Sub，性能优异                            |
| **ORM**                  | SQLModel                      | 0.0.24+                              | Python SQL ORM        | Pydantic + SQLAlchemy融合，类型安全，与FastAPI完美集成               |
| **Authentication**       | JWT + bcrypt                  | python-jose 3.4.0+<br/>bcrypt 4.3.0+ | Token认证+密码加密    | 无状态认证适合微服务，bcrypt算法安全性高（抗彩虹表）                 |
| **Rate Limiting**        | slowapi                       | 0.1.9+                               | API限流保护           | 基于令牌桶算法，支持IP和用户维度限流，防止滥用                       |
| **LLM Tracing**          | Langfuse                      | 3.0.3                                | LLM可观测性平台       | 追踪每次LLM调用的token消耗、延迟、成本，支持实验对比                 |
| **Metrics**              | Prometheus                    | prometheus-client 0.19.0+            | 时序指标收集          | 云原生监控标准，支持多维度标签，PromQL查询强大                       |
| **Monitoring UI**        | Grafana                       | 10.0+                                | 监控可视化            | 丰富的图表类型，告警规则配置，与Prometheus完美集成                   |
| **Logging**              | structlog                     | 25.2.0+                              | 结构化日志库          | JSON格式日志便于解析，支持上下文绑定，性能高                         |
| **Frontend Testing**     | Vitest                        | 内置于Vite                           | 前端单元测试          | 与Vite共享配置，启动速度快，Vue组件测试友好                          |
| **Backend Testing**      | pytest                        | 8.3.5+                               | Python测试框架        | Fixture机制强大，插件生态丰富，异步测试支持完善                      |
| **E2E Testing**          | Playwright                    | TBD (Phase 2)                        | 端到端测试            | 跨浏览器支持，录制回放功能，比Cypress更现代                          |
| **Build Tool**           | Vite                          | 7.1.7                                | 前端构建工具          | 开发模式秒启动（ESBuild），生产构建快5倍（Rollup）                   |
| **Bundler**              | Rollup (via Vite)             | 内置于Vite                           | JavaScript打包工具    | Tree-shaking效果好，输出体积小，插件生态成熟                         |
| **Package Manager**      | uv (Python)<br/>npm (Node.js) | uv latest<br/>npm 10+                | 依赖管理工具          | uv比pip快10-100倍，npm最成熟稳定                                     |
| **Container**            | Docker + Docker Compose       | Docker 24+<br/>Compose 2+            | 容器化运行环境        | 环境一致性保证，一键启动开发环境，生产部署简化                       |
| **Web Server**           | uvicorn                       | 0.34.0+                              | ASGI服务器            | FastAPI官方推荐，支持HTTP/2、WebSocket，性能优异                     |
| **CSS Preprocessor**     | Sass                          | 1.93.3                               | CSS预处理器           | 变量、嵌套、混入功能，与Ant Design Vue变量定制集成                   |
| **Code Formatter**       | Prettier + Black              | prettier 3.6.2<br/>black (via ruff)  | 代码格式化            | 统一代码风格，减少code review争议，支持保存自动格式化                |
| **Linter**               | ESLint + Ruff                 | eslint 9.39.1<br/>ruff latest        | 代码检查              | 发现潜在bug，强制最佳实践，Ruff比flake8快10-100倍                    |

---

## Data Models

基于PRD需求和LangGraph 0.4.1架构，以下是系统核心数据模型。这些模型在后端使用SQLModel定义，通过OpenAPI自动生成TypeScript接口供前端使用。

### Model: User

**Purpose:** 用户账户管理，支持JWT认证和RBAC权限控制

**Key Attributes:**

- `id`: UUID - 用户唯一标识符
- `email`: String - 用户邮箱（唯一，用于登录）
- `username`: String - 用户名（唯一）
- `hashed_password`: String - bcrypt加密的密码哈希
- `is_active`: Boolean - 账户是否激活
- `is_superuser`: Boolean - 是否为超级管理员
- `created_at`: DateTime - 账户创建时间
- `last_login`: DateTime - 最后登录时间

**TypeScript Interface:**

```typescript
interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string; // ISO 8601
  last_login: string | null; // ISO 8601
}

interface UserCreate {
  email: string;
  username: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}
```

**Relationships:**

- 一对多 → WorkflowExecution
- 一对多 → HumanApproval

---

### Model: WorkflowExecution

**Purpose:** 记录完整的BMAD工作流执行过程，包括Phase 0-4的状态流转

**Key Attributes:**

- `id`: UUID - 工作流执行唯一标识符
- `user_id`: UUID - 发起用户ID
- `thread_id`: String - LangGraph线程ID
- `status`: Enum - 执行状态（pending/running/paused/completed/failed）
- `current_phase`: String - 当前执行阶段
- `input_data`: JSON - 用户输入
- `output_data`: JSON - 最终输出
- `started_at`: DateTime - 开始时间
- `completed_at`: DateTime - 完成时间
- `total_tokens`: Integer - 总token消耗
- `total_cost`: Decimal - 总成本

**TypeScript Interface:**

```typescript
type WorkflowStatus = 'pending' | 'running' | 'paused' | 'completed' | 'failed';
type WorkflowPhase = 'P0' | 'P1' | 'P2' | 'P2.5' | 'P3' | 'P4';

interface WorkflowExecution {
  id: string;
  user_id: string;
  thread_id: string;
  status: WorkflowStatus;
  current_phase: WorkflowPhase;
  input_data: {
    problem_description: string;
    domain?: string;
    constraints?: string[];
  };
  output_data: {
    algorithm?: string;
    code?: string;
    documentation?: string;
  } | null;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
  total_tokens: number;
  total_cost: number;
}
```

**Relationships:**

- 多对一 → User
- 一对多 → AgentExecution
- 一对多 → HumanApproval

---

### Model: AgentExecution

**Purpose:** 记录单个智能体的执行详情

**TypeScript Interface:**

```typescript
type AgentName = 'orchestrator' | 'algorithm' | 'constraint' | 'objective' | 'domain' | 'code_implementation' | 'extension' | 'quality';

interface AgentExecution {
  id: string;
  workflow_id: string;
  agent_name: AgentName;
  input_data: Record<string, any>;
  output_data: Record<string, any> | null;
  started_at: string;
  completed_at: string | null;
  duration_ms: number;
  token_count: number;
  model_used: string;
  status: 'success' | 'failed' | 'skipped';
  error_message: string | null;
}
```

---

### Model: HumanApproval

**Purpose:** 记录Human-in-the-Loop确认点的人工决策

**TypeScript Interface:**

```typescript
type ApprovalPoint = 'P1' | 'P2' | 'P2.5';
type ApprovalDecision = 'approved' | 'rejected' | 'modified';

interface HumanApproval {
  id: string;
  workflow_id: string;
  user_id: string;
  approval_point: ApprovalPoint;
  context_data: Record<string, any>;
  decision: ApprovalDecision;
  feedback: string;
  modified_data: Record<string, any> | null;
  created_at: string;
  decided_at: string | null;
}
```

---

### Model: ModelConfig

**Purpose:** 管理国产大模型配置

**TypeScript Interface:**

```typescript
type ModelProvider = 'qwen' | 'glm' | 'deepseek' | 'local';

interface ModelConfig {
  id: string;
  name: string;
  provider: ModelProvider;
  api_base_url: string;
  model_version: string;
  max_tokens: number;
  temperature: number;
  is_active: boolean;
  priority: number;
}
```

---

**数据模型关系图**：

```mermaid
erDiagram
    User ||--o{ WorkflowExecution : "发起"
    User ||--o{ HumanApproval : "审批"
    WorkflowExecution ||--o{ AgentExecution : "包含"
    WorkflowExecution ||--o{ HumanApproval : "需要"

    User {
        uuid id PK
        string email UK
        string username UK
        string hashed_password
        boolean is_active
        datetime created_at
    }

    WorkflowExecution {
        uuid id PK
        uuid user_id FK
        string thread_id UK
        enum status
        enum current_phase
        json input_data
        json output_data
        datetime started_at
    }

    AgentExecution {
        uuid id PK
        uuid workflow_id FK
        enum agent_name
        json input_data
        json output_data
        integer duration_ms
        integer token_count
    }

    HumanApproval {
        uuid id PK
        uuid workflow_id FK
        uuid user_id FK
        enum approval_point
        enum decision
        json context_data
        datetime decided_at
    }

    ModelConfig {
        uuid id PK
        string name UK
        enum provider
        string api_base_url
        boolean is_active
    }
```

---

## API Specification

完整的RESTful API规范，基于OpenAPI 3.0标准。FastAPI自动生成交互式API文档（Swagger UI: `http://localhost:8000/docs`）。

### 核心端点概览

**Authentication:**

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户

**Workflows:**

- `POST /api/v1/workflows` - 创建工作流
- `GET /api/v1/workflows` - 查询工作流列表
- `GET /api/v1/workflows/{id}` - 获取工作流详情
- `POST /api/v1/workflows/{id}/resume` - 恢复暂停的工作流
- `DELETE /api/v1/workflows/{id}` - 取消工作流

**Agents:**

- `GET /api/v1/workflows/{id}/agents` - 获取工作流的智能体列表
- `GET /api/v1/agents/{id}` - 获取智能体执行详情

**Approvals:**

- `GET /api/v1/approvals/pending` - 获取待确认列表
- `GET /api/v1/approvals/{id}` - 获取确认详情
- `POST /api/v1/approvals/{id}` - 提交确认决策

**Models:**

- `GET /api/v1/models` - 获取模型配置列表
- `POST /api/v1/models` - 创建模型配置（需superuser）
- `PATCH /api/v1/models/{id}` - 更新模型配置

**System:**

- `GET /health` - 健康检查
- `GET /metrics` - Prometheus指标

### 认证方式

所有需要认证的端点使用Bearer Token（JWT）：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 限流规则

- 登录端点：5次/分钟
- 工作流创建：10次/分钟
- 查询端点：100次/分钟

### 错误响应格式

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    request_id: string;
  };
}
```

---

## Components

系统被划分为以下主要逻辑组件，遵循单一职责原则和低耦合高内聚原则。

### 后端组件

#### API Gateway Component

**Responsibility:** 提供统一的HTTP API入口，处理请求路由、认证授权、限流和错误处理

**实现位置**: `backend/app/api/v1/`

**Technology Stack:**

- FastAPI 0.115.12
- Pydantic 2.11
- slowapi 0.1.9
- uvicorn 0.34

---

#### LangGraph Workflow Engine

**Responsibility:** 编排BMAD八大智能体工作流，管理StateGraph状态流转和checkpoint持久化

**Key Interfaces:**

- `create_workflow(input_data)` - 创建新工作流
- `resume_workflow(thread_id, user_input)` - 恢复暂停的工作流
- `interrupt_workflow(thread_id, approval_point)` - 暂停工作流等待人工确认

**实现位置**: `backend/app/core/langgraph/`

**Technology Stack:**

- LangGraph 0.4.1
- langgraph-checkpoint-postgres 2.0.19
- langchain-core 0.3.58

---

#### Model Adapter Service

**Responsibility:** 提供统一的国产大模型调用接口，支持Qwen、GLM、DeepSeek等模型的热切换

**实现位置**: `backend/model_adapters/`（待Story 1.4实现）

---

#### Database Service

**Responsibility:** 管理数据库连接、事务和ORM操作

**实现位置**: `backend/app/services/database.py`

**Technology Stack:**

- SQLModel 0.0.24
- psycopg2-binary 2.9.10

---

#### Logging & Monitoring Service

**Responsibility:** 结构化日志记录、Prometheus指标导出、Langfuse LLM追踪

**实现位置**:

- `backend/app/core/logging.py`
- `backend/app/core/metrics.py`
- `backend/app/core/middleware.py`

**Technology Stack:**

- structlog 25.2.0
- langfuse 3.0.3
- prometheus-client 0.19.0

---

### 前端组件

#### Application Shell

**Responsibility:** 应用主框架，包含顶部导航、侧边栏、底部栏和路由出口

**实现位置**: `frontend/web/src/layouts/`

**Technology Stack:**

- Vue 3.5 Composition API
- Ant Design Vue 4.2

---

#### Page Views

**Responsibility:** 各功能页面的顶层视图组件

**实现位置**: `frontend/web/src/views/`

- `Dashboard.vue` - 工作流概览仪表盘
- `WorkflowMonitor.vue` - 实时工作流监控
- `Settings.vue` - 用户设置和模型配置

---

#### API Service Layer

**Responsibility:** 封装所有HTTP API调用，提供类型安全的接口

**实现位置**: `frontend/web/src/services/`

**Technology Stack:**

- Axios 1.13.2
- TypeScript 5.9

---

#### State Management Stores

**Responsibility:** 管理全局应用状态

**实现位置**: `frontend/web/src/stores/`

- `user.ts` - 用户登录状态、Token、权限
- `app.ts` - 全局UI状态（侧边栏折叠、主题等）

**Technology Stack:**

- Pinia 2.3.1

---

### Component Interaction Diagram

```mermaid
graph TB
    subgraph "Frontend"
        FE[Vue 3 App] --> Router[Vue Router]
        FE --> Store[Pinia Store]
        FE --> API[API Service]
    end

    subgraph "Backend"
        Gateway[API Gateway] --> Auth[Auth Service]
        Gateway --> Workflow[LangGraph Engine]
        Workflow --> Model[Model Adapter]
        Workflow --> DB[Database]
    end

    API -->|REST| Gateway
    Model --> LLM[国产大模型]
    DB --> PG[(PostgreSQL)]
    DB --> RD[(Redis)]
```

---

## Core Workflows

### 工作流1: 用户登录和Token获取

```mermaid
sequenceDiagram
    participant U as 用户浏览器
    participant FE as Vue Frontend
    participant API as FastAPI Gateway
    participant Auth as Auth Service
    participant DB as PostgreSQL

    U->>FE: 输入邮箱和密码
    FE->>API: POST /api/v1/auth/login
    API->>Auth: authenticate_user(email, password)
    Auth->>DB: 查询用户
    DB-->>Auth: 返回用户数据
    Auth->>Auth: 验证密码(bcrypt)
    Auth->>Auth: 生成JWT Token
    Auth-->>API: 返回Token
    API-->>FE: 200 OK + Token
    FE->>FE: 保存Token到localStorage
    FE->>FE: 更新Pinia userStore
    FE-->>U: 跳转到Dashboard
```

---

### 工作流2: 创建和执行BMAD工作流（含HITL）

```mermaid
sequenceDiagram
    participant U as 用户
    participant FE as Vue Frontend
    participant API as FastAPI Gateway
    participant LG as LangGraph Engine
    participant MA as Model Adapter
    participant LLM as 国产大模型
    participant DB as PostgreSQL

    U->>FE: 输入问题描述
    FE->>API: POST /api/v1/workflows
    API->>LG: create_workflow(input_data)
    LG->>DB: 创建WorkflowExecution记录

    loop Phase 0-4
        LG->>MA: 调用智能体
        MA->>LLM: API请求
        LLM-->>MA: 返回响应
        MA-->>LG: 智能体输出
        LG->>DB: 保存checkpoint
    end

    Note over LG: P1确认点
    LG->>DB: 创建HumanApproval记录
    LG-->>API: 返回status=paused
    API-->>FE: 工作流已暂停
    FE-->>U: 显示算法推荐，等待确认

    U->>FE: 批准算法
    FE->>API: POST /api/v1/approvals/{id}
    API->>LG: resume_workflow(thread_id)
    LG->>DB: 加载checkpoint

    loop 继续执行
        LG->>MA: 调用智能体
    end

    LG-->>API: 返回最终结果
    API-->>FE: 工作流完成
    FE-->>U: 显示生成的代码
```

---

## Database Schema

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    INDEX idx_email (email)
);

-- 工作流执行表
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_phase VARCHAR(10) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- 智能体执行表
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    token_count INTEGER DEFAULT 0,
    model_used VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    INDEX idx_workflow_id (workflow_id)
);

-- 人工确认表
CREATE TABLE human_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    approval_point VARCHAR(10) NOT NULL,
    context_data JSONB NOT NULL,
    decision VARCHAR(20),
    feedback TEXT,
    modified_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    decided_at TIMESTAMP,
    INDEX idx_workflow_id (workflow_id)
);

-- 模型配置表
CREATE TABLE model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(20) NOT NULL,
    api_base_url VARCHAR(500) NOT NULL,
    api_key VARCHAR(500) NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3, 2) DEFAULT 0.7,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 10
);
```

---

## Unified Project Structure

```
BMAD-METHOD/
├── backend/                          # FastAPI + LangGraph后端
│   ├── app/
│   │   ├── api/v1/                  # API路由
│   │   ├── core/                    # 核心模块
│   │   │   ├── config.py
│   │   │   ├── langgraph/          # LangGraph工作流
│   │   │   ├── logging.py
│   │   │   └── metrics.py
│   │   ├── models/                  # SQLModel数据模型
│   │   ├── schemas/                 # Pydantic Schema
│   │   ├── services/                # 业务服务层
│   │   └── main.py                  # 应用入口
│   ├── model_adapters/              # 国产模型适配器
│   ├── tests/                       # 后端测试
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
├── frontend/web/                    # Vue 3前端
│   ├── src/
│   │   ├── components/              # UI组件
│   │   ├── layouts/                 # 布局组件
│   │   ├── router/                  # Vue Router
│   │   ├── services/                # API服务层
│   │   ├── stores/                  # Pinia状态管理
│   │   ├── views/                   # 页面视图
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── docs/                            # 项目文档
│   ├── architecture.md              # 本架构文档
│   ├── langgraph集成方案.md         # PRD v1.2
│   └── stories/                     # 用户故事
└── README.md
```

---

## Development Workflow

### Prerequisites

```bash
- Docker 24+ 和 Docker Compose 2+
- Python 3.13.2 (通过conda管理)
- Node.js 20+ (通过nvm管理)
- uv (Python包管理器)
```

### Initial Setup

```bash
# 1. 克隆仓库
git clone <repository-url>
cd BMAD-METHOD

# 2. 后端设置
cd backend
conda activate bmad-langgraph
uv sync
cp .env.example .env
docker-compose up -d

# 3. 前端设置
cd ../frontend/web
source ~/.nvm/nvm.sh
nvm use 20
npm install
cp .env.development .env.local
```

### Development Commands

```bash
# 启动后端 (终端1)
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000

# 启动前端 (终端2)
cd frontend/web
npm run dev

# 运行测试
cd backend && pytest tests/
cd frontend/web && npm run test
```

---

## Security and Performance

**Frontend Security:**

- XSS Prevention: Vue 3自动转义
- Token存储: localStorage
- HTTPS强制: 生产环境

**Backend Security:**

- Input Validation: Pydantic自动验证
- Rate Limiting: 5-100次/分钟
- CORS: 仅允许前端域名

**Performance Targets:**

- Frontend Bundle: < 500KB (gzipped)
- API Response: < 2秒（非LLM）
- Database Query: < 100ms

---

## Testing Strategy

**Frontend:**

- Unit: Vitest
- E2E: Playwright (Phase 2)

**Backend:**

- Unit: pytest
- Integration: FastAPI TestClient
- E2E: 登录 → 创建工作流 → HITL确认

---

## Coding Standards

**Critical Rules:**

- Type Sharing: TypeScript类型通过OpenAPI生成
- API Calls: 必须通过service层，禁止直接axios
- State Updates: 使用Pinia actions，禁止直接修改state

**Naming Conventions:**

| Element    | Frontend   | Backend    |
| ---------- | ---------- | ---------- |
| Components | PascalCase | -          |
| Functions  | camelCase  | snake_case |
| API Routes | -          | kebab-case |
| Tables     | -          | snake_case |

---

## Error Handling

**Error Format:**

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    request_id: string;
  };
}
```

**Frontend:** Axios拦截器统一处理
**Backend:** FastAPI全局异常处理

---

## Monitoring

**Stack:**

- Frontend: Vite性能监控
- Backend: Prometheus + Grafana
- LLM Tracing: Langfuse
- Logging: structlog

**Key Metrics:**

- Core Web Vitals
- API响应时间
- LLM token消耗
- 错误率

---

## 附录

### 相关文档

- PRD: `docs/langgraph集成方案.md` (v1.2)
- User Stories: `docs/stories/`
- Quick Start: `backend/README.md`, `frontend/web/README.md`

### 联系方式

- 架构师: Winston (Architect)
- 项目仓库: BMAD-METHOD
- 文档更新: 2025-11-05

---

**文档结束**
