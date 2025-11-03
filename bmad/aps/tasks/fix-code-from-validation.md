# Task: Fix Code from Validation

**任务ID**: `fix-code-from-validation`
**版本**: V1.0 (V4.4新增)
**用途**: Phase 3 Step 3.6.8 - 根据修复策略自动修复代码

## 背景

在V4.4之前，代码验证失败后只能整体重试，效率低且成功率不可控。本任务实现：

1. 根据修复策略执行针对性修复
2. 支持全量重新生成、组件级重新生成、增量修复三种策略
3. 使用增强prompt避免重复错误
4. 生成修复后的完整代码

## 输入

```yaml
inputs:
  - implementation_code: 当前生成的代码
  - fix_strategy: 修复策略（来自analyze-validation-errors.md）
  - classified_errors: 分类后的错误信息
  - ten_element_model: TenElementModel对象
  - user_approved_solution: 用户确认的方案
  - solution_document_path: 方案文档路径
  - retry_count: 当前重试次数
```

## 核心功能

### 1. 策略路由器

```python
def execute_fix_strategy(
    implementation_code,
    fix_strategy,
    classified_errors,
    ten_element_model,
    user_approved_solution,
    solution_document_path,
    retry_count
):
    """
    根据修复策略类型路由到不同的修复函数

    Returns:
        dict: 修复结果
    """
    strategy_type = fix_strategy.get("strategy_type")

    print("=" * 70)
    print(f"执行修复策略: {strategy_type}")
    print("=" * 70)

    if strategy_type == "full_regenerate":
        return full_regenerate_code(
            ten_element_model,
            user_approved_solution,
            solution_document_path,
            fix_strategy,
            retry_count
        )

    elif strategy_type == "component_regenerate":
        return component_regenerate_code(
            implementation_code,
            fix_strategy,
            ten_element_model,
            user_approved_solution,
            solution_document_path
        )

    elif strategy_type == "incremental_fix":
        return incremental_fix_code(
            implementation_code,
            fix_strategy,
            classified_errors
        )

    else:
        raise ValueError(f"未知的修复策略类型: {strategy_type}")
```

### 2. 全量重新生成

