# V4.0 分阶段实施详细指南

**方案A实操手册：从轻适配到完整工厂**

> 💡 **核心原则**：先做最小可行方案（Phase 1），验证效果后再决定是否继续

---

## 📚 文档概览

本文档是V4.0分阶段实施的**实操手册**，提供每个阶段的详细步骤、代码示例和决策标准。

**推荐阅读顺序**：

1. Phase 0 → Phase 1 → 决策点1（**80%场景到此结束**）
2. 仅在Phase 1不足时，继续阅读Phase 2-3

---

## 🎯 Phase 0: 痛点确认（Week 1）

### 目标

明确核心痛点，避免过度设计。

### Day 1-2: 现状评估

#### 1.1 BMAD架构分析

**任务**: 理解当前BMAD架构

```bash
# 检查BMAD版本
cat package.json | grep version

# 查看核心模块
ls bmad/aps/

# 确认workflow引擎
cat bmad/aps/agents/orchestrator.md | grep -A 5 "workflow"
```

**产出**:

- [ ] 当前BMAD版本: **\_**
- [ ] 使用的模型: **\_**
- [ ] workflow引擎: workflow.xml or 其他?
- [ ] 主要痛点: **\_**

#### 1.2 痛点列表

**模板**:

| 痛点           | 影响程度 | 频率   | 优先级 |
| -------------- | -------- | ------ | ------ |
| 不支持国产模型 | 高       | 每天   | P0     |
| 开发效率低     | 中       | 每周   | P1     |
| 无法独立部署   | 高       | 一次性 | P2     |
| ...            | ...      | ...    | ...    |

**关键问题**:

- 最痛的Top 3是什么？
- 哪些痛点是**必须立即解决**的？
- 哪些痛点可以通过**简单方案**解决？

---

### Day 3: 痛点确认

#### 3.1 核心痛点识别

**常见痛点分类**：

**类型A: 模型问题**（80%场景）

- ❌ 不支持国产模型（Qwen/GLM/DeepSeek）
- ❌ API调用成本高
- ❌ 数据隐私问题

→ **解决方案**: Phase 1 轻适配器 ✅

**类型B: 部署问题**

- ❌ 无法离线部署
- ❌ 依赖外部服务

→ **解决方案**: Docker化 + Phase 1 ✅

**类型C: 效率问题**（仅大规模场景）

- ❌ 开发智能体太慢（年开发30+个）
- ❌ 代码复用困难

→ **解决方案**: Phase 1+2+3（需谨慎评估）

#### 3.2 预期目标

**SMART目标模板**：

```
具体（Specific）: 支持Qwen模型，BMAD正常运行
可衡量（Measurable）: 3周内完成，成本<3人周
可实现（Achievable）: 基于成熟的LangChain
相关性（Relevant）: 解决国产化要求
时限性（Time-bound）: 2025-11-30前上线
```

---

### Day 4-5: 方案选择

#### 5.1 决策矩阵

| 方案            | 解决痛点  | 工作量  | 风险 | ROI     | 推荐度     |
| --------------- | --------- | ------- | ---- | ------- | ---------- |
| **V3.0**        | 模型      | 1-2周   | 极低 | 立即    | ⭐⭐⭐⭐⭐ |
| **Phase 1**     | 模型+集成 | 2-3周   | 低   | 立即    | ⭐⭐⭐⭐⭐ |
| **Phase 1+2**   | +编译器   | 7-10周  | 中   | 3-6月   | ⭐⭐⭐⭐   |
| **Phase 1+2+3** | +完整     | 25-30周 | 中   | 18-36月 | ⭐⭐⭐     |

#### 5.2 选择建议

**如果核心痛点是国产模型支持** → **选择 Phase 1** ✅

**如果还需要编译器（批量开发）** → 先做Phase 1，再评估

---

### Phase 0 产出

- ✅ **现状分析报告**（1-2页PPT）
- ✅ **痛点列表**（优先级排序）
- ✅ **Phase 1实施计划**
- ✅ **成功标准定义**

---

## 🚀 Phase 1: 轻适配器（Week 2-4）⭐⭐⭐⭐⭐

### 目标

用2-3周时间，让BMAD支持国产模型。

### Week 2: 模型适配层开发

#### 2.1 环境准备

```bash
# 创建Python虚拟环境
conda create -n bmad-langgraph python=3.11
conda activate bmad-langgraph

# 安装依赖
pip install langchain langchain-community
pip install dashscope  # 通义千问
pip install zhipuai    # 智谱GLM
```

#### 2.2 模型适配器实现

**文件**: `bmad_adapter/model_adapter.py`

