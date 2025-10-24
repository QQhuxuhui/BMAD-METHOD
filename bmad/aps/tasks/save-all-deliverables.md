# Task: Save All Deliverables

**任务ID**: `save-all-deliverables`
**版本**: V4.3
**用途**: Phase 3 Step 3.6 - 统一保存所有交付物到输出目录

## 输入

```yaml
inputs:
  - implementation_code: 生成的代码
  - solution_document_path: 方案文档路径（已保存）
  - ten_element_model: TenElementModel对象
  - code_traceability: 代码可追溯性映射
  - output_folder: 输出目录路径
  - models_folder: 模型子目录名称
  - docs_folder: 文档子目录名称
```

## 🚨 强制要求（MANDATORY）

### 1. 必须使用IDE的Write工具

**CRITICAL**: 此任务执行时，AI必须实际调用IDE提供的Write工具来保存文件，而不是仅输出内容示例。

```
适用于所有IDE:
- Claude Code: 使用 Write 工具
- Cursor: 使用 Write 工具
- Windsurf: 使用 Write 工具
```

### 2. 所有交付物必须保存

必须保存以下所有文件：

```yaml
required_deliverables:
  - complete_code:
      path: '{output_folder}/models/scheduling_solution_{timestamp}.py'
      min_size: 2048 bytes
      critical: true

  - ten_element_model_export:
      path: '{output_folder}/models/ten_element_model_{timestamp}.yaml'
      min_size: 1024 bytes
      critical: true

  - code_traceability:
      path: '{output_folder}/models/code_traceability_{timestamp}.yaml'
      min_size: 512 bytes
      critical: true

  - code_documentation:
      path: '{output_folder}/docs/code_documentation_{timestamp}.md'
      min_size: 1024 bytes
      critical: true

  - deliverable_manifest:
      path: '{output_folder}/deliverable_manifest_{timestamp}.json'
      min_size: 256 bytes
      critical: true

  - readme:
      path: '{output_folder}/README.md'
      min_size: 512 bytes
      critical: false # 如果已存在则不覆盖
```

### 3. 保存后必须验证

每个文件保存后，必须验证：

- ✓ 文件已创建
- ✓ 文件大小 >= 最小阈值
- ✓ 文件可读取
- ✓ 格式正确（Python/YAML/Markdown/JSON）

验证失败则抛出错误，阻断流程。

## 处理逻辑

### 步骤1: 准备输出目录结构

```python
import os
from pathlib import Path

def prepare_output_directories(output_folder, models_folder, docs_folder):
    """
    创建完整的输出目录结构

    Returns:
        dict: 目录路径信息
    """
    base_path = Path(output_folder)

    directories = {
        "base": base_path,
        "models": base_path / models_folder,
        "docs": base_path / docs_folder,
        "reports": base_path / "reports",
        "data": base_path / "data"
    }

    # 创建所有目录
    for dir_name, dir_path in directories.items():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ 目录已准备: {dir_path}")

    # 转换为字符串路径
    return {k: str(v) for k, v in directories.items()}
```

### 步骤2: 生成文件名

```python
from datetime import datetime

def generate_filenames(timestamp=None):
    """
    生成所有交付物的文件名

    Returns:
        dict: 文件名映射
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filenames = {
        "complete_code": f"scheduling_solution_{timestamp}.py",
        "ten_element_model_export": f"ten_element_model_{timestamp}.yaml",
        "code_traceability": f"code_traceability_{timestamp}.yaml",
        "code_documentation": f"code_documentation_{timestamp}.md",
        "deliverable_manifest": f"deliverable_manifest_{timestamp}.json",
        "readme": "README.md"
    }

    print(f"✓ 时间戳: {timestamp}")
    return filenames, timestamp
```

### 步骤3: 导出TenElementModel为YAML

```python
import yaml

def export_ten_element_model(ten_element_model):
    """
    将TenElementModel导出为YAML格式

    Returns:
        str: YAML内容
    """
    yaml_content = yaml.dump(
        ten_element_model,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

    print("✓ TenElementModel已导出为YAML")
    return yaml_content
```

### 步骤4: 导出代码可追溯性为YAML

```python
def export_code_traceability(code_traceability):
    """
    将代码可追溯性映射导出为YAML格式

    Returns:
        str: YAML内容
    """
    yaml_content = yaml.dump(
        code_traceability,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

    print("✓ 代码可追溯性已导出为YAML")
    return yaml_content
```

