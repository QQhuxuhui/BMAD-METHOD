# Phase 2 至 Phase 4 及验证机制详解

**专家协调、方案集成、质量保证的完整流程与交付物管理**

---

## 6. Phase 2: 专家协调

### 6.1 流程概述

```yaml
Phase名称: Phase 2 - 专家协调
预计时间: 10-48分钟（取决于模式）
主导智能体: Orchestrator
协作智能体: Domain Expert, Constraint Expert, Objective Expert, Algorithm Expert
目标: 4位专家基于TenElementModel提供专业分析建议
关键特性: 模式A并行 vs 模式B串行、跨专家一致性校验
```

### 6.2 模式 A: 并行协调流程

**适用场景**: 专家用户，需求清晰

**流程图**:
```
TenElementModel (Phase 1.5)
         ↓
    [并行调用4专家]
         ├────→ Domain Expert (领域专家) ──→ 领域分析报告
         ├────→ Constraint Expert (约束专家) ──→ 约束分析报告
         ├────→ Objective Expert (目标专家) ──→ 目标分析报告
         └────→ Algorithm Expert (算法专家) ──→ 算法推荐报告
         ↓
    [同步等待所有完成]
         ↓
    跨专家一致性校验
         ↓
    💾 保存 Phase 2 状态
```

#### 步骤 2.1: 领域专家分析（并行）

**执行者**: Domain Expert

**输入**:
```yaml
inputs:
  - ten_element_model: object  # 来自 Phase 1.5
  - requirement_analysis: object  # 来自 Phase 1
```

**处理过程**:
```python
def domain_expert_analyze(tem, req_analysis):
    """
    领域专家分析
    """
    # 1. 加载领域专家库
    domain_library = load_knowledge_library(
        "templates/domain-library/README.md"
    )

    # 2. 识别领域特征
    domain_features = identify_domain_features(req_analysis)
    # - 行业: 物流配送
    # - 子领域: 冷链配送
    # - 特殊要求: 温度控制

    # 3. 匹配领域模板
    matched_template = match_domain_template(
        domain_features,
        domain_library
    )
    # 匹配到: @专家库/领域库/vehicle/冷链配送.md

    # 4. 提取领域特定规则
    domain_rules = extract_domain_rules(matched_template)

    # 5. 验证TenElementModel的领域适配性
    adaptation_analysis = analyze_domain_adaptation(tem, domain_rules)

    # 6. 提出领域特定建议
    recommendations = generate_domain_recommendations(
        tem,
        domain_rules,
        adaptation_analysis
    )

    return {
        "domain_analysis": {
            "identified_domain": "物流配送 - 冷链配送",
            "domain_template": matched_template,
            "domain_features": domain_features,
            "domain_rules": domain_rules,
            "adaptation_score": adaptation_analysis.score
        },
        "recommendations": recommendations,
        "citations": [matched_template.path]
    }
```

**输出示例**:
```yaml
domain_analysis:
  identified_domain: "物流配送 - 冷链配送"
  confidence: 0.95

  domain_template:
    name: "冷链配送领域模板"
    path: "@专家库/领域库/vehicle/冷链配送.md"

  domain_features:
    - "货物温度敏感"
    - "时效性要求高"
    - "专用车辆（冷藏车）"
    - "成本结构特殊（冷链加成）"

  domain_rules:
    - rule_id: "DR1"
      name: "冷链温度控制规则"
      description: "全程温度监控，温度异常处理"
      type: "hard_requirement"

    - rule_id: "DR2"
      name: "货物装载顺序规则"
      description: "先装后卸原则，温度敏感商品优先"
      type: "best_practice"

    - rule_id: "DR3"
      name: "配送时间优化规则"
      description: "最小化在途时间，保证新鲜度"
      type: "objective_enhancement"

  adaptation_score: 0.92

recommendations:
  - rec_id: "R1"
    type: "constraint_enhancement"
    description: "建议增加装载顺序约束"
    target_element: "constraints"
    priority: "medium"

  - rec_id: "R2"
    type: "objective_adjustment"
    description: "建议在目标函数中增加新鲜度指标"
    target_element: "objectives.secondary"
    priority: "low"

  - rec_id: "R3"
    type: "parameter_adjustment"
    description: "建议服务时间增加温度检查时间"
    target_element: "time_model.service_time"
    priority: "low"
```

---

#### 步骤 2.2: 约束专家分析（并行）

**执行者**: Constraint Expert

**输入**:
```yaml
inputs:
  - ten_element_model: object
  - domain_analysis: object  # 可选，如果并行则未获得
```

**处理过程**:
```python
def constraint_expert_analyze(tem, domain_analysis=None):
    """
    约束专家分析
    """
    # 1. 加载约束专家库
    constraint_library = load_knowledge_library(
        "templates/constraint-library/README.md"
    )

    # 2. 分析 TEM 中的约束
    constraints = tem.constraints

    # 3. 为每个约束匹配知识模板
    constraint_analysis = []
    for constraint in constraints:
        # 3.1 匹配模板
        template = match_constraint_template(
            constraint,
            constraint_library
        )

        # 3.2 验证约束建模正确性
        validation = validate_constraint_modeling(
            constraint,
            template
        )

        # 3.3 生成约束处理代码模板
        code_template = generate_constraint_code(
            constraint,
            template
        )

        constraint_analysis.append({
            "constraint_id": constraint.id,
            "constraint_name": constraint.name,
            "matched_template": template,
            "validation": validation,
            "code_template": code_template
        })

    # 4. 检查约束完整性
    completeness_check = check_constraint_completeness(
        constraints,
        tem,
        domain_analysis
    )

    # 5. 检查约束一致性
    consistency_check = check_constraint_consistency(constraints)

    # 6. 提出建议
    recommendations = generate_constraint_recommendations(
        constraint_analysis,
        completeness_check,
        consistency_check
    )

    return {
        "constraint_analysis": constraint_analysis,
        "completeness_check": completeness_check,
        "consistency_check": consistency_check,
        "recommendations": recommendations
    }
```

**输出示例**:
```yaml
constraint_analysis:
  - constraint_id: "C1"
    constraint_name: "车辆容量约束"
    constraint_type: "capacity"
    hardness: "hard"

    matched_template:
      name: "车辆容量约束模板"
      path: "@专家库/约束库/capacity/车辆容量约束.md"
      match_score: 0.98

    validation:
      formula_correct: true
      variables_defined: true
      hardness_appropriate: true
      penalty_appropriate: true  # hard约束无罚值

    code_template:
      validation_function: |
        def validate_vehicle_capacity(route, demands, capacity):
            total_demand = sum(demands[i] for i in route)
            return total_demand <= capacity

      repair_function: |
        def repair_capacity_violation(route, demands, capacity):
            # 移除最后几个客户直到满足容量
            while sum(demands[i] for i in route) > capacity:
                route.pop()
            return route

  - constraint_id: "C2"
    constraint_name: "客户时间窗约束"
    constraint_type: "temporal"
    hardness: "soft"

    matched_template:
      name: "时间窗约束模板"
      path: "@专家库/约束库/temporal/时间窗约束.md"
      match_score: 0.95

    validation:
      formula_correct: true
      variables_defined: true
      hardness_appropriate: true
      penalty_appropriate: true  # soft约束有罚值10000

    code_template:
      validation_function: |
        def validate_time_window(arrival_time, tw_start, tw_end):
            return tw_start <= arrival_time <= tw_end

      penalty_function: |
        def calculate_tw_penalty(arrival_time, tw_start, tw_end):
            if arrival_time < tw_start:
                return (tw_start - arrival_time) * 10000
            elif arrival_time > tw_end:
                return (arrival_time - tw_end) * 10000
            return 0

completeness_check:
  all_required_constraints_present: true
  missing_constraints: []
  redundant_constraints: []

consistency_check:
  no_conflicts: true
  conflicts: []

recommendations:
  - rec_id: "CR1"
    type: "constraint_refinement"
    target: "C2"
    description: "建议将客户时间窗约束分为硬时间窗（承诺）和软时间窗（偏好）"
    priority: "low"
```

---

#### 步骤 2.3: 目标专家分析（并行）

**执行者**: Objective Expert

**输出示例**:
```yaml
objective_analysis:
  primary_objective:
    objective_id: "O1"
    objective_name: "总成本最小化"
    objective_type: "cost"

    matched_template:
      name: "成本最小化目标模板"
      path: "@专家库/目标库/cost/成本最小化.md"

    validation:
      formula_correct: true
      components_complete: true
      all_costs_included: true

    recommendations:
      - "建议在成本函数中明确区分固定成本和变动成本"
      - "建议考虑冷链设备折旧成本"

  secondary_objective:
    objective_id: "O2"
    objective_name: "客户满意度最大化"
    objective_type: "quality"

    matched_template:
      name: "满意度优化模板"
      path: "@专家库/目标库/quality/满意度优化.md"

    validation:
      formula_correct: true
      measurable: true
      weight_appropriate: true

  multi_objective_analysis:
    method: "weighted_sum"
    weight_sum: 1.0
    weight_appropriateness: "合理"
    potential_conflicts:
      - conflict: "成本与准时率可能冲突"
        resolution: "通过权重平衡"

  recommendations:
    - rec_id: "OR1"
      description: "建议增加新鲜度作为独立评价指标"
      priority: "medium"
```

---

#### 步骤 2.4: 算法专家分析（并行）

**执行者**: Algorithm Expert

**输出示例**:
```yaml
algorithm_analysis:
  problem_characteristics:
    problem_type: "车辆路径问题 (VRPTW)"
    scale: "中等规模"
    variables_count: 1200  # 12车 × 100客户
    constraints_complexity: "高（4类约束）"
    time_sensitivity: "中（10分钟求解）"

  algorithm_recommendation:
    primary_algorithm:
      name: "遗传算法 (Genetic Algorithm)"
      type: "meta-heuristic"
      path: "@专家库/算法库/meta-heuristic/遗传算法.md"
      confidence: 0.93

      reasons:
        - "适合中等规模问题"
        - "能处理多约束"
        - "解质量稳定"
        - "有丰富的VRPTW应用案例"

      configuration:
        population_size: 100
        crossover_rate: 0.8
        crossover_operator: "Order Crossover (OX)"
        mutation_rate: 0.05
        mutation_operator: "Swap + Inversion"
        selection: "Tournament (size=3)"
        max_generations: 500
        elite_ratio: 0.1

      initialization:
        - method: "节约算法 (Clarke-Wright)"
          ratio: 0.5
        - method: "随机生成"
          ratio: 0.5

      local_search:
        - operator: "2-opt"
          frequency: "每代"
          probability: 0.3
        - operator: "Or-opt"
          frequency: "每10代"
          probability: 0.2
        - operator: "客户重分配"
          frequency: "每20代"
          probability: 0.1

    alternative_algorithms:
      - name: "禁忌搜索 (Tabu Search)"
        confidence: 0.85
        pros: ["更快收敛", "局部搜索能力强"]
        cons: ["参数敏感", "可能陷入局部最优"]

  complexity_analysis:
    time_complexity: "O(G × P × N²)"
    # G=代数, P=种群, N=客户数
    space_complexity: "O(P × N)"
    estimated_runtime: "8-10分钟"

  performance_prediction:
    solution_quality: "预计达到最优解的95%"
    convergence_speed: "预计500代收敛"
    success_rate: "92%"

  implementation_notes:
    - "需要实现修复算子处理容量约束违反"
    - "时间窗约束使用罚函数处理"
    - "建议使用并行评估加速"
```

