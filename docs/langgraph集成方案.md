# LangGraph集成方案产品需求文档 (PRD)

**项目名称**: BMAD-METHOD LangGraph集成方案
**PRD版本**: v1.2
**创建日期**: 2025-11-04
**产品负责人**: John (PM)
**技术基础**: LangGraph 0.4.1 生产级版本（已完成）

---

## 📋 执行摘要

本文档基于现有的成熟技术方案，定义BMAD-METHOD与LangGraph 0.4.1集成的完整产品需求。方案采用分阶��实施策略，80%场景通过2-3周的Phase 1即可解决核心痛点，避免大规模投入风险。

**核心价值主张**：

- ✅ 支持国产大模型（Qwen、GLM、DeepSeek）的即插即用
- ✅ 基于LangGraph 0.4.1的生产级checkpoint持久化特性
- ✅ 通过YAML配置将智能体开发效率提升3-5倍
- ✅ 渐进式投入，每阶段都有决策点和退出机制

---

## 🎯 目标和背景上下文

### 目标

- **Phase 1**：实现BMAD-METHOD与LangGraph 0.4.1的轻量级集成，包括前后端项目基础设施搭建和国产模型（Qwen/GLM/DeepSeek）的即插即用，2-3周内快速见效
- **Phase 2**：在Phase 1验证ROI达标后，开发YAML到Python的编译器POC，验证智能体批量开发的可行性，4-6周完成POC验证
- **Phase 3**：仅在年开发智能体数量≥30个的明确需求下，构建完整的BMAD DSL编译器和自研LangGraph框架，18-26周实现企业级智能体工厂
- **Phase 4**：基于LangGraph 0.4.1的人机协作特性，优化智能体工作流中的人工确认和决策机制

### 背景上下文

BMAD-METHOD已经发展到V4.4.1版本，具备了完整的八大智能体协作系统（新增代码实现专家）。当前的核心痛点是：

1. **国产模型支持需求迫切** - 需要支持通义千问、智谱GLM、DeepSeek等国产大模型
2. **开发效率有待提升** - 传统手写Python方式开发智能体需要2-3天，希望通过YAML配置方式缩短到4-6小时
3. **批量生产能力不足** - 面对年开发30+智能体的场景，需要标准化的生产流程

本方案采用**分阶段实施**的明智策略：

- **80%的场景**只需要Phase 1（2-3周）即可满足需求
- **15%的场景**可能需要Phase 1+2（7-10周）
- **仅5%的超大规模场景**才需要完整的Phase 1+2+3（25-30周）

### 变更日志

| 日期       | 版本 | 描述                                                                                               | 作者      |
| ---------- | ---- | -------------------------------------------------------------------------------------------------- | --------- |
| 2025-11-04 | v1.0 | 基于LangGraph 0.4.1和现有V4.4.1架构创建PRD                                                         | John (PM) |
| 2025-11-05 | v1.1 | Epic 1新增Story 1.2/1.3（前后端项目初始化），原Story 1.2-1.6重新编号为1.4-1.8，时间估算调整为3-4周 | John (PM) |
| 2025-11-05 | v1.2 | 根据实际完成的backend和frontend项目更新技术栈说明，修正版本号和依赖配置                            | John (PM) |

---

## 📋 需求分析

### 功能需求

**FR1**: 国产模型适配器支持

- 支持通义千问Qwen2.5系列（0.5B-110B）的API调用
- 支持智谱GLM-4.5系列（9B-355B）的API调用
- 支持DeepSeek R1系列（7B-671B）的API调用
- 提供统一的模型适配接口，支持模型热切换
- 支持本地部署（vLLM/Ollama）和云端API两种模式

**FR1.5**: 基础项目架构搭建

- 基于production-ready模板搭建FastAPI后端项目结构
- 基于enterprise-ready模板搭建Vue 3 + TypeScript前端项目结构
- 配置开发环境和构建工具链（Vite、ESLint、Prettier等）
- 实现基础的健康检查和监控端点
- 配置Docker容器化开发环境
- 提供完整的开发文档和启动脚本

**FR2**: LangGraph 0.4.1工作流编排

- 实现八大智能体的StateGraph编排（Orchestrator、Algorithm、Constraint、Objective、Domain、Code Implementation、Extension、Quality）
- 支持Phase 0-4的完整工作流状态管理
- 支持条件路由和并行执行
- 实现Human-in-Loop机制（interrupt/continue）
- 提供工作流持久化和恢复能力

**FR3**: LangServe API自动生成

- 一行代码自动生成RESTful API端点（/invoke、/stream、/batch、/stream_events等）
- 内置Server-Sent Events流式传输支持
- 自动生成OpenAPI文档和Playground测试UI
- 支持JWT Token认证和权限控制
- 提供健康检查和监控端点

**FR4**: 前端集成支持

- 提供React/Vue的SSE流式接收Hook示例
- 实现实时工作流状态展示组件
- 支持工作流执行过程的可视化监控
- 提供人工确认界面（Human-in-Loop交互）

**FR5**: 分阶段实施支持

- Phase 1：轻量级模型适配器（2-3周实现）
- Phase 2：YAML到Python编译器POC（4-6周实现）
- Phase 3：完整BMAD DSL编译器框架（18-26周实现）
- 提供各阶段的独立部署和验证能力

**FR6**: 代码实现专家支持

- 支持十要素建模验证
- 提供代码生成和追溯能力
- 实现Phase 3.5的专项代码生成工作流
- 集成代码质量保证机制

**FR7**: Human-in-the-Loop优化

- 实现P1触发点（��法推荐确认）
- 实现P2触发点（冲突仲裁）
- 实现P2.5触发点（代码质量确认）
- 提供直观的人工确认界面

### 非功能需求

**NFR1**: 性能要求

- 单个智能体响应时间 < 10秒（国产模型调用）
- 工作流完整执行时间 < 60分钟（标准APS流程）
- 支持并发用户数 ≥ 10个
- API响应时间 < 2秒（非模型调用）

**NFR2**: 可靠性要求

