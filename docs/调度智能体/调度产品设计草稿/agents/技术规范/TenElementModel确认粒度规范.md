# TenElementModel 确认粒度规范

---

version: "1.0"
created: "2025-10-16"
updated: "2025-10-16"
status: "active"
applies_to: "V4.3+"
v4_3_feature: true

---

## 📋 文档概述

本规范定义了 TenElementModel (十要素模型) 在不同交互模式下的确认粒度标准,用于支持 V4.3 的双模式交互系统。

### 核心概念

**框架级确认** (Framework-Level Confirmation):

- 仅确认模型的整体结构和要素类型
- 用于增量确认模式 (模式B) 的 Phase 1.5
- 目的: 建立全局视图,细节推迟到各专家阶段

**细节级确认** (Detail-Level Confirmation):

- 确认每个要素的具体参数和边界条件
- 用于集中确认模式 (模式A) 的完整确认
- 用于增量确认模式 (模式B) 的专家阶段

---

## 🎯 粒度划分标准

### 原则

框架级确认应满足:

1. **可理解性**: 用户无需深入专业知识即可理解
2. **全局视图**: 提供问题的整体结构和规模感
3. **可修改性**: 后续可以基于框架进行细节补充
4. **最小性**: 只包含建立全局视图所需的最少信息

细节级确认应满足:

1. **可执行性**: 包含足够的细节用于算法实现
2. **专业性**: 需要专家指导或专业知识才能确定
3. **上下文依赖**: 依赖于其他要素的确认结果
4. **精确性**: 需要具体的数值、范围、公式等

---

## 📊 十要素粒度划分详细规范

### 1. 决策变量 (Decision Variables)

#### 框架级 (Framework)

```yaml
框架级属性:
  - count: 决策变量数量
  - names: 变量名称列表
  - types: 变量类型列表 (integer, float, boolean, categorical)
  - descriptions: 简短描述 (1句话)

示例:
  decision_variables:
    count: 3
    names: ['车辆分配', '路径选择', '服务时间']
    types: ['integer', 'integer_list', 'float']
    descriptions:
      - '每个客户分配哪辆车'
      - '每辆车的访问顺序'
      - '每个客户的具体服务时间'
```

#### 细节级 (Detail)

```yaml
细节级属性:
  - domain: 取值域 (范围、离散值集合)
  - initial_value: 初始值或初始化策略
  - constraints_related: 相关的约束列表
  - optimization_role: 在优化中的角色 (主要/辅助)

示例:
  decision_variables:
    - name: '车辆分配'
      type: 'integer'
      domain:
        type: 'range'
        min: 1
        max: 10 # 10辆车
      initial_value:
        strategy: 'nearest_vehicle'
        description: '初始分配给最近的车辆'
      constraints_related:
        - '容量约束'
        - '时间窗约束'
      optimization_role: 'primary'
```

#### 确认责任分配

- **框架级**: 编排智能体 (Phase 1.5)
- **细节级**:
  - domain → 领域专家 (基于业务规模)
  - initial_value → 算法专家 (基于算法选择)
  - constraints_related → 约束专家 (交叉验证)

---

### 2. 约束条件 (Constraints)

#### 框架级 (Framework)

```yaml
框架级属性:
  - count: 约束数量
  - categories: 约束类别列表
  - names: 约束名称列表
  - scope: 约束作用范围 (local/global)

示例:
  constraints:
    count: 5
    categories: ['时间约束', '容量约束', '逻辑约束']
    names:
      - '时间窗约束'
      - '车辆容量约束'
      - '客户必须服务约束'
      - '车辆最大工作时长'
      - '服务顺序约束'
    scopes: ['local', 'local', 'global', 'local', 'local']
```

#### 细节级 (Detail)

