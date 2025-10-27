# Task: Check Execution Status

**任务ID**: `check-execution-status`
**版本**: V4.3
**用途**: 检查当前执行状态，识别任务中断位置，提供恢复建议

## 输入

```yaml
inputs:
  - state_folder: 状态文件目录路径（默认: aps-outputs/states）
```

## 功能说明

当用户任务中断或忘记执行位置时，通过扫描状态文件识别：

- 已完成哪些Phase
- 最后完成的Phase是什么
- 下一步应该执行什么
- 提供恢复建议

## 处理逻辑

### 步骤1: 扫描状态文件目录

```python
import os
from pathlib import Path
import yaml
from datetime import datetime

def scan_state_files(state_folder="aps-outputs/states"):
    """
    扫描状态文件目录，识别已完成的Phase

    Returns:
        dict: 状态文件信息
    """
    state_path = Path(state_folder)

    if not state_path.exists():
        return {
            "exists": False,
            "message": f"状态目录不存在: {state_folder}",
            "suggestion": "尚未执行任何Phase，请运行 start-scheduling 开始"
        }

    # 查找所有_latest.yaml文件
    latest_files = list(state_path.glob("*_state_latest.yaml"))

    # 读取manifest文件
    manifest_path = state_path / "phase_state_manifest.json"
    manifest = {}
    if manifest_path.exists():
        import json
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

    return {
        "exists": True,
        "state_folder": str(state_path),
        "latest_files": latest_files,
        "manifest": manifest
    }
```

### 步骤2: 解析Phase完成状态

```python
def parse_phase_status(scan_result):
    """
    解析各Phase的完成状态

    Returns:
        dict: Phase状态字典
    """
    if not scan_result["exists"]:
        return {"completed_phases": [], "last_phase": None}

    phase_order = [
        "phase_0",
        "phase_0_5",
        "phase_1",
        "phase_1_5",
        "phase_2",
        "phase_3"
    ]

    completed_phases = []
    phase_details = {}

    # 从manifest获取详细信息
    manifest = scan_result.get("manifest", {})
    phases_info = manifest.get("phases", {})

    for phase_id in phase_order:
        phase_file = Path(scan_result["state_folder"]) / f"{phase_id}_state_latest.yaml"

        if phase_file.exists():
            # 读取状态文件获取时间戳
            try:
                with open(phase_file, 'r') as f:
                    state_data = yaml.safe_load(f)
                    metadata = state_data.get("metadata", {})
                    timestamp = metadata.get("timestamp", "Unknown")
            except:
                timestamp = "Unknown"

            completed_phases.append(phase_id)
            phase_details[phase_id] = {
                "completed": True,
                "file": str(phase_file),
                "timestamp": timestamp,
                "manifest_info": phases_info.get(phase_id, {})
            }
        else:
            phase_details[phase_id] = {
                "completed": False
            }

    # 确定最后完成的Phase
    last_phase = completed_phases[-1] if completed_phases else None

    return {
        "completed_phases": completed_phases,
        "last_phase": last_phase,
        "phase_details": phase_details,
        "total_completed": len(completed_phases)
    }
```

### 步骤3: 检查方案文件

```python
def check_solution_files(state_folder="aps-outputs"):
    """
    检查是否有方案文件生成

    Returns:
        dict: 方案文件状态
    """
    docs_path = Path(state_folder) / "docs"

    solution_files = {
        "has_solution_document": False,
        "has_solution_data": False,
        "solution_files": []
    }

    if not docs_path.exists():
        return solution_files

    # 查找方案文档
    md_files = list(docs_path.glob("solution_document_*.md"))
    yaml_files = list(docs_path.glob("solution_data_*.yaml"))

    if md_files:
        solution_files["has_solution_document"] = True
        solution_files["solution_document"] = str(md_files[-1])  # 最新的

    if yaml_files:
        solution_files["has_solution_data"] = True
        solution_files["solution_data"] = str(yaml_files[-1])  # 最新的

    solution_files["solution_files"] = [str(f) for f in md_files + yaml_files]

    return solution_files
```

### 步骤4: 生成恢复建议

```python
def generate_recovery_suggestions(phase_status, solution_files):
    """
    基于当前状态生成恢复建议

    Returns:
        dict: 恢复建议
    """
    last_phase = phase_status["last_phase"]
    completed = phase_status["completed_phases"]

    suggestions = {
        "primary_suggestion": "",
        "alternative_suggestions": [],
        "next_phase": None
    }

    # 如果有方案文件
    if solution_files["has_solution_data"]:
        suggestions["primary_suggestion"] = "发现方案文件，可以直接生成代码"
        suggestions["primary_action"] = {
            "command": "generate-code",
            "input": solution_files["solution_data"],
            "description": "基于已有方案YAML独立生成代码"
        }
        suggestions["alternative_suggestions"].append({
            "action": "继续完整流程",
            "command": "resume",
            "description": "从Phase 3.4用户确认方案继续"
        })

    # 根据最后完成的Phase建议
    elif last_phase == "phase_2":
        suggestions["primary_suggestion"] = "Phase 2已完成，建议从Phase 3开始"
        suggestions["next_phase"] = "Phase 3"
        suggestions["primary_action"] = {
            "command": "resume",
            "description": "智能恢复，自动从Phase 3开始"
        }

    elif last_phase == "phase_1_5":
        suggestions["primary_suggestion"] = "TenElementModel已生成，建议从Phase 2开始"
        suggestions["next_phase"] = "Phase 2"
        suggestions["primary_action"] = {
            "command": "resume",
            "description": "智能恢复，自动从Phase 2开始"
        }

    elif last_phase == "phase_1":
        suggestions["primary_suggestion"] = "需求分析已完成，建议从Phase 1.5开始"
        suggestions["next_phase"] = "Phase 1.5"
        suggestions["primary_action"] = {
            "command": "resume"
        }

    elif last_phase == "phase_0" or last_phase == "phase_0_5":
        suggestions["primary_suggestion"] = "初始化已完成，建议从Phase 1开始"
        suggestions["next_phase"] = "Phase 1"
        suggestions["primary_action"] = {
            "command": "resume"
        }

    elif not completed:
        suggestions["primary_suggestion"] = "未发现任何已完成的Phase，建议启动完整流程"
        suggestions["primary_action"] = {
            "command": "start-scheduling",
            "description": "从Phase 0开始完整流程"
        }

    return suggestions
```

