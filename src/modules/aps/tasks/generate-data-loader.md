# Task: Generate Data Loader

**任务ID**: `generate-data-loader`
**版本**: V1.0
**用途**: Phase 3 Step 3.15 - 生成通用数据加载模块，支持多种数据格式

## 背景

在V4.4之前，生成的代码会调用`load_input_data()`等数据加载函数，但这些函数从未被实际生成，导致代码无法运行（P0缺陷）。

本任务负责根据TenElementModel Element 9（输入数据定义）生成完整的数据加载代码，支持多种常见数据格式。

## 输入

```yaml
inputs:
  - ten_element_model: TenElementModel对象
  - solution_document_path: 方案文档路径（用于引用标注）
```

## 核心功能

### 1. 数据格式检测

基于TenElementModel Element 9的数据源配置，自动检测数据格式：

```python
def detect_data_format(input_data_element):
    """
    从TenElementModel Element 9检测数据格式

    Returns:
        list: 数据格式列表，如 ['csv', 'json', 'excel']
    """
    formats = set()

    for data_source in input_data_element.get('data_sources', []):
        file_path = data_source.get('file_path', '')

        if file_path.endswith('.csv'):
            formats.add('csv')
        elif file_path.endswith('.json'):
            formats.add('json')
        elif file_path.endswith(('.xlsx', '.xls')):
            formats.add('excel')
        elif file_path.endswith('.parquet'):
            formats.add('parquet')
        elif data_source.get('type') == 'database':
            formats.add('database')

    return list(formats)
```

### 2. 生成加载器代码

根据检测到的数据格式，生成对应的加载函数：

```python
def generate_data_loading_module(ten_element_model, solution_document_path):
    """
    生成通用数据加载模块

    方案依据: solution_document Section 6 - 实现路线图
    TenElementModel: Element 9 - input_data

    Args:
        ten_element_model: TenElementModel对象
        solution_document_path: 方案文档路径

    Returns:
        str: 完整的Python数据加载模块代码
    """
    input_data_element = ten_element_model.get('input_data', {})
    data_sources = input_data_element.get('data_sources', [])

    # 检测需要支持的数据格式
    formats = detect_data_format(input_data_element)

    code_lines = []

    # 生成文档注释
    code_lines.append('"""')
    code_lines.append('数据加载模块')
    code_lines.append('')
    code_lines.append(f'方案依据: {solution_document_path} Section 6 - 实现路线图')
    code_lines.append('TenElementModel: Element 9 - input_data')
    code_lines.append('引用: @TenElementModel/input_data')
    code_lines.append('')
    code_lines.append('V4.4新增: 修复P0缺陷 - 自动生成数据加载代码')
    code_lines.append(f'支持格式: {", ".join(formats)}')
    code_lines.append('"""')
    code_lines.append('')

    # 生成导入语句
    imports = generate_imports(formats)
    code_lines.append(imports)
    code_lines.append('')

    # 为每种格式生成加载函数
    for fmt in formats:
        loader_func = generate_format_loader(fmt, input_data_element)
        code_lines.append(loader_func)
        code_lines.append('')

    # 生成统一的加载入口函数
    main_loader = generate_main_loader_function(data_sources, solution_document_path)
    code_lines.append(main_loader)
    code_lines.append('')

    return '\n'.join(code_lines)
```

### 3. 格式特定加载器

为每种数据格式生成加载函数：

#### CSV加载器

```python
def generate_csv_loader(data_source_config):
    """生成CSV数据加载函数"""
    code = '''def load_csv_data(file_path):
    """
    加载CSV格式数据

    方案依据: TenElementModel Element 9 - CSV数据源

    Args:
        file_path: CSV文件路径

    Returns:
        dict: 加载的数据字典
    """
    import pandas as pd

    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"CSV文件加载失败: {file_path}, 错误: {str(e)}")
'''
    return code
```

#### JSON加载器

```python
def generate_json_loader(data_source_config):
    """生成JSON数据加载函数"""
    code = '''def load_json_data(file_path):
    """
    加载JSON格式数据

    方案依据: TenElementModel Element 9 - JSON数据源

    Args:
        file_path: JSON文件路径

    Returns:
        dict: 加载的数据字典
    """
    import json

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise ValueError(f"JSON文件加载失败: {file_path}, 错误: {str(e)}")
'''
    return code
```

