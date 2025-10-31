# Task: Validate Code Completeness

**任务ID**: `validate-code-completeness`
**版本**: V4.3
**用途**: Phase 4 Step 4.5 - 验证生成代码的完整性和正确性

## 输入

```yaml
inputs:
  - implementation_code: 生成的完整代码
  - ten_element_model: TenElementModel对象
  - solution_document: 方案文档内容
  - expert_guidance: 专家库指导信息
```

## 🚨 强制要求（MANDATORY）

### 1. 三层验证机制

**CRITICAL**: 必须通过三层验证，确保代码完整可运行。

```yaml
validation_levels:
  L1_completeness:
    name: 代码完整性检查
    checks:
      - 无TODO标记
      - 无pass语句
      - 无NotImplementedError
      - 无空实现

  L2_syntax:
    name: 语法正确性检查
    checks:
      - Python语法正确
      - 可成功编译
      - 导入语句有效
      - 无明显错误

  L3_consistency:
    name: 方案一致性检查
    checks:
      - 决策变量一致
      - 约束数量匹配
      - 目标函数数量匹配
      - 算法参数匹配
```

### 2. 阻断机制

如果任何验证失败，必须阻断流程并提供详细错误信息。

```yaml
blocking_mechanism:
  on_failure: BLOCK
  error_reporting: DETAILED
  recovery_suggestions: REQUIRED
```

## 处理逻辑

### 步骤1: L1验证 - 代码完整性

```python
def validate_code_completeness(code: str) -> dict:
    """
    L1验证：检查代码是否完整

    Args:
        code: 生成的代码

    Returns:
        result: 验证结果
    """
    import re

    result = {
        "level": "L1_completeness",
        "passed": True,
        "errors": [],
        "warnings": []
    }

    print("=" * 70)
    print("[L1] 代码完整性验证")
    print("=" * 70)

    # 1. 检查TODO
    todo_pattern = r'#\s*TODO|#\s*todo|TODO:|todo:'
    todo_matches = re.findall(todo_pattern, code, re.IGNORECASE)
    if todo_matches:
        line_numbers = []
        for i, line in enumerate(code.split('\n'), 1):
            if re.search(todo_pattern, line, re.IGNORECASE):
                line_numbers.append(i)

        result["passed"] = False
        result["errors"].append({
            "type": "TODO_FOUND",
            "count": len(todo_matches),
            "lines": line_numbers,
            "message": f"代码包含 {len(todo_matches)} 个TODO标记",
            "severity": "CRITICAL"
        })
        print(f"✗ 发现TODO标记: {len(todo_matches)} 个（行: {line_numbers[:5]}...）")
    else:
        print("✓ 无TODO标记")

    # 2. 检查pass语句（空实现）
    pass_pattern = r'^\s+pass\s*(?:#.*)?$'
    pass_matches = list(re.finditer(pass_pattern, code, re.MULTILINE))
    if pass_matches:
        line_numbers = []
        for match in pass_matches:
            line_num = code[:match.start()].count('\n') + 1
            line_numbers.append(line_num)

        result["passed"] = False
        result["errors"].append({
            "type": "EMPTY_IMPLEMENTATION",
            "count": len(pass_matches),
            "lines": line_numbers,
            "message": f"代码包含 {len(pass_matches)} 个空实现（pass语句）",
            "severity": "CRITICAL"
        })
        print(f"✗ 发现空实现: {len(pass_matches)} 个（行: {line_numbers[:5]}...）")
    else:
        print("✓ 无空实现")

    # 3. 检查NotImplementedError
    if "NotImplementedError" in code:
        result["passed"] = False
        result["errors"].append({
            "type": "NOT_IMPLEMENTED",
            "message": "代码包含NotImplementedError",
            "severity": "CRITICAL"
        })
        print("✗ 发现NotImplementedError")
    else:
        print("✓ 无NotImplementedError")

    # 4. 检查示例数据/占位符
    placeholder_patterns = [
        r'example_data',
        r'dummy_data',
        r'placeholder',
        r'测试数据',
        r'示例数据'
    ]

    for pattern in placeholder_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            result["warnings"].append({
                "type": "PLACEHOLDER_DATA",
                "pattern": pattern,
                "message": f"代码可能包含占位数据: {pattern}",
                "severity": "WARNING"
            })
            print(f"⚠ 可能包含占位数据: {pattern}")

    print("\n" + "-" * 70)
    if result["passed"]:
        print("✓ L1验证通过：代码完整")
    else:
        print(f"✗ L1验证失败：发现 {len(result['errors'])} 个错误")
    print("=" * 70 + "\n")

    return result
```

