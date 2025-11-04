# 决策变量映射指南

**Decision Variables Mapping Guide**

---

**版本**: 1.0.0
**所属模块**: 十要素映射 - 决策变量
**创建日期**: 2025-11-04
**最后更新**: 2025-11-04

---

## 🎯 概述

决策变量是调度优化问题的核心，定义了需要优化的决策内容。本指南详细说明如何将TenElementModel中的决策变量要素映射为具体的代码实现。

## 📋 决策变量类型映射

### 1. 二进制决策变量 (Binary Variables)

#### 应用场景

- 选择/不选择决策
- 任务分配问题
- 路径选择问题
- 设备开启/关闭

#### 代码实现模板

```python
# 基础二进制变量定义
import pulp
import ortools.linear_solver.pywraplp as ortools

class BinaryDecisionVariables:
    """二进制决策变量的标准化实现"""

    def __init__(self, solver, variable_configs):
        """
        初始化二进制决策变量

        Args:
            solver: 求解器实例 (pulp或ortools)
            variable_configs: 变量配置列表
        """
        self.solver = solver
        self.variables = {}
        self._create_variables(variable_configs)

    def _create_variables(self, configs):
        """根据配置创建决策变量"""
        for config in configs:
            name = config['name']
            indices = config.get('indices', [])

            if indices:
                # 多维索引变量
                self.variables[name] = {}
                for index in indices:
                    var_name = f"{name}_{index}"
                    if isinstance(self.solver, pulp.LpProblem):
                        var = pulp.LpVariable(var_name, cat='Binary')
                    else:
                        var = self.solver.BoolVar(var_name)
                    self.variables[name][index] = var
            else:
                # 单一变量
                if isinstance(self.solver, pulp.LpProblem):
                    var = pulp.LpVariable(name, cat='Binary')
                else:
                    var = self.solver.BoolVar(name)
                self.variables[name] = var

    def get_variable(self, name, index=None):
        """获取决策变量"""
        if index is not None:
            return self.variables[name].get(index)
        return self.variables.get(name)

    def get_all_variables(self):
        """获取所有决策变量"""
        return self.variables

# 使用示例
variable_configs = [
    {
        'name': 'x_ij',
        'description': '任务i分配给机器j',
        'indices': [(i, j) for i in range(10) for j in range(5)]
    },
    {
        'name': 'y_i',
        'description': '是否选择任务i',
        'indices': list(range(10))
    }
]

# 创建变量实例
binary_vars = BinaryDecisionVariables(solver, variable_configs)
```

### 2. 整数决策变量 (Integer Variables)

#### 应用场景

- 任务数量
- 设备数量
- 时间分配
- 位置编号

#### 代码实现模板

```python
class IntegerDecisionVariables:
    """整数决策变量的标准化实现"""

    def __init__(self, solver, variable_configs):
        """
        初始化整数决策变量

        Args:
            solver: 求解器实例
            variable_configs: 变量配置列表
        """
        self.solver = solver
        self.variables = {}
        self._create_variables(variable_configs)

    def _create_variables(self, configs):
        """创建整数决策变量"""
        for config in configs:
            name = config['name']
            lower_bound = config.get('lower_bound', 0)
            upper_bound = config.get('upper_bound', float('inf'))
            indices = config.get('indices', [])

            if indices:
                # 多维索引变量
                self.variables[name] = {}
                for index in indices:
                    var_name = f"{name}_{index}"
                    if isinstance(self.solver, pulp.LpProblem):
                        var = pulp.LpVariable(
                            var_name,
                            lowBound=lower_bound,
                            upBound=upper_bound,
                            cat='Integer'
                        )
                    else:
                        var = self.solver.IntVar(
                            lower_bound, upper_bound, var_name
                        )
                    self.variables[name][index] = var
            else:
                # 单一变量
                if isinstance(self.solver, pulp.LpProblem):
                    var = pulp.LpVariable(
                        name,
                        lowBound=lower_bound,
                        upBound=upper_bound,
                        cat='Integer'
                    )
                else:
                    var = self.solver.IntVar(
                        lower_bound, upper_bound, name
                    )
                self.variables[name] = var
```

### 3. 连续决策变量 (Continuous Variables)

#### 应用场景

- 时间安排
- 资源分配量
- 成本计算
- 权重系数

