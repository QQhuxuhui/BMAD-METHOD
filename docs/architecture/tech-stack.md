# Tech Stack

这是整个项目的**权威技术选型表**，所有开发必须遵循这些确切的版本。以下技术栈基于Story 1.2/1.3实际完成的项目配置。

## Technology Stack Table

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
