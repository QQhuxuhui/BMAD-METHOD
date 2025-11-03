# Task: Validate Element-Code Mapping

**任务ID**: `validate-element-code-mapping`
**版本**: V1.0 (V4.4新增)
**用途**: Phase 3 Step 3.6.3 - 验证生成的代码是否覆盖了所有十要素

## 背景

这是P0改进项的核心验证机制。在V4.4之前，虽然代码会调用TenElementModel，但没有强制验证每个Element是否都有对应的代码实现，导致Element 9数据加载模块缺失等问题。

本任务建立**十要素→代码的强制映射验证**，确保：

1. 每个Element都有对应的代码组件
2. 代码与TenElementModel完全一致
3. 防止Element缺失或遗漏

## 输入

```yaml
inputs:
  - implementation_code: 生成的完整代码
  - ten_element_model: TenElementModel对象
  - solution_document_path: 方案文档路径（用于报告）
```

## 🚨 强制映射表

### Element → Code 映射规则

```yaml
element_to_code_mapping:
  Element_1_decision_variables:
    required_patterns:
      - 'class\s+\w+.*:'
      - 'def __init__'
    validation_rule: '每个decision_variable必须有对应的class定义'
    min_count: "len(ten_element_model['decision_variables'])"

  Element_2_parameters:
    required_patterns:
      - 'class\s+\w+.*:'
      - '@dataclass'
    validation_rule: '参数必须在数据模型中定义'
    min_count: 1

  Element_3_constraints:
    required_patterns:
      - 'def\s+(validate|check|verify)_.*constraint'
      - 'def\s+evaluate_.*penalty'
    validation_rule: '每个constraint必须有对应的验证或惩罚函数'
    min_count: "len(ten_element_model['constraints'])"

  Element_4_objectives:
    required_patterns:
      - 'def\s+calculate_.*objective'
      - 'def\s+evaluate_.*'
    validation_rule: '每个objective必须有对应的计算函数'
    min_count: "len(ten_element_model['objectives'])"

  Element_5_algorithm:
    required_patterns:
      - 'class\s+\w*(Solver|Algorithm|Optimizer)'
      - 'def\s+solve'
    validation_rule: '必须有算法求解器类和solve方法'
    min_count: 1

  Element_9_input_data:
    required_patterns:
      - 'def\s+load_\w+'
      - 'load_all_input_data'
      - 'pd\.read_csv|pd\.read_json|pd\.read_excel'
    validation_rule: '每个data source必须有对应的load函数'
    min_count: "len(ten_element_model['input_data'].get('sources', []))"

  Element_10_output_format:
    required_patterns:
      - 'def\s+save_'
      - '\.to_csv|\.to_json|\.to_excel'
    validation_rule: '必须有输出保存函数'
    min_count: 1
```

## 处理逻辑

### 步骤1: 验证Element 1 - 决策变量

```python
import re

def validate_element_1_decision_variables(implementation_code, ten_element_model):
    """
    验证决策变量是否在代码中有对应的class定义

    Returns:
        dict: 验证结果
    """
    decision_variables = ten_element_model.get('decision_variables', [])

    result = {
        "element": "Element_1_decision_variables",
        "expected_count": len(decision_variables),
        "found_count": 0,
        "missing_items": [],
        "passed": True
    }

    print(f"\n[Element 1] 验证决策变量 (期望 {len(decision_variables)} 个):")

    for dv in decision_variables:
        dv_name = dv.get('name', '')

        # 检查是否有对应的类定义或属性
        # 匹配模式: class XXX 或 self.XXX
        patterns = [
            f"class\\s+{dv_name}",
            f"self\\.{dv_name}",
            f"{dv_name}\\s*:",  # 字典键或类型注解
            f"'{dv_name}'",     # 字符串形式
        ]

        found = False
        for pattern in patterns:
            if re.search(pattern, implementation_code, re.IGNORECASE):
                found = True
                break

        if found:
            result["found_count"] += 1
            print(f"  ✓ {dv_name}")
        else:
            result["missing_items"].append(dv_name)
            result["passed"] = False
            print(f"  ✗ {dv_name} (未找到)")

    print(f"  找到 {result['found_count']}/{result['expected_count']} 个决策变量")

    return result
```

