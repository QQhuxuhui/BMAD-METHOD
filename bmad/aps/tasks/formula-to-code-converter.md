# Task: Formula to Code Converter

**任务ID**: `formula-to-code-converter`
**版本**: V5.0
**用途**: Phase 4 Step 4.3 - 将数学公式转换为完整的Python代码实现

---

## 🎯 任务目标

执行智能体，你的任务是：

**将TenElementModel中的约束和目标函数的数学公式，转换为完整、可执行的Python代码。**

生成的代码将用于验证调度方案是否满足约束，以及计算目标函数值。

## 📥 输入

你将收到以下输入：

```yaml
inputs:
  ten_element_model:
    description: 包含约束和目标函数的数学定义
    structure:
      constraints:
        - name: 约束名称
          type: 约束类型（precedence/resource/time_window/capacity等）
          formula: 数学公式（如 "s[i+1] ≥ s[i] + p[i]"）
          description: 约束含义说明
          level: hard/soft（硬约束/软约束）

      objectives:
        - name: 目标函数名称
          type: minimize/maximize
          formula: 数学公式（如 "max(C_i)"）
          description: 目标含义说明
          weight: 权重（多目标时使用）

      decision_variables:
        - name: 决策变量名称
          type: 数据类型
          domain: 定义域
          description: 变量说明

      parameters:
        - name: 参数名称
          type: 数据类型
          source: 数据来源
          description: 参数说明

  expert_guidance:
    description: 专家库指导信息（来自expert-library-parser任务）
    structure:
      relevant_templates:
        - 相关专家库模板路径
      templates:
        template_path: 完整的专家库模板内容（含代码示例）
```

## 🚨 强制要求（MANDATORY）

### 1. 代码必须完整且可执行

**CRITICAL**: 你生成的代码必须是完整实现，绝对禁止：

```yaml
FORBIDDEN:
  - ❌ TODO注释（任何形式）
  - ❌ pass语句（空函数体）
  - ❌ 假数据或占位符（如 fake_data = [1,2,3]）
  - ❌ 硬编码值（如 capacity = 100）
  - ❌ 未定义的属性访问（如 task.unknown_field）

REQUIRED:
  - ✅ 完整的验证逻辑
  - ✅ 完整的错误处理
  - ✅ 完整的边界情况处理
  - ✅ 软约束必须包含repair()和get_penalty()方法
  - ✅ 所有数据从TenElementModel获取
```

### 2. 必须参考专家库实现模式

**CRITICAL**: 在生成代码前，你必须：

1. **研读专家库示例**：从`expert_guidance.templates`中学习代码结构
2. **学习设计模式**：
   - 数据类定义（使用`@dataclass`）
   - Handler类结构（如`TimeWindowConstraintHandler`）
   - 方法命名约定（`validate`, `get_penalty`, `repair`）
   - 返回值格式（`Tuple[bool, List[Dict]]`）

3. **参考这些专家库模板**：
   ```
   bmad/aps/templates/constraint-library/temporal/时间窗约束.md
   bmad/aps/templates/constraint-library/resource/资源约束.md
   bmad/aps/templates/objective-library/optimization/最小化完工时间.md
   ```

### 3. 必须绑定TenElementModel实际数据结构

**CRITICAL**: 生成代码前，你必须：

1. **解析决策变量**：确定每个变量的实际名称、类型、访问方式
2. **解析参数**：确定每个参数的来源和访问方式
3. **绑定数据结构**：生成的代码必须使用实际字段名，不能假设

**示例错误**（旧版本）：

```python
# ❌ 假设solution有tasks属性，假设task有start_time属性
for task in solution.tasks:
    if task.start_time < task.time_window[0]:
        return False
```

**正确做法**（新版本）：

```python
# ✅ 先从TenElementModel确认实际数据结构
# 假设TenElementModel.decision_variables定义了:
# - name: "任务开始时间", symbol: "s_i", access: "schedule[task_id].start"
# - name: "时间窗下限", symbol: "e_i", access: "task_data[task_id].earliest"

for task_id in schedule.keys():
    start_time = schedule[task_id].start
    earliest = task_data[task_id].earliest
    if start_time < earliest:
        return False
```

## 📋 执行步骤

请按以下步骤执行任务：

### 步骤1：研读专家库示例代码

**任务**：从`expert_guidance.templates`中学习代码实现模式。

**操作**：

1. 读取所有相关的专家库模板内容
2. 提取其中的Python代码块
3. 理解以下模式：
   - 数据类如何定义（`@dataclass`）
   - Handler类的结构
   - `validate()`方法的实现逻辑
   - `get_penalty()`和`repair()`方法的实现（软约束）
   - 错误处理和边界情况处理

**输出**：在心中形成"代码模板"，但要根据实际TenElementModel调整。

---

### 步骤2：解析TenElementModel数据结构

**任务**：确定实际的数据结构和访问方式。

**操作**：

