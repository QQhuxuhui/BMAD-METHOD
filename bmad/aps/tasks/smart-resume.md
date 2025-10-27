# Task: Smart Resume

**任务ID**: `smart-resume`
**版本**: V4.3
**用途**: 智能恢复任务执行，自动检测最后完成的Phase并从断点继续

## 输入

```yaml
inputs:
  - state_folder: 状态文件目录路径（默认: aps-outputs/states）
```

## 功能说明

当用户任务中断后，自动：

1. 检测最后完成的Phase
2. 加载相应的状态文件
3. 从下一个Phase继续执行
4. 如果有方案文件，提供快速代码生成选项

## 处理逻辑

### 步骤1: 检测恢复点

```python
import os
from pathlib import Path

def detect_resume_point(state_folder="aps-outputs/states"):
    """
    检测应该从哪个Phase恢复

    Returns:
        dict: 恢复点信息
    """
    state_path = Path(state_folder)

    # Phase检测顺序（从后往前）
    phase_detection_order = [
        ("phase_3", "Phase 3", "phase_3_state_latest.yaml"),
        ("phase_2", "Phase 2", "phase_2_state_latest.yaml"),
        ("phase_1_5", "Phase 1.5", "phase_1_5_state_latest.yaml"),
        ("phase_1", "Phase 1", "phase_1_state_latest.yaml"),
        ("phase_0_5", "Phase 0.5", "phase_0_5_state_latest.yaml"),
        ("phase_0", "Phase 0", "phase_0_state_latest.yaml")
    ]

    last_completed = None
    next_phase = None

    for phase_id, phase_name, filename in phase_detection_order:
        phase_file = state_path / filename
        if phase_file.exists():
            last_completed = {
                "phase_id": phase_id,
                "phase_name": phase_name,
                "state_file": str(phase_file)
            }

            # 确定下一个Phase
            if phase_id == "phase_0":
                next_phase = {"id": "phase_0_5", "name": "Phase 0.5"}
            elif phase_id == "phase_0_5":
                next_phase = {"id": "phase_1", "name": "Phase 1"}
            elif phase_id == "phase_1":
                next_phase = {"id": "phase_1_5", "name": "Phase 1.5"}
            elif phase_id == "phase_1_5":
                next_phase = {"id": "phase_2", "name": "Phase 2"}
            elif phase_id == "phase_2":
                next_phase = {"id": "phase_3", "name": "Phase 3"}
            elif phase_id == "phase_3":
                next_phase = {"id": "phase_4", "name": "Phase 4"}

            break

    return {
        "last_completed": last_completed,
        "next_phase": next_phase,
        "has_checkpoint": last_completed is not None
    }
```

### 步骤2: 检查方案文件

```python
def check_for_solution_files(state_folder="aps-outputs"):
    """
    检查是否存在可用的方案文件

    Returns:
        dict: 方案文件信息
    """
    docs_path = Path(state_folder) / "docs"

    result = {
        "has_solution_data": False,
        "solution_data_path": None,
        "can_generate_code_directly": False
    }

    if not docs_path.exists():
        return result

    # 查找最新的solution_data.yaml
    yaml_files = sorted(docs_path.glob("solution_data_*.yaml"), reverse=True)

    if yaml_files:
        result["has_solution_data"] = True
        result["solution_data_path"] = str(yaml_files[0])
        result["can_generate_code_directly"] = True

        print(f"✓ 发现方案文件: {yaml_files[0].name}")

    return result
```

### 步骤3: 生成恢复计划

```python
def generate_resume_plan(resume_point, solution_files):
    """
    生成智能恢复计划

    Returns:
        dict: 恢复计划
    """
    plan = {
        "resume_strategy": "",
        "resume_from": "",
        "actions": [],
        "estimated_time": ""
    }

    # 策略1: 如果有方案文件，提供快速代码生成
    if solution_files["can_generate_code_directly"]:
        plan["resume_strategy"] = "fast_code_generation"
        plan["resume_from"] = "solution_data.yaml"
        plan["actions"] = [
            {
                "step": 1,
                "action": "加载方案数据",
                "file": solution_files["solution_data_path"]
            },
            {
                "step": 2,
                "action": "生成代码",
                "task": "generate-code-from-yaml.md"
            },
            {
                "step": 3,
                "action": "保存交付物"
            }
        ]
        plan["estimated_time"] = "5-10分钟"

        print("✓ 恢复策略: 快速代码生成")
        return plan

    # 策略2: 从检测到的断点恢复
    if resume_point["has_checkpoint"]:
        last = resume_point["last_completed"]
        next_phase = resume_point["next_phase"]

        plan["resume_strategy"] = "phase_continuation"
        plan["resume_from"] = next_phase["name"]
        plan["actions"] = [
            {
                "step": 1,
                "action": f"加载{last['phase_name']}状态",
                "file": last["state_file"]
            },
            {
                "step": 2,
                "action": f"从{next_phase['name']}继续执行",
                "workflow": "scheduling-orchestration/workflow.yaml"
            }
        ]

        # 估算剩余时间
        time_estimates = {
            "phase_1": "10-15分钟",
            "phase_1_5": "10-15分钟",
            "phase_2": "20-40分钟",
            "phase_3": "20-30分钟",
            "phase_4": "10-15分钟"
        }
        plan["estimated_time"] = time_estimates.get(next_phase["id"], "未知")

        print(f"✓ 恢复策略: 从{next_phase['name']}继续")
        return plan

    # 策略3: 从头开始
    plan["resume_strategy"] = "start_from_beginning"
    plan["resume_from"] = "Phase 0"
    plan["actions"] = [
        {
            "step": 1,
            "action": "启动完整流程",
            "workflow": "scheduling-orchestration/workflow.yaml"
        }
    ]
    plan["estimated_time"] = "70-130分钟"

    print("✓ 恢复策略: 从头开始")
    return plan
```

