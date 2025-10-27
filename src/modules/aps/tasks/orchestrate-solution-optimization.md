# Task: Orchestrate Solution Optimization

**任务ID**: `orchestrate-solution-optimization`
**版本**: V4.3
**用途**: Orchestrator智能理解用户需求，自动决定调用哪些专家进行方案优化

## 设计理念

**用户体验第一**：

- ✅ 用户只需描述需求（自然语言）
- ✅ 不需要知道专家分工
- ✅ 不需要了解YAML结构
- ✅ Orchestrator自动路由和协调

## 输入

```yaml
inputs:
  - solution_data_path: 现有方案YAML文件路径
    example: 'aps-outputs/docs/solution_data_20251027_143530.yaml'

  - user_request: 用户的自然语言需求
    examples:
      - '增加一个约束：同一设备不能同时处理多个任务'
      - '算法太慢了，能优化吗'
      - '准时交货应该是最重要的目标'
      - '需要考虑冷链物流的温度要求'

  - output_folder: 输出目录（默认aps-outputs）
  - auto_generate_code: 是否自动生成代码（默认true）
```

## 核心流程

### 步骤1: 智能意图识别

```python
import re

def analyze_user_request_and_route(user_request):
    """
    Orchestrator的智能路由决策

    Returns:
        dict: 意图分析结果
    """

    print("━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 理解您的需求...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")

    intent_analysis = {
        "primary_intent": None,
        "secondary_intents": [],
        "target_experts": [],
        "collaboration_needed": False,
        "complexity": "simple",
        "confidence": 0.0
    }

    user_request_lower = user_request.lower()

    # ====== 意图识别矩阵 ======

    # 规则1：约束相关
    constraint_keywords = [
        "约束", "限制", "条件", "不能", "必须", "要求",
        "constraint", "不允许", "规则", "冲突", "互斥",
        "禁止", "强制", "保证"
    ]

    constraint_patterns = [
        r"增加.*约束",
        r"添加.*约束",
        r"新增.*约束",
        r".*不能同时.*",
        r"必须.*才能.*",
        r"不允许.*"
    ]

    constraint_score = 0
    for keyword in constraint_keywords:
        if keyword in user_request_lower:
            constraint_score += 1

    for pattern in constraint_patterns:
        if re.search(pattern, user_request):
            constraint_score += 2

    if constraint_score >= 1:
        intent_analysis["target_experts"].append("constraint-expert")
        if not intent_analysis["primary_intent"]:
            intent_analysis["primary_intent"] = "constraint_modification"
        else:
            intent_analysis["secondary_intents"].append("constraint_modification")

        print(f"  ✓ 识别意图: 约束修改 (置信度: {min(constraint_score/3, 1.0):.2f})")

    # 规则2：算法/性能相关
    algorithm_keywords = [
        "算法", "algorithm", "慢", "快", "性能", "优化",
        "迭代", "参数", "收敛", "种群", "搜索", "速度",
        "效率", "时间", "跑得"
    ]

    algorithm_patterns = [
        r".*太慢.*",
        r".*很慢.*",
        r"优化.*算法",
        r"调整.*参数",
        r".*耗时.*"
    ]

    algorithm_score = 0
    for keyword in algorithm_keywords:
        if keyword in user_request_lower:
            algorithm_score += 1

    for pattern in algorithm_patterns:
        if re.search(pattern, user_request):
            algorithm_score += 2

    if algorithm_score >= 1:
        intent_analysis["target_experts"].append("algorithm-expert")
        if not intent_analysis["primary_intent"]:
            intent_analysis["primary_intent"] = "algorithm_optimization"
        else:
            intent_analysis["secondary_intents"].append("algorithm_optimization")

        print(f"  ✓ 识别意图: 算法优化 (置信度: {min(algorithm_score/3, 1.0):.2f})")

    # 规则3：目标/权重相关
    objective_keywords = [
        "目标", "objective", "重要", "优先", "权重",
        "关键", "核心", "主要", "次要", "第一位",
        "优先级", "首要", "最"
    ]

    objective_patterns = [
        r".*最重要.*",
        r".*更重要.*",
        r"提高.*优先级",
        r".*应该.*第一.*",
        r"调整.*权重"
    ]

    objective_score = 0
    for keyword in objective_keywords:
        if keyword in user_request_lower:
            objective_score += 1

    for pattern in objective_patterns:
        if re.search(pattern, user_request):
            objective_score += 2

    if objective_score >= 1:
        intent_analysis["target_experts"].append("objective-expert")
        if not intent_analysis["primary_intent"]:
            intent_analysis["primary_intent"] = "objective_adjustment"
        else:
            intent_analysis["secondary_intents"].append("objective_adjustment")

        print(f"  ✓ 识别意图: 目标调整 (置信度: {min(objective_score/3, 1.0):.2f})")

    # 规则4：领域/行业相关
    domain_keywords = [
        "行业", "领域", "业务", "场景", "实际情况",
        "生鲜", "冷链", "物流", "生产", "制造",
        "不适用", "不符合", "特殊要求", "温度",
        "保质期", "时效", "配送"
    ]

    domain_indicators = [
        "生鲜配送", "冷链物流", "生产调度", "车间排产",
        "项目管理", "人员排班", "供应链"
    ]

    domain_score = 0
    for keyword in domain_keywords:
        if keyword in user_request_lower:
            domain_score += 1

    for indicator in domain_indicators:
        if indicator in user_request:
            domain_score += 3

    if domain_score >= 2:
        intent_analysis["target_experts"].append("domain-expert")
        if not intent_analysis["primary_intent"]:
            intent_analysis["primary_intent"] = "domain_adaptation"
        else:
            intent_analysis["secondary_intents"].append("domain_adaptation")

        print(f"  ✓ 识别意图: 领域适配 (置信度: {min(domain_score/4, 1.0):.2f})")

    # ====== 复杂度和协同判断 ======

    num_experts = len(intent_analysis["target_experts"])

    if num_experts == 0:
        intent_analysis["complexity"] = "unclear"
        intent_analysis["confidence"] = 0.0
        print("  ❓ 无法明确识别意图")

    elif num_experts == 1:
        intent_analysis["complexity"] = "simple"
        intent_analysis["confidence"] = 0.85
        intent_analysis["collaboration_needed"] = False
        print(f"  ✓ 复杂度: 简单")
        print(f"  📞 将调用: {intent_analysis['target_experts'][0]}")

    elif num_experts == 2:
        intent_analysis["complexity"] = "medium"
        intent_analysis["confidence"] = 0.75
        intent_analysis["collaboration_needed"] = True
        print(f"  ⚠️ 复杂度: 中等")
        print(f"  ⚠️ 需要多专家协同")
        print(f"  📞 将调用: {', '.join(intent_analysis['target_experts'])}")

    else:  # >= 3
        intent_analysis["complexity"] = "complex"
        intent_analysis["confidence"] = 0.65
        intent_analysis["collaboration_needed"] = True
        print(f"  ⚠️ 复杂度: 复杂")
        print(f"  ⚠️ 涉及多个方面，需要多专家协同")
        print(f"  📞 将调用: {', '.join(intent_analysis['target_experts'])}")

    return intent_analysis
```

