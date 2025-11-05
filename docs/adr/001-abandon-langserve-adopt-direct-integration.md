# ADR-001: 放弃LangServe，采用FastAPI + LangGraph直接集成

## 状态

✅ **已接受** - 2025-11-05

## 上下文

在设计BMAD-METHOD项目的后端架构时，我们最初考虑使用LangServe作为LangChain/LangGraph应用的部署工具。但在2025年初的技术调研中发现：

1. **LangServe已进入维护模式**
   - LangChain官方宣布LangServe不再接受新功能
   - 官方推荐迁移到LangGraph Platform
   - 仅接受bug修复，不再积极开发

2. **行业最佳实践演变**
   - 2025年主流方案是FastAPI + LangGraph直接集成
   - 生产级模板（如fastapi-langgraph-agent-production-ready-template）证明了这种方案的可行性
   - 更简洁、更高效、更易于定制

3. **项目需求分析**
   - 需要高度定制化的API端点
   - 需要细粒度的权限控制和监控
   - 需要集成国产模型适配器
   - 需要与LangGraph 1.0的新特性（Human-in-the-Loop）深度集成

## 决策

**我们决定：**

- ❌ **不使用LangServe**
- ✅ **采用FastAPI + LangGraph直接集成**

**具体方案：**

1. 使用FastAPI 0.115.0+作为Web框架
2. 直接在FastAPI路由中调用LangGraph工作流
3. 手动实现所需的API端点（/invoke、/stream等）
4. 参考fastapi-langgraph-agent-production-ready-template的架构模式

## 架构对比

### 方案A：LangServe（已放弃）

```
Client → LangServe → LangChain/LangGraph
```

**优点：**

- 自动生成/invoke、/stream等标准端点
- 开箱即用的流式传输支持

**缺点：**

- ❌ 已停止新功能开发
- ❌ 定制化困难
- ❌ 增加了一层抽象，调试复杂
- ❌ 不适合复杂的业务逻辑集成

### 方案B：FastAPI + LangGraph直接集成（已选择）

```
Client → FastAPI → LangGraph StateGraph → Model Adapters
```

**优点：**

- ✅ 完全控制API行为
- ✅ 更简洁的架构
- ✅ 易于调试和测试
- ✅ 2025年行业最佳实践
- ✅ 官方推荐方向
- ✅ 更好的性能和可维护性

**缺点：**

- 需要手动实现一些端点逻辑（可接受，已有成熟模板参考）

## 影响

### 对Story 1.4的影响

- **移除**：LangServe相关的所有Task
- **保留**：FastAPI端点实现
- **调整**：API端点设计更加灵活

### 对项目架构的影响

1. **技术栈更新**
   - 移除：LangServe 0.3.0+
   - 保留：FastAPI 0.115.0+, Uvicorn 0.26.0+, sse-starlette 2.1.0
   - 新增：更精细的中间件控制

2. **项目结构调整**

   ```
   backend/
   ├── langgraph_service/
   │   ├── main.py              # FastAPI应用
   │   ├── api/                 # API路由（手动实现）
   │   │   ├── v1/
   │   │   │   ├── models.py    # 模型配置端点
   │   │   │   ├── workflows.py # 工作流端点
   │   │   │   └── agents.py    # 智能体端点
   │   ├── workflows/           # LangGraph工作流
   │   └── agents/              # 智能体实现
   ```

3. **开发效率影响**
   - 初始开发：需要手动实现更多端点逻辑
   - 长期维护：更清晰的代码结构，更易于维护
   - 总体评估：**长期收益大于短期成本**

## 参考资源

1. **官方文档**
   - [LangServe GitHub - 维护模式声明](https://github.com/langchain-ai/langserve)
   - [LangGraph Platform Migration Guide](https://langchain-ai.github.io/langgraph/cloud/)

2. **最佳实践模板**
   - [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)

3. **技术文章**
   - [Build AI Workflows with FastAPI & LangGraph | 2025 Guide](https://www.zestminds.com/blog/build-ai-workflows-fastapi-langgraph/)
   - [Deploying LangGraph with FastAPI](https://medium.com/@sajith_k/deploying-langgraph-with-fastapi-a-step-by-step-tutorial-b5b7cdc91385)

## 相关决策

- Story 1.2: 后端项目初始化
- Story 1.3: 前端项目初始化
- Story 1.4: 模型适配器实现

## 备注

此决策是在2025-11-05做出的，基于当时的技术状态和行业最佳实践。如果LangChain官方推出新的部署方案，我们应重新评估此决策。

---

**决策人**: John (Product Manager)
**日期**: 2025-11-05
**审核人**: 开发团队（待审核）
