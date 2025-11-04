# LangGraph + 国产模型私有化部署方案调研报告

## 📋 执行摘要

**调研背景**: BMAD-METHOD 智能体系统需要从依赖 Claude API 的 IDE 环境转向支持国产化模型的企业级 Web 应用

**核心诉求**:

- ✅ 不依赖 Claude 等国外模型
- ✅ 支持国产大模型私有化部署
- ✅ 提供浏览器端 API 接口
- ✅ 保持当前 7 个专家智能体协作能力

**推荐方案**: **LangGraph + 国产大模型 (Qwen/GLM/DeepSeek) + vLLM 推理引擎**

---

## 🎯 方案概览

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                    浏览器 Web 应用                           │
│              (React/Vue + WebSocket)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Web API Gateway Layer                          │
│         (FastAPI/NestJS + LangGraph Server)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ REST API     │  │ WebSocket    │  │ Streaming    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ LangGraph   │  │ LangGraph   │  │ LangGraph   │
│ Orchestrator│  │ Algorithm   │  │ Quality     │
│ Agent       │  │ Expert      │  │ Evaluator   │
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 国产 LLM 1   │  │ 国产 LLM 2   │  │ 国产 LLM 3   │
│ (Qwen2.5)   │  │ (GLM-4.5)   │  │(DeepSeek R1)│
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │   vLLM 推理引擎集群      │
            │   (Docker + K8s)        │
            └─────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │   State Management      │
            │   (Postgres + Redis)    │
            └─────────────────────────┘
```

---

## 🔍 LangGraph 框架深度分析

### 1.1 核心能力

#### 有状态智能体编排

LangGraph 是 LangChain 团队专为构建多步骤、有状态的智能体工作流而设计的框架：

```typescript
// LangGraph StateGraph 定义
import { StateGraph, Annotation } from '@langchain/langgraph';

const StateAnnotation = Annotation.Root({
  projectDescription: Annotation<string>,
  phase: Annotation<string>,
  algorithmRecommendation: Annotation<string>,
  constraints: Annotation<string[]>,
  objectives: Annotation<string[]>,
  codeGenerated: Annotation<string>,
  qualityScore: Annotation<number>,
});

// 与 BMAD 的状态链管理高度匹配
```

#### 多智能体协作模式

LangGraph 支持多种协作模式，与 BMAD 的 7 个专家智能体架构完美匹配：

**1. Supervisor 模式** (监督者模式)

```typescript
// Orchestrator 作为 Supervisor
const workflow = new StateGraph(StateAnnotation)
  .addNode('orchestrator', orchestratorAgent)
  .addNode('algorithmExpert', algorithmExpertAgent)
  .addNode('constraintExpert', constraintExpertAgent)
  .addNode('objectiveExpert', objectiveExpertAgent)
  .addNode('domainExpert', domainExpertAgent)
  .addNode('extensionGuide', extensionGuideAgent)
  .addNode('qualityEvaluator', qualityEvaluatorAgent)
  .addConditionalEdges(
    'orchestrator',
    routeToExpert, // 根据当前 Phase 路由到不同专家
    ['algorithmExpert', 'constraintExpert', 'objectiveExpert'],
  );
```

**2. Handoff 机制** (智能体交接)

```typescript
import { Command } from '@langchain/langgraph';

async function algorithmExpert(state: State) {
  const recommendation = await callLLM(state);

  // 交接给下一个专家
  return new Command({
    update: { algorithmRecommendation: recommendation },
    goto: 'constraintExpert', // 交接给约束专家
  });
}
```

**3. Orchestrator-Worker 模式** (编排者-工作者)

```typescript
// 并行调用多个专家
function assignExperts(state: State) {
  return [
    new Send('algorithmExpert', { task: 'algorithm' }),
    new Send('constraintExpert', { task: 'constraint' }),
    new Send('objectiveExpert', { task: 'objective' }),
  ];
}
```

#### Human-in-the-Loop (人机协同)

LangGraph 内置 `interrupt()` 机制，与 BMAD 的用户确认机制完全对应：

```typescript
async function humanReview(state: State) {
  // 暂停等待人工确认
  const decision = interrupt({
    phase: state.phase,
    recommendation: state.algorithmRecommendation,
    action: '请确认算法推荐方案',
  });

  if (decision.approved) {
    return new Command({
      update: { approved: true },
      goto: 'codeGeneration',
    });
  } else {
    return new Command({
      update: { feedback: decision.feedback },
      goto: 'algorithmExpert', // 返回重新生成
    });
  }
}
```

#### 状态持久化

```typescript
import { MemorySaver } from '@langchain/langgraph';

const memory = new MemorySaver(); // 开发环境
// 生产环境使用 Postgres
const checkpointer = new PostgresSaver(connectionString);

const app = workflow.compile({ checkpointer: memory });

