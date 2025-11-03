# Task: Expert Peer Review

**任务ID**: `expert-peer-review`
**版本**: V1.0
**用途**: Phase 2.8 - 专家交叉审核（条件触发），当置信度较低时提升推荐质量

**方案依据**: @改进方案/P2-agent-collaboration.md - 专家协作模式优化 - 专家互审机制

## 触发条件

```yaml
trigger_conditions:
  - overall_confidence < 0.75
  - enable_peer_review: true # 可配置开关
```

## 输入

```yaml
inputs:
  - domain_analysis: 领域专家分析结果
  - constraint_analysis: 约束专家分析结果
  - objective_analysis: 目标专家分析结果
  - algorithm_recommendations: 算法专家推荐结果
  - confidence_assessment: 综合置信度评估结果
```

## 处理逻辑

### 步骤1: 算法专家审核约束合理性

```python
def algorithm_reviews_constraints(algorithm_expert, constraint_analysis):
    """
    算法专家审核约束专家的推荐是否合理

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 从算法实现角度审核约束的可行性和合理性
    """
    review_result = {
        "reviewer": "algorithm_expert",
        "reviewed": "constraint_analysis",
        "findings": [],
        "suggestions": [],
        "consistency_score": 0.0
    }

    constraints = constraint_analysis.get("constraints", {})
    hard_constraints = constraints.get("hard_constraints", [])
    soft_constraints = constraints.get("soft_constraints", [])

    findings = []
    suggestions = []

    # 审核1: 约束数量是否合理
    total_constraints = len(hard_constraints) + len(soft_constraints)
    if total_constraints > 20:
        findings.append({
            "type": "warning",
            "issue": "约束数量过多（>20），可能导致求解困难",
            "severity": "medium"
        })
        suggestions.append({
            "action": "建议约束专家对约束进行优先级排序和简化",
            "rationale": "过多约束会显著增加求解复杂度和时间"
        })

    # 审核2: 硬约束是否过于严格
    if len(hard_constraints) > 10:
        findings.append({
            "type": "warning",
            "issue": "硬约束数量较多（>10），可能导致无可行解",
            "severity": "high"
        })
        suggestions.append({
            "action": "建议将部分硬约束降级为软约束",
            "rationale": "保持求解灵活性，避免无可行解情况"
        })

    # 审核3: 约束冲突检测
    conflict_patterns = [
        ("时间窗", "最短完成时间"),
        ("容量限制", "最大化产出"),
        ("连续作业", "维护窗口")
    ]

    for pattern1, pattern2 in conflict_patterns:
        has_pattern1 = any(pattern1 in str(c) for c in hard_constraints + soft_constraints)
        has_pattern2 = any(pattern2 in str(c) for c in hard_constraints + soft_constraints)

        if has_pattern1 and has_pattern2:
            findings.append({
                "type": "potential_conflict",
                "issue": f"潜在冲突：{pattern1} vs {pattern2}",
                "severity": "medium"
            })
            suggestions.append({
                "action": f"请确认 {pattern1} 和 {pattern2} 的优先级关系",
                "rationale": "避免算法求解时的矛盾约束"
            })

    # 审核4: 约束建模复杂度
    complex_constraint_keywords = ["非线性", "时变", "动态", "随机"]
    complex_constraints = [
        c for c in hard_constraints + soft_constraints
        if any(keyword in str(c) for keyword in complex_constraint_keywords)
    ]

    if complex_constraints:
        findings.append({
            "type": "complexity_alert",
            "issue": f"发现{len(complex_constraints)}个复杂约束",
            "details": complex_constraints[:3],  # 只列出前3个
            "severity": "medium"
        })
        suggestions.append({
            "action": "建议使用启发式算法或近似方法处理复杂约束",
            "rationale": "精确求解可能耗时过长"
        })

    # 计算一致性评分
    issues_count = len(findings)
    if issues_count == 0:
        consistency_score = 1.0
    elif issues_count <= 2:
        consistency_score = 0.8
    elif issues_count <= 4:
        consistency_score = 0.6
    else:
        consistency_score = 0.4

    review_result["findings"] = findings
    review_result["suggestions"] = suggestions
    review_result["consistency_score"] = consistency_score

    return review_result
```