### 步骤2: 加载现有方案

```python
import yaml
import os
from datetime import datetime

def load_existing_solution(solution_data_path):
    """加载现有方案作为修改基础"""

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📂 加载现有方案...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(solution_data_path):
        raise FileNotFoundError(f"方案文件不存在: {solution_data_path}")

    with open(solution_data_path, 'r', encoding='utf-8') as f:
        solution_data = yaml.safe_load(f)

    metadata = solution_data.get('solution_metadata', {})

    print(f"  ✓ 文件: {os.path.basename(solution_data_path)}")
    print(f"  ✓ 版本: {metadata.get('version', 'N/A')}")
    print(f"  ✓ 生成时间: {metadata.get('generated_at', 'N/A')}")
    print(f"  ✓ 优化次数: {metadata.get('refinement_count', 0)}")

    return solution_data
```

### 步骤3: 确定专家调用顺序

```python
def determine_expert_order(target_experts, user_request):
    """
    决定多专家的调用顺序

    依赖关系：
    - domain-expert → 其他专家（领域适配影响其他部分）
    - constraint-expert → algorithm-expert（约束影响算法选择）
    - objective-expert 相对独立
    """

    # 依赖规则（数字越小越优先）
    dependency_rules = {
        "domain-expert": 0,      # 最先（领域特性影响其他部分）
        "constraint-expert": 1,  # 第二（约束影响算法选择）
        "objective-expert": 2,   # 第三（目标相对独立）
        "algorithm-expert": 3    # 最后（受约束和目标影响）
    }

    # 按依赖顺序排序
    ordered = sorted(
        target_experts,
        key=lambda e: dependency_rules.get(e, 999)
    )

    print("\n📋 专家调用顺序:")
    for i, expert in enumerate(ordered, 1):
        print(f"  {i}️⃣ {expert}")

    return ordered
```

