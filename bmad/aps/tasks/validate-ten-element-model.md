# Task: Validate Ten Element Model

**任务ID**: `validate-ten-element-model`
**版本**: V4.3
**用途**: Phase 1.5 - 验证TenElementModel的完整性、一致性和引用合规性

## 输入

```yaml
inputs:
  - ten_element_model_draft: 初步构建的十要素模型
```

## TenElementModel Schema

```yaml
ten_element_model:
  1_decision_variables:
    description: '决策变量定义'
    required: true
    validation_rules:
      - must_specify_domain
      - must_specify_type
      - must_have_clear_meaning

  2_parameters:
    description: '参数定义'
    required: true
    validation_rules:
      - must_specify_source
      - must_specify_data_type
      - must_cite_domain_library

  3_constraints:
    description: '约束定义'
    required: true
    validation_rules:
      - must_cite_constraint_library
      - must_specify_constraint_type
      - must_be_implementable

  4_objectives:
    description: '优化目标定义'
    required: true
    validation_rules:
      - must_cite_objective_library
      - must_specify_optimization_direction
      - must_define_weights_if_multi_objective

  5_algorithm:
    description: '算法选择'
    required: true
    validation_rules:
      - must_cite_algorithm_library
      - must_match_problem_complexity
      - must_be_compatible_with_constraints

  6_time_model:
    description: '时间模型定义'
    required: true
    validation_rules:
      - must_specify_horizon
      - must_specify_granularity
      - must_specify_time_windows_if_applicable

  7_uncertainty:
    description: '不确定性处理'
    required: false
    validation_rules:
      - if_present_must_specify_type
      - must_specify_handling_method

  8_solver_config:
    description: '求解器配置'
    required: true
    validation_rules:
      - must_specify_solver
      - must_specify_parameters
      - must_specify_termination_criteria

  9_input_data:
    description: '输入数据格式'
    required: true
    validation_rules:
      - must_specify_format
      - must_specify_source
      - must_provide_schema

  10_output_format:
    description: '输出格式定义'
    required: true
    validation_rules:
      - must_specify_structure
      - must_specify_delivery_format
      - must_match_user_requirements
```

## 处理逻辑

### 验证1: 完整性检查

```python
def check_completeness(model):
    issues = []

    # 检查所有必需元素
    required_elements = [1, 2, 3, 4, 5, 6, 8, 9, 10]
    for elem_id in required_elements:
        if elem_id not in model or model[elem_id] is None:
            issues.append({
                "type": "completeness",
                "severity": "critical",
                "element": elem_id,
                "message": f"元素{elem_id}缺失或未定义"
            })

    # 检查元素7（不确定性，可选）
    if 7 in model and model[7]:
        # 如果存在，必须完整定义
        if not model[7].get("type") or not model[7].get("handling_method"):
            issues.append({
                "type": "completeness",
                "severity": "high",
                "element": 7,
                "message": "不确定性元素存在但定义不完整"
            })

    return issues
```

### 验证2: 引用合规性检查（Guardrails）

```python
def check_citation_compliance(model):
    issues = []

    citation_required_elements = {
        2: "domain_library",
        3: "constraint_library",
        4: "objective_library",
        5: "algorithm_library"
    }

    for elem_id, library_name in citation_required_elements.items():
        element = model.get(elem_id)
        if element:
            citations = element.get("citations", [])
            if not citations:
                issues.append({
                    "type": "citation_compliance",
                    "severity": "critical",
                    "element": elem_id,
                    "message": f"元素{elem_id}缺少@{library_name}引用",
                    "guardrail_violation": true
                })
            else:
                # 验证引用格式
                for citation in citations:
                    if not citation.startswith("@专家库/"):
                        issues.append({
                            "type": "citation_format",
                            "severity": "high",
                            "element": elem_id,
                            "citation": citation,
                            "message": "引用格式不正确，应以@专家库/开头"
                        })

    return issues
```

### 验证3: 内部一致性检查

```python
def check_internal_consistency(model):
    issues = []

    # 检查1: 算法与约束兼容性
    algorithm = model.get(5, {})
    constraints = model.get(3, {})

    if algorithm.get("type") == "exact" and constraints.get("nonlinear"):
        issues.append({
            "type": "consistency",
            "severity": "high",
            "elements": [3, 5],
            "message": "精确算法通常不适用于非线性约束"
        })

    # 检查2: 目标与算法匹配
    objectives = model.get(4, {})
    if len(objectives.get("objectives", [])) > 1:
        if not algorithm.get("supports_multi_objective"):
            issues.append({
                "type": "consistency",
                "severity": "critical",
                "elements": [4, 5],
                "message": "多目标优化需要支持多目标的算法"
            })

    # 检查3: 时间模型与决策变量一致
    time_model = model.get(6, {})
    decision_vars = model.get(1, {})

    if time_model.get("has_time_windows") and not any(
        "time" in var.get("name", "").lower()
        for var in decision_vars.get("variables", [])
    ):
        issues.append({
            "type": "consistency",
            "severity": "moderate",
            "elements": [1, 6],
            "message": "时间模型定义了时间窗，但决策变量中未体现时间维度"
        })

    # 检查4: 求解器与问题规模匹配
    solver_config = model.get(8, {})
    problem_size = estimate_problem_size(model)

    if problem_size > 10000 and solver_config.get("solver") == "brute_force":
        issues.append({
            "type": "consistency",
            "severity": "critical",
            "elements": [8],
            "message": "问题规模过大，穷举法不可行"
        })

    return issues
```

