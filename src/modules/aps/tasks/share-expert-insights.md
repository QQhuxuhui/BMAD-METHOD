# Task: Share Expert Insights

**任务ID**: `share-expert-insights`
**版本**: V1.0
**用途**: Phase 2.0.5 - 在专家分析开始前，共享领域知识和上下文，提升协作效果

**方案依据**: @改进方案/P2-agent-collaboration.md - 跨专家知识共享机制

## 输入

```yaml
inputs:
  - ten_element_model: 十要素模型（Phase 1.5输出）
  - domain_type: 领域类型识别结果（Phase 0.1输出）
  - initial_analysis: 初步分析结果（Phase 0输出）
```

## 处理逻辑

### 步骤1: 提取领域特征

```python
def extract_domain_characteristics(ten_element_model, domain_type):
    """
    从十要素模型和领域类型中提取关键特征

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 识别领域关键特征，为专家提供上下文
    """
    characteristics = {
        "domain": domain_type,
        "scale": {},
        "complexity": {},
        "key_constraints": [],
        "business_rules": [],
        "domain_features": []
    }

    # 1. 评估问题规模
    characteristics["scale"] = estimate_problem_scale(ten_element_model)

    # 2. 评估复杂度
    characteristics["complexity"] = assess_complexity(ten_element_model)

    # 3. 识别关键约束
    characteristics["key_constraints"] = identify_critical_constraints(ten_element_model)

    # 4. 提取业务规则
    characteristics["business_rules"] = extract_business_rules(ten_element_model)

    # 5. 识别领域特定特征
    characteristics["domain_features"] = identify_domain_features(
        ten_element_model,
        domain_type
    )

    return characteristics


def estimate_problem_scale(ten_element_model):
    """
    评估问题规模
    """
    scale = {
        "level": "unknown",
        "indicators": {}
    }

    # 从十要素模型中提取规模指标
    decision_vars = ten_element_model.get("决策变量", {})
    constraints = ten_element_model.get("约束条件", {})

    # 决策变量数量
    var_count = len(decision_vars.get("列表", []))
    scale["indicators"]["decision_variables"] = var_count

    # 约束数量
    constraint_count = len(constraints.get("硬约束", [])) + len(constraints.get("软约束", []))
    scale["indicators"]["constraints"] = constraint_count

    # 判断规模级别
    if var_count > 1000 or constraint_count > 50:
        scale["level"] = "large"
        scale["description"] = "大规模问题"
    elif var_count > 100 or constraint_count > 20:
        scale["level"] = "medium"
        scale["description"] = "中等规模问题"
    else:
        scale["level"] = "small"
        scale["description"] = "小规模问题"

    return scale


def assess_complexity(ten_element_model):
    """
    评估问题复杂度
    """
    complexity = {
        "level": 0,
        "factors": []
    }

    score = 0

    # 因素1: 多目标
    objectives = ten_element_model.get("目标函数", {}).get("列表", [])
    if len(objectives) > 2:
        score += 2
        complexity["factors"].append("多目标优化（>2个目标）")
    elif len(objectives) > 1:
        score += 1
        complexity["factors"].append("双目标优化")

    # 因素2: 动态性
    if "动态" in str(ten_element_model):
        score += 1
        complexity["factors"].append("动态调度特性")

    # 因素3: 不确定性
    if "不确定" in str(ten_element_model) or "随机" in str(ten_element_model):
        score += 1
        complexity["factors"].append("不确定性因素")

    # 因素4: 特殊约束
    constraints = ten_element_model.get("约束条件", {})
    if len(constraints.get("硬约束", [])) > 10:
        score += 1
        complexity["factors"].append("复杂约束体系")

    complexity["level"] = score
    if score >= 4:
        complexity["description"] = "高度复杂"
    elif score >= 2:
        complexity["description"] = "中等复杂"
    else:
        complexity["description"] = "相对简单"

    return complexity


def identify_critical_constraints(ten_element_model):
    """
    识别关键约束
    """
    critical_constraints = []

    constraints = ten_element_model.get("约束条件", {})
    hard_constraints = constraints.get("硬约束", [])

    # 识别必须满足的硬约束
    for constraint in hard_constraints:
        if isinstance(constraint, dict):
            critical_constraints.append({
                "name": constraint.get("名称", "未命名约束"),
                "type": "hard",
                "priority": "critical",
                "description": constraint.get("描述", "")
            })

    return critical_constraints


def extract_business_rules(ten_element_model):
    """
    提取业务规则
    """
    business_rules = []

    # 从业务规则元素中提取
    rules_element = ten_element_model.get("业务规则", {})
    if rules_element:
        for rule in rules_element.get("列表", []):
            if isinstance(rule, str):
                business_rules.append(rule)
            elif isinstance(rule, dict):
                business_rules.append(rule.get("描述", str(rule)))

    # 从约束条件中提取隐含的业务规则
    constraints = ten_element_model.get("约束条件", {})
    for constraint in constraints.get("软约束", []):
        if isinstance(constraint, dict) and "业务" in constraint.get("描述", ""):
            business_rules.append(constraint.get("描述", ""))

    return business_rules


def identify_domain_features(ten_element_model, domain_type):
    """
    识别领域特定特征
    """
    domain_features = []

    # 制造业特征
    if domain_type in ["production_scheduling", "manufacturing"]:
        if "机器" in str(ten_element_model) or "设备" in str(ten_element_model):
            domain_features.append("多机器调度")
        if "故障" in str(ten_element_model) or "维护" in str(ten_element_model):
            domain_features.append("设备可靠性考虑")
        if "班次" in str(ten_element_model):
            domain_features.append("班次管理")

    # 物流配送特征
    if domain_type in ["vehicle_routing", "delivery"]:
        if "路径" in str(ten_element_model) or "routing" in str(ten_element_model).lower():
            domain_features.append("路径优化")
        if "时间窗" in str(ten_element_model):
            domain_features.append("时间窗约束")
        if "容量" in str(ten_element_model):
            domain_features.append("车辆容量约束")

    # 项目调度特征
    if domain_type in ["project_scheduling"]:
        if "依赖" in str(ten_element_model) or "precedence" in str(ten_element_model).lower():
            domain_features.append("任务依赖关系")
        if "资源" in str(ten_element_model):
            domain_features.append("资源约束")

    return domain_features
```