- 系统可用性 ≥ 99.5%
- 工作流执行成功率 ≥ 95%
- 支持工作流失败重试和断点续传
- 数据持久化一致性保证

**NFR3**: 扩展性要求

- 支持水平扩展（多实例部署）
- 支持新智能体的热插拔配置
- 模型服务支持负载均衡
- 支持工作流模板的动态加载

**NFR4**: 安全性要求

- API访问支持JWT认证
- 支持RBAC权限控制
- 数据传输加密（HTTPS）
- 敏感配置信息加密存储

**NFR5**: 可维护性要求

- 提供完整的日志记录和审计功能
- 支持工作流执行的监控和告警
- 提供健康检查端点
- 支持配置热更新

**NFR6**: 兼容性要求

- 兼容现有BMAD-METHOD V4.4.1架构
- 支持Docker容器化部署
- 兼容主流国产模型API格式
- 向后兼容现有智能体配置

**NFR7**: 开发效率要求

- Phase 1：新智能体开发时间从2-3天缩短到1天内
- Phase 2：通过YAML配置，开发时间缩短到4-6小时
- 提供开箱即用的开发环境（Docker Compose）
- 提供完整的开发者文档和示例

---

## 🎨 用户界面设计目标

### 整体UX愿景

为用户提供直观的智能体工作流交互界面，实时展示LangGraph工作流中各智能体的执行状态、输出结果和协作过程，让复杂的AI工作流变得透明、可控、易于理解。

### 关键交互模式

1. **工作流实时监控模式**：用户可以实时观察智能体协作过程，看到每个智能体的输入输出
2. **人工确认交互模式**：在Human-in-Loop场景下，用户能够清晰理解当前状态并做出决策
3. **智能体对话模式**：用户可以与特定智能体进行直接交互，提供反馈或调整方向
4. **历史回溯模式**：用户可以查看完整的工作流执行历史和决策轨迹

### 核心界面和视图

**实时工作流监控面板**

- 可视化工作流拓扑图，显示当前执行节点
- 实时流式显示各智能体的输出内容
- 执行进度条和时间估算
- 智能体间的数据流转可视化

**智能体交互界面**

- 当前活跃智能体的详细信息展示
- 智能体输出的格式化显示（支持代码、图表、文本）
- 用户反馈输入界面（支持文本、文件上传等）
- 历史对话记录和上下文展示

**人工确认决策界面**

- 中断点上下文信息展示
- 待确认方案的结构化呈现
- 决策选项和影响分析
- 反馈意见收集和处理

**工作流历史查看器**

- 完整执行历史的 timeline 视图
- 关键决策点的回溯和复盘
- 各智能体性能统计和分析
- 执行结果的导出和分享

### 可访问性要求：WCAG AA

- 确保所有交互元素支持键盘导航和屏幕阅读器
- 实时流式内容提供适当的暂停和恢复控制
- 提供高对比度主题和字体大小调节
- 复杂数据可视化提供文本替代方案

### 品牌风格

延续BMAD-METHOD的技术专业风格：

- 清晰的信息架构和数据可视化
- 深色/浅色主题切换（适应长时间使用）
- 突出智能体个性和角色差异
- 强调实时性和动态效果

### 目标设备和平台：Web响应式

**主要**：桌面浏览器（开发者、专业用户）
**次要**：平板设备（移动办公、会议展示）
**最小**：移动设备（紧急确认、状态查看）

---

## 🏗️ 技术假设和架构决策

### 仓库结构：Monorepo

采用单一的Monorepo结构，将LangGraph集成作为BMAD-METHOD项目的一部分管理。

**实际项目结构**（已完成）：

```
BMAD-METHOD/
├── backend/                    # FastAPI + LangGraph后端服务
│   ├── app/                   # FastAPI应用代码
│   ├── model_adapters/        # 模型适配器（待实现）
│   ├── shared/                # 共享代码（待实现）
│   ├── tests/                 # 测试代码
│   ├── pyproject.toml         # Python依赖配置
│   └── docker-compose.yml     # 本地开发环境
├── frontend/web/              # Vue 3前端应用
│   ├── src/                   # Vue应用代码
│   ├── public/                # 静态资源
│   └── package.json           # Node依赖配置
└── docs/                      # 项目文档
```

### 服务架构：微服务架构

采用基于FastAPI的微服务架构，遵循"轻适配器"的简化原则：

**Phase 1架构**（已实现）：

- **后端服务**：FastAPI + LangGraph 0.4.1（基于production-ready模板）
- **前端应用**：Vue 3 + TypeScript + Ant Design Vue
- **数据持久化**：PostgreSQL (checkpoint) + Redis (session/cache)
- **监控可观测性**：Langfuse (LLM追踪) + Prometheus + Grafana
- **国产模型适配**：轻量级适配层（待实现）

### 测试要求：Unit + Integration + E2E

**单元测试**：每个智能体节点的独立测试
**集成测试**：LangGraph工作流的端到端测试
**E2E测试**：完整用户场景的自动化测试

### 实际技术栈和依赖版本

**后端技术栈**（基于backend/pyproject.toml）：

```toml
# 核心框架
Python = ">=3.13"
FastAPI = ">=0.115.12"

# LangGraph生态
langgraph = ">=0.4.1"
langchain = ">=0.3.25"
langchain-core = ">=0.3.58"
langchain-openai = ">=0.3.16"
langchain-community = ">=0.3.20"
langgraph-checkpoint-postgres = ">=2.0.19"

# 认证和安全
passlib[bcrypt] = ">=1.7.4"
python-jose[cryptography] = ">=3.4.0"
bcrypt = ">=4.3.0"
slowapi = ">=0.1.9"           # API限流

# 数据库
SQLModel = ">=0.0.24"
psycopg2-binary = ">=2.9.10"
supabase = ">=2.15.0"

# 可观测性和监控
langfuse = "3.0.3"             # LLM追踪
structlog = ">=25.2.0"         # 结构化日志
prometheus-client = ">=0.19.0"
starlette-prometheus = ">=0.7.0"

# Web服务器
uvicorn = ">=0.34.0"

# 其他依赖
pydantic[email] = ">=2.11.1"
pydantic-settings = ">=2.8.1"
python-dotenv = ">=1.1.0"
python-multipart = ">=0.0.20"
email-validator = ">=2.2.0"
asgiref = ">=3.8.1"

# 工具库
duckduckgo-search = ">=3.9.0"
tqdm = ">=4.67.1"
colorama = ">=0.4.6"
```

