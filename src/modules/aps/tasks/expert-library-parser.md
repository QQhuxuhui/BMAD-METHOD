# Task: Expert Library Parser

**任务ID**: `expert-library-parser`
**版本**: V4.3
**用途**: Phase 4 Step 4.2 - 解析专家库文件，提取伪代码、框架代码和实现指导

## 输入

```yaml
inputs:
  - algorithm_name: 算法名称（如"遗传算法"）
  - expert_library_citation: 专家库引用路径（如"@专家库/algorithm库/meta-heuristic/遗传算法.md"）
  - constraint_citations: 约束专家库引用列表
  - objective_citations: 目标专家库引用列表
```

## 🚨 强制要求（MANDATORY）

### 1. 完整提取专家库指导内容

**CRITICAL**: 必须提取专家库中的所有实现指导信息，不能遗漏。

```yaml
extraction_principle:
  critical: true
  rule: '专家库是代码生成的唯一权威指导'

  required_sections:
    - 算法伪代码: 完整的算法流程逻辑
    - 核心类结构: 类定义、方法签名
    - 实现注意事项: 编码方式、性能优化、常见错误
    - 参数配置指南: 参数范围、推荐值、调优建议
    - 应用案例: 实际实现示例代码
```

### 2. 结构化输出

提取的内容必须结构化，便于后续代码生成使用。

```yaml
output_structure:
  algorithm_guidance:
    pseudocode: 伪代码文本
    framework: 框架代码
    implementation_notes: 实现注意事项
    parameter_guide: 参数配置指南
    examples: 应用案例代码

  constraint_guidance:
    - name: 约束名称
      type: 约束类型
      handling_method: 处理方法（repair/penalty）
      code_template: 代码模板

  objective_guidance:
    - name: 目标名称
      type: 目标类型
      calculation_method: 计算方法
      code_template: 代码模板
```

## 处理逻辑

### 步骤1: 解析引用路径到文件路径

```python
def resolve_citation_to_path(citation: str) -> str:
    """
    将专家库引用转换为实际文件路径

    Args:
        citation: 引用路径（如"@专家库/algorithm库/meta-heuristic/遗传算法.md"）

    Returns:
        file_path: 实际文件路径

    Examples:
        "@专家库/algorithm库/meta-heuristic/遗传算法.md"
        -> "bmad/aps/templates/algorithm-library/meta-heuristic/遗传算法.md"
    """
    import os

    # 移除@专家库前缀
    if citation.startswith("@专家库/"):
        citation = citation.replace("@专家库/", "")

    # 替换路径分隔符
    citation = citation.replace("algorithm库", "algorithm-library")
    citation = citation.replace("约束库", "constraint-library")
    citation = citation.replace("目标库", "objective-library")

    # 构建完整路径
    base_path = "bmad/aps/templates"
    file_path = os.path.join(base_path, citation)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"专家库文件不存在: {file_path}")

    print(f"✓ 解析引用: {citation} -> {file_path}")
    return file_path
```

### 步骤2: 提取Markdown章节内容

```python
def extract_section(content: str, section_title: str) -> str:
    """
    从Markdown文件中提取指定章节的内容

    Args:
        content: Markdown文件内容
        section_title: 章节标题（如"算法伪代码"）

    Returns:
        section_content: 章节内容
    """
    import re

    # 匹配章节标题（支持2-3级标题）
    pattern = rf'##\s+{re.escape(section_title)}(.*?)(?=##\s+|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        section_content = match.group(1).strip()
        print(f"✓ 提取章节: {section_title} ({len(section_content)} 字符)")
        return section_content
    else:
        print(f"⚠ 未找到章节: {section_title}")
        return ""
```

### 步骤3: 提取代码块

````python
def extract_code_blocks(content: str) -> list:
    """
    提取Markdown中的所有代码块

    Args:
        content: Markdown内容

    Returns:
        code_blocks: 代码块列表
    """
    import re

    # 匹配代码块（```python ... ```）
    pattern = r'```(?:python)?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)

    code_blocks = [block.strip() for block in matches]
    print(f"✓ 提取代码块: {len(code_blocks)} 个")

    return code_blocks