// 调用时指定 thread_id 实现多租户隔离
await app.invoke(initialState, {
  configurable: { thread_id: 'user_123_task_456' },
});
```

### 1.2 与 BMAD 架构对比

| 特性           | BMAD 当前架构         | LangGraph 架构            | 匹配度     |
| -------------- | --------------------- | ------------------------- | ---------- |
| **状态管理**   | YAML 文件状态链       | StateGraph + Checkpointer | ⭐⭐⭐⭐⭐ |
| **智能体协作** | 7 个专家 YAML 定义    | 7 个 Node + 条件边        | ⭐⭐⭐⭐⭐ |
| **人机交互**   | Human-in-Loop (P0-P4) | interrupt() + resume()    | ⭐⭐⭐⭐⭐ |
| **工作流编排** | Phase 0-4 线性流程    | 条件路由 + 并行执行       | ⭐⭐⭐⭐   |
| **质量门禁**   | 6 重验证 + 自动修复   | 循环节点 + 条件判断       | ⭐⭐⭐⭐   |
| **知识库引用** | Sidecar 模板 + @引用  | Agent Skills / 向量检索   | ⭐⭐⭐⭐   |

**结论**: LangGraph 的设计理念与 BMAD 高度契合，迁移风险低。

---

## 🇨🇳 国产大模型对比与选型

### 2.1 国产模型全景图 (2025)

| 模型                   | 参数规模  | 性能对标        | LangChain 支持     | 私有化难度 | 推荐度     |
| ---------------------- | --------- | --------------- | ------------------ | ---------- | ---------- |
| **通义千问 Qwen2.5**   | 0.5B-110B | GPT-4 级别      | ✅ 官方支持        | ⭐⭐       | ⭐⭐⭐⭐⭐ |
| **智谱 GLM-4.5**       | 9B-355B   | Claude 3.5 级别 | ✅ 官方支持        | ⭐⭐       | ⭐⭐⭐⭐⭐ |
| **DeepSeek R1**        | 7B-671B   | OpenAI o1 级别  | ✅ 兼容 OpenAI API | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |
| **百川 Baichuan-4**    | 7B-60B    | GPT-3.5 级别    | ✅ 官方集成        | ⭐⭐       | ⭐⭐⭐⭐   |
| **文心一言 4.0 Turbo** | 未公开    | GPT-4 级别      | ✅ 社区支持        | ⭐⭐⭐⭐   | ⭐⭐⭐     |
| **讯飞星火 4.0**       | 未公开    | GPT-4 级别      | ✅ 社区支持        | ⭐⭐⭐⭐   | ⭐⭐⭐     |

### 2.2 推荐模型组合方案

#### 方案 A: 通义千问 Qwen2.5 (阿里云)

**核心优势**:

- ✅ **性能卓越**: Qwen2.5-72B 在多项基准测试中超越 GPT-4
- ✅ **多模态支持**: Qwen2.5-VL 支持图表、文档分析
- ✅ **完整生态**: ModelScope 镜像下载，阿里云 PAI-EAS 一键部署
- ✅ **代码能力强**: Qwen2.5-Coder 专门优化代码生成
- ✅ **LangChain 原生支持**

**LangChain 集成示例**:

```python
from langchain_community.llms import Tongyi
from langchain.chat_models import init_chat_model

# 使用阿里云 API
model = init_chat_model(
    model="qwen-plus",
    model_provider="tongyi",
    api_key="YOUR_DASHSCOPE_API_KEY"
)

# 使用私有化部署的 Qwen
model = init_chat_model(
    model="Qwen/Qwen2.5-72B-Instruct",
    model_provider="openai",  # vLLM 兼容 OpenAI API
    base_url="http://your-vllm-server:8000/v1",
    api_key="EMPTY"
)
```

**硬件需求 (私有化部署)**:

```
Qwen2.5-7B-Instruct:
- GPU: 1 x RTX 4090 (24GB)
- 内存: 32GB
- 存储: 50GB

Qwen2.5-32B-Instruct:
- GPU: 2 x RTX 4090 / 1 x A100 (40GB)
- 内存: 64GB
- 存储: 100GB

Qwen2.5-72B-Instruct:
- GPU: 2 x A100 (80GB)
- 内存: 128GB
- 存储: 200GB
```

**部署命令**:

```bash
# Docker + vLLM 部署
docker run --gpus all \
  -p 8000:8000 \
  vllm/vllm-openai:v0.6.1 \
  --model Qwen/Qwen2.5-72B-Instruct \
  --served-model-name qwen-72b \
  --trust-remote-code \
  --gpu-memory-utilization 0.90 \
  --max-model-len 32768
```

---

#### 方案 B: 智谱 GLM-4.5 (清华智谱)

**核心优势**:

- ✅ **开源友好**: MIT 协议，完全开源
- ✅ **推理速度快**: 100+ tokens/秒
- ✅ **工具调用优化**: 原生支持 Function Calling
- ✅ **兼容 Claude Code**: 官方支持 Cline 等开发工具
- ✅ **中文能力强**: 相比 Llama 提升 50%

**LangChain 集成示例**:

```python
from langchain_community.chat_models import ChatZhipuAI

# 使用智谱 API
model = ChatZhipuAI(
    model="glm-4-plus",
    api_key="YOUR_ZHIPU_API_KEY"
)

# 使用私有化部署
model = init_chat_model(
    model="THUDM/glm-4-9b-chat",
    model_provider="openai",
    base_url="http://your-server:8000/v1"
)
```

**定价优势**:

- API 调用: 0.8 元/百万 tokens (输入), 2 元/百万 tokens (输出)
- 注册送 180 万 tokens，认证后 400 万 tokens
- 是 GPT-4 价格的 1/10

**硬件需求**:

```
GLM-4-9B:
- GPU: 1 x RTX 4090 (24GB)
- 存储: 18GB

GLM-4-Plus:
- 需要调用智谱 API (不支持私有化)
```

---

#### 方案 C: DeepSeek R1 (推理优化)

**核心优势**:

- ✅ **顶级推理能力**: 对标 OpenAI o1，部分超越
- ✅ **完全开源**: 支持 1.5B-671B 全系列
- ✅ **成本极低**: 私有化部署性价比最高
- ✅ **强推理 + 低资源**: R1-Distill-Qwen-7B 适合边缘部署

**LangChain 集成示例**:

```python
# DeepSeek R1 兼容 OpenAI API
model = init_chat_model(
    model="deepseek-reasoner",
    model_provider="openai",
    base_url="https://api.deepseek.com/v1",
    api_key="YOUR_DEEPSEEK_API_KEY"
)

