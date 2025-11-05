# 3. Tech Stack

这是项目的**唯一技术真实来源**。所有开发必须使用这些确切的技术和版本。

| 类别             | 技术                 | 版本     | 用途                       | 选择理由                                                      |
| ---------------- | -------------------- | -------- | -------------------------- | ------------------------------------------------------------- |
| **后端语言**     | Python               | 3.13+    | 后端智能体服务开发         | 采用生产级模板要求；支持最新类型注解和性能优化；向下兼容3.11+ |
| **后端框架**     | FastAPI              | 0.115.0+ | RESTful API和LangServe集成 | 原生async支持；自动OpenAPI文档生成；与LangServe无缝集成       |
| **智能体编排**   | LangGraph            | 0.6.4    | 智能体工作流StateGraph编排 | 当前版本；计划Story 1.3.5升级到1.0.2获得新特性                |
| **智能体工具**   | LangChain Core       | 0.2.38+  | 智能体工具链和提示管理     | LangGraph核心依赖；提供agent创建工具                          |
| **智能体SDK**    | LangGraph SDK        | 0.2.0+   | LangGraph客户端和工具      | 官方SDK；支持远程调用和监控                                   |
| **Checkpoint**   | LangGraph Checkpoint | 2.0.23+  | 工作流状态持久化           | 内置checkpoint机制；自动状态保存和恢复                        |
| **API服务**      | LangServe            | 0.3.0+   | 自动API端点生成            | 一行代码生成/invoke、/stream等端点；SSE流式传输支持           |
| **HTTP服务器**   | Uvicorn              | 0.26.0+  | ASGI服务器                 | 高性能async服务器；FastAPI官方推荐                            |
| **流式传输**     | sse-starlette        | 2.1.0    | Server-Sent Events实现     | 与FastAPI集成；实时流式数据推送                               |
| **HTTP客户端**   | httpx                | 0.25.0+  | 异步HTTP请求               | 支持async/await；用于模型API调用                              |
| **前端语言**     | TypeScript           | 5.3+     | 前端类型安全开发           | 类型安全；与后端类型共享；减少运行时错误                      |
| **前端框架**     | Vue                  | 3.4+     | 监控界面UI开发             | 组合式API；TypeScript支持好；团队更熟悉；性能优秀             |
| **UI组件库**     | Ant Design Vue       | 4.1+     | 企业级UI组件               | 完整的Vue 3组件体系；中文文档友好；适合管理后台               |
| **状态管理**     | Pinia                | 2.1+     | Vue状态管理                | Vue 3官方推荐；TypeScript友好；轻量级；直观的API              |
| **路由**         | Vue Router           | 4.2+     | 前端路由管理               | Vue 3官方路由；支持TypeScript                                 |
| **API风格**      | REST + SSE           | -        | 前后端通信协议             | LangServe原生支持REST；SSE实现实时流式传输                    |
| **数据库**       | PostgreSQL           | 16+      | 工作流状态和数据持久化     | LangGraph checkpoint后端；ACID事务保证；JSON支持              |
| **缓存**         | Redis                | 7+       | 会话缓存和任务队列         | 高性能；支持发布订阅；持久化选项                              |
| **文件存储**     | 本地文件系统         | -        | 代码生成和知识库存储       | Phase 1简化方案；避免引入云存储依赖                           |
| **认证**         | JWT                  | -        | API访问认证                | 无状态；易于扩展；LangServe支持中间件集成                     |
| **前端测试**     | Vitest               | 1.0+     | Vue组件单元测试            | Vite生态原生集成；快速；Vue Test Utils支持                    |
| **后端测试**     | Pytest               | 7.4+     | Python单元和集成测试       | Python标准测试框架；丰富的插件生态                            |
| **E2E测试**      | Playwright           | 1.40+    | 端到端自动化测试           | 跨浏览器；录制功能；与TypeScript集成                          |
| **构建工具**     | Vite                 | 5.0+     | 前端构建和开发服务器       | Vue官方推荐；极快的HMR；原生ESM                               |
| **打包工具**     | Rollup               | -        | 前端生产构建               | Vite底层依赖；Tree-shaking优化                                |
| **IaC工具**      | Docker Compose       | 2.23+    | 本地和生产环境编排         | 简单易用；统一开发和部署环境                                  |
| **CI/CD**        | GitHub Actions       | -        | 持续集成和部署             | 与GitHub深度集成；免费额度充足；YAML配置                      |
| **监控**         | Prometheus           | 2.48+    | 指标收集和告警             | 开源标准；丰富的exporter生态                                  |
| **监控可视化**   | Grafana              | 10.0+    | 监控数据可视化和仪表板     | 与Prometheus完美集成；丰富的图表类型；模板化仪表板            |
| **LLM可观测性**  | Langfuse             | Latest   | LLM调用追踪和性能分析      | 专为LLM设计；追踪token使用和成本；调试工作流                  |
| **日志**         | structlog            | 24.1.0+  | 结构化日志                 | JSON格式；易于解析和查询；Python原生支持                      |
| **限流**         | slowapi              | 0.1.9+   | API请求速率限制            | 基于Flask-Limiter；简单易用；保护API免受滥用                  |
| **CSS框架**      | Tailwind CSS         | 3.4+     | 实用优先的CSS框架          | 快速开发；与Vue组件结合好；构建时优化                         |
| **Python包管理** | Conda                | Latest   | Python环境和依赖管理       | 宿主机已配置；科学计算包支持好                                |
| **Node包管理**   | npm                  | 10+      | Node.js依赖管理            | 标准工具；与nvm配合使用                                       |
| **序列化**       | orjson               | 3.9.7+   | 高性能JSON序列化           | 比标准库快；LangGraph推荐                                     |
| **重试机制**     | tenacity             | 8.0.0+   | 智能重试和容错             | 灵活的重试策略；装饰器语法简洁                                |
| **数据库连接**   | psycopg              | 3.2.0+   | PostgreSQL Python驱动      | 最新版本；连接池支持；async支持                               |
| **序列化工具**   | cloudpickle          | 3.0.0+   | Python对象序列化           | LangGraph checkpoint依赖；支持复杂对象                        |
| **数据验证**     | Pydantic             | 2.10.0+  | 数据模型和验证             | FastAPI核心依赖；类型安全；自动文档生成                       |
| **可观测性**     | LangSmith            | 0.1.63+  | LangGraph工作流追踪        | 官方可观测性工具；调试和性能分析                              |

## 版本历史

### v1.1 (2025-11-05) - Story 1.2实施方法变更

- **Python版本**: 3.11+ → 3.13+（基于生产级模板要求）
- **新增技术**:
  - Grafana 10.0+ - 监控数据可视化
  - Langfuse - LLM调用追踪和可观测性
  - slowapi 0.1.9+ - API限流保护
- **原因**: 采用[fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)，获得生产级监控和安全特性

---