---

#### 步骤 2.5: 跨专家一致性校验

**执行者**: Orchestrator

**输入**:
```yaml
inputs:
  - domain_analysis: object
  - constraint_analysis: object
  - objective_analysis: object
  - algorithm_analysis: object
```

**处理过程**:
```python
def cross_expert_consistency_check(
    domain_analysis,
    constraint_analysis,
    objective_analysis,
    algorithm_analysis
):
    """
    跨专家一致性校验
    """
    consistency_report = {
        "checks": [],
        "conflicts": [],
        "recommendations": []
    }

    # 检查1: 领域规则与约束的一致性
    domain_rules = domain_analysis.domain_rules
    constraints = constraint_analysis.constraint_analysis

    for rule in domain_rules:
        if rule.type == "hard_requirement":
            # 检查是否有对应的约束
            constraint_exists = any(
                c.constraint_name == rule.name for c in constraints
            )
            if not constraint_exists:
                consistency_report["conflicts"].append({
                    "type": "missing_constraint",
                    "description": f"领域规则'{rule.name}'未建模为约束",
                    "severity": "high"
                })

    # 检查2: 目标与领域规则的一致性
    domain_objectives = [
        r for r in domain_rules if r.type == "objective_enhancement"
    ]
    for obj in domain_objectives:
        # 检查目标函数是否包含此考虑
        pass

    # 检查3: 算法与约束复杂度的匹配
    constraints_count = len(constraints)
    algorithm = algorithm_analysis.algorithm_recommendation.primary_algorithm

    if constraints_count > 5 and algorithm.type == "exact":
        consistency_report["conflicts"].append({
            "type": "algorithm_constraint_mismatch",
            "description": "约束过多，精确算法可能难以求解",
            "severity": "medium"
        })

    # 检查4: 算法与时间要求的匹配
    estimated_runtime = algorithm_analysis.performance_prediction.estimated_runtime
    time_limit = 10  # 分钟

    if estimated_runtime > time_limit:
        consistency_report["conflicts"].append({
            "type": "time_constraint_violation",
            "description": f"算法预计运行{estimated_runtime}分钟，超过限制{time_limit}分钟",
            "severity": "high"
        })

    # 检查5: 目标权重与业务优先级的一致性
    # ...

    # 生成总结
    consistency_report["summary"] = {
        "total_checks": len(consistency_report["checks"]),
        "conflicts_found": len(consistency_report["conflicts"]),
        "high_severity_conflicts": len([
            c for c in consistency_report["conflicts"]
            if c["severity"] == "high"
        ]),
        "overall_consistency": "high" if len(consistency_report["conflicts"]) == 0 else "medium"
    }

    return consistency_report
```

**输出示例**:
```yaml
consistency_report:
  summary:
    total_checks: 8
    conflicts_found: 1
    high_severity_conflicts: 0
    overall_consistency: "high"

  checks:
    - check_id: "CC1"
      name: "领域规则与约束一致性"
      status: "passed"

    - check_id: "CC2"
      name: "目标与领域规则一致性"
      status: "passed"

    - check_id: "CC3"
      name: "算法与约束复杂度匹配"
      status: "passed"

    - check_id: "CC4"
      name: "算法与时间要求匹配"
      status: "passed"

  conflicts:
    - conflict_id: "CF1"
      type: "recommendation_conflict"
      severity: "low"
      description: |
        领域专家建议增加新鲜度指标，但目标专家认为当前
        客户满意度指标已包含，存在冗余。
      resolution: "保持当前设计，新鲜度隐含在满意度中"

  recommendations:
    - rec_id: "CR1"
      description: "建议在Phase 3集成时优先考虑高优先级建议"
      priority: "high"
```

**冲突处理** (P2 级人机交互):

如果发现高严重度冲突，触发用户仲裁：

```markdown
# ⚠️ 专家建议冲突

在专家分析过程中，发现以下冲突需要您的决策：

## 冲突详情

**冲突类型**: 算法时间约束冲突
**严重程度**: 高

**情况说明**:
- 算法专家推荐的遗传算法预计需要 12 分钟运行时间
- 但系统设定的求解时间限制是 10 分钟
- 存在 2 分钟的超时风险

## 解决方案

请选择以下方案之一：

1. **延长时间限制** → 将时间限制调整为 15 分钟
   - ✅ 保证算法充分运行
   - ⚠️ 总流程时间增加

2. **优化算法参数** → 减少种群大小或迭代次数
   - ✅ 控制运行时间
   - ⚠️ 可能影响解的质量（95% → 90%）

3. **更换算法** → 使用更快的禁忌搜索算法
   - ✅ 运行时间 5-7 分钟
   - ⚠️ 算法专家置信度较低（85% vs 93%）

## 您的选择
请选择方案 1、2 或 3，或提供其他想法：
```

---

#### 步骤 2.6: 💾 保存 Phase 2 状态

**保存内容**:
```yaml
# phase_2_state.yaml

metadata:
  phase_id: "phase_2"
  phase_name: "专家协调"
  created_at: "2025-10-29T10:50:00Z"
  completed_at: "2025-10-29T11:05:00Z"
  duration: "15分钟"
  mode: "mode_a"  # 并行模式
  depends_on: ["phase_0", "phase_0_5", "phase_1", "phase_1_5"]

# 核心交付物 1: 领域分析
domain_analysis:
  identified_domain: "物流配送 - 冷链配送"
  domain_template: "@专家库/领域库/vehicle/冷链配送.md"
  domain_features: [...]
  domain_rules: [...]
  recommendations: [...]

# 核心交付物 2: 约束分析
constraint_analysis:
  - constraint_id: "C1"
    analysis: {...}
    code_template: {...}
  # ... 其他约束

# 核心交付物 3: 目标分析
objective_analysis:
  primary_objective: {...}
  secondary_objective: {...}
  multi_objective_analysis: {...}
  recommendations: [...]

# 核心交付物 4: 算法推荐
algorithm_recommendations:
  primary_algorithm:
    name: "遗传算法"
    configuration: {...}
    path: "@专家库/算法库/meta-heuristic/遗传算法.md"
  alternative_algorithms: [...]
  performance_prediction: {...}

# 核心交付物 5: 一致性报告
consistency_report:
  summary: {...}
  checks: [...]
  conflicts: [...]
  recommendations: [...]

# 验证信息
verification:
  all_experts_completed: true
  all_citations_present: true
  consistency_check_passed: true
  conflicts_resolved: true
  validation_passed: true

# 依赖信息
required_by: ["phase_3"]
```

---

### 6.3 模式 B: 串行协调流程

**适用场景**: 业务用户，需要引导

**流程图**:
```
TenElementModel (Phase 1.5)
         ↓
    领域专家分析
         ↓
    [用户确认领域分析结果] ← P0 级交互
         ↓
    约束专家分析 (参考领域分析)
         ↓
    [用户确认约束分析结果] ← P0 级交互
         ↓
    目标专家分析 (参考领域+约束)
         ↓
    [用户确认目标分析结果] ← P0 级交互
         ↓
    算法专家分析 (参考前三者)
         ↓
    [用户确认算法推荐] ← P0 级交互
         ↓
    跨专家一致性校验
         ↓
    💾 保存 Phase 2 状态
```

**与模式A的差异**:
1. **串行执行**: 一个专家完成后再调用下一个
2. **增量确认**: 每个专家完成后都需要用户确认
3. **上下文传递**: 后续专家可以参考前面专家的分析
4. **总时间更长**: 31-48分钟 (vs 模式A的10-15分钟)

---

### 6.4 Phase 2 交付物清单

| 交付物 | 类型 | 格式 | 持久化 | 验证层级 | 依赖者 |
|--------|------|------|--------|---------|-------|
| **domain_analysis** | 领域分析报告 | YAML Object | ✅ | L1: 字段完整性<br/>L2: 引用验证<br/>L3: 与TEM一致性 | Phase 3 |
| **constraint_analysis** | 约束分析报告 | YAML Array | ✅ | L1: 所有约束已分析<br/>L2: 代码模板生成<br/>L3: 一致性检查 | Phase 3 |
| **objective_analysis** | 目标分析报告 | YAML Object | ✅ | L1: 目标函数验证<br/>L2: 权重检查<br/>L3: 冲突分析 | Phase 3 |
| **algorithm_recommendations** | 算法推荐报告 | YAML Object | ✅ | L1: 算法配置完整<br/>L2: 引用验证<br/>L3: 性能预测 | Phase 3 |
| **consistency_report** | 一致性报告 | YAML Object | ✅ | L1: 所有检查执行<br/>L2: 冲突已解决 | Phase 3 |

---

## 7. Phase 3: 方案集成

### 7.1 流程详解

```yaml
Phase名称: Phase 3 - 方案集成
预计时间: 15-20分钟
主导智能体: Orchestrator + Algorithm Expert
协作智能体: Algorithm Expert (代码生成)
目标: 融合专家建议，生成完整YAML方案和可执行代码
关键特性: Theory-to-Code、交付物持久化、一致性验证
```

#### 步骤 3.1: 方案融合

**执行者**: Orchestrator

**输入**:
```yaml
inputs:
  - ten_element_model: object      # Phase 1.5
  - domain_analysis: object        # Phase 2.1
  - constraint_analysis: array     # Phase 2.2
  - objective_analysis: object     # Phase 2.3
  - algorithm_recommendations: object  # Phase 2.4
  - consistency_report: object     # Phase 2.5
```

**处理过程**:
```python
def integrate_solution(tem, domain, constraints, objectives, algorithm, consistency):
    """
    融合专家建议形成完整方案
    """
    # 1. 更新 TenElementModel

    # 1.1 更新算法要素（Phase 1.5时是占位）
    tem.algorithm = algorithm.primary_algorithm

    # 1.2 应用领域专家的高优先级建议
    for rec in domain.recommendations:
        if rec.priority == "high":
            apply_recommendation(tem, rec)

    # 1.3 应用约束专家的建议
    for rec in constraints.recommendations:
        if rec.priority == "high":
            apply_recommendation(tem, rec)

    # 1.4 应用目标专家的建议
    for rec in objectives.recommendations:
        if rec.priority == "high":
            apply_recommendation(tem, rec)

    # 2. 验证更新后的一致性
    updated_consistency = verify_updated_consistency(tem)

    # 3. 生成完整方案文档
    solution_document = generate_solution_document(
        tem,
        domain,
        constraints,
        objectives,
        algorithm
    )

    return {
        "updated_tem": tem,
        "solution_document": solution_document,
        "updated_consistency": updated_consistency
    }
```

