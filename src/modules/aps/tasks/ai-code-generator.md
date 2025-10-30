# Task: AI Code Generator

**任务ID**: `ai-code-generator`
**版本**: V4.3
**用途**: Phase 4 Step 4.4 - 基于专家库伪代码和TenElementModel，使用AI生成完整算法实现

## 输入

```yaml
inputs:
  - expert_guidance: 专家库指导信息（来自expert-library-parser）
  - ten_element_model: TenElementModel对象
  - algorithm_config: 算法配置参数
  - generated_formulas: 已生成的约束/目标函数代码（来自formula-to-code-converter）
```

## 🚨 强制要求（MANDATORY）

### 1. 生成完整可运行代码（零TODO）

**CRITICAL**: 生成的代码必须完整、可运行，不能包含任何TODO或pass语句。

```yaml
code_completeness_requirement:
  critical: true
  rule: '生成的代码必须100%完整，可直接运行'

  forbidden_patterns:
    - '# TODO'
    - 'pass  # '
    - 'raise NotImplementedError'
    - '... # 待实现'

  required_completeness:
    - 所有函数都有完整实现: 100%
    - 所有类方法都有完整实现: 100%
    - 数据加载逻辑完整: 100%
    - 算法核心逻辑完整: 100%
```

### 2. 严格基于专家库指导

生成的代码必须遵循专家库中的伪代码、框架和实现建议，不能随意发挥。

```yaml
expert_guidance_adherence:
  pseudocode_fidelity: 算法流程必须与伪代码一致
  framework_compliance: 类结构必须与框架代码一致
  implementation_notes: 必须遵循实现注意事项
  parameter_guide: 参数配置必须在推荐范围内
```

### 3. 绑定真实数据结构

生成的代码必须使用TenElementModel中定义的数据结构，不能使用示例数据。

```yaml
data_binding_requirement:
  input_data: 必须读取TenElementModel.input_data中定义的数据源
  output_format: 必须按照TenElementModel.output_format输出
  no_fake_data: 禁止使用硬编码的示例数据
```

## 处理逻辑

### 步骤1: 构建AI提示 - 算法核心实现

````python
def build_algorithm_implementation_prompt(
    expert_guidance: dict,
    ten_element_model: dict,
    algorithm_config: dict
) -> str:
    """
    构建AI提示，用于生成算法核心实现

    Args:
        expert_guidance: 专家库指导
        ten_element_model: TenElementModel
        algorithm_config: 算法配置

    Returns:
        prompt: AI提示文本
    """
    algorithm_name = expert_guidance['algorithm']['algorithm_name']
    pseudocode = expert_guidance['algorithm']['pseudocode']
    framework = expert_guidance['algorithm']['framework']
    implementation_notes = expert_guidance['algorithm']['implementation_notes']

    prompt = f"""
你是算法实现专家。请根据以下信息生成完整的Python算法实现代码。

# 🎯 核心要求
1. 将伪代码转换为完整的Python实现（**不要留任何TODO或pass语句**）
2. 严格遵循专家库的框架结构
3. 根据TenElementModel的数据结构进行数据绑定
4. 代码必须可直接运行，无需任何补充

# 📚 专家库指导

## 算法名称
{algorithm_name}

## 算法伪代码（流程逻辑）
```python
{pseudocode}
````

## 框架代码（类结构）

```python
{framework}
```

## 实现注意事项

{implementation_notes}

# 📊 问题具体配置（TenElementModel）

## 决策变量

{format_decision_variables(ten_element_model['decision_variables'])}

## 约束条件

{format_constraints(ten_element_model['constraints'])}

## 目标函数

{format_objectives(ten_element_model['objectives'])}

## 算法参数配置

{format_algorithm_config(algorithm_config)}

# 🔧 数据结构定义

基于TenElementModel，使用以下数据结构：

## Solution类

```python
class Solution:
    def __init__(self):
        self.tasks: List[Task] = []
        self.resources: List[Resource] = []
        self.objective_value = 0.0
        self.is_feasible = True
```

## Task类（决策变量）

```python
class Task:
    def __init__(self, task_id: int, machine_id: int):
        self.task_id = task_id
        self.machine_id = machine_id
        self.start_time = 0.0
        self.processing_time = 0.0
        # ... 其他属性根据TenElementModel定义
```

# 📝 生成要求

请生成 {algorithm_name} 类的**完整实现代码**，包括：

1. ****init**方法**: 初始化所有参数和数据结构
2. **initialize_population方法**: 生成初始种群（不要留TODO）
3. **evaluate_population方法**: 评估种群适应度（完整实现）
4. **selection方法**: 选择操作（根据配置的selection_method实现）
5. **crossover方法**: 交叉操作（根据配置的crossover_method实现）
6. **mutation方法**: 变异操作（根据配置的mutation_method实现）
7. **repair方法**: 修复不可行解（调用约束验证函数）
8. **environmental_selection方法**: 环境选择（精英保留策略）
9. **run方法**: 主循环（完整的算法流程）

## 关键点

- 编码方式: 根据决策变量类型选择（排列编码/整数编码/二进制编码）
- 初始化: 根据问题数据生成可行的初始解
- 交叉: 实现具体的交叉算子（如OX交叉、PMX交叉等）
- 变异: 实现具体的变异算子（如交换变异、插入变异等）
- 适应度: 调用目标函数计算适应度值

## 输出格式

```python
class {algorithm_name.replace(' ', '')}:
    \"\"\"
    {algorithm_name}实现

    方案依据: ...
    专家库: ...
    \"\"\"

    def __init__(self, problem: Problem, config: Config):
        # 完整实现...

    def initialize_population(self):
        # 完整实现，无TODO
        ...

    # ... 其他方法，全部完整实现
```

请开始生成完整代码：
"""

    return prompt