### 步骤2: 验证Element 9 - 输入数据（重点）

```python
def validate_element_9_input_data(implementation_code, ten_element_model):
    """
    验证每个数据源是否有对应的加载函数

    这是P0修复的核心验证点

    Returns:
        dict: 验证结果
    """
    input_data = ten_element_model.get('input_data', {})
    data_sources = input_data.get('sources', [])

    result = {
        "element": "Element_9_input_data",
        "expected_count": len(data_sources),
        "found_count": 0,
        "missing_items": [],
        "passed": True,
        "critical": True  # 标记为关键验证
    }

    print(f"\n[Element 9] 验证输入数据加载 (期望 {len(data_sources)} 个数据源):")

    # 首先检查是否有load_all_input_data函数
    has_load_all = bool(re.search(r'def\s+load_all_input_data', implementation_code))

    if has_load_all:
        print("  ✓ load_all_input_data() 函数存在")
    else:
        result["passed"] = False
        result["missing_items"].append("load_all_input_data")
        print("  ✗ load_all_input_data() 函数缺失 [CRITICAL]")

    # 检查每个数据源是否有对应的load函数
    for source in data_sources:
        file_path = source.get('file_path', '')
        file_name = file_path.split('/')[-1].replace('.csv', '').replace('.json', '').replace('.xlsx', '')

        # 可能的函数名模式
        patterns = [
            f"def\\s+load_{file_name}",
            f"def\\s+load_.*{file_name}",
            f"'{file_name}'.*pd\\.read",
        ]

        found = False
        for pattern in patterns:
            if re.search(pattern, implementation_code, re.IGNORECASE):
                found = True
                break

        if found:
            result["found_count"] += 1
            print(f"  ✓ {file_name} 数据加载函数")
        else:
            result["missing_items"].append(file_name)
            result["passed"] = False
            print(f"  ✗ {file_name} 数据加载函数缺失 [CRITICAL]")

    # 检查是否使用了pandas读取函数
    has_read_functions = bool(re.search(r'pd\.(read_csv|read_json|read_excel)', implementation_code))

    if not has_read_functions:
        result["passed"] = False
        print("  ✗ 未找到pandas数据读取函数 [WARNING]")

    print(f"  找到 {result['found_count']}/{result['expected_count']} 个数据源加载函数")

    return result
```

### 步骤3: 验证Element 3 - 约束

```python
def validate_element_3_constraints(implementation_code, ten_element_model):
    """
    验证约束是否有对应的验证或惩罚函数

    Returns:
        dict: 验证结果
    """
    constraints = ten_element_model.get('constraints', [])

    result = {
        "element": "Element_3_constraints",
        "expected_count": len(constraints),
        "found_count": 0,
        "missing_items": [],
        "passed": True
    }

    print(f"\n[Element 3] 验证约束函数 (期望 {len(constraints)} 个):")

    for constraint in constraints:
        constraint_name = constraint.get('name', '')
        constraint_type = constraint.get('type', '')

        # 规范化名称（处理空格和特殊字符）
        normalized_name = constraint_name.replace(' ', '_').replace('-', '_').lower()

        # 可能的函数模式
        patterns = [
            f"def\\s+(validate|check|verify)_{normalized_name}",
            f"def\\s+(validate|check|verify)_.*{constraint_type}",
            f"def\\s+evaluate_{normalized_name}_penalty",
        ]

        found = False
        for pattern in patterns:
            if re.search(pattern, implementation_code, re.IGNORECASE):
                found = True
                break

        if found:
            result["found_count"] += 1
            print(f"  ✓ {constraint_name}")
        else:
            result["missing_items"].append(constraint_name)
            result["passed"] = False
            print(f"  ✗ {constraint_name} (未找到)")

    print(f"  找到 {result['found_count']}/{result['expected_count']} 个约束函数")

    return result
```

### 步骤4: 验证Element 4 - 目标函数