**输出: solution_document.yaml**
```yaml
# solution_document.yaml - 完整调度解决方案

metadata:
  solution_name: "生鲜配送冷链调度优化方案"
  created_at: "2025-10-29T11:10:00Z"
  version: "1.0"
  based_on_tem: "phase_1_5:xyz789"

# 问题定义
problem:
  type: "车辆路径问题 (VRPTW)"
  domain: "物流配送 - 冷链配送"
  scale:
    customers: 100
    vehicles: 12
    time_horizon: "1天 (11:00-19:00)"

# 完整的 TenElementModel
ten_element_model:
  decision_variables: [...]
  parameters: {...}
  constraints: [...]
  objectives: {...}
  algorithm:  # 已由算法专家填充
    primary:
      name: "遗传算法"
      type: "meta-heuristic"
      configuration:
        population_size: 100
        crossover_rate: 0.8
        mutation_rate: 0.05
        max_generations: 500
        elite_ratio: 0.1
      initialization:
        - method: "Clarke-Wright"
          ratio: 0.5
        - method: "random"
          ratio: 0.5
      local_search:
        - operator: "2-opt"
          frequency: "every_generation"
        - operator: "Or-opt"
          frequency: "every_10_generations"
      citation: "@专家库/算法库/meta-heuristic/遗传算法.md"
  time_model: {...}
  uncertainty: [...]
  solver_config: {...}
  input_data_format: {...}
  output_format: {...}

# 专家分析摘要
expert_analyses:
  domain:
    identified_domain: "物流配送 - 冷链配送"
    key_features: ["温度敏感", "时效性高", "专用车辆"]
    citation: "@专家库/领域库/vehicle/冷链配送.md"

  constraints:
    total_count: 4
    hard_constraints: 3
    soft_constraints: 1
    citations:
      - "@专家库/约束库/capacity/车辆容量约束.md"
      - "@专家库/约束库/temporal/时间窗约束.md"

  objectives:
    primary: "成本最小化 (权重0.7)"
    secondary: "客户满意度 (权重0.3)"
    method: "加权求和"
    citations:
      - "@专家库/目标库/cost/成本最小化.md"
      - "@专家库/目标库/quality/满意度优化.md"

  algorithm:
    recommended: "遗传算法"
    confidence: 0.93
    estimated_quality: "95%最优"
    estimated_runtime: "8-10分钟"
    citation: "@专家库/算法库/meta-heuristic/遗传算法.md"

# 实施计划
implementation:
  language: "Python"
  libraries:
    - "numpy"
    - "pandas"
    - "matplotlib"
    - "deap"  # 遗传算法库
  estimated_loc: 800
  estimated_development_time: "自动生成"
```

---

#### 步骤 3.2: 一致性验证

**执行者**: Orchestrator

**验证内容**:
```python
def verify_solution_consistency(solution_document, tem, phase_2_state):
    """
    验证方案与TEM和Phase 2分析的一致性
    """
    checks = []

    # 1. 验证方案中的约束与TEM一致
    for constraint in solution_document.constraints:
        tem_constraint = find_constraint(tem, constraint.id)
        if not tem_constraint:
            checks.append((False, f"方案中的约束{constraint.id}不在TEM中"))
        elif not constraints_equal(constraint, tem_constraint):
            checks.append((False, f"约束{constraint.id}与TEM不一致"))
        else:
            checks.append((True, f"约束{constraint.id}一致"))

    # 2. 验证方案中的目标与TEM一致
    # ...

    # 3. 验证算法配置与算法专家推荐一致
    algo_recommended = phase_2_state.algorithm_recommendations.primary_algorithm
    algo_in_solution = solution_document.algorithm.primary

    if algo_recommended.name != algo_in_solution.name:
        checks.append((False, "方案算法与推荐不一致"))
    else:
        checks.append((True, "算法推荐一致"))

    # 4. 验证所有引用路径有效
    all_citations = extract_all_citations(solution_document)
    for citation in all_citations:
        if not citation_exists(citation):
            checks.append((False, f"引用路径无效: {citation}"))
        else:
            checks.append((True, f"引用有效: {citation}"))

    all_passed = all([check[0] for check in checks])
    return all_passed, checks
```

---

#### 步骤 3.3: 生成代码 (Theory-to-Code)

**执行者**: Algorithm Expert + Orchestrator

**输入**:
```yaml
inputs:
  - solution_document: object  # 完整方案
  - ten_element_model: object
  - constraint_analysis: array  # 包含代码模板
```

**代码生成流程**:
```python
def generate_code_from_solution(solution, tem, constraint_analysis):
    """
    Theory-to-Code: 从方案生成可执行代码
    """
    code_generator = CodeGenerator(language="python")

    # 1. 生成文件头和导入
    code_generator.add_imports([
        "numpy as np",
        "pandas as pd",
        "from deap import base, creator, tools, algorithms",
        "import random",
        "from typing import List, Tuple"
    ])

    # 2. 生成数据结构定义
    code_generator.generate_data_structures(tem)

    # 3. 生成约束验证函数（来自约束专家的代码模板）
    for constraint in constraint_analysis:
        code_generator.add_function(
            constraint.code_template.validation_function
        )
        if constraint.code_template.repair_function:
            code_generator.add_function(
                constraint.code_template.repair_function
            )

    # 4. 生成目标函数
    code_generator.generate_objective_function(tem.objectives)

    # 5. 生成遗传算法主体
    algorithm_template = load_algorithm_template(
        solution.algorithm.primary.citation
    )
    code_generator.generate_algorithm(
        algorithm_template,
        solution.algorithm.primary.configuration
    )

    # 6. 生成初始化函数
    for init_method in solution.algorithm.initialization:
        code_generator.generate_initialization(init_method)

    # 7. 生成局部搜索函数
    for ls_operator in solution.algorithm.local_search:
        code_generator.generate_local_search(ls_operator)

    # 8. 生成主函数和数据加载
    code_generator.generate_main_function(tem.input_data_format)

    # 9. 生成结果输出和可视化
    code_generator.generate_output(tem.output_format)

    # 10. 添加文档和注释
    code_generator.add_docstrings()
    code_generator.add_inline_comments()

    # 11. 代码格式化
    formatted_code = code_generator.format_code()

    # 12. 生成测试用例
    test_code = generate_test_cases(tem)

    # 13. 生成README和运行说明
    readme = generate_readme(solution, tem)

    return {
        "main_code": formatted_code,
        "test_code": test_code,
        "readme": readme,
        "total_lines": code_generator.count_lines()
    }
```

**生成的代码结构**:
```
生成的代码/
├── vrp_solver.py          # 主求解器（800行）
│   ├── 数据结构定义
│   ├── 约束验证函数 (C1-C4)
│   ├── 约束修复函数
│   ├── 目标函数
│   ├── 遗传算法主体
│   │   ├── 初始化
│   │   ├── 交叉算子
│   │   ├── 变异算子
│   │   ├── 选择算子
│   │   └── 主循环
│   ├── 局部搜索 (2-opt, Or-opt)
│   ├── 数据加载
│   ├── 结果输出
│   └── main()函数
│
├── test_vrp_solver.py     # 测试用例（200行）
│   ├── test_constraint_validation()
│   ├── test_objective_function()
│   ├── test_initialization()
│   ├── test_genetic_operators()
│   └── test_full_solve()
│
├── requirements.txt       # 依赖配置
├── README.md             # 运行说明
└── data/                 # 示例数据
    ├── customers.csv
    ├── vehicles.json
    └── distances.npy
```

