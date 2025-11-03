# LangChain Skill

这是 LangChain 开发助手 skill，用于帮助开发者使用 LangChain 框架构建 LLM 应用。

## 能力范围

### 核心组件

- **LLM 集成**: 支持多种 LLM 提供商（OpenAI、Anthropic、HuggingFace 等）
- **Prompt 模板**: 创建和管理提示词模板
- **Chain**: 构建复杂的调用链
- **Memory**: 实现对话记忆和上下文管理
- **Agents**: 创建具有工具使用能力的智能代理
- **Tools**: 集成外部工具和 API

### 数据处理

- **Document Loaders**: 加载各种格式的文档
- **Text Splitters**: 文本分割和处理
- **Embeddings**: 文本向量化
- **Vector Stores**: 向量数据库集成（Chroma, Pinecone, FAISS 等）
- **Retrievers**: 信息检索和 RAG 实现

### 输出处理

- **Output Parsers**: 结构化输出解析
- **Callbacks**: 回调和日志处理
- **Streaming**: 流式响应处理

## 使用方式

当用户询问以下问题时，自动激活此 skill：

1. **开发问题**
   - "如何使用 LangChain 创建..."
   - "LangChain 中的 XXX 怎么实现..."
   - "帮我写一个 LangChain 的..."

2. **架构设计**
   - "设计一个 RAG 系统..."
   - "如何构建多轮对话..."
   - "Agent 工具集成方案..."

3. **问题诊断**
   - "LangChain 报错..."
   - "为什么我的 chain 不工作..."
   - "如何优化 LangChain 性能..."

## 参考资源

**官方文档**: https://docs.langchain.com

### 重要文档链接

- 快速开始: https://docs.langchain.com/docs/get_started/quickstart
- Chains: https://docs.langchain.com/docs/modules/chains/
- Agents: https://docs.langchain.com/docs/modules/agents/
- Memory: https://docs.langchain.com/docs/modules/memory/
- RAG: https://docs.langchain.com/docs/use_cases/question_answering/

## 技术栈支持

- **Python**: 主要支持语言
- **JavaScript/TypeScript**: LangChain.js 支持
- **集成框架**: FastAPI, Streamlit, Gradio 等

## 最佳实践

1. **使用 LCEL (LangChain Expression Language)** 构建现代化的 chain
2. **合理使用缓存**减少 LLM 调用成本
3. **实现错误处理和重试机制**
4. **使用 Callbacks** 进行调试和监控
5. **向量数据库选择**根据规模和需求选择合适的向量存储

## 注意事项

- 始终检查 LangChain 版本兼容性
- 注意 API 密钥的安全管理
- 考虑 token 使用成本
- 实现适当的错误处理和超时机制
- 对敏感数据进行脱敏处理

## 示例场景

### 基础 LLM 调用

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template("告诉我关于{topic}的信息")
chain = prompt | llm
result = chain.invoke({"topic": "人工智能"})
```

### RAG 系统

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
```

### Agent 工具集成

```python
from langchain.agents import create_openai_functions_agent
from langchain.tools import Tool

tools = [
    Tool(name="Calculator", func=calculator, description="用于数学计算"),
    Tool(name="Search", func=search, description="搜索信息")
]
agent = create_openai_functions_agent(llm, tools, prompt)
```

## 更新日志

- 当前支持 LangChain v0.1.x 版本
- 重点关注 LCEL 新语法
- 支持最新的 OpenAI 和 Anthropic API
