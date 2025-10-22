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

```python
from datetime import datetime
import yaml
import json

def save_all_deliverables(integrated_solution, ten_element_model, output_paths, timestamp):
    """
    🚨 CRITICAL: 保存所有交付物到指定目录
    此步骤为强制要求，不得跳过

    Returns:
        dict: 保存的文件路径清单
    """
    saved_files = {}

    # 1. 保存完整代码
    code_path = f"{output_paths['models']}/scheduling_solution_{timestamp}.py"
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(generate_complete_code(integrated_solution, ten_element_model))
    saved_files['complete_code'] = code_path
    print(f"✓ 代码已保存: {code_path}")

    # 2. 保存TenElementModel导出
    model_path = f"{output_paths['models']}/ten_element_model_{timestamp}.yaml"
    with open(model_path, 'w', encoding='utf-8') as f:
        yaml.dump(ten_element_model, f, allow_unicode=True, default_flow_style=False)
    saved_files['ten_element_model'] = model_path
    print(f"✓ 模型已保存: {model_path}")

    # 3. 保存代码文档
    doc_path = f"{output_paths['docs']}/solution_documentation_{timestamp}.md"
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(generate_documentation(integrated_solution, ten_element_model, timestamp))
    saved_files['documentation'] = doc_path
    print(f"✓ 文档已保存: {doc_path}")

    # 4. 生成README.md（如不存在）
    readme_path = f"{output_paths['base']}/README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(generate_readme(timestamp))
        saved_files['readme'] = readme_path
        print(f"✓ README已创建: {readme_path}")

    # 5. 保存文件清单元数据
    manifest_path = f"{output_paths['base']}/file_manifest_{timestamp}.json"
    manifest = {
        "timestamp": timestamp,
        "files": saved_files,
        "ten_element_model_hash": ten_element_model.get("model_hash"),
        "workflow_mode": ten_element_model.get("workflow_mode")
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    saved_files['manifest'] = manifest_path
    print(f"✓ 文件清单已保存: {manifest_path}")

    return saved_files
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