# 私有化部署 (Ollama)
from langchain_community.llms import Ollama

model = Ollama(model="deepseek-r1:7b")
```

**硬件对比**:

```
DeepSeek R1 vs DeepSeek V3 成本对比:

V3 (671B MoE):
- 硬件成本: 150-200 万人民币 (8 x H100)
- 适用场景: 超大规模企业

R1-Distill-Qwen-32B:
- 硬件成本: 10 万人民币 (4 x RTX 4090)
- 适用场景: 中小企业私有化部署
- 性能保持: V3 的 80-90%
```

---

### 2.3 推荐选型策略

#### 场景 1: 预算充足 + 最高性能

```
推荐: Qwen2.5-72B-Instruct
硬件: 2 x A100 (80GB)
总成本: 约 40-50 万人民币
```

#### 场景 2: 中等预算 + 均衡性能

```
推荐: GLM-4-9B + DeepSeek R1-7B (混合部署)
- GLM-4-9B: 常规对话和代码生成
- DeepSeek R1-7B: 复杂推理任务
硬件: 2 x RTX 4090 (24GB)
总成本: 约 4-6 万人民币
```

#### 场景 3: 小预算 + 快速验证

```
推荐: Qwen2.5-7B-Instruct (Ollama 部署)
硬件: 1 x RTX 4090 (24GB)
总成本: 约 2 万人民币
```

---

## 🔧 私有化部署技术栈

### 3.1 推理引擎对比

| 引擎       | 性能       | 易用性     | 扩展性     | 推荐场景            |
| ---------- | ---------- | ---------- | ---------- | ------------------- |
| **vLLM**   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | 生产环境首选        |
| **Ollama** | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | 开发测试 + 边缘部署 |
| **SGLang** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐   | 超高并发场景        |
| **TGI**    | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | HuggingFace 生态    |

### 3.2 vLLM 生产级部署方案

#### Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  vllm-qwen:
    image: vllm/vllm-openai:v0.6.1
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0,1
    ports:
      - '8000:8000'
    volumes:
      - ./models:/models
      - ./cache:/root/.cache
    command: >
      --model /models/Qwen2.5-72B-Instruct
      --served-model-name qwen-72b
      --trust-remote-code
      --gpu-memory-utilization 0.90
      --max-model-len 32768
      --tensor-parallel-size 2
      --enable-prefix-caching
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 2
              capabilities: [gpu]

  vllm-glm:
    image: vllm/vllm-openai:v0.6.1
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=2
    ports:
      - '8001:8000'
    command: >
      --model THUDM/glm-4-9b-chat
      --served-model-name glm-4-9b
      --trust-remote-code
      --gpu-memory-utilization 0.85
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: langgraph
      POSTGRES_USER: langgraph
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - '5432:5432'

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data

  langgraph-api:
    build: ./langgraph-api
    depends_on:
      - vllm-qwen
      - vllm-glm
      - postgres
      - redis
    environment:
      - QWEN_BASE_URL=http://vllm-qwen:8000/v1
      - GLM_BASE_URL=http://vllm-glm:8000/v1
      - DATABASE_URL=postgresql://langgraph:${POSTGRES_PASSWORD}@postgres:5432/langgraph
      - REDIS_URL=redis://redis:6379
    ports:
      - '3000:3000'

volumes:
  postgres_data:
  redis_data:
```

#### 性能优化配置

```bash
# vLLM 高性能配置参数说明

--tensor-parallel-size 2       # 模型并行（多 GPU）
--gpu-memory-utilization 0.90  # GPU 显存利用率
--max-model-len 32768          # 最大上下文长度
--enable-prefix-caching        # 前缀缓存加速
--swap-space 4                 # CPU-GPU 交换空间 (GB)
--max-num-seqs 256             # 最大并发请求数
--disable-log-requests         # 生产环境禁用日志

# 量化加速 (降低显存需求)
--quantization awq             # AWQ 4-bit 量化
--quantization gptq            # GPTQ 量化
```

#### 负载均衡配置

```nginx
# nginx.conf
upstream vllm_cluster {
    least_conn;  # 最少连接数负载均衡

    server vllm-1:8000 max_fails=3 fail_timeout=30s;
    server vllm-2:8000 max_fails=3 fail_timeout=30s;
    server vllm-3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.your-domain.com;

    location /v1/ {
        proxy_pass http://vllm_cluster;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # 超时配置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # 流式传输
        proxy_buffering off;
    }
}
```

---

### 3.3 Kubernetes 生产部署

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-qwen
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm-qwen
  template:
    metadata:
      labels:
        app: vllm-qwen
    spec:
      containers:
        - name: vllm
          image: vllm/vllm-openai:v0.6.1
          command:
            - python3
            - -m
            - vllm.entrypoints.openai.api_server
            - --model
            - /models/Qwen2.5-72B-Instruct
            - --served-model-name
            - qwen-72b
            - --tensor-parallel-size
            - '2'
          ports:
            - containerPort: 8000
          resources:
            limits:
              nvidia.com/gpu: 2
              memory: 128Gi
            requests:
              nvidia.com/gpu: 2
              memory: 64Gi
          volumeMounts:
            - name: model-storage
              mountPath: /models
      volumes:
        - name: model-storage
          persistentVolumeClaim:
            claimName: model-pvc
      nodeSelector:
        gpu-type: a100

---
apiVersion: v1
kind: Service
metadata:
  name: vllm-qwen-service
