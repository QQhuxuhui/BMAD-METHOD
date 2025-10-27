# Task: Generate Code From YAML

**任务ID**: `generate-code-from-yaml`
**版本**: V4.3
**用途**: 从YAML格式的方案数据独立生成代码，支持跳过完整workflow直接从方案生成代码

## 输入

```yaml
inputs:
  - solution_data_path: 方案数据YAML文件路径
    example: 'aps-outputs/docs/solution_data_20251024_143530.yaml'
```

## 🚨 强制要求（MANDATORY）

### 1. 只需YAML文件即可生成代码

**CRITICAL**: 本任务支持独立使用，只需提供方案YAML文件，即可生成完整代码。

```yaml
独立使用场景:
  - 跳过Phase 0-3.4，直接从已有方案生成代码
  - 修改方案后重新生成代码
  - 基于外部导入的方案生成代码
  - 调试和测试代码生成逻辑
```

### 2. 与generate-code-from-solution.md一致

生成的代码必须与完整workflow中的代码生成保持一致：

- 相同的引用标记体系
- 相同的代码结构
- 相同的专家库引用机制

## 处理逻辑

### 步骤1: 加载YAML方案数据

```python
import yaml
import os

def load_solution_data_from_yaml(solution_data_path):
    """
    从YAML文件加载方案数据

    Returns:
        dict: 方案数据（包含所有必需信息）
    """
    if not os.path.exists(solution_data_path):
        raise FileNotFoundError(f"方案数据文件不存在: {solution_data_path}")

    # 读取YAML文件
    with open(solution_data_path, 'r', encoding='utf-8') as f:
        solution_data = yaml.safe_load(f)

    # 验证必需字段
    required_fields = [
        "solution_metadata",
        "solution_sections",
        "ten_element_model",
        "references",
        "citations_summary"
    ]

    missing_fields = []
    for field in required_fields:
        if field not in solution_data or solution_data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"YAML文件缺少必需字段: {missing_fields}")

    print(f"✓ YAML方案数据已加载: {solution_data_path}")
    print(f"✓ 包含字段: {list(solution_data.keys())}")

    return solution_data
```

### 步骤2: 重构为标准输入格式

```python
def restructure_solution_data(solution_data):
    """
    将YAML数据重构为代码生成所需的标准格式

    Returns:
        dict: 重构后的数据
    """
    # 构造user_approved_solution对象
    user_approved_solution = {
        "metadata": solution_data.get("solution_metadata", {}),
        "sections": solution_data.get("solution_sections", {}),
        "references": solution_data.get("references", {}),
        "traceability": solution_data.get("traceability", {}),
        "citations_summary": solution_data.get("citations_summary", {}),
        "approval_status": "approved",  # 标记为已确认
        "approved_at": solution_data.get("solution_metadata", {}).get("generated_at", "")
    }

    # 提取TenElementModel
    ten_element_model = solution_data.get("ten_element_model", {})

    # 提取方案文档路径（如果有）
    solution_document_path = solution_data.get("references", {}).get("solution_document_path", "")

    print("✓ 数据已重构为标准格式")
    return {
        "user_approved_solution": user_approved_solution,
        "ten_element_model": ten_element_model,
        "solution_document_path": solution_document_path
    }
```

### 步骤3: 调用代码生成逻辑

```python
def generate_code_from_yaml_data(restructured_data):
    """
    基于YAML数据生成代码

    复用 generate-code-from-solution.md 的逻辑

    Returns:
        dict: 代码生成结果
    """
    user_approved_solution = restructured_data["user_approved_solution"]
    ten_element_model = restructured_data["ten_element_model"]
    solution_document_path = restructured_data["solution_document_path"]

    # 以下逻辑与 generate-code-from-solution.md 完全相同

    # 1. 生成文件头部
    file_header = generate_file_header(user_approved_solution, solution_document_path)

    # 2. 提取代码生成指令
    generation_instructions = extract_code_generation_instructions(user_approved_solution)

    # 3. 生成各代码组件
    imports = generate_imports(generation_instructions["algorithm_selection"],
                              generation_instructions["constraint_strategy"])

    data_models = generate_data_models(ten_element_model,
                                      generation_instructions["problem_definition"],
                                      solution_document_path)

    constraint_functions = generate_constraint_functions(ten_element_model,
                                                        generation_instructions["constraint_strategy"],
                                                        solution_document_path)

    objective_functions = generate_objective_functions(ten_element_model,
                                                       generation_instructions["objective_strategy"],
                                                       solution_document_path)

    algorithm_core = generate_algorithm_core(generation_instructions["algorithm_selection"],
                                            solution_document_path)

    main_solver = generate_main_solver(ten_element_model,
                                      generation_instructions["algorithm_selection"],
                                      solution_document_path)

    # 4. 组装完整代码
    implementation_code = assemble_complete_code(
        file_header,
        imports,
        data_models,
        constraint_functions,
        objective_functions,
        algorithm_core,
        main_solver,
        user_approved_solution,
        solution_document_path
    )

    # 5. 生成代码追溯性
    code_traceability = generate_code_traceability(
        user_approved_solution,
        ten_element_model,
        solution_document_path
    )

    # 6. 生成代码元数据
    code_metadata = generate_code_metadata(implementation_code, user_approved_solution)

    print("✓ 代码生成完成（从YAML方案数据）")

    return {
        "implementation_code": implementation_code,
        "code_metadata": code_metadata,
        "code_traceability": code_traceability
    }
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

  code_traceability:
    type: object
    description: 代码与方案的可追溯性映射
```

## 使用场景

### 场景1: 独立代码生成

```bash
# 已有方案文件，直接生成代码
输入: solution_data_20251024_143530.yaml
输出: 完整的Python代码

优势:
  • 跳过Phase 0-3.4
  • 快速迭代
  • 调试方便
```

### 场景2: 方案修改后重新生成

```bash
# 手动修改方案YAML
# 重新生成代码
输入: solution_data_modified.yaml
输出: 基于修改后方案的代码
```

### 场景3: 外部方案导入

```bash
# 从其他项目导入方案
输入: external_solution_data.yaml
输出: 代码
```

## 与完整workflow的关系

```
完整Workflow:
  Phase 0-3.4 → solution_data.yaml + solution_document.md
  Phase 3.5 → generate-code-from-solution.md

独立使用:
  solution_data.yaml → generate-code-from-yaml.md → 代码

  跳过: Phase 0-3.4
  保持: 相同的代码质量和结构
```

## 质量检查

- [ ] YAML文件存在且可读
- [ ] YAML包含所有必需字段
- [ ] 重构为标准格式成功
- [ ] 生成的代码包含6层引用标记
- [ ] 代码结构与完整workflow一致
- [ ] 专家库引用正确

## 引用

- generate-code-from-solution.md（复用代码生成逻辑）
- @编排协调专家库/代码生成规范

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 从YAML方案数据独立生成代码，支持灵活调试和迭代
