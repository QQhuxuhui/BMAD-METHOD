# V4.0 架构设计

**三层分离架构：DSL层 → 编译层 → 执行层**

---

## 🏗️ 架构总览

### 设计哲学

**关注点分离 (Separation of Concerns)**

```
业务逻辑（What） → DSL 层（YAML）
转换逻辑（How）  → 编译层（Compiler）
执行逻辑（Run）  → 运行层（Runtime）
```

**优势**：

- **易于维护**：修改任何一层不影响其他层
- **易于测试**：每层可独立测试
- **易于扩展**：新增功能只需扩展相应层
- **易于优化**：可针对性优化某一层

---

## 📐 三层架构详解

### Layer 1: BMAD DSL 层（开发层）

#### 职责

- 定义智能体工作流的**业务逻辑**
- 提供**声明式配置**接口
- 管理**知识库**和**模板**

#### 核心组件

```
bmad/
├── aps/                          # APS 模块示例
│   ├── workflow.yaml            # 工作流定义（核心）
│   ├── config.yaml              # 全局配置
│   ├── agents/                  # 智能体定义
│   │   ├── orchestrator.md      # 总指挥
│   │   ├── algorithm-expert.md  # 算法专家
│   │   └── ...                  # 其他专家
│   ├── tasks/                   # 可复用任务
│   │   ├── analyze.md
│   │   ├── validate.md
│   │   └── ...
│   └── templates/               # 知识库
│       ├── algorithm-library/
│       ├── domain-library/
│       └── ...
```

#### workflow.yaml 结构

```yaml
# 元信息
workflow_id: 'aps-scheduling'
version: '4.4.1'
description: '完整调度优化流程'

# 全局配置
config:
  interaction_mode: 'auto'
  human_in_loop: true
  quality_gates_enabled: true

# Phase 定义
phases:
  - phase_id: 'phase-1'
    phase_name: '需求分析'
    steps:
      - step_id: '1.1'
        name: '深度理解'
        action: 'exec' # 动作类型
        target: 'tasks/analyze.md' # 目标文件
        inputs: [user_request] # 输入
        outputs: [analysis] # 输出

      - step_id: '1.2'
        action: 'human_confirmation'
        trigger_level: 'P1'
        inputs: [analysis]
        outputs: [confirmed]

# 输出定义
outputs:
  deliverables:
    - ten_element_model
    - complete_code
```

#### 特点

- ✅ **人类可读**：业务人员也能理解
- ✅ **版本可控**：Git 友好
- ✅ **易于维护**：修改配置即可
- ✅ **知识分离**：业务逻辑与技术实现分离

---

### Layer 2: 编译打包层（转换层）

#### 职责

- 将 YAML 配置**编译**为 Python 代码
- **验证**配置合法性
- **优化**生成代码
- 提供**调试**信息

#### 核心模块

```
bmad_compiler/
├── parser.py           # YAML 解析器
├── analyzer.py         # 语义分析器
├── generators/         # 代码生成器
│   ├── state.py        # State Schema 生成
│   ├── nodes.py        # Node Functions 生成
│   ├── edges.py        # Edge Connections 生成
│   └── graph.py        # Graph Assembly 生成
├── validator.py        # 验证器
├── optimizer.py        # 优化器
└── emitter.py          # 代码输出器
```

#### 编译流程

```
[输入] workflow.yaml
  ↓
┌─────────────────┐
│ 1. Parser       │ 解析 YAML → AST
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. Analyzer     │ 语义分析、类型检查
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. Generator    │ 生成 Python AST
│   - State       │
│   - Nodes       │
│   - Edges       │
│   - Graph       │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. Optimizer    │ 代码优化
│   - 去重        │
│   - 内联        │
│   - 缓存        │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. Validator    │ 验证生成代码
└────────┬────────┘
         ↓
┌─────────────────┐
│ 6. Emitter      │ 输出文件
└────────┬────────┘
         ↓
[输出] generated_graph.py + 配套文件
```

#### 生成物

```
generated/
├── {workflow_id}_graph.py       # 主图定义
├── {workflow_id}_state.py       # State Schema
├── {workflow_id}_nodes.py       # 所有节点函数
├── {workflow_id}_config.json    # 运行时配置
├── {workflow_id}_manifest.json  # 构建清单
└── {workflow_id}_debug.log      # 调试日志
```

#### 特点

- ✅ **自动化**：一键编译
- ✅ **一致性**：统一的代码风格
- ✅ **可优化**：编译时优化
- ✅ **可调试**：提供完整调试信息

---

### Layer 3: 自研 LangGraph 框架（执行层）

#### 职责