### 步骤2: L2验证 - 语法正确性

```python
def validate_code_syntax(code: str) -> dict:
    """
    L2验证：检查代码语法是否正确

    Args:
        code: 生成的代码

    Returns:
        result: 验证结果
    """
    import ast
    import sys

    result = {
        "level": "L2_syntax",
        "passed": True,
        "errors": [],
        "warnings": []
    }

    print("=" * 70)
    print("[L2] 语法正确性验证")
    print("=" * 70)

    # 1. Python语法检查
    try:
        compile(code, '<generated_code>', 'exec')
        print("✓ Python语法正确")
    except SyntaxError as e:
        result["passed"] = False
        result["errors"].append({
            "type": "SYNTAX_ERROR",
            "line": e.lineno,
            "offset": e.offset,
            "message": str(e),
            "text": e.text,
            "severity": "CRITICAL"
        })
        print(f"✗ 语法错误（行 {e.lineno}）: {e.msg}")
        print(f"  {e.text}")
        print(f"  {' ' * (e.offset - 1)}^")

    # 2. AST解析检查
    try:
        tree = ast.parse(code)
        print("✓ AST解析成功")

        # 统计代码结构
        stats = {
            "classes": 0,
            "functions": 0,
            "imports": 0
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                stats["classes"] += 1
            elif isinstance(node, ast.FunctionDef):
                stats["functions"] += 1
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                stats["imports"] += 1

        print(f"  - 类定义: {stats['classes']} 个")
        print(f"  - 函数定义: {stats['functions']} 个")
        print(f"  - 导入语句: {stats['imports']} 个")

    except Exception as e:
        result["warnings"].append({
            "type": "AST_PARSE_ERROR",
            "message": f"AST解析失败: {str(e)}",
            "severity": "WARNING"
        })
        print(f"⚠ AST解析警告: {e}")

    # 3. 检查常见错误模式
    common_errors = [
        (r'\bimport\s+\*', "使用了 import *"),
        (r'\bexec\s*\(', "使用了危险的exec()"),
        (r'\beval\s*\(', "使用了危险的eval()"),
    ]

    for pattern, description in common_errors:
        import re
        if re.search(pattern, code):
            result["warnings"].append({
                "type": "CODE_SMELL",
                "pattern": pattern,
                "message": description,
                "severity": "WARNING"
            })
            print(f"⚠ 代码警告: {description}")

    print("\n" + "-" * 70)
    if result["passed"]:
        print("✓ L2验证通过：语法正确")
    else:
        print(f"✗ L2验证失败：发现 {len(result['errors'])} 个错误")
    print("=" * 70 + "\n")

    return result
```

### 步骤3: L3验证 - 方案一致性