```yaml
细节级属性:
  - hardness: 约束硬度 (hard/soft/preference)
  - bounds: 边界值和参数
  - penalty: 违反惩罚函数 (对于软约束)
  - priority: 优先级 (对于冲突解决)
  - mathematical_form: 数学表达式

示例:
  constraints:
    - name: '时间窗约束'
      category: '时间约束'
      scope: 'local'
      hardness: 'soft'
      bounds:
        time_window_start: [8, 9, 10, ...] # 每个客户的时间窗
        time_window_end: [10, 11, 12, ...]
        tolerance: 10 # 分钟,允许违反的幅度
      penalty:
        type: 'linear'
        coefficient: 100 # 每分钟违反的惩罚系数
      priority: 'high'
      mathematical_form: |
        对于客户 i:
        如果 service_time[i] < time_window_start[i] - tolerance:
          penalty += 100 * (time_window_start[i] - tolerance - service_time[i])
        如果 service_time[i] > time_window_end[i] + tolerance:
          penalty += 100 * (service_time[i] - time_window_end[i] - tolerance)
```

#### 确认责任分配

- **框架级**: 编排智能体 (Phase 1.5)
- **细节级**:
  - hardness → 约束专家 (逐条确认)
  - bounds → 领域专家 (基于业务数据) + 约束专家 (验证合理性)
  - penalty → 目标专家 (权衡成本) + 约束专家 (设计惩罚函数)
  - mathematical_form → 约束专家 (建模)

---

### 3. 优化目标 (Objectives)

#### 框架级 (Framework)

```yaml
框架级属性:
  - count: 目标数量
  - types: 目标类型列表 (minimize/maximize)
  - names: 目标名称列表
  - categories: 目标类别 (cost/time/quality/efficiency)

示例:
  objectives:
    count: 2
    types: ['minimize', 'minimize']
    names: ['总运输成本', '总完成时间']
    categories: ['cost', 'time']
```

#### 细节级 (Detail)

```yaml
细节级属性:
  - weight: 目标权重 (对于多目标)
  - formula: 目标函数公式
  - components: 目标组成部分 (子目标)
  - evaluation_metric: 评价指标
  - target_value: 目标值 (如有)

示例:
  objectives:
    - name: '总运输成本'
      type: 'minimize'
      category: 'cost'
      weight: 0.6
      components:
        - name: '固定成本'
          formula: '车辆数量 * 固定成本/车'
          value: 'num_vehicles * 500'
        - name: '距离成本'
          formula: '总距离 * 单位距离成本'
          value: 'total_distance * 2.5'
        - name: '时间成本'
          formula: '总时间 * 单位时间成本'
          value: 'total_time * 50'
      formula: '固定成本 + 距离成本 + 时间成本'
      evaluation_metric: '元 (CNY)'
      target_value:
        type: 'upper_bound'
        value: 10000 # 不超过1万元
```

#### 确认责任分配

- **框架级**: 编排智能体 (Phase 1.5)
- **细节级**:
  - weight → 目标专家 (逐条确认用户优先级)
  - formula & components → 目标专家 (设计) + 领域专家 (提供业务数据)
  - evaluation_metric → 目标专家
  - target_value → 领域专家 (业务目标)

---

### 4. 算法选择 (Algorithm)

#### 框架级 (Framework)

```yaml
框架级属性:
  - category: 算法类别 (exact/heuristic/metaheuristic)
  - complexity_estimate: 复杂度估算 (simple/medium/complex)

示例:
  algorithm:
    category: 'metaheuristic'
    complexity_estimate: 'medium'
```

#### 细节级 (Detail)

```yaml
细节级属性:
  - specific_algorithm: 具体算法名称
  - parameters: 算法参数配置
  - termination_criteria: 终止条件
  - performance_requirements: 性能要求

示例:
  algorithm:
    category: 'metaheuristic'
    specific_algorithm: '遗传算法 (Genetic Algorithm)'
    parameters:
      population_size: 100
      crossover_rate: 0.8
      mutation_rate: 0.1
      selection_method: 'tournament'
      elitism: true
      elite_size: 5
    termination_criteria:
      max_generations: 1000
      convergence_threshold: 0.001
      max_time: 300 # 秒
    performance_requirements:
      solution_quality: '接近最优解 (gap < 5%)'
      runtime: '< 5分钟'
      memory: '< 4GB'
```

#### 确认责任分配

