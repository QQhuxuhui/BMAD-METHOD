# Task: Generate Code From Solution

**任务ID**: `generate-code-from-solution`
**版本**: V4.3  
**用途**: Phase 3 Step 3.5 - 严格按照用户确认的方案生成可执行代码

## 输入

```yaml
inputs:
  - user_approved_solution: 用户确认后的方案
  - ten_element_model: TenElementModel对象
  - solution_document_path: 方案文档路径（用于引用）
```

## 🚨 强制要求（MANDATORY）

### 1. 严格依据方案生成代码

**CRITICAL**: 代码生成必须严格按照用户确认的方案，每个代码组件都必须有明确的方案依据。

```yaml
code_generation_principle:
  critical: true
  rule: '方案是唯一权威，代码是方案的忠实实现'

  allowed:
    - 按照方案中的算法选择生成代码
    - 按照方案中的约束策略实现验证函数
    - 按照方案中的目标策略实现目标函数
    - 按照方案中的实现路线图组织代码结构

  forbidden:
    - 偏离方案自行决定算法
    - 添加方案中未提及的功能
    - 修改方案中确定的架构
    - 使用与方案不一致的处理策略
```

### 2. 代码必须包含方案引用

每个代码模块、函数、类都必须标注其方案依据：

```python
# ✅ 正确示例
class Task:
    """
    任务类 - 决策变量定义

    方案依据: solution_document Section 1.1 - 决策变量
    TenElementModel: Element 1 - decision_variables
    引用: @TenElementModel/decision_variables/Task
    """
    pass

def validate_precedence_constraint(schedule):
    """
    验证前后关系约束

    方案依据: solution_document Section 3.1 - 约束分类 > 硬约束
    处理策略: solution_document Section 3.2 - 硬约束处理 > repair方法
    引用: @约束专家库/precedence-constraint
    """
    pass
```

### 3. 只生成代码，不保存文件

本任务**只生成代码内容**，文件保存由后续Step 3.6完成。

```yaml
output_scope:
  generate: true # 生成代码
  save: false # 不保存文件（由Step 3.6负责）
```

## 处理逻辑

### 步骤1: 验证输入数据

```python
def validate_inputs(user_approved_solution, ten_element_model, solution_document_path):
    """
    验证输入数据完整性

    Raises:
        ValueError: 数据缺失或不一致

    Returns:
        dict: 验证报告
    """
    validation_report = {
        "all_valid": True,
        "checks": []
    }

    # 验证方案已确认
    if not user_approved_solution.get("approval_status") == "approved":
        raise ValueError("方案未获用户确认，无法生成代码")

    # 验证TenElementModel存在
    if not ten_element_model:
        raise ValueError("TenElementModel缺失")

    # 验证方案文档路径
    import os
    if not os.path.exists(solution_document_path):
        raise ValueError(f"方案文档不存在: {solution_document_path}")

    print("✓ 输入数据验证通过")
    print(f"✓ 方案确认时间: {user_approved_solution.get('approved_at')}")
    print(f"✓ 方案文档: {solution_document_path}")

    return validation_report
```

### 步骤2: 提取代码生成指令

```python
def extract_code_generation_instructions(user_approved_solution):
    """
    从方案中提取代码生成指令

    Returns:
        dict: 代码生成指令
    """
    sections = user_approved_solution['sections']

    generation_instructions = {
        "problem_definition": sections['1_problem_definition'],
        "domain_adaptation": sections['2_domain_adaptation'],
        "constraint_strategy": sections['3_constraint_strategy'],
        "objective_strategy": sections['4_objective_strategy'],
        "algorithm_selection": sections['5_algorithm_selection'],
        "implementation_roadmap": sections['6_implementation_roadmap']
    }

    print("✓ 代码生成指令已提取")
    return generation_instructions
```

### 步骤3: 生成代码组件

#### 3.1 生成导入语句

```python
def generate_imports(algorithm_selection, constraint_strategy):
    """
    基于方案生成导入语句

    方案依据: Section 5 - 算法选择, Section 3 - 约束策略
    """
    imports = []

    # 标准库导入
    imports.append("from datetime import datetime")
    imports.append("from typing import List, Dict, Optional, Tuple")
    imports.append("import copy")
    imports.append("import random")

    # 根据算法选择添加特定导入
    algorithm_name = algorithm_selection['sections']['selected_algorithm']['algorithm_name']
    if "genetic" in algorithm_name.lower():
        imports.append("import numpy as np")
    elif "tabu" in algorithm_name.lower():
        imports.append("from collections import deque")

    # 根据约束策略添加导入
    # ...

    return "\n".join(imports)
```

