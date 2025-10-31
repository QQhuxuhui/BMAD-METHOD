# P1: 知识库成熟度模型

**优先级**: 🟡 P1 - 30天内完成
**预计工期**: 4周
**负责模块**: 专家知识库
**影响范围**: Phase 2 专家协调

---

## 📋 问题描述

### 现状分析

**知识库覆盖度不足**:

```
当前状态（估算）:
  algorithm-library/     覆盖度: ~30%  (3/10算法有完整模板)
  constraint-library/    覆盖度: ~40%  (4/10约束类型有文档)
  objective-library/     覆盖度: ~20%  (2/10目标类型有文档)
  domain-library/        覆盖度: ~25%  (1/4领域有适配器)

问题影响:
  ❌ 专家推荐依赖大模型幻觉
  ❌ 推荐质量不稳定（置信度波动大）
  ❌ 缺少可复现性
  ❌ 无法量化产品能力
```

### 根本原因

1. **缺少知识库完整性指标体系**
   - 没有明确的覆盖度目标
   - 没有质量评估标准
   - 没有填充优先级

2. **缺少知识库自动扩展机制**
   - 虽然有"算法扩展指导专家"，但流程未自动化
   - 用户代码和反馈未闭环到知识库
   - 无法随使用量增长

3. **缺少知识库版本管理**
   - 知识模块更新无版本追踪
   - 不同版本间的兼容性未知
   - 无法回滚或对比

---

## 🎯 解决方案

### 总体架构

```
┌──────────────────────────────────────────────────────┐
│  知识库成熟度管理系统                                 │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │ 指标体系     │  │ 自动扩展     │  │ 版本管理   ││
│  │ - 覆盖度     │  │ - 代码提取   │  │ - Git版本  ││
│  │ - 质量评分   │  │ - 知识生成   │  │ - 变更日志 ││
│  │ - 使用率     │  │ - 入库审核   │  │ - 兼容性   ││
│  └──────────────┘  └──────────────┘  └────────────┘│
│                                                       │
│  ┌─────────────────────────────────────────────────┐│
│  │ 知识库仪表板                                    ││
│  │ - 实时覆盖度                                    ││
│  │ - 填充进度                                      ││
│  │ - 质量趋势                                      ││
│  │ - 使用热力图                                    ││
│  └─────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

---

## 🛠️ 实施步骤

### Phase 1: 建立指标体系（Week 1）

#### 1.1 定义覆盖度指标

**新建文件**: `bmad/aps/knowledge-library-manifest.yaml`

```yaml
# 知识库成熟度清单
version: '1.0'
last_updated: '2025-10-31'

# ============ 算法库 ============
algorithm_library:
  target_coverage: 0.80 # 目标覆盖80%主流算法

  categories:
    exact_algorithms:
      target: 10
      current: 3
      coverage: 0.30
      priority_list:
        - name: 'branch_and_bound'
          status: 'missing'
          priority: 'high'
          estimated_effort: '3天'

        - name: 'dynamic_programming'
          status: 'missing'
          priority: 'medium'
          estimated_effort: '2天'

        - name: 'integer_programming'
          status: 'partial'
          priority: 'high'
          estimated_effort: '1天'
          completion: 0.60

    meta_heuristic_algorithms:
      target: 10
      current: 4
      coverage: 0.40
      priority_list:
        - name: 'genetic_algorithm'
          status: 'complete'
          quality_score: 0.95
          last_updated: '2025-10-20'
          file: 'algorithm-library/meta-heuristic/genetic-algorithm.md'

        - name: 'tabu_search'
          status: 'missing'
          priority: 'high'
          estimated_effort: '2天'

        - name: 'simulated_annealing'
          status: 'missing'
          priority: 'high'
          estimated_effort: '2天'

        - name: 'particle_swarm_optimization'
          status: 'missing'
          priority: 'medium'
          estimated_effort: '3天'

  quality_requirements:
    - has_pseudocode: true
    - has_complexity_analysis: true
    - has_parameter_guide: true
    - has_code_template: true
    - has_example: true
    - quality_score_min: 0.80