**代码示例片段** (生成的代码):
```python
# vrp_solver.py (部分)

"""
生鲜配送冷链调度优化求解器

自动生成于: 2025-10-29 11:15:00
基于方案: solution_document.yaml
TenElementModel Hash: xyz789

🤖 Generated with APS (Advanced Planning & Scheduling)
Theory-to-Code Engine v1.0
"""

import numpy as np
import pandas as pd
from deap import base, creator, tools, algorithms
import random
from typing import List, Tuple

# ============================================================================
# 数据结构定义
# ============================================================================

class Customer:
    """客户数据结构"""
    def __init__(self, id, lat, lng, demand, tw_start, tw_end, order_time):
        self.id = id
        self.latitude = lat
        self.longitude = lng
        self.demand = demand
        self.time_window_start = tw_start
        self.time_window_end = tw_end
        self.order_time = order_time

class Vehicle:
    """车辆数据结构"""
    def __init__(self, id, capacity, start_location):
        self.id = id
        self.capacity = capacity  # 150件
        self.start_location = start_location

# ============================================================================
# 约束验证函数
# 来源: @专家库/约束库/capacity/车辆容量约束.md
# ============================================================================

def validate_vehicle_capacity(route: List[int],
                               customers: List[Customer],
                               capacity: int) -> bool:
    """
    验证车辆容量约束 (C1)

    Args:
        route: 车辆路径（客户ID列表）
        customers: 客户列表
        capacity: 车辆容量

    Returns:
        bool: True if 满足约束, False otherwise
    """
    total_demand = sum(customers[i].demand for i in route)
    return total_demand <= capacity

def repair_capacity_violation(route: List[int],
                               customers: List[Customer],
                               capacity: int) -> List[int]:
    """
    修复容量约束违反

    策略: 移除路径末尾的客户直到满足容量
    """
    while sum(customers[i].demand for i in route) > capacity and len(route) > 0:
        route.pop()
    return route

# ============================================================================
# 约束验证函数
# 来源: @专家库/约束库/temporal/时间窗约束.md
# ============================================================================

def validate_time_window(arrival_time: float,
                          customer: Customer) -> bool:
    """验证时间窗约束 (C2 - 软约束)"""
    return customer.time_window_start <= arrival_time <= customer.time_window_end

def calculate_time_window_penalty(arrival_time: float,
                                   customer: Customer,
                                   penalty_rate: float = 10000) -> float:
    """
    计算时间窗违反惩罚

    惩罚率: 10000元/分钟
    """
    if arrival_time < customer.time_window_start:
        early_penalty = (customer.time_window_start - arrival_time) * penalty_rate
        return early_penalty
    elif arrival_time > customer.time_window_end:
        late_penalty = (arrival_time - customer.time_window_end) * penalty_rate
        return late_penalty
    return 0.0

# ============================================================================
# 目标函数
# 来源: @专家库/目标库/cost/成本最小化.md
#       @专家库/目标库/quality/满意度优化.md
# ============================================================================

def calculate_total_cost(solution: List[List[int]],
                         customers: List[Customer],
                         vehicles: List[Vehicle],
                         distance_matrix: np.ndarray) -> float:
    """
    计算总成本 (主目标，权重0.7)

    成本组成:
    1. 固定成本: 200元/车
    2. 距离成本: 0.8元/km × 1.3 (冷链加成)
    3. 时间成本: 50元/小时
    4. 惩罚成本: 时间窗违反
    """
    # 固定成本
    vehicles_used = len([route for route in solution if len(route) > 0])
    fixed_cost = 200 * vehicles_used

    # 距离成本
    total_distance = 0
    for route in solution:
        if len(route) == 0:
            continue
        # 计算路径总距离
        distance = 0
        prev = 0  # 起点（配送中心）
        for customer_id in route:
            distance += distance_matrix[prev][customer_id]
            prev = customer_id
        distance += distance_matrix[prev][0]  # 返回起点
        total_distance += distance

    distance_rate = 0.8 * 1.3  # 冷链加成30%
    distance_cost = total_distance * distance_rate

    # 时间成本
    total_time = calculate_total_time(solution, customers, distance_matrix)
    time_cost = (total_time / 60) * 50  # 50元/小时

    # 惩罚成本
    penalty_cost = 0
    for route in solution:
        arrival_times = calculate_arrival_times(route, customers, distance_matrix)
        for i, customer_id in enumerate(route):
            penalty_cost += calculate_time_window_penalty(
                arrival_times[i],
                customers[customer_id]
            )

    total_cost = fixed_cost + distance_cost + time_cost + penalty_cost
    return total_cost

def calculate_customer_satisfaction(solution: List[List[int]],
                                    customers: List[Customer],
                                    distance_matrix: np.ndarray) -> float:
    """
    计算客户满意度 (次要目标，权重0.3)

    满意度 = α×准时率 + β×新鲜度 + γ×服务质量
    """
    # 准时率
    on_time_count = 0
    total_customers = sum(len(route) for route in solution)

    for route in solution:
        arrival_times = calculate_arrival_times(route, customers, distance_matrix)
        for i, customer_id in enumerate(route):
            if validate_time_window(arrival_times[i], customers[customer_id]):
                on_time_count += 1

    on_time_rate = on_time_count / total_customers if total_customers > 0 else 0

    # 新鲜度 (配送时间越短越好)
    avg_delivery_time = calculate_average_delivery_time(solution, customers, distance_matrix)
    freshness_score = 1.0 - (avg_delivery_time / 480)  # 480分钟为最大时长

    # 服务质量 (假设基础服务质量为0.9)
    service_quality = 0.9

    # 加权平均
    satisfaction = 0.4 * on_time_rate + 0.4 * freshness_score + 0.2 * service_quality
    return satisfaction

def evaluate_solution(solution: List[List[int]],
                      customers: List[Customer],
                      vehicles: List[Vehicle],
                      distance_matrix: np.ndarray) -> float:
    """
    综合目标函数 (加权求和)

    目标 = 0.7 × 成本得分 + 0.3 × 满意度得分
    """
    # 成本归一化 (越低越好，转换为得分)
    total_cost = calculate_total_cost(solution, customers, vehicles, distance_matrix)
    cost_score = 1.0 / (1.0 + total_cost / 10000)  # 归一化

    # 满意度 (越高越好)
    satisfaction_score = calculate_customer_satisfaction(solution, customers, distance_matrix)

    # 加权求和 (转换为最小化问题)
    fitness = -(0.7 * cost_score + 0.3 * satisfaction_score)
    return fitness

# ============================================================================
# 遗传算法主体
# 来源: @专家库/算法库/meta-heuristic/遗传算法.md
# 配置: population_size=100, crossover_rate=0.8, mutation_rate=0.05
# ============================================================================

# ... (后续代码)

if __name__ == "__main__":
    # 加载数据
    customers = load_customers("data/customers.csv")
    vehicles = load_vehicles("data/vehicles.json")
    distance_matrix = np.load("data/distances.npy")

    # 运行求解器
    best_solution, best_fitness = genetic_algorithm_vrp(
        customers,
        vehicles,
        distance_matrix,
        population_size=100,
        max_generations=500
    )

    # 输出结果
    save_solution("solution.json", best_solution)
    visualize_routes("routes_map.html", best_solution, customers)

    print(f"✅ 求解完成！最优成本: {-best_fitness:.2f}元")
```

---

#### 步骤 3.4: 保存所有交付物

**执行者**: Orchestrator

**保存的交付物**:

| 文件 | 类型 | 格式 | 大小 | 描述 |
|------|------|------|------|------|
| **solution_document.yaml** | 方案文档 | YAML | ~15KB | 完整调度解决方案 |
| **vrp_solver.py** | 主代码 | Python | ~800行 | 求解器实现 |
| **test_vrp_solver.py** | 测试代码 | Python | ~200行 | 单元测试 |
| **requirements.txt** | 依赖 | Text | ~10行 | Python依赖 |
| **README.md** | 说明文档 | Markdown | ~2KB | 运行说明 |
| **data/customers.csv** | 示例数据 | CSV | ~5KB | 客户数据模板 |
| **data/vehicles.json** | 示例数据 | JSON | ~1KB | 车辆数据模板 |
| **data/distances.npy** | 示例数据 | NumPy | ~40KB | 距离矩阵模板 |

**保存过程**:
```python
def save_all_deliverables(solution_doc, generated_code, test_code,
                           requirements, readme, data_templates):
    """
    保存所有交付物到文件系统
    """
    output_folder = config.output_folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_folder = f"{output_folder}/project_{timestamp}"

    # 创建目录结构
    os.makedirs(f"{project_folder}/data", exist_ok=True)

    saved_files = []

    # 1. 保存方案文档
    solution_file = f"{project_folder}/solution_document.yaml"
    with open(solution_file, 'w', encoding='utf-8') as f:
        yaml.dump(solution_doc, f, allow_unicode=True)
    saved_files.append({
        "file": solution_file,
        "type": "solution_document",
        "size": os.path.getsize(solution_file)
    })

    # 2. 保存主代码
    code_file = f"{project_folder}/vrp_solver.py"
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(generated_code)
    saved_files.append({
        "file": code_file,
        "type": "main_code",
        "size": os.path.getsize(code_file),
        "lines": generated_code.count('\n')
    })

    # 3. 保存测试代码
    test_file = f"{project_folder}/test_vrp_solver.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    saved_files.append({
        "file": test_file,
        "type": "test_code",
        "size": os.path.getsize(test_file)
    })

    # 4. 保存其他文件 (requirements, README, data)
    # ...

    # 5. 创建交付物清单
    manifest = {
        "created_at": datetime.now().isoformat(),
        "project_folder": project_folder,
        "total_files": len(saved_files),
        "files": saved_files
    }

    manifest_file = f"{project_folder}/MANIFEST.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    # 6. 验证所有文件已保存
    verification = verify_files_saved(saved_files)

    return {
        "saved_files": saved_files,
        "manifest": manifest,
        "verification": verification,
        "project_folder": project_folder
    }
```

**交付物验证**:
```python
def verify_deliverables_saved(saved_files):
    """
    验证所有交付物已成功保存
    """
    checks = []

    for file_info in saved_files:
        file_path = file_info["file"]

        # 检查1: 文件存在
        exists = os.path.exists(file_path)
        checks.append(("file_exists", file_path, exists))

        # 检查2: 文件可读
        if exists:
            readable = os.access(file_path, os.R_OK)
            checks.append(("file_readable", file_path, readable))

        # 检查3: 文件大小 > 0
        if exists:
            size = os.path.getsize(file_path)
            checks.append(("file_not_empty", file_path, size > 0))

        # 检查4: 文件内容完整性
        if exists and file_info["type"] == "main_code":
            # 检查代码文件包含必要的函数
            with open(file_path, 'r') as f:
                content = f.read()
            has_main = "if __name__ == '__main__':" in content
            has_algorithm = "genetic_algorithm" in content
            checks.append(("code_complete", file_path, has_main and has_algorithm))

    all_passed = all([check[2] for check in checks])

    return {
        "all_files_saved": all_passed,
        "checks": checks,
        "failed_checks": [c for c in checks if not c[2]]
    }
```

---

#### 步骤 3.5: 💾 保存 Phase 3 状态

**保存内容**:
```yaml
# phase_3_state.yaml

metadata:
  phase_id: "phase_3"
  phase_name: "方案集成"
  created_at: "2025-10-29T11:20:00Z"
  completed_at: "2025-10-29T11:35:00Z"
  duration: "15分钟"
  depends_on: ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2"]

# 核心交付物 1: 集成的解决方案
integrated_solution:
  solution_document_path: "{output_folder}/project_20251029_1120/solution_document.yaml"
  solution_hash: "sha256:solution123..."

# 核心交付物 2: 用户确认的方案
user_approved_solution:
  approved_at: "2025-10-29T11:30:00Z"
  user_comments: "方案合理，请继续生成代码"

# 核心交付物 3: 生成的代码
implementation_code:
  main_code_path: "{output_folder}/project_20251029_1120/vrp_solver.py"
  total_lines: 856
  language: "Python"
  libraries: ["numpy", "pandas", "deap"]

# 核心交付物 4: 代码可追溯性映射
code_traceability:
  constraints:
    - constraint_id: "C1"
      code_location: "vrp_solver.py:145-160"
      function: "validate_vehicle_capacity()"
    - constraint_id: "C2"
      code_location: "vrp_solver.py:162-175"
      function: "validate_time_window()"

  objectives:
    - objective_id: "O1"
      code_location: "vrp_solver.py:245-290"
      function: "calculate_total_cost()"
    - objective_id: "O2"
      code_location: "vrp_solver.py:292-320"
      function: "calculate_customer_satisfaction()"

  algorithm:
    algorithm_name: "遗传算法"
    code_location: "vrp_solver.py:450-650"
    functions:
      - "genetic_algorithm_vrp()"
      - "cx_order_crossover()"
      - "mut_swap_inversion()"
      - "local_search_2opt()"

# 核心交付物 5: 一致性验证结果
consistency_validation:
  tem_solution_consistent: true
  phase_2_solution_consistent: true
  all_constraints_implemented: true
  all_citations_valid: true

# 核心交付物 6: 所有保存的文件清单
saved_files:
  - file: "{output_folder}/project_20251029_1120/solution_document.yaml"
    type: "solution_document"
    size: 15360
  - file: "{output_folder}/project_20251029_1120/vrp_solver.py"
    type: "main_code"
    size: 34560
    lines: 856
  - file: "{output_folder}/project_20251029_1120/test_vrp_solver.py"
    type: "test_code"
    size: 8192
    lines: 203
  # ... 其他文件

# 核心交付物 7: 交付物清单
deliverable_manifest:
  manifest_file: "{output_folder}/project_20251029_1120/MANIFEST.json"
  total_files: 8
  total_size: 108032  # bytes
  project_folder: "{output_folder}/project_20251029_1120"

# 验证信息
verification:
  solution_integrated: true
  code_generated: true
  all_files_saved: true
  code_traceable: true
  consistency_validated: true
  validation_passed: true

# 依赖信息
required_by: ["phase_4"]
```

