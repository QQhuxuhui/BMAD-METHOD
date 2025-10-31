# Task: Generate Code From Solution

**任务ID**: `generate-code-from-solution`
**版本**: V4.4 (重大更新)
**用途**: Phase 3 Step 3.5 - 严格按照用户确认的方案生成可执行代码

## 🔥 V4.4 重大更新说明

**更新日期**: 2025-01-21

**核心变更**:

1. ❌ **移除TODO生成**: 不再生成任何TODO标记
2. ✅ **专家库解析**: 新增步骤0.1，解析专家库提取伪代码
3. ✅ **公式转代码**: 新增步骤0.2，将数学公式转为Python实现
4. ✅ **AI代码生成**: 步骤3.5改用AI根据专家库伪代码生成完整算法
5. ✅ **完整性验证**: 生成的代码100%完整，可直接运行

**依赖新任务**:

- expert-library-parser.md
- formula-to-code-converter.md
- ai-code-generator.md
- validate-code-completeness.md

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

### 2.5 代码必须包含6层引用标记体系（增强）

**新增要求**: 代码必须包含完整的引用标记，支持双向追溯和Workflow验证。

#### 必需的引用层次

1. **文件头部**（Line 1-50）
   - 完整追溯链（方案文档、Hash、数据来源）
   - 代码组成说明（各部分对应方案章节）

2. **模块分隔**（每个大块开头）
   - 章节对应、专家库引用、状态文件字段、置信度

3. **类级引用**（每个类的docstring）
   - 方案章节、TenElementModel元素、字段路径

4. **函数级引用**（关键函数docstring）
   - 方案章节、专家库引用、状态文件、置信度

5. **参数引用**（配置常量注释）
   - 每个参数的方案章节、理由、专家库引用

验证要求：

- Section引用 >= 5处
- 专家库引用 >= 3处
- 状态文件引用存在
- 在Step 3.6.5自动验证

### 3. 只生成代码，不保存文件

本任务**只生成代码内容**，文件保存由后续Step 3.6完成。

```yaml
output_scope:
  generate: true # 生成代码
  save: false # 不保存文件（由Step 3.6负责）
```

## 处理逻辑

### 步骤0.1: 解析专家库指导（新增）

**目的**: 从专家库中提取伪代码、框架代码和实现指导

```python
# 调用 expert-library-parser.md
from expert_library_parser import parse_expert_libraries

def extract_expert_guidance(user_approved_solution, ten_element_model):
    """
    解析专家库，提取算法、约束、目标的实现指导

    Returns:
        expert_guidance: 结构化的专家库指导信息
    """
    # 从方案中提取专家库引用
    algorithm_citation = user_approved_solution['sections']['5_algorithm_selection']['sections']['selected_algorithm'].get('citations', [])[0]

    constraint_citations = []
    for constraint in ten_element_model.get('constraints', []):
        if 'citation' in constraint:
            constraint_citations.append(constraint['citation'])

    objective_citations = []
    for objective in ten_element_model.get('objectives', []):
        if 'citation' in objective:
            objective_citations.append(objective['citation'])

    # 调用专家库解析器
    expert_guidance = parse_expert_libraries(
        algorithm_citation,
        constraint_citations,
        objective_citations
    )

    print("✓ 专家库解析完成")
    return expert_guidance
```

### 步骤0.2: 转换数学公式为代码（新增）

**目的**: 将TenElementModel中的约束公式和目标函数转换为Python代码

```python
# 调用 formula-to-code-converter.md
from formula_to_code_converter import convert_formulas_to_code

def generate_formula_implementations(ten_element_model, expert_guidance):
    """
    将数学公式转换为Python实现代码

    Returns:
        generated_formulas: 包含约束和目标函数的完整代码
    """
    # 调用公式转换器
    generated_formulas = convert_formulas_to_code(
        ten_element_model,
        expert_guidance
    )

    print("✓ 公式转代码转换完成")
    print(f"  - 约束代码: {len(generated_formulas['constraints'])} 个")
    print(f"  - 目标代码: {len(generated_formulas['objectives'])} 个")

    return generated_formulas
```

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

### 步骤1.5: 生成文件头部追溯信息（新增）