### 步骤2: 约束专家审核目标可行性

```python
def constraint_reviews_objectives(constraint_expert, objective_analysis):
    """
    约束专家审核目标专家的推荐是否可行

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 从约束满足角度审核目标的可行性
    """
    review_result = {
        "reviewer": "constraint_expert",
        "reviewed": "objective_analysis",
        "findings": [],
        "suggestions": [],
        "consistency_score": 0.0
    }

    objectives = objective_analysis.get("objectives", {})
    primary_objectives = objectives.get("primary", [])
    secondary_objectives = objectives.get("secondary", [])

    findings = []
    suggestions = []

    # 审核1: 目标数量
    total_objectives = len(primary_objectives) + len(secondary_objectives)
    if total_objectives > 4:
        findings.append({
            "type": "warning",
            "issue": "目标函数数量过多（>4），权重平衡困难",
            "severity": "medium"
        })
        suggestions.append({
            "action": "建议将次要目标合并或降级",
            "rationale": "过多目标会导致优化方向不明确"
        })

    # 审核2: 目标冲突检测
    conflicting_pairs = [
        ("成本最小化", "时间最小化"),
        ("效率最大化", "稳定性最大化"),
        ("产出最大化", "能耗最小化")
    ]

    for obj1, obj2 in conflicting_pairs:
        has_obj1 = any(obj1 in str(o) for o in primary_objectives + secondary_objectives)
        has_obj2 = any(obj2 in str(o) for o in primary_objectives + secondary_objectives)

        if has_obj1 and has_obj2:
            findings.append({
                "type": "objective_conflict",
                "issue": f"目标冲突：{obj1} vs {obj2}",
                "severity": "high"
            })
            suggestions.append({
                "action": f"请明确 {obj1} 和 {obj2} 的权重关系",
                "rationale": "冲突目标需要清晰的优先级定义"
            })

    # 审核3: 目标与约束的一致性
    # 检查目标是否与约束矛盾
    if "时间最小化" in str(objectives):
        # 检查是否存在时间窗约束
        if "时间窗" in str(constraint_expert):
            findings.append({
                "type": "info",
                "issue": "目标追求时间最小化，但存在时间窗约束",
                "severity": "low"
            })
            suggestions.append({
                "action": "确认时间窗约束不会过度限制时间优化",
                "rationale": "保证目标函数有优化空间"
            })

    # 审核4: 权重合理性
    weights = objective_analysis.get("weights", {})
    if weights:
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            findings.append({
                "type": "error",
                "issue": f"权重总和不为1（当前：{weight_sum}）",
                "severity": "high"
            })
            suggestions.append({
                "action": "请调整权重使总和为1",
                "rationale": "权重归一化是标准要求"
            })

        # 检查是否有权重过小的目标
        small_weight_objectives = [obj for obj, w in weights.items() if w < 0.1]
        if small_weight_objectives:
            findings.append({
                "type": "warning",
                "issue": f"部分目标权重过小（<0.1）：{small_weight_objectives}",
                "severity": "low"
            })
            suggestions.append({
                "action": "考虑移除权重过小的目标或提高其权重",
                "rationale": "权重过小的目标实际影响有限"
            })

    # 计算一致性评分
    high_severity_count = sum(1 for f in findings if f.get("severity") == "high")
    medium_severity_count = sum(1 for f in findings if f.get("severity") == "medium")

    if high_severity_count > 0:
        consistency_score = 0.5
    elif medium_severity_count > 2:
        consistency_score = 0.6
    elif medium_severity_count > 0:
        consistency_score = 0.75
    else:
        consistency_score = 0.9

    review_result["findings"] = findings
    review_result["suggestions"] = suggestions
    review_result["consistency_score"] = consistency_score

    return review_result
```