#### 3.2 生成数据模型类

```python
def generate_data_models(ten_element_model, problem_definition, solution_document_path):
    """
    基于TenElementModel生成数据模型类

    方案依据: solution_document Section 1.1 - 决策变量
              solution_document Section 6.2 - 数据结构设计
    TenElementModel: Element 1 - decision_variables
    """
    code_lines = []

    code_lines.append('"""')
    code_lines.append('数据模型定义')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 1.1 & 6.2')
    code_lines.append('TenElementModel: Element 1 (决策变量), Element 2 (参数)')
    code_lines.append('"""')
    code_lines.append('')

    # 为每个决策变量生成类
    for dv in ten_element_model.get('decision_variables', []):
        code_lines.append(f"class {dv['name']}:")
        code_lines.append(f'    """')
        code_lines.append(f"    {dv['description']}")
        code_lines.append(f'    ')
        code_lines.append(f"    方案依据: solution_document Section 1.1 - {dv['name']}")
        code_lines.append(f"    TenElementModel: decision_variables.{dv['name']}")
        code_lines.append(f"    引用: @TenElementModel/decision_variables/{dv['name']}")
        code_lines.append(f'    """')
        code_lines.append(f"    ")
        code_lines.append(f"    def __init__(self):")

        # 根据decision variable的字段生成属性
        for attr in dv.get('attributes', []):
            code_lines.append(f"        self.{attr['name']} = None  # {attr['description']}")

        code_lines.append('')

    return "\n".join(code_lines)
```

#### 3.3 生成约束验证函数

```python
def generate_constraint_functions(
    ten_element_model,
    constraint_strategy,
    solution_document_path
):
    """
    基于约束处理策略生成约束验证函数

    方案依据: solution_document Section 3 - 约束处理策略
    """
    code_lines = []

    code_lines.append('"""')
    code_lines.append('约束验证函数')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 3')
    code_lines.append('约束策略: 硬约束-repair方法, 软约束-penalty方法')
    code_lines.append('"""')
    code_lines.append('')

    # 硬约束验证
    hard_constraints = constraint_strategy['sections']['constraint_classification']['hard_constraints']

    for hc in hard_constraints:
        func_name = f"validate_{hc.get('name', 'constraint').replace(' ', '_').lower()}"
        code_lines.append(f"def {func_name}(solution):")
        code_lines.append(f'    """')
        code_lines.append(f"    验证约束: {hc.get('description', '')}")
        code_lines.append(f'    ')
        code_lines.append(f"    方案依据: solution_document Section 3.1 - 硬约束")
        code_lines.append(f"    处理策略: solution_document Section 3.2 - repair方法")

        # 获取引用
        citations = constraint_strategy['sections']['handling_methods']['hard_constraint_strategy'].get('citations', [])
        if citations:
            code_lines.append(f"    引用: {citations[0]}")

        code_lines.append(f'    ')
        code_lines.append(f"    Args:")
        code_lines.append(f"        solution: 待验证的解")
        code_lines.append(f'    ')
        code_lines.append(f"    Returns:")
        code_lines.append(f"        bool: 约束是否满足")
        code_lines.append(f'    """')
        code_lines.append(f"    # TODO: 实现约束验证逻辑")
        code_lines.append(f"    pass")
        code_lines.append('')

    # 软约束评估
    soft_constraints = constraint_strategy['sections']['constraint_classification']['soft_constraints']

    for sc in soft_constraints:
        func_name = f"evaluate_{sc.get('name', 'constraint').replace(' ', '_').lower()}_penalty"
        code_lines.append(f"def {func_name}(solution):")
        code_lines.append(f'    """')
        code_lines.append(f"    评估软约束违反惩罚: {sc.get('description', '')}")
        code_lines.append(f'    ')
        code_lines.append(f"    方案依据: solution_document Section 3.1 - 软约束")
        code_lines.append(f"    处理策略: solution_document Section 3.2 - penalty方法")

        # 获取引用
        citations = constraint_strategy['sections']['handling_methods']['soft_constraint_strategy'].get('citations', [])
        if citations:
            code_lines.append(f"    引用: {citations[0]}")

        code_lines.append(f'    ')
        code_lines.append(f"    Returns:")
        code_lines.append(f"        float: 惩罚值")
        code_lines.append(f'    """')
        code_lines.append(f"    # TODO: 实现惩罚计算逻辑")
        code_lines.append(f"    return 0.0")
        code_lines.append('')

    return "\n".join(code_lines)
```

#### 3.4 生成目标函数