````

### 步骤4: 解析算法专家库

```python
def parse_algorithm_library(citation: str) -> dict:
    """
    解析算法专家库文件

    Args:
        citation: 专家库引用

    Returns:
        guidance: 结构化的算法指导信息
    """
    # 1. 解析路径
    file_path = resolve_citation_to_path(citation)

    # 2. 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. 提取关键章节
    guidance = {
        "algorithm_name": extract_algorithm_name(content),
        "pseudocode": extract_section(content, "算法伪代码"),
        "framework": extract_section(content, "核心类结构"),
        "implementation_notes": extract_section(content, "实现注意事项"),
        "parameter_guide": extract_section(content, "参数配置指南"),
        "examples": extract_section(content, "应用案例"),
        "code_blocks": extract_code_blocks(content)
    }

    # 4. 提取伪代码中的函数定义
    pseudocode_section = guidance["pseudocode"]
    if pseudocode_section:
        guidance["main_function"] = extract_main_algorithm_function(pseudocode_section)

    # 5. 提取框架代码中的类和方法
    framework_section = guidance["framework"]
    if framework_section:
        guidance["class_structure"] = extract_class_structure(framework_section)

    print(f"✓ 算法专家库解析完成: {guidance['algorithm_name']}")
    return guidance

def extract_algorithm_name(content: str) -> str:
    """从标题提取算法名称"""
    import re
    match = re.search(r'^#\s+(.+?)\s*\(', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"

def extract_main_algorithm_function(pseudocode: str) -> str:
    """提取主算法函数的伪代码"""
    code_blocks = extract_code_blocks(pseudocode)
    if code_blocks:
        return code_blocks[0]  # 第一个代码块通常是主函数
    return ""

def extract_class_structure(framework: str) -> dict:
    """提取类结构信息"""
    code_blocks = extract_code_blocks(framework)
    if code_blocks:
        return {
            "class_code": code_blocks[0],
            "methods": extract_method_signatures(code_blocks[0])
        }
    return {}

def extract_method_signatures(class_code: str) -> list:
    """提取类中的方法签名"""
    import re
    pattern = r'def\s+(\w+)\s*\((.*?)\)'
    matches = re.findall(pattern, class_code)
    return [{"name": name, "params": params} for name, params in matches]
```

### 步骤5: 解析约束专家库

```python
def parse_constraint_library(citations: list) -> list:
    """
    解析约束专家库文件列表

    Args:
        citations: 约束专家库引用列表

    Returns:
        constraint_guidance: 约束处理指导列表
    """
    constraint_guidance = []

    for citation in citations:
        try:
            file_path = resolve_citation_to_path(citation)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            guidance = {
                "citation": citation,
                "name": extract_constraint_name(content),
                "type": extract_constraint_type(content),
                "handling_method": extract_section(content, "约束处理方法"),
                "code_template": extract_section(content, "实现模板"),
                "examples": extract_code_blocks(extract_section(content, "应用案例"))
            }

            constraint_guidance.append(guidance)
            print(f"✓ 约束专家库解析: {guidance['name']}")

        except FileNotFoundError as e:
            print(f"⚠ 跳过缺失的约束库: {citation}")
            continue

    return constraint_guidance

def extract_constraint_name(content: str) -> str:
    """提取约束名称"""
    import re
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"

def extract_constraint_type(content: str) -> str:
    """提取约束类型"""
    import re
    # 在元数据中查找类型
    match = re.search(r'类型:\s*(\w+)', content)
    if match:
        return match.group(1)
    return "unknown"
```

### 步骤6: 解析目标函数专家库