```python
"""
BMAD模型适配器 - 支持国产模型
"""
from typing import Optional
from langchain_community.llms import Tongyi
from langchain_community.chat_models import ChatGLM


class BMADModelAdapter:
    """统一的模型适配器"""

    def __init__(
        self,
        model_type: str = "qwen",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        初始化模型适配器

        Args:
            model_type: 模型类型 (qwen | glm | deepseek)
            api_key: API密钥
            base_url: 自定义API地址（用于私有化部署）
        """
        self.model_type = model_type

        if model_type == "qwen":
            self.model = Tongyi(
                dashscope_api_key=api_key,
                model_name="qwen-plus"
            )
        elif model_type == "glm":
            self.model = ChatGLM(
                api_key=api_key,
                model="glm-4"
            )
        elif model_type == "deepseek":
            # DeepSeek使用OpenAI兼容接口
            from langchain_community.llms import OpenAI
            self.model = OpenAI(
                api_key=api_key,
                base_url=base_url or "https://api.deepseek.com/v1"
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    def invoke(self, prompt: str, **kwargs) -> str:
        """
        调用模型

        Args:
            prompt: 输入提示词
            **kwargs: 额外参数（temperature, max_tokens等）

        Returns:
            模型响应文本
        """
        return self.model.invoke(prompt, **kwargs)

    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """异步调用"""
        return await self.model.ainvoke(prompt, **kwargs)


# 便捷函数
def create_model(model_type: str = "qwen", **kwargs):
    """创建模型实例"""
    return BMADModelAdapter(model_type=model_type, **kwargs)
```

#### 2.3 配置管理

**文件**: `bmad_adapter/config.py`

```python
"""配置管理"""
import os
from typing import Dict


class ModelConfig:
    """模型配置"""

    # 从环境变量或配置文件加载
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")
    GLM_API_KEY = os.getenv("GLM_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

    # 默认模型
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen")

    @classmethod
    def get_model_config(cls, model_type: str) -> Dict:
        """获取模型配置"""
        configs = {
            "qwen": {"api_key": cls.QWEN_API_KEY},
            "glm": {"api_key": cls.GLM_API_KEY},
            "deepseek": {"api_key": cls.DEEPSEEK_API_KEY},
        }
        return configs.get(model_type, {})
```

#### 2.4 单元测试

**文件**: `tests/test_model_adapter.py`

```python
"""模型适配器测试"""
import pytest
from bmad_adapter.model_adapter import BMADModelAdapter


def test_qwen_adapter():
    """测试通义千问适配器"""
    adapter = BMADModelAdapter(model_type="qwen")
    response = adapter.invoke("你好，请介绍一下你自己")
    assert len(response) > 0
    assert isinstance(response, str)


def test_glm_adapter():
    """测试智谱GLM适配器"""
    adapter = BMADModelAdapter(model_type="glm")
    response = adapter.invoke("1+1=?")
    assert "2" in response


@pytest.mark.asyncio
async def test_async_invoke():
    """测试异步调用"""
    adapter = BMADModelAdapter(model_type="qwen")
    response = await adapter.ainvoke("Hello")
    assert len(response) > 0
```

---

### Week 3: BMAD集成

#### 3.1 集成策略

**方案**: 在BMAD的agent执行流程中注入模型适配器

```python
"""
BMAD集成模块
"""
from bmad_adapter.model_adapter import create_model


class BMADAgentExecutor:
    """BMAD Agent执行器"""

    def __init__(self, model_type: str = "qwen"):
        self.model = create_model(model_type)

    def execute_agent(self, agent_md_path: str, inputs: dict) -> str:
        """
        执行BMAD Agent（.md文件）

        Args:
            agent_md_path: agent文件路径
            inputs: 输入参数

        Returns:
            Agent执行结果
        """
        # 读取.md文件
        with open(agent_md_path, 'r', encoding='utf-8') as f:
            agent_content = f.read()

        # 提取prompt（简化版，实际需要解析XML）
        prompt = self._build_prompt(agent_content, inputs)

        # 调用模型
        response = self.model.invoke(prompt)

        return response

    def _build_prompt(self, agent_content: str, inputs: dict) -> str:
        """构建最终prompt"""
        # 简化版：直接替换变量
        prompt = agent_content
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt
```

#### 3.2 端到端测试

```python
"""端到端测试"""
def test_bmad_workflow():
    """测试BMAD workflow"""
    executor = BMADAgentExecutor(model_type="qwen")

    # 测试单个agent
    result = executor.execute_agent(
        agent_md_path="bmad/aps/agents/analyzer.md",
        inputs={"user_request": "优化物流配送路线"}
    )

    assert len(result) > 0
    print(f"Agent执行结果: {result}")
```

---

### Week 4: 文档与交付

#### 4.1 使用文档

**文件**: `docs/model-adapter-guide.md`