```python
def generate_objective_functions(
    ten_element_model,
    objective_strategy,
    solution_document_path
):
    """
    基于目标优化策略生成目标函数

    方案依据: solution_document Section 4 - 目标优化策略
    """
    code_lines = []

    code_lines.append('"""')
    code_lines.append('目标函数')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 4')
    code_lines.append('TenElementModel: Element 4 - objectives')
    code_lines.append('"""')
    code_lines.append('')

    # 主目标函数
    primary_obj = objective_strategy['sections']['objective_hierarchy']['primary_objective']

    code_lines.append(f"def calculate_primary_objective(solution):")
    code_lines.append(f'    """')
    code_lines.append(f"    计算主目标: {primary_obj.get('name', '')}")
    code_lines.append(f"    {primary_obj.get('description', '')}")
    code_lines.append(f'    ')
    code_lines.append(f"    方案依据: solution_document Section 4.1 - 主目标")
    code_lines.append(f"    TenElementModel: objectives.{primary_obj.get('name', '')}")
    code_lines.append(f'    ')
    code_lines.append(f"    Returns:")
    code_lines.append(f"        float: 目标值")
    code_lines.append(f'    """')
    code_lines.append(f"    # TODO: 实现主目标计算")
    code_lines.append(f"    pass")
    code_lines.append('')

    # 次要目标函数
    secondary_objs = objective_strategy['sections']['objective_hierarchy']['secondary_objectives']

    for sec_obj in secondary_objs:
        func_name = f"calculate_{sec_obj.get('name', 'objective').replace(' ', '_').lower()}"
        code_lines.append(f"def {func_name}(solution):")
        code_lines.append(f'    """')
        code_lines.append(f"    计算次要目标: {sec_obj.get('name', '')}")
        code_lines.append(f'    ')
        code_lines.append(f"    方案依据: solution_document Section 4.1 - 次要目标")
        code_lines.append(f'    """')
        code_lines.append(f"    # TODO: 实现次要目标计算")
        code_lines.append(f"    pass")
        code_lines.append('')

    # 多目标聚合函数
    multi_obj = objective_strategy['sections']['multi_objective_handling']

    code_lines.append(f"def calculate_aggregated_objective(solution):")
    code_lines.append(f'    """')
    code_lines.append(f"    聚合多目标")
    code_lines.append(f'    ')
    code_lines.append(f"    方案依据: solution_document Section 4.2 - 多目标处理")
    code_lines.append(f"    方法: {multi_obj['approach']}")
    code_lines.append(f"    权重: {multi_obj['weights']}")
    code_lines.append(f'    ')
    code_lines.append(f"    引用:")
    for cite in multi_obj.get('citations', []):
        code_lines.append(f"        - {cite}")
    code_lines.append(f'    """')
    code_lines.append(f"    primary = calculate_primary_objective(solution)")
    code_lines.append(f"    ")
    code_lines.append(f"    # TODO: 根据权重聚合所有目标")
    code_lines.append(f"    return primary")
    code_lines.append('')

    return "\n".join(code_lines)
```

#### 3.5 生成算法核心

```python
def generate_algorithm_core(
    algorithm_selection,
    solution_document_path
):
    """
    基于算法选择生成算法核心代码

    方案依据: solution_document Section 5 - 算法选择与配置
    """
    code_lines = []

    selected = algorithm_selection['sections']['selected_algorithm']
    config = algorithm_selection['sections']['algorithm_configuration']

    algorithm_name = selected['algorithm_name']

    code_lines.append('"""')
    code_lines.append(f'{algorithm_name} 算法实现')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 5')
    code_lines.append(f'算法选择: {algorithm_name}')
    code_lines.append(f'选择理由: {selected["selection_rationale"]}')
    code_lines.append('引用:')
    for cite in selected.get('citations', []):
        code_lines.append(f'    - {cite}')
    code_lines.append('"""')
    code_lines.append('')

    # 算法类
    class_name = algorithm_name.replace(' ', '').replace('-', '')
    code_lines.append(f"class {class_name}:")
    code_lines.append(f'    """')
    code_lines.append(f"    {algorithm_name} 求解器")
    code_lines.append(f'    ')
    code_lines.append(f"    方案依据: solution_document Section 5.1 & 5.2")
    code_lines.append(f'    """')
    code_lines.append(f"    ")
    code_lines.append(f"    def __init__(self):")
    code_lines.append(f"        # 算法参数配置")
    code_lines.append(f"        # 方案依据: solution_document Section 5.2 - 算法配置")

    # 参数
    for param_name, param_value in config.get('parameters', {}).items():
        justification = config.get('parameter_justification', {}).get(param_name, '')
        code_lines.append(f"        self.{param_name} = {param_value}  # {justification}")

    code_lines.append('')
    code_lines.append(f"    def solve(self, problem_data):")
    code_lines.append(f'        """')
    code_lines.append(f"        求解入口")
    code_lines.append(f'        ')
    code_lines.append(f"        Args:")
    code_lines.append(f"            problem_data: 问题数据")
    code_lines.append(f'        ')
    code_lines.append(f"        Returns:")
    code_lines.append(f"            解决方案")
    code_lines.append(f'        """')
    code_lines.append(f"        # TODO: 实现{algorithm_name}算法")
    code_lines.append(f"        pass")
    code_lines.append('')

    return "\n".join(code_lines)
```

