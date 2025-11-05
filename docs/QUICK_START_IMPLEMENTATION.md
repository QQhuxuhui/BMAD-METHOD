# 🚀 BMAD-METHOD 快速启动实施指南

**方案A：快速启动**的详细执行计划

基于ADR-001决策，使用FastAPI + LangGraph直接集成和Vue 3 + TypeScript前端栈

---

## 📋 执行顺序

按以下顺序执行Stories：

```
Story 1.1 ✅ (已完成) → Story 1.2 (后端初始化) → Story 1.3 (前端初始化) → Story 1.4 (模型适配器)
```

**说明**:

- Story 1.1已完成环境搭建 ✓
- Story 1.2和1.3可以**并行执行**（后端和前端独立）
- Story 1.4依赖Story 1.2的基础设施

---

## 🎯 Story 1.2: 后端项目初始化

### 第1步：创建后端项目结构

```bash
# 进入项目根目录
cd /usr/src/workspace/github/QQhuxuhui/BMAD-METHOD

# 创建目录结构
mkdir -p backend/langgraph_service/{api/v1,workflows,agents,middleware,config,database}
mkdir -p backend/tests/{api,workflows}

# 创建__init__.py文件
find backend/langgraph_service -type d -exec touch {}/__init__.py \;
```

### 第2步：创建FastAPI主应用

创建 `backend/langgraph_service/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="BMAD LangGraph Service",
    description="智能体工作流服务API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "bmad-langgraph"}

@app.get("/")
async def root():
    return {"message": "BMAD LangGraph Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 第3步：更新依赖

添加到 `backend/requirements.txt`:

```txt
# 新增依赖
python-dotenv>=1.0.0
aiofiles>=23.0.0
```

安装依赖：

```bash
# 激活conda环境
/opt/anaconda3/envs/langgraph/bin/pip install python-dotenv aiofiles
```

### 第4步：创建配置管理

创建 `backend/langgraph_service/config/settings.py`:

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "BMAD LangGraph Service"
    debug: bool = True

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库配置
    database_url: str
    redis_url: str

    # CORS配置
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()
```

### 第5步：验证后端启动

```bash
# 启动后端服务
cd backend
/opt/anaconda3/envs/langgraph/bin/uvicorn langgraph_service.main:app --reload --port 8000

# 在另一个终端测试
curl http://localhost:8000/health
# 预期输出: {"status":"ok","service":"bmad-langgraph"}

# 访问API文档
# http://localhost:8000/api/docs
```

### 第6步：创建启动脚本

创建 `scripts/start_backend.sh`:

```bash
#!/bin/bash

echo "🚀 启动BMAD后端服务..."

# 激活conda环境并启动
/opt/anaconda3/envs/langgraph/bin/uvicorn \
    langgraph_service.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --app-dir backend
```

设置权限：

```bash
chmod +x scripts/start_backend.sh
```

---

## 🎨 Story 1.3: 前端项目初始化

### 第1步：初始化Vite项目

```bash
# 确保使用正确的Node.js版本
source ~/.nvm/nvm.sh
nvm use 20  # 或你项目要求的版本

# 创建Vite + Vue + TypeScript项目
cd /usr/src/workspace/github/QQhuxuhui/BMAD-METHOD
npm create vite@latest frontend/web -- --template vue-ts

# 进入项目目录
cd frontend/web

# 安装基础依赖
npm install
```

### 第2步：安装核心依赖

```bash
# UI框架和路由
npm install ant-design-vue@^4.1.0 vue-router@^4.2.0 pinia@^2.1.0

# HTTP客户端和工具
npm install axios dayjs @vueuse/core

# 开发依赖
npm install -D sass unplugin-vue-components vitest @vitejs/plugin-vue
```

### 第3步：配置Vite

更新 `frontend/web/vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false,
        }),
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### 第4步：创建基础项目结构

```bash
cd frontend/web/src

# 创建目录
mkdir -p {components,composables,layouts,router,services,stores,styles,types,views}

# 创建子目录
mkdir -p components/{common,business}
mkdir -p views
```

### 第5步：配置main.ts

更新 `frontend/web/src/main.ts`:

```typescript
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import Antd from 'ant-design-vue';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import 'ant-design-vue/dist/reset.css';
import 'dayjs/locale/zh-cn';

import App from './App.vue';
import router from './router';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(Antd, { locale: zhCN });

app.mount('#app');
```

### 第6步：创建路由配置

创建 `frontend/web/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Dashboard.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
```

### 第7步：创建Dashboard页面

创建 `frontend/web/src/views/Dashboard.vue`:

```vue
<template>
  <div class="dashboard">
    <a-typography-title :level="1">BMAD 监控平台</a-typography-title>
    <a-card title="系统状态">
      <p>
        后端服务: <a-tag :color="backendStatus ? 'green' : 'red'">{{ backendStatus ? '正常' : '离线' }}</a-tag>
      </p>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const backendStatus = ref(false);