### 步骤5: 生成代码文档

````python
def generate_code_documentation(
    implementation_code,
    solution_document_path,
    code_traceability,
    timestamp
):
    """
    生成代码使用文档

    Returns:
        str: Markdown文档内容
    """
    from datetime import datetime

    doc_lines = []

    # 文档头部
    doc_lines.append("# 调度优化求解器 - 使用文档\n")
    doc_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    doc_lines.append(f"**版本**: v1.0-{timestamp}\n")
    doc_lines.append("\n---\n\n")

    # 概述
    doc_lines.append("## 📋 概述\n\n")
    doc_lines.append("本求解器根据调度优化方案自动生成，用于求解特定的调度问题。\n\n")
    doc_lines.append(f"- **方案文档**: `{solution_document_path}`\n")
    doc_lines.append(f"- **算法**: {code_traceability['mappings']['algorithm_core']['algorithm']}\n")
    doc_lines.append(f"- **生成时间**: {timestamp}\n\n")

    # 环境要求
    doc_lines.append("## 🛠️ 环境要求\n\n")
    doc_lines.append("- **Python版本**: 3.8+\n")
    doc_lines.append("- **依赖库**:\n")
    doc_lines.append("  ```bash\n")
    doc_lines.append("  pip install pyyaml\n")
    doc_lines.append("  # 根据算法可能还需要: numpy, scipy等\n")
    doc_lines.append("  ```\n\n")

    # 快速开始
    doc_lines.append("## 🚀 快速开始\n\n")
    doc_lines.append("### 1. 准备输入数据\n\n")
    doc_lines.append("根据TenElementModel的定义准备输入数据（JSON格式）：\n\n")
    doc_lines.append("```json\n")
    doc_lines.append("{\n")
    doc_lines.append('  "tasks": [...],\n')
    doc_lines.append('  "resources": [...],\n')
    doc_lines.append('  "parameters": {...}\n')
    doc_lines.append("}\n")
    doc_lines.append("```\n\n")

    doc_lines.append("### 2. 运行求解器\n\n")
    doc_lines.append("```bash\n")
    doc_lines.append(f"python scheduling_solution_{timestamp}.py\n")
    doc_lines.append("```\n\n")

    doc_lines.append("或在代码中调用：\n\n")
    doc_lines.append("```python\n")
    doc_lines.append(f"from scheduling_solution_{timestamp} import solve_scheduling_problem\n")
    doc_lines.append("\n")
    doc_lines.append('solution = solve_scheduling_problem("input_data.json", "output/")\n')
    doc_lines.append("```\n\n")

    # 输出说明
    doc_lines.append("## 📤 输出说明\n\n")
    doc_lines.append("求解器将输出以下文件：\n\n")
    doc_lines.append("- `solution.json`: 最优解\n")
    doc_lines.append("- `solution_report.txt`: 求解报告\n")
    doc_lines.append("- `objective_values.txt`: 目标值详情\n\n")

    # 代码结构
    doc_lines.append("## 🏗️ 代码结构\n\n")
    doc_lines.append("代码按照以下结构组织：\n\n")
    doc_lines.append("```\n")
    doc_lines.append("求解器代码\n")
    doc_lines.append("├── 数据模型 (基于TenElementModel Element 1, 2)\n")
    doc_lines.append("├── 约束验证 (基于方案 Section 3)\n")
    doc_lines.append("├── 目标函数 (基于方案 Section 4)\n")
    doc_lines.append(f"├── 算法核心 - {code_traceability['mappings']['algorithm_core']['algorithm']} (基于方案 Section 5)\n")
    doc_lines.append("└── 求解器入口 (基于方案 Section 6)\n")
    doc_lines.append("```\n\n")

    # 可追溯性
    doc_lines.append("## 🔗 可追溯性\n\n")
    doc_lines.append("本代码的每个组件都有明确的方案依据：\n\n")
    doc_lines.append(f"- 查看完整可追溯性映射: `code_traceability_{timestamp}.yaml`\n")
    doc_lines.append(f"- 查看方案文档: `{solution_document_path}`\n")
    doc_lines.append(f"- 查看TenElementModel: `ten_element_model_{timestamp}.yaml`\n\n")

    # 故障排查
    doc_lines.append("## 🔧 故障排查\n\n")
    doc_lines.append("### 问题1: 约束验证失败\n\n")
    doc_lines.append("- 检查输入数据是否符合TenElementModel定义\n")
    doc_lines.append("- 查看方案文档中的约束定义\n\n")

    doc_lines.append("### 问题2: 求解时间过长\n\n")
    doc_lines.append("- 调整算法参数（参见方案文档 Section 5.2）\n")
    doc_lines.append("- 检查问题规模是否超出预期\n\n")

    # 联系信息
    doc_lines.append("## 📞 联系与支持\n\n")
    doc_lines.append("如有问题，请参考：\n\n")
    doc_lines.append(f"- 方案文档: `{solution_document_path}`\n")
    doc_lines.append("- APS Module文档: `src/modules/aps/README.md`\n\n")

    doc_lines.append("---\n\n")
    doc_lines.append(f"**文档生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    doc_lines.append("**BMAD版本**: v6-alpha\n")
    doc_lines.append("**APS模块版本**: V4.3\n")

    return "".join(doc_lines)
````

### 步骤6: 生成README（如果不存在）

````python
def generate_readme_if_not_exists(output_folder, timestamp):
    """
    如果README不存在，生成README.md

    Returns:
        str: README内容，如果已存在则返回None
    """
    readme_path = Path(output_folder) / "README.md"

    if readme_path.exists():
        print("✓ README.md已存在，跳过生成")
        return None

    readme_lines = []

    readme_lines.append("# 调度优化项目\n")
    readme_lines.append("\n")
    readme_lines.append(f"**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    readme_lines.append("\n")
    readme_lines.append("## 📁 目录结构\n")
    readme_lines.append("\n")
    readme_lines.append("```\n")
    readme_lines.append("aps-outputs/\n")
    readme_lines.append("├── models/           # 模型和代码\n")
    readme_lines.append("│   ├── scheduling_solution_*.py\n")
    readme_lines.append("│   ├── ten_element_model_*.yaml\n")
    readme_lines.append("│   └── code_traceability_*.yaml\n")
    readme_lines.append("├── docs/             # 文档\n")
    readme_lines.append("│   ├── solution_document_*.md\n")
    readme_lines.append("│   └── code_documentation_*.md\n")
    readme_lines.append("├── states/           # 状态文件（内部使用）\n")
    readme_lines.append("├── reports/          # 报告\n")
    readme_lines.append("└── data/             # 数据\n")
    readme_lines.append("```\n")
    readme_lines.append("\n")
    readme_lines.append("## 🚀 快速开始\n")
    readme_lines.append("\n")
    readme_lines.append("1. 查看方案文档: `docs/solution_document_*.md`\n")
    readme_lines.append("2. 查看代码文档: `docs/code_documentation_*.md`\n")
    readme_lines.append("3. 运行求解器: `python models/scheduling_solution_*.py`\n")
    readme_lines.append("\n")
    readme_lines.append("## 📋 交付物清单\n")
    readme_lines.append("\n")
    readme_lines.append(f"查看最新的交付物清单: `deliverable_manifest_{timestamp}.json`\n")
    readme_lines.append("\n")
    readme_lines.append("---\n")
    readme_lines.append("\n")
    readme_lines.append("Generated by APS Module V4.3\n")

    return "".join(readme_lines)
````

### 步骤7: 生成交付物清单

```python
import json

def generate_deliverable_manifest(saved_files, timestamp, code_traceability):
    """
    生成交付物清单JSON

    Returns:
        str: JSON内容
    """
    manifest = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "timestamp": timestamp,

        "deliverables": {
            "complete_code": {
                "file_path": saved_files["complete_code"],
                "file_type": "Python source code",
                "description": "完整的调度优化求解器代码",
                "based_on": "用户确认的方案",
                "traceability": "code_traceability_{}.yaml".format(timestamp)
            },
            "ten_element_model": {
                "file_path": saved_files["ten_element_model_export"],
                "file_type": "YAML",
                "description": "TenElementModel完整定义",
                "source": "Phase 1.5 - 十要素建模"
            },
            "solution_document": {
                "file_path": saved_files.get("solution_document_path", ""),
                "file_type": "Markdown",
                "description": "完整的调度优化方案文档",
                "source": "Phase 3 - 方案集成"
            },
            "code_documentation": {
                "file_path": saved_files["code_documentation"],
                "file_type": "Markdown",
                "description": "代码使用文档",
                "audience": "开发者和用户"
            },
            "code_traceability": {
                "file_path": saved_files["code_traceability"],
                "file_type": "YAML",
                "description": "代码与方案的可追溯性映射",
                "purpose": "审计和验证"
            }
        },

        "algorithm": code_traceability['mappings']['algorithm_core']['algorithm'],
        "solution_document": code_traceability.get('solution_document', ''),
        "approved_at": code_traceability.get('approved_at', ''),

        "bmad_version": "v6-alpha",
        "aps_module_version": "V4.3"
    }

    json_content = json.dumps(manifest, indent=2, ensure_ascii=False)

    print("✓ 交付物清单已生成")
    return json_content
```

### 步骤8: 使用Write工具保存所有文件

```markdown
## 🚨 CRITICAL STEP - 文件保存执行

**必须按顺序保存以下所有文件**：

### 文件1: 完整代码
```

IDE Tool: Write
File Path: {output*folder}/models/scheduling_solution*{timestamp}.py
Content: {implementation_code}

```

### 文件2: TenElementModel导出

```

IDE Tool: Write
File Path: {output*folder}/models/ten_element_model*{timestamp}.yaml
Content: {ten_element_model_yaml}

```

### 文件3: 代码可追溯性

```

IDE Tool: Write
File Path: {output*folder}/models/code_traceability*{timestamp}.yaml
Content: {code_traceability_yaml}

```

### 文件4: 代码文档

```

IDE Tool: Write
File Path: {output*folder}/docs/code_documentation*{timestamp}.md
Content: {code_documentation_md}

```

### 文件5: 交付物清单

```

IDE Tool: Write
File Path: {output*folder}/deliverable_manifest*{timestamp}.json
Content: {deliverable_manifest_json}

```

### 文件6: README（如果不存在）

```

IDE Tool: Write (仅当文件不存在时)
File Path: {output_folder}/README.md
Content: {readme_md}

```

**每保存一个文件后，立即输出确认信息**：

```

✓ 代码已保存: {file_path} ({file_size} bytes)

```

```

### 步骤9: 验证所有文件已保存

```python
def verify_all_deliverables_saved(saved_files):
    """
    验证所有交付物已成功保存

    Returns:
        dict: 验证结果
    """
    verification_result = {
        "all_saved": True,
        "details": []
    }

    min_sizes = {
        "complete_code": 2048,
        "ten_element_model_export": 1024,
        "code_traceability": 512,
        "code_documentation": 1024,
        "deliverable_manifest": 256,
        "readme": 512
    }

    for file_type, file_path in saved_files.items():
        if file_path is None:  # README可能跳过
            continue

        min_size = min_sizes.get(file_type, 100)

        # 验证文件存在
        if not os.path.exists(file_path):
            verification_result["all_saved"] = False
            verification_result["details"].append({
                "file_type": file_type,
                "path": file_path,
                "valid": False,
                "issue": "文件不存在"
            })
            continue

        # 验证文件大小
        file_size = os.path.getsize(file_path)
        if file_size < min_size:
            verification_result["all_saved"] = False
            verification_result["details"].append({
                "file_type": file_type,
                "path": file_path,
                "valid": False,
                "size": file_size,
                "min_size_required": min_size,
                "issue": f"文件太小: {file_size} < {min_size}"
            })
            continue

        # 验证通过
        verification_result["details"].append({
            "file_type": file_type,
            "path": file_path,
            "valid": True,
            "size": file_size
        })
        print(f"✓ 验证通过: {file_path} ({file_size} bytes)")

    return verification_result
```

## 输出

```yaml
outputs:
  saved_files:
    type: object
    description: 所有保存的文件路径清单
    structure:
      complete_code: string
      ten_element_model_export: string
      code_traceability: string
      code_documentation: string
      deliverable_manifest: string
      readme: string (可能为null)
      solution_document_path: string (来自输入)

  verification_result:
    type: object
    description: 验证结果
    structure:
      all_saved: boolean
      details: array

  deliverable_manifest:
    type: object
    description: 交付物清单对象
    structure:
      version: string
      generated_at: string (ISO8601)
      deliverables: object
      algorithm: string
```

## 质量检查

- [ ] 所有必需文件已保存
- [ ] 每个文件都使用Write工具保存
- [ ] 文件大小均 >= 最小阈值
- [ ] 所有文件可读且格式正确
- [ ] 交付物清单完整
- [ ] README已创建或已存在
- [ ] 验证结果显示all_saved = true

## 引用

- @编排协调专家库/输出管理规范
- @输出管理规范/文件命名规范

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 统一交付物管理，强制保存+验证