#### 3.6 生成主求解器

```python
def generate_main_solver(
    ten_element_model,
    algorithm_selection,
    solution_document_path
):
    """
    生成主求解器入口

    方案依据: solution_document Section 6 - 实现路线图
    """
    code_lines = []

    algorithm_name = algorithm_selection['sections']['selected_algorithm']['algorithm_name']
    class_name = algorithm_name.replace(' ', '').replace('-', '')

    code_lines.append('"""')
    code_lines.append('主求解器入口')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 6')
    code_lines.append('"""')
    code_lines.append('')

    code_lines.append(f"def solve_scheduling_problem(input_data_path, output_path):")
    code_lines.append(f'    """')
    code_lines.append(f"    调度问题求解主函数")
    code_lines.append(f'    ')
    code_lines.append(f"    方案依据: solution_document Section 6 - 实现路线图")
    code_lines.append(f"    TenElementModel: Element 9 (输入数据), Element 10 (输出格式)")
    code_lines.append(f'    ')
    code_lines.append(f"    Args:")
    code_lines.append(f"        input_data_path: 输入数据路径")
    code_lines.append(f"        output_path: 输出路径")
    code_lines.append(f'    """')
    code_lines.append(f"    print('开始求解...')")
    code_lines.append(f"    ")
    code_lines.append(f"    # 1. 加载数据")
    code_lines.append(f"    # 方案依据: TenElementModel Element 9")
    code_lines.append(f"    problem_data = load_input_data(input_data_path)")
    code_lines.append(f"    ")
    code_lines.append(f"    # 2. 初始化求解器")
    code_lines.append(f"    # 方案依据: solution_document Section 5")
    code_lines.append(f"    solver = {class_name}()")
    code_lines.append(f"    ")
    code_lines.append(f"    # 3. 求解")
    code_lines.append(f"    solution = solver.solve(problem_data)")
    code_lines.append(f"    ")
    code_lines.append(f"    # 4. 输出结果")
    code_lines.append(f"    # 方案依据: TenElementModel Element 10")
    code_lines.append(f"    save_solution(solution, output_path)")
    code_lines.append(f"    ")
    code_lines.append(f"    print('求解完成！')")
    code_lines.append(f"    return solution")
    code_lines.append('')

    return "\n".join(code_lines)
```

### 步骤4: 组装完整代码

```python
from datetime import datetime

def assemble_complete_code(
    imports,
    data_models,
    constraint_functions,
    objective_functions,
    algorithm_core,
    main_solver,
    user_approved_solution,
    solution_document_path
):
    """
    组装完整的Python代码文件

    Returns:
        str: 完整代码
    """
    code = []

    # ====== 文件头部 ======
    code.append('"""')
    code.append('调度优化求解器')
    code.append('')
    code.append(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    code.append(f'方案文档: {solution_document_path}')
    code.append(f'方案确认: {user_approved_solution.get("approved_at")}')
    code.append('')
    code.append('本代码严格按照用户确认的方案生成')
    code.append('每个组件都标注了对应的方案依据和引用')
    code.append('')
    code.append('架构:')
    code.append('  1. 数据模型 - 基于TenElementModel')
    code.append('  2. 约束验证 - 基于约束处理策略')
    code.append('  3. 目标函数 - 基于目标优化策略')
    code.append('  4. 算法核心 - 基于算法选择')
    code.append('  5. 求解器入口 - 基于实现路线图')
    code.append('"""')
    code.append('')

    # ====== 导入 ======
    code.append(imports)
    code.append('')
    code.append('')

    # ====== 数据模型 ======
    code.append('# ' + '='*70)
    code.append('# 数据模型')
    code.append('# ' + '='*70)
    code.append('')
    code.append(data_models)
    code.append('')

    # ====== 约束验证 ======
    code.append('# ' + '='*70)
    code.append('# 约束验证函数')
    code.append('# ' + '='*70)
    code.append('')
    code.append(constraint_functions)
    code.append('')

    # ====== 目标函数 ======
    code.append('# ' + '='*70)
    code.append('# 目标函数')
    code.append('# ' + '='*70)
    code.append('')
    code.append(objective_functions)
    code.append('')

    # ====== 算法核心 ======
    code.append('# ' + '='*70)
    code.append('# 算法核心')
    code.append('# ' + '='*70)
    code.append('')
    code.append(algorithm_core)
    code.append('')

    # ====== 求解器入口 ======
    code.append('# ' + '='*70)
    code.append('# 求解器入口')
    code.append('# ' + '='*70)
    code.append('')
    code.append(main_solver)
    code.append('')

    # ====== Main ======
    code.append('if __name__ == "__main__":')
    code.append('    # 示例使用')
    code.append('    solve_scheduling_problem("input_data.json", "output/")')
    code.append('')

    return "\n".join(code)
```