```python
def validate_element_4_objectives(implementation_code, ten_element_model):
    """
    验证目标函数是否有对应的计算函数

    Returns:
        dict: 验证结果
    """
    objectives = ten_element_model.get('objectives', [])

    result = {
        "element": "Element_4_objectives",
        "expected_count": len(objectives),
        "found_count": 0,
        "missing_items": [],
        "passed": True
    }

    print(f"\n[Element 4] 验证目标函数 (期望 {len(objectives)} 个):")

    for objective in objectives:
        obj_name = objective.get('name', '')

        # 规范化名称
        normalized_name = obj_name.replace(' ', '_').lower()

        # 可能的函数模式
        patterns = [
            f"def\\s+calculate_{normalized_name}",
            f"def\\s+evaluate_{normalized_name}",
            f"def\\s+compute_{normalized_name}",
            f"def\\s+calculate_.*objective",
        ]

        found = False
        for pattern in patterns:
            if re.search(pattern, implementation_code, re.IGNORECASE):
                found = True
                break

        if found:
            result["found_count"] += 1
            print(f"  ✓ {obj_name}")
        else:
            result["missing_items"].append(obj_name)
            result["passed"] = False
            print(f"  ✗ {obj_name} (未找到)")

    print(f"  找到 {result['found_count']}/{result['expected_count']} 个目标函数")

    return result
```

### 步骤5: 验证Element 5 - 算法

```python
def validate_element_5_algorithm(implementation_code, ten_element_model):
    """
    验证算法求解器是否存在

    Returns:
        dict: 验证结果
    """
    algorithm = ten_element_model.get('algorithm', {})
    algorithm_name = algorithm.get('name', '')

    result = {
        "element": "Element_5_algorithm",
        "expected": algorithm_name,
        "found": False,
        "missing_items": [],
        "passed": True
    }

    print(f"\n[Element 5] 验证算法实现 (期望: {algorithm_name}):")

    # 检查算法类
    solver_patterns = [
        r'class\s+\w*(Solver|Algorithm|Optimizer)',
        f"class\\s+.*{algorithm_name.replace(' ', '')}",
    ]

    has_solver_class = False
    for pattern in solver_patterns:
        if re.search(pattern, implementation_code, re.IGNORECASE):
            has_solver_class = True
            break

    if has_solver_class:
        print("  ✓ 算法求解器类存在")
    else:
        result["passed"] = False
        result["missing_items"].append("solver_class")
        print("  ✗ 算法求解器类缺失")

    # 检查solve方法
    has_solve_method = bool(re.search(r'def\s+solve\s*\(', implementation_code))

    if has_solve_method:
        print("  ✓ solve() 方法存在")
    else:
        result["passed"] = False
        result["missing_items"].append("solve_method")
        print("  ✗ solve() 方法缺失")

    result["found"] = has_solver_class and has_solve_method

    return result
```

### 步骤6: 验证Element 10 - 输出格式

```python
def validate_element_10_output(implementation_code, ten_element_model):
    """
    验证输出保存函数是否存在

    Returns:
        dict: 验证结果
    """
    output_format = ten_element_model.get('output_format', {})

    result = {
        "element": "Element_10_output_format",
        "expected": "save function",
        "found": False,
        "missing_items": [],
        "passed": True
    }

    print(f"\n[Element 10] 验证输出保存:")

    # 检查save函数
    save_patterns = [
        r'def\s+save_',
        r'\.to_csv',
        r'\.to_json',
        r'\.to_excel',
    ]

    for pattern in save_patterns:
        if re.search(pattern, implementation_code):
            result["found"] = True
            print(f"  ✓ 输出保存函数存在")
            break

    if not result["found"]:
        result["passed"] = False
        result["missing_items"].append("save_function")
        print("  ✗ 输出保存函数缺失")

    return result
```

### 步骤7: 主验证函数

