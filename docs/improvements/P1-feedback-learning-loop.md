# P1: 闭环学习机制

**优先级**: 🟡 P1 - 60天内完成
**预计工期**: 6周
**负责模块**: Phase 5 反馈与学习
**影响范围**: 全流程持续优化

---

## 📋 问题描述

### 现状

**缺少自我进化能力**:

```
当前系统: Phase 0-4 → 交付 → 结束
          ↓
      无反馈闭环
          ↓
      无法从失败中学习
      无法从成功中沉淀最佳实践
      无法随使用量增长能力
```

### 影响

1. **重复犯错** - 相同类型的问题反复出现
2. **能力固化** - 系统能力无法提升
3. **用户流失** - 失败案例没有改进机制
4. **资源浪费** - 优质用户代码未沉淀

---

## 🎯 解决方案

### 总体架构

```
┌──────────────────────────────────────────────────────┐
│  闭环学习系统                                         │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Phase 4: 交付                                        │
│      ↓                                                │
│  Phase 5: 反馈与学习（新增）                          │
│      ↓                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ 用户反馈 │  │ 失败分析 │  │ 知识提取 │           │
│  │ 收集     │→│ 根因定位 │→│ 入库     │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│      ↓              ↓              ↓                  │
│  ┌────────────────────────────────────────┐          │
│  │ 持续优化引擎                           │          │
│  │ - A/B测试                              │          │
│  │ - 策略优化                             │          │
│  │ - 知识库更新                           │          │
│  └────────────────────────────────────────┘          │
│      ↓                                                │
│  Phase 0-4: 能力提升                                  │
└──────────────────────────────────────────────────────┘
```

---

## 🛠️ 实施步骤

### Phase 5: 反馈与学习工作流

#### 5.1 新增Phase 5到主工作流

**文件**: `bmad/aps/workflows/scheduling-orchestration/workflow.yaml`

**位置**: Phase 4之后新增

```yaml
- phase_id: 'phase-5'
  phase_name: 'Phase 5: 反馈与学习（可选）'
  estimated_time: '3-5分钟'
  description: '收集用户反馈，提取失败教训，更新知识库'
  optional: true # 可选阶段
  trigger_condition: 'user_accepts_feedback_request'

  steps:
    - step_id: '5.1'
      name: '用户反馈收集'
      action: 'human_feedback'
      trigger_level: 'P3'
      template: '@交互对话模板库/feedback-collection-template.md'

      inputs:
        - deliverables: '${phase_3_state.state_data.deliverable_manifest}'
        - quality_report: '${phase_4_state.state_data.quality_report}'
        - execution_log: '${workflow_log}'

      questions:
        - question: '代码质量评分（1-5星）'
          type: 'rating'
          scale: 5

        - question: '代码是否直接可用？'
          type: 'boolean'

        - question: '遇到的主要问题'
          type: 'multiple_choice'
          options:
            - '代码无法运行'
            - '逻辑错误'
            - '性能不达标'
            - '缺少功能'
            - '其他'

        - question: '整体满意度（1-5星）'
          type: 'rating'
          scale: 5

        - question: '改进建议（可选）'
          type: 'text'
          optional: true

      outputs:
        - feedback_data:
            code_quality_rating: int # 1-5
            code_usable: bool
            main_issues: List[str]
            satisfaction_score: int # 1-5
            improvement_suggestions: str
            timestamp: datetime

    - step_id: '5.2'
      name: '失败案例分析'
      action: 'conditional_exec'
      condition: 'feedback_data.satisfaction_score < 4 OR NOT feedback_data.code_usable'
      target: 'bmad/aps/tasks/analyze-failure-cases.md'

      inputs:
        - feedback_data
        - workflow_log
        - phase_1_5_state: '十要素模型'
        - phase_2_state: '专家分析'
        - phase_3_state: '方案和代码'
        - quality_report

      outputs:
        - failure_analysis:
            root_causes: List[str]
            affected_phases: List[str]
            severity: str # critical | major | minor
            lessons_learned: List[str]

    - step_id: '5.3'
      name: '知识库更新建议'
      action: 'exec'
      target: 'bmad/aps/tasks/suggest-knowledge-updates.md'

      inputs:
        - failure_analysis
        - feedback_data
        - knowledge_library_manifest

      outputs:
        - update_recommendations:
            new_modules: List[dict]
            improved_modules: List[dict]
            deprecated_modules: List[dict]
            priority_queue: List[dict]

    - step_id: '5.4'
      name: '优质代码知识提取'
      action: 'conditional_exec'
      condition: 'feedback_data.code_quality_rating >= 4 AND feedback_data.code_usable'
      target: 'bmad/aps/tasks/expand-knowledge-library.md'

      inputs:
        - implementation_code: '${phase_3_state.state_data.implementation_code}'
        - ten_element_model: '${phase_1_5_state.state_data.ten_element_model}'
        - user_feedback: '${feedback_data}'

      outputs:
        - extracted_knowledge_modules
        - quality_evaluations
        - library_updated: bool

    - step_id: '5.5'
      name: '💾 保存Phase 5状态'
      action: 'exec'
      target: 'bmad/aps/tasks/save-phase-state.md'

      mandatory_save: true

      inputs:
        - phase_id: 'phase_5'
        - state_data:
            feedback_data: ${feedback_data}
            failure_analysis: ${failure_analysis}
            update_recommendations: ${update_recommendations}
            extracted_knowledge_modules: ${extracted_knowledge_modules}
        - state_folder: '${config.state_management.state_folder}'

      outputs:
        - saved_state_file
        - verification_result
```