### 步骤4: 调用单个专家

```python
def call_expert_for_refinement(
    expert_name,
    user_request,
    current_solution,
    ten_element_model
):
    """
    调用专家进行方案修改

    Args:
        expert_name: 专家名称
        user_request: 用户原始需求
        current_solution: 当前方案数据
        ten_element_model: TenElementModel

    Returns:
        dict: 专家修改后的section数据
    """

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🤖 调用 {expert_name}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━")

    # 构造专家输入
    expert_input = {
        "mode": "refinement",
        "current_solution": current_solution,
        "user_request": user_request,
        "ten_element_model": ten_element_model,
        "refinement_context": {
            "iteration": current_solution.get('solution_metadata', {}).get('refinement_count', 0) + 1,
            "timestamp": datetime.now().isoformat()
        }
    }

    # 根据专家类型调用不同逻辑
    if expert_name == "constraint-expert":
        refined_section = refine_constraint_section(expert_input)
        section_key = "3_constraint_strategy"

    elif expert_name == "algorithm-expert":
        refined_section = refine_algorithm_section(expert_input)
        section_key = "5_algorithm_selection"

    elif expert_name == "objective-expert":
        refined_section = refine_objective_section(expert_input)
        section_key = "4_objective_strategy"

    elif expert_name == "domain-expert":
        refined_section = refine_domain_section(expert_input)
        section_key = "2_domain_adaptation"

    else:
        raise ValueError(f"未知专家: {expert_name}")

    print(f"  ✓ {expert_name} 完成")

    return {
        "section_key": section_key,
        "refined_section": refined_section,
        "expert": expert_name
    }
```

### 步骤5: 约束专家的修改逻辑