### 步骤4: 执行恢复

```python
def execute_resume(plan):
    """
    执行恢复计划

    这个函数会根据plan调用相应的workflow或task
    """
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    print("开始恢复执行")
    print("━━━━━━━━━━━━━━━━━━━━━━━━\n")

    print(f"恢复策略: {plan['resume_strategy']}")
    print(f"恢复点: {plan['resume_from']}")
    print(f"预计耗时: {plan['estimated_time']}\n")

    print("执行步骤:")
    for action in plan["actions"]:
        print(f"  {action['step']}. {action['action']}")
        if action.get("file"):
            print(f"     文件: {action['file']}")
        if action.get("task"):
            print(f"     任务: {action['task']}")
        if action.get("workflow"):
            print(f"     工作流: {action['workflow']}")

    print("\n准备执行...")

    # 根据策略执行
    if plan["resume_strategy"] == "fast_code_generation":
        print("\n提示: 请执行命令 *generate-code")
        print(f"或手动调用: generate-code-from-yaml.md")
        print(f"输入文件: {plan['actions'][0]['file']}")

    elif plan["resume_strategy"] == "phase_continuation":
        print("\n提示: 继续执行主workflow")
        print("workflow会自动:")
        print("  • 加载所需的状态文件")
        print("  • 跳过已完成的Phase")
        print(f"  • 从{plan['resume_from']}开始执行")

    elif plan["resume_strategy"] == "start_from_beginning":
        print("\n提示: 请执行命令 *start-scheduling")
        print("这将启动完整的Phase 0-4流程")

    return {
        "status": "ready",
        "plan": plan
    }
```

## 输出

```yaml
outputs:
  resume_point:
    type: object
    description: 检测到的恢复点
    structure:
      last_completed: object
      next_phase: object
      has_checkpoint: boolean

  resume_plan:
    type: object
    description: 恢复计划
    structure:
      resume_strategy: string
      resume_from: string
      actions: array
      estimated_time: string

  execution_status:
    type: object
    description: 执行状态
    structure:
      status: string
      plan: object
```

## 恢复策略

### 策略1: 快速代码生成

```
条件: 发现 solution_data.yaml
动作:
  1. 加载方案YAML
  2. 调用 generate-code-from-yaml.md
  3. 生成代码

优势: 跳过Phase 3.4确认，最快
耗时: 5-10分钟
```

### 策略2: Phase续接

```
条件: 有Phase N的状态文件
动作:
  1. 加载 phase_N_state.yaml
  2. 从Phase N+1继续workflow

优势: 无缝继续，数据完整
耗时: 根据剩余Phase（10-40分钟）
```

### 策略3: 从头开始

```
条件: 没有任何状态文件
动作: 启动完整流程
耗时: 70-130分钟
```

## 使用示例

### 场景1: Phase 2完成后中断

```
检测:
  last_completed: Phase 2
  next_phase: Phase 3

恢复计划:
  策略: phase_continuation
  恢复点: Phase 3
  步骤:
    1. 加载 phase_2_state.yaml
    2. 从Phase 3继续执行

  预计耗时: 20-30分钟
```

### 场景2: 方案已生成

```
检测:
  发现: solution_data_20251024_143530.yaml

恢复计划:
  策略: fast_code_generation
  恢复点: solution_data.yaml
  步骤:
    1. 加载方案数据
    2. 生成代码（generate-code-from-yaml.md）
    3. 保存交付物

  预计耗时: 5-10分钟

  提示: 这是最快的恢复方式！
```

## 质量检查

- [ ] 正确检测最后完成的Phase
- [ ] 正确识别下一个Phase
- [ ] 检测到方案文件
- [ ] 生成合理的恢复计划
- [ ] 提供时间估算
- [ ] 给出明确的执行指引

## 引用

- check-execution-status.md（检测状态）
- generate-code-from-yaml.md（快速代码生成）
- @编排协调专家库/恢复策略

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 断点恢复的核心 - 智能恢复执行