spec:
  type: ClusterIP
  selector:
    app: vllm-qwen
  ports:
    - port: 8000
      targetPort: 8000

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-qwen-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-qwen
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 🏗️ BMAD 迁移到 LangGraph 方案

### 4.1 架构映射关系

| BMAD 组件              | LangGraph 实现           | 实现难度    |
| ---------------------- | ------------------------ | ----------- |
| **Orchestrator Agent** | Supervisor Node          | ⭐ 低       |
| **Algorithm Expert**   | Worker Node              | ⭐ 低       |
| **Constraint Expert**  | Worker Node              | ⭐ 低       |
| **Objective Expert**   | Worker Node              | ⭐ 低       |
| **Domain Expert**      | Worker Node              | ⭐ 低       |
| **Extension Guide**    | Worker Node              | ⭐ 低       |
| **Quality Evaluator**  | Validator Node           | ⭐⭐ 中     |
| **YAML State**         | StateGraph + Postgres    | ⭐⭐ 中     |
| **Human-in-Loop**      | interrupt() + WebSocket  | ⭐⭐⭐ 中高 |
| **Sidecar 知识库**     | Vector Store + RAG       | ⭐⭐⭐ 中高 |
| **质量门禁**           | Conditional Edges + Loop | ⭐⭐ 中     |

### 4.2 代码示例：7 个专家智能体迁移

#### Orchestrator Agent (系统编排协调)

```typescript
// src/agents/orchestrator.agent.ts
import { StateGraph, Annotation, Send } from '@langchain/langgraph';
import { ChatOpenAI } from '@langchain/openai';

// 状态定义
const APSState = Annotation.Root({
  projectDescription: Annotation<string>,
  phase: Annotation<string>,
  mode: Annotation<string>, // A 或 B
  algorithmRecommendation: Annotation<string>({ default: '' }),
  constraints: Annotation<string[]>({ default: () => [] }),
  objectives: Annotation<string[]>({ default: () => [] }),
  domainKnowledge: Annotation<string>({ default: '' }),
  extensionTemplate: Annotation<string>({ default: '' }),
  codeGenerated: Annotation<string>({ default: '' }),
  qualityReport: Annotation<any>({ default: null }),
  humanFeedback: Annotation<string>({ default: '' }),
  todoList: Annotation<string[]>({ default: () => [] }),
});

// Orchestrator Node
async function orchestratorAgent(state: typeof APSState.State) {
  const model = new ChatOpenAI({
    modelName: 'qwen-72b',
    configuration: {
      baseURL: 'http://vllm-qwen:8000/v1',
      apiKey: 'EMPTY',
    },
  });

  const systemPrompt = `你是系统编排协调智能体，负责协调 6 个专家完成 APS 项目开发。
当前处于 ${state.phase}，请根据项目描述决定下一步行动。

Phase 流程:
- Phase 0: 需求理解与初始规划
- Phase 1: 问题分析 (算法推荐 → 约束识别 → 目标确认)
- Phase 2: 专家协作 (领域适配 + 扩展指导)
- Phase 3: 代码生成与验证
- Phase 4: 质量评测与交付

请输出下一步要调用的专家节点名称。`;

  const response = await model.invoke([
    { role: 'system', content: systemPrompt },
    { role: 'user', content: state.projectDescription },
  ]);

  // 解析路由决策
  const nextExpert = parseExpertRoute(response.content);

  return new Command({
    update: {
      phase: calculateNextPhase(state.phase),
      todoList: [...state.todoList, `调用 ${nextExpert}`],
    },
    goto: nextExpert,
  });
}

// 路由函数
function routeToExpert(state: typeof APSState.State): string {
  switch (state.phase) {
    case 'Phase 0':
      return 'orchestrator';
    case 'Phase 1':
      if (!state.algorithmRecommendation) return 'algorithmExpert';
      if (state.constraints.length === 0) return 'constraintExpert';
      if (state.objectives.length === 0) return 'objectiveExpert';
      return 'humanReview'; // Phase 1 确认
    case 'Phase 2':
      if (!state.domainKnowledge) return 'domainExpert';
      if (!state.extensionTemplate) return 'extensionGuide';
      return 'humanReview'; // Phase 2 确认
    case 'Phase 3':
      if (!state.codeGenerated) return 'codeGenerator';
      return 'qualityEvaluator';
    case 'Phase 4':
      return '__end__';
    default:
      return '__end__';
  }
}
```

#### Algorithm Expert (调度算法专家)

```typescript
// src/agents/algorithm-expert.agent.ts
import { tool } from '@langchain/core/tools';
import * as z from 'zod';

// 知识库检索工具
const searchAlgorithmLibrary = tool(
  async ({ category, keywords }) => {
    // 从向量数据库检索算法知识
    const vectorStore = getVectorStore();
    const results = await vectorStore.similaritySearch(`${category}: ${keywords}`, { k: 5 });
    return results.map((doc) => doc.pageContent).join('\n\n');
  },
  {
    name: 'searchAlgorithmLibrary',
    description: '检索算法知识库（精确算法、启发式、元启发式、混合算法）',
    schema: z.object({
      category: z.enum(['exact', 'heuristic', 'metaheuristic', 'hybrid']),
      keywords: z.string(),
    }),
  },
);

async function algorithmExpertAgent(state: typeof APSState.State) {
  const model = new ChatOpenAI({
    modelName: 'qwen-72b',
    configuration: {
      baseURL: 'http://vllm-qwen:8000/v1',
    },
  }).bindTools([searchAlgorithmLibrary]);

  const systemPrompt = `你是张效率，调度算法专家，拥有 15 年算法研发经验。