---

### 失败案例分析任务

**新建文件**: `bmad/aps/tasks/analyze-failure-cases.md`

````markdown
# Task: Analyze Failure Cases

**任务ID**: `analyze-failure-cases`
**版本**: V1.0
**用途**: 分析失败案例，定位根因，提取教训

## 输入

- feedback_data: 用户反馈数据
- workflow_log: 完整工作流日志
- phase_states: 各Phase的状态数据
- quality_report: 质量报告

## 处理逻辑

### Step 1: 失败分类

```python
def classify_failure(feedback_data, workflow_log):
    """
    对失败进行分类
    """
    failure_categories = {
        "code_generation_error": False,      # 代码生成错误
        "logic_error": False,                # 逻辑错误
        "knowledge_gap": False,              # 知识缺失
        "model_hallucination": False,        # 大模型幻觉
        "requirement_misunderstanding": False, # 需求理解错误
        "workflow_issue": False              # 工作流问题
    }

    # 基于用户反馈判断
    if "代码无法运行" in feedback_data["main_issues"]:
        failure_categories["code_generation_error"] = True

    if "逻辑错误" in feedback_data["main_issues"]:
        failure_categories["logic_error"] = True

    # 基于工作流日志判断
    if has_low_confidence_warnings(workflow_log):
        failure_categories["knowledge_gap"] = True

    return failure_categories
```
````

### Step 2: 根因定位

```python
def identify_root_causes(failure_categories, phase_states, workflow_log):
    """
    定位失败的根本原因
    """
    root_causes = []

    # 代码生成错误 → 检查编码任务
    if failure_categories["code_generation_error"]:
        code_issues = analyze_generated_code(phase_states["phase_3"])
        if "missing_element_9" in code_issues:
            root_causes.append({
                "cause": "Element 9数据加载模块缺失",
                "phase": "Phase 3",
                "component": "generate-code-from-solution.md",
                "fix": "新增步骤3.15生成数据加载模块"
            })

    # 逻辑错误 → 检查专家分析
    if failure_categories["logic_error"]:
        expert_issues = analyze_expert_outputs(phase_states["phase_2"])
        if expert_issues["low_confidence"]:
            root_causes.append({
                "cause": "专家推荐置信度低，可能依赖幻觉",
                "phase": "Phase 2",
                "component": f"{expert_issues['expert']}-expert.md",
                "fix": "补充相关知识库模块"
            })

    # 知识缺失 → 检查知识库
    if failure_categories["knowledge_gap"]:
        missing_knowledge = identify_missing_knowledge(workflow_log)
        root_causes.append({
            "cause": f"知识库缺失: {missing_knowledge}",
            "phase": "Phase 2",
            "component": "knowledge-library",
            "fix": f"填充 {missing_knowledge} 知识模块"
        })

    return root_causes
```

