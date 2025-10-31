# P2: 智能体协作机制优化

**优先级**: 🟢 P2 - 持续优化
**预计工期**: 持续改进
**负责模块**: Phase 2 专家协调
**影响范围**: 专家智能体团队

---

## 📋 问题描述

### 现状

**专家协作不够紧密**:

```
当前模式:
  领域专家 ─┐
  约束专家 ─┼─→ 并行执行，独立输出
  目标专家 ─┤
  算法专家 ─┘

问题:
  → 缺少知识共享
  → 推荐可能不一致
  → 置信度未传递
  → 人机交互频繁
```

---

## 🎯 解决方案

### 1. 跨专家知识共享机制

#### 1.1 专家知识预共享步骤

**文件**: `bmad/aps/workflows/scheduling-orchestration/workflow.yaml`

**位置**: Step 2.0之后新增

```yaml
- step_id: '2.0.5'
  name: '🔗 专家知识预共享'
  action: 'exec'
  target: 'bmad/aps/tasks/share-expert-insights.md'
  description: '在各专家开始分析前，共享相关的领域知识，提升协作效果'

  inputs:
    - ten_element_model: '${phase_1_5_state.state_data.ten_element_model}'
    - domain_type: '${initial_analysis.domain_type}'

  outputs:
    - shared_context:
        from_domain_expert:
          - '制造业特点: 机器故障率高，需要考虑鲁棒性'
          - '业务规则: 急单优先，不能跨班次'
          - '实践建议: 维护窗口需要灵活调整'

        implications:
          for_algorithm_expert:
            - '优先考虑鲁棒性算法，如禁忌搜索'
            - '参数设置要保守'
          for_constraint_expert:
            - "注意识别'急单优先'这类隐含约束"
            - '班次约束是硬约束，优先级最高'
          for_objective_expert:
            - '除了效率，还要考虑稳定性目标'
            - '多目标权重建议: 稳定性0.4, 效率0.3, 成本0.3'
```

#### 1.2 知识共享任务

**新建文件**: `bmad/aps/tasks/share-expert-insights.md`

````markdown
# Task: Share Expert Insights

**任务ID**: `share-expert-insights`
**版本**: V1.0
**用途**: 在专家分析开始前，共享领域知识和上下文

## 输入

- ten_element_model: 十要素模型（初步）
- domain_type: 领域类型识别结果

## 处理逻辑

### Step 1: 提取领域特征

```python
def extract_domain_characteristics(ten_element_model, domain_type):
    """
    从十要素模型和领域类型中提取关键特征
    """
    characteristics = {
        "domain": domain_type,
        "scale": estimate_problem_scale(ten_element_model),
        "complexity": assess_complexity(ten_element_model),
        "key_constraints": identify_critical_constraints(ten_element_model),
        "business_rules": extract_business_rules(ten_element_model)
    }

    return characteristics
```
````

### Step 2: 生成专家指导

```python
def generate_expert_guidance(characteristics):
    """
    为每个专家生成针对性的指导建议
    """
    guidance = {
        "for_algorithm_expert": [],
        "for_constraint_expert": [],
        "for_objective_expert": []
    }

    # 根据领域特征生成建议
    if characteristics["domain"] == "manufacturing":
        if "机器故障" in characteristics["business_rules"]:
            guidance["for_algorithm_expert"].append(
                "优先考虑鲁棒性算法（禁忌搜索、模拟退火）"
            )
            guidance["for_objective_expert"].append(
                "建议增加稳定性目标，权重0.3-0.4"
            )

    if characteristics["scale"]["large"]:
        guidance["for_algorithm_expert"].append(
            "问题规模较大，建议使用元启发式算法"
        )

    return guidance
```

## 输出

- shared_context: 共享的上下文信息
- expert_guidance: 各专家的针对性指导

````

---

### 2. 置信度传递机制

#### 2.1 专家输出增强

**所有专家输出增加置信度信息**:

```yaml
# 示例：算法专家输出格式

algorithm_recommendations:
  primary_algorithm:
    name: "genetic_algorithm"
    confidence_score: 0.85
    confidence_breakdown:
      knowledge_coverage: 0.90      # 知识库覆盖度
      problem_similarity: 0.80      # 与历史问题相似度
      llm_certainty: 0.85           # LLM的确定性

    uncertainty_sources:
      - "参数配置未经基准测试验证"
      - "问题规模略大，可能影响性能"

    recommendation_basis:
      - from_knowledge_library: "@algorithm-library/genetic-algorithm.md"
      - similarity_cases: ["case_A", "case_B"]
      - confidence_factors: "知识库质量0.95 * 问题匹配度0.85"
````

#### 2.2 综合置信度评估

**新建文件**: `bmad/aps/tasks/assess-overall-confidence.md`

````markdown
# Task: Assess Overall Confidence

**任务ID**: `assess-overall-confidence`
**版本**: V1.0
**用途**: 综合评估所有专家的置信度，决定是否需要人机交互

## 输入

- domain_analysis: 领域专家输出（含置信度）
- constraint_analysis: 约束专家输出（含置信度）
- objective_analysis: 目标专家输出（含置信度）
- algorithm_recommendations: 算法专家输出（含置信度）

## 处理逻辑

```python
def assess_overall_confidence(all_expert_outputs):
    """
    综合评估整体置信度
    """
    # 提取各专家置信度
    confidence_scores = {
        "domain": all_expert_outputs["domain_analysis"]["confidence_score"],
        "constraint": all_expert_outputs["constraint_analysis"]["confidence_score"],
        "objective": all_expert_outputs["objective_analysis"]["confidence_score"],
        "algorithm": all_expert_outputs["algorithm_recommendations"]["confidence_score"]
    }

    # 计算加权平均（关键专家权重更高）
    weights = {
        "domain": 0.20,
        "constraint": 0.30,
        "objective": 0.25,
        "algorithm": 0.25
    }

    overall_score = sum(confidence_scores[k] * weights[k] for k in confidence_scores)

    # 识别薄弱环节
    weak_points = [k for k, v in confidence_scores.items() if v < 0.70]

    # 决策建议
    if overall_score >= 0.85:
        recommendation = "high_confidence_auto_proceed"
    elif overall_score >= 0.70:
        recommendation = "medium_confidence_light_review"
    else:
        recommendation = "low_confidence_human_review"

    return {
        "overall_confidence": overall_score,
        "expert_confidence": confidence_scores,
        "weak_points": weak_points,
        "recommendation": recommendation,
        "human_review_needed": overall_score < 0.70
    }
