# Task: Show Execution Progress

**任务ID**: `show-execution-progress`
**版本**: V4.3
**用途**: 显示Todo进度、Phase状态和生成文件的详细信息

## 输入

```yaml
inputs:
  - state_folder: 状态文件目录路径（默认: aps-outputs/states）
  - output_folder: 输出目录路径（默认: aps-outputs）
```

## 功能说明

提供全面的执行进度视图：

1. Todo List完成情况
2. 各Phase执行状态和时间
3. 已生成的文件清单
4. 状态文件链完整性

## 处理逻辑

### 步骤1: 加载Todo基线

```python
import yaml
from pathlib import Path

def load_todo_baseline(state_folder):
    """
    从Phase 0状态加载Todo基线

    Returns:
        dict: Todo基线信息
    """
    phase_0_file = Path(state_folder) / "phase_0_state_latest.yaml"

    if not phase_0_file.exists():
        return {
            "has_todo": False,
            "message": "未找到Todo基线（Phase 0未执行）"
        }

    with open(phase_0_file, 'r') as f:
        phase_0_state = yaml.safe_load(f)

    state_data = phase_0_state.get("state_data", {})
    confirmed_todo_list = state_data.get("confirmed_todo_list", [])

    return {
        "has_todo": True,
        "todo_list": confirmed_todo_list,
        "baseline_contract": state_data.get("baseline_contract", {})
    }
```

### 步骤2: 分析Phase执行状态

```python
from datetime import datetime

def analyze_phase_execution(state_folder):
    """
    分析各Phase的执行状态

    Returns:
        dict: Phase执行详情
    """
    state_path = Path(state_folder)

    phases = {
        "phase_0": {"name": "Phase 0: 任务规划", "time": "5-8分钟"},
        "phase_0_5": {"name": "Phase 0.5: 交互模式", "time": "2-3分钟"},
        "phase_1": {"name": "Phase 1: 需求分析", "time": "10-15分钟"},
        "phase_1_5": {"name": "Phase 1.5: 十要素建模", "time": "10-15分钟"},
        "phase_2": {"name": "Phase 2: 专家协调", "time": "20-40分钟"},
        "phase_3": {"name": "Phase 3: 方案与代码", "time": "20-30分钟"},
        "phase_4": {"name": "Phase 4: 质量保证", "time": "10-15分钟"}
    }

    phase_status = {}
    total_time_spent = 0

    for phase_id, info in phases.items():
        phase_file = state_path / f"{phase_id}_state_latest.yaml"

        if phase_file.exists():
            try:
                with open(phase_file, 'r') as f:
                    state = yaml.safe_load(f)
                    metadata = state.get("metadata", {})

                phase_status[phase_id] = {
                    "completed": True,
                    "name": info["name"],
                    "timestamp": metadata.get("timestamp", "Unknown"),
                    "file_size": phase_file.stat().st_size
                }
            except:
                phase_status[phase_id] = {
                    "completed": True,
                    "name": info["name"],
                    "error": "无法读取状态文件"
                }
        else:
            phase_status[phase_id] = {
                "completed": False,
                "name": info["name"],
                "estimated_time": info["time"]
            }

    return phase_status
```

### 步骤3: 列举生成的文件

```python
def list_generated_files(output_folder):
    """
    列举所有生成的文件

    Returns:
        dict: 文件清单
    """
    output_path = Path(output_folder)

    files = {
        "state_files": [],
        "solution_documents": [],
        "code_files": [],
        "model_files": [],
        "total_count": 0
    }

    # 状态文件
    states_path = output_path / "states"
    if states_path.exists():
        files["state_files"] = [
            {"name": f.name, "size": f.stat().st_size, "path": str(f)}
            for f in states_path.glob("*.yaml")
            if "_state_" in f.name
        ]

    # 方案文档
    docs_path = output_path / "docs"
    if docs_path.exists():
        files["solution_documents"] = [
            {"name": f.name, "size": f.stat().st_size, "path": str(f)}
            for f in docs_path.glob("solution_*.*")
        ]

    # 代码文件
    models_path = output_path / "models"
    if models_path.exists():
        files["code_files"] = [
            {"name": f.name, "size": f.stat().st_size, "path": str(f)}
            for f in models_path.glob("*.py")
        ]
        files["model_files"] = [
            {"name": f.name, "size": f.stat().st_size, "path": str(f)}
            for f in models_path.glob("*.yaml")
        ]

    files["total_count"] = (
        len(files["state_files"]) +
        len(files["solution_documents"]) +
        len(files["code_files"]) +
        len(files["model_files"])
    )

    return files
```

### 步骤4: 生成进度报告

```python
def generate_progress_report(todo_info, phase_status, generated_files):
    """
    生成完整的进度报告

    Returns:
        str: 格式化的进度报告
    """
    report = []

    report.append("╔══════════════════════════════════════════════════════════════╗")
    report.append("║             执行进度报告                                     ║")
    report.append("╚══════════════════════════════════════════════════════════════╝")
    report.append("")

    # Todo进度
    if todo_info["has_todo"]:
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append("Todo List状态")
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append("")

        for phase_group in todo_info["todo_list"]:
            phase_name = phase_group.get("phase", "Unknown")
            tasks = phase_group.get("tasks", [])
            report.append(f"[{phase_name}]")
            for task in tasks:
                report.append(f"  • {task}")
            report.append("")

    # Phase执行状态
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("Phase执行状态")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("")

    completed_count = 0
    for phase_id in ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2", "phase_3", "phase_4"]:
        if phase_id in phase_status:
            status = phase_status[phase_id]
            if status["completed"]:
                completed_count += 1
                ts = status.get("timestamp", "Unknown")
                report.append(f"✅ {status['name']}: 已完成")
                if ts != "Unknown":
                    report.append(f"   └─ 时间: {ts}")
            else:
                report.append(f"⏸️  {status['name']}: 未开始")
                report.append(f"   └─ 预计耗时: {status.get('estimated_time', 'N/A')}")

    report.append("")
    report.append(f"已完成: {completed_count}/7 Phase")
    report.append("")

    # 生成的文件
    if generated_files["total_count"] > 0:
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append("生成的文件")
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append("")

        if generated_files["solution_documents"]:
            report.append("方案文档:")
            for f in generated_files["solution_documents"]:
                size_kb = f["size"] / 1024
                report.append(f"  📄 {f['name']} ({size_kb:.1f} KB)")

        if generated_files["code_files"]:
            report.append("\n代码文件:")
            for f in generated_files["code_files"]:
                size_kb = f["size"] / 1024
                report.append(f"  💻 {f['name']} ({size_kb:.1f} KB)")

        if generated_files["model_files"]:
            report.append("\n模型文件:")
            for f in generated_files["model_files"]:
                size_kb = f["size"] / 1024
                report.append(f"  📊 {f['name']} ({size_kb:.1f} KB)")

        report.append("")
        report.append(f"总计: {generated_files['total_count']} 个文件")
        report.append("")

    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(report)
```

## 输出

```yaml
outputs:
  progress_report:
    type: string
    description: 格式化的进度报告

  todo_status:
    type: object
    description: Todo完成状态

  phase_execution_status:
    type: object
    description: 各Phase执行状态

  generated_files_list:
    type: object
    description: 生成的文件清单
```

## 质量检查

- [ ] Todo List显示完整
- [ ] 所有Phase状态准确
- [ ] 生成文件列举完整
- [ ] 报告格式清晰易读
- [ ] 包含时间信息

## 引用

- phase_0_state.yaml（Todo基线）
- phase_state_manifest.json（状态清单）

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 全面的进度展示，帮助用户了解执行情况