def format_decision_variables(decision_variables: list) -> str:
"""格式化决策变量信息"""
lines = []
for dv in decision_variables:
lines.append(f"- {dv['name']}: {dv['type']}, {dv['domain']}")
lines.append(f" 描述: {dv['description']}")
return "\n".join(lines)

def format_constraints(constraints: list) -> str:
"""格式化约束信息"""
lines = []
for c in constraints:
lines.append(f"- {c['name']} ({c['type']}): {c['formula']}")
return "\n".join(lines)

def format_objectives(objectives: list) -> str:
"""格式化目标函数信息"""
lines = []
for obj in objectives:
lines.append(f"- {obj['name']} ({obj['type']}): {obj['formula']}")
lines.append(f" 权重: {obj.get('weight', 1.0)}")
return "\n".join(lines)

def format_algorithm_config(config: dict) -> str:
"""格式化算法配置"""
lines = []
for key, value in config.items():
lines.append(f"- {key}: {value}")
return "\n".join(lines)

````

### 步骤2: 构建AI提示 - 数据加载实现

```python
def build_data_loader_prompt(
    ten_element_model: dict
) -> str:
    """
    构建AI提示，用于生成数据加载代码

    Args:
        ten_element_model: TenElementModel

    Returns:
        prompt: AI提示文本
    """
    input_data = ten_element_model.get('input_data', {})
    sources = input_data.get('sources', [])
    data_format = input_data.get('format', 'CSV')

    prompt = f"""
你是数据处理专家。请生成完整的数据加载函数实现。

# 🎯 核心要求
1. 生成完整的load_input_data()函数（**不要留TODO**）
2. 严格按照TenElementModel中定义的数据源加载
3. 根据数据格式（{data_format}）选择合适的解析方法
4. 进行数据验证和完整性检查

# 📊 数据源定义（来自TenElementModel）

## 输入数据源
{format_data_sources(sources)}

## 数据格式
{data_format}

## 数据验证要求
{input_data.get('validation', '数据完整性检查')}

# 📝 生成要求

请生成完整的数据加载函数，包括：

1. **load_input_data(input_data_path)**: 主加载函数
   - 读取所有数据源文件
   - 解析数据（根据格式选择pandas/json/xml等）
   - 验证数据完整性
   - 构造problem_data字典

2. **validate_input_data(data)**: 数据验证函数
   - 检查必需字段
   - 检查数据类型
   - 检查数据范围

## 数据结构要求
返回的problem_data必须包含：
```python
problem_data = {{
    "tasks": [...],          # 任务列表
    "resources": [...],      # 资源列表
    "constraints": [...],    # 约束参数
    "objectives": [...],     # 目标参数
    # ... 根据数据源定义
}}
````

## 示例框架