- **执行**编译后的工作流
- 提供 BMAD **特有功能**（.md 执行、@引用等）
- **状态管理**和**持久化**
- **监控**和**日志**

#### 核心模块

```
bmad_runtime/
├── executor.py         # BMadExecutor - .md 文件执行
├── state_manager.py    # BMadStateManager - 状态管理
├── guardrails.py       # BMadGuardrails - 强约束
├── human_loop.py       # BMadHumanLoop - 人机交互
├── knowledge_base.py   # BMadKnowledgeBase - @引用
└── checkpointer.py     # BMadCheckpointer - YAML 格式

bmad_langgraph/         # LangGraph 扩展
├── nodes.py            # 自定义节点类型
├── edges.py            # 自定义边类型
├── tools.py            # 工具集成
└── monitors.py         # 监控集成
```

#### 运行时架构

```
┌─────────────────────────────────────┐
│   Generated Graph (编译产物)        │
│   import BMadExecutor, BMadRuntime  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   BMAD Runtime Extensions           │
│   ┌──────────────────────────────┐  │
│   │ BMadExecutor                 │  │
│   │  - 加载 .md 文件             │  │
│   │  - 解析 XML Agent 定义        │  │
│   │  - 处理 @引用                │  │
│   │  - 调用 LLM                  │  │
│   └──────────────────────────────┘  │
│   ┌──────────────────────────────┐  │
│   │ BMadStateManager             │  │
│   │  - Phase 状态保存/加载        │  │
│   │  - 验证状态完整性            │  │
│   └──────────────────────────────┘  │
│   ┌──────────────────────────────┐  │
│   │ BMadGuardrails               │  │
│   │  - 引用检查                  │  │
│   │  - 偏离检测                  │  │
│   │  - 质量门禁                  │  │
│   └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   LangGraph Core (第三方)           │
│   - StateGraph                      │
│   - Checkpointer                    │
│   - Send API / interrupt()          │
└─────────────────────────────────────┘
```

#### 特点

- ✅ **高性能**：基于成熟的 LangGraph
- ✅ **BMAD 特性**：完整支持 BMAD 独有功能
- ✅ **生产级**：监控、日志、容错完备
- ✅ **易部署**：基于 LangServe 快速部署

---

## 🔄 端到端数据流

### 完整示例：从 YAML 到执行

#### 输入：workflow.yaml

```yaml
phases:
  - phase_id: 'phase-1'
    steps:
      - step_id: '1.1'
        action: 'exec'
        target: 'tasks/analyze.md'
        inputs: [user_request]
        outputs: [analysis]
```

#### 编译过程

```python
# ===== 步骤 1: Parser =====
ast = {
    'phases': [{
        'phase_id': 'phase-1',
        'steps': [{
            'step_id': '1.1',
            'action': 'exec',
            'target': 'tasks/analyze.md',
            'inputs': ['user_request'],
            'outputs': ['analysis']
        }]
    }]
}

# ===== 步骤 2: Analyzer =====
analyzed = {
    'state_fields': ['user_request', 'analysis'],
    'nodes': [{'id': 'step_1_1', 'type': 'exec', ...}],
    'edges': [('START', 'step_1_1'), ('step_1_1', 'END')]
}

# ===== 步骤 3: Generator =====
# 生成 State Schema
class Phase1State(TypedDict):
    user_request: str
    analysis: Optional[Dict]

# 生成 Node Function
def step_1_1(state: Phase1State, config: RunnableConfig):
    executor = BMadExecutor()
    result = executor.execute_md(
        path="tasks/analyze.md",
        inputs={"user_request": state["user_request"]},
        config=config
    )
    return {"analysis": result}

# 生成 Graph
builder = StateGraph(Phase1State)
builder.add_node("step_1_1", step_1_1)
builder.add_edge(START, "step_1_1")
builder.add_edge("step_1_1", END)
graph = builder.compile()
```

#### 运行时执行

```python
# 用户调用
result = graph.invoke({
    "user_request": "我需要优化配送路线"
})

# 内部流程
# 1. LangGraph 调用 step_1_1 节点
# 2. step_1_1 调用 BMadExecutor.execute_md()
# 3. BMadExecutor 执行以下步骤:
#    a. 加载 tasks/analyze.md
#    b. 解析文件内容（包括 XML）
#    c. 处理 @引用（如有）
#    d. 构建 Prompt
#    e. 调用 LLM
#    f. 解析输出
#    g. 验证 Guardrails
#    h. 返回结果
# 4. 结果返回给 LangGraph
# 5. LangGraph 更新 State
# 6. 继续下一个节点（如有）
```

---

## 🎨 设计模式

### 1. Visitor 模式（编译器）