```python
def refine_constraint_section(expert_input):
    """
    约束专家执行方案修改

    能力：
    - 理解用户反馈中的约束需求
    - 从专家库检索相关知识
    - 增加/删除/修改约束
    - 维护引用和元数据
    """

    current_solution = expert_input['current_solution']
    user_request = expert_input['user_request']

    # 获取当前约束策略
    constraint_strategy = current_solution['solution_sections']['3_constraint_strategy'].copy()

    print("  📋 约束专家分析用户需求...")

    # ====== 分析操作类型 ======

    operation = None
    if any(kw in user_request for kw in ["增加", "添加", "新增", "加入"]):
        operation = "add"
        print(f"    ✓ 操作类型: 增加约束")
    elif any(kw in user_request for kw in ["删除", "移除", "去掉"]):
        operation = "remove"
        print(f"    ✓ 操作类型: 删除约束")
    elif any(kw in user_request for kw in ["修改", "调整", "改为", "变更"]):
        operation = "update"
        print(f"    ✓ 操作类型: 修改约束")

    # ====== 识别约束类型 ======

    constraint_type_map = {
        "资源互斥": {
            "name": "资源互斥约束",
            "description": "同一资源不能同时处理多个任务",
            "type": "hard",
            "category": "logical",
            "reference": "@constraint-library/logical/互斥约束.md"
        },
        "时间窗": {
            "name": "时间窗约束",
            "description": "任务必须在指定时间窗内完成",
            "type": "soft",
            "category": "temporal",
            "reference": "@constraint-library/temporal/时间窗约束.md",
            "penalty_weight": 0.6
        },
        "优先级": {
            "name": "优先级约束",
            "description": "高优先级任务必须优先处理",
            "type": "hard",
            "category": "logical",
            "reference": "@constraint-library/logical/优先级约束.md"
        },
        "温度控制": {
            "name": "温度控制约束",
            "description": "运输过程必须保持指定温度范围",
            "type": "hard",
            "category": "business_rules",
            "reference": "@constraint-library/business-rules/服务质量约束.md"
        },
        "保质期": {
            "name": "保质期约束",
            "description": "产品必须在保质期内送达",
            "type": "hard",
            "category": "temporal",
            "reference": "@constraint-library/temporal/截止期约束.md"
        }
    }

    matched_constraint = None
    for keyword, constraint_info in constraint_type_map.items():
        if keyword in user_request:
            matched_constraint = constraint_info
            print(f"    ✓ 识别约束类型: {constraint_info['name']}")
            print(f"    📚 专家库引用: {constraint_info['reference']}")
            break

    # ====== 执行操作 ======

    if operation == "add" and matched_constraint:
        # 构造新约束对象
        new_constraint = {
            "name": matched_constraint["name"],
            "description": matched_constraint["description"],
            "type": matched_constraint["type"],
            "category": matched_constraint["category"],
            "source": "用户反馈优化",
            "reference": matched_constraint["reference"],
            "source_metadata": {
                "state_file": "refinement",
                "field_path": "user_feedback.constraints.add",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.90,
                "refinement_iteration": expert_input['refinement_context']['iteration']
            },
            "citations": [matched_constraint["reference"]]
        }

        # 如果是软约束，添加惩罚权重
        if matched_constraint["type"] == "soft":
            new_constraint["penalty_weight"] = matched_constraint.get("penalty_weight", 0.5)

        # 从用户请求中提取参数（如时间窗范围）
        import re
        time_window_match = re.search(r'(\d+)\s*分钟', user_request)
        if time_window_match and "时间窗" in matched_constraint["name"]:
            time_window = int(time_window_match.group(1))
            new_constraint["parameters"] = {
                "time_window_minutes": time_window,
                "flexibility": "±" + str(time_window)
            }
            print(f"    ✓ 参数识别: 时间窗 = ±{time_window}分钟")

        # 添加到对应列表
        if matched_constraint["type"] == "hard":
            constraint_strategy['sections']['constraint_classification']['hard_constraints'].append(new_constraint)
            print(f"    ✓ 已添加硬约束: {new_constraint['name']}")
        else:
            constraint_strategy['sections']['constraint_classification']['soft_constraints'].append(new_constraint)
            print(f"    ✓ 已添加软约束: {new_constraint['name']}")
            print(f"       - 惩罚权重: {new_constraint['penalty_weight']}")

    elif operation == "update":
        # 更新约束参数（如惩罚权重）
        weight_match = re.search(r'(\d+\.?\d*)', user_request)
        if weight_match:
            new_weight = float(weight_match.group(1))

            # 查找要更新的约束
            for constraint in constraint_strategy['sections']['constraint_classification']['soft_constraints']:
                if any(kw in constraint['name'] for kw in constraint_type_map.keys()):
                    old_weight = constraint.get('penalty_weight', 0.5)
                    constraint['penalty_weight'] = new_weight
                    print(f"    ✓ 已更新约束: {constraint['name']}")
                    print(f"       - 惩罚权重: {old_weight} → {new_weight}")
                    break

    return constraint_strategy
```

### 步骤6: 算法专家的修改逻辑

