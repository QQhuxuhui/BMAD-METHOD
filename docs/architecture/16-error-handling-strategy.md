# 16. Error Handling Strategy

## 16.1 统一错误格式

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}
```

## 16.2 错误处理流程

1. 后端抛出BMadException
2. 中间件捕获并格式化
3. 返回统一JSON错误响应
4. 前端拦截器显示用户友好消息
5. structlog记录详细错误日志

---
