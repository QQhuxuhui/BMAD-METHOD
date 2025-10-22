# Task: Analyze User Request

**任务ID**: `analyze-user-request`
**版本**: V4.3
**用途**: Phase 0.1 - 初步理解用户需求，识别问题域和关键要求

## 输入

```yaml
inputs:
  - user_request: 用户的原始调度需求描述
```

## 处理逻辑

### 步骤1: 识别问题领域

```python
def identify_problem_domain(user_request):
    """
    识别调度问题所属的领域
    """
    # 领域关键词映射
    domain_keywords = {
        "vehicle_routing": ["配送", "车辆", "路径", "routing", "delivery", "运输"],
        "production_scheduling": ["生产", "车间", "工序", "production", "manufacturing", "作业"],
        "project_scheduling": ["项目", "任务", "资源", "project", "task", "milestone"],
        "workforce_scheduling": ["排班", "人员", "班次", "shift", "staff", "workforce"],
        "service_scheduling": ["服务", "预约", "时段", "appointment", "service"],
        "supply_chain": ["供应链", "库存", "采购", "supply", "inventory", "procurement"]
    }

    detected_domains = []
    request_lower = user_request.lower()

    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in request_lower:
                detected_domains.append(domain)
                break

    return {
        "primary_domain": detected_domains[0] if detected_domains else "generic",
        "all_domains": detected_domains,
        "confidence": 0.8 if detected_domains else 0.3
    }
```

### 步骤2: 提取关键需求

```python
def extract_key_requirements(user_request):
    """
    从用户描述中提取关键需求要素
    """
    requirements = {
        "entities": [],      # 实体：车辆、订单、工序等
        "constraints": [],   # 明确提到的约束
        "objectives": [],    # 优化目标
        "scale": {},         # 问题规模
        "time_horizon": {},  # 时间范围
        "special_needs": []  # 特殊需求
    }

    # 实体识别
    entity_patterns = {
        "vehicles": r"(\d+).*[车辆|trucks|vehicles]",
        "orders": r"(\d+).*[订单|orders|客户|customers]",
        "machines": r"(\d+).*[机器|设备|machines]",
        "workers": r"(\d+).*[人员|工人|workers]"
    }

    for entity_type, pattern in entity_patterns.items():
        matches = re.findall(pattern, user_request, re.IGNORECASE)
        if matches:
            requirements["entities"].append({
                "type": entity_type,
                "count": int(matches[0])
            })

    # 约束识别
    constraint_keywords = ["时间窗", "容量", "优先级", "依赖", "time window", "capacity", "precedence"]
    for keyword in constraint_keywords:
        if keyword.lower() in user_request.lower():
            requirements["constraints"].append(keyword)

    # 目标识别
    objective_keywords = {
        "minimize_cost": ["成本最小", "降低成本", "minimize cost", "reduce cost"],
        "minimize_time": ["时间最短", "最快", "minimize time", "shortest"],
        "maximize_efficiency": ["效率最高", "最大化利用", "maximize efficiency"]
    }

    for obj_type, keywords in objective_keywords.items():
        for keyword in keywords:
            if keyword.lower() in user_request.lower():
                requirements["objectives"].append(obj_type)
                break

    return requirements
```

### 步骤3: 评估问题复杂度

```python
def assess_complexity(key_requirements, problem_domain):
    """
    评估问题复杂度（Level 1-4）
    """
    complexity_score = 0

    # 规模因素
    total_entities = sum(e["count"] for e in key_requirements["entities"])
    if total_entities > 1000:
        complexity_score += 3
    elif total_entities > 100:
        complexity_score += 2
    elif total_entities > 10:
        complexity_score += 1

    # 约束数量
    constraint_count = len(key_requirements["constraints"])
    if constraint_count > 5:
        complexity_score += 2
    elif constraint_count > 2:
        complexity_score += 1

    # 多目标
    if len(key_requirements["objectives"]) > 1:
        complexity_score += 1

    # 特殊需求
    if key_requirements["special_needs"]:
        complexity_score += 1

    # 映射到复杂度级别
    if complexity_score >= 7:
        level = 4
        description = "非常复杂：大规模、多约束、多目标"
    elif complexity_score >= 5:
        level = 3
        description = "复杂：中大规模、多约束或多目标"
    elif complexity_score >= 3:
        level = 2
        description = "中等：中等规模、标准约束"
    else:
        level = 1
        description = "简单：小规模、基本约束"

    return {
        "level": level,
        "score": complexity_score,
        "description": description
    }
```

