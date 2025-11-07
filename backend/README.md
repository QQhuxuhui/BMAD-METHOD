# BMAD LangGraph Service

> **基于**: [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)
> **Story**: Story 1.2 - 初始化FastAPI+LangGraph后端项目
> **实施日期**: 2025-11-05

BMAD（Business Model Analysis & Design）智能体工作流服务，基于生产级FastAPI模板构建，集成LangGraph 0.4.1用于智能体编排，提供完整的监控、认证和可观测性特性。

## BMAD项目特定说明

### 快速开始（BMAD开发者）

1. **激活Python环境**:

```bash
conda activate bmad-langgraph  # Python 3.13.2
```

2. **启动开发服务器**:

```bash
cd backend
APP_ENV=development .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

3. **访问服务**:

- API文档: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health
- 根端点: http://127.0.0.1:8000/

### BMAD集成配置

本服务已集成Story 1.1的基础设施：

**数据库配置** (PostgreSQL):

- 主机: localhost:5432
- 数据库: bmad_langgraph_dev
- 用户: bmad_user
- 配置文件: `.env.development`

**缓存配置** (Redis):

- 主机: localhost:6379
- 数据库: 0
- 用途: Session存储、Rate Limiting

**前端集成** (CORS):

- 允许来源: http://localhost:3000, http://localhost:5173, http://localhost:8000

### 环境管理

本项目使用**conda + uv**的环境管理方案：

```bash
# 环境信息
Python版本: 3.13.2
包管理器: uv (现代Python包管理器)
依赖数量: 129个包

# 常用命令
conda activate bmad-langgraph           # 激活环境
uv pip list                             # 查看已安装包
uv pip install <package>                # 安装新包
uv sync                                 # 同步所有依赖
```

### 目录结构（BMAD特定）

```
backend/
├── app/                      # FastAPI应用（来自模板）
│   ├── main.py              # 应用入口
│   ├── api/v1/              # API路由
│   ├── core/                # 核心配置（数据库、Redis、日志）
│   ├── middleware/          # 中间件（CORS、日志、错误处理）
│   ├── agents/              # LangGraph智能体
│   └── utils/               # 工具函数
├── model_adapters/          # BMAD模型适配器（Story 1.4）
├── shared/                  # BMAD共享代码（Story 1.4）
├── tests/                   # 测试目录
├── .env.development         # BMAD开发环境配置
└── pyproject.toml          # 项目依赖配置
```

### 开发注意事项

1. **环境变量**: 使用`.env.development`配置，包含BMAD特定设置
2. **数据库迁移**: ORM自动处理表创建，如有问题运行`schemas.sql`
3. **API Key**: 开发环境使用占位符密钥，生产环境需配置真实密钥
4. **监控**: Langfuse、Prometheus、Grafana配置已保留，需配置密钥启用

### 工作流系统 (Story 1.5.x)

**八智能体工作流架构**:

```
P0 (Orchestrator) → P1 (Algorithm/Constraint/Objective) → P1 Approval (HITL)
  → P2 (Domain) → P3 (Code Impl/Extension) → P2.5 Approval (HITL)
  → P4 (Quality) → END
```

**关键特性**:

- ✅ StateGraph 编排器 (LangGraph 0.6.6)
- ✅ PostgreSQL Checkpoint 持久化
- ✅ HITL 人机交互 (P1, P2.5 审批点)
- ✅ SSE 流式输出
- ✅ RESTful API (6个端点)

**运行集成测试**:

```bash
# 启动数据库 (Docker Compose)
docker-compose up -d postgres

# 运行所有集成测试
.venv/bin/pytest tests/integration/ -v

# 运行特定测试
.venv/bin/pytest tests/integration/test_hitl_workflow.py -v
.venv/bin/pytest tests/api/test_workflows.py -v
```

**已知限制** (Story 1.5.5):

- User表迁移假设已存在（需手动创建或通过其他Story）
- P2.5审批点端到端测试覆盖不完整
- 并发resume操作缺少防护机制（计划Story 1.5.6处理）

**API使用示例**:

```python
# 创建工作流
POST /api/v1/workflows
{
  "problem_description": "优化配送路线",
  "domain": "logistics",
  "constraints": ["时间窗口", "车辆容量"]
}

# 恢复工作流（P1审批）
POST /api/v1/workflows/{id}/resume
{
  "decision": "approved",
  "feedback": "算法选择合理"
}