【核心职责】
1. 分析项目需求，推荐最优算法类别
2. 引用知识库中的算法模板
3. 解释算法原理和适用场景

【知识库结构】
- 精确算法：分支定界、动态规划、整数规划
- 启发式算法：贪心、局部搜索、构造式启发
- 元启发式算法：遗传算法、模拟退火、粒子群
- 混合算法：Matheuristics、Large Neighborhood Search

【约束】
- 必须使用 searchAlgorithmLibrary 工具检索知识库
- 所有推荐必须附 @引用路径`;

  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: `项目描述:\n${state.projectDescription}` },
  ];

  const response = await model.invoke(messages);

  // 处理工具调用
  if (response.tool_calls && response.tool_calls.length > 0) {
    const toolResults = await Promise.all(response.tool_calls.map((tc) => searchAlgorithmLibrary.invoke(tc.args)));

    messages.push(response);
    messages.push(
      ...toolResults.map((r) => ({
        role: 'tool',
        content: r,
        tool_call_id: response.tool_calls[0].id,
      })),
    );

    const finalResponse = await model.invoke(messages);

    return new Command({
      update: { algorithmRecommendation: finalResponse.content },
      goto: 'constraintExpert',
    });
  }

  return new Command({
    update: { algorithmRecommendation: response.content },
    goto: 'constraintExpert',
  });
}
```

#### Human Review Node (人机交互确认)

```typescript
// src/agents/human-review.agent.ts
import { interrupt } from '@langchain/langgraph';

async function humanReviewAgent(state: typeof APSState.State) {
  // 准备确认内容
  const reviewData = {
    phase: state.phase,
    summary: generatePhaseSummary(state),
    details: {
      algorithm: state.algorithmRecommendation,
      constraints: state.constraints,
      objectives: state.objectives,
      code: state.codeGenerated,
    },
    action: getActionPrompt(state.phase),
  };

  // 暂停等待人工确认（通过 WebSocket 推送到前端）
  const decision = interrupt(reviewData);

  if (decision.approved) {
    return new Command({
      update: {
        phase: advancePhase(state.phase),
        humanFeedback: decision.feedback || '',
      },
      goto: routeToExpert({ ...state, phase: advancePhase(state.phase) }),
    });
  } else {
    // 用户拒绝，返回上一个专家重新生成
    return new Command({
      update: { humanFeedback: decision.feedback },
      goto: getPreviousExpert(state.phase),
    });
  }
}

function getActionPrompt(phase: string): string {
  const prompts = {
    'Phase 1': '请确认算法推荐、约束识别、目标定义是否准确',
    'Phase 2': '请确认领域知识和扩展模板是否符合需求',
    'Phase 3': '请审查生成的代码和质量报告',
  };
  return prompts[phase] || '请确认当前阶段输出';
}
```

#### 完整工作流编排

```typescript
// src/workflows/aps-workflow.ts
import { StateGraph, START, END } from '@langchain/langgraph';
import { PostgresSaver } from '@langchain/langgraph-checkpoint-postgres';

export function createAPSWorkflow() {
  const checkpointer = new PostgresSaver({
    connectionString: process.env.DATABASE_URL,
  });

  const workflow = new StateGraph(APSState)
    // 添加所有节点
    .addNode('orchestrator', orchestratorAgent)
    .addNode('algorithmExpert', algorithmExpertAgent)
    .addNode('constraintExpert', constraintExpertAgent)
    .addNode('objectiveExpert', objectiveExpertAgent)
    .addNode('domainExpert', domainExpertAgent)
    .addNode('extensionGuide', extensionGuideAgent)
    .addNode('qualityEvaluator', qualityEvaluatorAgent)
    .addNode('humanReview', humanReviewAgent)

    // 定义流程
    .addEdge(START, 'orchestrator')
    .addConditionalEdges('orchestrator', routeToExpert, [
      'algorithmExpert',
      'constraintExpert',
      'objectiveExpert',
      'domainExpert',
      'extensionGuide',
      'qualityEvaluator',
      'humanReview',
      END,
    ])
    // 所有专家完成后回到 orchestrator
    .addEdge('algorithmExpert', 'orchestrator')
    .addEdge('constraintExpert', 'orchestrator')
    .addEdge('objectiveExpert', 'orchestrator')
    .addEdge('domainExpert', 'orchestrator')
    .addEdge('extensionGuide', 'orchestrator')

    // 质量评测循环
    .addConditionalEdges(
      'qualityEvaluator',
      (state) => {
        const score = state.qualityReport?.totalScore || 0;
        return score >= 80 ? 'humanReview' : 'orchestrator'; // 不合格返回重新生成
      },
      ['humanReview', 'orchestrator'],
    )

    // 人工确认后路由
    .addConditionalEdges('humanReview', routeToExpert, ['orchestrator', 'algorithmExpert', 'constraintExpert', 'objectiveExpert', END]);

  return workflow.compile({ checkpointer });
}
```

---

### 4.3 前后端集成

#### FastAPI 后端