- **框架级**: 编排智能体 (Phase 1.5,基于问题复杂度)
- **细节级**:
  - specific_algorithm → 算法专家 (基于问题特征推荐)
  - parameters → 算法专家 (逐个参数确认)
  - termination_criteria → 算法专家 + 用户 (时间要求)
  - performance_requirements → 用户 + 算法专家 (可行性评估)

---

### 5. 时间模型 (Time Model)

#### 框架级 (Framework)

```yaml
框架级属性:
  - type: 时间类型 (discrete/continuous/mixed)
  - granularity: 时间粒度 (second/minute/hour/day)
  - has_uncertainty: 是否有不确定性

示例:
  time_model:
    type: 'discrete'
    granularity: 'minute'
    has_uncertainty: true
```

#### 细节级 (Detail)

```yaml
细节级属性:
  - time_horizon: 时间跨度
  - time_windows: 时间窗定义
  - travel_time_matrix: 旅行时间矩阵
  - service_time: 服务时间
  - uncertainty_model: 不确定性模型 (如有)

示例:
  time_model:
    type: 'discrete'
    granularity: 'minute'
    time_horizon:
      start: '08:00'
      end: '18:00'
      duration_minutes: 600
    travel_time_matrix:
      type: 'symmetric'
      source: 'distance_matrix + average_speed'
      average_speed: 40 # km/h
    service_time:
      type: 'fixed'
      default: 15 # 分钟
      customer_specific: true
    uncertainty_model:
      type: 'stochastic'
      distribution: 'normal'
      parameters:
        mean: 0
        std_dev: 5 # 分钟,旅行时间的标准差
```

#### 确认责任分配

- **框架级**: 编排智能体 (Phase 1.5)
- **细节级**:
  - time_horizon → 领域专家 (业务时间)
  - travel_time_matrix → 领域专家 (提供数据)
  - service_time → 领域专家 (业务数据)
  - uncertainty_model → 领域专家 (历史数据分析) + 算法专家 (建模)

---

### 6-10. 其他要素

其他要素 (数据源、求解器配置、输出格式、性能指标、验证规则) 的粒度划分遵循相同原则:

- **框架级**: 类型、数量、类别
- **细节级**: 具体配置、参数、公式

---

## 💻 代码实现规范

### 框架级提取器

```python
class FrameworkLevelExtractor:
    """提取TenElementModel的框架级信息"""

    def extract_framework(self, full_model: dict) -> dict:
        """
        从完整模型中提取框架级信息

        Args:
            full_model: 完整的 TenElementModel

        Returns:
            框架级模型
        """
        framework = {}

        # 1. 决策变量框架
        framework["decision_variables"] = {
            "count": len(full_model.get("decision_variables", [])),
            "names": [v["name"] for v in full_model.get("decision_variables", [])],
            "types": [v["type"] for v in full_model.get("decision_variables", [])],
            "descriptions": [v.get("description", "") for v in full_model.get("decision_variables", [])]
        }

        # 2. 约束条件框架
        constraints = full_model.get("constraints", [])
        framework["constraints"] = {
            "count": len(constraints),
            "categories": list(set(c.get("category", "未分类") for c in constraints)),
            "names": [c["name"] for c in constraints],
            "scopes": [c.get("scope", "local") for c in constraints]
        }

        # 3. 优化目标框架
        objectives = full_model.get("objectives", [])
        framework["objectives"] = {
            "count": len(objectives),
            "types": [o.get("type", "minimize") for o in objectives],
            "names": [o["name"] for o in objectives],
            "categories": [o.get("category", "未分类") for o in objectives]
        }

        # 4. 算法框架
        algorithm = full_model.get("algorithm", {})
        framework["algorithm"] = {
            "category": algorithm.get("category", "未指定"),
            "complexity_estimate": self._estimate_complexity(full_model)
        }

        # 5. 时间模型框架
        time_model = full_model.get("time_model", {})
        framework["time_model"] = {
            "type": time_model.get("type", "discrete"),
            "granularity": time_model.get("granularity", "minute"),
            "has_uncertainty": time_model.get("has_uncertainty", False)
        }

        # ... 其他要素的框架提取

        return framework

    def _estimate_complexity(self, full_model: dict) -> str:
        """基于问题规模估算复杂度"""
        var_count = len(full_model.get("decision_variables", []))
        constraint_count = len(full_model.get("constraints", []))

        if var_count <= 10 and constraint_count <= 5:
            return "simple"
        elif var_count <= 50 and constraint_count <= 20:
            return "medium"
        else:
            return "complex"
```