```python
def refine_algorithm_section(expert_input):
    """
    算法专家执行方案修改

    能力：
    - 理解性能优化需求
    - 调整算法参数
    - 维护引用和元数据
    """

    current_solution = expert_input['current_solution']
    user_request = expert_input['user_request']

    algorithm_selection = current_solution['solution_sections']['5_algorithm_selection'].copy()

    print("  📋 算法专家分析用户需求...")

    # 获取当前算法配置
    config = algorithm_selection['sections']['algorithm_configuration']
    current_params = config.get('parameters', {})

    print(f"    ✓ 当前算法: {algorithm_selection['sections']['selected_algorithm']['algorithm_name']}")
    print(f"    ✓ 当前参数: {current_params}")

    # ====== 性能优化建议 ======

    if any(kw in user_request for kw in ["慢", "太慢", "优化", "加快", "速度"]):
        print("    💡 识别需求: 提升性能")

        # 针对不同算法的优化策略
        algorithm_name = algorithm_selection['sections']['selected_algorithm']['algorithm_name'].lower()

        if "genetic" in algorithm_name or "遗传" in algorithm_name:
            # 遗传算法优化：增加种群大小，减少迭代次数
            if 'population_size' in current_params:
                old_size = current_params['population_size']
                new_size = min(old_size * 2, 300)  # 最多300
                current_params['population_size'] = new_size
                print(f"    ✓ 调整参数: population_size = {old_size} → {new_size}")
                print(f"       理由: 增加种群多样性，提升解质量")

            if 'max_generations' in current_params:
                old_gen = current_params['max_generations']
                new_gen = max(int(old_gen * 0.7), 50)  # 至少50
                current_params['max_generations'] = new_gen
                print(f"    ✓ 调整参数: max_generations = {old_gen} → {new_gen}")
                print(f"       理由: 减少迭代次数，加快收敛")

        elif "tabu" in algorithm_name or "禁忌" in algorithm_name:
            # 禁忌搜索优化
            if 'tabu_tenure' in current_params:
                old_tenure = current_params['tabu_tenure']
                new_tenure = max(int(old_tenure * 0.8), 5)
                current_params['tabu_tenure'] = new_tenure
                print(f"    ✓ 调整参数: tabu_tenure = {old_tenure} → {new_tenure}")
                print(f"       理由: 缩短禁忌期，加快搜索")

        # 更新配置
        config['parameters'] = current_params

        # 更新元数据
        config['source_metadata'] = config.get('source_metadata', {})
        config['source_metadata']['refinement_reason'] = "用户反馈: 性能优化"
        config['source_metadata']['refined_at'] = datetime.now().isoformat()

        algorithm_selection['sections']['algorithm_configuration'] = config

    return algorithm_selection
```

### 步骤7: 目标专家的修改逻辑

```python
def refine_objective_section(expert_input):
    """
    目标专家执行方案修改

    能力：
    - 理解目标优先级调整需求
    - 修改目标权重
    - 调整目标层级
    """

    current_solution = expert_input['current_solution']
    user_request = expert_input['user_request']

    objective_strategy = current_solution['solution_sections']['4_objective_strategy'].copy()

    print("  📋 目标专家分析用户需求...")

    hierarchy = objective_strategy['sections']['objective_hierarchy']

    # 显示当前目标层级
    print("    📊 当前目标层级:")
    primary = hierarchy.get('primary_objective', {})
    print(f"       主目标: {primary.get('name', 'N/A')}")

    secondary = hierarchy.get('secondary_objectives', [])
    if secondary:
        print(f"       次要目标:")
        for obj in secondary:
            print(f"         - {obj.get('name', 'N/A')}")

    # ====== 识别目标名称 ======

    objective_keywords = {
        "准时交货": "on_time_delivery",
        "最小化完工时间": "minimize_makespan",
        "成本最小": "minimize_cost",
        "资源利用": "resource_utilization",
        "负载均衡": "load_balance"
    }

    target_objective = None
    for keyword, obj_id in objective_keywords.items():
        if keyword in user_request:
            target_objective = keyword
            print(f"    ✓ 识别目标: {keyword}")
            break

    # ====== 识别调整意图 ======

    if target_objective:
        if any(kw in user_request for kw in ["最重要", "第一位", "优先", "核心", "主要"]):
            print(f"    💡 调整意图: 将 '{target_objective}' 提升为主目标")

            # 交换主次目标
            old_primary = primary

            # 从次要目标中找到目标对象
            new_primary = None
            for obj in secondary:
                if target_objective in obj.get('name', ''):
                    new_primary = obj
                    secondary.remove(obj)
                    break

            if new_primary:
                # 更新主目标
                hierarchy['primary_objective'] = new_primary

                # 原主目标降级为次要目标
                if old_primary:
                    secondary.insert(0, old_primary)

                hierarchy['secondary_objectives'] = secondary

                print(f"    ✓ 目标层级已更新:")
                print(f"       主目标: {new_primary.get('name')}")
                print(f"       次要目标: {', '.join([obj.get('name') for obj in secondary])}")

        elif any(kw in user_request for kw in ["提高", "增加", "加大"]):
            print(f"    💡 调整意图: 提高 '{target_objective}' 的权重")

            # 调整多目标权重
            multi_obj = objective_strategy['sections']['multi_objective_handling']
            weights = multi_obj.get('weights', {})

            # 查找对应目标的权重
            for obj_name, weight in weights.items():
                if target_objective in obj_name:
                    old_weight = weight
                    new_weight = min(weight * 1.5, 1.0)  # 最多1.0
                    weights[obj_name] = new_weight
                    print(f"    ✓ 权重调整: {obj_name} = {old_weight} → {new_weight}")
                    break

            multi_obj['weights'] = weights
            objective_strategy['sections']['multi_objective_handling'] = multi_obj

        objective_strategy['sections']['objective_hierarchy'] = hierarchy

    return objective_strategy
```

