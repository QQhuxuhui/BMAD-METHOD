# 12. Deployment Architecture

## 12.1 部署环境

| 环境        | 前端URL                          | 后端URL                              | 用途     |
| ----------- | -------------------------------- | ------------------------------------ | -------- |
| Development | http://localhost:5173            | http://localhost:8000                | 本地开发 |
| Staging     | https://staging.bmad.example.com | https://staging-api.bmad.example.com | 预生产   |
| Production  | https://bmad.example.com         | https://api.bmad.example.com         | 生产     |

## 12.2 Docker Compose部署

```yaml
# docker/docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.frontend

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

---