onMounted(async () => {
  try {
    const response = await axios.get('/api/health');
    backendStatus.value = response.data.status === 'ok';
  } catch (error) {
    console.error('Failed to check backend status:', error);
  }
});
</script>

<style scoped>
.dashboard {
  padding: 24px;
}
</style>
```

### 第8步：创建环境变量文件

创建 `.env.development`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=BMAD 监控平台
```

### 第9步：验证前端启动

```bash
# 启动前端开发服务器
cd frontend/web
npm run dev

# 访问 http://localhost:3000
# 应该看到Dashboard页面
```

### 第10步：创建启动脚本

创建 `scripts/start_frontend.sh`:

```bash
#!/bin/bash

echo "🎨 启动BMAD前端服务..."

cd frontend/web
npm run dev
```

设置权限：

```bash
chmod +x scripts/start_frontend.sh
```

---

## 🔗 同时启动前后端

### 方法1：使用两个终端

**终端1 - 后端**:

```bash
./scripts/start_backend.sh
```

**终端2 - 前端**:

```bash
./scripts/start_frontend.sh
```

### 方法2：更新Docker Compose（推荐）

更新 `docker/docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  postgres:
    # ... 保持不变

  redis:
    # ... 保持不变

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: bmad-backend-dev
    ports:
      - '8000:8000'
    environment:
      DATABASE_URL: postgresql://bmad_user:bmad_dev_password@postgres:5432/bmad_langgraph_dev
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app
    command: uvicorn langgraph_service.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - bmad-network

  frontend:
    build:
      context: ../frontend/web
      dockerfile: Dockerfile.dev
    container_name: bmad-frontend-dev
    ports:
      - '3000:3000'
    volumes:
      - ../frontend/web:/app
      - /app/node_modules
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    networks:
      - bmad-network

networks:
  bmad-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

启动所有服务：

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

---

## ✅ 验证清单

完成后，请验证以下内容：

### 后端验证

- [ ] 后端服务启动成功（http://localhost:8000）
- [ ] 健康检查端点可访问（http://localhost:8000/health）
- [ ] API文档可访问（http://localhost:8000/api/docs）
- [ ] PostgreSQL连接正常
- [ ] Redis连接正常

### 前端验证

- [ ] 前端服务启动成功（http://localhost:3000）
- [ ] Dashboard页面加载正常
- [ ] 可以显示后端服务状态
- [ ] Ant Design Vue组件正常渲染
- [ ] Vue DevTools可以检测到Pinia和Router

### 集成验证

- [ ] 前端可以调用后端API
- [ ] CORS配置正确，无跨域错误
- [ ] 浏览器控制台无错误

---

## 📚 下一步

完成Story 1.2和1.3后，继续执行：

1. **Story 1.4**: 实现国产模型适配器
   - 参考：`docs/stories/1.4.story.md`
   - 依赖：Story 1.2的基础设施

2. **Story 1.5**: 实现工作流监控界面
   - 依赖：Story 1.3的前端基础

---

## 🔧 故障排查

### 常见问题

**问题1**: 后端启动失败，提示找不到模块

**解决**:

```bash
# 确保在正确的conda环境中
/opt/anaconda3/envs/langgraph/bin/python -m pip install -r backend/requirements.txt
```

**问题2**: 前端启动失败，npm命令not found

**解决**:

```bash
# 加载nvm
source ~/.nvm/nvm.sh

# 使用正确的Node.js版本
nvm use 20
```

**问题3**: 前端无法访问后端API（CORS错误）

**解决**:

- 检查后端`main.py`中的CORS配置
- 确保前端URL在`cors_origins`列表中
- 检查Vite proxy配置

**问题4**: Docker Compose启动失败

**解决**:

```bash
# 查看日志
docker compose -f docker/docker-compose.dev.yml logs

# 重新构建
docker compose -f docker/docker-compose.dev.yml build --no-cache

# 清理并重启
docker compose -f docker/docker-compose.dev.yml down -v
docker compose -f docker/docker-compose.dev.yml up -d
```

---

## 📖 参考资源

### 官方文档

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Vue 3](https://vuejs.org/)
- [Ant Design Vue](https://antdv.com/)
- [Vite](https://vitejs.dev/)

### 模板参考

- [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)
- [antdv-pro](https://github.com/antdv-pro/antdv-pro)

### 项目文档

- [ADR-001: 放弃LangServe，采用直接集成](./adr/001-abandon-langserve-adopt-direct-integration.md)
- [Story 1.2: 后端项目初始化](./stories/1.2.story.md)
- [Story 1.3: 前端项目初始化](./stories/1.3.story.md)

---

**文档创建**: 2025-11-05
**创建人**: John (Product Manager)
**审核状态**: 待开发团队审核