```python
from datetime import datetime

def validate_element_code_mapping(
    implementation_code,
    ten_element_model,
    solution_document_path
):
    """
    完整的十要素→代码映射验证

    Returns:
        dict: 完整验证报告
    """
    print("\n" + "=" * 70)
    print("十要素→代码映射验证")
    print("=" * 70)

    validation_results = []

    # 执行各个Element的验证
    validation_results.append(
        validate_element_1_decision_variables(implementation_code, ten_element_model)
    )

    validation_results.append(
        validate_element_3_constraints(implementation_code, ten_element_model)
    )

    validation_results.append(
        validate_element_4_objectives(implementation_code, ten_element_model)
    )

    validation_results.append(
        validate_element_5_algorithm(implementation_code, ten_element_model)
    )

    validation_results.append(
        validate_element_9_input_data(implementation_code, ten_element_model)
    )

    validation_results.append(
        validate_element_10_output(implementation_code, ten_element_model)
    )

    # 汇总结果
    all_passed = all(r.get("passed", False) for r in validation_results)
    total_elements = len(validation_results)
    passed_elements = sum(1 for r in validation_results if r.get("passed", False))

    # 收集所有缺失项
    missing_mappings = []
    for r in validation_results:
        if not r.get("passed", False):
            element_name = r.get("element", "Unknown")
            for item in r.get("missing_items", []):
                missing_mappings.append(f"{element_name}: {item}")

    # 生成验证报告
    validation_report = {
        "metadata": {
            "validated_at": datetime.now().isoformat(),
            "solution_document": solution_document_path,
            "version": "V4.4"
        },

        "overall_result": "PASS" if all_passed else "FAIL",

        "summary": {
            "total_elements": total_elements,
            "passed_elements": passed_elements,
            "failed_elements": total_elements - passed_elements,
            "all_covered": all_passed
        },

        "element_results": validation_results,

        "missing_mappings": missing_mappings
    }

    # 打印验证摘要
    print("\n" + "=" * 70)
    print("验证摘要")
    print("=" * 70)
    print(f"总体结果: {validation_report['overall_result']}")
    print(f"通过: {passed_elements}/{total_elements} 个Element")

    if not all_passed:
        print(f"\n缺失的映射 ({len(missing_mappings)} 个):")
        for mapping in missing_mappings:
            print(f"  ✗ {mapping}")
    else:
        print("\n✓✓✓ 所有十要素都有对应的代码映射 ✓✓✓")

    print("=" * 70 + "\n")

    # 如果验证失败，抛出异常阻断流程
    if not all_passed:
        error_message = f"""
❌ 十要素代码覆盖验证失败！

缺失的映射:
{chr(10).join(['  - ' + m for m in missing_mappings])}

这意味着生成的代码没有覆盖所有十要素，无法保证代码完整性。

解决方案:
- 从 Step 3.5 重新生成代码
- 确保generate-code-from-solution.md包含所有Element的生成步骤
- 检查TenElementModel是否正确传递
"""
        raise RuntimeError(error_message)

    return validation_report
```

## 输出

```yaml
outputs:
  validation_report:
    type: object
    description: 完整的验证报告
    structure:
      metadata: object
      overall_result: string (PASS/FAIL)
      summary:
        total_elements: integer
        passed_elements: integer
        failed_elements: integer
        all_covered: boolean
      element_results: array
      missing_mappings: array

  missing_mappings:
    type: array
    description: 缺失的Element→代码映射列表
```

## 质量门禁

```yaml
verification_gate:
  critical: true
  check: 'validation_report.summary.all_covered == true'
  on_fail: 'block_with_error'
  max_retries: 3

error_handling:
  on_fail:
    action: '阻断workflow并返回修复'
    message: '十要素代码映射不完整'
    next_step: 'analyze-validation-errors'
```

## 质量检查

- [ ] 所有10个Element都已验证
- [ ] Element 9（数据加载）验证详细
- [ ] 缺失项报告清晰
- [ ] 验证失败时正确阻断
- [ ] 错误信息包含修复建议

## 引用

- @TenElementModel定义
- @P0改进文档/十要素完整性保障

---

**创建**: 2025-11-03
**BMAD版本**: v6-alpha (V4.4)
**核心机制**: 十要素→代码强制映射验证，P0改进核心
