# Task: Analyze Requirements Deep

**任务ID**: `analyze-requirements-deep`
**版本**: V4.3
**用途**: Phase 1 Step 1.1 - 需求深度理解，基于Phase 0的初步分析进行深入分析

## 输入

```yaml
inputs:
  - user_request: 用户的原始调度需求描述
  - confirmed_todo_list: 用户确认的任务清单（从Phase 0状态加载）
```

## 🚨 强制要求（MANDATORY）

### 1. 必须基于Phase 0的基础

本任务是Phase 1的深度分析，必须基于Phase 0的初步分析结果：

- ✓ 对照 `confirmed_todo_list` 进行分析
- ✓ 深化Phase 0识别的问题域
- ✓ 扩展Phase 0提取的关键需求

### 2. 生成澄清问题

如果需求不明确（confidence < 0.70），必须生成澄清问题，触发Step 1.2用户澄清。

## 处理逻辑

### 步骤1: 回顾Phase 0分析结果

```python
def review_phase_0_baseline(confirmed_todo_list):
    """
    回顾Phase 0的分析基线

    Args:
        confirmed_todo_list: Phase 0确认的任务清单

    Returns:
        dict: Phase 0基线总结
    """
    baseline_summary = {
        "phase_0_tasks": [],
        "identified_phases": [],
        "initial_scope": ""
    }

    # 提取Phase 0识别的任务
    for phase_group in confirmed_todo_list:
        phase_name = phase_group.get("phase", "")
        tasks = phase_group.get("tasks", [])

        baseline_summary["phase_0_tasks"].extend(tasks)
        baseline_summary["identified_phases"].append(phase_name)

    print(f"✓ Phase 0基线已加载: {len(baseline_summary['phase_0_tasks'])}个任务")
    print(f"✓ 识别的Phase: {baseline_summary['identified_phases']}")

    return baseline_summary
```

### 步骤2: 深度需求分析

#### 2.1 调度问题类型识别

```python
def identify_scheduling_problem_type(user_request):
    """
    识别具体的调度问题类型

    Returns:
        dict: 问题类型分析
    """
    problem_types = {
        "job_shop": {
            "keywords": ["作业车间", "工序", "机器", "job shop", "operation"],
            "characteristics": ["多个工序", "机器顺序", "加工时间"]
        },
        "flow_shop": {
            "keywords": ["流水车间", "flow shop", "生产线"],
            "characteristics": ["固定顺序", "流水线", "连续加工"]
        },
        "vrp": {
            "keywords": ["车辆路径", "配送", "routing", "delivery"],
            "characteristics": ["车辆容量", "客户位置", "时间窗"]
        },
        "rcpsp": {
            "keywords": ["资源约束", "项目调度", "RCPSP", "project"],
            "characteristics": ["资源限制", "任务依赖", "项目工期"]
        },
        "workforce": {
            "keywords": ["排班", "人员", "班次", "shift"],
            "characteristics": ["员工技能", "工作时长", "班次覆盖"]
        },
        "appointment": {
            "keywords": ["预约", "时段", "appointment", "booking"],
            "characteristics": ["时间槽", "资源可用", "客户偏好"]
        }
    }

    detected_type = None
    max_match_count = 0

    request_lower = user_request.lower()

    for ptype, info in problem_types.items():
        match_count = sum(1 for kw in info["keywords"] if kw in request_lower)
        if match_count > max_match_count:
            max_match_count = match_count
            detected_type = ptype

    if detected_type:
        result = {
            "problem_type": detected_type,
            "characteristics": problem_types[detected_type]["characteristics"],
            "confidence": min(0.9, 0.5 + max_match_count * 0.1)
        }
    else:
        result = {
            "problem_type": "generic_scheduling",
            "characteristics": ["需要进一步澄清"],
            "confidence": 0.3
        }

    print(f"✓ 问题类型: {result['problem_type']} (置信度: {result['confidence']})")
    return result
```

#### 2.2 决策变量候选识别

