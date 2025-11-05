# Development Workflow

## Prerequisites

```bash
- Docker 24+ 和 Docker Compose 2+
- Python 3.13.2 (通过conda管理)
- Node.js 20+ (通过nvm管理)
- uv (Python包管理器)
```

## Initial Setup

```bash
# 1. 克隆仓库
git clone <repository-url>
cd BMAD-METHOD

# 2. 后端设置
cd backend
conda activate bmad-langgraph
uv sync
cp .env.example .env
docker-compose up -d

# 3. 前端设置
cd ../frontend/web
source ~/.nvm/nvm.sh
nvm use 20
npm install
cp .env.development .env.local
```

## Development Commands

```bash
# 启动后端 (终端1)
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000

# 启动前端 (终端2)
cd frontend/web
npm run dev

# 运行测试
cd backend && pytest tests/
cd frontend/web && npm run test
```

---