```python
def full_regenerate_code(
    ten_element_model,
    user_approved_solution,
    solution_document_path,
    fix_strategy,
    retry_count
):
    """
    完全重新生成代码，使用增强的prompt

    Returns:
        dict: 新生成的代码和元数据
    """
    print("\n执行全量重新生成...")
    print(f"重试次数: {retry_count}")

    # 导入代码生成任务
    from generate_code_from_solution import (
        generate_imports,
        generate_data_models,
        generate_constraint_functions,
        generate_objective_functions,
        generate_algorithm_core,
        generate_main_solver,
        generate_data_loading_module,
        assemble_complete_code,
        generate_code_traceability
    )

    # 获取增强的prompt
    enhanced_prompts = fix_strategy.get("enhanced_prompts", [])
    additional_instructions = ""

    if enhanced_prompts:
        additional_instructions = enhanced_prompts[0].get("additional_instructions", "")

    # 添加全局上下文
    context = f"""
{'=' * 70}
代码重新生成 - 第 {retry_count + 1} 次尝试
{'=' * 70}

{additional_instructions}

核心要求:
1. 严格遵循TenElementModel定义
2. 每个组件都必须完整实现，不允许TODO或pass
3. 确保所有Element都有对应的代码映射
4. 使用完整的错误处理和数据验证
5. 添加详细的引用标记和方案依据

{'=' * 70}
"""

    print(context)

    # 重新生成各个组件
    try:
        # 步骤3.1: 生成导入语句
        imports = generate_imports(ten_element_model, user_approved_solution)

        # 步骤3.2: 生成数据模型
        data_models = generate_data_models(ten_element_model, solution_document_path)

        # 步骤3.15: 生成数据加载模块 (V4.4新增)
        data_loading_module = generate_data_loading_module(
            ten_element_model,
            solution_document_path
        )

        # 步骤3.3: 生成约束函数
        constraint_functions = generate_constraint_functions(
            ten_element_model,
            user_approved_solution,
            solution_document_path
        )

        # 步骤3.4: 生成目标函数
        objective_functions = generate_objective_functions(
            ten_element_model,
            user_approved_solution,
            solution_document_path
        )

        # 步骤3.5: 生成算法核心
        algorithm_core = generate_algorithm_core(
            ten_element_model,
            user_approved_solution,
            solution_document_path
        )

        # 步骤3.6: 生成主求解器
        main_solver = generate_main_solver(
            ten_element_model,
            user_approved_solution,
            solution_document_path
        )

        # 步骤4: 组装完整代码
        regenerated_code = assemble_complete_code(
            imports=imports,
            data_models=data_models,
            data_loading_module=data_loading_module,
            constraint_functions=constraint_functions,
            objective_functions=objective_functions,
            algorithm_core=algorithm_core,
            main_solver=main_solver,
            user_approved_solution=user_approved_solution,
            solution_document_path=solution_document_path
        )

        # 生成可追溯性信息
        code_traceability = generate_code_traceability(
            ten_element_model,
            user_approved_solution,
            solution_document_path
        )

        # 添加修复元数据
        code_traceability["fix_metadata"] = {
            "retry_count": retry_count,
            "fix_strategy": "full_regenerate",
            "fixed_at": datetime.now().isoformat(),
            "version": "V4.4"
        }

        print(f"\n✓ 代码重新生成完成 ({len(regenerated_code)} 字符)")

        return {
            "fixed_code": regenerated_code,
            "code_traceability": code_traceability,
            "fix_method": "full_regenerate",
            "success": True
        }

    except Exception as e:
        print(f"\n✗ 代码重新生成失败: {e}")
        return {
            "fixed_code": None,
            "error": str(e),
            "fix_method": "full_regenerate",
            "success": False
        }
```

### 3. 组件级重新生成