```python
def validate_solution_consistency(
    code: str,
    ten_element_model: dict,
    solution_document: dict
) -> dict:
    """
    L3验证：检查代码与方案的一致性

    Args:
        code: 生成的代码
        ten_element_model: TenElementModel
        solution_document: 方案文档

    Returns:
        result: 验证结果
    """
    import re

    result = {
        "level": "L3_consistency",
        "passed": True,
        "errors": [],
        "warnings": []
    }

    print("=" * 70)
    print("[L3] 方案一致性验证")
    print("=" * 70)

    # 1. 检查决策变量定义
    decision_variables = ten_element_model.get('decision_variables', [])
    print(f"\n检查决策变量（期望 {len(decision_variables)} 个）:")

    for dv in decision_variables:
        dv_name = dv['name']
        # 检查是否在代码中定义了对应的类或属性
        if dv_name in code or dv['domain'].split('[')[0] in code:
            print(f"  ✓ {dv_name}")
        else:
            result["warnings"].append({
                "type": "MISSING_DECISION_VARIABLE",
                "variable": dv_name,
                "message": f"决策变量可能未实现: {dv_name}",
                "severity": "WARNING"
            })
            print(f"  ⚠ {dv_name} (可能未实现)")

    # 2. 检查约束函数
    constraints = ten_element_model.get('constraints', [])
    print(f"\n检查约束函数（期望 {len(constraints)} 个）:")

    constraint_functions_found = 0
    for constraint in constraints:
        constraint_type = constraint['type']
        # 查找约束验证函数
        func_pattern = f"def validate_{constraint_type}_constraint|def evaluate_{constraint_type}_penalty"

        if re.search(func_pattern, code):
            print(f"  ✓ {constraint['name']} ({constraint_type})")
            constraint_functions_found += 1
        else:
            result["errors"].append({
                "type": "MISSING_CONSTRAINT",
                "constraint": constraint['name'],
                "constraint_type": constraint_type,
                "message": f"约束函数未找到: {constraint['name']}",
                "severity": "ERROR"
            })
            print(f"  ✗ {constraint['name']} ({constraint_type}) - 未找到")
            result["passed"] = False

    print(f"  找到 {constraint_functions_found}/{len(constraints)} 个约束函数")

    # 3. 检查目标函数
    objectives = ten_element_model.get('objectives', [])
    print(f"\n检查目标函数（期望 {len(objectives)} 个）:")

    objective_functions_found = 0
    for objective in objectives:
        # 查找目标计算函数
        obj_name_normalized = objective['name'].replace(' ', '_').lower()
        func_pattern = f"def calculate_{obj_name_normalized}|def calculate_.*objective"

        if re.search(func_pattern, code):
            print(f"  ✓ {objective['name']}")
            objective_functions_found += 1
        else:
            result["warnings"].append({
                "type": "MISSING_OBJECTIVE",
                "objective": objective['name'],
                "message": f"目标函数可能未找到: {objective['name']}",
                "severity": "WARNING"
            })
            print(f"  ⚠ {objective['name']} (可能未找到)")

    print(f"  找到 {objective_functions_found}/{len(objectives)} 个目标函数")

    # 4. 检查算法参数
    algorithm = ten_element_model.get('algorithm', {})
    algorithm_params = algorithm.get('parameters', {})
    print(f"\n检查算法参数（期望 {len(algorithm_params)} 个）:")

    params_found = 0
    for param_name, param_value in algorithm_params.items():
        if param_name in code:
            print(f"  ✓ {param_name} = {param_value}")
            params_found += 1
        else:
            result["warnings"].append({
                "type": "MISSING_PARAMETER",
                "parameter": param_name,
                "message": f"算法参数可能未配置: {param_name}",
                "severity": "WARNING"
            })
            print(f"  ⚠ {param_name} (可能未配置)")

    print(f"  找到 {params_found}/{len(algorithm_params)} 个参数")

    # 5. 检查数据加载
    input_data = ten_element_model.get('input_data', {})
    data_sources = input_data.get('sources', [])
    print(f"\n检查数据源（期望 {len(data_sources)} 个）:")

    if "load_input_data" in code:
        print("  ✓ 数据加载函数存在")
    else:
        result["errors"].append({
            "type": "MISSING_DATA_LOADER",
            "message": "未找到数据加载函数 load_input_data",
            "severity": "CRITICAL"
        })
        print("  ✗ 数据加载函数未找到")
        result["passed"] = False

    print("\n" + "-" * 70)
    if result["passed"]:
        print("✓ L3验证通过：代码与方案一致")
    else:
        print(f"✗ L3验证失败：发现 {len(result['errors'])} 个错误")
    print("=" * 70 + "\n")

    return result
```

### 步骤4: 主验证函数