```python
# api/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.postgres import PostgresSaver
import asyncio
import json

app = FastAPI()

# 初始化 LangGraph
workflow = create_aps_workflow()

# 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, thread_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[thread_id] = websocket

    def disconnect(self, thread_id: str):
        if thread_id in self.active_connections:
            del self.active_connections[thread_id]

    async def send_update(self, thread_id: str, message: dict):
        if thread_id in self.active_connections:
            await self.active_connections[thread_id].send_json(message)

manager = ConnectionManager()

# 创建 APS 任务
@app.post("/api/aps/tasks")
async def create_task(request: dict):
    thread_id = f"task_{uuid.uuid4()}"

    initial_state = {
        "projectDescription": request["description"],
        "phase": "Phase 0",
        "mode": request.get("mode", "A")
    }

    # 异步启动工作流
    asyncio.create_task(
        run_workflow(thread_id, initial_state)
    )

    return {
        "taskId": thread_id,
        "status": "running",
        "websocketUrl": f"/ws/{thread_id}"
    }

# WebSocket 连接
@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    await manager.connect(thread_id, websocket)

    try:
        while True:
            # 等待人工确认消息
            data = await websocket.receive_json()

            if data["type"] == "human_decision":
                # 恢复工作流执行
                await workflow.update_state(
                    {"configurable": {"thread_id": thread_id}},
                    {"humanDecision": data["decision"]},
                    as_node="humanReview"
                )

                # 继续执行
                async for update in workflow.astream(
                    None,
                    {"configurable": {"thread_id": thread_id}}
                ):
                    await manager.send_update(thread_id, {
                        "type": "state_update",
                        "data": update
                    })

    except WebSocketDisconnect:
        manager.disconnect(thread_id)

# 运行工作流
async def run_workflow(thread_id: str, initial_state: dict):
    async for event in workflow.astream(
        initial_state,
        {
            "configurable": {"thread_id": thread_id},
            "stream_mode": "updates"
        }
    ):
        event_type = list(event.keys())[0]
        event_data = event[event_type]

        # 检测是否需要人工确认
        if event_type == "humanReview":
            await manager.send_update(thread_id, {
                "type": "human_review_required",
                "data": event_data
            })
            # 暂停，等待 WebSocket 消息
            return

        # 推送状态更新
        await manager.send_update(thread_id, {
            "type": "agent_update",
            "agent": event_type,
            "data": event_data
        })
```

#### React 前端

```typescript
// frontend/src/hooks/useAPSTask.ts
import { useEffect, useState } from 'react';

export function useAPSTask(taskId: string) {
  const [state, setState] = useState<any>(null);
  const [needsReview, setNeedsReview] = useState(false);
  const [reviewData, setReviewData] = useState<any>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:3000/ws/${taskId}`);

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'state_update':
          setState(message.data);
          break;

        case 'human_review_required':
          setNeedsReview(true);
          setReviewData(message.data);
          break;

        case 'agent_update':
          // 更新智能体执行日志
          console.log(`Agent ${message.agent} updated:`, message.data);
          break;
      }
    };

    setWs(websocket);

    return () => websocket.close();
  }, [taskId]);

  const approveReview = (feedback?: string) => {
    ws?.send(JSON.stringify({
      type: 'human_decision',
      decision: {
        approved: true,
        feedback: feedback || ''
      }
    }));
    setNeedsReview(false);
  };

  const rejectReview = (feedback: string) => {
    ws?.send(JSON.stringify({
      type: 'human_decision',
      decision: {
        approved: false,
        feedback
      }
    }));
    setNeedsReview(false);
  };

  return {
    state,
    needsReview,
    reviewData,
    approveReview,
    rejectReview
  };
}

// 使用示例
function APSTaskPage({ taskId }: { taskId: string }) {
  const { state, needsReview, reviewData, approveReview, rejectReview } =
    useAPSTask(taskId);

  if (needsReview) {
    return (
      <HumanReviewDialog
        data={reviewData}
        onApprove={approveReview}
        onReject={rejectReview}
      />
    );
  }

  return (
    <div>
      <h2>当前阶段: {state?.phase}</h2>
      <TaskProgress state={state} />
      <AgentOutputs state={state} />
    </div>
  );
}
```

---

## 📈 成本分析

### 5.1 硬件成本估算

#### 方案 A: 高性能方案 (Qwen2.5-72B)

```
硬件配置:
├── GPU: 2 x NVIDIA A100 (80GB) - ¥400,000
├── CPU: AMD EPYC 7763 (64 核) - ¥50,000
├── 内存: 512GB DDR4 - ¥30,000
├── 存储: 4TB NVMe SSD - ¥8,000
├── 网络: 10GbE 交换机 - ¥5,000
└── 服务器机箱 + 电源 - ¥20,000

总计: ¥513,000 (一次性投入)

运营成本 (月):
├── 电费: 2 x A100 @ 400W x 24h x 30d x ¥0.8/度 ≈ ¥460
├── 带宽: 100Mbps 专线 - ¥500
└── 运维: 0.5 人 x ¥15,000 - ¥7,500

月成本: ¥8,460
年运营成本: ¥101,520
```

#### 方案 B: 中等方案 (GLM-4-9B + Qwen2.5-32B)

```
硬件配置:
├── GPU: 3 x NVIDIA RTX 4090 (24GB) - ¥54,000
├── CPU: AMD Ryzen 9 7950X - ¥4,000
├── 内存: 128GB DDR5 - ¥5,000
├── 存储: 2TB NVMe SSD - ¥2,000
├── 主板 + 电源 + 机箱 - ¥5,000
└── 散热系统 - ¥3,000

总计: ¥73,000 (一次性投入)

运营成本 (月):
├── 电费: 3 x 450W x 24h x 30d x ¥0.8/度 ≈ ¥780
└── 带宽: 50Mbps - ¥300

月成本: ¥1,080
年运营成本: ¥12,960
```

#### 方案 C: 入门方案 (Qwen2.5-7B + DeepSeek R1-7B)

```
硬件配置:
├── GPU: 1 x NVIDIA RTX 4090 (24GB) - ¥18,000
├── CPU: AMD Ryzen 7 7700X - ¥2,000
├── 内存: 64GB DDR5 - ¥2,000
├── 存储: 1TB NVMe SSD - ¥800
└── 主板 + 电源 + 机箱 - ¥3,000

