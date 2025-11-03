# BMAD-METHOD LangGraph 集成方案文档

本目录包含 BMAD-METHOD 智能体系统迁移到 LangGraph 框架的完整技术方案。

## 📚 文档索引

### 核心方案文档

| 文档                                                                                   | 说明                                                          | 状态    | 推荐度     |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ------- | ---------- |
| **[v4.0-bmad-langgraph-integration/](./v4.0-bmad-langgraph-integration/)** 🆕          | **智能体工厂模式：BMAD DSL → 编译器 → LangGraph（批量开发）** | ✅ 最新 | ⭐⭐⭐⭐⭐ |
| **[langgraph-langserve-deployment.md](./langgraph-langserve-deployment.md)**           | **LangGraph + LangServe 快速部署方案（单个智能体）**          | ✅ 稳定 | ⭐⭐⭐⭐⭐ |
| [langgraph-private-deployment-research.md](./langgraph-private-deployment-research.md) | LangGraph + 国产模型私有化部署详细方案                        | ✅ 完成 | ⭐⭐⭐⭐   |
| [enterprise-web-deployment-research.md](./enterprise-web-deployment-research.md)       | 企业级 Web 部署调研（包含 MCP 等多方案对比）                  | ✅ 完成 | ⭐⭐⭐     |

---

## 🎯 快速开始

### 如果你只想看一份文档

👉 **直接阅读**: [langgraph-langserve-deployment.md](./langgraph-langserve-deployment.md)

这是最新、最简化的方案，包含：

- ✅ 完整的代码示例（可直接运行）
- ✅ Docker Compose 一键部署
- ✅ 前端集成示例（React/Vue）
- ✅ 认证、监控、测试完整方案

**核心优势**：

- 不需要自己实现 WebSocket（使用框架内置 SSE）
- 不需要手写 API 路由（LangServe 自动生成）
- 开发时间缩短 50-70%（从 4-6 周降至 1-2 周）

---

## 📖 文档详细说明

### 1. LangGraph + LangServe 快速部署方案（推荐）⭐⭐⭐⭐⭐

**文件**: `langgraph-langserve-deployment.md`

**适用场景**:

- ✅ 已完成国产模型部署
- ✅ 希望快速实现 Web API
- ✅ 不想从零开发 WebSocket
- ✅ 需要开箱即用的测试 UI

**核心内容**:

```python
# 一行代码完成 API 部署
from langserve import add_routes
add_routes(app, aps_workflow, path="/aps")

# 自动生成:
# POST /aps/invoke       - 同步调用
# POST /aps/stream       - 流式输出 (SSE)
# POST /aps/stream_events - 流式事件
# GET  /aps/playground   - 交互式测试 UI
```

**关键技术**:

- **LangServe**: 自动 API 生成框架
- **SSE (Server-Sent Events)**: 框架内置流式传输
- **LangGraph**: 智能体编排引擎
- **FastAPI**: Web 框架基础

**代码量**: ~500 行（完整实现）

**开发周期**: 1-2 周

---

### 2. LangGraph + 国产模型私有化部署方案 ⭐⭐⭐⭐

**文件**: `langgraph-private-deployment-research.md`

**适用场景**:

- ✅ 需要了解国产模型选型（Qwen/GLM/DeepSeek）
- ✅ 关注私有化部署成本分析
- ✅ 需要详细的硬件配置建议
- ✅ 想了解 vLLM/Ollama 推理引擎对比

**核心内容**:

1. **国产模型对比**
   - 通义千问 Qwen2.5 (0.5B-110B)
   - 智谱 GLM-4.5 (9B-355B)
   - DeepSeek R1 (7B-671B)
   - 性能对标、LangChain 集成、硬件需求

2. **私有化部署技术栈**
   - vLLM 生产级部署方案
   - Docker Compose 配置
   - K8s 集群部署
   - 性能优化配置

