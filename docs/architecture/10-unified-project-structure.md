# 10. Unified Project Structure

```
BMAD-METHOD/
├── .github/workflows/          # CI/CD
├── backend/                    # 后端（Python）
│   ├── langgraph_service/      # 工作流服务
│   │   ├── main.py
│   │   ├── workflow_engine.py
│   │   ├── api_gateway.py
│   │   ├── middleware/
│   │   ├── agents/             # 八大智能体
│   │   └── services/
│   ├── model_adapters/         # 模型适配器
│   ├── shared/                 # 后端共享
│   │   ├── database/
│   │   └── utils/
│   └── tests/
├── frontend/web/               # 前端（Vue）
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── composables/
│   │   ├── stores/             # Pinia
│   │   ├── router/
│   │   ├── services/
│   │   └── main.ts
│   ├── tests/
│   └── package.json
├── shared/types/               # 共享类型定义
├── docker/                     # Docker配置
├── docs/                       # 文档
└── scripts/                    # 脚本
```

---