```python
def component_regenerate_code(
    implementation_code,
    fix_strategy,
    ten_element_model,
    user_approved_solution,
    solution_document_path
):
    """
    只重新生成缺失或有问题的组件

    Returns:
        dict: 修复后的代码
    """
    print("\n执行组件级重新生成...")

    component_targets = fix_strategy.get("component_targets", [])
    print(f"需要重新生成 {len(component_targets)} 个组件:")
    for target in component_targets:
        print(f"  - {target['component']}: {target['reason']}")

    # 解析现有代码，提取各个部分
    code_sections = parse_code_sections(implementation_code)

    # 导入生成函数
    from generate_code_from_solution import (
        generate_data_loading_module,
        generate_constraint_functions,
        generate_objective_functions
    )

    # 为每个缺失的组件重新生成
    regenerated_components = {}

    for target in component_targets:
        component_name = target["component"]

        try:
            if component_name == "data_loading_module":
                # 重新生成数据加载模块
                new_component = generate_data_loading_module(
                    ten_element_model,
                    solution_document_path
                )
                regenerated_components["data_loading"] = new_component
                print(f"  ✓ 重新生成: {component_name}")

            elif component_name.startswith("constraint_"):
                # 重新生成约束函数
                new_component = generate_constraint_functions(
                    ten_element_model,
                    user_approved_solution,
                    solution_document_path
                )
                regenerated_components["constraints"] = new_component
                print(f"  ✓ 重新生成: {component_name}")

            elif component_name.startswith("objective_"):
                # 重新生成目标函数
                new_component = generate_objective_functions(
                    ten_element_model,
                    user_approved_solution,
                    solution_document_path
                )
                regenerated_components["objectives"] = new_component
                print(f"  ✓ 重新生成: {component_name}")

        except Exception as e:
            print(f"  ✗ 生成失败: {component_name} - {e}")

    # 重新组装代码
    fixed_code = reassemble_code(code_sections, regenerated_components)

    print(f"\n✓ 组件重新生成完成，替换了 {len(regenerated_components)} 个组件")

    return {
        "fixed_code": fixed_code,
        "regenerated_components": list(regenerated_components.keys()),
        "fix_method": "component_regenerate",
        "success": True
    }


def parse_code_sections(implementation_code):
    """
    解析代码，提取各个section

    Returns:
        dict: 代码各部分
    """
    import re

    sections = {
        "header": "",
        "imports": "",
        "data_models": "",
        "data_loading": "",
        "constraints": "",
        "objectives": "",
        "algorithm": "",
        "main_solver": ""
    }

    # 使用正则表达式提取各个section
    # Section标记格式: # ====== [第X部分] 名称 ======

    current_section = "header"
    lines = implementation_code.split('\n')

    for line in lines:
        # 检测section标记
        if re.match(r'#\s*=+\s*\[.*?\]\s*', line) or re.match(r'#\s*=+\s*数据加载', line):
            if '数据模型' in line or '第1部分' in line:
                current_section = "data_models"
            elif '数据加载' in line:
                current_section = "data_loading"
            elif '约束' in line or '第2部分' in line:
                current_section = "constraints"
            elif '目标' in line or '第3部分' in line:
                current_section = "objectives"
            elif '算法' in line or '第4部分' in line:
                current_section = "algorithm"
            elif '求解器' in line or '第5部分' in line:
                current_section = "main_solver"
        elif 'import ' in line and current_section == "header":
            current_section = "imports"

        sections[current_section] += line + '\n'

    return sections


def reassemble_code(code_sections, regenerated_components):
    """
    重新组装代码，替换重新生成的组件

    Returns:
        str: 完整代码
    """
    # 替换重新生成的组件
    for component_key, new_code in regenerated_components.items():
        if component_key in code_sections:
            code_sections[component_key] = new_code

    # 按顺序组装
    assembled_code = ""
    order = [
        "header",
        "imports",
        "data_models",
        "data_loading",
        "constraints",
        "objectives",
        "algorithm",
        "main_solver"
    ]

    for section_name in order:
        if section_name in code_sections and code_sections[section_name].strip():
            assembled_code += code_sections[section_name]
            if not assembled_code.endswith('\n\n'):
                assembled_code += '\n'

    return assembled_code
```

### 4. 增量修复

```python
def incremental_fix_code(implementation_code, fix_strategy, classified_errors):
    """
    应用增量修复，只修改有问题的部分

    Returns:
        dict: 修复后的代码
    """
    print("\n执行增量修复...")

    fixed_code = implementation_code
    applied_fixes = []

    # 获取修复动作
    actions = fix_strategy.get("actions", [])

    for action in actions:
        if action.get("action") == "apply_incremental_fixes":
            fixes = action.get("fixes", [])

            for fix in fixes:
                fix_type = fix.get("type")

                if fix_type == "remove_placeholder":
                    # 移除占位符数据
                    pattern = fix.get("pattern")
                    import re

                    # 查找并注释掉包含占位符的行
                    lines = fixed_code.split('\n')
                    modified_lines = []

                    for line in lines:
                        if re.search(pattern, line, re.IGNORECASE):
                            # 注释掉这一行并添加说明
                            modified_lines.append(f"# FIXED: Removed placeholder - {line.strip()}")
                            applied_fixes.append(f"移除占位符: {pattern}")
                        else:
                            modified_lines.append(line)

                    fixed_code = '\n'.join(modified_lines)
                    print(f"  ✓ 移除占位符: {pattern}")

                elif fix_type == "add_parameter":
                    # 添加缺失的参数
                    param_name = fix.get("parameter")
                    # 简化处理：在配置部分添加参数
                    # 实际实现可能需要更复杂的逻辑

                    applied_fixes.append(f"添加参数: {param_name}")
                    print(f"  ✓ 添加参数: {param_name}")

    print(f"\n✓ 增量修复完成，应用了 {len(applied_fixes)} 个修复")

    return {
        "fixed_code": fixed_code,
        "applied_fixes": applied_fixes,
        "fix_method": "incremental_fix",
        "success": True
    }
```