1. 列出所有决策变量：

   ```
   决策变量清单：
   - 变量名: 任务开始时间
     符号: s[i]
     类型: float
     访问方式: schedule.get_task(i).start_time

   - 变量名: 机器分配
     符号: x[i,j]
     类型: binary
     访问方式: assignment.is_assigned(task_i, machine_j)
   ```

2. 列出所有参数：

   ```
   参数清单：
   - 参数名: 加工时间
     符号: p[i]
     类型: float
     来源: problem_data.tasks[i].processing_time

   - 参数名: 时间窗
     符号: [e_i, l_i]
     类型: Tuple[float, float]
     来源: problem_data.tasks[i].time_window
   ```

3. 确认数据访问模式（避免假设）。

---

### 步骤3：生成约束验证代码

**任务**：为每个约束生成完整的验证代码。

**代码结构**（参考专家库）：

```python
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class [约束名]Data:
    """约束相关的数据结构"""
    # 根据约束需要定义字段
    pass

class [约束名]ConstraintHandler:
    """
    [约束名]验证处理器

    约束公式: [从TenElementModel.constraints[i].formula获取]
    约束描述: [从TenElementModel.constraints[i].description获取]
    约束类型: [hard/soft]

    ┌────────────────────────────────────────────────┐
    │ 方案引用                                       │
    ├────────────────────────────────────────────────┤
    │ TenElementModel: constraints.[约束名]
    │ 专家库参考: [列出参考的专家库模板]
    │ 数据绑定: [列出使用的决策变量和参数]
    └────────────────────────────────────────────────┘
    """

    def __init__(self, problem_data: ProblemData):
        """
        初始化约束处理器

        Args:
            problem_data: 问题数据（包含参数）
        """
        self.problem_data = problem_data

    def validate(self, solution: Solution) -> Tuple[bool, List[Dict]]:
        """
        验证解是否满足约束

        Args:
            solution: 待验证的解（包含决策变量值）

        Returns:
            (is_valid, violations)
            - is_valid: 是否满足约束（对于硬约束，违反即False）
            - violations: 违反详情列表
        """
        violations = []

        # TODO（你需要生成）: 实现具体的验证逻辑
        # 1. 根据数学公式实现检查
        # 2. 记录违反情况
        # 3. 处理边界情况

        is_valid = len(violations) == 0
        return is_valid, violations

    def get_penalty(self, violations: List[Dict]) -> float:
        """
        计算违反惩罚（仅软约束需要）

        Args:
            violations: 违反详情

        Returns:
            penalty: 惩罚值
        """
        if not violations:
            return 0.0

        # TODO（你需要生成）: 计算惩罚
        penalty = 0.0
        return penalty

    def repair(self, solution: Solution, violations: List[Dict]) -> Solution:
        """
        修复违反（仅软约束需要）

        Args:
            solution: 当前解
            violations: 违反详情

        Returns:
            repaired_solution: 修复后的解
        """
        # TODO（你需要生成）: 实现修复策略
        return solution
```

**你的任务**：

1. 将上述模板中的所有`# TODO（你需要生成）`替换为完整实现
2. 填充所有`pass`语句
3. 根据实际约束调整数据类定义
4. 确保代码语法正确、逻辑完整

---

### 步骤4：生成目标函数代码

**任务**：为每个目标函数生成完整的计算代码。

**代码结构**（参考专家库）：

```python
class [目标名]ObjectiveHandler:
    """
    [目标名]计算处理器

    目标公式: [从TenElementModel.objectives[i].formula获取]
    目标描述: [从TenElementModel.objectives[i].description获取]
    优化方向: [minimize/maximize]

    ┌────────────────────────────────────────────────┐
    │ 方案引用                                       │
    ├────────────────────────────────────────────────┤
    │ TenElementModel: objectives.[目标名]
    │ 专家库参考: [列出参考的专家库模板]
    │ 数据绑定: [列出使用的决策变量和参数]
    └────────────────────────────────────────────────┘
    """

    def __init__(self, problem_data: ProblemData):
        self.problem_data = problem_data

    def calculate(self, solution: Solution) -> float:
        """
        计算目标函数值

        Args:
            solution: 待评估的解

        Returns:
            objective_value: 目标函数值
        """
        # TODO（你需要生成）: 实现目标函数计算
        # 1. 根据数学公式实现
        # 2. 处理边界情况（如空解）
        # 3. 返回数值结果

        return 0.0
```

**你的任务**：

1. 替换所有`# TODO`为完整实现
2. 确保计算逻辑与数学公式一致
3. 处理特殊情况（如除零、空集合等）

---

### 步骤5：生成多目标聚合函数（如果需要）

**任务**：如果有多个目标函数，生成聚合函数。

**代码结构**：

```python
def calculate_aggregated_objective(
    solution: Solution,
    problem_data: ProblemData,
    weights: Dict[str, float]
) -> float:
    """
    多目标聚合函数

    聚合方法: 加权求和
    目标函数: [列出所有目标]
    权重: [列出权重]

    Args:
        solution: 待评估的解
        problem_data: 问题数据
        weights: 目标权重

    Returns:
        aggregated_value: 聚合后的目标值
    """
    # 初始化各目标处理器
    # obj1_handler = Objective1Handler(problem_data)
    # obj2_handler = Objective2Handler(problem_data)

    # 计算各目标值
    # obj1_value = obj1_handler.calculate(solution)
    # obj2_value = obj2_handler.calculate(solution)

    # 归一化和聚合
    # aggregated = weights['obj1'] * normalize(obj1_value) + ...

    # TODO（你需要生成）: 完整实现

    return 0.0
```

