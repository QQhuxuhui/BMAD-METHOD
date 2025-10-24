# Task: Check Cross-Expert Consistency

**任务ID**: `check-cross-expert-consistency`
**版本**: V4.3
**用途**: Phase 2 - 跨专家一致性校验，检查各专家分析结果是否存在冲突

## 输入

```yaml
inputs:
  - domain_analysis: 领域专家分析结果
  - constraint_analysis: 约束专家分析结果
  - objective_analysis: 目标专家分析结果
  - algorithm_recommendations: 算法专家推荐结果
```

## 🚨 强制要求（MANDATORY）

### 1. 必须检查所有专家间的一致性

本任务是Phase 2的关键质量保证环节，必须检查：

```yaml
consistency_checks:
  - domain_vs_constraint: 领域约束与约束分析的一致性
  - constraint_vs_objective: 约束与目标的兼容性
  - algorithm_vs_constraint: 算法能力与约束处理的匹配
  - algorithm_vs_objective: 算法能力与目标优化的匹配
```

### 2. 发现冲突必须报告

如果发现任何冲突，必须：

- 明确标识冲突类型
- 说明冲突原因
- 提供解决建议
- 标记为需要用户仲裁（触发Step 2.A.3或用户介入）

## 处理逻辑

### 步骤1: 提取各专家的关键决策

```python
def extract_expert_decisions(
    domain_analysis,
    constraint_analysis,
    objective_analysis,
    algorithm_recommendations
):
    """
    提取各专家的关键决策点

    Returns:
        dict: 专家决策汇总
    """
    decisions = {
        "domain": {
            "industry": domain_analysis.get("industry_identification", {}),
            "domain_constraints": domain_analysis.get("domain_constraints", []),
            "business_rules": domain_analysis.get("business_rules", [])
        },
        "constraint": {
            "hard_constraints": constraint_analysis.get("hard_constraints", []),
            "soft_constraints": constraint_analysis.get("soft_constraints", []),
            "handling_method": constraint_analysis.get("handling_method", {})
        },
        "objective": {
            "primary_objective": objective_analysis.get("primary_objective", {}),
            "secondary_objectives": objective_analysis.get("secondary_objectives", []),
            "multi_objective_approach": objective_analysis.get("multi_objective_approach", "")
        },
        "algorithm": {
            "selected_algorithm": algorithm_recommendations.get("selected_algorithm", ""),
            "algorithm_capabilities": algorithm_recommendations.get("capabilities", {}),
            "recommended_parameters": algorithm_recommendations.get("recommended_parameters", {})
        }
    }

    print("✓ 专家决策已提取")
    return decisions
```

### 步骤2: 检查领域约束与约束分析的一致性

```python
def check_domain_constraint_consistency(domain_decisions, constraint_decisions):
    """
    检查领域专家识别的约束是否与约束专家分析一致

    Returns:
        dict: 一致性检查结果
    """
    check_result = {
        "check_name": "领域约束 vs 约束分析",
        "status": "PASS",
        "issues": []
    }

    # 获取领域专家识别的约束
    domain_constraints = domain_decisions.get("domain_constraints", [])

    # 获取约束专家的约束清单
    hard_constraints = constraint_decisions.get("hard_constraints", [])
    soft_constraints = constraint_decisions.get("soft_constraints", [])
    all_constraints = hard_constraints + soft_constraints

    # 检查领域约束是否都被约束专家覆盖
    for dc in domain_constraints:
        dc_name = dc.get("name", "") if isinstance(dc, dict) else str(dc)

        # 检查是否在约束清单中
        found = False
        for c in all_constraints:
            c_name = c.get("name", "") if isinstance(c, dict) else str(c)
            if dc_name.lower() in c_name.lower() or c_name.lower() in dc_name.lower():
                found = True
                break

        if not found:
            check_result["status"] = "WARNING"
            check_result["issues"].append({
                "type": "missing_constraint",
                "description": f"领域约束 '{dc_name}' 未在约束分析中体现",
                "severity": "medium",
                "recommendation": "请约束专家确认是否遗漏"
            })

    if check_result["issues"]:
        print(f"⚠️ 领域约束一致性检查: 发现{len(check_result['issues'])}个问题")
    else:
        print("✓ 领域约束一致性检查: 通过")

    return check_result
```

### 步骤3: 检查约束与目标的兼容性