#### 代码实现模板

```python
class ContinuousDecisionVariables:
    """连续决策变量的标准化实现"""

    def __init__(self, solver, variable_configs):
        """
        初始化连续决策变量

        Args:
            solver: 求解器实例
            variable_configs: 变量配置列表
        """
        self.solver = solver
        self.variables = {}
        self._create_variables(variable_configs)

    def _create_variables(self, configs):
        """创建连续决策变量"""
        for config in configs:
            name = config['name']
            lower_bound = config.get('lower_bound', 0)
            upper_bound = config.get('upper_bound', float('inf'))
            indices = config.get('indices', [])

            if indices:
                # 多维索引变量
                self.variables[name] = {}
                for index in indices:
                    var_name = f"{name}_{index}"
                    if isinstance(self.solver, pulp.LpProblem):
                        var = pulp.LpVariable(
                            var_name,
                            lowBound=lower_bound,
                            upBound=upper_bound,
                            cat='Continuous'
                        )
                    else:
                        var = self.solver.NumVar(
                            lower_bound, upper_bound, var_name
                        )
                    self.variables[name][index] = var
            else:
                # 单一变量
                if isinstance(self.solver, pulp.LpProblem):
                    var = pulp.LpVariable(
                        name,
                        lowBound=lower_bound,
                        upBound=upper_bound,
                        cat='Continuous'
                    )
                else:
                    var = self.solver.NumVar(
                        lower_bound, upper_bound, name
                    )
                self.variables[name] = var
```

## 🏗️ 高级数据结构

### 1. 稀疏矩阵结构

#### 应用场景

- 大规模调度问题
- 内存优化
- 计算效率提升

#### 代码实现

```python
import scipy.sparse as sp
from collections import defaultdict

class SparseDecisionVariables:
    """稀疏决策变量的实现"""

    def __init__(self, solver, variable_configs):
        """
        初始化稀疏决策变量

        Args:
            solver: 求解器实例
            variable_configs: 变量配置列表
        """
        self.solver = solver
        self.variables = {}
        self.sparse_matrix = None
        self.index_mapping = {}
        self._create_sparse_variables(variable_configs)

    def _create_sparse_variables(self, configs):
        """创建稀疏决策变量"""
        for config in configs:
            name = config['name']
            sparse_pattern = config.get('sparse_pattern', 'all')
            non_zero_positions = config.get('non_zero_positions', [])

            if sparse_pattern == 'custom':
                # 自定义稀疏模式
                self.variables[name] = {}
                for (i, j) in non_zero_positions:
                    var_name = f"{name}_{i}_{j}"
                    if isinstance(self.solver, pulp.LpProblem):
                        var = pulp.LpVariable(var_name, cat='Binary')
                    else:
                        var = self.solver.BoolVar(var_name)
                    self.variables[name][(i, j)] = var
            elif sparse_pattern == 'diagonal':
                # 对角线模式
                size = config.get('size', 10)
                self.variables[name] = {}
                for i in range(size):
                    var_name = f"{name}_{i}_{i}"
                    if isinstance(self.solver, pulp.LpProblem):
                        var = pulp.LpVariable(var_name, cat='Binary')
                    else:
                        var = self.solver.BoolVar(var_name)
                    self.variables[name][(i, i)] = var

    def to_sparse_matrix(self, name, solution_values=None):
        """转换为稀疏矩阵"""
        if name not in self.variables:
            raise ValueError(f"Variable {name} not found")

        variables = self.variables[name]

        # 确定矩阵维度
        max_i = max(idx[0] for idx in variables.keys())
        max_j = max(idx[1] for idx in variables.keys())

        # 创建稀疏矩阵
        rows = []
        cols = []
        data = []

        for (i, j), var in variables.items():
            rows.append(i)
            cols.append(j)
            if solution_values is not None:
                data.append(solution_values.get(var, 0))
            else:
                data.append(1)  # 结构矩阵

        return sp.csr_matrix((data, (rows, cols)),
                           shape=(max_i + 1, max_j + 1))
```

### 2. 多维索引结构

#### 应用场景

- 复杂调度问题
- 多资源分配
- 时间-空间-资源三维决策

#### 代码实现