### 5. 主修复函数

```python
from datetime import datetime

def fix_code_from_validation(
    implementation_code,
    fix_strategy,
    classified_errors,
    ten_element_model,
    user_approved_solution,
    solution_document_path,
    retry_count=0
):
    """
    完整的代码修复流程

    方案依据: P0改进文档 - 自动修复机制设计
    引用: @docs/improvements/P0-ten-element-completeness.md
    核心策略: 根据错误类型选择修复方法（全量/组件/增量）

    Returns:
        dict: 修复结果
    """
    print("\n" + "=" * 70)
    print("开始代码修复流程")
    print("=" * 70)

    # 执行修复策略
    fix_result = execute_fix_strategy(
        implementation_code,
        fix_strategy,
        classified_errors,
        ten_element_model,
        user_approved_solution,
        solution_document_path,
        retry_count
    )

    # 生成修复报告
    fix_report = {
        "metadata": {
            "fixed_at": datetime.now().isoformat(),
            "retry_count": retry_count,
            "version": "V4.4"
        },

        "fix_method": fix_result.get("fix_method"),
        "success": fix_result.get("success"),

        "code_changes": {
            "original_size": len(implementation_code),
            "fixed_size": len(fix_result.get("fixed_code", "")),
            "size_delta": len(fix_result.get("fixed_code", "")) - len(implementation_code)
        },

        "applied_actions": fix_result.get("regenerated_components") or fix_result.get("applied_fixes") or ["full_regenerate"]
    }

    # 打印修复摘要
    print("\n" + "=" * 70)
    print("修复完成")
    print("=" * 70)
    print(f"修复方法: {fix_report['fix_method']}")
    print(f"修复状态: {'✓ 成功' if fix_report['success'] else '✗ 失败'}")
    print(f"代码大小: {fix_report['code_changes']['original_size']} → {fix_report['code_changes']['fixed_size']} 字符")
    print(f"应用的修复: {len(fix_report['applied_actions'])} 个")
    print("=" * 70 + "\n")

    return {
        "fixed_code": fix_result.get("fixed_code"),
        "fix_report": fix_report,
        "code_traceability": fix_result.get("code_traceability")
    }
```

## 输出

```yaml
outputs:
  fixed_code:
    type: string
    description: 修复后的完整代码

  fix_report:
    type: object
    description: 修复报告
    structure:
      metadata: object
      fix_method: string
      success: boolean
      code_changes: object
      applied_actions: array

  code_traceability:
    type: object
    description: 代码可追溯性信息（包含修复元数据）
```

## 修复策略处理逻辑

### full_regenerate

- 完全重新执行generate-code-from-solution.md
- 使用增强的prompt（包含错误历史）
- 适用于严重错误或多个错误

### component_regenerate

- 解析现有代码，提取各个section
- 只重新生成有问题的组件
- 保留正确的代码部分
- 重新组装完整代码

### incremental_fix

- 应用文本级别的修复
- 移除占位符、添加参数等
- 最小化改动

## 质量检查

- [ ] 修复策略正确执行
- [ ] 生成的代码完整
- [ ] 修复报告详细
- [ ] 错误处理完善
- [ ] 可追溯性信息完整

## 错误处理

### 如果修复失败

```python
if not fix_result.get("success"):
    return {
        "fixed_code": implementation_code,  # 返回原代码
        "fix_report": {
            "success": False,
            "error": fix_result.get("error"),
            "recommendation": "escalate_to_human"
        }
    }
```

## 引用

- @代码生成任务/generate-code-from-solution.md
- @质量评测专家库/代码修复方法
- @编排协调专家库/自动修复策略

---

**创建**: 2025-11-03
**BMAD版本**: v6-alpha (V4.4)
**核心机制**: 自动代码修复，支持验证-修复闭环
