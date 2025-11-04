# 6. Components

## 6.1 核心组件列表

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