```python
def parse_objective_library(citations: list) -> list:
    """
    解析目标函数专家库文件列表

    Args:
        citations: 目标函数专家库引用列表

    Returns:
        objective_guidance: 目标函数指导列表
    """
    objective_guidance = []

    for citation in citations:
        try:
            file_path = resolve_citation_to_path(citation)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            guidance = {
                "citation": citation,
                "name": extract_objective_name(content),
                "type": extract_objective_type(content),
                "calculation_method": extract_section(content, "计算方法"),
                "code_template": extract_section(content, "实现模板"),
                "examples": extract_code_blocks(extract_section(content, "应用案例"))
            }

            objective_guidance.append(guidance)
            print(f"✓ 目标函数专家库解析: {guidance['name']}")

        except FileNotFoundError as e:
            print(f"⚠ 跳过缺失的目标库: {citation}")
            continue

    return objective_guidance

def extract_objective_name(content: str) -> str:
    """提取目标函数名称"""
    import re
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"

def extract_objective_type(content: str) -> str:
    """提取目标函数类型"""
    import re
    # 在元数据中查找类型
    match = re.search(r'优化方向:\s*(\w+)', content)
    if match:
        return match.group(1)
    return "minimize"
```

### 步骤7: 主处理函数

```python
def parse_expert_libraries(
    algorithm_citation: str,
    constraint_citations: list,
    objective_citations: list
) -> dict:
    """
    解析所有相关的专家库

    Args:
        algorithm_citation: 算法专家库引用
        constraint_citations: 约束专家库引用列表
        objective_citations: 目标函数专家库引用列表

    Returns:
        expert_guidance: 完整的专家库指导信息
    """
    print("=" * 70)
    print("开始解析专家库...")
    print("=" * 70)

    expert_guidance = {
        "algorithm": None,
        "constraints": [],
        "objectives": []
    }

    # 1. 解析算法专家库
    if algorithm_citation:
        print(f"\n[1/3] 解析算法专家库: {algorithm_citation}")
        expert_guidance["algorithm"] = parse_algorithm_library(algorithm_citation)

    # 2. 解析约束专家库
    if constraint_citations:
        print(f"\n[2/3] 解析约束专家库: {len(constraint_citations)} 个")
        expert_guidance["constraints"] = parse_constraint_library(constraint_citations)

    # 3. 解析目标函数专家库
    if objective_citations:
        print(f"\n[3/3] 解析目标函数专家库: {len(objective_citations)} 个")
        expert_guidance["objectives"] = parse_objective_library(objective_citations)

    print("\n" + "=" * 70)
    print("专家库解析完成！")
    print("=" * 70)
    print(f"✓ 算法指导: {'已提取' if expert_guidance['algorithm'] else '未找到'}")
    print(f"✓ 约束指导: {len(expert_guidance['constraints'])} 个")
    print(f"✓ 目标指导: {len(expert_guidance['objectives'])} 个")

    return expert_guidance
```

## 输出

```yaml
outputs:
  expert_guidance:
    type: object
    description: 结构化的专家库指导信息
    structure:
      algorithm:
        algorithm_name: string
        pseudocode: string (伪代码文本)
        framework: string (框架代码)
        implementation_notes: string
        parameter_guide: string
        examples: string
        code_blocks: list (所有代码块)
        main_function: string (主函数伪代码)
        class_structure: object (类结构信息)

      constraints:
        - citation: string
          name: string
          type: string
          handling_method: string
          code_template: string
          examples: list

      objectives:
        - citation: string
          name: string
          type: string
          calculation_method: string
          code_template: string
          examples: list
```

## 质量检查

- [ ] 所有引用路径都能正确解析
- [ ] 所有章节都能正确提取
- [ ] 代码块都能正确识别
- [ ] 输出结构完整
- [ ] 处理缺失文件的情况（不中断流程）

## 使用示例

```python
# 调用示例
algorithm_citation = "@专家库/algorithm库/meta-heuristic/遗传算法.md"
constraint_citations = [
    "@专家库/约束库/precedence/工艺路线约束.md",
    "@专家库/约束库/resource/设备独占约束.md"
]
objective_citations = [
    "@专家库/目标库/delivery/交付率目标.md"
]

expert_guidance = parse_expert_libraries(
    algorithm_citation,
    constraint_citations,
    objective_citations
)

# 使用提取的指导信息
print(expert_guidance["algorithm"]["pseudocode"])
print(expert_guidance["algorithm"]["framework"])
```

## 引用

- @专家库模板体系
- @代码生成规范

---

**创建**: 2025-01-21
**BMAD版本**: v6-alpha
**核心机制**: 专家库解析与结构化提取