```markdown
# BMAD模型适配器使用指南

## 快速开始

1. 安装依赖
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. 配置API密钥
   \`\`\`bash
   export QWEN_API_KEY="your-api-key"
   \`\`\`

3. 使用模型
   \`\`\`python
   from bmad_adapter import create_model

   model = create_model("qwen")
   response = model.invoke("你好")
   \`\`\`

## 支持的模型

- 通义千问（qwen）
- 智谱GLM（glm）
- DeepSeek（deepseek）

## 常见问题

Q: 如何切换模型？
A: 设置环境变量 \`DEFAULT_MODEL=glm\`
```

#### 4.2 性能测试

```python
"""性能基准测试"""
import time
from bmad_adapter import create_model


def benchmark_model(model_type: str, num_requests: int = 10):
    """性能测试"""
    model = create_model(model_type)

    start_time = time.time()
    for i in range(num_requests):
        model.invoke(f"测试请求 {i+1}")
    end_time = time.time()

    avg_latency = (end_time - start_time) / num_requests
    print(f"{model_type} 平均延迟: {avg_latency:.2f}s")


# 运行测试
benchmark_model("qwen")
benchmark_model("glm")
```

---

### Phase 1 成功标准

- ✅ **功能完整**：支持至少2个国产模型
- ✅ **性能达标**：延迟<3秒（P95）
- ✅ **稳定可靠**：无明显bug，测试覆盖率>80%
- ✅ **易于使用**：文档完善，团队培训完成
- ✅ **可维护**：代码规范，有单元测试

---

## 🔴 决策点1（Week 4末）

### 评估问题

#### 1. Phase 1是否解决了核心痛点？

**评估标准**：

| 原痛点         | Phase 1解决程度 | 说明                  |
| -------------- | --------------- | --------------------- |
| 不支持国产模型 | ✅ 完全解决     | Qwen/GLM可用          |
| API调用成本高  | ✅ 完全解决     | 使用自己的API密钥     |
| 数据隐私问题   | ✅ 完全解决     | 本地/私有化部署       |
| 开发效率低     | ⚠️ 部分解决     | 仍需手写代码          |
| 批量生产慢     | ❌ 未解决       | 需要编译器（Phase 2） |

#### 2. 团队反馈

**问卷调查**：

```
1. 你对Phase 1方案的满意度？（1-5分）
   □ 1 □ 2 □ 3 □ 4 □ 5

2. Phase 1是否满足当前需求？
   □ 完全满足 → 停止
   □ 基本满足 → 停止
   □ 不满足 → 继续评估

3. 如果需要继续，主要原因是？
   □ 开发效率仍然太低
   □ 需要批量生产能力
   □ 需要更好的代码复用
   □ 其他: _____
```

#### 3. ROI分析

**Phase 1 成本**：

```
开发成本: 2-3周 × 2人 = 4-6人周
维护成本: 2人天/月
总成本: 约6人周（首年）
```

**Phase 1 收益**：

```
支持国产模型: ✅ 立即见效
降低API成本: 节省XX元/月
数据隐私: ✅ 合规要求
团队满意度: 提升XX%
```

**ROI**: **立即见效**，无需等待

---

### 决策

**🟢 推荐停止（80%场景）**

**条件**：

- ✅ Phase 1解决了核心痛点
- ✅ 团队满意度高
- ✅ 智能体数量<30个/年

**行动**：

- 停止Phase 2开发
- 使用Phase 1方案
- 定期回顾（每季度）

---

**🟡 继续Phase 2（20%场景）**

**条件**：

- ⚠️ Phase 1确实不够用
- ⚠️ 年开发智能体≥30个
- ⚠️ 管理层批准额外投入

**行动**：

- 进入Phase 2评估
- 制定Phase 2实施计划
- 明确Phase 2成功标准

---

## ⚠️ Phase 2: 编译器POC（Week 5-10）

> **前提**: 已完成Phase 1，且决策点1决定继续

### 目标

验证YAML→Python编译器的可行性和ROI。

### Week 5-6: YAML解析器

#### 核心功能

```python
"""YAML解析器"""
import yaml
from typing import Dict, List


class WorkflowParser:
    """workflow.yaml解析器"""

    def parse(self, yaml_path: str) -> Dict:
        """解析workflow.yaml"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)

        return {
            "workflow_id": workflow.get("workflow_id"),
            "phases": self._parse_phases(workflow.get("phases", [])),
            "steps": self._parse_steps(workflow.get("steps", []))
        }

    def _parse_phases(self, phases: List) -> List[Dict]:
        """解析phases"""
        return phases

    def _parse_steps(self, steps: List) -> List[Dict]:
        """解析steps"""
        return steps
```

### Week 7-8: 代码生成器