```python
def validate_complete_code(
    implementation_code: str,
    ten_element_model: dict,
    solution_document: dict,
    expert_guidance: dict
) -> dict:
    """
    完整的三层验证

    Args:
        implementation_code: 生成的代码
        ten_element_model: TenElementModel
        solution_document: 方案文档
        expert_guidance: 专家库指导

    Returns:
        validation_report: 完整验证报告
    """
    print("\n" + "=" * 70)
    print("开始代码完整性验证（三层验证机制）")
    print("=" * 70 + "\n")

    validation_report = {
        "overall_result": "PASSED",
        "levels": [],
        "summary": {
            "total_errors": 0,
            "total_warnings": 0,
            "critical_issues": []
        }
    }

    # L1: 代码完整性
    l1_result = validate_code_completeness(implementation_code)
    validation_report["levels"].append(l1_result)
    validation_report["summary"]["total_errors"] += len(l1_result["errors"])
    validation_report["summary"]["total_warnings"] += len(l1_result["warnings"])

    if not l1_result["passed"]:
        validation_report["overall_result"] = "FAILED"
        for error in l1_result["errors"]:
            if error.get("severity") == "CRITICAL":
                validation_report["summary"]["critical_issues"].append(error)

    # L2: 语法正确性
    l2_result = validate_code_syntax(implementation_code)
    validation_report["levels"].append(l2_result)
    validation_report["summary"]["total_errors"] += len(l2_result["errors"])
    validation_report["summary"]["total_warnings"] += len(l2_result["warnings"])

    if not l2_result["passed"]:
        validation_report["overall_result"] = "FAILED"
        for error in l2_result["errors"]:
            if error.get("severity") == "CRITICAL":
                validation_report["summary"]["critical_issues"].append(error)

    # L3: 方案一致性
    l3_result = validate_solution_consistency(
        implementation_code,
        ten_element_model,
        solution_document
    )
    validation_report["levels"].append(l3_result)
    validation_report["summary"]["total_errors"] += len(l3_result["errors"])
    validation_report["summary"]["total_warnings"] += len(l3_result["warnings"])

    if not l3_result["passed"]:
        validation_report["overall_result"] = "FAILED"
        for error in l3_result["errors"]:
            if error.get("severity") in ["CRITICAL", "ERROR"]:
                validation_report["summary"]["critical_issues"].append(error)

    # 生成验证报告
    print("\n" + "=" * 70)
    print("验证报告")
    print("=" * 70)
    print(f"整体结果: {validation_report['overall_result']}")
    print(f"总错误数: {validation_report['summary']['total_errors']}")
    print(f"总警告数: {validation_report['summary']['total_warnings']}")
    print(f"严重问题: {len(validation_report['summary']['critical_issues'])} 个")

    if validation_report["overall_result"] == "PASSED":
        print("\n✓✓✓ 所有验证通过，代码质量合格 ✓✓✓")
    else:
        print("\n✗✗✗ 验证失败，需要修复以下问题 ✗✗✗")
        for issue in validation_report["summary"]["critical_issues"]:
            print(f"\n  [{issue['type']}] {issue['message']}")
            if 'lines' in issue:
                print(f"  影响行数: {issue['lines']}")

    print("=" * 70 + "\n")

    # 如果验证失败，抛出异常阻断流程
    if validation_report["overall_result"] == "FAILED":
        error_summary = "\n".join([
            f"- {issue['type']}: {issue['message']}"
            for issue in validation_report["summary"]["critical_issues"]
        ])
        raise RuntimeError(
            f"代码验证失败，发现 {len(validation_report['summary']['critical_issues'])} 个严重问题:\n{error_summary}"
        )

    return validation_report
```

## 输出

```yaml
outputs:
  validation_report:
    type: object
    description: 完整验证报告
    structure:
      overall_result: string (PASSED/FAILED)
      levels:
        - level: string (L1/L2/L3)
          passed: boolean
          errors: list
          warnings: list
      summary:
        total_errors: integer
        total_warnings: integer
        critical_issues: list
```

## 质量检查

- [ ] L1验证执行完成
- [ ] L2验证执行完成
- [ ] L3验证执行完成
- [ ] 验证报告完整
- [ ] 失败时正确阻断流程
- [ ] 错误信息详细清晰

## 错误处理

### 如果L1验证失败

```
错误类型: TODO_FOUND / EMPTY_IMPLEMENTATION / NOT_IMPLEMENTED
处理建议:
1. 返回ai-code-generator重新生成
2. 更新AI提示强调不要留TODO
3. 最多重试3次
```

### 如果L2验证失败

```
错误类型: SYNTAX_ERROR
处理建议:
1. 检查生成的代码语法
2. 可能是AI生成错误，需要重新生成
3. 提供详细的语法错误位置
```

### 如果L3验证失败

```
错误类型: MISSING_CONSTRAINT / MISSING_DATA_LOADER
处理建议:
1. 检查generate-code-from-solution的调用逻辑
2. 确认所有组件都已生成
3. 可能需要补充生成缺失的组件
```

## 引用

- @代码质量规范
- @验证机制框架

---

**创建**: 2025-01-21
**BMAD版本**: v6-alpha
**核心机制**: 三层验证机制确保代码完整性