```python
class YAMLVisitor:
    def visit_workflow(self, workflow):
        # 访问 workflow 节点
        pass

    def visit_phase(self, phase):
        # 访问 phase 节点
        pass

    def visit_step(self, step):
        # 访问 step 节点
        pass
```

### 2. Strategy 模式（Executor）

```python
class ActionStrategy:
    def execute(self, step, state): pass

class ExecStrategy(ActionStrategy):
    def execute(self, step, state):
        return self.executor.execute_md(...)

class HumanConfirmationStrategy(ActionStrategy):
    def execute(self, step, state):
        return self.human_loop.request_confirmation(...)
```

### 3. Repository 模式（State Manager）

```python
class StateRepository:
    def save(self, phase_id, state): pass
    def load(self, phase_id): pass
    def exists(self, phase_id): pass
```

### 4. Chain of Responsibility（Guardrails）

```python
class GuardrailChain:
    def __init__(self):
        self.checks = [
            CitationCheck(),
            DeviationCheck(),
            QualityGateCheck()
        ]

    def validate(self, output):
        for check in self.checks:
            if not check.validate(output):
                return False
        return True
```

---

## 📊 架构优势

### 1. 可维护性

| 场景             | 传统单体架构   | V4.0 三层架构        |
| ---------------- | -------------- | -------------------- |
| **修改业务逻辑** | 改 Python 代码 | 改 YAML 配置         |
| **优化性能**     | 改代码重测试   | 编译器优化，自动应用 |
| **新增功能**     | 改多处代码     | 扩展一层即可         |
| **团队协作**     | 冲突频繁       | 各层独立开发         |

### 2. 可测试性

```
DSL 层测试:
  - YAML 格式验证
  - 业务逻辑正确性（人工审查）

编译层测试:
  - 单元测试（每个模块）
  - 集成测试（端到端编译）
  - 生成代码验证（类型检查、语法检查）

运行层测试:
  - Executor 单元测试
  - State Manager 单元测试
  - 端到端集成测试
```

### 3. 可扩展性

```
新增 action 类型:
  1. DSL 层：定义新的 action 名称
  2. 编译层：扩展 Generator
  3. 运行层：实现新的 Strategy

成本：低（只需扩展，不需修改现有代码）
```

### 4. 性能优化

```
编译时优化:
  - 常量折叠
  - 死代码消除
  - 函数内联
  - 批处理合并

运行时优化:
  - 缓存（知识库、模板）
  - 并行执行（Send API）
  - 懒加载（按需加载模块）
```

---

## 🔐 架构保证

### 类型安全

```python
# 编译器生成的代码保证类型安全

from typing import TypedDict

class State(TypedDict):
    user_request: str
    analysis: dict

# mypy 检查通过
```

### 错误处理

```python
# 每个生成的节点都有完整错误处理

def step_1_1(state: State, config: RunnableConfig) -> State:
    try:
        result = executor.execute_md(...)
        return {"analysis": result}
    except FileNotFoundError:
        log.error("Task file not found: ...")
        raise
    except LLMError as e:
        log.error(f"LLM execution failed: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise
```

### 监控埋点

```python
# 自动生成监控代码

@monitor(name="step_1_1", phase="phase-1")
def step_1_1(state: State, config: RunnableConfig) -> State:
    start_time = time.time()
    try:
        result = executor.execute_md(...)
        metrics.record("step_1_1", "success", time.time() - start_time)
        return {"analysis": result}
    except Exception as e:
        metrics.record("step_1_1", "error", time.time() - start_time)
        raise
```

---

## 📝 总结

### 核心设计原则

1. **关注点分离**：业务、转换、执行各司其职
2. **声明式优先**：用 YAML 描述 What，不是 How
3. **编译时保证**：尽可能在编译时发现问题
4. **运行时优化**：基于成熟的 LangGraph 引擎
5. **易于扩展**：新增功能成本低

### 架构评分

| 维度         | 评分       | 说明              |
| ------------ | ---------- | ----------------- |
| **可维护性** | ⭐⭐⭐⭐⭐ | YAML 配置易于维护 |
| **可测试性** | ⭐⭐⭐⭐⭐ | 每层可独立测试    |
| **可扩展性** | ⭐⭐⭐⭐⭐ | 扩展成本低        |
| **性能**     | ⭐⭐⭐⭐   | 与手写代码持平    |
| **学习曲线** | ⭐⭐⭐⭐   | YAML 易学         |

**总体评价**: ⭐⭐⭐⭐⭐ **五星架构**

---

**文档版本**: V1.0
**创建日期**: 2025-11-03
**状态**: ✅ 完成
