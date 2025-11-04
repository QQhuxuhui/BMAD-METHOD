# 5. API Specification

完整的OpenAPI 3.0规范请参考PRD文档。以下是关键端点概述：

## 5.1 LangServe自动生成端点

- `POST /langgraph/invoke` - 同步调用工作流
- `POST /langgraph/stream` - SSE流式调用工作流
- `POST /langgraph/batch` - 批量调用工作流
- `POST /langgraph/stream_events` - 详细事件流（调试）

## 5.2 工作流管理API

- `GET /api/v1/workflows` - 获取工作流列表
- `POST /api/v1/workflows` - 创建新工作流
- `GET /api/v1/workflows/{workflowId}` - 获取工作流详情
- `DELETE /api/v1/workflows/{workflowId}` - 取消工作流
- `POST /api/v1/workflows/{workflowId}/resume` - 恢复暂停的工作流

## 5.3 人工确认API

- `GET /api/v1/confirmations/pending` - 获取待确认列表
- `GET /api/v1/confirmations/{confirmationId}` - 获取确认详情
- `POST /api/v1/confirmations/{confirmationId}/respond` - 响应人工确认

## 5.4 模型配置API

- `GET /api/v1/models` - 获取模型配置列表
- `POST /api/v1/models` - 添加模型配置
- `PUT /api/v1/models/{modelId}` - 更新模型配置
- `DELETE /api/v1/models/{modelId}` - 删除模型配置
- `POST /api/v1/models/{modelId}/test` - 测试模型连接

## 5.5 认证API

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新Token

## 5.6 健康检查

- `GET /api/v1/health` - 服务健康状态

---