### Step 3: 提取教训

```python
def extract_lessons_learned(root_causes, feedback_data):
    """
    从失败中提取可行动的教训
    """
    lessons = []

    for cause in root_causes:
        lesson = {
            "problem": cause["cause"],
            "solution": cause["fix"],
            "affected_component": cause["component"],
            "priority": calculate_priority(cause),
            "actionable_steps": generate_action_steps(cause)
        }
        lessons.append(lesson)

    return lessons
```

## 输出

```yaml
failure_analysis:
  root_causes:
    - cause: 'Element 9数据加载模块缺失'
      phase: 'Phase 3'
      component: 'generate-code-from-solution.md'
      fix: '新增步骤3.15生成数据加载模块'
      severity: 'critical'

  affected_phases: ['Phase 3']

  severity: 'critical' # critical | major | minor

  lessons_learned:
    - problem: '编码任务步骤未覆盖所有十要素'
      solution: '建立十要素→代码映射强制验证'
      priority: 'P0'
      actionable_steps:
        - '修改generate-code-from-solution.md'
        - '添加validate-element-code-mapping任务'
        - '更新workflow添加验证门禁'

  recommendations:
    immediate_actions: [...]
    preventive_measures: [...]
```

````

---

### 知识库更新建议任务

**新建文件**: `bmad/aps/tasks/suggest-knowledge-updates.md`

```markdown
# Task: Suggest Knowledge Updates

**任务ID**: `suggest-knowledge-updates`
**版本**: V1.0
**用途**: 基于失败分析，生成知识库更新建议

## 输入

- failure_analysis: 失败分析结果
- feedback_data: 用户反馈
- knowledge_library_manifest: 知识库清单

## 处理逻辑

### Step 1: 识别知识缺口

```python
def identify_knowledge_gaps(failure_analysis, knowledge_library_manifest):
    """
    识别知识库中的缺口
    """
    gaps = []

    for cause in failure_analysis["root_causes"]:
        if "知识库缺失" in cause["cause"]:
            # 解析缺失的知识类型
            missing_type = parse_missing_knowledge_type(cause)

            # 检查知识库清单
            if not exists_in_manifest(missing_type, knowledge_library_manifest):
                gaps.append({
                    "type": missing_type["category"],  # algorithm | constraint | objective
                    "name": missing_type["name"],
                    "priority": "high",
                    "reason": cause["cause"]
                })

    return gaps
````

### Step 2: 生成更新建议

```python
def generate_update_recommendations(gaps, knowledge_library_manifest):
    """
    生成具体的知识库更新建议
    """
    recommendations = {
        "new_modules": [],      # 需要新增的模块
        "improved_modules": [], # 需要改进的模块
        "deprecated_modules": [], # 需要废弃的模块
        "priority_queue": []    # 优先级队列
    }

    # 新增模块
    for gap in gaps:
        module_spec = {
            "name": gap["name"],
            "type": gap["type"],
            "priority": gap["priority"],
            "estimated_effort": estimate_effort(gap),
            "rationale": gap["reason"],
            "target_file": generate_file_path(gap)
        }
        recommendations["new_modules"].append(module_spec)

    # 改进现有模块（如果用户反馈质量不高）
    if feedback_data["code_quality_rating"] < 4:
        low_quality_modules = identify_low_quality_modules(
            feedback_data,
            knowledge_library_manifest
        )
        recommendations["improved_modules"] = low_quality_modules

    # 生成优先级队列
    all_updates = recommendations["new_modules"] + recommendations["improved_modules"]
    recommendations["priority_queue"] = sort_by_priority(all_updates)

    return recommendations
```

## 输出