```python
def identify_decision_variable_candidates(user_request, problem_type):
    """
    识别潜在的决策变量

    Returns:
        list: 决策变量候选列表
    """
    candidates = []

    # 基于问题类型推断决策变量
    type_to_variables = {
        "job_shop": ["工序-机器分配", "工序开始时间", "工序顺序"],
        "flow_shop": ["作业顺序", "作业开始时间"],
        "vrp": ["车辆-客户分配", "访问顺序", "路径"],
        "rcpsp": ["任务开始时间", "资源分配"],
        "workforce": ["员工-班次分配", "班次时间"],
        "appointment": ["客户-时段分配"]
    }

    ptype = problem_type.get("problem_type", "generic_scheduling")
    candidates = type_to_variables.get(ptype, ["需要根据需求确定"])

    print(f"✓ 决策变量候选: {len(candidates)}个")
    return candidates
```

#### 2.3 约束候选识别

```python
def identify_constraint_candidates(user_request):
    """
    识别需求中提到的约束

    Returns:
        list: 约束候选列表
    """
    constraint_patterns = {
        "precedence": ["先后", "之前", "之后", "前置", "依赖", "precedence"],
        "capacity": ["容量", "能力", "上限", "capacity", "limit"],
        "time_window": ["时间窗", "截止", "最早", "最晚", "time window", "deadline"],
        "resource": ["资源", "设备", "人员", "resource", "equipment"],
        "skill": ["技能", "资质", "能力", "skill", "qualification"],
        "exclusion": ["互斥", "不能同时", "冲突", "exclusive"],
        "setup": ["准备时间", "切换", "setup", "changeover"]
    }

    detected_constraints = []
    request_lower = user_request.lower()

    for constraint_type, keywords in constraint_patterns.items():
        for keyword in keywords:
            if keyword in request_lower:
                detected_constraints.append({
                    "type": constraint_type,
                    "keyword_found": keyword,
                    "description": f"检测到{constraint_type}约束"
                })
                break

    print(f"✓ 约束候选: {len(detected_constraints)}个")
    return detected_constraints
```

#### 2.4 优化目标识别

```python
def identify_optimization_objectives(user_request):
    """
    识别优化目标

    Returns:
        list: 目标候选列表
    """
    objective_patterns = {
        "makespan": ["最短时间", "最小完工时间", "makespan", "completion time"],
        "cost": ["成本", "费用", "开销", "cost", "expense"],
        "tardiness": ["延误", "拖期", "tardiness", "lateness"],
        "utilization": ["利用率", "使用率", "utilization"],
        "distance": ["距离", "路程", "distance", "travel"],
        "satisfaction": ["满意度", "服务质量", "satisfaction", "quality"]
    }

    detected_objectives = []
    request_lower = user_request.lower()

    for obj_type, keywords in objective_patterns.items():
        for keyword in keywords:
            if keyword in request_lower:
                # 判断是最大化还是最小化
                if any(word in request_lower for word in ["最小", "最短", "minimize", "reduce"]):
                    direction = "minimize"
                elif any(word in request_lower for word in ["最大", "maximize", "increase"]):
                    direction = "maximize"
                else:
                    direction = "unknown"

                detected_objectives.append({
                    "type": obj_type,
                    "direction": direction,
                    "keyword_found": keyword
                })
                break

    print(f"✓ 优化目标候选: {len(detected_objectives)}个")
    return detected_objectives
```

### 步骤3: 生成需求分析报告

```python
from datetime import datetime

def generate_requirement_analysis(
    user_request,
    confirmed_todo_list,
    problem_type,
    decision_variables,
    constraints,
    objectives
):
    """
    生成完整的需求分析报告

    Returns:
        dict: 需求分析报告
    """
    requirement_analysis = {
        "metadata": {
            "analyzed_at": datetime.now().isoformat(),
            "phase": "Phase 1",
            "version": "4.3"
        },

        "problem_understanding": {
            "problem_type": problem_type["problem_type"],
            "confidence": problem_type["confidence"],
            "characteristics": problem_type["characteristics"]
        },

        "ten_element_candidates": {
            "decision_variables": decision_variables,
            "constraints": constraints,
            "objectives": objectives
        },

        "scope_analysis": {
            "entities_identified": True if decision_variables else False,
            "constraints_identified": len(constraints) > 0,
            "objectives_identified": len(objectives) > 0
        },

        "alignment_with_todo": {
            "todo_list": confirmed_todo_list,
            "coverage": "待在Step 1.3进行偏离检测"
        },

        "completeness": {
            "information_sufficient": problem_type["confidence"] >= 0.70,
            "needs_clarification": problem_type["confidence"] < 0.70
        }
    }

    print("✓ 需求分析报告已生成")
    return requirement_analysis
```

