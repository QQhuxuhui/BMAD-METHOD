# 11. Development Workflow

## 11.1 环境搭建

```bash
# 1. Python环境（conda）
conda create -n bmad-langgraph python=3.11
conda activate bmad-langgraph

# 2. 安装依赖
cd backend
pip install -r requirements.txt

cd ../frontend/web
npm install

# 3. 启动数据库
cd ../../docker
docker-compose -f docker-compose.dev.yml up -d postgres redis

# 4. 配置环境变量
cp ../.env.example .env
# 编辑.env配置数据库和API密钥
```

## 11.2 开发命令

```bash
# 启动后端
cd backend
uvicorn langgraph_service.main:app --reload --port 8000

# 启动前端
cd frontend/web
npm run dev

# 运行测试
cd backend && pytest tests/
cd frontend/web && npm run test
```

---
