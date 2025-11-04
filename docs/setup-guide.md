# BMAD LangGraph 1.0 环境搭建指南

本文档提供BMAD智能体系统LangGraph 1.0开发环境的完整搭建步骤。

## 系统要求

### 宿主机环境

- **Conda**: Python环境管理（已配置）
- **Docker**: 容器技术（已配置）
- **Docker Compose**: 容器编排（已配置）
- **nvm**: Node.js版本管理（可选，需要时执行`source ~/.nvm/nvm.sh`）

### 软件版本

- Python: 3.11+ (推荐 3.11.14)
- PostgreSQL: 16+ (Docker容器)
- Redis: 7+ (Docker容器)
- LangGraph: 1.0.2

## 快速开始

```bash
# 1. 创建Python虚拟环境
conda create -n bmad-langgraph python=3.11
conda activate bmad-langgraph

# 2. 安装Python依赖
cd backend
pip install -r requirements.txt

# 3. 配置环境变量
cd ..
cp .env.example .env
# 根据需要编辑.env文件

# 4. 启动数据库服务
docker compose -f docker/docker-compose.dev.yml up -d

# 5. 验证环境
python scripts/verify_environment.py
```

## 详细步骤

### 1. 创建Python虚拟环境

使用Conda创建独立的Python 3.11环境：

```bash
# 创建环境
conda create -n bmad-langgraph python=3.11 -y

# 激活环境
conda activate bmad-langgraph

# 验证Python版本
python --version  # 应显示: Python 3.11.x
```

### 2. 安装Python依赖包

项目依赖已在`backend/requirements.txt`中定义：

```bash
cd backend
pip install -r requirements.txt
```

**核心依赖包**：

- `langgraph==1.0.2` - 智能体工作流引擎
- `langchain>=1.0.0` - LangChain主框架
- `langchain-core>=0.2.38` - 核心功能
- `langgraph-sdk>=0.2.9` - SDK工具
- `fastapi>=0.115.0` - Web框架
- `uvicorn>=0.26.0` - ASGI服务器
- `psycopg[binary]>=3.2.0` - PostgreSQL驱动
- `redis>=5.0.0` - Redis客户端

### 3. 配置环境变量

创建`.env`配置文件：

```bash
cd ..
cp .env.example .env
```

编辑`.env`文件，配置数据库连接：

```bash
# 数据库配置
POSTGRES_DB=bmad_langgraph_dev
POSTGRES_USER=bmad_user
POSTGRES_PASSWORD=bmad_dev_password  # ⚠️ 生产环境请修改

# 数据库连接字符串
DATABASE_URL=postgresql://bmad_user:bmad_dev_password@localhost:5432/bmad_langgraph_dev

# Redis配置
REDIS_URL=redis://localhost:6379/0

# API密钥（Phase 1暂时可为空）
OPENAI_API_KEY=
QWEN_API_KEY=
GLM_API_KEY=
DEEPSEEK_API_KEY=
```

### 4. 启动Docker Compose服务

使用Docker Compose启动PostgreSQL和Redis：

```bash
# 启动服务（后台运行）
docker compose -f docker/docker-compose.dev.yml up -d

# 查看服务状态
docker ps --filter "name=bmad-"

# 查看日志（可选）
docker compose -f docker/docker-compose.dev.yml logs -f
```

**服务清单**：

- `bmad-postgres-dev`: PostgreSQL 16 (端口5432)
- `bmad-redis-dev`: Redis 7 (端口6379)

### 5. 验证环境配置

运行验证脚本确保所有组件正常：

```bash
python scripts/verify_environment.py
```

验证项包括：

- ✅ Python版本检查
- ✅ 关键包安装验证
- ✅ PostgreSQL连接测试
- ✅ Redis连接测试
- ✅ LangGraph基础功能测试

## 常见问题排查

### 问题1：端口被占用

**症状**：Docker Compose启动失败，提示端口已被占用

**解决方案**：

```bash
# 检查5432端口占用
lsof -i :5432

# 停止系统PostgreSQL服务
sudo systemctl stop postgresql

# 检查6379端口占用
lsof -i :6379

# 停止系统Redis服务
sudo systemctl stop redis-server
```

### 问题2：数据库连接失败

**症状**：`password authentication failed`

**解决方案**：

1. 检查`.env`文件中的密码是否与Docker配置一致
2. 重新创建容器使用正确的密码：

```bash
docker compose -f docker/docker-compose.dev.yml down -v
docker compose -f docker/docker-compose.dev.yml up -d
```

### 问题3：Python包导入失败

**症状**：`ModuleNotFoundError`

**解决方案**：

```bash
# 确认已激活虚拟环境
conda activate bmad-langgraph

# 重新安装依赖
pip install -r backend/requirements.txt

# 验证包安装
pip list | grep langgraph
```

### 问题4：Docker容器不健康

**症状**：容器状态显示`unhealthy`

**解决方案**：

```bash
# 查看容器日志
docker logs bmad-postgres-dev
docker logs bmad-redis-dev

# 重启服务
docker compose -f docker/docker-compose.dev.yml restart
```

## 开发命令速查

### Conda环境管理

```bash
# 列出所有环境
conda env list

# 激活环境
conda activate bmad-langgraph

# 停用环境
conda deactivate

# 删除环境（谨慎使用）
conda env remove -n bmad-langgraph
```

### Docker Compose操作

```bash
# 启动服务
docker compose -f docker/docker-compose.dev.yml up -d

# 停止服务
docker compose -f docker/docker-compose.dev.yml stop

# 停止并删除容器+数据卷
docker compose -f docker/docker-compose.dev.yml down -v

# 查看日志
docker compose -f docker/docker-compose.dev.yml logs -f [service_name]

# 重启服务
docker compose -f docker/docker-compose.dev.yml restart
```

### 数据库操作

```bash
# 连接PostgreSQL
docker exec -it bmad-postgres-dev psql -U bmad_user -d bmad_langgraph_dev

# 连接Redis
docker exec -it bmad-redis-dev redis-cli
```

## 下一步

环境搭建完成后，可以开始：

1. **Story 1.2**: FastAPI服务集成
2. **Story 1.3**: 智能体编排引擎开发
3. **Story 1.4**: 工作流状态持久化

## 参考资源

- [LangGraph 1.0 官方文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Redis 文档](https://redis.io/docs/)
