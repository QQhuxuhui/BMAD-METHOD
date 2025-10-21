# Task: Check Todo Completion

**任务ID**: `check-todo-completion`
**版本**: V4.3
**用途**: Phase 4.4 - 检查Todo完成度，验证执行合同履行情况

## 输入

```yaml
inputs:
  - confirmed_todo_list: Phase 0.3用户确认的Todo List
  - tracker_initialized: Phase 0.4初始化的TodoTracker
```

## 处理逻辑

### 步骤1: 加载Todo基线

```python
def load_todo_baseline(tracker_initialized):
    """
    加载Todo基线数据
    """
    baseline = tracker_initialized.get("baseline", {})

    baseline_data = {
        "todo_list_hash": baseline.get("todo_list_hash"),
        "total_tasks": baseline.get("total_tasks"),
        "task_sequence": baseline.get("task_sequence", []),
        "planned_deliverables": baseline.get("planned_deliverables", []),
        "phases": baseline.get("phases", [])
    }

    return baseline_data
```

### 步骤2: 统计任务完成情况

```python
def count_task_completion(tracker_initialized):
    """
    统计任务完成情况
    """
    tracking = tracker_initialized.get("tracking", {})

    completion_stats = {
        "total_tasks": len(tracker_initialized["baseline"]["task_sequence"]),
        "completed_tasks": len(tracking.get("completed_tasks", [])),
        "in_progress_tasks": len(tracking.get("in_progress_tasks", [])),
        "pending_tasks": len(tracking.get("pending_tasks", [])),
        "skipped_tasks": 0,
        "added_tasks": 0
    }

    # 计算完成率
    completion_stats["completion_rate"] = (
        completion_stats["completed_tasks"] / completion_stats["total_tasks"]
        if completion_stats["total_tasks"] > 0 else 0
    )

    return completion_stats
```

### 步骤3: 检查每个Phase的完成情况

```python
def check_phase_completion(baseline_data, tracking):
    """
    检查每个Phase的完成情况
    """
    phase_completion = []

    for phase in baseline_data["phases"]:
        phase_id = phase["phase_id"]

        # 获取该Phase的所有任务
        phase_tasks = [
            task for task in baseline_data["task_sequence"]
            if task["phase"] == phase_id
        ]

        # 统计完成情况
        completed = [
            task for task in phase_tasks
            if task["task_id"] in tracking.get("completed_tasks", [])
        ]

        phase_completion.append({
            "phase_id": phase_id,
            "phase_name": phase["phase_name"],
            "total_tasks": len(phase_tasks),
            "completed_tasks": len(completed),
            "completion_rate": len(completed) / len(phase_tasks) if phase_tasks else 0,
            "status": "completed" if len(completed) == len(phase_tasks) else "incomplete"
        })

    return phase_completion
```

### 步骤4: 检查计划交付物

```python
def check_planned_deliverables(baseline_data, integrated_solution):
    """
    检查计划的交付物是否都已生成
    """
    planned = baseline_data["planned_deliverables"]

    # 实际生成的交付物
    # 这里简化处理，实际会检查文件系统或解决方案中的实际交付物
    actual_deliverables = []

    if integrated_solution.get("ten_element_model"):
        actual_deliverables.append("TenElementModel")

    if integrated_solution.get("complete_code"):
        actual_deliverables.append("完整代码")

    if integrated_solution.get("quality_report"):
        actual_deliverables.append("质量报告")

    deliverable_check = {
        "planned": planned,
        "actual": actual_deliverables,
        "missing": [d for d in planned if d not in actual_deliverables],
        "extra": [d for d in actual_deliverables if d not in planned],
        "all_delivered": set(planned).issubset(set(actual_deliverables))
    }

    return deliverable_check
```

### 步骤5: 检查未完成项及原因

```python
def analyze_uncompleted_items(baseline_data, tracking):
    """
    分析未完成项及其原因
    """
    all_task_ids = [task["task_id"] for task in baseline_data["task_sequence"]]
    completed_ids = tracking.get("completed_tasks", [])

    uncompleted = [tid for tid in all_task_ids if tid not in completed_ids]

    uncompleted_items = []
    for task_id in uncompleted:
        task = next(
            (t for t in baseline_data["task_sequence"] if t["task_id"] == task_id),
            None
        )

        if task:
            # 分析原因
            reason = "unknown"
            if task_id in tracking.get("pending_tasks", []):
                reason = "pending"
            elif task_id in tracking.get("in_progress_tasks", []):
                reason = "in_progress"
            else:
                reason = "skipped"

            uncompleted_items.append({
                "task_id": task_id,
                "task_name": task["task_name"],
                "phase": task["phase"],
                "reason": reason
            })

    return uncompleted_items
```