# 流式监控
GET /api/v1/workflows/{id}/stream
```

### 相关Story

- **Story 1.1**: PostgreSQL + Redis基础设施 ✅
- **Story 1.2**: FastAPI + LangGraph后端初始化 ✅
- **Story 1.3**: Agent系统架构设计 ✅
- **Story 1.4**: 模型适配器实现 ✅
- **Story 1.5.0-1.5.4**: 工作流系统实现 ✅
- **Story 1.5.5**: 工作流系统集成验证 ✅

---

# FastAPI LangGraph Agent Template (原模板文档)

A production-ready FastAPI template for building AI agent applications with LangGraph integration. This template provides a robust foundation for building scalable, secure, and maintainable AI agent services.

## 🌟 Features

- **Production-Ready Architecture**
  - FastAPI for high-performance async API endpoints
  - LangGraph integration for AI agent workflows
  - Langfuse for LLM observability and monitoring
  - Structured logging with environment-specific formatting
  - Rate limiting with configurable rules
  - PostgreSQL for data persistence
  - Docker and Docker Compose support
  - Prometheus metrics and Grafana dashboards for monitoring

- **Security**
  - JWT-based authentication
  - Session management
  - Input sanitization
  - CORS configuration
  - Rate limiting protection

- **Developer Experience**
  - Environment-specific configuration
  - Comprehensive logging system
  - Clear project structure
  - Type hints throughout
  - Easy local development setup

- **Model Evaluation Framework**
  - Automated metric-based evaluation of model outputs
  - Integration with Langfuse for trace analysis
  - Detailed JSON reports with success/failure metrics
  - Interactive command-line interface
  - Customizable evaluation metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL ([see Database setup](#database-setup))
- Docker and Docker Compose (optional)

### Environment Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:

```bash
uv sync
```

3. Copy the example environment file:

```bash
cp .env.example .env.[development|staging|production] # e.g. .env.development
```

4. Update the `.env` file with your configuration (see `.env.example` for reference)

### Database setup

1. Create a PostgreSQL database (e.g Supabase or local PostgreSQL)
2. Update the database connection settings in your `.env` file:

```bash
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=cool_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

- You don't have to create the tables manually, the ORM will handle that for you.But if you faced any issues,please run the `schemas.sql` file to create the tables manually.

### Running the Application

#### Local Development

1. Install dependencies:

```bash
uv sync
```

2. Run the application:

```bash
make [dev|staging|production] # e.g. make dev
```

1. Go to Swagger UI:

```bash
http://localhost:8000/docs
```

#### Using Docker

1. Build and run with Docker Compose:

```bash
make docker-build-env ENV=[development|staging|production] # e.g. make docker-build-env ENV=development
make docker-run-env ENV=[development|staging|production] # e.g. make docker-run-env ENV=development
```

2. Access the monitoring stack:

```bash
# Prometheus metrics
http://localhost:9090

# Grafana dashboards
http://localhost:3000
Default credentials:
- Username: admin
- Password: admin
```

The Docker setup includes:

- FastAPI application
- PostgreSQL database
- Prometheus for metrics collection
- Grafana for metrics visualization
- Pre-configured dashboards for:
  - API performance metrics
  - Rate limiting statistics
  - Database performance
  - System resource usage

## 📊 Model Evaluation

The project includes a robust evaluation framework for measuring and tracking model performance over time. The evaluator automatically fetches traces from Langfuse, applies evaluation metrics, and generates detailed reports.

### Running Evaluations

You can run evaluations with different options using the provided Makefile commands:

```bash
# Interactive mode with step-by-step prompts
make eval [ENV=development|staging|production]

# Quick mode with default settings (no prompts)
make eval-quick [ENV=development|staging|production]

# Evaluation without report generation
make eval-no-report [ENV=development|staging|production]
```

### Evaluation Features

- **Interactive CLI**: User-friendly interface with colored output and progress bars
- **Flexible Configuration**: Set default values or customize at runtime
- **Detailed Reports**: JSON reports with comprehensive metrics including:
  - Overall success rate
  - Metric-specific performance
  - Duration and timing information
  - Trace-level success/failure details

### Customizing Metrics

Evaluation metrics are defined in `evals/metrics/prompts/` as markdown files:

1. Create a new markdown file (e.g., `my_metric.md`) in the prompts directory
2. Define the evaluation criteria and scoring logic
3. The evaluator will automatically discover and apply your new metric

### Viewing Reports

Reports are automatically generated in the `evals/reports/` directory with timestamps in the filename:

```
evals/reports/evaluation_report_YYYYMMDD_HHMMSS.json
```

Each report includes:

- High-level statistics (total trace count, success rate, etc.)
- Per-metric performance metrics
- Detailed trace-level information for debugging

## 🔧 Configuration

The application uses a flexible configuration system with environment-specific settings:

- `.env.development`
-
