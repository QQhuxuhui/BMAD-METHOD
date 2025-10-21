# 约束模式专家知识库 - Constraint Library

**专家**: 李严谨 (Constraint Expert)
**版本**: V4.2
**用途**: 约束识别、约束建模、约束验证、约束修复

## 知识库结构

```
constraint-library/
├── README.md                    # 本文档
├── capacity/                    # 容量约束
│   ├── resource-capacity.md
│   ├── vehicle-capacity.md
│   └── warehouse-capacity.md
├── temporal/                    # 时间约束
│   ├── time-windows.md
│   ├── precedence.md
│   ├── makespan.md
│   └── deadline.md
├── assignment/                  # 分配约束
│   ├── one-to-one.md
│   ├── many-to-one.md
│   ├── compatibility.md
│   └── exclusivity.md
├── routing/                     # 路径约束
│   ├── connectivity.md
│   ├── visit-once.md
│   └── tour-constraints.md
├── resource/                    # 资源约束
│   ├── availability.md
│   ├── skill-requirements.md
│   └── tool-requirements.md
├── logical/                     # 逻辑约束
│   ├── if-then.md
│   ├── mutual-exclusion.md
│   └── dependency.md
└── domain-specific/             # 领域特定约束
    ├── manufacturing/
    ├── logistics/
    └── service/
```

## 约束分类体系

### 按强制性

| 类型     | 描述                 | 处理方式           | 引用路径                                 |
| -------- | -------------------- | ------------------ | ---------------------------------------- |
| 硬约束   | 必须满足，否则无效   | 直接建模到模型中   | 各分类/\*.md                             |
| 软约束   | 优先满足，违反有惩罚 | 添加到目标函数     | @专家库/约束库/soft-constraints.md       |
| 偏好约束 | 可选满足             | 多目标优化或后处理 | @专家库/约束库/preference-constraints.md |

### 按数学形式

| 形式       | 示例          | 建模方法                 | 引用路径                                |
| ---------- | ------------- | ------------------------ | --------------------------------------- |
| 线性等式   | Σ x_i = b     | 直接添加约束             | @专家库/约束库/linear-equality.md       |
| 线性不等式 | Σ a_i x_i ≤ b | 直接添加约束             | @专家库/约束库/linear-inequality.md     |
| 非线性     | x² + y² ≤ r²  | 线性化或使用非线性求解器 | @专家库/约束库/nonlinear-constraints.md |
| 逻辑约束   | if A then B   | 大M法、指示变量          | @专家库/约束库/logical/if-then.md       |
| 组合约束   | 排列、组合    | 枚举或约束规划           | @专家库/约束库/combinatorial.md         |

### 按领域

| 领域     | 常见约束               | 引用路径                                        |
| -------- | ---------------------- | ----------------------------------------------- |
| 车辆调度 | 容量、时间窗、访问一次 | @专家库/约束库/domain-specific/logistics/\*     |
| 生产调度 | 资源、优先级、工艺流程 | @专家库/约束库/domain-specific/manufacturing/\* |
| 人员排班 | 技能、班次、劳动法规   | @专家库/约束库/domain-specific/service/\*       |
| 项目调度 | 先后关系、资源可用性   | @专家库/约束库/temporal/precedence.md           |

## 约束模板结构

每个约束文件包含：

```markdown
# [约束名称]

**约束ID**: `constraint-id`
**分类**: capacity | temporal | assignment | routing | resource | logical
**数学形式**: linear_equality | linear_inequality | nonlinear | logical

## 约束描述

[自然语言描述约束含义]

## 数学建模

### 符号定义

- x_i: 决策变量
- a_i: 参数

### 约束公式
```

Σ a_i \* x_i ≤ b

````

### 建模注意事项

[特殊考虑]

## Python实现

```python
def add_constraint(model, variables, parameters):
    """
    添加约束到模型

    参数:
        model: 优化模型
        variables: 决策变量
        parameters: 约束参数

    返回:
        constraint: 约束对象
    ```
    # 实现代码
    pass
````

## 验证方法

如何验证约束是否满足：

```python
def validate_constraint(solution, parameters):
    """验证约束"""
    pass
```

## 修复策略

当约束违反时如何修复：

```python
def repair_constraint_violation(solution):
    """修复约束违反"""
    pass
```

## 常见错误

- 错误1: [描述]
- 错误2: [描述]

## 相关约束

- 强化版: @专家库/约束库/.../stronger-version.md
- 松弛版: @专家库/约束库/.../relaxed-version.md

## 示例应用

[实际案例]

````

## 约束识别流程

