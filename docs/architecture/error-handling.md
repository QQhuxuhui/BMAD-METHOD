# Error Handling

**Error Format:**

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    request_id: string;
  };
}
```

**Frontend:** Axios拦截器统一处理
**Backend:** FastAPI全局异常处理

---