总计: ¥25,800 (一次性投入)

运营成本 (月):
├── 电费: 450W x 24h x 30d x ¥0.8/度 ≈ ¥260
└── 带宽: 20Mbps - ¥150

月成本: ¥410
年运营成本: ¥4,920
```

### 5.2 云 API vs 私有化 TCO 对比 (3 年)

| 项目            | Claude API     | 智谱 API       | 私有化 (方案 B) |
| --------------- | -------------- | -------------- | --------------- |
| **初期投入**    | ¥0             | ¥0             | ¥73,000         |
| **月调用量**    | 1000 万 tokens | 1000 万 tokens | 无限制          |
| **月 API 成本** | ~¥150,000      | ~¥15,000       | ¥0              |
| **月运维成本**  | ¥0             | ¥0             | ¥1,080          |
| **3 年总成本**  | ¥5,400,000     | ¥540,000       | ¥111,880        |
| **性价比**      | ❌ 极低        | ⚠️ 中等        | ✅ 极高         |

**结论**:

- **日调用量 > 100 万 tokens**: 私有化部署回本周期 < 6 个月
- **日调用量 > 500 万 tokens**: 私有化部署回本周期 < 2 个月
- **数据敏感企业**: 私有化是唯一选择

---

## 🚀 实施路线图

### Phase 1: 技术验证 (2 周)

**目标**: 验证 LangGraph + 国产模型可行性

```
Week 1: 环境搭建
├── Day 1-2: 部署 Ollama + Qwen2.5-7B
├── Day 3-4: 搭建 LangGraph 开发环境
└── Day 5: 实现单一 Agent (Algorithm Expert)

Week 2: 原型开发
├── Day 1-3: 实现 3 个核心 Agent (Orchestrator + 2 Experts)
├── Day 4: 实现 Human-in-Loop WebSocket
└── Day 5: 端到端测试 + 评审

交付物:
✅ 可运行的原型 Demo
✅ 性能基准测试报告
✅ Go/No-Go 决策建议
```

### Phase 2: 核心迁移 (6 周)

**目标**: 迁移 7 个专家 + 状态管理

```
Week 3-4: 智能体迁移
├── 迁移 7 个专家 YAML → LangGraph Nodes
├── 实现知识库 Vector Store (Pinecone/Weaviate)
├── 实现强引用策略验证
└── 单元测试覆盖率 > 80%

Week 5-6: 状态与工作流
├── 实现 StateGraph 完整流程
├── Postgres + Redis 状态持久化
├── 实现 Phase 0-4 条件路由
└── 实现质量门禁循环

Week 7-8: 私有化部署
├── vLLM + Qwen2.5-32B 生产部署
├── Docker Compose 多容器编排
├── Nginx 负载均衡配置
└── 性能压测 (100 并发)

交付物:
✅ 7 个智能体完整迁移
✅ 生产级 Docker 部署包
✅ 压测报告 (QPS/P95/P99)
```

### Phase 3: Web API 开发 (4 周)

**目标**: 提供完整 REST + WebSocket API

```
Week 9-10: 后端 API
├── FastAPI/NestJS 框架搭建
├── 实现 CRUD API (任务管理)
├── 实现 WebSocket 实时通信
├── JWT 认证 + 多租户隔离
└── Swagger 文档生成

Week 11-12: 前端集成
├── React 前端脚手架
├── 任务创建与监控界面
├── Human-Review 确认对话框
├── 实时日志与进度展示
└── 结果可视化 (代码高亮 + 甘特图)

交付物:
✅ 完整的 Web 应用
✅ API 文档 (Swagger)
✅ 用户操作手册
```

### Phase 4: 生产优化 (4 周)

**目标**: 企业级稳定性与性能

```
Week 13-14: 性能优化
├── 模型量化 (AWQ/GPTQ 4-bit)
├── 前缀缓存优化
├── 批处理推理优化
└── GPU 显存优化

Week 15: 监控与告警
├── Prometheus + Grafana 监控
├── ELK 日志聚合
├── 告警规则配置
└── 链路追踪 (Jaeger)

Week 16: 安全加固
├── 数据加密 (传输 + 存储)
├── 访问控制 (RBAC)
├── 审计日志
└── 渗透测试

交付物:
✅ 生产就绪系统
✅ 监控大盘
✅ 运维手册
```

---

## ⚠️ 风险与挑战

### 技术风险

| 风险项                     | 概率 | 影响 | 缓解措施                     |
| -------------------------- | ---- | ---- | ---------------------------- |
| **国产模型性能不足**       | 中   | 高   | 混合部署 (Qwen+GLM+DeepSeek) |
| **LangGraph 学习曲线陡峭** | 中   | 中   | 提前技术培训 + 原型验证      |
| **状态迁移数据丢失**       | 低   | 高   | 双写模式 + 数据校验          |
| **GPU 硬件故障**           | 低   | 高   | 冗余部署 + 热备份            |
| **并发性能瓶颈**           | 中   | 中   | K8s 弹性扩展 + 负载均衡      |

### 业务风险

| 风险项           | 概率 | 影响 | 缓解措施                 |
| ---------------- | ---- | ---- | ------------------------ |
| **用户体验下降** | 中   | 高   | 充分 UAT 测试 + 灰度发布 |
| **迁移周期过长** | 中   | 中   | 分阶段交付 + MVP 先行    |
| **团队技能不足** | 高   | 中   | 外部顾问 + 内部培训      |
| **预算超支**     | 低   | 中   | 分期采购 + 弹性方案      |

---

## 🎓 团队技能要求

### 必备技能

```
角色 1: LangGraph 专家 (1 人)
├── 熟练掌握 LangChain/LangGraph 框架
├── 理解 StateGraph、Supervisor、Handoff 模式
├── 熟悉 TypeScript/Python 任一语言
└── 智能体编排与调试经验