### 步骤3: 交叉验证一致性

```python
def cross_validate_consistency(all_expert_outputs, review_results):
    """
    交叉验证所有专家输出的一致性

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 发现专家之间的不一致和潜在问题
    """
    validation_result = {
        "overall_consistency": 0.0,
        "consistency_matrix": {},
        "identified_conflicts": [],
        "resolution_suggestions": []
    }

    conflicts = []
    suggestions = []

    # 验证1: 领域专家 vs 约束专家
    domain_features = all_expert_outputs.get("domain_analysis", {}).get("domain_features", [])
    constraints = all_expert_outputs.get("constraint_analysis", {}).get("constraints", {})

    # 检查领域特征是否在约束中体现
    if "多机器调度" in domain_features:
        if not any("机器" in str(c) for c in constraints.get("hard_constraints", [])):
            conflicts.append({
                "type": "missing_constraint",
                "issue": "领域特征识别出'多机器调度'，但约束中未体现机器相关约束",
                "experts": ["domain", "constraint"]
            })
            suggestions.append({
                "action": "约束专家需补充机器相关约束",
                "priority": "high"
            })

    # 验证2: 约束专家 vs 目标专家
    # 合并审核结果中的发现
    for review in review_results:
        for finding in review.get("findings", []):
            if finding.get("type") in ["objective_conflict", "potential_conflict"]:
                conflicts.append({
                    "type": finding["type"],
                    "issue": finding["issue"],
                    "experts": [review["reviewer"], review["reviewed"]]
                })

        for suggestion in review.get("suggestions", []):
            suggestions.append({
                "action": suggestion["action"],
                "priority": "medium"
            })

    # 验证3: 算法推荐 vs 问题规模
    algorithm = all_expert_outputs.get("algorithm_recommendations", {}).get("primary_algorithm", {})
    domain_scale = all_expert_outputs.get("domain_analysis", {}).get("problem_scale", {})

    if domain_scale.get("level") == "large":
        if algorithm.get("name") in ["branch_and_bound", "dynamic_programming"]:
            conflicts.append({
                "type": "algorithm_scale_mismatch",
                "issue": f"问题规模较大，但推荐了精确算法 {algorithm.get('name')}",
                "experts": ["domain", "algorithm"]
            })
            suggestions.append({
                "action": "建议算法专家重新考虑，改用元启发式算法",
                "priority": "high"
            })

    # 计算一致性矩阵
    consistency_matrix = {
        "domain_vs_constraint": 0.9,
        "constraint_vs_objective": review_results[1]["consistency_score"] if len(review_results) > 1 else 0.8,
        "algorithm_vs_constraint": review_results[0]["consistency_score"] if len(review_results) > 0 else 0.8
    }

    # 计算总体一致性
    overall_consistency = sum(consistency_matrix.values()) / len(consistency_matrix)

    validation_result["overall_consistency"] = round(overall_consistency, 3)
    validation_result["consistency_matrix"] = consistency_matrix
    validation_result["identified_conflicts"] = conflicts
    validation_result["resolution_suggestions"] = suggestions

    return validation_result
```

### 步骤4: 生成审核报告