### 步骤4: 生成澄清问题（如需要）

```python
def generate_clarification_questions(requirement_analysis, user_request):
    """
    如果需求不够清晰，生成澄清问题

    Returns:
        list: 澄清问题列表
    """
    clarification_questions = []

    confidence = requirement_analysis["problem_understanding"]["confidence"]

    # 如果置信度低，生成澄清问题
    if confidence < 0.70:
        clarification_questions.append({
            "priority": "high",
            "question": "请明确您的调度问题类型",
            "reason": f"当前置信度较低({confidence})",
            "options": ["作业车间调度", "车辆路径问题", "项目调度", "排班问题", "其他"]
        })

    # 检查决策变量是否明确
    if not requirement_analysis["ten_element_candidates"]["decision_variables"]:
        clarification_questions.append({
            "priority": "high",
            "question": "请描述需要决策的对象",
            "reason": "未能识别明确的决策变量",
            "examples": ["需要决定哪些工序在哪些机器上加工？", "需要决定车辆的配送路线？"]
        })

    # 检查约束是否明确
    if len(requirement_analysis["ten_element_candidates"]["constraints"]) == 0:
        clarification_questions.append({
            "priority": "medium",
            "question": "是否有特定的约束条件？",
            "reason": "未能识别明确的约束",
            "examples": ["时间限制", "容量限制", "先后关系", "资源限制"]
        })

    # 检查目标是否明确
    if len(requirement_analysis["ten_element_candidates"]["objectives"]) == 0:
        clarification_questions.append({
            "priority": "high",
            "question": "您希望优化什么？",
            "reason": "未能识别明确的优化目标",
            "examples": ["最小化完工时间", "最小化成本", "最大化利用率"]
        })

    if clarification_questions:
        print(f"✓ 生成澄清问题: {len(clarification_questions)}个")
    else:
        print("✓ 需求清晰，无需澄清")

    return clarification_questions
```

## 输出

```yaml
outputs:
  requirement_analysis:
    type: object
    description: 需求分析报告
    structure:
      metadata: 元数据
      problem_understanding: 问题理解
      ten_element_candidates: 十要素候选
      scope_analysis: 范围分析
      alignment_with_todo: 与Todo List对齐情况
      completeness: 完整性评估

  clarification_questions:
    type: array
    description: 澄清问题列表（如需要）
    structure:
      - priority: string (high/medium/low)
        question: string
        reason: string
        options/examples: array
```

## 质量检查

- [ ] 问题类型已识别（confidence >= 0.70为佳）
- [ ] 决策变量候选已识别
- [ ] 约束候选已识别
- [ ] 优化目标已识别
- [ ] 与Phase 0 Todo List对齐
- [ ] 如confidence < 0.70，已生成澄清问题
- [ ] 分析报告完整

## 与Phase 0的区别

| 维度 | Phase 0 (初步分析)    | Phase 1 (深度理解)   |
| ---- | --------------------- | -------------------- |
| 目的 | 快速理解，生成Todo    | 深入分析，准备建模   |
| 深度 | ⭐⭐                  | ⭐⭐⭐⭐⭐           |
| 输出 | initial_understanding | requirement_analysis |
| 后续 | 生成Todo List         | 生成TenElementModel  |

## 引用

- @编排协调专家库/需求分析方法
- @领域专家库/问题类型识别
- Phase 0分析结果（confirmed_todo_list）

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 基于Phase 0深化分析，为十要素建模做准备