**前端技术栈**（基于frontend/web/package.json）：

```json
{
  "dependencies": {
    "vue": "^3.5.22",
    "ant-design-vue": "^4.2.6",
    "vue-router": "^4.6.3",
    "pinia": "^2.3.1",
    "axios": "^1.13.2",
    "@vueuse/core": "^14.0.0",
    "dayjs": "^1.11.19"
  },
  "devDependencies": {
    "typescript": "~5.9.3",
    "vite": "^7.1.7",
    "@vitejs/plugin-vue": "^6.0.1",
    "vue-tsc": "^3.1.0",
    "eslint": "^9.39.1",
    "prettier": "^3.6.2",
    "sass": "^1.93.3"
  }
}
```

### LangGraph 0.4.1关键特性

**1. 持久化状态（Durable State）**

- 智能体执行状态自动持久化
- 服务器重启或工作流中断后自动恢复
- 支持跨多天的审批流程和后台作业

**2. 内置持久化（Built-in Persistence）**

- 无需编写自定义数据库逻辑
- 支持工作流的任意点保存和恢复
- 完美支持多会话工作流

**3. 人机协作模式（Human-in-the-Loop）**

- 一等API支持暂停执行等待人工审核
- 支持修改和批准功能
- 让人类在高风险决策中保持控制

**4. 图形化执行模型**

- 为复杂工作流提供精细控制
- 支持条件分支和并行执行
- 更好的错误处理和恢复机制

### 开发环境管理

**环境管理方案**：conda + uv

```bash
# Python环境
Python版本: 3.13.2 (conda管理)
包管理器: uv (现代Python包管理器)
环境名称: bmad-langgraph

# Node.js环境
Node版本: 20.x+ (nvm管理)
包管理器: npm 10.x+

# 常用命令
conda activate bmad-langgraph    # 激活Python环境
source ~/.nvm/nvm.sh             # 激活nvm
nvm use 20                       # 切换Node版本
```

### 更新的分阶段实施策略

**Phase 1**：搭建基础设施并实现轻量级集成（✅ 部分完成）

- ✅ **Story 1.1**: PostgreSQL + Redis基础设施搭建完成
- ✅ **Story 1.2**: 基于production-ready模板初始化后端项目完成
- ✅ **Story 1.3**: 从零搭建高质量Vue 3前端项目完成
- 🔄 **Story 1.4**: 国产模型适配器开发中
- ⏳ **Story 1.5-1.8**: 待开始

**技术成果**：

- 后端：FastAPI + LangGraph 0.4.1，集成Langfuse、Prometheus、Grafana监控
- 前端：Vue 3.5 + TypeScript + Ant Design Vue 4.2
- 数据层：PostgreSQL (checkpoint) + Redis (session/cache)
- 开发环境：conda + uv (Python 3.13.2) + nvm (Node 20.x)

**Phase 2**：YAML编译器POC开发

- 利用LangGraph 0.4.1的稳定API进行YAML编译
- 使用内置的checkpoint机制替代自定义持久化
- 简化Phase 3.5的代码实现专家集成

**Phase 3**：完整智能体工厂建设

- 利用1.0的人机协作模式优化工作流
- 使用内置持久化简化架构
- 降低自研组件的复杂性

### 额外技术假设和约束

**国产模型服务假设**：

- 已部署vLLM或Ollama服务，提供标准OpenAI兼容API
- 支持Qwen、GLM、DeepSeek等主流国产模型
- 模型推理性能满足业务需求（响应时间<10秒）

**部署环境约束**（基于实际项目配置）：

- **Python环境**：3.13.2 (conda管理)，pyproject.toml要求>=3.13
- **Node.js环境**：20.x+ (nvm管理)，package.json要求>=20
- **包管理器**：uv (Python)，npm 10.x+ (Node.js)
- **Docker容器化**：支持多阶段构建和镜像优化（已配置）
- **数据库**：PostgreSQL 16+，Redis 7+
- **监控可观测性**：Langfuse（LLM追踪）、Grafana 10.0+（监控可视化）、Prometheus 2.48+（指标收集）
- **安全和限流**：JWT认证、slowapi 0.1.9+（API限流保护）

**分阶段技术约束**：

- **Phase 1**：
  - Story 1.2：基于production-ready模板快速搭建后端（6-8小时 vs 3-5天），获得生产级监控和安全特性
  - Story 1.3：从零搭建前端（30小时），确保代码质量和团队掌控力
  - 最小化架构变更，聚焦模型适配和LangServe集成
- **Phase 2**：引入YAML编译器，保持向后兼容
- **Phase 3**：可选的完整重写，保留双引擎方案

---

## 🧠 智能体与专家库架构设计

### 核心设计理念

BMAD-METHOD的智能体系统基于**知识驱动**的理念，每个智能体不仅是一个LLM代理，更是一个知识载体。智能体通过加载专家库获得专业能力，并通过@引用机制确保输出的可追溯性和可验证性。

**核心原则**：

1. **Agent as Doc** - 智能体是知识的载体而非替代者
2. **知识索引化** - 专家库README.md是知识目录，不是知识本身
3. **按需动态加载** - 根据问题特征智能加载具体知识文件
4. **强制引用约束** - 所有输出必须附@引用路径，禁止未经引用的推断
5. **两阶段推理** - 分析问题→加载知识→生成方案

### 专家库结构设计

**专家库组织**（参考bmad/aps/templates/）：

