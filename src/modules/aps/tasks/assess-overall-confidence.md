# Task: Assess Overall Confidence

**任务ID**: `assess-overall-confidence`
**版本**: V1.0
**用途**: Phase 2后 - 综合评估所有专家的置信度，决定是否需要人机交互

**方案依据**: @改进方案/P2-agent-collaboration.md - 置信度传递机制

## 输入

```yaml
inputs:
  - domain_analysis: 领域专家输出（含置信度）
  - constraint_analysis: 约束专家输出（含置信度）
  - objective_analysis: 目标专家输出（含置信度）
  - algorithm_recommendations: 算法专家输出（含置信度）
  - workflow_mode: 当前工作流模式（mode_a/mode_b/mode_c）
```

## 处理逻辑

### 步骤1: 提取专家置信度

```python
def extract_expert_confidence(all_expert_outputs):
    """
    从各专家输出中提取置信度信息

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    """
    confidence_data = {
        "domain": {
            "score": 0.0,
            "breakdown": {},
            "uncertainty_sources": []
        },
        "constraint": {
            "score": 0.0,
            "breakdown": {},
            "uncertainty_sources": []
        },
        "objective": {
            "score": 0.0,
            "breakdown": {},
            "uncertainty_sources": []
        },
        "algorithm": {
            "score": 0.0,
            "breakdown": {},
            "uncertainty_sources": []
        }
    }

    # 提取领域专家置信度
    if "confidence_score" in all_expert_outputs.get("domain_analysis", {}):
        confidence_data["domain"]["score"] = all_expert_outputs["domain_analysis"]["confidence_score"]
        confidence_data["domain"]["breakdown"] = all_expert_outputs["domain_analysis"].get("confidence_breakdown", {})
        confidence_data["domain"]["uncertainty_sources"] = all_expert_outputs["domain_analysis"].get("uncertainty_sources", [])
    else:
        # 如果没有置信度信息，使用默认值
        confidence_data["domain"]["score"] = 0.75
        confidence_data["domain"]["uncertainty_sources"] = ["未提供置信度评估"]

    # 提取约束专家置信度
    if "confidence_score" in all_expert_outputs.get("constraint_analysis", {}):
        confidence_data["constraint"]["score"] = all_expert_outputs["constraint_analysis"]["confidence_score"]
        confidence_data["constraint"]["breakdown"] = all_expert_outputs["constraint_analysis"].get("confidence_breakdown", {})
        confidence_data["constraint"]["uncertainty_sources"] = all_expert_outputs["constraint_analysis"].get("uncertainty_sources", [])
    else:
        confidence_data["constraint"]["score"] = 0.75
        confidence_data["constraint"]["uncertainty_sources"] = ["未提供置信度评估"]

    # 提取目标专家置信度
    if "confidence_score" in all_expert_outputs.get("objective_analysis", {}):
        confidence_data["objective"]["score"] = all_expert_outputs["objective_analysis"]["confidence_score"]
        confidence_data["objective"]["breakdown"] = all_expert_outputs["objective_analysis"].get("confidence_breakdown", {})
        confidence_data["objective"]["uncertainty_sources"] = all_expert_outputs["objective_analysis"].get("uncertainty_sources", [])
    else:
        confidence_data["objective"]["score"] = 0.75
        confidence_data["objective"]["uncertainty_sources"] = ["未提供置信度评估"]

    # 提取算法专家置信度
    if "confidence_score" in all_expert_outputs.get("algorithm_recommendations", {}):
        confidence_data["algorithm"]["score"] = all_expert_outputs["algorithm_recommendations"]["confidence_score"]
        confidence_data["algorithm"]["breakdown"] = all_expert_outputs["algorithm_recommendations"].get("confidence_breakdown", {})
        confidence_data["algorithm"]["uncertainty_sources"] = all_expert_outputs["algorithm_recommendations"].get("uncertainty_sources", [])
    else:
        confidence_data["algorithm"]["score"] = 0.75
        confidence_data["algorithm"]["uncertainty_sources"] = ["未提供置信度评估"]

    return confidence_data
```

### 步骤2: 计算综合置信度

