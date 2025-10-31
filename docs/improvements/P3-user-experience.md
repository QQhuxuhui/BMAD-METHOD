# P3: 用户体验设计优化

**优先级**: 🟢 P3 - 长期持续
**预计工期**: 持续迭代
**负责模块**: 用户交互层
**影响范围**: 全流程用户体验

---

## 📋 问题描述

### 现状

**用户体验有提升空间**:

```
当前交互:
  Mode A: 2-3次集中确认
  Mode B: 4-5次增量确认

改进空间:
  → 缺少零交互模式（专家用户）
  → 缺少方案对比功能
  → 缺少进度可视化
  → 缺少批量处理能力
  → 用户等待时焦虑
```

---

## 🎯 解决方案

### 1. Mode C：专家模式（零交互）

#### 1.1 设计思路

**适用场景**:

- 重复性问题（与历史案例相似度 > 0.9）
- 标准问题（知识库覆盖度 > 0.8）
- 高置信度（综合置信度 > 0.85）

**降级策略**:

- 如果置信度不足，自动降级到Mode A
- 用户可以随时介入

#### 1.2 实现方案

**新建文件**: `bmad/aps/tasks/execute-mode-c.md`

````markdown
# Task: Execute Mode C (Expert Mode)

**任务ID**: `execute-mode-c`
**版本**: V1.0
**用途**: 专家模式，零交互自动执行

## 前置条件检查

```python
def can_use_mode_c(problem, historical_cases, knowledge_library):
    """
    判断是否可以使用Mode C
    """
    checks = {
        "similarity_check": False,
        "coverage_check": False,
        "confidence_check": False
    }

    # 1. 相似度检查
    similar_cases = find_similar_cases(problem, historical_cases)
    if similar_cases and similar_cases[0]["similarity"] > 0.90:
        checks["similarity_check"] = True

    # 2. 知识库覆盖度检查
    coverage = assess_knowledge_coverage(problem, knowledge_library)
    if coverage > 0.80:
        checks["coverage_check"] = True

    # 3. 预估置信度
    estimated_confidence = estimate_confidence(problem, similar_cases, coverage)
    if estimated_confidence > 0.85:
        checks["confidence_check"] = True

    return all(checks.values()), checks
```
````

## 执行流程

```yaml
mode_c_workflow:
  - phase_0: '自动生成Todo List（不等待确认）'
  - phase_1: '自动需求分析'
  - phase_1_5: '自动建模（使用最相似案例的模板）'
  - phase_2: '专家协调（基于历史最佳策略）'
  - phase_3: '方案生成与代码生成'
  - phase_4: '质量保证（自动运行所有检查）'
  - phase_5: '可选反馈（邀请用户评价）'
# 关键：全程无人机交互，仅在最后交付时通知用户
```

## 监控与降级

```python
def monitor_and_fallback(execution_state):
    """
    监控执行过程，必要时降级到Mode A
    """
    # 实时监控置信度
    if execution_state["current_confidence"] < 0.70:
        return {
            "action": "fallback_to_mode_a",
            "reason": "置信度下降到不安全水平",
            "trigger_human_review": True
        }

    # 监控异常
    if execution_state["errors_count"] > 0:
        return {
            "action": "fallback_to_mode_a",
            "reason": "执行过程中遇到错误",
            "trigger_human_review": True
        }

    return {"action": "continue"}
```

## 输出

- execution_result: 执行结果
- actual_confidence: 实际置信度
- fallback_triggered: 是否触发降级

````

#### 1.3 用户选择界面

**模式选择增强**:

```markdown
## 选择您的交互模式

### 🚀 Mode C: 专家模式（推荐）
**适合**: 重复性问题或标准问题
**特点**: 零交互，全自动执行
**时长**: 35-45分钟
**置信度**: 高（> 85%）
**说明**: 系统将自动完成所有步骤，最后交付完整方案和代码

✅ 您的问题与历史案例相似度: 92%
✅ 知识库覆盖度: 87%
✅ 预估成功率: 90%

### 💼 Mode A: 集中确认
（现有模式）

### 🎯 Mode B: 增量确认
（现有模式）

---

💡 **智能推荐**: 您的问题适合使用 Mode C，可节省 10-15分钟
````

---

### 2. 方案对比功能

#### 2.1 多方案生成

**在Phase 3生成多个候选方案**:

```python
def generate_multiple_solutions(expert_analyses, ten_element_model):
    """
    生成多个候选方案供用户选择
    """
    solutions = []

    # 方案A: 推荐方案（最优综合评分）
    solution_a = generate_solution(
        algorithm=expert_analyses["algorithm_recommendations"]["primary"],
        constraint_strategy="repair_first",
        objective_strategy="weighted_sum"
    )
    solution_a["name"] = "方案A（推荐）"
    solution_a["score"] = calculate_overall_score(solution_a)
    solutions.append(solution_a)

    # 方案B: 速度优先
    solution_b = generate_solution(
        algorithm=expert_analyses["algorithm_recommendations"]["alternatives"][0],
        constraint_strategy="penalty",
        objective_strategy="lexicographic"
    )
    solution_b["name"] = "方案B（速度优先）"
    solution_b["score"] = calculate_overall_score(solution_b)
    solutions.append(solution_b)

    # 方案C: 质量优先
    solution_c = generate_solution(
        algorithm=expert_analyses["algorithm_recommendations"]["alternatives"][1],
        constraint_strategy="repair_with_backtrack",
        objective_strategy="pareto_front"
    )
    solution_c["name"] = "方案C（质量优先）"
    solution_c["score"] = calculate_overall_score(solution_c)
    solutions.append(solution_c)

    return sorted(solutions, key=lambda s: s["score"], reverse=True)
