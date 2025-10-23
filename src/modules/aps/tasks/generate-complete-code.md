# Task: Generate Complete Code

**任务ID**: `generate-complete-code`
**版本**: V4.3
**用途**: Phase 3 - 生成完整可执行代码并强制保存到输出目录

## 输入

```yaml
inputs:
  - integrated_solution: 集成后的解决方案（包含所有专家建议）
  - ten_element_model: TenElementModel基线
  - output_folder: 输出目录路径（从config.yaml加载）
  - models_folder: 模型子目录名称
  - docs_folder: 文档子目录名称
```

## 🚨 强制要求（MANDATORY）

### 1. 必须保存到指定目录

```yaml
mandatory_save_requirement:
  critical: true
  blocking: true
  description: '所有生成的代码文件MUST保存到{output_folder}目录，不得仅输出到终端'

save_locations:
  complete_code:
    path: '{output_folder}/{models_folder}/scheduling_solution_{timestamp}.py'
    required: true

  ten_element_model_export:
    path: '{output_folder}/{models_folder}/ten_element_model_{timestamp}.yaml'
    required: true

  code_documentation:
    path: '{output_folder}/docs/solution_documentation_{timestamp}.md'
    required: true

  readme:
    path: '{output_folder}/README.md'
    required: true
```

### 1.1 IDE 工具调用指令（跨 IDE 兼容）

**🚨 CRITICAL - 文件保存方法**：

不同 IDE 中，AI 必须使用 IDE 提供的**文件写入工具**来保存文件，而不是输出 Python 代码示例。

**指令**：

1. **Claude Code/Cursor/Windsurf/其他 IDE**: 使用 `Write` 工具保存文件
2. **文件路径**: 必须使用完整的绝对路径或项目相对路径
3. **保存顺序**: 按照以下顺序逐个保存，每保存一个文件后验证成功

**示例（伪代码，实际使用 IDE 工具）**：

```
Tool: Write
Path: {project-root}/{output_folder}/models/scheduling_solution_{timestamp}.py
Content: [生成的完整代码]

Tool: Write
Path: {project-root}/{output_folder}/models/ten_element_model_{timestamp}.yaml
Content: [TenElementModel YAML 导出]

Tool: Write
Path: {project-root}/{output_folder}/docs/solution_documentation_{timestamp}.md
Content: [使用文档]
```

**验证**：每个文件保存后，确认以下信息：

- ✓ 文件路径
- ✓ 文件大小 > 最小要求
- ✓ 文件可访问

### 2. 文件命名规范

```python
# 使用时间戳确保可追溯性
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

file_naming_convention = {
    "code_file": f"scheduling_solution_{timestamp}.py",
    "model_file": f"ten_element_model_{timestamp}.yaml",
    "doc_file": f"solution_documentation_{timestamp}.md"
}
```

### 3. 保存后验证

```python
import os

def verify_file_saved(file_path, min_size=100):
    """
    验证文件已成功保存

    Args:
        file_path: 文件路径
        min_size: 最小文件大小（bytes）

    Returns:
        bool: 文件是否有效保存
    """
    if not os.path.exists(file_path):
        return False

    if not os.path.isfile(file_path):
        return False

    if os.path.getsize(file_path) < min_size:
        return False

    # 验证文件可读
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            _ = f.read(1)
        return True
    except Exception:
        return False
```

## 处理逻辑

### 步骤1: 准备输出目录结构

```python
import os
from pathlib import Path

def prepare_output_directories(output_folder):
    """
    创建输出目录结构
    """
    base_path = Path(output_folder)

    directories = [
        base_path,
        base_path / "models",
        base_path / "docs",
        base_path / "reports",
        base_path / "data"
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ 目录已创建/验证: {directory}")

    return {
        "base": str(base_path),
        "models": str(base_path / "models"),
        "docs": str(base_path / "docs"),
        "reports": str(base_path / "reports"),
        "data": str(base_path / "data")
    }
```

### 步骤2: 生成完整代码

从集成方案提取以下代码组件：

```yaml
code_components:
  imports:
    - 标准库导入
    - 第三方库导入
    - 自定义模块导入

  data_models:
    - 决策变量类定义
    - 参数类定义
    - 解决方案类定义

  constraints:
    - 约束验证函数
    - 约束修复函数（如有）

  objective_functions:
    - 主目标函数
    - 辅助目标函数（多目标情况）

  algorithm_implementation:
    - 算法主体代码
    - 算法参数配置
    - 邻域操作（如适用）

  main_solver:
    - 求解器入口函数
    - 数据加载
    - 结果输出

  utility_functions:
    - 日志记录
    - 性能统计
    - 结果可视化
```

### 步骤3: 保存所有文件（MANDATORY）

**🚨 CRITICAL INSTRUCTIONS - 文件保存执行步骤**：

此步骤必须实际执行文件保存操作，而非仅输出代码。所有 AI（Claude Code、Cursor、Windsurf 等）必须：

1. **使用 IDE 提供的 Write 工具**，不得使用 Python 代码示例替代
2. **按顺序保存**以下所有文件
3. **每保存一个文件后立即验证**文件已成功创建