```python
class MultiIndexDecisionVariables:
    """多维索引决策变量的实现"""

    def __init__(self, solver, variable_configs):
        """
        初始化多维索引决策变量

        Args:
            solver: 求解器实例
            variable_configs: 变量配置列表
        """
        self.solver = solver
        self.variables = {}
        self.index_structure = {}
        self._create_multi_index_variables(variable_configs)

    def _create_multi_index_variables(self, configs):
        """创建多维索引变量"""
        for config in configs:
            name = config['name']
            index_structure = config['index_structure']
            variable_type = config.get('type', 'binary')

            # 生成所有索引组合
            from itertools import product
            index_combinations = list(product(*index_structure))

            self.variables[name] = {}
            self.index_structure[name] = index_structure

            for indices in index_combinations:
                # 创建变量名
                index_str = '_'.join(str(idx) for idx in indices)
                var_name = f"{name}_{index_str}"

                # 根据类型创建变量
                if isinstance(self.solver, pulp.LpProblem):
                    if variable_type == 'binary':
                        var = pulp.LpVariable(var_name, cat='Binary')
                    elif variable_type == 'integer':
                        lower = config.get('lower_bound', 0)
                        upper = config.get('upper_bound', float('inf'))
                        var = pulp.LpVariable(
                            var_name, lowBound=lower, upBound=upper, cat='Integer'
                        )
                    elif variable_type == 'continuous':
                        lower = config.get('lower_bound', 0)
                        upper = config.get('upper_bound', float('inf'))
                        var = pulp.LpVariable(
                            var_name, lowBound=lower, upBound=upper, cat='Continuous'
                        )
                else:
                    if variable_type == 'binary':
                        var = self.solver.BoolVar(var_name)
                    elif variable_type == 'integer':
                        lower = config.get('lower_bound', 0)
                        upper = config.get('upper_bound', float('inf'))
                        var = self.solver.IntVar(lower, upper, var_name)
                    elif variable_type == 'continuous':
                        lower = config.get('lower_bound', 0)
                        upper = config.get('upper_bound', float('inf'))
                        var = self.solver.NumVar(lower, upper, var_name)

                # 使用元组作为键
                self.variables[name][indices] = var

    def get_variable(self, name, *indices):
        """获取指定索引的变量"""
        if name not in self.variables:
            raise ValueError(f"Variable {name} not found")

        key = tuple(indices) if len(indices) > 1 else indices[0]
        return self.variables[name].get(key)

    def get_variables_by_slice(self, name, **slice_conditions):
        """通过切片条件获取变量集合"""
        if name not in self.variables:
            raise ValueError(f"Variable {name} not found")

        result = {}
        for indices, var in self.variables[name].items():
            match = True
            for i, (dim_name, condition) in enumerate(slice_conditions.items()):
                if callable(condition):
                    if not condition(indices[i]):
                        match = False
                        break
                else:
                    if indices[i] != condition:
                        match = False
                        break

            if match:
                result[indices] = var

        return result
```

## 🔧 变量管理工具

### 1. 变量访问器

```python
class VariableAccessor:
    """决策变量的统一访问接口"""

    def __init__(self, variable_containers):
        """
        初始化变量访问器

        Args:
            variable_containers: 变量容器字典
        """
        self.containers = variable_containers
        self.cache = {}

    def get(self, variable_name, *indices):
        """获取决策变量"""
        cache_key = (variable_name, indices)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 查找对应的变量容器
        for container in self.containers.values():
            if hasattr(container, 'variables') and variable_name in container.variables:
                var = container.get_variable(variable_name, *indices)
                self.cache[cache_key] = var
                return var

        raise ValueError(f"Variable {variable_name} not found")

    def get_solution_value(self, variable_name, *indices, solution=None):
        """获取变量的解值"""
        var = self.get(variable_name, *indices)

        if solution is not None:
            return solution.get(var, 0)
        elif hasattr(var, 'value'):
            return var.value
        elif hasattr(var, 'solution_value'):
            return var.solution_value()
        else:
            return 0
```

### 2. 变量验证器