```

#### 2.2 对比展示模板

**新建文件**: `bmad/aps/templates/interaction-templates/solution-comparison-template.md`

```markdown
# 方案对比与选择

系统为您生成了 **3个候选方案**，请选择最适合您的方案：

---

## 📊 方案对比

| 维度             | 方案A（推荐）⭐ | 方案B（速度优先） | 方案C（质量优先）   |
| ---------------- | --------------- | ----------------- | ------------------- |
| **算法**         | 混合遗传算法    | 禁忌搜索          | 模拟退火 + 局部搜索 |
| **预计求解时间** | 5-10分钟        | 3-5分钟 ⚡        | 10-20分钟           |
| **解质量**       | 优（95%最优）   | 良（90%最优）     | 优+（96%最优）🏆    |
| **代码复杂度**   | 中              | 低 ✅             | 高                  |
| **可维护性**     | 高 ✅           | 中                | 中                  |
| **内存占用**     | 中等（100MB）   | 低（50MB）✅      | 高（200MB）         |
| **参数敏感度**   | 中              | 低 ✅             | 高                  |
| **综合评分**     | **9.2/10** ⭐   | 7.8/10            | 8.5/10              |

---

## 📝 详细说明

### 方案A：混合遗传算法（推荐）⭐

**优势**:

- ✅ 综合性能最佳，适合大多数场景
- ✅ 代码结构清晰，易于理解和修改
- ✅ 鲁棒性强，参数不敏感

**劣势**:

- ⚠️ 求解时间略长于方案B

**适用场景**:

- 生产环境部署
- 需要长期维护的系统
- 对解质量和稳定性要求高

---

### 方案B：禁忌搜索（速度优先）⚡

**优势**:

- ✅ 求解速度最快
- ✅ 代码简洁，易于部署
- ✅ 内存占用小

**劣势**:

- ⚠️ 解质量略低于其他方案
- ⚠️ 对某些复杂约束处理不够好

**适用场景**:

- 原型验证
- 实时性要求高
- 资源受限环境

---

### 方案C：模拟退火 + 局部搜索（质量优先）🏆

**优势**:

- ✅ 解质量最高
- ✅ 对复杂问题表现出色

**劣势**:

- ⚠️ 求解时间最长
- ⚠️ 参数调优复杂
- ⚠️ 代码复杂度高

**适用场景**:

- 科研和竞赛
- 对解质量要求极高
- 离线优化

---

## ❓ 帮助您选择

### 如果您关注...

- **🎯 综合平衡** → 选择方案A
- **⚡ 快速原型** → 选择方案B
- **🏆 极致性能** → 选择方案C

### 系统推荐

基于您的问题特征和历史数据，我们推荐 **方案A**，理由：

1. ✅ 问题规模中等，方案A的求解时间完全可接受
2. ✅ 您的约束较复杂，方案A的鲁棒性更有保障
3. ✅ 方案A的代码可维护性最佳，适合长期使用

---

## 🔀 选择方案

请输入您选择的方案编号（A/B/C），或输入"对比更多"查看详细技术对比。

> 💡 **提示**: 如果不确定，建议选择方案A（推荐方案）
```

---

### 3. 进度可视化

#### 3.1 实时进度展示

```markdown
# 调度优化求解进度

┌────────────────────────────────────────────────────────┐
│ APS调度智能体团队 - 执行进度 │
└────────────────────────────────────────────────────────┘

⏱️ 预计剩余时间: 25-30分钟
📊 总体进度: ████████████░░░░░░░░ 60%

---

## 阶段进度

✅ Phase 0: 任务规划 (已完成)
└─ 用时: 3分钟 | 质量评分: A

✅ Phase 1: 需求分析 (已完成)
└─ 用时: 8分钟 | 质量评分: A

✅ Phase 1.5: 十要素建模 (已完成)
└─ 用时: 12分钟 | 质量评分: A+