```python
"""代码生成器"""
class CodeGenerator:
    """Python代码生成器"""

    def generate(self, workflow: Dict) -> str:
        """生成Python代码"""
        code = "# Auto-generated by BMAD Compiler\n\n"
        code += "from langgraph.graph import StateGraph\n\n"

        # 生成状态定义
        code += self._generate_state(workflow)

        # 生成节点函数
        code += self._generate_nodes(workflow)

        # 生成图构建
        code += self._generate_graph(workflow)

        return code

    def _generate_state(self, workflow: Dict) -> str:
        """生成State类"""
        return '''
class State(TypedDict):
    """工作流状态"""
    user_request: str
    analysis: str
    result: str
'''

    def _generate_nodes(self, workflow: Dict) -> str:
        """生成节点函数"""
        nodes = ""
        for step in workflow["steps"]:
            nodes += f'''
def step_{step["step_id"]}(state: State) -> State:
    """执行步骤 {step["step_id"]}"""
    # TODO: 实现步骤逻辑
    return state
'''
        return nodes

    def _generate_graph(self, workflow: Dict) -> str:
        """生成图构建代码"""
        return '''
# 构建工作流图
workflow = StateGraph(State)

# 添加节点
workflow.add_node("step_1", step_1)

# 添加边
workflow.set_entry_point("step_1")
workflow.set_finish_point("step_1")

# 编译
app = workflow.compile()
'''
```

### Week 9: POC演示

**演示内容**：

1. 手写workflow.yaml（50行）
2. 运行编译器生成Python代码（200行）
3. 执行生成的代码
4. 对比手写vs编译的效率

**成功标准**：

- ✅ YAML能正确生成Python代码
- ✅ 生成的代码可运行
- ✅ 开发效率提升≥2x

---

## 🔴 决策点2（Week 10）

### ROI验证

**Phase 2 投入**：

```
额外投入: 4-6周 × 3人 = 12-18人周
累计投入: 16-24人周
```

**预期收益**：

```
每个智能体节省: 1.5天
年开发智能体: _____ 个
年节省: _____ × 1.5天 = _____ 人天
```

**回本计算**：

```
回本智能体数 = 16-24人周 ÷ (1.5天/5天/周)
            = 16-24 ÷ 0.3
            ≈ 53-80个智能体
```

### 决策

**🟢 停止Phase 3（推荐）**

**条件**：

- ✅ 年开发智能体<50个
- ✅ Phase 2 POC满足需求

**行动**：

- 使用Phase 1+2方案
- 优化POC代码
- 生产环境试运行

---

**🟡 继续Phase 3（仅超大规模）**

**条件**：

- ⚠️ 年开发智能体≥50个
- ⚠️ Phase 2验证成功
- ⚠️ 预算充足（额外18-26周）

**行动**：

- 进入Phase 3开发
- 详见原完整方案文档

---

## 📊 总结对比

| 阶段        | 投入     | 产出         | ROI回本点 | 推荐场景            |
| ----------- | -------- | ------------ | --------- | ------------------- |
| **Phase 1** | 2-3周    | 国产模型支持 | 立即      | **80%场景终点** ✅  |
| **Phase 2** | +4-6周   | 编译器POC    | 50-80个   | 中大规模（30-50个） |
| **Phase 3** | +18-26周 | 完整工厂     | 80-120个  | 超大规模（50+个）   |

---

## 🎯 最佳实践

### 成功要素

1. **严格把控决策点**
   - 不要因为"已经投入了"而继续
   - 每个阶段独立评估ROI
   - 80%场景在Phase 1停止是成功！

2. **快速迭代**
   - Phase 1: 2周MVP + 1周优化
   - 不要追求完美，先跑通流程
   - 根据反馈快速调整

3. **团队沟通**
   - 每周进度同步
   - 决策点前组织评审会
   - 记录决策理由

4. **文档先行**
   - 先写使用文档
   - 再写代码
   - 文档即设计

### 常见陷阱

❌ **陷阱1**: 直接开始Phase 3

- **后果**: 投入20-24周，最后发现Phase 1就够了
- **避免**: 严格遵循分阶段流程

❌ **陷阱2**: Phase 1做得太复杂

- **后果**: 2-3周变成6-8周
- **避免**: MVP原则，先跑通最小流程

❌ **陷阱3**: 没有明确成功标准

- **后果**: 无法判断是否继续
- **避免**: Phase开始前定义成功标准

❌ **陷阱4**: 忽略团队反馈

- **后果**: 开发出来没人用
- **避免**: 每周收集反馈，快速调整

---

## 📞 支持与反馈

**问题咨询**：

- 参考主文档: [README.md](./README.md)
- 审查报告: [07-review-findings.md](./07-review-findings.md)

**进度跟踪**：

- 使用项目管理工具（Jira/Trello）
- 每周进度报告
- 决策点评审会

---

**维护者**: BMAD-LangGraph Integration Team
**最后更新**: 2025-11-04
**文档版本**: V1.0