```python
def check_constraint_objective_compatibility(constraint_decisions, objective_decisions):
    """
    检查约束是否会阻止目标的优化

    Returns:
        dict: 兼容性检查结果
    """
    check_result = {
        "check_name": "约束 vs 目标兼容性",
        "status": "PASS",
        "conflicts": []
    }

    # 检查硬约束是否过于严格，导致无法优化
    hard_constraints = constraint_decisions.get("hard_constraints", [])
    primary_objective = objective_decisions.get("primary_objective", {})

    # 示例检查：如果目标是最小化时间，但有很多时间窗约束
    if "time" in primary_objective.get("name", "").lower():
        time_related_constraints = [
            c for c in hard_constraints
            if any(kw in str(c).lower() for kw in ["time", "deadline", "时间", "截止"])
        ]

        if len(time_related_constraints) > 5:
            check_result["status"] = "WARNING"
            check_result["conflicts"].append({
                "type": "over_constrained",
                "description": f"时间相关硬约束较多({len(time_related_constraints)}个)，可能限制目标优化空间",
                "severity": "medium",
                "recommendation": "考虑将部分时间约束设为软约束"
            })

    # 检查多目标是否冲突
    secondary_objectives = objective_decisions.get("secondary_objectives", [])
    if len(secondary_objectives) > 0:
        # 检查目标方向是否冲突
        # 例如：同时最小化成本和最大化服务质量可能冲突
        pass

    if check_result["conflicts"]:
        print(f"⚠️ 约束-目标兼容性检查: 发现{len(check_result['conflicts'])}个潜在冲突")
    else:
        print("✓ 约束-目标兼容性检查: 通过")

    return check_result
```

### 步骤4: 检查算法与约束的匹配

```python
def check_algorithm_constraint_match(algorithm_decisions, constraint_decisions):
    """
    检查算法能力是否能处理约束

    Returns:
        dict: 匹配检查结果
    """
    check_result = {
        "check_name": "算法 vs 约束匹配",
        "status": "PASS",
        "mismatches": []
    }

    selected_algorithm = algorithm_decisions.get("selected_algorithm", "")
    algorithm_capabilities = algorithm_decisions.get("algorithm_capabilities", {})

    hard_constraints = constraint_decisions.get("hard_constraints", [])
    handling_method = constraint_decisions.get("handling_method", {})

    # 检查算法是否支持约束处理方法
    constraint_method = handling_method.get("hard_constraint", "")

    # 示例：如果约束方法是repair，算法需要支持repair
    if "repair" in constraint_method.lower():
        if not algorithm_capabilities.get("supports_repair", True):
            check_result["status"] = "WARNING"
            check_result["mismatches"].append({
                "type": "capability_mismatch",
                "description": f"算法 '{selected_algorithm}' 可能不支持repair方法处理硬约束",
                "severity": "high",
                "recommendation": "选择支持repair的算法或改用penalty方法"
            })

    # 检查算法是否适合约束类型
    # 例如：Genetic Algorithm适合处理复杂约束，Tabu Search适合邻域搜索

    if check_result["mismatches"]:
        print(f"⚠️ 算法-约束匹配检查: 发现{len(check_result['mismatches'])}个不匹配")
    else:
        print("✓ 算法-约束匹配检查: 通过")

    return check_result
```

### 步骤5: 检查算法与目标的匹配

```python
def check_algorithm_objective_match(algorithm_decisions, objective_decisions):
    """
    检查算法是否能有效优化目标

    Returns:
        dict: 匹配检查结果
    """
    check_result = {
        "check_name": "算法 vs 目标匹配",
        "status": "PASS",
        "mismatches": []
    }

    selected_algorithm = algorithm_decisions.get("selected_algorithm", "")
    multi_objective_approach = objective_decisions.get("multi_objective_approach", "")

    secondary_objectives = objective_decisions.get("secondary_objectives", [])

    # 如果是多目标问题，检查算法是否支持
    if len(secondary_objectives) > 0:
        # 检查算法是否适合多目标优化
        multi_obj_algorithms = ["NSGA-II", "MOEA", "Multi-objective"]

        if not any(mo_alg in selected_algorithm for mo_alg in multi_obj_algorithms):
            if multi_objective_approach == "pareto":
                check_result["status"] = "WARNING"
                check_result["mismatches"].append({
                    "type": "multi_objective_mismatch",
                    "description": f"多目标优化方法为Pareto，但算法 '{selected_algorithm}' 可能不支持",
                    "severity": "high",
                    "recommendation": "考虑使用加权和方法或选择多目标算法"
                })

    if check_result["mismatches"]:
        print(f"⚠️ 算法-目标匹配检查: 发现{len(check_result['mismatches'])}个不匹配")
    else:
        print("✓ 算法-目标匹配检查: 通过")

    return check_result
```

### 步骤6: 生成一致性报告