---

### 7.2 Phase 3 交付物清单

| 交付物 | 类型 | 格式 | 持久化 | 验证层级 | 依赖者 |
|--------|------|------|--------|---------|-------|
| **integrated_solution** | 完整方案 | YAML | ✅ | L1: 结构完整<br/>L2: 与TEM一致<br/>L3: 与Phase2一致 | Phase 4 |
| **user_approved_solution** | 确认记录 | YAML | ✅ | L1: 用户已确认 | Phase 4 |
| **implementation_code** | 可执行代码 | Python | ✅ | L1: 语法正确<br/>L2: 可执行<br/>L3: 逻辑完整<br/>L4: 可追溯 | Phase 4 |
| **code_traceability** | 可追溯性映射 | YAML | ✅ | L1: 所有要素可追溯 | Phase 4 |
| **consistency_validation** | 一致性验证 | YAML | ✅ | L1: 所有检查通过 | Phase 4 |
| **saved_files** | 文件清单 | Array | ✅ | L1: 所有文件已保存<br/>L2: 文件完整性 | Phase 4 |
| **deliverable_manifest** | 交付物清单 | JSON | ✅ | L1: 清单完整 | Phase 4 |

---

## 8. Phase 4: 质量保证

### 8.1 流程概述

```yaml
Phase名称: Phase 4 - 质量保证
预计时间: 9-12分钟
主导智能体: Quality Evaluator
协作智能体: Orchestrator
目标: 6层质量门禁验证，确保交付物质量
关键特性: 质量分数量化、智能检测、自动阻断
```

#### 步骤 4.1: 6层质量门禁验证

**执行者**: Quality Evaluator

**输入**:
```yaml
inputs:
  - phase_0_state: object
  - phase_0_5_state: object
  - phase_1_state: object
  - phase_1_5_state: object
  - phase_2_state: object
  - phase_3_state: object
```

**处理过程**:
```python
def execute_quality_gates(all_phase_states):
    """
    执行6层质量门禁
    """
    quality_report = {
        "gate_results": [],
        "overall_score": 0.0,
        "pass": True,
        "issues": []
    }

    # 门禁 1: 代码语法检查
    gate_1 = check_code_syntax(all_phase_states.phase_3)
    quality_report["gate_results"].append(gate_1)

    # 门禁 2: 逻辑完整性检查
    gate_2 = check_logic_completeness(all_phase_states.phase_3)
    quality_report["gate_results"].append(gate_2)

    # 门禁 3: TEM一致性检查
    gate_3 = check_tem_consistency(
        all_phase_states.phase_1_5,
        all_phase_states.phase_2,
        all_phase_states.phase_3
    )
    quality_report["gate_results"].append(gate_3)

    # 门禁 4: 引用完整性检查 (Guardrails)
    gate_4 = check_citation_integrity(all_phase_states)
    quality_report["gate_results"].append(gate_4)

    # 门禁 5: 性能基准检查
    gate_5 = check_performance_baseline(all_phase_states.phase_3)
    quality_report["gate_results"].append(gate_5)

    # 门禁 6: 交付物完整性检查
    gate_6 = check_deliverables_completeness(all_phase_states.phase_3)
    quality_report["gate_results"].append(gate_6)

    # 计算总分
    quality_report["overall_score"] = calculate_overall_score(
        quality_report["gate_results"]
    )

    # 判断是否通过
    quality_report["pass"] = quality_report["overall_score"] >= 0.80

    return quality_report
```

---

#### 门禁 1: 代码语法检查

**检查内容**:
```python
def check_code_syntax(phase_3_state):
    """
    门禁 1: 代码语法检查
    """
    code_file = phase_3_state.implementation_code.main_code_path

    checks = []

    # 1. Python语法检查
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            code_content = f.read()

        compile(code_content, code_file, 'exec')
        checks.append(("syntax_valid", True, "Python语法正确"))
    except SyntaxError as e:
        checks.append(("syntax_valid", False, f"语法错误: {e}"))

    # 2. 导入检查
    import_errors = check_imports(code_content)
    if not import_errors:
        checks.append(("imports_valid", True, "所有导入有效"))
    else:
        checks.append(("imports_valid", False, f"导入错误: {import_errors}"))

    # 3. 函数定义检查
    required_functions = [
        "validate_vehicle_capacity",
        "validate_time_window",
        "calculate_total_cost",
        "calculate_customer_satisfaction",
        "evaluate_solution"
    ]

    for func_name in required_functions:
        if func_name in code_content:
            checks.append((f"function_{func_name}", True, f"函数{func_name}已定义"))
        else:
            checks.append((f"function_{func_name}", False, f"缺少函数{func_name}"))

    # 4. main函数检查
    if "if __name__ == '__main__':" in code_content:
        checks.append(("main_function", True, "main函数存在"))
    else:
        checks.append(("main_function", False, "缺少main函数"))

    all_passed = all([check[1] for check in checks])
    score = sum([1 for check in checks if check[1]]) / len(checks)

    return {
        "gate_id": "G1",
        "gate_name": "代码语法检查",
        "passed": all_passed,
        "score": score,
        "checks": checks,
        "weight": 0.15
    }
```

**输出示例**:
```yaml
gate_1:
  gate_id: "G1"
  gate_name: "代码语法检查"
  passed: true
  score: 1.0
  checks:
    - check: "syntax_valid"
      passed: true
      message: "Python语法正确"
    - check: "imports_valid"
      passed: true
      message: "所有导入有效"
    - check: "function_validate_vehicle_capacity"
      passed: true
      message: "函数validate_vehicle_capacity已定义"
    # ... 其他检查
  weight: 0.15
```

---

#### 门禁 2: 逻辑完整性检查

**检查内容**:
```python
def check_logic_completeness(phase_3_state):
    """
    门禁 2: 逻辑完整性检查
    """
    tem = load_state("phase_1_5").ten_element_model
    code_traceability = phase_3_state.code_traceability

    checks = []

    # 1. 所有约束都已实现
    for constraint in tem.constraints:
        constraint_id = constraint.id

        # 查找代码映射
        code_mapping = find_constraint_in_traceability(
            code_traceability.constraints,
            constraint_id
        )

        if code_mapping:
            checks.append((
                f"constraint_{constraint_id}_implemented",
                True,
                f"约束{constraint_id}已实现: {code_mapping.function}"
            ))
        else:
            checks.append((
                f"constraint_{constraint_id}_implemented",
                False,
                f"约束{constraint_id}未实现"
            ))

    # 2. 所有目标都已实现
    for obj_type in ["primary", "secondary"]:
        obj = getattr(tem.objectives, obj_type, None)
        if obj:
            code_mapping = find_objective_in_traceability(
                code_traceability.objectives,
                obj.id
            )

            if code_mapping:
                checks.append((
                    f"objective_{obj.id}_implemented",
                    True,
                    f"目标{obj.id}已实现: {code_mapping.function}"
                ))
            else:
                checks.append((
                    f"objective_{obj.id}_implemented",
                    False,
                    f"目标{obj.id}未实现"
                ))

    # 3. 算法已实现
    algorithm = tem.algorithm.primary
    if code_traceability.algorithm.algorithm_name == algorithm.name:
        checks.append((
            "algorithm_implemented",
            True,
            f"算法{algorithm.name}已实现"
        ))
    else:
        checks.append((
            "algorithm_implemented",
            False,
            f"算法实现不匹配: 期望{algorithm.name}, 实际{code_traceability.algorithm.algorithm_name}"
        ))

    # 4. 数据加载和输出逻辑
    code_file = phase_3_state.implementation_code.main_code_path
    with open(code_file, 'r') as f:
        code_content = f.read()

    if "load_customers" in code_content or "pd.read_csv" in code_content:
        checks.append(("data_loading", True, "数据加载逻辑存在"))
    else:
        checks.append(("data_loading", False, "缺少数据加载逻辑"))

    if "save_solution" in code_content or "json.dump" in code_content:
        checks.append(("output_logic", True, "结果输出逻辑存在"))
    else:
        checks.append(("output_logic", False, "缺少结果输出逻辑"))

    all_passed = all([check[1] for check in checks])
    score = sum([1 for check in checks if check[1]]) / len(checks)

    return {
        "gate_id": "G2",
        "gate_name": "逻辑完整性检查",
        "passed": all_passed,
        "score": score,
        "checks": checks,
        "weight": 0.20
    }
```

---

#### 门禁 3: TEM一致性检查

**检查内容**:
```python
def check_tem_consistency(phase_1_5_state, phase_2_state, phase_3_state):
    """
    门禁 3: TEM一致性检查
    """
    tem_baseline = phase_1_5_state.ten_element_model
    tem_in_solution = phase_3_state.integrated_solution.ten_element_model

    checks = []

    # 1. 决策变量一致性
    dv_baseline = tem_baseline.decision_variables
    dv_solution = tem_in_solution.decision_variables

    if len(dv_baseline) == len(dv_solution):
        dv_match = all([
            dv_b.id == dv_s.id
            for dv_b, dv_s in zip(dv_baseline, dv_solution)
        ])
        if dv_match:
            checks.append(("decision_variables_consistent", True, "决策变量一致"))
        else:
            checks.append(("decision_variables_consistent", False, "决策变量ID不一致"))
    else:
        checks.append((
            "decision_variables_consistent",
            False,
            f"决策变量数量不一致: {len(dv_baseline)} vs {len(dv_solution)}"
        ))

    # 2. 约束一致性
    constraints_baseline = tem_baseline.constraints
    constraints_solution = tem_in_solution.constraints

    if len(constraints_baseline) == len(constraints_solution):
        constraints_match = all([
            c_b.id == c_s.id
            for c_b, c_s in zip(constraints_baseline, constraints_solution)
        ])
        if constraints_match:
            checks.append(("constraints_consistent", True, "约束一致"))
        else:
            checks.append(("constraints_consistent", False, "约束ID不一致"))
    else:
        checks.append((
            "constraints_consistent",
            False,
            f"约束数量不一致: {len(constraints_baseline)} vs {len(constraints_solution)}"
        ))

    # 3. 目标一致性
    obj_baseline = tem_baseline.objectives
    obj_solution = tem_in_solution.objectives

    if obj_baseline.primary.id == obj_solution.primary.id:
        checks.append(("primary_objective_consistent", True, "主目标一致"))
    else:
        checks.append(("primary_objective_consistent", False, "主目标不一致"))

    if hasattr(obj_baseline, 'secondary') and hasattr(obj_solution, 'secondary'):
        if obj_baseline.secondary.id == obj_solution.secondary.id:
            checks.append(("secondary_objective_consistent", True, "次要目标一致"))
        else:
            checks.append(("secondary_objective_consistent", False, "次要目标不一致"))

    # 4. 算法一致性
    algo_baseline = phase_2_state.algorithm_recommendations.primary_algorithm
    algo_solution = tem_in_solution.algorithm.primary

    if algo_baseline.name == algo_solution.name:
        checks.append(("algorithm_consistent", True, "算法一致"))
    else:
        checks.append((
            "algorithm_consistent",
            False,
            f"算法不一致: {algo_baseline.name} vs {algo_solution.name}"
        ))

    # 5. Hash验证
    baseline_hash = phase_1_5_state.model_baseline.model_hash
    # 重新计算solution的hash
    solution_hash = calculate_hash(tem_in_solution)

    # Hash可能不同（因为Phase2的修改），但核心要素应一致
    # 这里主要检查核心要素而非hash

    all_passed = all([check[1] for check in checks])
    score = sum([1 for check in checks if check[1]]) / len(checks)

    return {
        "gate_id": "G3",
        "gate_name": "TEM一致性检查",
        "passed": all_passed,
        "score": score,
        "checks": checks,
        "weight": 0.25
    }
```