#### Excel加载器

```python
def generate_excel_loader(data_source_config):
    """生成Excel数据加载函数"""
    code = '''def load_excel_data(file_path, sheet_name=0):
    """
    加载Excel格式数据

    方案依据: TenElementModel Element 9 - Excel数据源

    Args:
        file_path: Excel文件路径
        sheet_name: 工作表名称或索引（默认第一个）

    Returns:
        dict: 加载的数据字典
    """
    import pandas as pd

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"Excel文件加载失败: {file_path}, 错误: {str(e)}")
'''
    return code
```

#### Parquet加载器

```python
def generate_parquet_loader(data_source_config):
    """生成Parquet数据加载函数"""
    code = '''def load_parquet_data(file_path):
    """
    加载Parquet格式数据

    方案依据: TenElementModel Element 9 - Parquet数据源

    Args:
        file_path: Parquet文件路径

    Returns:
        dict: 加载的数据字典
    """
    import pandas as pd

    try:
        df = pd.read_parquet(file_path)
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"Parquet文件加载失败: {file_path}, 错误: {str(e)}")
'''
    return code
```

#### 数据库加载器

```python
def generate_database_loader(data_source_config):
    """生成数据库数据加载函数"""
    code = '''def load_database_data(connection_string, query):
    """
    从数据库加载数据

    方案依据: TenElementModel Element 9 - 数据库数据源

    Args:
        connection_string: 数据库连接字符串
        query: SQL查询语句

    Returns:
        dict: 加载的数据字典
    """
    import pandas as pd
    from sqlalchemy import create_engine

    try:
        engine = create_engine(connection_string)
        df = pd.read_sql(query, engine)
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"数据库查询失败, 错误: {str(e)}")
'''
    return code
```

### 4. 统一加载入口

生成`load_all_input_data()`函数作为统一入口：

```python
def generate_main_loader_function(data_sources, solution_document_path):
    """
    生成主数据加载函数

    这是求解器调用的统一入口函数
    """
    code_lines = []

    code_lines.append('def load_all_input_data(input_data_path):')
    code_lines.append('    """')
    code_lines.append('    加载所有输入数据（统一入口）')
    code_lines.append('    ')
    code_lines.append(f'    方案依据: {solution_document_path} Section 6 - 实现路线图')
    code_lines.append('    TenElementModel: Element 9 - input_data')
    code_lines.append('    ')
    code_lines.append('    Args:')
    code_lines.append('        input_data_path: 输入数据路径（文件或目录）')
    code_lines.append('    ')
    code_lines.append('    Returns:')
    code_lines.append('        dict: 包含所有输入数据的字典')
    code_lines.append('    """')
    code_lines.append('    import os')
    code_lines.append('    ')
    code_lines.append('    all_data = {}')
    code_lines.append('    ')
    code_lines.append('    # 检测输入路径类型')
    code_lines.append('    if os.path.isfile(input_data_path):')
    code_lines.append('        # 单个文件')
    code_lines.append('        file_ext = os.path.splitext(input_data_path)[1].lower()')
    code_lines.append('        ')
    code_lines.append('        if file_ext == ".csv":')
    code_lines.append('            all_data = load_csv_data(input_data_path)')
    code_lines.append('        elif file_ext == ".json":')
    code_lines.append('            all_data = load_json_data(input_data_path)')
    code_lines.append('        elif file_ext in [".xlsx", ".xls"]:')
    code_lines.append('            all_data = load_excel_data(input_data_path)')
    code_lines.append('        elif file_ext == ".parquet":')
    code_lines.append('            all_data = load_parquet_data(input_data_path)')
    code_lines.append('        else:')
    code_lines.append('            raise ValueError(f"不支持的文件格式: {file_ext}")')
    code_lines.append('    ')
    code_lines.append('    elif os.path.isdir(input_data_path):')
    code_lines.append('        # 目录 - 加载所有支持格式的文件')

    # 根据data_sources配置生成特定的加载逻辑
    for source in data_sources:
        source_name = source.get('name', 'data')
        file_path = source.get('file_path', '')

        if file_path:
            code_lines.append(f'        # 加载 {source_name}')
            code_lines.append(f'        {source_name}_path = os.path.join(input_data_path, "{os.path.basename(file_path)}")')
            code_lines.append(f'        if os.path.exists({source_name}_path):')

            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                code_lines.append(f'            all_data["{source_name}"] = load_csv_data({source_name}_path)')
            elif ext == '.json':
                code_lines.append(f'            all_data["{source_name}"] = load_json_data({source_name}_path)')
            elif ext in ['.xlsx', '.xls']:
                code_lines.append(f'            all_data["{source_name}"] = load_excel_data({source_name}_path)')
            elif ext == '.parquet':
                code_lines.append(f'            all_data["{source_name}"] = load_parquet_data({source_name}_path)')

            code_lines.append('        ')

    code_lines.append('    else:')
    code_lines.append('        raise ValueError(f"输入路径不存在: {input_data_path}")')
    code_lines.append('    ')
    code_lines.append('    return all_data')

    return '\n'.join(code_lines)
```

