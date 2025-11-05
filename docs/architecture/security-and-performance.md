# Security and Performance

**Frontend Security:**

- XSS Prevention: Vue 3自动转义
- Token存储: localStorage
- HTTPS强制: 生产环境

**Backend Security:**

- Input Validation: Pydantic自动验证
- Rate Limiting: 5-100次/分钟
- CORS: 仅允许前端域名

**Performance Targets:**

- Frontend Bundle: < 500KB (gzipped)
- API Response: < 2秒（非LLM）
- Database Query: < 100ms

---