```
````

## 输出

- overall_confidence: 综合置信度（0-1）
- weak_points: 薄弱环节列表
- recommendation: 流程建议
- human_review_needed: 是否需要人工审核

````

---

### 3. 专家协作模式优化

#### 3.1 从并行到流水线

**Mode A改进** - 从完全并行改为部分串行：

```yaml
# 当前：完全并行
并行: [领域专家, 约束专家, 目标专家, 算法专家]

# 改进：领域专家先行，其他基于领域洞察
步骤1: 领域专家分析
  ↓ (共享领域洞察)
步骤2: 并行 [约束专家, 目标专家] (基于领域洞察)
  ↓ (共享约束和目标)
步骤3: 算法专家推荐 (基于前面所有信息)
````

**优势**:

- 减少信息不一致
- 算法推荐更精准
- 整体质量提升

**代价**:

- 增加5-8分钟执行时间

#### 3.2 专家互审机制

**新增可选步骤**: 专家交叉审核

```yaml
- step_id: '2.8'
  name: '🔍 专家交叉审核（可选）'
  action: 'conditional_exec'
  condition: 'overall_confidence < 0.75 AND enable_peer_review'
  target: 'bmad/aps/tasks/expert-peer-review.md'

  description: '置信度较低时，触发专家交叉审核机制'

  inputs:
    - domain_analysis
    - constraint_analysis
    - objective_analysis
    - algorithm_recommendations

  process:
    - algorithm_expert_reviews_constraints: '算法专家审核约束合理性'
    - constraint_expert_reviews_objectives: '约束专家审核目标可行性'
    - cross_validation: '交叉验证一致性'

  outputs:
    - peer_review_report
    - identified_conflicts
    - resolution_suggestions
```

---

### 4. 智能人机交互触发

#### 4.1 动态交互决策

```python
def decide_human_interaction(overall_confidence, weak_points, mode):
    """
    基于置信度动态决定是否需要人机交互
    """
    decisions = {
        "need_interaction": False,
        "interaction_type": None,
        "focus_areas": []
    }

    # Mode A: 集中确认
    if mode == "mode_a":
        if overall_confidence < 0.70:
            decisions["need_interaction"] = True
            decisions["interaction_type"] = "comprehensive_review"
            decisions["focus_areas"] = weak_points

    # Mode B: 增量确认 - 始终交互
    elif mode == "mode_b":
        decisions["need_interaction"] = True
        decisions["interaction_type"] = "incremental_review"

    # Mode C: 专家模式（未来）- 高置信度时零交互
    elif mode == "mode_c":
        if overall_confidence < 0.85:
            decisions["need_interaction"] = True
            decisions["interaction_type"] = "minimal_review"
            decisions["focus_areas"] = weak_points

    return decisions
```

---

## ✅ 验证清单

- [ ] 专家知识预共享任务已创建
- [ ] 置信度评估任务已创建
- [ ] 所有专家输出包含置信度
- [ ] 综合置信度评估已集成
- [ ] 专家协作模式已优化
- [ ] 动态交互决策已实现
- [ ] 端到端测试通过

---

## 📊 预期收益

### 短期收益

- ✅ 专家推荐一致性提升20%
- ✅ 人机交互频率降低10-15%
- ✅ 整体置信度提升

### 中期收益

- ✅ 人机交互频率降低20%
- ✅ 用户体验改善
- ✅ 推荐质量稳定

### 长期收益

- ✅ 支持Mode C零交互模式
- ✅ 专家团队智能化协作
- ✅ 形成协作最佳实践

---

## 📞 相关资源

- **知识共享任务**: `bmad/aps/tasks/share-expert-insights.md`
- **置信度评估**: `bmad/aps/tasks/assess-overall-confidence.md`
- **工作流配置**: `bmad/aps/workflows/scheduling-orchestration/workflow.yaml`

---

**创建日期**: 2025-10-31
**最后更新**: 2025-10-31
**状态**: ⏳ 待实施