### 细节项生成器

```python
class DetailItemsGenerator:
    """生成需要增量确认的细节项"""

    def generate_detail_items(
        self,
        element_type: str,
        framework: dict,
        full_model: dict
    ) -> list:
        """
        生成特定要素的细节确认项

        Args:
            element_type: 要素类型 (decision_variables, constraints, etc.)
            framework: 框架级模型
            full_model: 完整模型 (用于提取细节)

        Returns:
            细节确认项列表
        """
        if element_type == "constraints":
            return self._generate_constraint_details(framework, full_model)
        elif element_type == "objectives":
            return self._generate_objective_details(framework, full_model)
        # ... 其他要素类型

    def _generate_constraint_details(self, framework: dict, full_model: dict) -> list:
        """生成约束细节确认项"""
        items = []

        constraints = full_model.get("constraints", [])
        for i, constraint in enumerate(constraints):
            item = {
                "element_type": "constraint",
                "index": i,
                "name": constraint["name"],
                "framework_info": {
                    "category": constraint.get("category"),
                    "scope": constraint.get("scope")
                },
                "confirmation_questions": [
                    {
                        "id": f"constraint_{i}_hardness",
                        "question": f"「{constraint['name']}」的约束硬度?",
                        "type": "single_choice",
                        "options": [
                            {"value": "hard", "label": "硬约束 (必须满足,不可违反)"},
                            {"value": "soft", "label": "软约束 (可适度违反,但需惩罚)"},
                            {"value": "preference", "label": "偏好约束 (尽量满足,违反影响较小)"}
                        ],
                        "default": constraint.get("hardness", "hard"),
                        "field": "hardness",
                        "expert": "constraint-expert"
                    },
                    {
                        "id": f"constraint_{i}_bounds",
                        "question": f"「{constraint['name']}」的具体边界值?",
                        "type": "structured_input",
                        "schema": constraint.get("bounds_schema", {}),
                        "context": "请根据业务实际情况填写",
                        "field": "bounds",
                        "expert": "domain-expert + constraint-expert"
                    },
                    {
                        "id": f"constraint_{i}_penalty",
                        "question": f"「{constraint['name']}」违反时的惩罚函数?",
                        "type": "formula_input",
                        "condition": "hardness == 'soft'",
                        "template": "linear: coefficient * violation_amount",
                        "field": "penalty",
                        "expert": "objective-expert + constraint-expert"
                    }
                ]
            }
            items.append(item)

        return items
```

---

## 🔄 使用流程

### 模式A: 集中确认模式

```python
# Phase 1.5: 完整确认
full_model = generate_complete_ten_element_model(requirements)

# 一次性确认所有要素的框架和细节
confirmed_model = confirm_with_user(full_model, confirmation_type="complete")

# 后续各专家直接使用确认后的模型
```

### 模式B: 增量确认模式

```python
# Phase 1.5: 框架确认
full_model = generate_complete_ten_element_model(requirements)
extractor = FrameworkLevelExtractor()
framework = extractor.extract_framework(full_model)

# 仅确认框架
confirmed_framework = confirm_with_user(framework, confirmation_type="framework")

# Phase 2: 各专家增量确认细节
generator = DetailItemsGenerator()

# 2.1 约束专家
constraint_details = generator.generate_detail_items("constraints", confirmed_framework, full_model)
confirmed_constraints = incremental_confirm_with_expert(
    "constraint-expert",
    constraint_details
)

# 2.2 目标专家
objective_details = generator.generate_detail_items("objectives", confirmed_framework, full_model)
confirmed_objectives = incremental_confirm_with_expert(
    "objective-expert",
    objective_details
)

# ... 其他专家

# Phase 2.5: 合并框架和细节
complete_model = merge_framework_and_details(
    confirmed_framework,
    confirmed_constraints,
    confirmed_objectives,
    ...
)
```