### 步骤2: 生成专家指导

```python
def generate_expert_guidance(characteristics):
    """
    为每个专家生成针对性的指导建议

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    目的: 基于领域特征，为各专家提供针对性建议
    """
    guidance = {
        "for_domain_expert": [],
        "for_constraint_expert": [],
        "for_objective_expert": [],
        "for_algorithm_expert": []
    }

    # 基于领域类型生成建议
    domain = characteristics["domain"]

    # 制造业领域
    if domain in ["production_scheduling", "manufacturing"]:
        guidance["for_domain_expert"].append(
            "关注点：机器故障率、维护窗口、班次管理"
        )

        if "设备可靠性考虑" in characteristics["domain_features"]:
            guidance["for_algorithm_expert"].append(
                "优先考虑鲁棒性算法（禁忌搜索、模拟退火）"
            )
            guidance["for_objective_expert"].append(
                "建议增加稳定性目标，权重0.3-0.4"
            )

        if "班次管理" in characteristics["domain_features"]:
            guidance["for_constraint_expert"].append(
                "班次约束通常是硬约束，优先级最高"
            )

    # 物流配送领域
    elif domain in ["vehicle_routing", "delivery"]:
        guidance["for_domain_expert"].append(
            "关注点：路径优化、时间窗、车辆容量"
        )

        if "时间窗约束" in characteristics["domain_features"]:
            guidance["for_constraint_expert"].append(
                "时间窗约束需要精确建模，注意软/硬时间窗区分"
            )
            guidance["for_algorithm_expert"].append(
                "推荐使用改进的遗传算法或蚁群算法处理时间窗"
            )

    # 项目调度领域
    elif domain in ["project_scheduling"]:
        guidance["for_domain_expert"].append(
            "关注点：任务依赖、资源约束、关键路径"
        )

        if "任务依赖关系" in characteristics["domain_features"]:
            guidance["for_constraint_expert"].append(
                "任务依赖关系（precedence）是核心约束，必须严格满足"
            )

    # 基于规模生成建议
    scale_level = characteristics["scale"]["level"]

    if scale_level == "large":
        guidance["for_algorithm_expert"].append(
            "问题规模较大，建议使用元启发式算法（遗传算法、粒子群等）"
        )
        guidance["for_algorithm_expert"].append(
            "考虑并行化或分治策略提升求解效率"
        )
    elif scale_level == "small":
        guidance["for_algorithm_expert"].append(
            "问题规模较小，可考虑精确算法（整数规划、分支定界）"
        )

    # 基于复杂度生成建议
    complexity_level = characteristics["complexity"]["level"]

    if complexity_level >= 3:
        guidance["for_domain_expert"].append(
            "问题复杂度较高，需要深入理解业务规则"
        )
        guidance["for_constraint_expert"].append(
            "建议对约束进行优先级排序和分类"
        )
        guidance["for_objective_expert"].append(
            "多目标情况下，建议明确权重或使用帕累托前沿方法"
        )

    # 基于业务规则生成建议
    for rule in characteristics["business_rules"]:
        if "急单" in rule or "优先" in rule:
            guidance["for_constraint_expert"].append(
                f"注意识别隐含约束：{rule}"
            )
            guidance["for_objective_expert"].append(
                "优先级相关的业务规则可能需要体现在目标函数中"
            )

    return guidance


def generate_shared_context(characteristics, guidance):
    """
    生成共享上下文信息

    V1.0新增 - 方案依据: @改进方案/P2-agent-collaboration.md
    """
    shared_context = {
        "domain_summary": {
            "type": characteristics["domain"],
            "scale": characteristics["scale"]["description"],
            "complexity": characteristics["complexity"]["description"],
            "key_features": characteristics["domain_features"]
        },

        "critical_points": {
            "constraints": characteristics["key_constraints"],
            "business_rules": characteristics["business_rules"]
        },

        "expert_guidance": guidance,

        "collaboration_hints": []
    }

    # 生成协作提示
    if len(characteristics["business_rules"]) > 3:
        shared_context["collaboration_hints"].append(
            "业务规则较多，建议约束专家和目标专家密切协作"
        )

    if characteristics["complexity"]["level"] >= 3:
        shared_context["collaboration_hints"].append(
            "问题复杂度高，建议算法专家参考约束专家的优先级排序"
        )

    return shared_context
```