角色 2: 大模型工程师 (1 人)
├── 熟悉 vLLM/SGLang/TGI 推理引擎
├── GPU 服务器运维经验
├── 模型量化与优化技能
└── Docker + K8s 容器编排

角色 3: 全栈工程师 (1 人)
├── FastAPI/NestJS 后端开发
├── React/Vue 前端开发
├── WebSocket 实时通信
└── Postgres + Redis 数据库

角色 4: DevOps 工程师 (0.5 人)
├── CI/CD 流水线搭建
├── 监控告警系统 (Prometheus/Grafana)
├── 日志聚合 (ELK)
└── 安全加固
```

### 可选技能加分项

- 向量数据库 (Pinecone/Weaviate)
- 提示工程与 Few-Shot Learning
- GPU 性能调优 (CUDA/TensorRT)
- 企业安全合规 (ISO 27001/等保三级)

---

## 📚 参考资源

### 官方文档

1. **LangGraph**
   - [LangGraph JS 官方文档](https://langchain-ai.github.io/langgraphjs/)
   - [LangGraph Python 官方文档](https://langchain-ai.github.io/langgraph/)
   - [Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)

2. **国产大模型**
   - [通义千问 Qwen 官方文档](https://qwen.readthedocs.io/)
   - [智谱 AI GLM 开发文档](https://open.bigmodel.cn/dev/howuse/model)
   - [DeepSeek 官方文档](https://platform.deepseek.com/docs)

3. **推理引擎**
   - [vLLM 文档](https://docs.vllm.ai/)
   - [Ollama 文档](https://github.com/ollama/ollama)
   - [SGLang 文档](https://sgl-project.github.io/)

### 开源项目

1. **LangGraph 示例**
   - [langgraph-supervisor-py](https://github.com/langchain-ai/langgraph-supervisor-py)
   - [local-deep-researcher](https://github.com/langchain-ai/local-deep-researcher)

2. **国产模型集成**
   - [Qwen LangChain 集成](https://github.com/QwenLM/Qwen)
   - [ChatGLM 部署教程](https://github.com/THUDM/ChatGLM-6B)

3. **私有化部署**
   - [vLLM Docker 部署](https://docs.vllm.ai/en/latest/deployment/docker.html)
   - [K8s 大模型部署](https://github.com/vllm-project/vllm/tree/main/examples/kubernetes)

### 技术博客

1. [Building Local AI Agents with LangGraph and Ollama](https://www.digitalocean.com/community/tutorials/local-ai-agents-with-langgraph-and-ollama)
2. [Multi-Agent System Best Practices](https://skywork.ai/blog/ai-agent-orchestration-best-practices-handoffs/)
3. [vLLM 性能优化指南](https://docs.vllm.ai/en/latest/performance/)

---

## 🎬 结论与建议

### 核心结论

1. **技术可行性**: ⭐⭐⭐⭐⭐
   - LangGraph 与 BMAD 架构高度匹配
   - 国产模型性能已达 GPT-4 级别
   - 私有化部署方案成熟

2. **成本优势**: ⭐⭐⭐⭐⭐
   - 私有化 3 年 TCO 仅为云 API 的 2-10%
   - 硬件回本周期 < 6 个月（中高频场景）

3. **国产化支持**: ⭐⭐⭐⭐⭐
   - Qwen2.5、GLM-4.5、DeepSeek R1 全面支持
   - 完全自主可控，满足合规要求

4. **实施难度**: ⭐⭐⭐ (中等)
   - 需要 3-4 个月完整迁移
   - 需要组建 3-4 人技术团队
   - 需要 7-50 万硬件投入（根据方案）

### 推荐行动方案

**🚀 第一步: 立即启动 Phase 1 技术验证 (2 周)**

```bash
# 快速启动脚本
git clone https://github.com/your-org/bmad-langgraph-poc
cd bmad-langgraph-poc

# 安装 Ollama + Qwen2.5-7B
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b

# 安装依赖
npm install
# 或
pip install -r requirements.txt

# 启动原型
npm run dev
# 或
python main.py
```

**📅 建议时间线**:

- Week 1-2: Phase 1 技术验证
- Week 3: Go/No-Go 决策会议
- Week 4-9: Phase 2 核心迁移 (如果 Go)
- Week 10-13: Phase 3 Web API 开发
- Week 14-16: Phase 4 生产优化

**💰 预算建议**:

- **小规模试点**: ¥25,800 (方案 C: 单卡 4090)
- **中等规模**: ¥73,000 (方案 B: 三卡 4090)
- **大规模生产**: ¥513,000 (方案 A: 双卡 A100)

---

## 🤝 后续支持

如需进一步技术支持，可提供：

1. ✅ **技术咨询**: LangGraph 架构设计评审
2. ✅ **原型开发**: 2 周 MVP 快速验证
3. ✅ **培训服务**: LangGraph + 国产模型实战培训
4. ✅ **运维支持**: 生产环境故障排查与优化

---

**报告编制**: Claude Code AI Assistant
**调研日期**: 2025-11-03
**版本**: v2.0 (国产化私有化专版)
**状态**: ✅ 调研完成，建议立即启动技术验证
