# API Specification

完整的RESTful API规范，基于OpenAPI 3.0标准。FastAPI自动生成交互式API文档（Swagger UI: `http://localhost:8000/docs`）。

## 核心端点概览

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

## 认证方式

所有需要认证的端点使用Bearer Token（JWT）：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 限流规则

- 登录端点：5次/分钟
- 工作流创建：10次/分钟
- 查询端点：100次/分钟

## 错误响应格式

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