```python
from datetime import datetime
import os

def generate_file_header(user_approved_solution, solution_document_path):
    """
    生成文件头部的完整追溯信息

    方案依据: 支持双向追溯和一致性验证
    """
    # 提取方案元数据
    metadata = user_approved_solution.get('metadata', {})
    data_sources = metadata.get('data_sources', {})

    # 提取文件名
    solution_filename = os.path.basename(solution_document_path)

    header = f'''"""
调度优化求解器

╔════════════════════════════════════════════════════════════╗
║ 方案追溯信息                                               ║
╚════════════════════════════════════════════════════════════╝

方案文档: {solution_filename}
  └─ 章节: 完整方案（Section 1-6）
  └─ 路径: {solution_document_path}
  └─ 确认时间: {user_approved_solution.get('approved_at', 'N/A')}

数据来源:
  └─ TenElementModel: {data_sources.get('ten_element_model', {}).get('source_file', 'N/A')}
     └─ Hash: {data_sources.get('ten_element_model', {}).get('hash', 'N/A')}
  └─ 专家分析: {data_sources.get('expert_analyses', {}).get('source_file', 'N/A')}
     └─ Hash: {data_sources.get('expert_analyses', {}).get('hash', 'N/A')}

代码生成:
  └─ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  └─ 生成方式: 基于方案 + 引用专家库

╔════════════════════════════════════════════════════════════╗
║ 代码组成                                                   ║
╚════════════════════════════════════════════════════════════╝

[第1部分] 数据模型
  └─ 方案依据: Section 1.1 决策变量, Section 1.2 参数
  └─ 来源: TenElementModel Element 1, 2

[第2部分] 约束验证
  └─ 方案依据: Section 3.2 约束处理策略
  └─ 专家库: @constraint-library/handling-methods/repair-strategies.md

[第3部分] 目标函数
  └─ 方案依据: Section 4.2 多目标处理
  └─ 专家库: @objective-library/multi-objective/weighted-sum.md

[第4部分] 算法核心
  └─ 方案依据: Section 5.1 算法选择, Section 5.2 参数配置
  └─ 专家库: 引用自专家库（质量评分0.95）
  └─ 代码来源: 引用专家库（非AI生成）

[第5部分] 求解器入口
  └─ 方案依据: Section 6 实现路线图
  └─ 组装: 组合上述1-4部分

"""
'''

    print("✓ 文件头部追溯信息已生成")
    return header
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

#### 3.3 生成约束验证函数（修改：使用已转换的代码）

```python
def generate_constraint_functions(
    ten_element_model,
    constraint_strategy,
    solution_document_path,
    generated_formulas  # 新增参数：来自步骤0.2
):
    """
    基于约束处理策略生成约束验证函数

    方案依据: solution_document Section 3 - 约束处理策略

    ⚠️ 重要变更: 不再生成TODO，直接使用formula-to-code-converter转换的完整代码
    """
    code_lines = []

    code_lines.append('"""')
    code_lines.append('约束验证函数')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 3')
    code_lines.append('约束策略: 硬约束-repair方法, 软约束-penalty方法')
    code_lines.append('代码来源: formula-to-code-converter (完整实现)')
    code_lines.append('"""')
    code_lines.append('')

    # 使用已转换的约束代码（无TODO）
    for constraint_code in generated_formulas['constraints']:
        code_lines.append(constraint_code['code'])
        code_lines.append('')

    print(f"✓ 约束函数代码已集成: {len(generated_formulas['constraints'])} 个（完整实现，无TODO）")

    return "\n".join(code_lines)
```

#### 3.4 生成目标函数（修改：使用已转换的代码）

```python
def generate_objective_functions(
    ten_element_model,
    objective_strategy,
    solution_document_path,
    generated_formulas  # 新增参数：来自步骤0.2
):
    """
    基于目标优化策略生成目标函数

    方案依据: solution_document Section 4 - 目标优化策略

    ⚠️ 重要变更: 不再生成TODO，直接使用formula-to-code-converter转换的完整代码
    """
    code_lines = []

    code_lines.append('"""')
    code_lines.append('目标函数')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 4')
    code_lines.append('TenElementModel: Element 4 - objectives')
    code_lines.append('代码来源: formula-to-code-converter (完整实现)')
    code_lines.append('"""')
    code_lines.append('')

    # 使用已转换的目标函数代码（无TODO）
    for objective_code in generated_formulas['objectives']:
        code_lines.append(objective_code['code'])
        code_lines.append('')

    # 添加聚合目标函数
    code_lines.append(generated_formulas['aggregated_objective'])
    code_lines.append('')

    print(f"✓ 目标函数代码已集成: {len(generated_formulas['objectives'])} 个 + 聚合函数（完整实现，无TODO）")

    return "\n".join(code_lines)