## 输出

```yaml
outputs:
  - shared_context:
      domain_summary:
        type: 'production_scheduling'
        scale: '中等规模问题'
        complexity: '中等复杂'
        key_features: ['多机器调度', '设备可靠性考虑', '班次管理']

      critical_points:
        constraints:
          - name: '班次不跨越约束'
            type: 'hard'
            priority: 'critical'
        business_rules:
          - '急单优先处理'
          - '维护窗口需灵活调整'

      expert_guidance:
        for_domain_expert:
          - '关注点：机器故障率、维护窗口、班次管理'
          - '问题复杂度较高，需要深入理解业务规则'

        for_constraint_expert:
          - '班次约束通常是硬约束，优先级最高'
          - '注意识别隐含约束：急单优先处理'
          - '建议对约束进行优先级排序和分类'

        for_objective_expert:
          - '建议增加稳定性目标，权重0.3-0.4'
          - '优先级相关的业务规则可能需要体现在目标函数中'
          - '多目标情况下，建议明确权重或使用帕累托前沿方法'

        for_algorithm_expert:
          - '优先考虑鲁棒性算法（禁忌搜索、模拟退火）'
          - '问题规模较大，建议使用元启发式算法'

      collaboration_hints:
        - '业务规则较多，建议约束专家和目标专家密切协作'
        - '问题复杂度高，建议算法专家参考约束专家的优先级排序'
```

## 执行流程

1. 接收十要素模型和领域类型
2. 提取领域特征（规模、复杂度、关键约束、业务规则）
3. 为各专家生成针对性指导建议
4. 生成共享上下文信息
5. 输出给后续的Phase 2专家团队

## 版本历史

### V1.0 (2025-11-03)

**问题描述**:

- 当前专家团队完全并行独立执行，缺少知识共享
- 导致推荐可能不一致，人机交互频繁

**新增内容**:

- 创建专家知识预共享任务
- 实现领域特征提取逻辑
- 实现专家指导生成逻辑
- 建立共享上下文机制

**方案依据**:

- @改进方案/P2-agent-collaboration.md - 跨专家知识共享机制

**符合规范**:

- ✅ 版本标注：V1.0
- ✅ 方案依据：标注改进方案来源
- ✅ 渐进式增强：新增任务，不破坏现有流程
- ✅ 详细文档：完整的函数说明和示例输出