```python
def load_input_data(input_data_path: str) -> Dict:
    \"\"\"
    加载输入数据

    方案依据: TenElementModel Element 9
    数据来源: {', '.join(sources)}
    \"\"\"
    import pandas as pd
    import os

    problem_data = {{
        "tasks": [],
        "resources": [],
        # ...
    }}

    # 加载每个数据源文件
    # 完整实现，无TODO

    return problem_data
```

请生成完整的数据加载代码：
"""

    return prompt

def format_data_sources(sources: list) -> str:
"""格式化数据源列表"""
if not sources:
return "未指定数据源"
lines = []
for i, source in enumerate(sources, 1):
lines.append(f"{i}. {source}")
return "\n".join(lines)

````

### 步骤3: 调用AI生成代码

```python
def call_ai_for_code_generation(prompt: str) -> str:
    """
    调用AI生成代码

    Args:
        prompt: AI提示

    Returns:
        generated_code: 生成的代码
    """
    print("🤖 调用AI生成代码...")
    print(f"  提示长度: {len(prompt)} 字符")

    # 这里应该调用实际的AI服务
    # 在BMAD框架中，这会自动使用Claude等LLM
    # 由于当前是任务定义，这里提供接口说明

    # 实际实现时，BMAD会自动处理AI调用
    # generated_code = bmad_ai_service.generate(prompt)

    # 任务定义阶段，返回指导说明
    instruction = """
    在实际执行时，此函数会调用BMAD的AI服务（Claude等）。
    AI将根据提示生成完整的Python代码。

    AI生成过程：
    1. 理解专家库的伪代码逻辑
    2. 参考框架代码的类结构
    3. 结合TenElementModel的数据定义
    4. 生成完整、可运行的Python实现
    5. 确保无TODO、无pass语句
    """

    print("✓ AI代码生成完成")
    return instruction
````

### 步骤4: 验证生成代码的完整性

```python
def validate_generated_code(code: str) -> dict:
    """
    验证生成的代码是否完整

    Args:
        code: 生成的代码

    Returns:
        validation_result: 验证结果
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # 1. 检查TODO
    if "TODO" in code or "todo" in code.lower():
        validation_result["valid"] = False
        validation_result["errors"].append("代码包含TODO标记，需要重新生成")

    # 2. 检查pass语句（可能是空实现）
    import re
    pass_pattern = r'^\s+pass\s*(?:#|$)'
    if re.search(pass_pattern, code, re.MULTILINE):
        validation_result["valid"] = False
        validation_result["errors"].append("代码包含空实现（pass语句），需要重新生成")

    # 3. 检查NotImplementedError
    if "NotImplementedError" in code:
        validation_result["valid"] = False
        validation_result["errors"].append("代码包含NotImplementedError，需要重新生成")

    # 4. 语法检查
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        validation_result["valid"] = False
        validation_result["errors"].append(f"语法错误: {e}")

    # 5. 检查关键方法是否存在
    required_methods = [
        'def initialize_population',
        'def evaluate_population',
        'def selection',
        'def crossover',
        'def mutation',
        'def run'
    ]

    for method in required_methods:
        if method not in code:
            validation_result["warnings"].append(f"未找到方法: {method}")

    if validation_result["valid"]:
        print("✓ 代码验证通过")
    else:
        print("✗ 代码验证失败:")
        for error in validation_result["errors"]:
            print(f"  - {error}")

    return validation_result
```

### 步骤5: 生成完整算法实现

```python
def generate_algorithm_implementation(
    expert_guidance: dict,
    ten_element_model: dict,
    algorithm_config: dict
) -> str:
    """
    生成完整的算法实现代码

    Args:
        expert_guidance: 专家库指导
        ten_element_model: TenElementModel
        algorithm_config: 算法配置

    Returns:
        code: 完整的算法实现代码
    """
    print("=" * 70)
    print("生成算法核心实现...")
    print("=" * 70)

    # 1. 构建AI提示
    prompt = build_algorithm_implementation_prompt(
        expert_guidance,
        ten_element_model,
        algorithm_config
    )

    # 2. 调用AI生成代码
    code = call_ai_for_code_generation(prompt)

    # 3. 验证代码完整性
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        validation = validate_generated_code(code)

        if validation["valid"]:
            print(f"✓ 算法实现生成成功（尝试 {retry_count + 1}/{max_retries}）")
            return code

        # 如果验证失败，重新生成
        print(f"⚠ 第 {retry_count + 1} 次生成失败，重新生成...")
        retry_count += 1

        # 更新提示，强调问题
        prompt += f"""

        # ⚠️ 上次生成失败，错误信息：
        {chr(10).join(validation['errors'])}

        请务必：
        1. 不要留任何TODO
        2. 不要使用pass作为函数体
        3. 完整实现所有方法
        """

        code = call_ai_for_code_generation(prompt)

    raise RuntimeError(f"算法实现生成失败，已尝试 {max_retries} 次")
