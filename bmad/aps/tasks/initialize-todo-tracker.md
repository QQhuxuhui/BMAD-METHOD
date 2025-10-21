# Task: Initialize Todo Tracker

**任务ID**: `initialize-todo-tracker`
**版本**: V4.3
**用途**: Phase 0.4 - 初始化Todo追踪器，建立执行基线

## 输入

```yaml
inputs:
  - confirmed_todo_list: 用户确认后的Todo List
```

## 处理逻辑

### 步骤1: 创建追踪器基线

```python
from datetime import datetime
import json

def create_tracker_baseline(confirmed_todo_list):
    """
    创建Todo追踪器的基线数据
    """
    baseline = {
        "created_at": datetime.now().isoformat(),
        "todo_list_hash": generate_hash(confirmed_todo_list),
        "total_tasks": count_total_tasks(confirmed_todo_list),
        "phases": extract_phases(confirmed_todo_list),
        "task_sequence": extract_task_sequence(confirmed_todo_list),
        "planned_deliverables": extract_deliverables(confirmed_todo_list),
        "estimated_timeline": confirmed_todo_list.get("estimated_timeline"),
        "status": "initialized"
    }

    return baseline

def generate_hash(todo_list):
    """生成Todo List的哈希值用于版本控制"""
    import hashlib
    content = json.dumps(todo_list, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()[:8]

def count_total_tasks(todo_list):
    """统计总任务数"""
    total = 0
    for phase in todo_list.get("todo_items", []):
        total += len(phase.get("tasks", []))
    return total

def extract_phases(todo_list):
    """提取Phase信息"""
    phases = []
    for phase in todo_list.get("todo_items", []):
        phases.append({
            "phase_id": phase["phase"],
            "phase_name": phase["phase_name"],
            "task_count": len(phase.get("tasks", [])),
            "estimated_time": phase.get("estimated_time")
        })
    return phases

def extract_task_sequence(todo_list):
    """提取任务执行序列"""
    sequence = []
    for phase in todo_list.get("todo_items", []):
        for task in phase.get("tasks", []):
            sequence.append({
                "phase": phase["phase"],
                "task_id": task["task_id"],
                "task_name": task["task_name"],
                "dependencies": task.get("dependencies", [])
            })
    return sequence

def extract_deliverables(todo_list):
    """提取计划交付物"""
    deliverables = []
    for phase in todo_list.get("todo_items", []):
        for task in phase.get("tasks", []):
            if "deliverable" in task.get("task_name", "").lower():
                deliverables.append(task["task_name"])
    return deliverables
```

### 步骤2: 初始化状态追踪

```python
def initialize_status_tracking(baseline):
    """
    初始化状态追踪结构
    """
    tracking = {
        "baseline_hash": baseline["todo_list_hash"],
        "current_phase": "phase-0",
        "completed_tasks": [],
        "in_progress_tasks": [],
        "pending_tasks": [task["task_id"] for task in baseline["task_sequence"]],
        "deviation_events": [],
        "milestone_timestamps": {
            "initialized": datetime.now().isoformat()
        }
    }

    return tracking
```

### 步骤3: 设置偏离检测参数

```python
def setup_deviation_detection(baseline):
    """
    设置偏离检测参数
    """
    deviation_config = {
        "similarity_threshold": 0.60,  # 相似度低于0.60触发偏离警告
        "check_frequency": "per_phase",  # 每个Phase结束时检查
        "baseline_features": {
            "task_sequence": baseline["task_sequence"],
            "planned_deliverables": baseline["planned_deliverables"],
            "phase_coverage": [p["phase_id"] for p in baseline["phases"]]
        },
        "alert_triggers": {
            "task_skipped": True,
            "new_task_added": True,
            "sequence_changed": True,
            "deliverable_missing": True
        }
    }

    return deviation_config
```

### 步骤4: 创建追踪器实例

```python
def create_tracker_instance(baseline, tracking, deviation_config):
    """
    创建完整的追踪器实例
    """
    tracker = {
        "tracker_id": f"tracker_{baseline['todo_list_hash']}",
        "baseline": baseline,
        "tracking": tracking,
        "deviation_config": deviation_config,
        "metadata": {
            "version": "4.3",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    }

    return tracker
```

## 输出

```yaml
outputs:
  tracker_initialized:
    type: object
    structure:
      tracker_id: string
      baseline:
        created_at: string
        todo_list_hash: string
        total_tasks: integer
        phases: array
        task_sequence: array
        planned_deliverables: array
        estimated_timeline: object
        status: string
      tracking:
        baseline_hash: string
        current_phase: string
        completed_tasks: array
        in_progress_tasks: array
        pending_tasks: array
        deviation_events: array
        milestone_timestamps: object
      deviation_config:
        similarity_threshold: float
        check_frequency: string
        baseline_features: object
        alert_triggers: object
      metadata:
        version: string
        created_at: string
        last_updated: string

  baseline_contract:
    type: object
    description: "执行合同基线（供偏离检测使用）"
```

## 示例输出

```json
{
  "tracker_initialized": {
    "tracker_id": "tracker_a3f8c9d2",
    "baseline": {
      "created_at": "2025-10-21T16:30:00",
      "todo_list_hash": "a3f8c9d2",
      "total_tasks": 28,
      "phases": [
        {
          "phase_id": "phase-0",
          "phase_name": "Phase 0: 任务规划",
          "task_count": 4,
          "estimated_time": "5-8分钟"
        }
      ],
      "task_sequence": [
        {
          "phase": "phase-0",
          "task_id": "task-0.1",
          "task_name": "需求理解与初步分析",
          "dependencies": []
        }
      ],
      "planned_deliverables": [
        "TenElementModel",
        "完整代码",
        "质量报告"
      ],
      "estimated_timeline": {
        "mode_a": "70-95分钟",
        "mode_b": "95-130分钟"
      },
      "status": "initialized"
    },
    "tracking": {
      "baseline_hash": "a3f8c9d2",
      "current_phase": "phase-0",
      "completed_tasks": [],
      "in_progress_tasks": [],
      "pending_tasks": ["task-0.1", "task-0.2", "..."],
      "deviation_events": [],
      "milestone_timestamps": {
        "initialized": "2025-10-21T16:30:00"
      }
    },
    "deviation_config": {
      "similarity_threshold": 0.60,
      "check_frequency": "per_phase",
      "baseline_features": {
        "task_sequence": [...],
        "planned_deliverables": [...],
        "phase_coverage": ["phase-0", "phase-0.5", "..."]
      },
      "alert_triggers": {
        "task_skipped": true,
        "new_task_added": true,
        "sequence_changed": true,
        "deliverable_missing": true
      }
    },
    "metadata": {
      "version": "4.3",
      "created_at": "2025-10-21T16:30:00",
      "last_updated": "2025-10-21T16:30:00"
    }
  },
  "baseline_contract": {
    "hash": "a3f8c9d2",
    "total_tasks": 28,
    "created_at": "2025-10-21T16:30:00"
  }
}
```

## 质量检查

- [ ] 基线数据完整
- [ ] 哈希值正确生成
- [ ] 任务序列提取完整
- [ ] 偏离检测参数合理
- [ ] 追踪器结构正确

## 引用

- @编排协调专家库/Todo追踪机制
- V4.3架构规范: TodoTracker设计
- @任务管理规范/偏离检测标准

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: TodoTracker初始化，建立执行合同基线