# ============ 约束库 ============
constraint_library:
  target_coverage: 0.90 # 约束类型相对固定，目标90%

  categories:
    temporal_constraints:
      target: 5
      current: 3
      coverage: 0.60
      priority_list:
        - name: 'precedence_constraint'
          status: 'complete'
          quality_score: 0.95
          file: 'constraint-library/temporal/precedence-constraint.md'

        - name: 'time_window_constraint'
          status: 'complete'
          quality_score: 0.90

        - name: 'disjunctive_constraint'
          status: 'complete'
          quality_score: 0.92

        - name: 'synchronization_constraint'
          status: 'missing'
          priority: 'medium'
          estimated_effort: '1天'

        - name: 'deadline_constraint'
          status: 'missing'
          priority: 'low'
          estimated_effort: '1天'

    resource_constraints:
      target: 6
      current: 2
      coverage: 0.33
      priority_list:
        - name: 'resource_capacity_constraint'
          status: 'complete'
          quality_score: 0.88

        - name: 'resource_assignment_constraint'
          status: 'complete'
          quality_score: 0.90

        - name: 'cumulative_constraint'
          status: 'missing'
          priority: 'high'
          estimated_effort: '2天'

        - name: 'renewable_resource_constraint'
          status: 'missing'
          priority: 'medium'
          estimated_effort: '2天'

# ============ 目标库 ============
objective_library:
  target_coverage: 0.70 # 目标类型多样化，目标70%

  categories:
    time_based:
      target: 6
      current: 3
      coverage: 0.50
      priority_list:
        - name: 'makespan_minimization'
          status: 'complete'
          quality_score: 0.85
          file: 'objective-library/time/makespan-minimization.md'

        - name: 'tardiness_minimization'
          status: 'missing'
          priority: 'high'
          estimated_effort: '1天'

        - name: 'flow_time_minimization'
          status: 'missing'
          priority: 'medium'
          estimated_effort: '1天'

    cost_based:
      target: 6
      current: 2
      coverage: 0.33
      priority_list:
        - name: 'total_cost_minimization'
          status: 'partial'
          completion: 0.70
          priority: 'high'

        - name: 'setup_cost_minimization'
          status: 'complete'
          quality_score: 0.80

# ============ 领域库 ============
domain_library:
  target_coverage: 0.75 # 4个主要领域

  categories:
    manufacturing:
      status: 'partial'
      completion: 0.60
      priority: 'high'
      estimated_effort: '5天'

    logistics:
      status: 'missing'
      priority: 'high'
      estimated_effort: '7天'

    service:
      status: 'missing'
      priority: 'medium'
      estimated_effort: '5天'

    project:
      status: 'missing'
      priority: 'low'
      estimated_effort: '5天'

# ============ 总体指标 ============
overall_metrics:
  total_modules: 47
  completed_modules: 14
  overall_coverage: 0.30
  target_coverage: 0.70

  quality_distribution:
    excellent: 5 # quality_score >= 0.90
    good: 6 # quality_score >= 0.80
    acceptable: 3 # quality_score >= 0.70
    poor: 0 # quality_score < 0.70

  filling_progress:
    week_1: 0.30
    week_2_target: 0.40
    week_3_target: 0.50
    week_4_target: 0.60
    month_2_target: 0.70
