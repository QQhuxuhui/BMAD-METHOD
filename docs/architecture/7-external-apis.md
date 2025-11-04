# 7. External APIs

## 7.1 国产大模型API

**Qwen（通义千问）API**

- Base URL: `https://dashscope.aliyuncs.com/api/v1` (云端) 或 `http://localhost:8000/v1` (本地)
- 认证: API Key
- 关键端点: `POST /chat/completions`

**GLM（智谱AI）API**

- Base URL: `https://open.bigmodel.cn/api/paas/v4` (云端) 或 `http://localhost:8001/v1` (本地)
- 认证: API Key
- 关键端点: `POST /chat/completions`

**DeepSeek API**

- Base URL: `https://api.deepseek.com/v1` (云端) 或 `http://localhost:8002/v1` (本地)
- 认证: API Key
- 关键端点: `POST /chat/completions`

## 7.2 GitHub API（Phase 2.5）

- Base URL: `https://api.github.com`
- 认证: Personal Access Token
- 用途: 代码生成后的仓库操作

---