```mermaid
graph TD
    A[需求描述] --> B{识别约束类型}
    B --> C[容量类]
    B --> D[时间类]
    B --> E[分配类]
    B --> F[逻辑类]

    C --> G[选择具体约束模板]
    D --> G
    E --> G
    F --> G

    G --> H[数学建模]
    H --> I[实现代码]
    I --> J[验证约束]
````

## 使用指南

### 如何识别约束

从需求描述中识别关键词：

| 关键词                    | 对应约束类型 | 引用路径                     |
| ------------------------- | ------------ | ---------------------------- |
| "不能超过"、"最多"        | 容量约束     | @专家库/约束库/capacity/\*   |
| "必须在...之前"、"时间窗" | 时间约束     | @专家库/约束库/temporal/\*   |
| "每个...只能"             | 分配约束     | @专家库/约束库/assignment/\* |
| "如果...则..."            | 逻辑约束     | @专家库/约束库/logical/\*    |
| "需要技能"                | 资源约束     | @专家库/约束库/resource/\*   |
| "访问一次"                | 路径约束     | @专家库/约束库/routing/\*    |

### 引用规范

在TenElementModel的约束元素中引用：

```yaml
3_constraints:
  constraints:
    - constraint_id: 'capacity_1'
      name: '车辆容量约束'
      type: 'capacity'
      hard_or_soft: 'hard'
      citation: '@专家库/约束库/capacity/vehicle-capacity.md'
      mathematical_form: 'linear_inequality'
      description: '车辆装载量不能超过额定容量'
      formula: 'Σ demand_i * x_ij ≤ capacity_j, ∀j'
      parameters:
        capacity_j: '车辆j的额定容量'
        demand_i: '客户i的需求量'

    - constraint_id: 'time_window_1'
      name: '客户时间窗约束'
      type: 'temporal'
      hard_or_soft: 'hard'
      citation: '@专家库/约束库/temporal/time-windows.md'
      mathematical_form: 'linear_inequality'
      description: '必须在客户指定的时间窗内服务'
      formula: 'e_i ≤ arrival_i ≤ l_i, ∀i'
      parameters:
        e_i: '客户i的最早服务时间'
        l_i: '客户i的最晚服务时间'
```

## 约束一致性检查

### 检查冗余约束

```python
def check_redundancy(constraints):
    """检查是否存在冗余约束"""
    # 识别被其他约束蕴含的约束
    pass
```

### 检查矛盾约束

```python
def check_contradiction(constraints):
    """检查是否存在矛盾约束"""
    # 识别不可能同时满足的约束
    pass
```

### 检查完整性

```python
def check_completeness(constraints, problem_description):
    """检查约束是否完整覆盖需求"""
    pass
```

## 约束建模技巧

### 线性化技巧

**非线性转线性**:

- 绝对值: |x| → x ≤ z, -x ≤ z
- 乘积: x \* y → 引入辅助变量
- 最大值/最小值: max(x, y) → z ≥ x, z ≥ y

### 大M法

处理逻辑约束if-then:

```
if binary_var == 1 then constraint_satisfied
→ constraint + M * (1 - binary_var) ≥ 0
```

### 指示变量

引入0-1变量表示条件成立：

```
indicator_var = 1 if condition_holds else 0
```

## 约束强度分析

| 约束强度 | 描述           | 处理策略               |
| -------- | -------------- | ---------------------- |
| 非常强   | 大幅削减可行域 | 优先建模，可能需要分解 |
| 强       | 显著限制可行解 | 标准建模               |
| 中等     | 一定程度限制   | 标准建模               |
| 弱       | 限制较少       | 可考虑松弛或后处理     |

## 知识扩展指南

### 添加新约束模式

1. **确定分类**
   - capacity / temporal / assignment / routing / resource / logical / domain-specific

2. **创建约束文件**
   - 使用标准模板

3. **提供数学建模**
   - 公式
   - 符号定义
   - 建模技巧

4. **实现代码**
   - 添加约束
   - 验证约束
   - 修复约束

5. **更新分类体系**
   - 添加到README
   - 更新决策树

## Token优化

Sidecar模式：

- Agent文件: ~200 tokens
- 按需加载: ~1-3K tokens/约束
- Token节省: 60%

## 质量保证

所有约束模板必须：

- [ ] 有清晰的自然语言描述
- [ ] 提供数学公式
- [ ] 包含Python实现
- [ ] 提供验证方法
- [ ] 标注常见错误
- [ ] 包含示例应用

## 维护日志

| 版本 | 日期       | 变更         |
| ---- | ---------- | ------------ |
| V4.2 | 2025-10-20 | 初始框架创建 |

---

**维护**: 约束专家团队
**BMAD版本**: v6-alpha
**最后更新**: 2025-10-20

**使用此知识库**: 在 `agents/constraint-expert.md` 的 `<critical-actions>` 中自动加载