```
knowledge_base/aps/
├── README.md                          # 专家库总索引
├── algorithm-library/                 # 算法专家库
│   ├── README.md                      # 算法索引（决策矩阵）
│   ├── greedy/                        # 贪心算法知识
│   ├── heuristic/                     # 启发式算法知识
│   ├── exact/                         # 精确算法知识
│   └── specialized/                   # 领域特定算法
├── constraint-library/                # 约束专家库
│   ├── README.md                      # 约束索引
│   ├── temporal/                      # 时间约束知识
│   ├── capacity/                      # 容量约束知识
│   └── spatial/                       # 空间约束知识
├── objective-library/                 # 目标专家库
├── domain-library/                    # 领域专家库
├── code-implementation-library/       # 代码实现专家库
├── quality-library/                   # 质量专家库
└── orchestrator-library/              # 编排专家库
```

**README.md的双重作用**：

1. **知识索引/目录** - 列出专家库包含的所有知识文件和路径
2. **决策矩阵** - 提供决策表，指导何时加载哪些知识文件

**示例**（algorithm-library/README.md）：

```markdown
# 算法专家知识库

## 知识库结构

[列出所有知识文件的目录树]

## 算法分类矩阵（决策表）

| 规模 | 决策变量数 | 推荐算法 | 引用路径                                    |
| ---- | ---------- | -------- | ------------------------------------------- |
| 小   | 20-100     | 精确算法 | @专家库/算法库/exact/dynamic-programming.md |
| 中   | 100-1000   | 启发式   | @专家库/算法库/heuristic/\*                 |
| 大   | 1000+      | 元启发式 | @专家库/算法库/specialized/\*               |
```

### 智能体工作流程

**原有bmad-method的工作机制**：

```
步骤1: 智能体启动
  └─> 加载 README.md (知识索引/决策矩阵) 到永久上下文
      └─> "我知道自己有哪些知识技能，以及在什么情况下使用"

步骤2: 接收任务
  └─> 智能体分析问题特征（规模、目标、约束）

步骤3: 查询索引
  └─> 在README的决策矩阵中查找
      例如：规模=1000变量 → 查表 → 推荐"元启发式"
           → 找到路径: @专家库/算法库/heuristic/遗传算法.md

步骤4: 动态加载
  └─> 加载具体知识文件（遗传算法.md）
      └─> 获取详细的算法原理、伪代码、实现模板

步骤5: 使用知识推理
  └─> 基于加载的详细知识生成方案

步骤6: 输出附引用
  └─> "推荐使用遗传算法 @专家库/算法库/heuristic/遗传算法.md"
```

### LangGraph实现方案：两阶段提示词链

**为什么选择两阶段提示词方案**：

- ✅ **稳定性最高** - 不依赖function calling（国产模型工具调用不稳定）
- ✅ **完全可控** - 系统精确控制知识加载过程
- ✅ **保持原理** - 完美还原原有bmad-method的工作机制
- ⚠️ **成本稍高** - 需要两次LLM调用（但可靠性优先）

**技术实现**：

```python
async def agent_expert_node(state: WorkflowState) -> Dict[str, Any]:
    """
    智能体节点 - 两阶段动态加载版本

    Stage 1: 分析问题，确定需要加载的知识文件
    Stage 2: 基于加载的知识生成最终方案
    """

    # ============================================
    # Stage 1: 分析阶段
    # ============================================

    # 1. 加载知识库索引（README.md）
    knowledge_index = load_knowledge_index('algorithm')

    # 2. 构建第一阶段提示词
    stage1_prompt = f"""
你是算法专家。

## 你的知识库索引（已加载）：
{knowledge_index}

## 你的任务：
1. 分析问题特征（规模、目标、约束、时间限制）
2. 在知识库索引的决策矩阵中查找合适的算法
3. 输出需要加载的知识文件路径列表

## 输出格式（JSON）：
{{
  "problem_analysis": {{
    "scale": "small|medium|large",
    "objective_type": "...",
    ...
  }},
  "required_knowledge": [
    "algorithm-library/exact/dynamic-programming.md",
    "algorithm-library/heuristic/遗传算法.md"
  ],
  "reasoning": "为什么需要这些文件"
}}
"""

    # 3. LLM调用（第一阶段）
    stage1_response = await llm.ainvoke(stage1_prompt + user_input)

    # 4. 解析需要加载的知识文件
    required_files = parse_required_knowledge(stage1_response.content)
    # 例如：["algorithm-library/heuristic/遗传算法.md"]

    # ============================================
    # Stage 2: 推理阶段
    # ============================================

    # 5. 动态加载知识文件
    loaded_knowledge = ""
    for file_path in required_files:
        knowledge_content = load_knowledge_file(file_path)
        loaded_knowledge += f"\n# @bmad/aps/templates/{file_path}\n{knowledge_content}\n"

    # 6. 构建第二阶段提示词
    stage2_prompt = f"""
你是算法专家。你已经加载了相关知识，现在基于这些知识提供推荐。

## 加载的专家知识：
{loaded_knowledge}

## 强约束策略：
1. **所有推荐必须基于上述加载的知识** - 不要编造
2. **必须使用@引用路径** - 格式：@bmad/aps/templates/xxx.md#section
3. **禁止未经引用的推断**

## 输出格式（JSON）：
{{
  "algorithm_recommendations": [
    {{
      "algorithm_name": "...",
      "rationale": "理由 @bmad/aps/templates/algorithm-library/xxx.md",
      ...
    }}
  ]
}}
"""

    # 7. LLM调用（第二阶段）
    stage2_response = await llm.ainvoke(stage2_prompt + user_input)

    # 8. 解析并返回最终结果（包含@引用）
    return parse_final_output(stage2_response.content)
```

### 与原有智能体的兼容性

**智能体配置迁移**：

原有智能体采用XML格式配置（bmad/aps/agents/orchestrator.md）：

```xml
<agent id="bmad/aps/agents/orchestrator.md">
  <persona>
    <role>系统编排者</role>
    <identity>...</identity>
    <principles>强制@引用约束</principles>
  </persona>
  <activation>
    <step n="4">加载 COMPLETE 文件 {project-root}/bmad/aps/templates/orchestrator-library/README.md 到永久上下文</step>
  </activation>
</agent>
```