### 验证4: 可行性检查

```python
def check_feasibility(model):
    issues = []

    # 检查约束可满足性
    constraints = model.get(3, {})
    if has_contradictory_constraints(constraints):
        issues.append({
            "type": "feasibility",
            "severity": "critical",
            "element": 3,
            "message": "检测到矛盾约束，问题可能无解"
        })

    # 检查算法实现可行性
    algorithm = model.get(5, {})
    if algorithm.get("complexity") == "NP-hard" and not algorithm.get("heuristic"):
        time_model = model.get(6, {})
        if time_model.get("horizon") > 365:  # 一年以上
            issues.append({
                "type": "feasibility",
                "severity": "high",
                "elements": [5, 6],
                "message": "NP-hard问题在长时间范围内可能难以求解，建议使用启发式"
            })

    return issues
```

### 验证5: 聚合报告

```python
def generate_validation_report(all_issues):
    critical_count = sum(1 for i in all_issues if i["severity"] == "critical")
    high_count = sum(1 for i in all_issues if i["severity"] == "high")
    moderate_count = sum(1 for i in all_issues if i["severity"] == "moderate")

    if critical_count > 0:
        validation_status = "failed"
        level = "fail"
    elif high_count > 0:
        validation_status = "warning"
        level = "warning"
    else:
        validation_status = "passed"
        level = "pass"

    return {
        "validation_status": validation_status,
        "level": level,
        "summary": {
            "total_issues": len(all_issues),
            "critical": critical_count,
            "high": high_count,
            "moderate": moderate_count
        },
        "issues": all_issues
    }
```

## 输出

```yaml
outputs:
  validation_report:
    type: object
    structure:
      validation_status: "passed" | "warning" | "failed"
      level: "pass" | "warning" | "fail"
      summary:
        total_issues: integer
        critical: integer
        high: integer
        moderate: integer
      issues: array
        - type: string
          severity: string
          element: integer | array
          message: string
          guardrail_violation: boolean

  issues_found:
    type: array
    description: "所有发现的问题列表"
```

## 示例输出

```json
{
  "validation_report": {
    "validation_status": "warning",
    "level": "warning",
    "summary": {
      "total_issues": 3,
      "critical": 0,
      "high": 2,
      "moderate": 1
    },
    "issues": [
      {
        "type": "citation_compliance",
        "severity": "high",
        "element": 3,
        "message": "约束定义中部分约束缺少@constraint_library引用",
        "guardrail_violation": true,
        "affected_constraints": ["capacity_constraint_1", "time_window_constraint_2"]
      },
      {
        "type": "consistency",
        "severity": "high",
        "elements": [4, 5],
        "message": "多目标优化但算法不支持多目标",
        "suggestion": "建议使用NSGA-II或加权和方法"
      },
      {
        "type": "consistency",
        "severity": "moderate",
        "elements": [1, 6],
        "message": "时间窗约束存在但决策变量中未明确体现时间维度"
      }
    ]
  }
}
```

## 质量门禁

```yaml
quality_gates:
  - name: '完整性门禁'
    rule: '所有必需元素存在'
    severity: 'critical'
    block_on_fail: true

  - name: '引用合规性门禁'
    rule: 'citations_required=true, 所有元素有@引用'
    severity: 'critical'
    block_on_fail: true

  - name: '内部一致性门禁'
    rule: '无critical级别一致性问题'
    severity: 'high'
    block_on_fail: true

  - name: '可行性门禁'
    rule: '问题有解且可在合理时间内求解'
    severity: 'high'
    block_on_fail: false
```

## 错误处理

```yaml
on_validation_failed:
  if: level == "fail"
  action: 'block_and_request_fixes'
  message: 'TenElementModel验证失败，请修复critical问题后继续'

on_validation_warning:
  if: level == "warning"
  action: 'alert_and_continue'
  message: 'TenElementModel存在警告，建议修复后继续'

on_guardrail_violation:
  action: 'block'
  message: '检测到Guardrails违规（缺少@引用），必须修复'
```

## 质量检查

- [ ] 所有10个元素的验证规则完整
- [ ] Guardrails引用检查严格执行
- [ ] 一致性检查覆盖关键组合
- [ ] 可行性检查合理
- [ ] 报告格式清晰易读

## 引用

- @编排协调专家库/TenElementModel规范
- @质量评测专家库/模型验证方法
- V4.3架构规范: Guardrails策略

---

**创建**: 2025-10-20
**BMAD版本**: v6-alpha
**核心机制**: TenElementModel验证，统一真相源保证