```python
def generate_peer_review_report(review_results, validation_result):
    """
    生成专家互审报告

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    """
    report = {
        "summary": {
            "review_triggered": True,
            "overall_consistency": validation_result["overall_consistency"],
            "total_issues_found": 0,
            "critical_issues": 0,
            "recommendations_count": 0
        },

        "review_details": review_results,

        "cross_validation": validation_result,

        "action_items": [],

        "impact_assessment": ""
    }

    # 统计问题数量
    total_issues = 0
    critical_issues = 0

    for review in review_results:
        total_issues += len(review.get("findings", []))
        critical_issues += sum(
            1 for f in review.get("findings", [])
            if f.get("severity") == "high"
        )

    total_issues += len(validation_result.get("identified_conflicts", []))

    report["summary"]["total_issues_found"] = total_issues
    report["summary"]["critical_issues"] = critical_issues

    # 收集所有建议
    all_suggestions = []
    for review in review_results:
        all_suggestions.extend(review.get("suggestions", []))
    all_suggestions.extend(validation_result.get("resolution_suggestions", []))

    report["summary"]["recommendations_count"] = len(all_suggestions)

    # 生成行动项（按优先级排序）
    high_priority = [s for s in all_suggestions if s.get("priority") == "high"]
    medium_priority = [s for s in all_suggestions if s.get("priority") == "medium"]
    other_priority = [s for s in all_suggestions if s.get("priority") not in ["high", "medium"]]

    report["action_items"] = high_priority + medium_priority + other_priority

    # 影响评估
    if critical_issues > 0:
        report["impact_assessment"] = "发现严重问题，强烈建议人工审核并修正"
    elif total_issues > 5:
        report["impact_assessment"] = "发现多个问题，建议人工审核关键部分"
    elif total_issues > 0:
        report["impact_assessment"] = "发现少量问题，可继续执行但需关注"
    else:
        report["impact_assessment"] = "专家推荐一致性良好，可安全继续"

    return report
```

## 输出

```yaml
outputs:
  - peer_review_report:
      summary:
        review_triggered: true
        overall_consistency: 0.752
        total_issues_found: 6
        critical_issues: 1
        recommendations_count: 8

      review_details:
        - reviewer: 'algorithm_expert'
          reviewed: 'constraint_analysis'
          consistency_score: 0.8
          findings:
            - type: 'warning'
              issue: '硬约束数量较多（>10），可能导致无可行解'
              severity: 'high'
          suggestions:
            - action: '建议将部分硬约束降级为软约束'
              rationale: '保持求解灵活性'

        - reviewer: 'constraint_expert'
          reviewed: 'objective_analysis'
          consistency_score: 0.75
          findings:
            - type: 'objective_conflict'
              issue: '目标冲突：成本最小化 vs 时间最小化'
              severity: 'high'
          suggestions:
            - action: '请明确成本和时间的权重关系'
              rationale: '冲突目标需要清晰的优先级'

      cross_validation:
        overall_consistency: 0.752
        consistency_matrix:
          domain_vs_constraint: 0.9
          constraint_vs_objective: 0.75
          algorithm_vs_constraint: 0.8
        identified_conflicts:
          - type: 'objective_conflict'
            issue: '目标冲突：成本最小化 vs 时间最小化'
            experts: ['constraint', 'objective']

      action_items:
        - action: '建议将部分硬约束降级为软约束'
          priority: 'high'
        - action: '请明确成本和时间的权重关系'
          priority: 'high'

      impact_assessment: '发现严重问题，强烈建议人工审核并修正'
```

## 执行流程

1. 检查触发条件（overall_confidence < 0.75）
2. 算法专家审核约束合理性
3. 约束专家审核目标可行性
4. 交叉验证所有专家输出的一致性
5. 生成详细的审核报告
6. 输出给工作流引擎决策下一步

## 版本历史

### V1.0 (2025-11-03)

**问题描述**:

- 专家团队独立工作，缺少互审机制
- 推荐结果可能存在不一致和冲突
- 置信度低时没有额外的质量保障措施

**新增内容**:

- 创建专家互审任务（条件触发）
- 实现算法专家审核约束逻辑
- 实现约束专家审核目标逻辑
- 实现交叉验证一致性逻辑
- 生成详细的审核报告

**方案依据**:

- @改进方案/P2-agent-collaboration.md - 专家协作模式优化 - 专家互审机制

**符合规范**:

- ✅ 版本标注：V1.0
- ✅ 方案依据：标注改进方案来源
- ✅ 渐进式增强：条件触发，不影响正常流程
- ✅ 详细文档：完整的函数说明和示例输出