**迁移策略**：

1. **提取persona信息** - 从XML中解析role、identity、principles
2. **保留专家库路径** - 从activation步骤中提取专家库路径
3. **转换为Python节点** - 使用两阶段提示词实现相同的加载机制
4. **保持@引用规范** - 在提示词中强制要求使用@引用

### 引用验证机制

**@引用格式规范**：

```
格式：@bmad/aps/templates/{library-name}/{file-path}#{section-id}

示例：
- @bmad/aps/templates/algorithm-library/heuristic/遗传算法.md
- @bmad/aps/templates/constraint-library/temporal/time-window.md#validation
```

**验证逻辑**（可选实现）：

```python
def validate_references(output: Dict, loaded_files: List[str]) -> bool:
    """验证输出中的@引用是否合法"""
    references = extract_references(output)
    for ref in references:
        file_path = parse_reference_path(ref)
        if file_path not in loaded_files:
            logger.warning(f"Invalid reference: {ref} (file not loaded)")
            return False
    return True
```

### 性能优化考虑

**两阶段调用的性能影响**：

- **额外延迟** - 约增加5-10秒（一次额外的LLM调用）
- **成本增加** - 约增加20-30% token消耗
- **可靠性提升** - 避免function calling失败，成功率从70%提升到95%+

**优化策略**（可选）：

1. **智能预加载** - 基于关键词预加载常用知识文件
2. **缓存机制** - 相似问题复用已加载的知识
3. **并行处理** - 多个智能体的Stage 1可以并行执行

### 实施路径

**Phase 1实施步骤**（Story 1.5）：

1. **复制专家库** - 将bmad/aps/templates/复制到backend/knowledge_base/aps/
2. **实现加载器** - 开发library_loader.py核心模块
3. **迁移Orchestrator** - 重构orchestrator_node.py使用两阶段加载
4. **迁移其他7个智能体** - 复用相同的模式
5. **集成测试** - 验证完整工作流和@引用机制

**技术债务管理**：

- **暂不实现引用验证** - Phase 1聚焦核心功能，引用验证留待Phase 2
- **暂不优化性能** - 先保证可靠性，性能优化在Phase 2按需实施
- **保持向后兼容** - 保留原有bmad/aps/目录，不影响现有系统

---

## 📚 史诗列表

### 史诗 1：Phase 1 - LangGraph 0.4.1轻量级集成

**目标**：搭建前后端项目基础设施，实现BMAD-METHOD与LangGraph 0.4.1的轻量级集成，重点支持国产模型，2-3周快速见效

**时间优化**（2025-11-05更新）：

- Story 1.2采用模板方案节省80%时间（3-5天 → 6-8小时）
- Story 1.3从零搭建优化开发效率（保持2天高质量交付）
- Epic 1总时间从3-4周优化到2-3周

这个史诗将建立完整的项目基础设施（后端FastAPI + 前端Vue 3），实现核心的模型适配能力，并为后续扩展奠定基础。包含从环境搭建、项目初始化到基础API端点实现的完整工作流，让团队能够立即使用国产模型并获得价值。

### 史诗 2：Phase 2 - YAML编译器POC开发

**目标**：开发YAML到Python代码的编译器概念验证，实现声明式智能体配置，4-6周验证ROI

这个史诗专注于提升开发效率，通过编译器技术让非技术用户也能通过YAML配置创建智能体。包含从YAML解析到代码生成的完整工具链，验证批量开发智能体的可行性。

### 史诗 3：Phase 3 - 完整BMAD DSL工厂

**目标**：构建完整的企业级智能体工厂，实现批量生产和管理，18-26周大规模部署

这个史诗仅在明确年开发30+智能体需求时实施，包含完整的DSL编译器、自研框架、以及企业级部署和管理功能。是最终的生产级解决方案。

### 史诗 4：Human-in-the-Loop工作流优化

**目标**：基于LangGraph 0.4.1的人机协作特性，优化智能体工作流中的人工确认和决策机制

这个史诗专门解决方案中的P1、P2、P2.5触发点问题，利用LangGraph 0.4.1的interrupt机制实现更流畅的人机协作体验。

---

## 📝 详细史诗和用户故事

### 史诗 1：Phase 1 - LangGraph 0.4.1轻量级集成

**史诗目标**：建立LangGraph 0.4.1与BMAD-METHOD的基础集成，实现国产模型支持和基础API服务，2-3周内提供可用价值

#### 故事 1.1：搭建LangGraph 0.4.1开发环境

**作为一个** BMAD开发者
**我希望** 能够快速搭建LangGraph 0.4.1开发环境
**以便于** 开始智能体集成开发工作

**验收标准**：

1. ✅ 创建完整的Python 3.13.2虚拟环境配置（conda + uv管理）
2. ✅ 安装LangGraph 0.4.1及核心依赖包（129个包）
3. ✅ 配置PostgreSQL 16和Redis 7的Docker Compose开发环境
4. ✅ 验证LangGraph 0.4.1基础功能正常工作
5. ✅ 提供环境验证脚本和开发文档

**实际完成情况**（2025-11-05）：

- Python 3.13.2 (conda环境: bmad-langgraph)
- LangGraph 0.4.1 + LangChain 0.3.25
- PostgreSQL: localhost:5432/bmad_langgraph_dev
- Redis: localhost:6379
- 开发环境一键启动脚本已完成

#### 故事 1.2：初始化FastAPI+LangGraph后端项目

**作为一个** BMAD开发者
**我希望** 基于production-ready模板快速搭建FastAPI+LangGraph后端项目结构
**以便于** 开始智能体服务开发并遵循行业最佳实践

**验收标准**：

1. ✅ 创建符合项目规范的后端目录结构（backend/app/）
2. ✅ 初始化FastAPI应用，包含基础配置和中间件（CORS、日志、限流）
3. ✅ 集成LangGraph 0.4.1并验证基础功能（StateGraph可用）
4. ✅ 实现健康检查和监控端点（/health, /metrics）
5. ✅ 配置开发环境和依赖管理（uv, pyproject.toml）
6. ✅ 提供完整的开发文档和启动脚本（README.md）