### 步骤6: 生成完成度报告

```python
def generate_completion_report(
    completion_stats,
    phase_completion,
    deliverable_check,
    uncompleted_items,
    baseline_data
):
    """
    生成综合完成度报告
    """
    # 判断总体完成状态
    overall_complete = (
        completion_stats["completion_rate"] >= 0.95 and
        deliverable_check["all_delivered"] and
        len(uncompleted_items) == 0
    )

    report = {
        "overall_status": "completed" if overall_complete else "incomplete",
        "completion_percentage": round(completion_stats["completion_rate"] * 100, 1),
        "baseline_hash": baseline_data["todo_list_hash"],
        "statistics": completion_stats,
        "phase_breakdown": phase_completion,
        "deliverables": deliverable_check,
        "uncompleted_items": uncompleted_items,
        "summary": {
            "total_tasks": completion_stats["total_tasks"],
            "completed": completion_stats["completed_tasks"],
            "uncompleted": len(uncompleted_items),
            "all_phases_complete": all(
                p["status"] == "completed" for p in phase_completion
            ),
            "all_deliverables_ready": deliverable_check["all_delivered"]
        }
    }

    return report
```

## 输出

```yaml
outputs:
  completion_status:
    type: object
    required: true
    structure:
      overall_status: string (completed | incomplete)
      completion_percentage: float
      baseline_hash: string
      statistics: object
      phase_breakdown: array
      deliverables: object
      uncompleted_items: array
      summary: object

  uncompleted_items:
    type: array
    description: "未完成任务列表"
```

## 示例输出

### 完整完成示例

```json
{
  "completion_status": {
    "overall_status": "completed",
    "completion_percentage": 100.0,
    "baseline_hash": "a3f8c9d2",
    "statistics": {
      "total_tasks": 28,
      "completed_tasks": 28,
      "in_progress_tasks": 0,
      "pending_tasks": 0,
      "skipped_tasks": 0,
      "added_tasks": 0,
      "completion_rate": 1.0
    },
    "phase_breakdown": [
      {
        "phase_id": "phase-0",
        "phase_name": "Phase 0: 任务规划",
        "total_tasks": 4,
        "completed_tasks": 4,
        "completion_rate": 1.0,
        "status": "completed"
      }
    ],
    "deliverables": {
      "planned": ["TenElementModel", "完整代码", "质量报告"],
      "actual": ["TenElementModel", "完整代码", "质量报告"],
      "missing": [],
      "extra": [],
      "all_delivered": true
    },
    "uncompleted_items": [],
    "summary": {
      "total_tasks": 28,
      "completed": 28,
      "uncompleted": 0,
      "all_phases_complete": true,
      "all_deliverables_ready": true
    }
  },
  "uncompleted_items": []
}
```

### 部分完成示例

```json
{
  "completion_status": {
    "overall_status": "incomplete",
    "completion_percentage": 85.7,
    "baseline_hash": "a3f8c9d2",
    "statistics": {
      "total_tasks": 28,
      "completed_tasks": 24,
      "in_progress_tasks": 1,
      "pending_tasks": 3,
      "skipped_tasks": 0,
      "added_tasks": 0,
      "completion_rate": 0.857
    },
    "phase_breakdown": [
      {
        "phase_id": "phase-4",
        "phase_name": "Phase 4: 质量保证",
        "total_tasks": 5,
        "completed_tasks": 4,
        "completion_rate": 0.8,
        "status": "incomplete"
      }
    ],
    "deliverables": {
      "planned": ["TenElementModel", "完整代码", "质量报告"],
      "actual": ["TenElementModel", "完整代码"],
      "missing": ["质量报告"],
      "extra": [],
      "all_delivered": false
    },
    "uncompleted_items": [
      {
        "task_id": "task-4.1",
        "task_name": "质量全面验证",
        "phase": "phase-4",
        "reason": "in_progress"
      }
    ],
    "summary": {
      "total_tasks": 28,
      "completed": 24,
      "uncompleted": 4,
      "all_phases_complete": false,
      "all_deliverables_ready": false
    }
  },
  "uncompleted_items": [...]
}
```

## 质量检查

- [ ] 基线数据加载正确
- [ ] 完成率计算准确
- [ ] Phase分解详细
- [ ] 交付物检查完整
- [ ] 未完成项原因分析清晰

## 引用

- @编排协调专家库/Todo完成度检查
- V4.3架构规范: TodoTracker验证机制
- @任务管理规范/执行合同履行验证

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: Todo完成度验证，确保执行合同履行