---

#### 门禁 4: 引用完整性检查 (Guardrails)

**检查内容**:
```python
def check_citation_integrity(all_phase_states):
    """
    门禁 4: 引用完整性检查 (Guardrails)

    这是核心的Guardrails机制，确保所有知识都有明确引用
    """
    checks = []

    # 1. Phase 1.5 TEM中的引用
    tem = all_phase_states.phase_1_5.ten_element_model

    # 1.1 约束引用
    for constraint in tem.constraints:
        if constraint.citation and constraint.citation.startswith("@专家库"):
            # 验证引用路径存在
            citation_path = resolve_citation_path(constraint.citation)
            if os.path.exists(citation_path):
                checks.append((
                    f"constraint_{constraint.id}_citation_valid",
                    True,
                    f"约束{constraint.id}引用有效: {constraint.citation}"
                ))
            else:
                checks.append((
                    f"constraint_{constraint.id}_citation_missing",
                    False,
                    f"约束{constraint.id}引用路径不存在: {citation_path}"
                ))
        else:
            checks.append((
                f"constraint_{constraint.id}_no_citation",
                False,
                f"约束{constraint.id}缺少@专家库引用"
            ))

    # 1.2 目标引用
    for obj_type in ["primary", "secondary"]:
        obj = getattr(tem.objectives, obj_type, None)
        if obj:
            if obj.citation and obj.citation.startswith("@专家库"):
                citation_path = resolve_citation_path(obj.citation)
                if os.path.exists(citation_path):
                    checks.append((
                        f"objective_{obj.id}_citation_valid",
                        True,
                        f"目标{obj.id}引用有效"
                    ))
                else:
                    checks.append((
                        f"objective_{obj.id}_citation_missing",
                        False,
                        f"目标{obj.id}引用路径不存在"
                    ))
            else:
                checks.append((
                    f"objective_{obj.id}_no_citation",
                    False,
                    f"目标{obj.id}缺少@专家库引用"
                ))

    # 2. Phase 2 专家分析中的引用
    phase_2 = all_phase_states.phase_2

    # 2.1 领域分析引用
    domain_template = phase_2.domain_analysis.domain_template
    if domain_template.startswith("@专家库"):
        citation_path = resolve_citation_path(domain_template)
        if os.path.exists(citation_path):
            checks.append(("domain_citation_valid", True, "领域分析引用有效"))
        else:
            checks.append(("domain_citation_missing", False, "领域分析引用路径不存在"))
    else:
        checks.append(("domain_no_citation", False, "领域分析缺少引用"))

    # 2.2 算法推荐引用
    algorithm_citation = phase_2.algorithm_recommendations.primary_algorithm.citation
    if algorithm_citation and algorithm_citation.startswith("@专家库"):
        citation_path = resolve_citation_path(algorithm_citation)
        if os.path.exists(citation_path):
            checks.append(("algorithm_citation_valid", True, "算法推荐引用有效"))
        else:
            checks.append(("algorithm_citation_missing", False, "算法推荐引用路径不存在"))
    else:
        checks.append(("algorithm_no_citation", False, "算法推荐缺少引用"))

    # 3. Phase 3 solution_document中的引用
    solution_doc = all_phase_states.phase_3.integrated_solution

    # 检查solution中是否保留了所有引用
    all_citations = extract_all_citations(solution_doc)
    for citation in all_citations:
        citation_path = resolve_citation_path(citation)
        if os.path.exists(citation_path):
            checks.append((
                f"solution_citation_{hash(citation)}",
                True,
                f"方案引用有效: {citation}"
            ))
        else:
            checks.append((
                f"solution_citation_{hash(citation)}_missing",
                False,
                f"方案引用路径不存在: {citation}"
            ))

    all_passed = all([check[1] for check in checks])
    score = sum([1 for check in checks if check[1]]) / len(checks) if checks else 0

    return {
        "gate_id": "G4",
        "gate_name": "引用完整性检查 (Guardrails)",
        "passed": all_passed,
        "score": score,
        "checks": checks,
        "weight": 0.20,
        "critical": True  # 这是关键门禁
    }
```

**Guardrails 失败处理**:
```python
def handle_guardrails_failure(gate_4_result):
    """
    Guardrails失败时的处理
    """
    if not gate_4_result["passed"]:
        error_message = f"""
        🚨 Guardrails验证失败 - 引用完整性不足

        质量门禁4未通过，检测到以下问题：

        """

        failed_checks = [
            check for check in gate_4_result["checks"] if not check[1]
        ]

        for i, (check_id, passed, message) in enumerate(failed_checks, 1):
            error_message += f"{i}. {message}\n"

        error_message += """

        📌 Guardrails要求：
        - 所有约束必须引用@专家库/约束库中的模板
        - 所有目标必须引用@专家库/目标库中的模板
        - 所有算法必须引用@专家库/算法库中的模板
        - 所有领域特性必须引用@专家库/领域库中的模板

        ❌ 此问题会阻断交付流程，请修复后重试。
        """

        raise GuardrailsViolationError(error_message)
```

---

#### 门禁 5: 性能基准检查

**检查内容**:
```python
def check_performance_baseline(phase_3_state):
    """
    门禁 5: 性能基准检查
    """
    checks = []

    algorithm_analysis = load_state("phase_2").algorithm_recommendations
    performance_prediction = algorithm_analysis.performance_prediction

    # 1. 预计运行时间检查
    estimated_runtime = performance_prediction.estimated_runtime
    time_limit = load_state("phase_1_5").ten_element_model.solver_config.time_limit

    # 解析时间（如 "8-10分钟" -> 10）
    max_runtime = parse_max_runtime(estimated_runtime)

    if max_runtime <= time_limit / 60:  # 转换为分钟
        checks.append((
            "runtime_acceptable",
            True,
            f"预计运行时间{estimated_runtime}在限制{time_limit/60}分钟内"
        ))
    else:
        checks.append((
            "runtime_excessive",
            False,
            f"预计运行时间{estimated_runtime}超过限制{time_limit/60}分钟"
        ))

    # 2. 解质量预测
    solution_quality = performance_prediction.solution_quality
    min_quality_threshold = 0.90  # 至少达到90%最优

    quality_percentage = parse_quality_percentage(solution_quality)
    if quality_percentage >= min_quality_threshold:
        checks.append((
            "quality_acceptable",
            True,
            f"解质量{solution_quality}满足要求"
        ))
    else:
        checks.append((
            "quality_insufficient",
            False,
            f"解质量{solution_quality}低于90%阈值"
        ))

    # 3. 代码复杂度检查
    code_file = phase_3_state.implementation_code.main_code_path
    with open(code_file, 'r') as f:
        code_lines = len(f.readlines())

    expected_loc = load_state("phase_3").integrated_solution.implementation.estimated_loc

    # 允许±30%的偏差
    if 0.7 * expected_loc <= code_lines <= 1.3 * expected_loc:
        checks.append((
            "code_size_reasonable",
            True,
            f"代码行数{code_lines}符合预期{expected_loc}"
        ))
    else:
        checks.append((
            "code_size_deviation",
            False,
            f"代码行数{code_lines}偏离预期{expected_loc}过多"
        ))

    # 4. 算法配置合理性
    algorithm_config = phase_3_state.integrated_solution.ten_element_model.algorithm.primary.configuration

    # 检查关键参数
    if "population_size" in algorithm_config:
        pop_size = algorithm_config["population_size"]
        if 50 <= pop_size <= 200:
            checks.append(("population_size_reasonable", True, f"种群大小{pop_size}合理"))
        else:
            checks.append(("population_size_unreasonable", False, f"种群大小{pop_size}不合理"))

    if "max_generations" in algorithm_config:
        max_gen = algorithm_config["max_generations"]
        if 100 <= max_gen <= 1000:
            checks.append(("max_generations_reasonable", True, f"最大代数{max_gen}合理"))
        else:
            checks.append(("max_generations_unreasonable", False, f"最大代数{max_gen}不合理"))

    all_passed = all([check[1] for check in checks])
    score = sum([1 for check in checks if check[1]]) / len(checks)

    return {
        "gate_id": "G5",
        "gate_name": "性能基准检查",
        "passed": all_passed,
        "score": score,
        "checks": checks,
        "weight": 0.10
    }
```

---

#### 门禁 6: 交付物完整性检查