**实际完成情况**（2025-11-05）：

- 基于production-ready模板成功搭建
- FastAPI 0.115.12 + LangGraph 0.4.1
- 集成Langfuse 3.0.3 (LLM追踪)
- Prometheus + Grafana监控已配置
- JWT认证 + slowapi限流已实现
- Docker Compose开发环境已就绪
- 实际开发时间：约8小时（比原计划3-5天节省80%）

**实施方案**：**克隆模板 + 适配BMAD**（2025-11-05决策）

**采用模板**：[fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)

**核心优势**：

- ⏱️ 开发时间缩短80%（3-5天 → 6-8小时）
- 🏭 获得生产级监控和安全特性（Langfuse、Grafana、JWT、Rate Limiting）
- ✅ 1.5k stars，积极维护，MIT许可

**实际技术栈**（已完成）：

- Python 3.13.2（conda管理）
- FastAPI 0.115.12+
- LangGraph 0.4.1（实际版本）
- LangChain 0.3.25+
- langgraph-checkpoint-postgres 2.0.19+
- PostgreSQL 16+ (checkpoint后端)
- Redis 7+ (session/cache)
- structlog 25.2.0+ (结构化日志)
- Langfuse 3.0.3 (LLM可观测性)
- Prometheus + Grafana (监控可视化)
- slowapi 0.1.9+ (API限流)
- Docker Compose (容器化)

**实际开发时间**：约8小时（vs 原计划3-5天，节省80%）

#### 故事 1.3：初始化Vue 3 + TypeScript前端项目

**作为一个** BMAD开发者
**我希望** 从零开始搭建Vue 3 + TypeScript + Ant Design Vue前端项目
**以便于** 开始监控界面UI开发并完全掌控代码质量

**验收标准**：

1. ✅ 使用Vite 7.1创建Vue 3.5 + TypeScript 5.9项目
2. ✅ 集成Ant Design Vue 4.2 UI组件库
3. ✅ 配置Pinia 2.3状态管理和Vue Router 4.6路由
4. ✅ 实现基础布局和导航结构（MainLayout）
5. ✅ 配置开发环境和构建工具（ESLint, Prettier, Sass）
6. ✅ 提供完整的开发文档和启动脚本（README.md）

**实际完成情况**（2025-11-05）：

- 从零搭建完成，代码质量高
- Vue 3.5.22 + TypeScript 5.9.3
- Ant Design Vue 4.2.6
- 路由、状态管理、HTTP客户端全部配置完成
- 工具库：@vueuse/core 14.0, dayjs 1.11
- 开发工具链：Vite 7.1, vue-tsc, ESLint, Prettier
- 实际开发时间：约30小时（1.5-2天，高质量交付）

**实施方案**：**从零开始搭建**（2025-11-05决策）

**决策理由**（对比克隆模板方案）：

- ⏱️ **时间更优**：30小时 vs 模板适配47小时（快36%）
- ✨ **代码质量更高**：简洁、精准、无冗余代码
- 🎯 **完全贴合需求**：只实现需要的功能（Dashboard、WorkflowMonitor、Settings）
- 📚 **学习价值**：团队深入理解Vue 3生态，提升能力
- 🔒 **可维护性强**：完全掌控每一行代码，易于维护

**对比分析**：

- antdv-pro虽然功能丰富（827 stars），但包含大量不需要的企业级功能（多租户、复杂权限）
- 技术栈版本不完全匹配（Vue 3.3 vs 3.4，Vite 4 vs 5）
- 需要删除50%代码并学习他人架构，成本高于从零开始

**参考最佳实践**（不全盘克隆）：