```python
def calculate_overall_confidence(confidence_data):
    """
    计算加权综合置信度

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 综合评估整体置信度，关键专家权重更高
    """
    # 专家权重配置
    weights = {
        "domain": 0.20,      # 领域专家：提供上下文
        "constraint": 0.30,  # 约束专家：最关键，直接影响可行性
        "objective": 0.25,   # 目标专家：重要，影响优化方向
        "algorithm": 0.25    # 算法专家：重要，影响求解效果
    }

    # 计算加权平均
    overall_score = sum(
        confidence_data[expert]["score"] * weights[expert]
        for expert in weights.keys()
    )

    # 识别薄弱环节（置信度 < 0.70）
    weak_points = [
        expert
        for expert, data in confidence_data.items()
        if data["score"] < 0.70
    ]

    # 收集所有不确定性来源
    all_uncertainty_sources = []
    for expert, data in confidence_data.items():
        for source in data["uncertainty_sources"]:
            all_uncertainty_sources.append({
                "expert": expert,
                "source": source
            })

    return {
        "overall_score": round(overall_score, 3),
        "expert_scores": {
            expert: data["score"]
            for expert, data in confidence_data.items()
        },
        "weak_points": weak_points,
        "uncertainty_sources": all_uncertainty_sources,
        "weights_used": weights
    }
```

### 步骤3: 生成流程建议

```python
def generate_recommendation(overall_confidence, workflow_mode):
    """
    基于置信度和工作流模式生成流程建议

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 动态决定是否需要人机交互
    """
    overall_score = overall_confidence["overall_score"]
    weak_points = overall_confidence["weak_points"]

    recommendation = {
        "action": "",
        "reason": "",
        "focus_areas": [],
        "human_review_needed": False,
        "review_type": None,
        "priority_level": ""
    }

    # Mode A: 集中确认模式
    if workflow_mode == "mode_a":
        if overall_score >= 0.85:
            recommendation["action"] = "auto_proceed"
            recommendation["reason"] = "综合置信度高（≥0.85），可自动继续"
            recommendation["human_review_needed"] = False
            recommendation["priority_level"] = "low"

        elif overall_score >= 0.70:
            recommendation["action"] = "light_review"
            recommendation["reason"] = "综合置信度中等（0.70-0.85），建议轻度审核"
            recommendation["human_review_needed"] = True
            recommendation["review_type"] = "focused_review"
            recommendation["focus_areas"] = weak_points
            recommendation["priority_level"] = "medium"

        else:  # < 0.70
            recommendation["action"] = "comprehensive_review"
            recommendation["reason"] = "综合置信度较低（<0.70），需要全面审核"
            recommendation["human_review_needed"] = True
            recommendation["review_type"] = "comprehensive_review"
            recommendation["focus_areas"] = weak_points
            recommendation["priority_level"] = "high"

    # Mode B: 增量确认模式
    elif workflow_mode == "mode_b":
        # Mode B 始终需要人机交互
        recommendation["action"] = "incremental_review"
        recommendation["reason"] = "Mode B增量确认模式，需要逐步确认"
        recommendation["human_review_needed"] = True
        recommendation["review_type"] = "incremental_review"

        if overall_score < 0.70:
            recommendation["focus_areas"] = weak_points
            recommendation["priority_level"] = "high"
        elif overall_score < 0.85:
            recommendation["focus_areas"] = weak_points
            recommendation["priority_level"] = "medium"
        else:
            recommendation["priority_level"] = "low"

    # Mode C: 专家模式（未来）
    elif workflow_mode == "mode_c":
        if overall_score >= 0.85:
            recommendation["action"] = "zero_interaction"
            recommendation["reason"] = "Mode C专家模式，高置信度（≥0.85），零交互"
            recommendation["human_review_needed"] = False
            recommendation["priority_level"] = "low"

        else:
            recommendation["action"] = "minimal_review"
            recommendation["reason"] = "Mode C专家模式，置信度<0.85，最小化审核"
            recommendation["human_review_needed"] = True
            recommendation["review_type"] = "minimal_review"
            recommendation["focus_areas"] = weak_points
            recommendation["priority_level"] = "medium"

    return recommendation
```

### 步骤4: 生成详细报告