```

#### 1.2 建立质量评估标准

**新建文件**: `bmad/aps/tasks/evaluate-knowledge-quality.md`

````markdown
# Task: Evaluate Knowledge Quality

**任务ID**: `evaluate-knowledge-quality`
**用途**: 评估知识模块的质量

## 质量评分标准

```python
def calculate_quality_score(knowledge_module):
    """
    计算知识模块的质量评分（0-1）

    评分维度:
    1. 完整性 (40%)
    2. 准确性 (30%)
    3. 可用性 (20%)
    4. 可维护性 (10%)
    """
    scores = {
        "completeness": 0.0,
        "accuracy": 0.0,
        "usability": 0.0,
        "maintainability": 0.0
    }

    # 1. 完整性评估
    required_sections = [
        "module_name", "category", "description",
        "when_to_use", "pseudocode", "complexity",
        "parameters", "examples", "citations"
    ]
    present_sections = [s for s in required_sections if s in knowledge_module]
    scores["completeness"] = len(present_sections) / len(required_sections)

    # 2. 准确性评估（人工审核标记）
    if "accuracy_review" in knowledge_module:
        scores["accuracy"] = knowledge_module["accuracy_review"]["score"]
    else:
        scores["accuracy"] = 0.5  # 默认中等

    # 3. 可用性评估
    usability_checks = {
        "has_code_template": bool(knowledge_module.get("code_template")),
        "has_example": bool(knowledge_module.get("examples")),
        "has_parameter_guide": bool(knowledge_module.get("parameter_guide")),
        "clear_when_to_use": len(knowledge_module.get("when_to_use", "")) > 50
    }
    scores["usability"] = sum(usability_checks.values()) / len(usability_checks)

    # 4. 可维护性评估
    maintainability_checks = {
        "has_version": bool(knowledge_module.get("version")),
        "has_last_updated": bool(knowledge_module.get("updated")),
        "has_citations": bool(knowledge_module.get("citations")),
        "well_structured": True  # 简化假设
    }
    scores["maintainability"] = sum(maintainability_checks.values()) / len(maintainability_checks)

    # 加权总分
    weights = {
        "completeness": 0.40,
        "accuracy": 0.30,
        "usability": 0.20,
        "maintainability": 0.10
    }

    total_score = sum(scores[k] * weights[k] for k in scores)

    return {
        "total_score": total_score,
        "dimension_scores": scores,
        "grade": get_grade(total_score)
    }

def get_grade(score):
    if score >= 0.90:
        return "excellent"
    elif score >= 0.80:
        return "good"
    elif score >= 0.70:
        return "acceptable"
    else:
        return "poor"
```
````

## 输出

- quality_report: 质量评估报告
- improvement_suggestions: 改进建议

````

---

### Phase 2: 知识填充计划（Week 2-4）

#### 2.1 高优先级知识模块填充

**Week 2目标**: 覆盖度 30% → 40%

```yaml
week_2_tasks:
  - module: "tabu_search"
    type: "algorithm"
    priority: "high"
    estimated_effort: "2天"
    assignee: "算法专家"
    deliverables:
      - "algorithm-library/meta-heuristic/tabu-search.md"
      - "伪代码 + 复杂度分析 + 参数指南"

  - module: "simulated_annealing"
    type: "algorithm"
    priority: "high"
    estimated_effort: "2天"
    deliverables:
      - "algorithm-library/meta-heuristic/simulated-annealing.md"

  - module: "cumulative_constraint"
    type: "constraint"
    priority: "high"
    estimated_effort: "2天"
    deliverables:
      - "constraint-library/resource/cumulative-constraint.md"
````

**Week 3目标**: 覆盖度 40% → 50%

**Week 4目标**: 覆盖度 50% → 60%

#### 2.2 知识模块标准模板

**文件**: `bmad/aps/templates/knowledge-module-template.md`

```markdown
<!-- Powered by BMAD-CORE™ -->
<!-- Module ID: bmad/aps/{library-type}/{category}/{module-name}.md -->
<!-- Aliases: @专家库/{library-type}/{category}/{module-name}.md -->

---

module_name: {模块名称}
category: {分类}
version: v1.0.0
updated: {更新日期}
quality_score: {质量评分}
keywords: ['{关键词1}', '{关键词2}']
description: {一句话描述}

---

# {模块名称} - {英文名}

## 🎯 适用场景 (When to Use)

**使用条件**:

- 条件1
- 条件2
- 条件3

**不适用场景**:

- 场景1
- 场景2

## 📐 数学公式 (Mathematical Formulation)
```

[数学公式]

````

## 💻 伪代码 (Pseudocode)