- [antdv-pro](https://github.com/antdv-pro/antdv-pro) - 参考路由配置和布局设计
- Vue 3官方文档 - Composition API最佳实践
- Ant Design Vue官方文档 - 组件使用规范

**实际技术栈**（已完成）：

- Vue 3.5.22
- TypeScript 5.9.3
- Ant Design Vue 4.2.6
- Vite 7.1.7
- Pinia 2.3.1
- Vue Router 4.6.3
- Axios 1.13.2
- @vueuse/core 14.0.0
- dayjs 1.11.19

**实际开发时间**：约30小时（1.5-2天，高质量精简交付）

#### 故事 1.4：实现国产模型适配器

**作为一个** BMAD系统用户
**我希望** 能够使用国产大模型（Qwen/GLM/DeepSeek）替代OpenAI
**以便于** 满足数据本地化和成本控制需求

**验收标准**：

1. 实现统一的模型适配接口，支持多种国产模型
2. 支持vLLM和Ollama两种推理引擎
3. 实现模型热切换功能，无需重启服务
4. 提供模型健康检查和性能监控
5. 兼容现有BMAD工作流的调用方式

#### 故事 1.5：迁移八大智能体到LangGraph 0.4.1

**作为一个** BMAD开发者
**我希望** 将现有八大智能体迁移到LangGraph 0.4.1架构
**以便于** 利用新版本的持久化和人机协作特性

**验收标准**：

1. 使用新的langchain.agents API替代prebuilt模块
2. 实现Orchestrator到Code Implementation Expert的完整工作流
3. 配置LangGraph 0.4.1的checkpoint持久化机制
4. 验证Phase 0-4的完整工作流执行
5. 保持与现有workflow.yaml配置的兼容性

#### 故事 1.6：集成LangServe自动API生成

**作为一个** 前端开发者
**我希望** 通过LangServe自动生成RESTful API
**以便于** 快速集成智能体功能到前端界面

**验收标准**：

1. 配置LangServe 0.3.0+与LangGraph 0.4.1的集成
2. 自动生成/invoke、/stream、/stream_events等端点
3. 生成OpenAPI文档和Playground测试界面
4. 实现JWT认证和权限控制
5. 提供API使用示例和前端集成代码

#### 故事 1.7：实现SSE流式传输前端集成

**作为一个** 最终用户
**我希望** 能够实时看到智能体的工作过程和输出结果
**以便于** 理解AI的思考过程并及时调整

**验收标准**：

1. 实现React/Vue的SSE Hook组件
2. 实时显示智能体执行状态和进度
3. 支持工作流的可视化拓扑展示
4. 提供人工确认界面（interrupt机制）
5. 支持执行历史的回溯和复盘

#### 故事 1.8：Phase 1集成测试和验证

**作为一个** 项目经理
**我希望** 验证Phase 1是否解决了核心痛点
**以便于** 决定是否继续Phase 2的大规模投入

**验收标准**：

1. 完成端到端的功能测试
2. 验证国产模型的性能和稳定性
3. 评估用户体验和开发效率提升
4. 制定Phase 2-3的ROI评估报告
5. 提供明确的决策建议和下一步行动计划

### 史诗 2：Phase 2 - YAML编译器POC开发

**史诗目标**：开发YAML到Python代码的编译器概念验证，实现声明式智能体配置，验证开发效率提升3-5倍的假设，4-6周完成POC验证

#### 故事 2.1：设计YAML DSL规范

**作为一个** 系统架构师
**我希望** 定义清晰的YAML DSL语法规范
**以便于** 用户能够通过简单的配置描述复杂的智能体工作流

**验收标准**：

1. 定义智能体配置的YAML Schema（基于现有agents/\*.md格式）
2. 设计工作流编排的YAML语法（基于现有workflow.yaml格式）
3. 支持条件分支、并行执行、循环控制等流程控制
4. 定义@引用语法用于知识库依赖加载
5. 提供完整的YAML规范文档和示例

#### 故事 2.2：开发YAML解析器

**作为一个** 编译器开发者
**我希望** 能够解析YAML配置并生成抽象语法树（AST）
**以便于** 后续的代码生成处理

**验收标准**：

1. 实现YAML文件的解析和验证
2. 构建类型安全的AST数据结构
3. 支持YAML引用解析（$ref、@include等）
4. 实现语法错误检查和友好的错误提示
5. 提供AST可视化工具用于调试

#### 故事 2.3：开发Python代码生成器

**作为一个** 编译器开发者
**我希望** 能够将AST转换为可执行的Python LangGraph代码
**以便于** 用户无需手写复杂的Python代码

**验收标准**：

1. 实现AST到Python代码的模板化生成
2. 支持LangGraph 0.4.1的新API（langchain.agents）
3. 生成包含类型注解和文档的优质代码
4. 支持智能体节点、路由逻辑、状态管理的代码生成
5. 提供代码格式化和质量检查功能

#### 故事 2.4：实现基础@引用系统

**作为一个** 知识库管理员
**我希望** YAML配置能够引用外部的知识库和模板
**以便于** 实现知识的复用和模块化管理

**验收标准**：

1. 实现@template语法引用templates/目录下的知识库
2. 实现@agent语法引用agents/目录下的智能体配置
3. 支持相对路径和绝对路径的引用解析
4. 实现循环依赖检测和错误处理
5. 提供引用关系的可视化图表

#### 故事 2.5：POC演示和ROI验证

**作为一个** 项目决策者
**我希望** 看到完整的YAML到智能体的端到端演示
**以便于** 评估是否值得投入Phase 3的完整开发

**验收标准**：

1. 创建一个完整的YAML配置示例（至少3个智能体）
2. 演示从YAML到可执行代码的完整流程
3. 对比YAML方式vs手写Python的开发时间
4. 生成详细的ROI分析报告
5. 提供Phase 3继续开发的决策建议

### 史诗 3：Phase 3 - 完整BMAD DSL工厂

**史诗目标**：构建完整的企业级智能体工厂，实现批量生产和管理能力，仅在年开发30+智能体需求时实施，18-26周交付生产级解决方案

#### 故事 3.1：增强编译器核心引擎

**作为一个** 编译器架构师
**我希望** 拥有一个功能完整、性能优化的编译器核心
**以便于** 支持复杂的企业级智能体开发需求

**验收标准**：

1. 实现完整的YAML 1.2规范支持
2. 支持增量编译和缓存优化
3. 实现并行编译和依赖优化
4. 提供编译器插件机制
5. 性能：单个智能体编译时间<5秒

#### 故事 3.2：实现完整的@引用和依赖管理

**作为一个** 知识架构师
**我希望** 实现强大的知识库引用和依赖管理系统
**以便于** 支持复杂的企业知识复用和管理

**验收标准**：

1. 支持跨项目的知识库引用
2. 实现版本化的知识库管理
3. 支持语义化的依赖解析
4. 提供���识库的权限控制
5. 实现知识库的影响分析

#### 故事 3.3：开发BMAD Executor执行引擎

**作为一个** 系统架构师
**我希望** 拥有一个高性能的智能体执行引擎
**以便于** 支持大规模并发的智能体运行

**验收标准**：

1. 实现轻量级的LangGraph包装器
2. 支持动态加载和卸载智能体
3. 实现资源池化和性能优化
4. 支持智能体的热更新
5. 性能：支持100+并发智能体执行

#### 故事 3.4：构建智能体工厂管理界面

**作为一个** 团队管理者
**我希望** 有一个可视化的智能体工厂管理界面
**以便于** 监控和管理大规模的智能体生产

**验收标准**：

1. 提供智能体的可视化设计器
2. 实现智能体版本管理和发布流程
3. 支持智能体的批量部署和更新
4. 提供生产运行监控和告警
5. 支持多租户和权限管理

### 史诗 4：Human-in-the-Loop工作流优化

**史诗目标**：基于LangGraph 0.4.1的人机协作特性，优化智能体工作流中的人工确认和决策机制，提供流畅的协作体验

#### 故事 4.1：实现P1触发点人工确认

**作为一个** 业务分析师
**我希望** 在工作流开始时能够确认算法推荐
**以便于** 确保后续的智能体工作朝着正确方向进行

**验收标准**：

1. 实现LangGraph 0.4.1的interrupt机制
2. 在Orchestrator节点后设置P1确认点
3. 提供算法推荐的结构化展示界面
4. 支持用户批准、修改或重新执行
5. 记录人工决策的理由和依据

#### 故事 4.2：实现P2触发点冲突仲裁

**作为一个** 项目决策者
**我希望** 在智能体意见冲突时能够进行仲裁
**以便于** 确保最终方案符合业务需求

**验收标准**：

1. 识别智能体输出冲突的自动检测
2. 提供冲突对比和差异分析界面
3. 支持人工选择、合并或重新生成
4. 记录仲裁决策的过程和理由
5. 提供决策影响的风险提示

#### 故事 4.3：实现P2.5代码质量确认

**作为一个** 技术负责人
**我希望** 在代码生成完成后能够进行质量审查
**以便于** 确保交付的代码符合组织标准

**验收标准**：

1. 在Code Implementation Expert完成后设置确认点
2. 提供代码质量评分和审查报告
3. 支持代码的逐行审查和修改
4. 集成十要素建模的验证结果
5. 记录质量确认的通过/拒绝决策

#### 故事 4.4：优化人工确认用户体验

**作为一个** 最终用户
**我希望** 人工确认过程尽可能简单直观
**以便于** 快速做出决策而不影响工作效率

**验收标准**：

1. 设计简洁直观的确认界面
2. 提供充分的上下文信息和决策支持
3. 支持快捷操作和批量确认
4. 实现移动设备友好的响应式设计
5. 提供确认历史和决策追溯功能

---

## 🎯 下一步行动

### UX专家提示

请将此PRD文档提供给UX专家，启动智能体交互界面的设计工作，重点关注：

- 实时工作流监控面板的可视化设计
- 人工确认界面的用户体验优化
- 智能体状态和输出的直观展示
- 移动端友好的响应式设计

### 架构师提示

请将此PRD文档提供给架构师，启动基于LangGraph 0.4.1的技术架构设计工作，重点关注：

- LangGraph 0.4.1与现有BMAD架构的集成方案
- 国产模型适配器的技术实现
- StateGraph工作流的具体设计
- 数据持久化和状态管理策略

### 项目实施建议

基于你现有的完整技术方案，强烈建议直接启动Phase 1的实施：

1. **立即可行**：所有技术组件都已成熟稳定
2. **风险可控**：2-3周的小规模投入
3. **价值明确**：立即获得国产模型支持能力
4. **可扩展**：为后续Phase奠定坚实基础

**核心建议**：不要被完整的20-24周方案吓到，80%场景通过Phase 1的2-3周投入就能解决核心痛点！

### 决策点规划

- **Week 2-3（Phase 1结束）**：决策点1 - Phase 1是否满足需求？
  - ✅ **是（80%场景）** → 停止并庆祝！2-3周解决核心问题
  - ❌ **否** → 评估是否继续Phase 2（需要年开发30+智能体）

- **Week 10（Phase 2结束）**：决策点2 - ROI是否达标？
  - ✅ **是** → 继续Phase 3（需明确大规模需求）
  - ❌ **否** → 停止，使用Phase 1方案

---

## 📊 成功指标

### Phase 1成功指标（2-3周交付）

**基础设施指标**：

- [ ] 后端FastAPI服务正常运行，健康检查端点可用
- [ ] 前端Vue应用正常运行，可访问监控界面
- [ ] 前后端通过Docker Compose可一键启动
- [ ] Langfuse LLM可观测性功能正常工作
- [ ] Grafana监控面板可访问，显示关键指标
- [ ] JWT认证和API限流功能正常工作

**功能指标**：

- [ ] 国产模型成功集成，支持Qwen/GLM/DeepSeek
- [ ] LangGraph 0.4.1工作流正常运行，兼容八大智能体
- [ ] API端点正常工作，前端可实时监控
- [ ] 用户可以人工确认关键决策点

**效率指标**：

- [ ] Story 1.2后端搭建时间：6-8小时（vs 原计划3-5天，节省80%）
- [ ] Story 1.3前端搭建时间：30小时（1.5-2天，高质量交付）
- [ ] Epic 1总交付时间：2-3周（vs 原计划3-4周，节省25%）
- [ ] 新智能体开发时间从2-3天缩短到1天内

### Phase 2成功指标

- [ ] YAML配置成功转换为可执行Python代码
- [ ] 开发时间从2-3天缩短到4-6小时
- [ ] 编译器稳定性达到95%以上
- [ ] ROI分析显示明确收益
- [ ] 决策层批准继续Phase 3投入

### Phase 3成功指标

- [ ] 年开发智能体数量≥30个
- [ ] 批量生产能力验证成功
- [ ] 企业级功能完整可用
- [ ] 投资回报在18-36个月内实现

---

**文档版本**: v1.2
**最后更新**: 2025-11-05
**状态**: ✅ Phase 1部分完成（Story 1.1-1.3已完成）

**维护者**: John (PM)
**审批人**: 待指定

**v1.2更新内容**（2025-11-05）：

- ✅ 修正LangGraph版本：1.0.2 → 0.4.1（与实际项目一致）
- ✅ 更新后端技术栈：基于实际pyproject.toml配置
- ✅ 更新前端技术栈：基于实际package.json配置
- ✅ 添加实际项目结构说明（backend/和frontend/web/）
- ✅ 更新Story 1.1-1.3的完成状态和实际技术细节
- ✅ 更新开发环境管理方案（conda + uv）
- ✅ 移除不适用的"重大变更影响"章节（langgraph.prebuilt弃用）

**v1.1更新内容**（2025-11-05）：

- Epic 1时间优化：3-4周 → 2-3周
- Story 1.2实施方案调整：克隆模板+适配（节省80%时间）
- Story 1.3实施方案调整：从零搭建（确保代码质量）
- 技术栈更新：Python 3.13+、Langfuse、Grafana、slowapi
- 成功指标细化：增加基础设施指标和效率指标