**检查内容**:
```python
def check_deliverables_completeness(phase_3_state):
    """
    门禁 6: 交付物完整性检查
    """
    checks = []

    # 1. 必需文件存在性检查
    required_files = [
        "solution_document.yaml",
        "vrp_solver.py",  # 主代码
        "test_vrp_solver.py",  # 测试代码
        "requirements.txt",
        "README.md",
        "MANIFEST.json"
    ]

    saved_files = phase_3_state.saved_files
    saved_file_names = [os.path.basename(f["file"]) for f in saved_files]

    for required_file in required_files:
        if required_file in saved_file_names:
            checks.append((
                f"file_{required_file}_exists",
                True,
                f"文件{required_file}已保存"
            ))
        else:
            checks.append((
                f"file_{required_file}_missing",
                False,
                f"缺少文件{required_file}"
            ))

    # 2. 文件大小合理性
    for file_info in saved_files:
        file_size = file_info.get("size", 0)
        file_type = file_info.get("type", "")

        # 主代码应该至少10KB
        if file_type == "main_code":
            if file_size >= 10000:  # 10KB
                checks.append(("main_code_size_ok", True, f"主代码大小{file_size}字节正常"))
            else:
                checks.append(("main_code_too_small", False, f"主代码大小{file_size}字节过小"))

        # 方案文档应该至少5KB
        if file_type == "solution_document":
            if file_size >= 5000:  # 5KB
                checks.append(("solution_doc_size_ok", True, "方案文档大小正常"))
            else:
                checks.append(("solution_doc_too_small", False, "方案文档过小"))

    # 3. 文件内容完整性
    main_code_file = next(
        (f["file"] for f in saved_files if f["type"] == "main_code"),
        None
    )

    if main_code_file and os.path.exists(main_code_file):
        with open(main_code_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键内容
        critical_content = [
            "def validate_vehicle_capacity",
            "def calculate_total_cost",
            "if __name__ == '__main__':",
            "import numpy",
            "import pandas"
        ]

        for critical in critical_content:
            if critical in content:
                checks.append((
                    f"content_{critical.replace(' ', '_')}",
                    True,
                    f"包含关键内容: {critical}"
                ))
            else:
                checks.append((
                    f"missing_{critical.replace(' ', '_')}",
                    False,
                    f"缺少关键内容: {critical}"
                ))

    # 4. MANIFEST.json完整性
    manifest_file = phase_3_state.deliverable_manifest.manifest_file
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        if "created_at" in manifest and "files" in manifest:
            checks.append(("manifest_complete", True, "MANIFEST.json完整"))
        else:
            checks.append(("manifest_incomplete", False, "MANIFEST.json缺少必要字段"))
    else:
        checks.append(("manifest_missing", False, "MANIFEST.json文件不存在"))

    # 5. 代码可追溯性
    traceability = phase_3_state.code_traceability
    tem = load_state("phase_1_5").ten_element_model

    # 所有约束都有代码位置
    for constraint in tem.constraints:
        constraint_trace = find_constraint_in_traceability(
            traceability.constraints,
            constraint.id
        )
        if constraint_trace:
            checks.append((
                f"trace_constraint_{constraint.id}",
                True,
                f"约束{constraint.id}可追溯"
            ))
        else:
            checks.append((
                f"trace_constraint_{constraint.id}_missing",
                False,
                f"约束{constraint.id}无追溯信息"
            ))

    all_passed = all([check[1] for check in checks])
    score = sum([1 for check in checks if check[1]]) / len(checks)

    return {
        "gate_id": "G6",
        "gate_name": "交付物完整性检查",
        "passed": all_passed,
        "score": score,
        "checks": checks,
        "weight": 0.10
    }
```

---

#### 步骤 4.2: 计算质量总分

**执行者**: Quality Evaluator

**处理过程**:
```python
def calculate_overall_score(gate_results):
    """
    计算质量总分（加权平均）
    """
    total_weighted_score = 0.0
    total_weight = 0.0

    for gate in gate_results:
        gate_score = gate["score"]
        gate_weight = gate["weight"]

        total_weighted_score += gate_score * gate_weight
        total_weight += gate_weight

    overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

    return overall_score
```

**质量等级**:
```yaml
quality_levels:
  excellent:
    range: [0.95, 1.0]
    label: "优秀"
    color: "green"

  good:
    range: [0.85, 0.95]
    label: "良好"
    color: "blue"

  acceptable:
    range: [0.80, 0.85]
    label: "合格"
    color: "yellow"

  poor:
    range: [0.60, 0.80]
    label: "需改进"
    color: "orange"

  fail:
    range: [0.0, 0.60]
    label: "不合格"
    color: "red"
    action: "阻断交付"
```

---

#### 步骤 4.3: Todo完成度检查

**执行者**: Orchestrator

**处理过程**:
```python
def check_todo_completion(all_phase_states):
    """
    检查Todo List的完成度
    """
    baseline_contract = all_phase_states.phase_0.baseline_contract
    tracker_state = load_current_tracker_state()

    # 1. 统计完成情况
    total_tasks = len(baseline_contract.todo_list)
    completed_tasks = len(tracker_state.completed)
    completion_rate = completed_tasks / total_tasks

    # 2. 检查是否所有任务都已完成
    all_completed = (completion_rate == 1.0)

    # 3. 识别未完成任务
    uncompleted_tasks = [
        task for task in tracker_state.current
        if task["status"] != "completed"
    ]

    # 4. 计算平均偏离度
    deviation_history = tracker_state.deviation_history
    if deviation_history:
        avg_deviation = 1.0 - (sum(deviation_history) / len(deviation_history))
    else:
        avg_deviation = 0.0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": completion_rate,
        "all_completed": all_completed,
        "uncompleted_tasks": uncompleted_tasks,
        "average_deviation": avg_deviation,
        "passed": all_completed and avg_deviation < 0.15
    }
```

**输出示例**:
```yaml
todo_completion:
  total_tasks: 14
  completed_tasks: 14
  completion_rate: 1.0
  all_completed: true
  uncompleted_tasks: []
  average_deviation: 0.08
  passed: true
```

---

#### 步骤 4.4: 生成质量报告

**执行者**: Quality Evaluator

**处理过程**:
```python
def generate_quality_report(gate_results, overall_score, todo_completion):
    """
    生成最终质量报告
    """
    # 确定质量等级
    quality_level = determine_quality_level(overall_score)

    # 收集所有问题
    all_issues = []
    for gate in gate_results:
        if not gate["passed"]:
            failed_checks = [
                check for check in gate["checks"] if not check[1]
            ]
            for check_id, passed, message in failed_checks:
                all_issues.append({
                    "gate": gate["gate_name"],
                    "check": check_id,
                    "message": message,
                    "severity": "critical" if gate.get("critical", False) else "warning"
                })

    # 生成改进建议
    recommendations = generate_recommendations(gate_results, all_issues)

    # 决定是否通过
    pass_decision = (
        overall_score >= 0.80 and
        todo_completion["passed"] and
        not any([issue["severity"] == "critical" for issue in all_issues])
    )

    report = {
        "quality_assessment": {
            "overall_score": overall_score,
            "quality_level": quality_level,
            "pass_decision": pass_decision
        },
        "gate_results": gate_results,
        "todo_completion": todo_completion,
        "issues": all_issues,
        "recommendations": recommendations,
        "statistics": {
            "total_checks": sum([len(gate["checks"]) for gate in gate_results]),
            "passed_checks": sum([
                len([c for c in gate["checks"] if c[1]])
                for gate in gate_results
            ]),
            "critical_issues": len([i for i in all_issues if i["severity"] == "critical"]),
            "warnings": len([i for i in all_issues if i["severity"] == "warning"])
        }
    }

    return report
```

**质量报告示例**:
```yaml
quality_report:
  quality_assessment:
    overall_score: 0.96
    quality_level:
      label: "优秀"
      range: [0.95, 1.0]
      color: "green"
    pass_decision: true

  gate_results:
    - gate_id: "G1"
      gate_name: "代码语法检查"
      passed: true
      score: 1.0
      weight: 0.15

    - gate_id: "G2"
      gate_name: "逻辑完整性检查"
      passed: true
      score: 1.0
      weight: 0.20

    - gate_id: "G3"
      gate_name: "TEM一致性检查"
      passed: true
      score: 0.95
      weight: 0.25

    - gate_id: "G4"
      gate_name: "引用完整性检查 (Guardrails)"
      passed: true
      score: 1.0
      weight: 0.20
      critical: true

    - gate_id: "G5"
      gate_name: "性能基准检查"
      passed: true
      score: 0.90
      weight: 0.10

    - gate_id: "G6"
      gate_name: "交付物完整性检查"
      passed: true
      score: 0.95
      weight: 0.10

  todo_completion:
    total_tasks: 14
    completed_tasks: 14
    completion_rate: 1.0
    all_completed: true
    average_deviation: 0.08
    passed: true

  issues: []

  recommendations:
    - "所有质量检查已通过，建议交付"
    - "代码质量优秀，可直接使用"
    - "建议保留此项目作为最佳实践案例"

  statistics:
    total_checks: 38
    passed_checks: 38
    critical_issues: 0
    warnings: 0

  generated_at: "2025-10-29T11:45:00Z"
```

---

#### 步骤 4.5: 💾 保存 Phase 4 状态

**保存内容**:
```yaml
# phase_4_state.yaml

metadata:
  phase_id: "phase_4"
  phase_name: "质量保证"
  created_at: "2025-10-29T11:35:00Z"
  completed_at: "2025-10-29T11:45:00Z"
  duration: "10分钟"
  depends_on: ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2", "phase_3"]

# 核心交付物 1: 质量报告
quality_report:
  quality_assessment:
    overall_score: 0.96
    quality_level: "优秀"
    pass_decision: true

  gate_results: [...]  # 6个门禁结果详情
  issues: []
  recommendations: [...]
  statistics: {...}

  final_decision:
    approved_for_delivery: true
    approved_at: "2025-10-29T11:45:00Z"
    approver: "Quality Evaluator"
    quality_score: 0.96

  project_metadata:
    project_id: "project_20251029_1120"
    project_name: "生鲜配送冷链调度优化方案"
    created_by: "APS调度智能体系统 v1.0"
    total_duration: "105分钟"

# 核心交付物 2: 门禁状态
gate_status:
  gate_1_syntax: "passed"
  gate_2_logic: "passed"
  gate_3_tem_consistency: "passed"
  gate_4_guardrails: "passed"
  gate_5_performance: "passed"
  gate_6_deliverables: "passed"
  all_gates_passed: true

# 核心交付物 3: Todo完成度状态
todo_completion_status:
  total_tasks: 14
  completed_tasks: 14
  completion_rate: 1.0
  all_completed: true
  average_deviation: 0.08
  passed: true

# 验证信息
verification:
  all_gates_passed: true
  all_todos_completed: true
  no_critical_issues: true
  quality_threshold_met: true
  validation_passed: true
```

---

### 8.2 Phase 4 交付物清单

| 交付物 | 类型 | 格式 | 持久化 | 验证层级 | 说明 |
|--------|------|------|--------|---------|------|
| **quality_report** | 质量报告 | YAML | ✅ | L1: 字段完整性<br/>L2: 分数计算正确<br/>L3: 门禁结果有效 | 包含6层门禁结果、问题、建议、统计 |
| **gate_status** | 门禁状态 | YAML | ✅ | L1: 状态有效 | 各门禁的通过/失败状态 |
| **todo_completion_status** | Todo完成度 | YAML | ✅ | L1: 完成度统计 | 任务完成情况和偏离度 |

---

## 9. 状态依赖关系图