```python
def generate_confidence_report(confidence_data, overall_confidence, recommendation):
    """
    生成详细的置信度评估报告

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    """
    report = {
        "summary": {
            "overall_score": overall_confidence["overall_score"],
            "level": "",
            "human_review_needed": recommendation["human_review_needed"]
        },

        "expert_details": {},

        "weak_points_analysis": [],

        "recommendation": recommendation,

        "next_steps": []
    }

    # 综合置信度级别
    score = overall_confidence["overall_score"]
    if score >= 0.85:
        report["summary"]["level"] = "高置信度"
    elif score >= 0.70:
        report["summary"]["level"] = "中等置信度"
    else:
        report["summary"]["level"] = "低置信度"

    # 各专家详情
    for expert, data in confidence_data.items():
        report["expert_details"][expert] = {
            "score": data["score"],
            "status": "✅ 良好" if data["score"] >= 0.70 else "⚠️ 需关注",
            "breakdown": data["breakdown"],
            "uncertainty_sources": data["uncertainty_sources"]
        }

    # 薄弱点分析
    for expert in overall_confidence["weak_points"]:
        data = confidence_data[expert]
        report["weak_points_analysis"].append({
            "expert": expert,
            "score": data["score"],
            "main_issues": data["uncertainty_sources"]
        })

    # 下一步行动
    if recommendation["human_review_needed"]:
        if recommendation["review_type"] == "comprehensive_review":
            report["next_steps"].append("进行全面人工审核")
            report["next_steps"].append(f"重点关注：{', '.join(recommendation['focus_areas'])}")

        elif recommendation["review_type"] == "focused_review":
            report["next_steps"].append("进行重点区域审核")
            report["next_steps"].append(f"审核范围：{', '.join(recommendation['focus_areas'])}")

        elif recommendation["review_type"] == "incremental_review":
            report["next_steps"].append("按照Mode B流程进行增量确认")

        elif recommendation["review_type"] == "minimal_review":
            report["next_steps"].append("进行最小化审核（Mode C）")
            report["next_steps"].append(f"关注点：{', '.join(recommendation['focus_areas'])}")

    else:
        report["next_steps"].append("✅ 置信度充足，自动继续执行")
        report["next_steps"].append("进入Phase 3方案优化")

    return report
```

## 输出

```yaml
outputs:
  - confidence_assessment:
      summary:
        overall_score: 0.782
        level: '中等置信度'
        human_review_needed: true

      expert_details:
        domain:
          score: 0.85
          status: '✅ 良好'
          breakdown:
            knowledge_coverage: 0.90
            problem_similarity: 0.80
          uncertainty_sources: []

        constraint:
          score: 0.75
          status: '✅ 良好'
          breakdown:
            knowledge_coverage: 0.80
            constraint_completeness: 0.70
          uncertainty_sources:
            - '部分软约束优先级不明确'

        objective:
          score: 0.68
          status: '⚠️ 需关注'
          breakdown:
            knowledge_coverage: 0.75
            objective_clarity: 0.60
          uncertainty_sources:
            - '多目标权重需要确认'
            - '稳定性目标定义模糊'

        algorithm:
          score: 0.80
          status: '✅ 良好'
          breakdown:
            knowledge_coverage: 0.85
            problem_similarity: 0.75
          uncertainty_sources: []

      weak_points_analysis:
        - expert: 'objective'
          score: 0.68
          main_issues:
            - '多目标权重需要确认'
            - '稳定性目标定义模糊'

      recommendation:
        action: 'light_review'
        reason: '综合置信度中等（0.70-0.85），建议轻度审核'
        human_review_needed: true
        review_type: 'focused_review'
        focus_areas: ['objective']
        priority_level: 'medium'

      next_steps:
        - '进行重点区域审核'
        - '审核范围：objective'
```

## 执行流程

1. 接收所有专家的输出结果
2. 提取各专家的置信度信息
3. 计算加权综合置信度
4. 识别薄弱环节
5. 基于工作流模式生成流程建议
6. 生成详细的置信度评估报告
7. 输出给工作流引擎决策下一步

## 版本历史

### V1.0 (2025-11-03)

**问题描述**:

- 当前没有置信度评估机制
- 无法动态决定是否需要人机交互
- 人机交互频率固定，不够智能

**新增内容**:

- 创建综合置信度评估任务
- 实现专家置信度提取逻辑
- 实现加权综合置信度计算
- 实现基于置信度的流程建议生成
- 支持三种工作流模式（Mode A/B/C）

**方案依据**:

- @改进方案/P2-agent-collaboration.md - 置信度传递机制
- @改进方案/P2-agent-collaboration.md - 智能人机交互触发

**符合规范**:

- ✅ 版本标注：V1.0
- ✅ 方案依据：标注改进方案来源
- ✅ 渐进式增强：新增任务，不破坏现有流程
- ✅ 详细文档：完整的函数说明和示例输出
