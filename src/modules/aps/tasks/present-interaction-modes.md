# Task: Present Interaction Modes

**任务ID**: `present-interaction-modes`
**版本**: V4.3
**用途**: Phase 0.5.1 - 向用户呈现双模式交互的对比信息

## 输入

```yaml
inputs:
  - initial_understanding: Phase 0初步分析结果
  - complexity_assessment: 问题复杂度评估
```

## 双模式介绍

### 模式A：集中确认模式

**特点**：
- 快速高效，全局视角
- 一次性呈现完整TenElementModel
- 并行调用所有专家
- 适合熟悉调度优化的专家用户

**流程**：
- Phase 1.5：一次性确认完整十要素模型（10-15分钟）
- Phase 2：并行调用所有专家（10-15分钟）
- 总时间：70-95分钟

**优点**：
- 时间最短
- 全局决策，避免返工
- 适合清晰需求

**缺点**：
- 信息量大，需要较强理解能力
- 不适合不确定性高的场景

### 模式B：增量确认模式

**特点**：
- 渐进式，上下文丰富
- 分步骤呈现和确认
- 串行调用专家，逐步细化
- 适合业务用户或需求不明确的场景

**流程**：
- Phase 1.5：仅确认十要素框架（5-8分钟）
- Phase 2：分4步增量确认（31-48分钟）
  - 2.1 领域专家确认
  - 2.2 约束专家确认
  - 2.3 目标专家确认
  - 2.4 算法专家确认
- 总时间：95-130分钟

**优点**：
- 逐步理解，上下文丰富
- 每步决策都有前序结果支撑
- 适合探索式需求

**缺点**：
- 时间较长
- 可能需要局部返工

## 处理逻辑

### 步骤1: 分析用户特征

```python
def analyze_user_profile(initial_understanding, complexity_assessment):
    """
    分析用户特征，推荐合适模式
    """
    # 复杂度因素
    complexity_level = complexity_assessment["level"]

    # 需求明确度
    confidence = initial_understanding["confidence"]

    # 推荐逻辑
    if complexity_level <= 2 and confidence >= 0.7:
        recommendation = "mode_a"
        reason = "需求明确且复杂度适中，推荐集中确认模式以节省时间"
    elif confidence < 0.5:
        recommendation = "mode_b"
        reason = "需求不够明确，推荐增量确认模式以逐步细化"
    elif complexity_level >= 3:
        recommendation = "mode_b"
        reason = "问题较复杂，推荐增量确认模式以降低认知负担"
    else:
        recommendation = "user_choice"
        reason = "两种模式都适合，请根据个人偏好选择"

    return {
        "recommended_mode": recommendation,
        "reason": reason,
        "user_profile": {
            "complexity_level": complexity_level,
            "confidence": confidence
        }
    }
```

### 步骤2: 生成对比表格

```python
def generate_mode_comparison():
    """
    生成模式对比表格
    """
    comparison = {
        "dimensions": [
            {
                "name": "时间投入",
                "mode_a": "70-95分钟",
                "mode_b": "95-130分钟",
                "winner": "mode_a"
            },
            {
                "name": "决策方式",
                "mode_a": "一次性全局决策",
                "mode_b": "分步渐进式决策",
                "winner": "depends"
            },
            {
                "name": "认知负担",
                "mode_a": "较高（一次性信息量大）",
                "mode_b": "较低（分步呈现）",
                "winner": "mode_b"
            },
            {
                "name": "上下文丰富度",
                "mode_a": "中等",
                "mode_b": "高（每步都有前序结果）",
                "winner": "mode_b"
            },
            {
                "name": "适合用户",
                "mode_a": "专家用户",
                "mode_b": "业务用户",
                "winner": "depends"
            },
            {
                "name": "需求明确度要求",
                "mode_a": "高",
                "mode_b": "低（可探索）",
                "winner": "depends"
            }
        ],
        "phase_breakdown": {
            "mode_a": {
                "phase_1.5": "10-15分钟（完整确认）",
                "phase_2": "10-15分钟（并行）",
                "total": "70-95分钟"
            },
            "mode_b": {
                "phase_1.5": "5-8分钟（框架确认）",
                "phase_2": "31-48分钟（分4步）",
                "total": "95-130分钟"
            }
        }
    }

    return comparison
```

### 步骤3: 生成呈现文本

```python
def generate_presentation_text(comparison, recommendation):
    """
    生成用户友好的呈现文本
    """
    text = f"""
## 🔀 交互模式选择

为了给您最佳的体验，APS提供两种交互模式：

### 📊 模式对比

| 维度 | 模式A（集中确认） | 模式B（增量确认） |
|------|------------------|------------------|
"""

    for dim in comparison["dimensions"]:
        text += f"| {dim['name']} | {dim['mode_a']} | {dim['mode_b']} |\n"

    text += f"""

### ⏱️ 时间分解

**模式A**：{comparison['phase_breakdown']['mode_a']['total']}
- Phase 1.5: {comparison['phase_breakdown']['mode_a']['phase_1.5']}
- Phase 2: {comparison['phase_breakdown']['mode_a']['phase_2']}

**模式B**：{comparison['phase_breakdown']['mode_b']['total']}
- Phase 1.5: {comparison['phase_breakdown']['mode_b']['phase_1.5']}
- Phase 2: {comparison['phase_breakdown']['mode_b']['phase_2']}

### 💡 推荐

{recommendation['reason']}

**建议模式**：{recommendation['recommended_mode'].replace('_', ' ').title()}
"""

    return text
```

## 输出

```yaml
outputs:
  mode_comparison:
    type: object
    structure:
      dimensions: array
      phase_breakdown: object
      presentation_text: string

  recommendation:
    type: object
    structure:
      recommended_mode: string (mode_a | mode_b | user_choice)
      reason: string
      user_profile: object
```

## 示例输出

```json
{
  "mode_comparison": {
    "dimensions": [
      {
        "name": "时间投入",
        "mode_a": "70-95分钟",
        "mode_b": "95-130分钟",
        "winner": "mode_a"
      }
    ],
    "phase_breakdown": {
      "mode_a": {
        "phase_1.5": "10-15分钟（完整确认）",
        "phase_2": "10-15分钟（并行）",
        "total": "70-95分钟"
      },
      "mode_b": {
        "phase_1.5": "5-8分钟（框架确认）",
        "phase_2": "31-48分钟（分4步）",
        "total": "95-130分钟"
      }
    },
    "presentation_text": "## 🔀 交互模式选择\n\n..."
  },
  "recommendation": {
    "recommended_mode": "mode_b",
    "reason": "问题较复杂，推荐增量确认模式以降低认知负担",
    "user_profile": {
      "complexity_level": 3,
      "confidence": 0.65
    }
  }
}
```

## 质量检查

- [ ] 对比表格信息完整
- [ ] 推荐逻辑合理
- [ ] 呈现文本清晰易懂
- [ ] 考虑了用户特征
- [ ] 时间估算准确

## 引用

- @编排协调专家库/双模式交互设计
- V4.3架构规范: Phase 0.5 交互模式选择
- @用户体验规范/模式推荐策略

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 智能模式推荐，提升用户体验