```

#### 3.5 生成算法核心（修改：调用AI代码生成器）

```python
# 调用 ai-code-generator.md
from ai_code_generator import generate_algorithm_implementation

def generate_algorithm_core(
    algorithm_selection,
    solution_document_path,
    expert_guidance,  # 新增参数：来自步骤0.1
    ten_element_model,  # 新增参数
    generated_formulas  # 新增参数：来自步骤0.2
):
    """
    基于算法选择生成算法核心代码

    方案依据: solution_document Section 5 - 算法选择与配置

    ⚠️ 重要变更: 不再生成TODO，调用AI根据专家库伪代码生成完整实现
    """
    selected = algorithm_selection['sections']['selected_algorithm']
    config = algorithm_selection['sections']['algorithm_configuration']
    algorithm_name = selected['algorithm_name']

    print(f"生成算法实现: {algorithm_name}")
    print("  - 基于专家库伪代码")
    print("  - 使用AI生成完整实现")
    print("  - 无TODO，可直接运行")

    # 调用AI代码生成器
    algorithm_code = generate_algorithm_implementation(
        expert_guidance,
        ten_element_model,
        config
    )

    print(f"✓ 算法核心代码已生成: {algorithm_name}（完整实现，无TODO）")

    return algorithm_code
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

## 引用标记生成规范（新增）

### 模块分隔注释模板

在每个代码模块开头添加：

```python
# ══════════════════════════════════════════════════════════════
# 第N部分: 模块名称
# ══════════════════════════════════════════════════════════════
# 方案依据: solution_document Section X.X
# 专家库引用: @xxx-library/yyy/zzz.md
# 状态文件: phase_X_state_xxx.yaml
#   - 字段路径: state_data.xxx.yyy
#   - 置信度: 0.XX
# 生成方式: 引用专家库/AI生成/模板适配
# ══════════════════════════════════════════════════════════════
```

### 类级引用docstring模板

```python
class ClassName:
    """
    类说明

    ┌────────────────────────────────────────────────┐
    │ 方案引用                                       │
    ├────────────────────────────────────────────────┤
    │ 方案文档: Section X.X                          │
    │ 来源: TenElementModel Element X                │
    │ 状态文件: phase_X_state.yaml                   │
    │ 字段路径: state_data.xxx.yyy                   │
    └────────────────────────────────────────────────┘
    """
```

### 函数级引用docstring模板

```python
def function_name():
    """
    函数说明

    ┌────────────────────────────────────────────────┐
    │ 方案引用                                       │
    ├────────────────────────────────────────────────┤
    │ 方案文档: Section X.X                          │
    │ 专家库: @xxx-library/yyy.md                    │
    │ 状态文件: phase_X_state.yaml                   │
    │ 字段路径: state_data.xxx                       │
    │ 置信度: 0.XX                                   │
    └────────────────────────────────────────────────┘
    """
```

### 参数引用注释模板

```python
# 参数名 [方案: Section X.X, 理由: XXX]
# [专家库: @xxx-library/yyy.md]
# [置信度: 0.XX]
PARAMETER_NAME = value
```

### 引用标记验证

生成的代码将在Step 3.6.5自动验证以下内容：

- ✓ 文件头部包含方案追溯信息
- ✓ Section引用 >= 5处
- ✓ 专家库引用 >= 3处
- ✓ 状态文件引用存在
- ✓ 包含置信度信息

## 引用

- @算法专家库/代码生成模板
- @约束专家库/约束实现代码
- @目标专家库/目标函数实现
- @编排协调专家库/代码集成规范
- citation-format-template.md（引用格式规范）

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha  
**核心机制**: 基于方案的代码生成，方案是唯一权威，完整的引用标记体系