3. **成本分析**
   - 硬件成本估算（¥25,800 - ¥513,000）
   - 3 年 TCO 对比（私有化 vs 云 API）
   - ROI 分析（2-6 个月回本）

4. **BMAD 迁移方案**
   - 7 个专家智能体映射
   - 完整代码示例（TypeScript）
   - 前后端集成方案

**代码量**: ~2000 行（含详细注释）

**开发周期**: 3-4 个月（完整迁移）

---

### 3. 企业级 Web 部署调研（多方案对比）⭐⭐⭐

**文件**: `enterprise-web-deployment-research.md`

**适用场景**:

- ✅ 需要了解多种技术方案对比
- ✅ 关注 MCP (Model Context Protocol) 方案
- ✅ 想对比 LangGraph/LangChain/AutoGen 等框架
- ✅ 需要完整的技术调研报告

**核心内容**:

1. **多方案对比**
   - MCP (Model Context Protocol) + NestJS
   - LangGraph Platform 方案
   - 纯 Claude Agent SDK 方案
   - FastAPI + AutoGen 方案

2. **技术选型矩阵**
   - 开发难度、成本、扩展性对比
   - 适用场景分析
   - 推荐度评分

3. **实施路线图**
   - Phase 1-4 详细规划
   - 风险评估与缓解措施
   - 团队技能要求

**这是最早的调研文档**，如果你只想快速上手，可以跳过这份文档。

---

## 🔄 方案演进历程

```
V1.0 (enterprise-web-deployment-research.md)
├── 调研了 MCP、LangGraph、Claude SDK 等多种方案
├── 发现需要依赖 Claude API（不符合国产化要求）
└── 结论：需要支持国产模型的方案

    ↓

V2.0 (langgraph-private-deployment-research.md)
├── 深度调研国产模型（Qwen/GLM/DeepSeek）
├── 设计完整的私有化部署架构
├── 提供详细的成本分析和迁移路线
└── 发现：需要自己实现 WebSocket（复杂）

    ↓

V3.0 (langgraph-langserve-deployment.md) ⭐ 推荐单个智能体快速开发
├── 发现 LangServe 框架（自动 API 生成）
├── 使用 SSE 替代 WebSocket（更简单）
├── 开发时间缩短 50-70%
└── 适用场景：1-5个智能体的快速开发

    ↓

V4.0 (v4.0-bmad-langgraph-integration/) 🚀 NEW - 推荐批量开发
├── BMAD DSL → 编译器 → LangGraph
├── 智能体工厂模式（开发效率提升 3-5倍）
├── 声明式配置 + 自动代码生成
└── 适用场景：5+智能体的企业级批量开发
```

---

## 🚀 推荐实施路径

### 路径 A: 快速上手（推荐大多数场景）

```
1. 阅读 langgraph-langserve-deployment.md
   ↓
2. 按照文档中的"快速启动"章节操作
   ↓
3. 1 周内完成原型验证
   ↓
4. 2-3 周完成完整迁移
```

### 路径 B: 深度定制（企业级大规模部署）

```
1. 阅读 langgraph-private-deployment-research.md
   ↓
2. 评估硬件成本和国产模型选型
   ↓
3. 按照 16 周路线图逐步实施
   ↓
4. 根据需要参考 langgraph-langserve-deployment.md 简化部分流程
```

---

## 🛠️ 技术栈对比

