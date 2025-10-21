# Task: Final Consistency Check

**任务ID**: `final-consistency-check`
**版本**: V4.3
**用途**: Phase 3.2 - 方案集成后的最终一致性检查

## 输入

```yaml
inputs:
  - integrated_solution: 集成后的完整解决方案
  - ten_element_model: TenElementModel基线
```

## 处理逻辑

### 步骤1: 验证与TenElementModel的一致性

```python
def verify_model_alignment(integrated_solution, ten_element_model):
    """
    验证集成方案与TenElementModel的对齐
    """
    alignment_check = {
        "decision_variables_match": False,
        "parameters_match": False,
        "constraints_implemented": False,
        "objectives_implemented": False,
        "algorithm_match": False,
        "issues": []
    }

    # 检查决策变量
    solution_vars = set(integrated_solution.get("decision_variables", {}).keys())
    model_vars = set(v["name"] for v in ten_element_model.get("decision_variables", []))

    if solution_vars == model_vars:
        alignment_check["decision_variables_match"] = True
    else:
        missing = model_vars - solution_vars
        extra = solution_vars - model_vars
        if missing:
            alignment_check["issues"].append(f"缺少决策变量: {missing}")
        if extra:
            alignment_check["issues"].append(f"多余决策变量: {extra}")

    # 检查约束实现
    solution_constraints = integrated_solution.get("constraints", [])
    model_constraints = ten_element_model.get("constraints", [])

    if len(solution_constraints) >= len(model_constraints):
        alignment_check["constraints_implemented"] = True
    else:
        alignment_check["issues"].append(
            f"约束实现不完整: {len(solution_constraints)}/{len(model_constraints)}"
        )

    # 检查目标函数
    solution_objectives = integrated_solution.get("objectives", [])
    model_objectives = ten_element_model.get("objectives", [])

    if len(solution_objectives) == len(model_objectives):
        alignment_check["objectives_implemented"] = True
    else:
        alignment_check["issues"].append(
            f"目标函数不匹配: {len(solution_objectives)}/{len(model_objectives)}"
        )

    # 检查算法
    solution_algorithm = integrated_solution.get("algorithm", {}).get("name")
    model_algorithm = ten_element_model.get("algorithm", {}).get("name")

    if solution_algorithm == model_algorithm:
        alignment_check["algorithm_match"] = True
    else:
        alignment_check["issues"].append(
            f"算法不匹配: {solution_algorithm} vs {model_algorithm}"
        )

    return alignment_check
```

### 步骤2: 检查专家建议的一致性

```python
def check_expert_consistency(integrated_solution):
    """
    检查来自不同专家的建议是否一致
    """
    consistency_check = {
        "constraint_objective_consistent": True,
        "algorithm_constraint_compatible": True,
        "domain_rules_aligned": True,
        "conflicts": []
    }

    # 检查约束与目标是否冲突
    constraints = integrated_solution.get("constraints", [])
    objectives = integrated_solution.get("objectives", [])

    # 示例：检查是否有约束使得目标无法优化
    # 实际实现会更复杂

    # 检查算法与约束的兼容性
    algorithm = integrated_solution.get("algorithm", {})
    complex_constraints = [c for c in constraints if c.get("complexity") == "high"]

    if algorithm.get("type") == "exact" and len(complex_constraints) > 5:
        consistency_check["algorithm_constraint_compatible"] = False
        consistency_check["conflicts"].append(
            "精确算法可能无法处理过多复杂约束"
        )

    return consistency_check
```

### 步骤3: 验证引用完整性

```python
def verify_citation_integrity(integrated_solution):
    """
    验证所有组件都有正确的引用
    """
    citation_check = {
        "all_cited": True,
        "valid_paths": True,
        "missing_citations": [],
        "invalid_citations": []
    }

    # 需要引用的组件
    components_requiring_citation = [
        "constraints",
        "objectives",
        "algorithm",
        "domain_rules"
    ]

    for component_name in components_requiring_citation:
        component = integrated_solution.get(component_name)

        if isinstance(component, list):
            for idx, item in enumerate(component):
                if not item.get("citation"):
                    citation_check["all_cited"] = False
                    citation_check["missing_citations"].append(
                        f"{component_name}[{idx}]"
                    )
        elif isinstance(component, dict):
            if not component.get("citation"):
                citation_check["all_cited"] = False
                citation_check["missing_citations"].append(component_name)

    return citation_check
```