🔄 Phase 2: 专家协调 (进行中)
├─ ✅ 领域专家分析 (已完成)
├─ ✅ 约束专家分析 (已完成)
├─ 🔄 目标专家分析 (分析中... 75%)
│ └─ 正在执行: 多目标权重优化
└─ ⏳ 算法专家推荐 (等待中)

⏳ Phase 3: 方案集成与代码生成 (等待中)
⏳ Phase 4: 质量保证 (等待中)

---

## 专家工作状态

👨‍💼 **目标优化专家** (王目标)
状态: 🔄 工作中
任务: 分析多目标优化策略
进度: ████████████████░░░░ 75%
预计完成: 2分钟后

👨‍💻 **算法专家** (张效率)
状态: ⏳ 待命中
任务: 算法推荐与参数配置
预计开始: 3分钟后

---

## 知识库调用记录

📚 已调用知识模块: 8个
└─ @领域库/manufacturing/job-shop ✅
└─ @约束库/temporal/precedence-constraint ✅
└─ @约束库/resource/capacity-constraint ✅
└─ @目标库/time/makespan-minimization 🔄
└─ ... (更多)

---

💡 **提示**: 您可以随时按 Ctrl+C 中断执行
```

#### 3.2 进度追踪任务

**新建文件**: `bmad/aps/tasks/update-progress-display.md`

````markdown
# Task: Update Progress Display

**任务ID**: `update-progress-display`
**版本**: V1.0
**用途**: 更新实时进度显示

## 实现

```python
import sys
from datetime import datetime, timedelta

class ProgressTracker:
    """进度追踪器"""

    def __init__(self, total_phases=5):
        self.total_phases = total_phases
        self.current_phase = 0
        self.phase_start_time = None
        self.phase_progress = {}
        self.start_time = datetime.now()

    def start_phase(self, phase_id, phase_name, estimated_time):
        """开始新阶段"""
        self.current_phase += 1
        self.phase_start_time = datetime.now()
        self.phase_progress[phase_id] = {
            "name": phase_name,
            "status": "in_progress",
            "progress": 0.0,
            "estimated_time": estimated_time
        }
        self._render()

    def update_phase_progress(self, phase_id, progress, current_task):
        """更新阶段进度"""
        if phase_id in self.phase_progress:
            self.phase_progress[phase_id]["progress"] = progress
            self.phase_progress[phase_id]["current_task"] = current_task
            self._render()

    def complete_phase(self, phase_id, quality_score):
        """完成阶段"""
        if phase_id in self.phase_progress:
            self.phase_progress[phase_id]["status"] = "completed"
            self.phase_progress[phase_id]["progress"] = 1.0
            self.phase_progress[phase_id]["quality_score"] = quality_score
            self._render()

    def _render(self):
        """渲染进度界面"""
        # 清屏（可选）
        # sys.stdout.write("\033[2J\033[H")

        print("\n" + "="*60)
        print("  APS调度智能体团队 - 执行进度")
        print("="*60)

        # 总体进度
        overall_progress = self.current_phase / self.total_phases
        bar_length = 40
        filled = int(bar_length * overall_progress)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\n📊 总体进度: {bar} {overall_progress*100:.0f}%")

        # 预计剩余时间
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        if overall_progress > 0:
            estimated_total = elapsed / overall_progress
            remaining = estimated_total - elapsed
            print(f"⏱️  预计剩余时间: {remaining:.0f}分钟")

        print("\n## 阶段进度\n")

        # 各阶段状态
        for phase_id, info in self.phase_progress.items():
            status_icon = {
                "completed": "✅",
                "in_progress": "🔄",
                "pending": "⏳"
            }.get(info["status"], "⏳")

            print(f"{status_icon} {info['name']}")

            if info["status"] == "completed":
                quality_grade = self._get_quality_grade(info.get("quality_score", 0))
                print(f"   └─ 质量评分: {quality_grade}")

            elif info["status"] == "in_progress":
                progress = info.get("progress", 0)
                task = info.get("current_task", "进行中")
                bar = "█" * int(20 * progress) + "░" * (20 - int(20 * progress))
                print(f"   └─ {task}: {bar} {progress*100:.0f}%")

        print("\n" + "="*60 + "\n")

    def _get_quality_grade(self, score):
        """获取质量等级"""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        else:
            return "C"
```
````

````

---

### 4. 批量处理能力

#### 4.1 批量任务管理器

**新建文件**: `bmad/aps/scripts/batch-processor.py`

```python
#!/usr/bin/env python3
"""
批量处理管理器

Usage:
    python scripts/batch-processor.py --tasks tasks.yaml --mode mode_c
"""

import yaml
import argparse
from pathlib import Path
from datetime import datetime
import concurrent.futures