### 步骤5: 生成代码可追溯性映射

```python
def generate_code_traceability(
    user_approved_solution,
    ten_element_model,
    solution_document_path
):
    """
    生成代码与方案的可追溯性映射

    Returns:
        dict: 可追溯性映射
    """
    traceability = {
        "solution_document": solution_document_path,
        "approved_at": user_approved_solution.get("approved_at"),
        "mappings": {
            "data_models": {
                "source": "solution_document Section 1.1 & 6.2",
                "ten_element_model": "Element 1 (decision_variables), Element 2 (parameters)",
                "code_components": ["class Task", "class Resource", "..."]
            },
            "constraint_functions": {
                "source": "solution_document Section 3",
                "strategy": "硬约束-repair, 软约束-penalty",
                "code_components": ["validate_*", "evaluate_*_penalty"]
            },
            "objective_functions": {
                "source": "solution_document Section 4",
                "ten_element_model": "Element 4 (objectives)",
                "code_components": ["calculate_primary_objective", "calculate_aggregated_objective"]
            },
            "algorithm_core": {
                "source": "solution_document Section 5",
                "algorithm": user_approved_solution['sections']['5_algorithm_selection']['sections']['selected_algorithm']['algorithm_name'],
                "code_components": ["class TabuSearch", "solve()"]
            },
            "main_solver": {
                "source": "solution_document Section 6",
                "ten_element_model": "Element 9 (input_data), Element 10 (output_format)",
                "code_components": ["solve_scheduling_problem()"]
            }
        }
    }

    return traceability
```

### 步骤6: 生成代码元数据

```python
def generate_code_metadata(implementation_code, user_approved_solution):
    """
    生成代码元数据

    Returns:
        dict: 代码元数据
    """
    code_metadata = {
        "generated_at": datetime.now().isoformat(),
        "solution_approved_at": user_approved_solution.get("approved_at"),
        "code_statistics": {
            "total_lines": len(implementation_code.split('\n')),
            "code_size_bytes": len(implementation_code.encode('utf-8'))
        },
        "algorithm": user_approved_solution['sections']['5_algorithm_selection']['sections']['selected_algorithm']['algorithm_name'],
        "language": "Python",
        "version": "3.8+"
    }

    return code_metadata
```

## 输出

```yaml
outputs:
  implementation_code:
    type: string
    description: 生成的完整Python代码
    format: 'UTF-8编码的Python源文件内容'

  code_metadata:
    type: object
    description: 代码元数据
    structure:
      generated_at: string (ISO8601)
      solution_approved_at: string (ISO8601)
      code_statistics:
        total_lines: integer
        code_size_bytes: integer
      algorithm: string
      language: string
      version: string

  code_traceability:
    type: object
    description: 代码与方案的可追溯性映射
    structure:
      solution_document: string (文件路径)
      approved_at: string (ISO8601)
      mappings: object (详细映射关系)
```

## 质量检查

- [ ] 代码严格按照方案生成
- [ ] 每个组件都有方案依据标注
- [ ] 使用方案中确定的算法
- [ ] 使用方案中确定的约束策略
- [ ] 使用方案中确定的目标策略
- [ ] 代码结构符合实现路线图
- [ ] 所有引用都清晰标注
- [ ] 代码可追溯性完整
- [ ] 代码语法正确（Python 3.8+）

## 引用

- @算法专家库/代码生成模板
- @约束专家库/约束实现代码
- @目标专家库/目标函数实现
- @编排协调专家库/代码集成规范

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha  
**核心机制**: 基于方案的代码生成，方案是唯一权威
