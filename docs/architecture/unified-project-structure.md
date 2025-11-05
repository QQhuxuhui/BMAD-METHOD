# Unified Project Structure

```
BMAD-METHOD/
├── backend/                          # FastAPI + LangGraph后端
│   ├── app/
│   │   ├── api/v1/                  # API路由
│   │   ├── core/                    # 核心模块
│   │   │   ├── config.py
│   │   │   ├── langgraph/          # LangGraph工作流
│   │   │   ├── logging.py
│   │   │   └── metrics.py
│   │   ├── models/                  # SQLModel数据模型
│   │   ├── schemas/                 # Pydantic Schema
│   │   ├── services/                # 业务服务层
│   │   └── main.py                  # 应用入口
│   ├── model_adapters/              # 国产模型适配器
│   ├── tests/                       # 后端测试
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
├── frontend/web/                    # Vue 3前端
│   ├── src/
│   │   ├── components/              # UI组件
│   │   ├── layouts/                 # 布局组件
│   │   ├── router/                  # Vue Router
│   │   ├── services/                # API服务层
│   │   ├── stores/                  # Pinia状态管理
│   │   ├── views/                   # 页面视图
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── docs/                            # 项目文档
│   ├── architecture.md              # 本架构文档
│   ├── langgraph集成方案.md         # PRD v1.2
│   └── stories/                     # 用户故事
└── README.md
```

---