class BatchProcessor:
    """批量任务处理器"""

    def __init__(self, mode="mode_c", max_workers=3):
        self.mode = mode
        self.max_workers = max_workers
        self.results = []

    def load_tasks(self, tasks_file):
        """加载任务列表"""
        with open(tasks_file) as f:
            return yaml.safe_load(f)["tasks"]

    def process_single_task(self, task):
        """处理单个任务"""
        print(f"\n▶️ 开始处理任务: {task['name']}")

        start_time = datetime.now()

        try:
            # 调用主工作流
            from aps_orchestrator import run_workflow

            result = run_workflow(
                user_request=task["description"],
                mode=self.mode,
                output_dir=f"outputs/{task['name']}"
            )

            duration = (datetime.now() - start_time).total_seconds() / 60

            return {
                "task_name": task["name"],
                "status": "success",
                "duration_minutes": duration,
                "output_dir": result["output_dir"],
                "quality_score": result["quality_score"]
            }

        except Exception as e:
            return {
                "task_name": task["name"],
                "status": "failed",
                "error": str(e)
            }

    def process_batch(self, tasks_file):
        """批量处理"""
        tasks = self.load_tasks(tasks_file)

        print(f"\n{'='*60}")
        print(f"  批量处理管理器")
        print(f"  模式: {self.mode}")
        print(f"  任务数: {len(tasks)}")
        print(f"  并发数: {self.max_workers}")
        print(f"{'='*60}\n")

        # 并发执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_single_task, task): task
                      for task in tasks}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                self.results.append(result)
                self._print_result(result)

        # 生成报告
        self._generate_report()

    def _print_result(self, result):
        """打印单个结果"""
        if result["status"] == "success":
            print(f"✅ {result['task_name']}: 成功")
            print(f"   └─ 用时: {result['duration_minutes']:.1f}分钟")
            print(f"   └─ 质量: {result['quality_score']:.2f}")
        else:
            print(f"❌ {result['task_name']}: 失败")
            print(f"   └─ 错误: {result['error']}")

    def _generate_report(self):
        """生成批量处理报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "total_tasks": len(self.results),
            "successful": sum(1 for r in self.results if r["status"] == "success"),
            "failed": sum(1 for r in self.results if r["status"] == "failed"),
            "results": self.results
        }

        # 保存报告
        report_file = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        with open(report_file, 'w') as f:
            yaml.dump(report, f, allow_unicode=True)

        print(f"\n{'='*60}")
        print(f"  批量处理完成")
        print(f"  成功: {report['successful']}/{report['total_tasks']}")
        print(f"  失败: {report['failed']}/{report['total_tasks']}")
        print(f"  报告: {report_file}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量处理任务")
    parser.add_argument("--tasks", required=True, help="任务配置文件")
    parser.add_argument("--mode", default="mode_c", choices=["mode_a", "mode_b", "mode_c"])
    parser.add_argument("--workers", type=int, default=3, help="并发数")

    args = parser.parse_args()

    processor = BatchProcessor(mode=args.mode, max_workers=args.workers)
    processor.process_batch(args.tasks)
````

#### 4.2 批量任务配置示例

```yaml
# tasks.yaml

tasks:
  - name: 'task_1_workshop_scheduling'
    description: '10台机器，50个工单的车间调度'
    priority: 'high'

  - name: 'task_2_vehicle_routing'
    description: '25辆车，100个客户的配送路径优化'
    priority: 'medium'

  - name: 'task_3_project_scheduling'
    description: '20个项目任务的资源分配和时间安排'
    priority: 'low'
```

---

## ✅ 验证清单

- [ ] Mode C专家模式已实现
- [ ] 方案对比功能已实现
- [ ] 进度可视化已实现
- [ ] 批量处理器已实现
- [ ] 用户界面友好度测试通过
- [ ] 端到端用户体验测试通过

---

## 📊 预期收益

### 短期收益

- ✅ Mode C支持标准问题零交互
- ✅ 方案对比帮助用户做出更好决策
- ✅ 进度可视化减少用户焦虑

### 中期收益

- ✅ 用户满意度提升30%
- ✅ 批量处理支持规模化应用
- ✅ Mode C覆盖60%标准问题

### 长期收益

- ✅ 形成差异化竞争优势
- ✅ 支持SaaS化部署
- ✅ 用户粘性增强

---

## 📞 相关资源

- **Mode C任务**: `bmad/aps/tasks/execute-mode-c.md`
- **方案对比模板**: `bmad/aps/templates/interaction-templates/solution-comparison-template.md`
- **进度追踪**: `bmad/aps/tasks/update-progress-display.md`
- **批量处理器**: `bmad/aps/scripts/batch-processor.py`

---

**创建日期**: 2025-10-31
**最后更新**: 2025-10-31
**状态**: ⏳ 待实施
