# 13. Security and Performance

## 13.1 安全要求

**前端安全**:

- CSP Headers配置
- XSS防护（Vue自动转义）
- JWT存储在httpOnly cookie

**后端安全**:

- Pydantic输入验证
- SQL参数化查询
- API限流（10/minute）
- CORS策略配置

**认证安全**:

- JWT Token（24小时过期）
- Refresh Token（7天）

## 13.2 性能优化

**前端**:

- Bundle大小 < 500KB (gzipped)
- 路由懒加载
- API响应缓存（Redis，5分钟）

**后端**:

- API响应 < 2秒
- 模型调用 < 10秒
- 数据库连接池（5-20）
- Redis缓存热点数据

---