### 步骤4: 生成初步理解报告

```python
def generate_initial_understanding(user_request, domain, requirements, complexity):
    """
    生成结构化的初步理解报告
    """
    understanding = {
        "problem_domain": domain,
        "key_requirements": requirements,
        "complexity_assessment": complexity,
        "estimated_phases": [],
        "recommended_experts": [],
        "potential_challenges": [],
        "confidence": 0.0
    }

    # 估算需要的Phase
    if complexity["level"] >= 3:
        understanding["estimated_phases"] = ["0", "0.5", "1", "1.5", "2", "3", "4"]
    else:
        understanding["estimated_phases"] = ["0", "1", "1.5", "2", "3", "4"]

    # 推荐需要调用的专家
    understanding["recommended_experts"] = ["domain-expert", "constraint-expert", "objective-expert", "algorithm-expert"]

    if complexity["level"] >= 3:
        understanding["recommended_experts"].append("extension-guide")

    # 识别潜在挑战
    if len(requirements["constraints"]) > 5:
        understanding["potential_challenges"].append("复杂约束组合，需要仔细建模")

    if len(requirements["objectives"]) > 1:
        understanding["potential_challenges"].append("多目标优化，需要权衡策略")

    if complexity["level"] == 4:
        understanding["potential_challenges"].append("大规模问题，需要高效算法")

    # 置信度评估
    confidence_factors = [
        domain["confidence"],
        0.8 if requirements["entities"] else 0.3,
        0.7 if requirements["objectives"] else 0.4
    ]
    understanding["confidence"] = sum(confidence_factors) / len(confidence_factors)

    return understanding
```

## 输出

```yaml
outputs:
  initial_understanding:
    type: object
    structure:
      problem_domain:
        primary_domain: string
        all_domains: array
        confidence: float
      key_requirements:
        entities: array
        constraints: array
        objectives: array
        scale: object
        time_horizon: object
        special_needs: array
      complexity_assessment:
        level: integer (1-4)
        score: integer
        description: string
      estimated_phases: array
      recommended_experts: array
      potential_challenges: array
      confidence: float

  clarification_needed:
    type: boolean
    description: '是否需要进一步澄清'

  suggested_questions:
    type: array
    description: '如需澄清，建议的问题列表'
```

## 示例输出

```json
{
  "initial_understanding": {
    "problem_domain": {
      "primary_domain": "vehicle_routing",
      "all_domains": ["vehicle_routing", "service_scheduling"],
      "confidence": 0.85
    },
    "key_requirements": {
      "entities": [
        { "type": "vehicles", "count": 50 },
        { "type": "orders", "count": 200 }
      ],
      "constraints": ["时间窗", "容量", "优先级"],
      "objectives": ["minimize_cost", "minimize_time"],
      "scale": { "medium": true },
      "time_horizon": { "daily": true },
      "special_needs": []
    },
    "complexity_assessment": {
      "level": 3,
      "score": 6,
      "description": "复杂：中大规模、多约束或多目标"
    },
    "estimated_phases": ["0", "0.5", "1", "1.5", "2", "3", "4"],
    "recommended_experts": ["domain-expert", "constraint-expert", "objective-expert", "algorithm-expert"],
    "potential_challenges": ["多目标优化，需要权衡策略", "复杂约束组合，需要仔细建模"],
    "confidence": 0.75
  },
  "clarification_needed": false,
  "suggested_questions": []
}
```

## 质量检查

- [ ] 问题领域识别准确
- [ ] 关键需求要素完整
- [ ] 复杂度评估合理
- [ ] 推荐专家符合问题特征
- [ ] 潜在挑战识别到位

## 引用

- @编排协调专家库/需求分析方法论
- @领域专家库/领域识别模式
- V4.3架构规范: Phase 0 需求理解

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 快速需求理解，为后续Phase提供基础