### 步骤5: 生成状态报告

```python
def generate_status_report(phase_status, solution_files, suggestions):
    """
    生成完整的状态报告

    Returns:
        str: 格式化的状态报告
    """
    report = []

    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("当前执行状态")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("")

    # Phase状态
    phase_names = {
        "phase_0": "Phase 0: 任务规划",
        "phase_0_5": "Phase 0.5: 交互模式选择",
        "phase_1": "Phase 1: 需求分析",
        "phase_1_5": "Phase 1.5: 十要素建模",
        "phase_2": "Phase 2: 专家协调",
        "phase_3": "Phase 3: 方案集成与代码生成"
    }

    for phase_id in ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2", "phase_3"]:
        phase_name = phase_names.get(phase_id, phase_id)
        detail = phase_status["phase_details"].get(phase_id, {})

        if detail.get("completed"):
            timestamp = detail.get("timestamp", "Unknown")
            report.append(f"✅ {phase_name}: 已完成")
            if timestamp != "Unknown":
                report.append(f"   └─ 时间: {timestamp}")

            # 特殊标注
            if phase_id == "phase_1_5":
                report.append("   └─ TenElementModel已生成")
            elif phase_id == "phase_2":
                report.append("   └─ 专家分析已完成")
        else:
            report.append(f"⏸️  {phase_name}: 未开始")

    report.append("")

    # 方案文件状态
    if solution_files["has_solution_document"] or solution_files["has_solution_data"]:
        report.append("生成的文件:")
        if solution_files["has_solution_document"]:
            report.append(f"  📄 方案文档: {os.path.basename(solution_files['solution_document'])}")
        if solution_files["has_solution_data"]:
            report.append(f"  📊 方案数据: {os.path.basename(solution_files['solution_data'])}")
        report.append("")

    # 恢复建议
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("恢复建议")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("")

    last_phase = phase_status["last_phase"]
    if last_phase:
        report.append(f"最后完成: {phase_names.get(last_phase, last_phase)}")

    report.append(f"建议: {suggestions['primary_suggestion']}")

    if suggestions.get("primary_action"):
        action = suggestions["primary_action"]
        report.append(f"执行命令: *{action['command']}")
        if action.get("description"):
            report.append(f"说明: {action['description']}")

    if suggestions.get("alternative_suggestions"):
        report.append("")
        report.append("其他选项:")
        for alt in suggestions["alternative_suggestions"]:
            report.append(f"  • {alt['action']}: *{alt['command']}")

    report.append("")

    return "\n".join(report)
```

## 输出

```yaml
outputs:
  status_report:
    type: string
    description: 格式化的状态报告

  phase_status:
    type: object
    description: Phase完成状态
    structure:
      completed_phases: array
      last_phase: string
      total_completed: integer

  recovery_suggestions:
    type: object
    description: 恢复建议
    structure:
      primary_suggestion: string
      primary_action: object
      alternative_suggestions: array
      next_phase: string
```

## 使用示例

### 场景1: Phase 2完成后中断

```
输入: state_folder = "aps-outputs/states"

输出:
━━━━━━━━━━━━━━━━━━━━━━━━
当前执行状态
━━━━━━━━━━━━━━━━━━━━━━━━

✅ Phase 0: 任务规划: 已完成
✅ Phase 0.5: 交互模式选择: 已完成
✅ Phase 1: 需求分析: 已完成
✅ Phase 1.5: 十要素建模: 已完成
   └─ TenElementModel已生成
✅ Phase 2: 专家协调: 已完成
   └─ 专家分析已完成
⏸️  Phase 3: 方案集成与代码生成: 未开始

━━━━━━━━━━━━━━━━━━━━━━━━
恢复建议
━━━━━━━━━━━━━━━━━━━━━━━━

最后完成: Phase 2: 专家协调
建议: Phase 2已完成，建议从Phase 3开始
执行命令: *resume
说明: 智能恢复，自动从Phase 3开始
```

### 场景2: 发现方案文件

```
输出:
━━━━━━━━━━━━━━━━━━━━━━━━
当前执行状态
━━━━━━━━━━━━━━━━━━━━━━━━

✅ Phase 0-2: 已完成
✅ Phase 3.1-3.3: 已完成

生成的文件:
  📄 方案文档: solution_document_20251024_143530.md
  📊 方案数据: solution_data_20251024_143530.yaml

━━━━━━━━━━━━━━━━━━━━━━━━
恢复建议
━━━━━━━━━━━━━━━━━━━━━━━━

建议: 发现方案文件，可以直接生成代码
执行命令: *generate-code
说明: 基于已有方案YAML独立生成代码

其他选项:
  • 继续完整流程: *resume
```

## 质量检查

- [ ] 状态目录扫描成功
- [ ] 识别所有已完成的Phase
- [ ] 正确识别最后完成的Phase
- [ ] 提供了恢复建议
- [ ] 建议的命令可执行

## 引用

- @编排协调专家库/状态管理
- phase_state_manifest.json

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 断点恢复的第一步 - 识别中断位置