| 组件           | V1.0 方案      | V2.0 方案          | V3.0 方案（单个智能体） | **V4.0 方案（批量开发）** 🆕    |
| -------------- | -------------- | ------------------ | ----------------------- | ------------------------------- |
| **开发方式**   | 手写Python     | 手写Python         | 手写Python              | **YAML配置** ✅                 |
| **智能体框架** | MCP/LangGraph  | LangGraph          | LangGraph               | **BMAD DSL + LangGraph** ✅     |
| **Web 框架**   | NestJS/FastAPI | FastAPI            | FastAPI + LangServe     | **FastAPI + LangServe** ✅      |
| **流式传输**   | 手写 WebSocket | 手写 WebSocket     | 框架内置 SSE            | **框架内置 SSE** ✅             |
| **API 路由**   | 手写路由       | 手写路由           | 自动生成                | **自动生成** ✅                 |
| **测试 UI**    | 需自己开发     | 需自己开发         | 内置 Playground         | **内置 Playground** ✅          |
| **大模型**     | Claude API     | 国产模型（私有化） | 国产模型（私有化）      | **国产模型（私有化）** ✅       |
| **开发周期**   | 4-6 周         | 3-4 个月           | 1-2 周                  | **初期 3-4月，后续 4-6h/个** ✅ |
| **代码量**     | ~2000 行       | ~2000 行           | ~500 行                 | **~100 行 YAML** ✅             |
| **开发效率**   | 1x             | 1x                 | 1x                      | **3-5x** ✅                     |
| **适用场景**   | 探索           | 1-2个              | 1-5个                   | **5+ 智能体** ✅                |

---

## 📞 快速咨询

### 常见问题

**Q: 我应该看哪份文档？**
A: 直接看 `langgraph-langserve-deployment.md`，这是最新、最简化的方案。

**Q: 我的模型已经部署好了，还需要做什么？**
A: 只需要：

1. 安装 LangGraph + LangServe（pip install）
2. 编写智能体工作流（~500 行代码）
3. 一行代码部署 API（add_routes）
4. Docker Compose 启动服务

**Q: 流式传输怎么实现？**
A: 不需要自己实现！LangServe 自动将 LangGraph 的 `.stream()` 转换为 SSE。前端用浏览器原生的 EventSource API 接收即可。

**Q: 需要 WebSocket 吗？**
A: 不需要！使用 SSE (Server-Sent Events) 更简单，浏览器原生支持。

**Q: 支持 Human-in-Loop 吗？**
A: 完全支持！LangGraph 的 `interrupt()` 机制可以暂停工作流等待用户确认。

**Q: 成本如何？**
A: 如果模型已部署，只需：

- 开发成本：1-2 周开发时间
- 运营成本：Postgres + Redis（~¥50/月）
- 零额外 API 调用费用

**Q: 如何快速验证可行性？**
A: 按照 `langgraph-langserve-deployment.md` 中的"快速启动"章节，1 天内可以搭建原型。

---

## 📝 贡献指南

如果你在实施过程中有新的发现或改进建议，欢迎：

1. 创建新的 Markdown 文档
2. 更新本 README.md 索引
3. 提交 PR 或反馈

---

## 🔗 相关资源

### 官方文档

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangServe 官方文档](https://python.langchain.com/docs/langserve/)
- [LangChain 中文文档](https://python.langchain.com.cn/)

### 社区资源

- [LangGraph 示例代码](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [LangServe 部署案例](https://github.com/langchain-ai/langserve/tree/main/examples)

### 国产模型

- [通义千问 Qwen 文档](https://qwen.readthedocs.io/)
- [智谱 AI GLM 文档](https://open.bigmodel.cn/)
- [DeepSeek 官方文档](https://platform.deepseek.com/docs)

---

## 📅 更新日志

- **2025-11-03 (晚)**: 🚀 新增 V4.0 智能体工厂方案
  - 创建 v4.0-bmad-langgraph-integration/ 子目录
  - 完成核心方案设计文档（README + 01-overview + 02-architecture）
  - 定位：批量开发智能体（5+ 个）的企业级方案
  - 核心特性：BMAD DSL → 编译器 → LangGraph，开发效率提升 3-5倍
  - 技术可行性：95%，开发周期：12-16周

- **2025-11-03 (早)**: 创建文档目录，整理三份调研报告
  - 新增 V3.0 方案（LangGraph + LangServe）
  - 确认推荐方案：langgraph-langserve-deployment.md（单个智能体快速开发）
  - 创建本索引文档

---

**维护者**: Claude Code AI Assistant
**最后更新**: 2025-11-03
**文档状态**: ✅ 活跃维护中