```yaml
update_recommendations:
  new_modules:
    - name: 'tabu_search'
      type: 'algorithm'
      priority: 'high'
      estimated_effort: '2天'
      rationale: '用户问题需要该算法，但知识库缺失'
      target_file: 'algorithm-library/meta-heuristic/tabu-search.md'

  improved_modules:
    - name: 'genetic_algorithm'
      type: 'algorithm'
      current_quality: 0.75
      target_quality: 0.90
      issues:
        - '参数指南不够详细'
        - '缺少复杂度分析'

  priority_queue:
    - { module: 'tabu_search', priority: 1, effort: '2天' }
    - { module: 'genetic_algorithm_improvement', priority: 2, effort: '1天' }
```

````

---

### A/B测试框架

**新建文件**: `bmad/aps/ab-testing-framework.py`

```python
#!/usr/bin/env python3
"""
A/B测试框架 - 用于持续优化专家策略

Usage:
    from ab_testing_framework import ABTestManager

    manager = ABTestManager()
    strategy = manager.select_strategy("algorithm_selection")
    ...
    manager.record_outcome(strategy, success_score=0.85)
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Strategy:
    """策略定义"""
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]

@dataclass
class Outcome:
    """结果记录"""
    strategy_name: str
    timestamp: datetime
    success_score: float  # 0-1
    user_satisfaction: float  # 0-1
    execution_time: float  # seconds
    metadata: Dict[str, Any]

class ABTestManager:
    """A/B测试管理器"""

    def __init__(self, data_file: str = "bmad/aps/ab-test-data.json"):
        self.data_file = Path(data_file)
        self.strategies = self._load_strategies()
        self.history = self._load_history()
        self.epsilon = 0.1  # 探索率

    def _load_strategies(self) -> Dict[str, List[Strategy]]:
        """加载策略配置"""
        return {
            "algorithm_selection": [
                Strategy(
                    name="greedy_best_fit",
                    category="algorithm_selection",
                    description="贪心选择最佳拟合算法",
                    parameters={"考虑因素": ["问题规模", "约束复杂度"]}
                ),
                Strategy(
                    name="multi_criteria_weighted",
                    category="algorithm_selection",
                    description="多准则加权评分",
                    parameters={"权重": {"性能": 0.4, "易用性": 0.3, "稳定性": 0.3}}
                )
            ],
            "constraint_handling": [
                Strategy(name="repair_first", category="constraint_handling",
                        description="优先修复策略", parameters={}),
                Strategy(name="penalty_based", category="constraint_handling",
                        description="罚函数策略", parameters={}),
                Strategy(name="hybrid", category="constraint_handling",
                        description="混合策略", parameters={})
            ],
            "objective_weighting": [
                Strategy(name="user_defined", category="objective_weighting",
                        description="用户定义权重", parameters={}),
                Strategy(name="auto_optimized", category="objective_weighting",
                        description="自动优化权重", parameters={}),
                Strategy(name="pareto_front", category="objective_weighting",
                        description="帕累托前沿", parameters={})
            ]
        }

    def _load_history(self) -> List[Outcome]:
        """加载历史记录"""
        if not self.data_file.exists():
            return []

        with open(self.data_file) as f:
            data = json.load(f)
            return [Outcome(**item) for item in data]

    def select_strategy(self, category: str) -> Strategy:
        """
        选择策略（epsilon-greedy）

        Args:
            category: 策略类别

        Returns:
            Strategy: 选中的策略
        """
        strategies = self.strategies.get(category, [])
        if not strategies:
            raise ValueError(f"Unknown category: {category}")

        # Epsilon-greedy策略
        if random.random() < self.epsilon:
            # 探索：随机选择
            strategy = random.choice(strategies)
            print(f"🔍 探索模式: 尝试策略 {strategy.name}")
        else:
            # 利用：选择最佳策略
            strategy = self._get_best_strategy(category)
            print(f"✅ 利用模式: 使用最佳策略 {strategy.name}")

        return strategy

    def _get_best_strategy(self, category: str) -> Strategy:
        """获取当前最佳策略"""
        strategies = self.strategies[category]

        # 计算每个策略的平均成功率
        performance = {}
        for strategy in strategies:
            outcomes = [o for o in self.history
                       if o.strategy_name == strategy.name]

            if outcomes:
                avg_score = sum(o.success_score for o in outcomes) / len(outcomes)
                performance[strategy.name] = avg_score
            else:
                # 未测试过的策略给予中等评分
                performance[strategy.name] = 0.5

        # 选择最佳
        best_name = max(performance, key=performance.get)
        return next(s for s in strategies if s.name == best_name)

    def record_outcome(self, strategy: Strategy, success_score: float,
                      user_satisfaction: float = None,
                      execution_time: float = None,
                      metadata: Dict = None):
        """
        记录策略结果

        Args:
            strategy: 使用的策略
            success_score: 成功评分（0-1）
            user_satisfaction: 用户满意度（可选）
            execution_time: 执行时间（可选）
            metadata: 其他元数据（可选）
        """
        outcome = Outcome(
            strategy_name=strategy.name,
            timestamp=datetime.now(),
            success_score=success_score,
            user_satisfaction=user_satisfaction or success_score,
            execution_time=execution_time or 0.0,
            metadata=metadata or {}
        )

        self.history.append(outcome)
        self._save_history()

        print(f"📊 记录结果: {strategy.name} → 成功率 {success_score:.2%}")

    def _save_history(self):
        """保存历史记录"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(o) for o in self.history]
        # 处理datetime序列化
        for item in data:
            item["timestamp"] = item["timestamp"].isoformat()

        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_report(self) -> Dict:
        """生成A/B测试报告"""
        report = {
            "total_experiments": len(self.history),
            "strategies_tested": len(set(o.strategy_name for o in self.history)),
            "performance_by_strategy": {},
            "best_strategy_per_category": {}
        }

        # 按策略统计性能
        for category, strategies in self.strategies.items():
            category_outcomes = {}

            for strategy in strategies:
                outcomes = [o for o in self.history
                           if o.strategy_name == strategy.name]

                if outcomes:
                    category_outcomes[strategy.name] = {
                        "试验次数": len(outcomes),
                        "平均成功率": sum(o.success_score for o in outcomes) / len(outcomes),
                        "平均满意度": sum(o.user_satisfaction for o in outcomes) / len(outcomes)
                    }

            report["performance_by_strategy"][category] = category_outcomes

            # 找出最佳策略
            if category_outcomes:
                best = max(category_outcomes.items(),
                          key=lambda x: x[1]["平均成功率"])
                report["best_strategy_per_category"][category] = {
                    "策略": best[0],
                    "成功率": best[1]["平均成功率"]
                }

        return report


if __name__ == "__main__":
    # 示例使用
    manager = ABTestManager()

    # 模拟10次实验
    for i in range(10):
        strategy = manager.select_strategy("algorithm_selection")
        # 模拟结果（实际应基于真实反馈）
        success = random.uniform(0.6, 0.95)
        manager.record_outcome(strategy, success_score=success)

    # 生成报告
    report = manager.generate_report()
    print("\n📈 A/B测试报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
````

---

## ✅ 验证清单

- [ ] Phase 5工作流已添加到主流程
- [ ] `analyze-failure-cases.md` 已创建
- [ ] `suggest-knowledge-updates.md` 已创建
- [ ] A/B测试框架已实现
- [ ] 用户反馈模板已创建
- [ ] 失败案例知识库已建立
- [ ] 端到端测试通过

---

## 📊 预期收益

### 短期收益（60天）

- ✅ 建立失败案例知识库
- ✅ 识别系统薄弱环节
- ✅ 快速响应用户问题

### 中期收益（6个月）

- ✅ 失败率下降30%
- ✅ 知识库自动更新
- ✅ 策略持续优化

### 长期收益

- ✅ 系统能力随使用量增长
- ✅ 形成学习飞轮效应
- ✅ 建立不可复制的竞争壁垒

---

## 📞 相关资源

- **工作流文件**: `bmad/aps/workflows/scheduling-orchestration/workflow.yaml`
- **A/B测试**: `bmad/aps/ab-testing-framework.py`
- **失败案例库**: `bmad/aps/failure-cases/`

---

**创建日期**: 2025-10-31
**最后更新**: 2025-10-31
**状态**: ⏳ 待实施