```python
class VariableValidator:
    """决策变量的验证工具"""

    def __init__(self, variable_definitions):
        """
        初始化变量验证器

        Args:
            variable_definitions: 变量定义列表
        """
        self.definitions = variable_definitions
        self.validation_rules = {
            'bounds': self._validate_bounds,
            'type': self._validate_type,
            'index_structure': self._validate_index_structure
        }

    def validate_variables(self, variables):
        """验证所有决策变量"""
        validation_results = {}

        for var_name, var_data in self.definitions.items():
            validation_results[var_name] = {}

            for rule_name, rule_func in self.validation_rules.items():
                try:
                    result = rule_func(var_name, var_data, variables)
                    validation_results[var_name][rule_name] = result
                except Exception as e:
                    validation_results[var_name][rule_name] = {
                        'valid': False,
                        'error': str(e)
                    }

        return validation_results

    def _validate_bounds(self, var_name, definition, variables):
        """验证变量边界"""
        # 实现边界验证逻辑
        return {'valid': True, 'message': 'Bounds validation passed'}

    def _validate_type(self, var_name, definition, variables):
        """验证变量类型"""
        # 实现类型验证逻辑
        return {'valid': True, 'message': 'Type validation passed'}

    def _validate_index_structure(self, var_name, definition, variables):
        """验证索引结构"""
        # 实现索引结构验证逻辑
        return {'valid': True, 'message': 'Index structure validation passed'}
```

## 📊 性能优化

### 1. 内存优化策略

- **延迟加载**：按需创建决策变量
- **稀疏存储**：只存储必要的变量
- **索引压缩**：优化多维索引的存储
- **缓存机制**：缓存频繁访问的变量

### 2. 计算优化策略

- **批量操作**：批量创建和修改变量
- **向量化操作**：使用向量化计算
- **并行处理**：多线程变量操作
- **预编译**：预编译变量访问模式

---

## 🔗 相关知识模块

- **@代码实现库/十要素映射/约束条件映射**：决策变量在约束中的应用
- **@代码实现库/十要素映射/目标函数映射**：决策变量在目标中的使用
- **@代码实现库/架构模式/代码结构设计**：变量组织的最佳实践
- **@代码实现库/质量指南/性能优化指南**：变量操作的性能优化

---

## 📝 使用示例

### 完整的决策变量实现示例

```python
# 从TenElementModel解析决策变量配置
def parse_decision_variables(ten_element_model):
    """从十要素模型解析决策变量配置"""
    decision_variables = ten_element_model.get('decision_variables', {})

    variable_configs = []
    for var_name, var_config in decision_variables.items():
        config = {
            'name': var_name,
            'type': var_config.get('type', 'binary'),
            'description': var_config.get('description', ''),
            'lower_bound': var_config.get('lower_bound', 0),
            'upper_bound': var_config.get('upper_bound', float('inf')),
            'indices': var_config.get('indices', [])
        }
        variable_configs.append(config)

    return variable_configs

# 创建决策变量管理器
class DecisionVariableManager:
    """决策变量管理器"""

    def __init__(self, solver, ten_element_model):
        """
        初始化决策变量管理器

        Args:
            solver: 求解器实例
            ten_element_model: 十要素模型
        """
        self.solver = solver
        self.ten_element_model = ten_element_model
        self.containers = {}
        self.accessor = None
        self._initialize_variables()

    def _initialize_variables(self):
        """初始化所有决策变量"""
        variable_configs = parse_decision_variables(self.ten_element_model)

        # 按类型分组
        binary_configs = [c for c in variable_configs if c['type'] == 'binary']
        integer_configs = [c for c in variable_configs if c['type'] == 'integer']
        continuous_configs = [c for c in variable_configs if c['type'] == 'continuous']

        # 创建变量容器
        if binary_configs:
            self.containers['binary'] = BinaryDecisionVariables(self.solver, binary_configs)

        if integer_configs:
            self.containers['integer'] = IntegerDecisionVariables(self.solver, integer_configs)

        if continuous_configs:
            self.containers['continuous'] = ContinuousDecisionVariables(self.solver, continuous_configs)

        # 创建访问器
        self.accessor = VariableAccessor(self.containers)

    def get_variable(self, name, *indices):
        """获取决策变量"""
        return self.accessor.get(name, *indices)

    def validate_solution(self, solution):
        """验证解的有效性"""
        validator = VariableValidator(parse_decision_variables(self.ten_element_model))
        return validator.validate_variables(self.containers)
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-11-04
**下次审查**: 2025-12-04
**状态**: 初版完成

---

_本指南持续完善中，欢迎贡献更多决策变量映射的最佳实践！_