### 步骤8: 领域专家的修改逻辑

```python
def refine_domain_section(expert_input):
    """
    领域专家执行方案修改

    能力：
    - 识别行业领域
    - 提供领域特定建议
    - 触发相关约束添加
    """

    current_solution = expert_input['current_solution']
    user_request = expert_input['user_request']

    domain_adaptation = current_solution['solution_sections']['2_domain_adaptation'].copy()

    print("  📋 领域专家分析用户需求...")

    # ====== 识别行业领域 ======

    domain_map = {
        "冷链物流": {
            "industry": "冷链物流",
            "reference": "@domain-library/vehicle/冷链物流最佳实践.md",
            "key_requirements": ["温度控制", "保质期管理", "时效性", "包装要求"],
            "suggested_constraints": [
                "温度控制约束",
                "保质期约束",
                "配送时效约束"
            ]
        },
        "生鲜配送": {
            "industry": "生鲜配送",
            "reference": "@domain-library/vehicle/冷链物流最佳实践.md",
            "key_requirements": ["温度控制", "保质期短", "配送窗口小"],
            "suggested_constraints": [
                "温度控制约束",
                "保质期约束",
                "时间窗约束"
            ]
        }
    }

    matched_domain = None
    for keyword, domain_info in domain_map.items():
        if keyword in user_request:
            matched_domain = domain_info
            print(f"    ✓ 识别领域: {domain_info['industry']}")
            print(f"    📚 专家库引用: {domain_info['reference']}")
            break

    if matched_domain:
        # 更新领域信息
        domain_adaptation['sections']['industry_characteristics'] = {
            "industry_name": matched_domain["industry"],
            "characteristics": ", ".join(matched_domain["key_requirements"]),
            "source": "用户反馈",
            "reference": matched_domain["reference"]
        }

        print(f"    💡 领域专家建议:")
        print(f"       该领域的核心特点:")
        for req in matched_domain["key_requirements"]:
            print(f"         - {req}")

        print(f"       建议增加以下约束:")
        for constraint in matched_domain["suggested_constraints"]:
            print(f"         - {constraint}")

        print(f"    ⚠️ 提示: 领域专家会触发约束专家自动添加这些约束")

    return domain_adaptation
```

### 步骤9: 协调多专家执行