### 步骤4: 检查实现完整性

```python
def check_implementation_completeness(integrated_solution):
    """
    检查解决方案实现的完整性
    """
    completeness_check = {
        "has_data_loading": False,
        "has_constraint_validation": False,
        "has_objective_calculation": False,
        "has_algorithm_implementation": False,
        "has_result_output": False,
        "missing_components": []
    }

    # 检查各个实现组件
    if "data_loading" in integrated_solution:
        completeness_check["has_data_loading"] = True
    else:
        completeness_check["missing_components"].append("data_loading")

    if "constraint_validation" in integrated_solution:
        completeness_check["has_constraint_validation"] = True
    else:
        completeness_check["missing_components"].append("constraint_validation")

    if "objective_calculation" in integrated_solution:
        completeness_check["has_objective_calculation"] = True
    else:
        completeness_check["missing_components"].append("objective_calculation")

    if "algorithm_implementation" in integrated_solution:
        completeness_check["has_algorithm_implementation"] = True
    else:
        completeness_check["missing_components"].append("algorithm_implementation")

    if "result_output" in integrated_solution:
        completeness_check["has_result_output"] = True
    else:
        completeness_check["missing_components"].append("result_output")

    return completeness_check
```

### 步骤5: 生成一致性报告

```python
def generate_consistency_report(
    alignment_check,
    consistency_check,
    citation_check,
    completeness_check
):
    """
    生成综合一致性报告
    """
    # 计算总体状态
    all_checks_passed = (
        all(alignment_check.get(k, False) for k in [
            "decision_variables_match",
            "constraints_implemented",
            "objectives_implemented",
            "algorithm_match"
        ]) and
        consistency_check["constraint_objective_consistent"] and
        consistency_check["algorithm_constraint_compatible"] and
        citation_check["all_cited"] and
        all(completeness_check.get(f"has_{c}", False) for c in [
            "data_loading", "constraint_validation",
            "objective_calculation", "algorithm_implementation",
            "result_output"
        ])
    )

    report = {
        "overall_status": "pass" if all_checks_passed else "fail",
        "alignment_check": alignment_check,
        "consistency_check": consistency_check,
        "citation_check": citation_check,
        "completeness_check": completeness_check,
        "summary": {
            "total_issues": (
                len(alignment_check.get("issues", [])) +
                len(consistency_check.get("conflicts", [])) +
                len(citation_check.get("missing_citations", [])) +
                len(completeness_check.get("missing_components", []))
            ),
            "critical_issues": len(alignment_check.get("issues", [])),
            "warnings": len(consistency_check.get("conflicts", []))
        }
    }

    return report
```

## 输出

```yaml
outputs:
  consistency_validation:
    type: object
    required: true
    structure:
      overall_status: string (pass | fail)
      alignment_check: object
      consistency_check: object
      citation_check: object
      completeness_check: object
      summary: object
```

## 示例输出

```json
{
  "consistency_validation": {
    "overall_status": "pass",
    "alignment_check": {
      "decision_variables_match": true,
      "parameters_match": true,
      "constraints_implemented": true,
      "objectives_implemented": true,
      "algorithm_match": true,
      "issues": []
    },
    "consistency_check": {
      "constraint_objective_consistent": true,
      "algorithm_constraint_compatible": true,
      "domain_rules_aligned": true,
      "conflicts": []
    },
    "citation_check": {
      "all_cited": true,
      "valid_paths": true,
      "missing_citations": [],
      "invalid_citations": []
    },
    "completeness_check": {
      "has_data_loading": true,
      "has_constraint_validation": true,
      "has_objective_calculation": true,
      "has_algorithm_implementation": true,
      "has_result_output": true,
      "missing_components": []
    },
    "summary": {
      "total_issues": 0,
      "critical_issues": 0,
      "warnings": 0
    }
  }
}
```

## 质量检查

- [ ] TenElementModel对齐验证完成
- [ ] 专家建议一致性检查完成
- [ ] 引用完整性验证通过
- [ ] 实现完整性检查通过
- [ ] 一致性报告清晰详细

## 引用

- @质量评测专家库/一致性检查标准
- @编排协调专家库/最终验证流程
- V4.3架构规范: Phase 3 一致性保证

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 多维度一致性检查，确保方案质量