```python
def algorithm_name(input_data):
    """
    [算法描述]
    """
    # Step 1: [步骤1]
    ...

    # Step 2: [步骤2]
    ...

    return solution
````

## ⏱️ 复杂度分析 (Complexity Analysis)

- **时间复杂度**: O(...)
- **空间复杂度**: O(...)
- **最优情况**: ...
- **最坏情况**: ...

## 🎛️ 参数指南 (Parameter Guide)

| 参数   | 类型  | 默认值 | 取值范围   | 说明     |
| ------ | ----- | ------ | ---------- | -------- |
| param1 | int   | 100    | [10, 1000] | 参数说明 |
| param2 | float | 0.8    | [0, 1]     | 参数说明 |

## 📊 示例 (Examples)

### 示例1: [场景描述]

**输入**:

```yaml
[输入数据]
```

**输出**:

```yaml
[输出结果]
```

## 🔗 引用 (Citations)

- [论文1] Author, Year
- [书籍1] Title, Publisher, Year
- [代码] GitHub链接

## 💡 实践建议 (Best Practices)

1. 建议1
2. 建议2
3. 建议3

## ⚠️ 常见陷阱 (Common Pitfalls)

1. 陷阱1及解决方法
2. 陷阱2及解决方法

---

**创建**: {创建日期}
**BMAD版本**: v6-alpha
**质量评分**: {0-1分数}

````

---

### Phase 3: 自动扩展机制（Week 3-4）

#### 3.1 设计知识提取工作流

**新建文件**: `bmad/aps/tasks/expand-knowledge-library.md`

```markdown
# Task: Expand Knowledge Library

**任务ID**: `expand-knowledge-library`
**版本**: V1.0
**用途**: 从用户代码中提取知识，扩展知识库

## 触发条件

1. 用户确认代码质量 >= 0.9
2. 用户明确授权知识提取
3. 代码与现有知识库相似度 < 0.8（避免重复）

## 输入

- implementation_code: 用户确认的高质量代码
- ten_element_model: 对应的十要素模型
- user_feedback: 用户反馈和评价
- problem_description: 问题描述

## 处理逻辑

### Step 1: 代码分析

```python
def analyze_user_code(code, ten_element_model):
    """
    分析用户代码，识别可提取的知识
    """
    analysis_result = {
        "algorithms_found": [],
        "constraints_found": [],
        "objectives_found": [],
        "domain_patterns_found": []
    }

    # 1. 识别算法模式
    # 分析类结构、核心循环、搜索策略
    algorithms = extract_algorithms(code)
    for algo in algorithms:
        if is_novel_or_improved(algo, knowledge_library):
            analysis_result["algorithms_found"].append(algo)

    # 2. 识别约束处理
    constraint_functions = extract_constraint_functions(code)
    for constraint in constraint_functions:
        if is_reusable(constraint):
            analysis_result["constraints_found"].append(constraint)

    # 3. 识别目标计算
    objective_functions = extract_objective_functions(code)
    for obj in objective_functions:
        if is_generalizable(obj):
            analysis_result["objectives_found"].append(obj)

    return analysis_result
````

### Step 2: 知识生成

```python
def generate_knowledge_module(extracted_pattern, analysis):
    """
    将提取的模式转换为标准知识模块
    """
    module = {
        "module_name": extracted_pattern["name"],
        "category": extracted_pattern["category"],
        "description": generate_description(extracted_pattern),
        "pseudocode": abstract_to_pseudocode(extracted_pattern["code"]),
        "complexity": analyze_complexity(extracted_pattern["code"]),
        "parameters": extract_parameters(extracted_pattern["code"]),
        "examples": [{
            "problem": analysis["problem_description"],
            "solution": extracted_pattern["code"]
        }],
        "source": "user_contribution",
        "quality_score": analysis["user_feedback"]["quality_score"],
        "validation_needed": True
    }

    return module
```

### Step 3: 质量评估

```python
def evaluate_extracted_knowledge(module):
    """
    评估提取知识的质量和可复用性
    """
    scores = {
        "generalizability": 0.0,  # 通用性
        "novelty": 0.0,           # 新颖性
        "correctness": 0.0,       # 正确性
        "reusability": 0.0        # 可复用性
    }

    # 评估通用性：是否适用于多个场景
    scores["generalizability"] = assess_generalizability(module)

    # 评估新颖性：与现有知识库的差异度
    scores["novelty"] = calculate_novelty(module, knowledge_library)

    # 评估正确性：基于用户反馈和代码分析
    scores["correctness"] = module["quality_score"]

    # 评估可复用性：代码结构、注释质量等
    scores["reusability"] = assess_reusability(module)

    overall_score = sum(scores.values()) / len(scores)

    return {
        "overall_score": overall_score,
        "recommendation": "accept" if overall_score >= 0.75 else "review"
    }