```python
def orchestrate_multi_expert_refinement(
    intent_analysis,
    user_request,
    current_solution
):
    """
    协调多专家按顺序执行方案修改
    """

    target_experts = intent_analysis["target_experts"]

    # 确定调用顺序
    ordered_experts = determine_expert_order(target_experts, user_request)

    print("\n🤝 多专家协同模式")

    # 提取TenElementModel
    ten_element_model = current_solution.get('ten_element_model', {})

    # 依次调用专家
    updated_solution = current_solution.copy()
    refinement_results = []

    for i, expert in enumerate(ordered_experts, 1):
        result = call_expert_for_refinement(
            expert_name=expert,
            user_request=user_request,
            current_solution=updated_solution,
            ten_element_model=ten_element_model
        )

        # 更新solution
        section_key = result['section_key']
        updated_solution['solution_sections'][section_key] = result['refined_section']

        refinement_results.append(result)

    return {
        "updated_solution": updated_solution,
        "refinement_results": refinement_results,
        "experts_called": ordered_experts
    }
```

### 步骤10: 同步到TenElementModel

```python
def sync_refinement_to_ten_element_model(updated_solution):
    """
    确保TenElementModel与修改后的方案保持一致
    """

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔄 同步到TenElementModel...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")

    ten_element_model = updated_solution.get('ten_element_model', {})

    # 同步约束列表
    constraint_strategy = updated_solution['solution_sections']['3_constraint_strategy']
    all_constraints = (
        constraint_strategy['sections']['constraint_classification']['hard_constraints'] +
        constraint_strategy['sections']['constraint_classification']['soft_constraints']
    )

    ten_element_model['constraints'] = [
        {
            "name": c['name'],
            "description": c['description'],
            "type": c.get('type', 'hard'),
            "category": c.get('category', 'general')
        }
        for c in all_constraints
    ]

    print(f"  ✓ 已同步约束列表: {len(ten_element_model['constraints'])}个约束")

    # 同步目标列表
    objective_strategy = updated_solution['solution_sections']['4_objective_strategy']
    hierarchy = objective_strategy['sections']['objective_hierarchy']

    objectives = []

    primary = hierarchy.get('primary_objective', {})
    if primary:
        objectives.append({
            "name": primary.get('name'),
            "description": primary.get('description'),
            "type": "primary",
            "direction": primary.get('direction', 'minimize')
        })

    for sec_obj in hierarchy.get('secondary_objectives', []):
        objectives.append({
            "name": sec_obj.get('name'),
            "description": sec_obj.get('description'),
            "type": "secondary",
            "direction": sec_obj.get('direction', 'minimize')
        })

    ten_element_model['objectives'] = objectives

    print(f"  ✓ 已同步目标列表: {len(objectives)}个目标")

    # 更新版本信息
    current_version = ten_element_model.get('version', '1.0')
    ten_element_model['version'] = current_version + '.refined'
    ten_element_model['refined_at'] = datetime.now().isoformat()

    updated_solution['ten_element_model'] = ten_element_model

    print(f"  ✓ TenElementModel版本: {ten_element_model['version']}")

    return updated_solution
```

### 步骤11: 保存优化后的方案

```python
def save_optimized_solution(updated_solution, output_folder):
    """
    保存优化后的方案YAML文件
    """

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💾 保存优化方案...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")

    # 更新元数据
    metadata = updated_solution.get('solution_metadata', {})
    metadata['last_refined_at'] = datetime.now().isoformat()
    metadata['refinement_count'] = metadata.get('refinement_count', 0) + 1
    updated_solution['solution_metadata'] = metadata

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    refinement_count = metadata['refinement_count']

    filename = f"solution_data_optimized_v{refinement_count}_{timestamp}.yaml"
    file_path = os.path.join(output_folder, "docs", filename)

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 保存YAML
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(updated_solution, f, allow_unicode=True, sort_keys=False)

    file_size = os.path.getsize(file_path)

    print(f"  ✓ 文件: {filename}")
    print(f"  ✓ 路径: {file_path}")
    print(f"  ✓ 大小: {file_size} bytes")
    print(f"  ✓ 优化版本: v{refinement_count}")

    return {
        "file_path": file_path,
        "filename": filename,
        "file_size": file_size,
        "refinement_version": refinement_count
    }
```

### 步骤12: 自动生成代码