### 5. 导入语句生成

```python
def generate_imports(formats):
    """
    根据数据格式生成必要的导入语句
    """
    imports = []

    imports.append('import os')
    imports.append('import json')

    if 'csv' in formats or 'excel' in formats or 'parquet' in formats:
        imports.append('import pandas as pd')

    if 'database' in formats:
        imports.append('from sqlalchemy import create_engine')

    return '\n'.join(imports)
```

### 6. 格式路由

```python
def generate_format_loader(fmt, input_data_element):
    """
    根据格式生成对应的加载函数
    """
    if fmt == 'csv':
        return generate_csv_loader(input_data_element)
    elif fmt == 'json':
        return generate_json_loader(input_data_element)
    elif fmt == 'excel':
        return generate_excel_loader(input_data_element)
    elif fmt == 'parquet':
        return generate_parquet_loader(input_data_element)
    elif fmt == 'database':
        return generate_database_loader(input_data_element)
    else:
        return f'# 格式 {fmt} 暂不支持'
```

## 输出

```yaml
outputs:
  data_loading_code:
    type: string
    description: 完整的Python数据加载模块代码
    contains:
      - 格式检测逻辑
      - 各格式特定加载函数
      - load_all_input_data()统一入口
      - 完整的错误处理
      - 方案引用标注
```

## 代码质量要求

- ✅ 生成的代码100%可运行，无TODO或占位符
- ✅ 包含完整的错误处理和异常捕获
- ✅ 所有函数都有方案引用标注
- ✅ 支持文件和目录两种输入方式
- ✅ 自动检测文件格式，无需手动指定
- ✅ 生成的函数名与generate_main_solver中的调用一致

## 使用示例

```python
# 在 generate-code-from-solution.md 中调用
from generate_data_loader import generate_data_loading_module

# 生成数据加载模块
data_loading_code = generate_data_loading_module(
    ten_element_model,
    solution_document_path
)

# 集成到最终代码
complete_code = assemble_complete_code(
    imports=imports,
    data_models=data_models,
    data_loading_module=data_loading_code,  # ← 集成在这里
    constraint_functions=constraint_functions,
    objective_functions=objective_functions,
    algorithm_core=algorithm_core,
    main_solver=main_solver,
    user_approved_solution=user_approved_solution,
    solution_document_path=solution_document_path
)
```

## 注意事项

1. **格式自动检测**: 根据文件扩展名自动选择加载器，无需用户指定
2. **错误容错**: 所有加载函数都包含异常处理，提供清晰的错误信息
3. **依赖管理**: 生成的代码仅导入实际需要的库（如pandas、sqlalchemy）
4. **方案追溯**: 每个函数都标注了TenElementModel Element 9引用
5. **统一接口**: `load_all_input_data()`提供统一调用接口，屏蔽格式差异

## 引用

- @TenElementModel/input_data
- @数据加载专家库/多格式支持
- generate-code-from-solution.md (调用方)

---

**创建**: 2025-01-21
**BMAD版本**: v6-alpha
**核心机制**: 通用数据加载器生成，修复P0缺陷，支持多种数据格式