#### 3.1 计算时间戳

```python
# 首先计算时间戳（用于文件命名）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# 例如: 20251022_143530
```

#### 3.2 使用 Write 工具保存文件

**文件 1: 完整代码**

```
IDE Tool: Write
File Path: {output_folder}/models/scheduling_solution_{timestamp}.py
Content: [生成的完整调度算法 Python 代码，包含：
  - 导入语句
  - 数据模型类
  - 约束验证函数
  - 目标函数
  - 算法主体
  - 求解器入口
  - 结果输出
]
```

**文件 2: TenElementModel 导出**

```
IDE Tool: Write
File Path: {output_folder}/models/ten_element_model_{timestamp}.yaml
Content: [TenElementModel 的完整 YAML 序列化，包含所有 10 个要素]
```

**文件 3: 代码文档**

```
IDE Tool: Write
File Path: {output_folder}/docs/solution_documentation_{timestamp}.md
Content: [使用说明文档，包含：
  - 问题概述
  - 环境要求
  - 安装步骤
  - 使用方法
  - 参数说明
  - 示例运行
]
```

**文件 4: README（如果不存在）**

```
IDE Tool: Write (仅当文件不存在时)
File Path: {output_folder}/README.md
Content: [项目总览、目录结构说明、快速开始指南]
```

**文件 5: 文件清单**

```
IDE Tool: Write
File Path: {output_folder}/file_manifest_{timestamp}.json
Content: {
  "timestamp": "{timestamp}",
  "files": {
    "complete_code": "{output_folder}/models/scheduling_solution_{timestamp}.py",
    "ten_element_model": "{output_folder}/models/ten_element_model_{timestamp}.yaml",
    "documentation": "{output_folder}/docs/solution_documentation_{timestamp}.md"
  },
  "ten_element_model_hash": "{model_hash}",
  "workflow_mode": "{mode}"
}
```

#### 3.3 保存后记录

保存每个文件后，向用户输出确认信息：

```
✓ 代码已保存: {output_folder}/models/scheduling_solution_{timestamp}.py (8432 bytes)
✓ 模型已保存: {output_folder}/models/ten_element_model_{timestamp}.yaml (3256 bytes)
✓ 文档已保存: {output_folder}/docs/solution_documentation_{timestamp}.md (5120 bytes)
✓ 清单已保存: {output_folder}/file_manifest_{timestamp}.json (512 bytes)
```

#### 3.4 构建 saved_files 数据结构

```python
saved_files = {
    "complete_code": f"{output_folder}/models/scheduling_solution_{timestamp}.py",
    "ten_element_model": f"{output_folder}/models/ten_element_model_{timestamp}.yaml",
    "documentation": f"{output_folder}/docs/solution_documentation_{timestamp}.md",
    "readme": f"{output_folder}/README.md",
    "manifest": f"{output_folder}/file_manifest_{timestamp}.json"
}
```

### 步骤4: 验证所有文件已保存（MANDATORY）

```python
def verify_all_files_saved(saved_files):
    """
    🚨 CRITICAL: 验证所有文件已成功保存
    此验证为质量门禁6的前置条件

    Returns:
        dict: 验证结果
    """
    verification_result = {
        "all_saved": True,
        "details": []
    }

    min_sizes = {
        "complete_code": 2048,
        "ten_element_model": 1024,
        "documentation": 512,
        "readme": 256,
        "manifest": 128
    }

    for file_type, file_path in saved_files.items():
        min_size = min_sizes.get(file_type, 100)
        is_valid = verify_file_saved(file_path, min_size)

        verification_result["details"].append({
            "file_type": file_type,
            "path": file_path,
            "valid": is_valid,
            "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "min_size_required": min_size
        })

        if not is_valid:
            verification_result["all_saved"] = False
            print(f"✗ 验证失败: {file_path}")
        else:
            print(f"✓ 验证通过: {file_path}")

    return verification_result
```

## 输出

```yaml
outputs:
  saved_files:
    type: object
    required: true
    structure:
      complete_code: '文件路径'
      ten_element_model: '文件路径'
      documentation: '文件路径'
      readme: '文件路径'
      manifest: '文件路径'

  verification_result:
    type: object
    required: true
    structure:
      all_saved: boolean
      details: array

  code_metadata:
    type: object
    structure:
      timestamp: string
      model_hash: string
      total_lines: integer
      file_size_bytes: integer
```

## 质量检查

- [ ] 输出目录结构已创建
- [ ] 所有文件已保存到指定位置
- [ ] 文件命名符合规范（包含时间戳）
- [ ] 所有文件已通过验证（大小、可读性）
- [ ] 代码包含完整引用（@citations）
- [ ] 文档清晰说明使用方式
- [ ] 文件清单（manifest）已生成

## 引用

- @算法专家库/代码生成模板
- @约束专家库/约束实现代码
- @目标专家库/目标函数实现
- @编排协调专家库/代码集成规范
- @质量评测专家库/代码验证标准
- @输出管理规范/文件保存要求

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 强制文件保存 + 验证，确保交付物持久化