```yaml
Phase_0:
  produces:
    - confirmed_todo_list
    - baseline_contract
    - tracker_initialized
  consumed_by: [Phase_1, Phase_4]

Phase_0_5:
  depends_on: [Phase_0]
  produces:
    - selected_mode
    - workflow_configuration
    - phase_plan
  consumed_by: [Phase_1_5, Phase_2]

Phase_1:
  depends_on: [Phase_0, Phase_0_5]
  produces:
    - requirement_analysis
    - clarified_requirements
    - deviation_score
  consumed_by: [Phase_1_5]

Phase_1_5:
  depends_on: [Phase_0, Phase_0_5, Phase_1]
  produces:
    - ten_element_model (统一真相源)
    - model_baseline
    - model_hash
  consumed_by: [Phase_2, Phase_3, Phase_4]
  critical: true  # 核心交付物

Phase_2:
  depends_on: [Phase_0, Phase_0_5, Phase_1, Phase_1_5]
  produces:
    - domain_analysis
    - constraint_analysis
    - objective_analysis
    - algorithm_recommendations
    - consistency_report
  consumed_by: [Phase_3, Phase_4]

Phase_3:
  depends_on: [Phase_0, Phase_0_5, Phase_1, Phase_1_5, Phase_2]
  produces:
    - integrated_solution
    - implementation_code
    - code_traceability
    - consistency_validation
    - saved_files
    - deliverable_manifest
  consumed_by: [Phase_4]
  critical: true  # 核心交付物

Phase_4:
  depends_on: [Phase_0, Phase_0_5, Phase_1, Phase_1_5, Phase_2, Phase_3]
  produces:
    - quality_report
    - gate_status
    - todo_completion_status
  consumed_by: []  # 最终阶段
  critical: true
```

---

## 10. 验证机制详解

### 10.1 验证层级定义

```yaml
验证层级体系:
  L1 - 字段完整性验证:
    description: "检查必需字段是否存在"
    timing: "保存时立即执行"
    failure_handling: "阻断保存，重试3次"

    checks:
      - 必需字段存在
      - 数据类型正确
      - 非空检查
      - 格式验证

  L2 - 引用完整性验证:
    description: "检查引用路径有效性 (Guardrails)"
    timing: "保存时立即执行"
    failure_handling: "阻断保存，报告错误"

    checks:
      - @专家库引用存在
      - 引用路径可解析
      - 引用文件可访问
      - 引用内容匹配

  L3 - 逻辑一致性验证:
    description: "检查跨Phase状态一致性"
    timing: "Phase完成时执行"
    failure_handling: "警告，但不阻断"

    checks:
      - TEM要素一致性
      - 决策变量匹配
      - 约束目标一致
      - 算法配置合理

  L4 - 代码可追溯性验证:
    description: "检查Theory到Code的映射"
    timing: "Phase 3完成时执行"
    failure_handling: "警告，建议修复"

    checks:
      - 所有约束有代码映射
      - 所有目标有函数实现
      - 算法有完整实现
      - 代码位置准确

  L5 - 性能基准验证:
    description: "检查性能预测合理性"
    timing: "Phase 4质量门禁时执行"
    failure_handling: "警告，记录到报告"

    checks:
      - 运行时间预测
      - 解质量预测
      - 算法参数合理性
      - 代码复杂度

  L6 - 交付物完整性验证:
    description: "检查所有文件完整性"
    timing: "Phase 4质量门禁时执行"
    failure_handling: "阻断交付"

    checks:
      - 必需文件存在
      - 文件大小合理
      - 文件内容完整
      - MANIFEST一致性
```

---

### 10.2 Guardrails 强约束机制

```yaml
Guardrails核心原则:
  principle: "所有知识都必须有明确的@专家库引用"

  enforcement_points:
    - Phase 1.5: TenElementModel构建时
    - Phase 2: 专家分析时
    - Phase 3: 方案集成时
    - Phase 4: 质量门禁4

  citation_format:
    template: "@专家库/{category}/{subcategory}/{template_name}.md"

    examples:
      - "@专家库/约束库/capacity/车辆容量约束.md"
      - "@专家库/目标库/cost/成本最小化.md"
      - "@专家库/算法库/meta-heuristic/遗传算法.md"
      - "@专家库/领域库/vehicle/冷链配送.md"

  verification_algorithm:
    step_1: "提取所有@专家库引用"
    step_2: "解析引用路径到文件系统路径"
    step_3: "验证文件存在性"
    step_4: "验证文件内容匹配"
    step_5: "记录验证结果"

  failure_handling:
    missing_citation:
      severity: "critical"
      action: "阻断Phase进行"
      message: "约束/目标/算法缺少@专家库引用"

    invalid_path:
      severity: "critical"
      action: "阻断Phase进行"
      message: "引用路径无效或文件不存在"

    content_mismatch:
      severity: "warning"
      action: "记录警告，继续执行"
      message: "引用内容与实际使用不完全匹配"

  benefits:
    - "100%可追溯性"
    - "知识来源透明"
    - "支持审计和合规"
    - "知识质量保证"
    - "防止幻觉生成"
```

---

### 10.3 状态持久化验证流程

```python
def save_phase_state_with_verification(phase_id, state_data, max_retries=3):
    """
    带验证的状态保存流程
    """
    for attempt in range(max_retries):
        try:
            # 1. 执行L1验证: 字段完整性
            l1_result = verify_field_completeness(state_data)
            if not l1_result["passed"]:
                raise ValidationError(f"L1验证失败: {l1_result['errors']}")

            # 2. 执行L2验证: 引用完整性 (如果适用)
            if phase_id in ["phase_1_5", "phase_2", "phase_3"]:
                l2_result = verify_citation_integrity(state_data)
                if not l2_result["passed"]:
                    raise GuardrailsViolationError(f"L2验证失败: {l2_result['errors']}")

            # 3. 保存文件
            state_file = f"{STATE_FOLDER}/{phase_id}_state.yaml"
            with open(state_file, 'w', encoding='utf-8') as f:
                yaml.dump(state_data, f, allow_unicode=True)

            # 4. 验证文件已保存
            if not os.path.exists(state_file):
                raise IOError(f"文件保存失败: {state_file}")

            # 5. 计算校验和
            checksum = calculate_checksum(state_file)
            state_data["verification"]["checksum"] = checksum
            state_data["verification"]["saved_at"] = datetime.now().isoformat()

            # 6. 更新验证信息
            with open(state_file, 'w', encoding='utf-8') as f:
                yaml.dump(state_data, f, allow_unicode=True)

            # 7. 创建最新链接
            latest_link = f"{STATE_FOLDER}/latest/{phase_id}_state.yaml"
            if os.path.exists(latest_link):
                os.remove(latest_link)
            os.symlink(state_file, latest_link)

            # 成功
            return {
                "success": True,
                "state_file": state_file,
                "checksum": checksum,
                "verification_passed": True
            }

        except (ValidationError, GuardrailsViolationError, IOError) as e:
            if attempt < max_retries - 1:
                # 重试
                time.sleep(2 ** attempt)  # 指数退避
                continue
            else:
                # 最终失败
                return {
                    "success": False,
                    "error": str(e),
                    "attempt": attempt + 1
                }
```

---

### 10.4 错误恢复机制

```yaml
错误类型与恢复策略:

  ValidationError (字段验证错误):
    severity: "high"
    recovery:
      - action: "自动重试"
        max_retries: 3
        backoff: "指数退避 (1s, 2s, 4s)"
      - action: "修复数据"
        if_possible: true
      - action: "报告用户"
        if_failed: true

    examples:
      - "必需字段缺失"
      - "数据类型错误"
      - "格式不正确"

  GuardrailsViolationError (引用完整性错误):
    severity: "critical"
    recovery:
      - action: "阻断流程"
        immediate: true
      - action: "生成详细错误报告"
      - action: "提示修复方案"
      - action: "等待用户修复"

    examples:
      - "缺少@专家库引用"
      - "引用路径无效"
      - "引用文件不存在"

  ConsistencyError (一致性错误):
    severity: "medium"
    recovery:
      - action: "记录警告"
      - action: "继续执行"
      - action: "在质量报告中说明"

    examples:
      - "TEM与方案不一致"
      - "约束ID不匹配"
      - "目标权重和不为1"

  PerformanceWarning (性能警告):
    severity: "low"
    recovery:
      - action: "记录警告"
      - action: "继续执行"
      - action: "建议优化"

    examples:
      - "预计运行时间过长"
      - "解质量低于预期"
      - "参数配置不optimal"

  IOError (文件IO错误):
    severity: "high"
    recovery:
      - action: "自动重试"
        max_retries: 3
      - action: "检查磁盘空间"
      - action: "检查文件权限"
      - action: "切换备用路径"

    examples:
      - "磁盘空间不足"
      - "文件权限不足"
      - "路径不存在"
```

---

## 11. 完整验证矩阵

| Phase | L1 字段完整性 | L2 引用完整性 | L3 逻辑一致性 | L4 代码可追溯性 | L5 性能基准 | L6 交付物完整性 |
|-------|------------|------------|------------|---------------|-----------|--------------|
| **Phase 0** | ✅ 必需 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 |
| **Phase 0.5** | ✅ 必需 | ❌ 不适用 | ✅ 配置一致性 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 |
| **Phase 1** | ✅ 必需 | ❌ 不适用 | ✅ 需求一致性 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 |
| **Phase 1.5** | ✅ 必需 | ✅ 必需 (Guardrails) | ✅ TEM一致性 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 |
| **Phase 2** | ✅ 必需 | ✅ 必需 (Guardrails) | ✅ 跨专家一致性 | ❌ 不适用 | ❌ 不适用 | ❌ 不适用 |
| **Phase 3** | ✅ 必需 | ✅ 必需 (Guardrails) | ✅ 方案一致性 | ✅ 必需 | ❌ 不适用 | ✅ 文件完整性 |
| **Phase 4** | ✅ 必需 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 | ✅ 检查 |

---

## 12. 总结

### 12.1 工作流完整性

本文档详细描述了APS调度智能体系统从Phase 0到Phase 4的完整工作流，包括：

1. **Phase 0**: 任务规划与Todo List确认
2. **Phase 0.5**: 交互模式选择 (模式A vs 模式B)
3. **Phase 1**: 需求分析与偏离检测
4. **Phase 1.5**: TenElementModel构建 (统一真相源)
5. **Phase 2**: 4专家协调 (领域/约束/目标/算法)
6. **Phase 3**: 方案集成与Theory-to-Code生成
7. **Phase 4**: 6层质量门禁验证

### 12.2 交付物体系

每个Phase都有明确的交付物，并通过YAML文件持久化：

- **17个核心交付物** 跨7个Phase
- **6层验证机制** 确保质量
- **100%可追溯性** 通过Guardrails保证

### 12.3 验证机制完整性

6层验证机制覆盖：
- L1: 字段完整性 (所有Phase)
- L2: 引用完整性 (Guardrails, Phase 1.5/2/3/4)
- L3: 逻辑一致性 (Phase 0.5/1/1.5/2/3/4)
- L4: 代码可追溯性 (Phase 3/4)
- L5: 性能基准 (Phase 4)
- L6: 交付物完整性 (Phase 3/4)

### 12.4 质量保证

- **6层质量门禁** 确保最终交付质量
- **TodoTracker + 偏离检测** 确保任务不偏离
- **状态持久化 + 验证** 确保流程可恢复
- **Guardrails强约束** 确保知识可追溯

---

**文档版本**: V1.0
**最后更新**: 2025-10-29
**维护团队**: APS Product Team