```

### 步骤6: 生成数据加载实现

```python
def generate_data_loader_implementation(
    ten_element_model: dict
) -> str:
    """
    生成完整的数据加载代码

    Args:
        ten_element_model: TenElementModel

    Returns:
        code: 完整的数据加载代码
    """
    print("=" * 70)
    print("生成数据加载实现...")
    print("=" * 70)

    # 1. 构建AI提示
    prompt = build_data_loader_prompt(ten_element_model)

    # 2. 调用AI生成代码
    code = call_ai_for_code_generation(prompt)

    # 3. 验证代码完整性
    validation = validate_generated_code(code)

    if not validation["valid"]:
        raise RuntimeError(f"数据加载代码生成失败: {validation['errors']}")

    print("✓ 数据加载实现生成成功")
    return code
```

### 步骤7: 主处理函数

```python
def generate_complete_implementation(
    expert_guidance: dict,
    ten_element_model: dict,
    algorithm_config: dict,
    generated_formulas: dict
) -> dict:
    """
    生成完整的代码实现

    Args:
        expert_guidance: 专家库指导
        ten_element_model: TenElementModel
        algorithm_config: 算法配置
        generated_formulas: 已生成的公式代码

    Returns:
        complete_code: 完整的代码实现
    """
    print("=" * 70)
    print("开始AI代码生成...")
    print("=" * 70)

    complete_code = {
        "algorithm_implementation": "",
        "data_loader": "",
        "helper_functions": []
    }

    # 1. 生成算法核心实现
    print("\n[1/2] 生成算法核心实现")
    complete_code["algorithm_implementation"] = generate_algorithm_implementation(
        expert_guidance,
        ten_element_model,
        algorithm_config
    )

    # 2. 生成数据加载实现
    print("\n[2/2] 生成数据加载实现")
    complete_code["data_loader"] = generate_data_loader_implementation(
        ten_element_model
    )

    # 3. 生成辅助函数（如果需要）
    # complete_code["helper_functions"] = generate_helper_functions(...)

    print("\n" + "=" * 70)
    print("AI代码生成完成！")
    print("=" * 70)
    print(f"✓ 算法实现: {len(complete_code['algorithm_implementation'])} 字符")
    print(f"✓ 数据加载: {len(complete_code['data_loader'])} 字符")

    return complete_code
```

## 输出

```yaml
outputs:
  complete_code:
    type: object
    description: AI生成的完整代码
    structure:
      algorithm_implementation: string (算法核心代码，无TODO)
      data_loader: string (数据加载代码，无TODO)
      helper_functions: list (辅助函数列表)
```

## 质量检查

- [ ] 算法实现代码无TODO
- [ ] 算法实现代码无pass
- [ ] 数据加载代码无TODO
- [ ] 所有代码语法正确
- [ ] 代码逻辑与专家库伪代码一致
- [ ] 数据结构与TenElementModel一致
- [ ] 包含完整的方案引用标记

## AI提示工程最佳实践

### 提示结构

1. **明确目标**: 开头清晰说明要生成什么
2. **提供上下文**: 专家库伪代码、框架、实现建议
3. **具体要求**: 列出所有必需的方法和功能
4. **约束条件**: 禁止TODO、pass等不完整实现
5. **示例格式**: 提供期望的代码格式

### 提示优化技巧

- 使用"完整实现"、"可直接运行"等强调词
- 明确指出"不要留TODO"、"不要使用pass"
- 提供TenElementModel的具体数据结构
- 参考专家库的实现案例
- 使用重试机制处理生成失败

## 引用

- @专家库模板体系
- @TenElementModel规范
- @AI提示工程最佳实践

---

**创建**: 2025-01-21
**BMAD版本**: v6-alpha
**核心机制**: AI驱动的代码生成，基于专家库指导和TenElementModel