```python
from datetime import datetime

def generate_consistency_report(all_checks):
    """
    生成完整的一致性报告

    Args:
        all_checks: 所有检查结果列表

    Returns:
        dict: 一致性报告
    """
    # 汇总所有问题
    all_issues = []
    all_conflicts = []
    all_mismatches = []

    for check in all_checks:
        all_issues.extend(check.get("issues", []))
        all_conflicts.extend(check.get("conflicts", []))
        all_mismatches.extend(check.get("mismatches", []))

    # 确定总体状态
    if all_issues or all_conflicts or all_mismatches:
        if any(item.get("severity") == "high" for item in all_issues + all_conflicts + all_mismatches):
            overall_status = "FAIL"
        else:
            overall_status = "WARNING"
    else:
        overall_status = "PASS"

    # 生成报告
    consistency_report = {
        "metadata": {
            "checked_at": datetime.now().isoformat(),
            "version": "4.3",
            "phase": "Phase 2"
        },

        "overall_status": overall_status,

        "summary": {
            "total_checks": len(all_checks),
            "passed_checks": sum(1 for c in all_checks if c["status"] == "PASS"),
            "warning_checks": sum(1 for c in all_checks if c["status"] == "WARNING"),
            "failed_checks": sum(1 for c in all_checks if c["status"] == "FAIL"),
            "total_issues": len(all_issues) + len(all_conflicts) + len(all_mismatches)
        },

        "checks": all_checks,

        "issues": all_issues,
        "conflicts": all_conflicts,
        "mismatches": all_mismatches,

        "recommendations": []
    }

    # 生成建议
    if overall_status == "FAIL":
        consistency_report["recommendations"].append({
            "priority": "high",
            "action": "需要解决高严重性问题后才能继续",
            "trigger": "P2级用户仲裁"
        })
    elif overall_status == "WARNING":
        consistency_report["recommendations"].append({
            "priority": "medium",
            "action": "建议审查警告项，但可以继续流程",
            "trigger": "可选的用户确认"
        })
    else:
        consistency_report["recommendations"].append({
            "priority": "low",
            "action": "所有检查通过，可以继续",
            "trigger": "无需用户介入"
        })

    print(f"━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"一致性检查报告")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"总体状态: {overall_status}")
    print(f"通过检查: {consistency_report['summary']['passed_checks']}/{consistency_report['summary']['total_checks']}")
    print(f"发现问题: {consistency_report['summary']['total_issues']}个")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━")

    return consistency_report
```

### 步骤7: 识别需要用户仲裁的冲突

```python
def identify_conflicts_for_arbitration(consistency_report):
    """
    识别需要用户仲裁的冲突

    Returns:
        list: 冲突列表（用于触发Step 2.A.3）
    """
    conflicts = []

    # 收集所有高严重性问题
    all_problems = (
        consistency_report.get("issues", []) +
        consistency_report.get("conflicts", []) +
        consistency_report.get("mismatches", [])
    )

    for problem in all_problems:
        if problem.get("severity") == "high":
            conflicts.append({
                "conflict_type": problem.get("type", "unknown"),
                "description": problem.get("description", ""),
                "severity": "high",
                "involved_experts": extract_experts_from_problem(problem),
                "recommendation": problem.get("recommendation", "")
            })

    if conflicts:
        print(f"⚠️ 需要用户仲裁的冲突: {len(conflicts)}个")
    else:
        print("✓ 无需用户仲裁")

    return conflicts

def extract_experts_from_problem(problem):
    """从问题描述中提取涉及的专家"""
    experts = []
    problem_str = str(problem).lower()

    if "domain" in problem_str or "领域" in problem_str:
        experts.append("领域专家")
    if "constraint" in problem_str or "约束" in problem_str:
        experts.append("约束专家")
    if "objective" in problem_str or "目标" in problem_str:
        experts.append("目标专家")
    if "algorithm" in problem_str or "算法" in problem_str:
        experts.append("算法专家")

    return experts if experts else ["未知"]
```

## 输出

```yaml
outputs:
  consistency_report:
    type: object
    description: 一致性检查报告
    structure:
      metadata: 元数据
      overall_status: string (PASS/WARNING/FAIL)
      summary: 检查统计
      checks: array (各项检查结果)
      issues: array (问题列表)
      conflicts: array (冲突列表)
      mismatches: array (不匹配列表)
      recommendations: array (建议列表)

  conflicts:
    type: array
    description: 需要用户仲裁的高严重性冲突
    trigger_condition: '如果非空，触发Step 2.A.3或用户介入'
```

## 质量检查

- [ ] 所有4个专家分析已检查
- [ ] 领域约束与约束分析一致性已检查
- [ ] 约束与目标兼容性已检查
- [ ] 算法与约束匹配性已检查
- [ ] 算法与目标匹配性已检查
- [ ] 所有高严重性问题已标识
- [ ] 一致性报告完整
- [ ] 如有冲突，已生成conflicts列表

## 一致性检查矩阵

| 检查项  | 专家1 | 专家2 | 检查内容                   |
| ------- | ----- | ----- | -------------------------- |
| Check 1 | 领域  | 约束  | 领域约束是否被约束分析覆盖 |
| Check 2 | 约束  | 目标  | 约束是否阻止目标优化       |
| Check 3 | 算法  | 约束  | 算法能力是否匹配约束处理   |
| Check 4 | 算法  | 目标  | 算法能力是否匹配目标优化   |

## 引用

- @质量评测专家库/一致性检查标准
- @编排协调专家库/冲突识别方法

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 跨专家一致性校验，确保专家分析协调一致