```

### Step 4: 入库审核

- 自动审核（overall_score >= 0.85）
- 人工审核（0.75 <= overall_score < 0.85）
- 拒绝（overall_score < 0.75）

## 输出

- extracted_knowledge_modules: 提取的知识模块列表
- quality_evaluations: 质量评估结果
- library_update_plan: 知识库更新计划

````

---

### Phase 4: 知识库仪表板（Week 4）

#### 4.1 实时覆盖度监控

**新建文件**: `bmad/aps/scripts/generate-knowledge-dashboard.py`

```python
#!/usr/bin/env python3
"""
生成知识库仪表板

Usage:
    python scripts/generate-knowledge-dashboard.py
"""

import yaml
import json
from pathlib import Path
from datetime import datetime

def generate_dashboard():
    """生成HTML仪表板"""

    # 读取知识库清单
    with open('bmad/aps/knowledge-library-manifest.yaml') as f:
        manifest = yaml.safe_load(f)

    # 统计数据
    stats = {
        "overall_coverage": manifest["overall_metrics"]["overall_coverage"],
        "target_coverage": manifest["overall_metrics"]["target_coverage"],
        "total_modules": manifest["overall_metrics"]["total_modules"],
        "completed_modules": manifest["overall_metrics"]["completed_modules"],
        "libraries": {}
    }

    # 各库统计
    for lib_name in ["algorithm_library", "constraint_library", "objective_library", "domain_library"]:
        lib = manifest[lib_name]
        stats["libraries"][lib_name] = {
            "target": lib["target_coverage"],
            "current": calculate_current_coverage(lib),
            "modules": count_modules(lib)
        }

    # 生成HTML
    html = generate_html_dashboard(stats)

    # 保存
    output_path = Path("docs/knowledge-library-dashboard.html")
    output_path.write_text(html, encoding='utf-8')

    print(f"✓ 仪表板已生成: {output_path}")

def generate_html_dashboard(stats):
    """生成HTML代码"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>知识库仪表板</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            .metric {{ display: inline-block; margin: 20px; padding: 20px; border: 2px solid #333; border-radius: 10px; }}
            .progress-bar {{ width: 300px; height: 30px; background: #eee; border-radius: 5px; }}
            .progress-fill {{ height: 100%; background: #4CAF50; border-radius: 5px; transition: width 0.3s; }}
        </style>
    </head>
    <body>
        <h1>APS知识库成熟度仪表板</h1>
        <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="metric">
            <h2>总体覆盖度</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {stats['overall_coverage']*100}%"></div>
            </div>
            <p>{stats['overall_coverage']*100:.1f}% / {stats['target_coverage']*100:.1f}% (目标)</p>
            <p>{stats['completed_modules']} / {stats['total_modules']} 模块</p>
        </div>

        <!-- 各库详情 -->
        ...
    </body>
    </html>
    """

if __name__ == "__main__":
    generate_dashboard()
````

---

## ✅ 验证清单

- [ ] `knowledge-library-manifest.yaml` 已创建
- [ ] 定义了4个库的覆盖度目标
- [ ] 制定了优先级填充计划
- [ ] 建立了质量评估标准
- [ ] 创建了知识模块标准模板
- [ ] 实现了知识提取工作流
- [ ] 生成了知识库仪表板
- [ ] Week 2覆盖度达到40%
- [ ] Week 3覆盖度达到50%
- [ ] Week 4覆盖度达到60%

---

## 📊 预期收益

### 短期收益（30天）

- ✅ 知识库覆盖度：20% → 50-60%
- ✅ 专家推荐准确率：+20%
- ✅ 置信度稳定性提升

### 中期收益（6个月）

- ✅ 知识库覆盖度：60% → 70%+
- ✅ 推荐质量持续稳定
- ✅ 建立知识资产

### 长期收益

- ✅ 知识库随使用量增长
- ✅ 形成竞争壁垒
- ✅ 可授权或售卖知识库

---

## 📞 相关资源

- **清单文件**: `bmad/aps/knowledge-library-manifest.yaml`
- **仪表板**: `docs/knowledge-library-dashboard.html`
- **模板**: `bmad/aps/templates/knowledge-module-template.md`

---

**创建日期**: 2025-10-31
**最后更新**: 2025-10-31
**状态**: ⏳ 待实施