---

## ✅ 质量保证

### 框架级确认的验证清单

- [ ] 用户能够理解所有要素的名称和类型
- [ ] 要素数量合理 (变量数 < 100, 约束数 < 50)
- [ ] 类别划分清晰明确
- [ ] 没有包含需要专业知识才能理解的细节

### 细节级确认的验证清单

- [ ] 每个细节项都有明确的确认问题
- [ ] 提供了充分的背景信息和示例
- [ ] 分配给了合适的专家负责
- [ ] 包含了足够的细节用于算法实现

---

## 📚 示例: 生鲜配送问题

### 框架级模型 (Phase 1.5 确认)

```yaml
decision_variables:
  count: 3
  names: ['车辆分配', '路径规划', '服务时间']
  types: ['integer', 'permutation', 'float_array']
  descriptions:
    - '每个订单分配给哪辆配送车'
    - '每辆车的配送顺序'
    - '每个订单的具体送达时间'

constraints:
  count: 4
  categories: ['时间约束', '容量约束', '业务规则']
  names:
    - '配送时间窗'
    - '车辆载重限制'
    - '温度保鲜时长'
    - '司机工作时长'
  scopes: ['local', 'local', 'global', 'local']

objectives:
  count: 2
  types: ['minimize', 'minimize']
  names: ['配送总成本', '顾客等待时间']
  categories: ['cost', 'time']

algorithm:
  category: 'metaheuristic'
  complexity_estimate: 'medium'

time_model:
  type: 'discrete'
  granularity: 'minute'
  has_uncertainty: true
```

**用户确认反馈**: "看起来很合理,3个决策变量和4个主要约束符合我的理解。我们主要关注成本和顾客满意度。"

### 细节级确认项 (Phase 2 各专家增量确认)

#### 约束专家确认 "配送时间窗"

```yaml
确认项 1/4:

问题: 「配送时间窗」的约束硬度?

当前分析: 基于生鲜配送的时效性要求,建议设为「软约束」,允许适度延误(最多15分钟),
  但对延误进行惩罚。这样既保证了时效性,又给算法留有优化空间。

选项: 1. ✅ 确认分析,继续下一项
  2. 📝 修改为硬约束 (绝对不能延误)
  3. 📝 修改为偏好约束 (延误影响较小)
  4. 🔍 需要更多背景信息
  5. ❓ 请举例说明不同选择的影响
  ...
```

**用户反馈**: "1,我同意设为软约束,但延误惩罚要足够高,保证大部分订单按时送达"

#### 目标专家确认 "配送总成本"

```yaml
确认项 1/2:

问题: 「配送总成本」和「顾客等待时间」的权重分配?

当前分析:
  两个目标的权衡:
    - 成本优先: 减少车辆数、优化路径、降低运营成本
    - 时效优先: 更快配送、提升顾客满意度

  建议权重: 成本 0.6, 时间 0.4
  理由: 作为商业企业,成本控制是基础,但也要保证服务质量

选项: 1. ✅ 确认建议权重 (成本 60%, 时间 40%)
  2. 📝 调整为成本优先 (成本 70%, 时间 30%)
  3. 📝 调整为时效优先 (成本 40%, 时间 60%)
  4. 📝 平衡权重 (成本 50%, 时间 50%)
  5. 📝 自定义权重
  6. 🔍 查看不同权重的模拟结果
  ...
```

**用户反馈**: "2,我们要更强调成本控制,设为7:3"

---

## 版本历史

**V1.0** (2025-10-16):

- 初始版本
- 定义框架级和细节级确认的标准
- 为每个十要素提供详细的粒度划分
- 提供代码实现规范

---

**最后更新**: 2025-10-16
**维护者**: APS项目组
**关联特性**: V4.3 双模式交互系统