---

### 步骤6：自我验证

**任务**：检查生成的代码是否符合要求。

**验证清单**：

```yaml
代码完整性:
  - [ ] 所有约束都已生成代码
  - [ ] 所有目标函数都已生成代码
  - [ ] 没有TODO注释
  - [ ] 没有pass语句（除except中）
  - [ ] 没有假数据或占位符

专家库对齐:
  - [ ] 使用了@dataclass定义数据结构
  - [ ] 使用了Handler类模式
  - [ ] 方法命名符合约定（validate/get_penalty/repair/calculate）
  - [ ] 返回值格式正确

数据结构绑定:
  - [ ] 所有决策变量访问都基于TenElementModel定义
  - [ ] 所有参数访问都基于TenElementModel定义
  - [ ] 没有未定义的属性访问
  - [ ] 数据类型正确

代码质量:
  - [ ] 代码语法正确（可通过compile()测试）
  - [ ] 包含完整的docstring
  - [ ] 包含错误处理
  - [ ] 包含边界情况处理
  - [ ] 包含方案引用标记（┌─┐格式）
```

**验证方法**：

1. 在脑海中执行代码
2. 检查每个变量是否都有定义
3. 检查边界情况（空输入、零值、负值等）
4. 确认返回值类型正确

---

## 📤 输出

生成并输出以下结构：

```python
# ========================================
# Auto-generated by BMAD APS
# Formula to Code Converter V5.0
# DO NOT MODIFY MANUALLY
# ========================================

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# ========== 约束验证代码 ==========

# 约束1: [名称]
[完整的约束验证代码，包括数据类和Handler类]

# 约束2: [名称]
[完整的约束验证代码]

# ...（所有约束）

# ========== 目标函数代码 ==========

# 目标1: [名称]
[完整的目标函数代码]

# 目标2: [名称]
[完整的目标函数代码]

# ...（所有目标）

# ========== 多目标聚合函数 ==========
[如果有多个目标，生成聚合函数]
```

## 🎓 示例参考

### 示例1：时间窗约束（硬约束）

假设TenElementModel定义：

```yaml
constraint:
  name: 时间窗约束
  type: time_window
  formula: 'e_i ≤ s_i ≤ l_i'
  level: hard

decision_variables:
  - name: 开始时间
    symbol: s_i
    access: solution.schedule[task_id].start_time

parameters:
  - name: 最早开始
    symbol: e_i
    access: problem_data.tasks[task_id].earliest_start
  - name: 最晚开始
    symbol: l_i
    access: problem_data.tasks[task_id].latest_start
```

生成的代码应该类似：

```python
@dataclass
class TimeWindow:
    earliest: float
    latest: float

class TimeWindowConstraintHandler:
    """时间窗约束验证"""

    def __init__(self, problem_data):
        self.problem_data = problem_data

    def validate(self, solution):
        violations = []

        for task_id in solution.schedule.keys():
            # 从solution获取决策变量
            start_time = solution.schedule[task_id].start_time

            # 从problem_data获取参数
            earliest = self.problem_data.tasks[task_id].earliest_start
            latest = self.problem_data.tasks[task_id].latest_start

            # 验证公式: e_i ≤ s_i ≤ l_i
            if start_time < earliest or start_time > latest:
                violations.append({
                    'task_id': task_id,
                    'start_time': start_time,
                    'time_window': (earliest, latest),
                    'violation_type': 'out_of_window'
                })

        is_valid = len(violations) == 0
        return is_valid, violations
```

## 📚 质量标准总结

你生成的代码将被以下标准评估：

| 标准     | 要求                          | 检查方式      |
| -------- | ----------------------------- | ------------- |
| 完整性   | 无TODO、无pass、无假数据      | 代码审查      |
| 正确性   | 数学公式与代码逻辑一致        | 逻辑验证      |
| 可执行性 | 语法正确、可通过编译          | compile()测试 |
| 数据绑定 | 使用TenElementModel定义的结构 | 结构对比      |
| 模式对齐 | 遵循专家库的代码模式          | 模式匹配      |
| 文档完整 | 包含docstring和方案引用       | 文档检查      |

---

**记住**：你是代码生成者，不是调用者。直接生成完整、可执行的代码。

**参考但不要复制**：从专家库学习模式，但根据实际TenElementModel调整实现。

**质量优先**：宁可多花时间确保完整，也不要留下TODO或假设。

---

**创建**: 2025-01-21
**更新**: 2025-01-21 (V5.0 直接指导智能体)
**BMAD版本**: v6-alpha
**核心机制**: 智能体直接生成代码，参考专家库，绑定TenElementModel
