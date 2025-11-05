# Introduction

本文档概述了BMAD-METHOD LangGraph集成方案的完整全栈架构，包括后端系统、前端实现及其集成方式。它是AI驱动开发的唯一真实来源，确保整个技术栈的一致性。

这种统一的方法结合了传统上分离的后端和前端架构文档，简化了现代全栈应用的开发流程，因为这些关注点日益交织在一起。

## Starter Template or Existing Project

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

## Change Log

| Date       | Version | Description                            | Author              |
| ---------- | ------- | -------------------------------------- | ------------------- |
| 2025-11-05 | v1.0    | 基于PRD v1.2和实际项目创建初始架构文档 | Winston (Architect) |

---