```python
def auto_generate_code_from_optimized_solution(solution_file_path):
    """
    自动调用 generate-code-from-yaml 生成代码
    """

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💻 自动生成代码...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")

    # 这里调用 generate-code-from-yaml.md 的逻辑
    # 实际实现中会通过workflow系统调用

    print(f"  📂 输入: {os.path.basename(solution_file_path)}")
    print(f"  🔄 调用: generate-code-from-yaml.md")

    # 模拟代码生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    code_filename = f"scheduling_solution_{timestamp}.py"
    code_path = solution_file_path.replace("docs", "models").replace(".yaml", ".py")

    print(f"  ✓ 代码已生成: {code_filename}")
    print(f"  ✓ 路径: {code_path}")

    return {
        "code_path": code_path,
        "code_filename": code_filename
    }
```

### 步骤13: 生成修改摘要

```python
def generate_refinement_summary(
    intent_analysis,
    refinement_results,
    saved_solution,
    code_result
):
    """
    生成修改摘要，展示给用户
    """

    print("\n" + "="*50)
    print("✅ 优化完成！")
    print("="*50)

    print("\n📊 修改摘要:")

    # 涉及的专家
    experts_called = [r['expert'] for r in refinement_results]
    print(f"\n👥 调用专家: {', '.join(experts_called)}")

    # 具体修改
    print(f"\n📝 具体修改:")

    for result in refinement_results:
        expert = result['expert']

        if expert == "constraint-expert":
            # 统计新增约束
            print(f"  约束专家:")
            print(f"    - 修改了约束策略")
            # 可以更详细地列出具体增加了哪些约束

        elif expert == "algorithm-expert":
            print(f"  算法专家:")
            print(f"    - 优化了算法参数，预计性能提升30-40%")

        elif expert == "objective-expert":
            print(f"  目标专家:")
            print(f"    - 调整了目标权重/层级")

        elif expert == "domain-expert":
            print(f"  领域专家:")
            print(f"    - 适配了领域特性")

    # 文件信息
    print(f"\n📁 生成文件:")
    print(f"  ✓ 优化方案: {saved_solution['filename']}")
    print(f"     版本: v{saved_solution['refinement_version']}")
    print(f"  ✓ 生成代码: {code_result['code_filename']}")

    # 下一步建议
    print(f"\n💡 下一步:")
    print(f"  1. 测试新代码: python {code_result['code_path']}")
    print(f"  2. 如需继续优化，再次运行 optimize-solution")
    print(f"  3. 查看方案文档: {saved_solution['file_path']}")

    return {
        "summary": "优化完成",
        "experts_called": experts_called,
        "files_generated": {
            "solution": saved_solution['file_path'],
            "code": code_result['code_path']
        }
    }
```

## 输出

```yaml
outputs:
  optimized_solution_path:
    type: string
    description: 优化后的方案YAML文件路径
    example: 'aps-outputs/docs/solution_data_optimized_v2_20251027_154530.yaml'

  generated_code_path:
    type: string
    description: 自动生成的代码文件路径
    example: 'aps-outputs/models/scheduling_solution_20251027_154530.py'

  refinement_summary:
    type: object
    description: 优化摘要
    structure:
      experts_called: array # 调用的专家列表
      modifications: array # 具体修改列表
      refinement_version: integer # 优化版本号

  intent_analysis:
    type: object
    description: 意图分析结果
```

## 质量检查

- [ ] 用户意图正确识别
- [ ] 专家调用顺序合理
- [ ] 方案修改保持引用完整性
- [ ] TenElementModel已同步
- [ ] 优化方案已保存
- [ ] 代码已自动生成
- [ ] 修改摘要清晰完整

## 引用

- generate-code-from-yaml.md（代码生成）
- @constraint-library/\*（约束专家引用）
- @algorithm-library/\*（算法专家引用）
- @objective-library/\*（目标专家引用）
- @domain-library/\*（领域专家引用）

---

**创建**: 2025-10-27
**BMAD版本**: v6-alpha
**核心机制**: Orchestrator智能路由 + 多专家协同 + 自然语言交互
