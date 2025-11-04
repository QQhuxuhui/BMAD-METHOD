# 专家主导的代码生成任务

**Code Generation by Expert Task**

---

**任务ID**: generate-code-by-expert
**版本**: 1.0.0
**创建日期**: 2025-11-04
**负责专家**: 代码实现专家（吴实现）
**预计时间**: 20-25分钟

---

## 🎯 任务概述

本任务由代码实现专家主导，基于用户确认的技术方案和TenElementModel，生成高质量的调度优化代码。确保代码与十要素模型严格对齐，符合工程化标准。

## 📋 输入要求

### 必需输入

1. **技术方案文档** (`solution_document`)
   - 格式：Markdown文件路径
   - 内容：完整的6个技术章节 + 附录
   - 验证：必须通过方案一致性检查

2. **TenElementModel** (`ten_element_model`)
   - 格式：YAML对象
   - 内容：完整的10个要素定义
   - 验证：必须包含所有要素的完整定义

3. **算法推荐** (`algorithm_recommendations`)
   - 格式：专家分析结果
   - 内容：具体的算法选择和参数配置
   - 验证：必须来自算法专家的专业推荐

### 可选输入

4. **约束分析** (`constraint_analysis`) - 来自约束专家
5. **目标分析** (`objective_analysis`) - 来自目标专家
6. **领域适配建议** (`domain_analysis`) - 来自领域专家

## 🔧 执行流程

### Phase 1: 方案理解与需求分析 (3-5分钟)

#### 步骤1.1: 深度理解技术方案

```yaml
活动:
  - 仔细阅读技术方案文档的所有章节
  - 提取关键设计决策和架构要求
  - 识别算法、约束、目标的具体要求
  - 评估实现的复杂度和风险点

检查清单:
  - [ ] 理解问题定义和建模方法
  - [ ] 掌握领域适配方案
  - [ ] 明确约束处理策略
  - [ ] 了解目标优化策略
  - [ ] 熟悉算法选择与配置
  - [ ] 理解实现路线图
  - [ ] 掌握TenElementModel完整定义
```

#### 步骤1.2: 解析十要素模型

```yaml
活动:
  - 逐项分析TenElementModel的10个要素
  - 建立要素间的依赖关系图
  - 识别关键要素和实现优先级
  - 规划要素到代码的映射策略

要素分析矩阵:
  1. 决策变量: 变量类型、维度、边界
  2. 参数: 配置参数、数据参数
  3. 约束: 约束类型、复杂度、实现方法
  4. 优化目标: 目标数量、权重、优化方向
  5. 算法: 算法类型、参数、性能要求
  6. 时间模型: 时间表示、动态性
  7. 不确定性: 随机性、场景、鲁棒性
  8. 求解配置: 求解器选择、参数调优
  9. 输入数据: 数据格式、规模、来源
  10. 输出格式: 结果表示、可视化
```

#### 步骤1.3: 制定实现策略

```yaml
输出: 实现策略文档

内容:
  - 代码架构设计方案
  - 模块划分策略
  - 算法实现计划
  - 质量保证措施
  - 风险缓解方案

决策点:
  - 使用哪个求解器框架 (pulp/or-tools/custom)
  - 是否需要特殊的数据结构
  - 性能优化策略
  - 错误处理机制
```

### Phase 2: 代码架构设计 (4-6分钟)

#### 步骤2.1: 设计整体代码架构

```yaml
架构原则:
  - 单一职责: 每个模块职责明确
  - 开放封闭: 易于扩展，稳定核心
  - 依赖倒置: 依赖抽象而非实现
  - 接口隔离: 接口设计精简专用

目录结构设计:
```

project_name/
├── main.py # 主执行入口
├── config/
│ ├── **init**.py
│ ├── solver_config.py # 求解器配置
│ └── model_config.py # 模型配置
├── models/
│ ├── **init**.py
│ ├── decision_variables.py # 决策变量
│ ├── constraints.py # 约束定义
│ ├── objectives.py # 目标函数
│ └── data_structures.py # 数据结构
├── algorithms/
│ ├── **init**.py
│ ├── base_algorithm.py # 算法基类
│ ├── [specific_algorithm].py # 具体算法实现
│ └── solver_wrapper.py # 求解器封装
├── utils/
│ ├── **init**.py
│ ├── data_loader.py # 数据加载
│ ├── solution_processor.py # 解处理
│ └── validators.py # 验证工具
├── tests/
│ ├── **init**.py
│ ├── test_models.py # 模型测试
│ ├── test_algorithms.py # 算法测试
│ └── test_integration.py # 集成测试
└── examples/
├── sample_data.py # 示例数据
└── usage_example.py # 使用示例

````

#### 步骤2.2: 定义模块接口规范
```yaml
接口设计原则:
  - 统一命名规范
  - 明确输入输出类型
  - 完整的文档说明
  - 适当的错误处理

核心接口:
  DecisionVariableInterface:
    - create_variables(): 创建决策变量
    - get_variable(): 获取变量
    - validate_structure(): 验证结构

  ConstraintInterface:
    - add_constraint(): 添加约束
    - validate_constraints(): 验证约束
    - get_constraint_info(): 获取约束信息

  ObjectiveInterface:
    - set_objective(): 设置目标
    - get_objective_value(): 获取目标值
    - multi_objective_handler(): 多目标处理

  AlgorithmInterface:
    - solve(): 求解
    - get_solution(): 获取解
    - get_performance_metrics(): 获取性能指标
````

#### 步骤2.3: 设计数据流和控制流

```yaml
数据流设计: 输入数据 → 数据验证 → 模型构建 → 算法求解 → 结果处理 → 输出结果

控制流设计: main()
  ├── load_configuration()
  ├── load_data()
  ├── build_model()
  │   ├── create_decision_variables()
  │   ├── add_constraints()
  │   └── set_objectives()
  ├── solve_problem()
  ├── process_solution()
  ├── validate_solution()
  └── generate_output()
```

### Phase 3: 核心代码实现 (8-12分钟)

#### 步骤3.1: 实现决策变量模块

```python
# 基于十要素映射生成决策变量代码
def generate_decision_variables_code(ten_element_model):
    """生成决策变量代码"""

    decision_variables = ten_element_model.get('decision_variables', {})

    code_template = '''
from typing import Dict, List, Tuple, Any
import pulp
import ortools.linear_solver.pywraplp as ortools

class DecisionVariables:
    """决策变量管理类"""

    def __init__(self, solver, model_config):
        self.solver = solver
        self.config = model_config
        self.variables = {}
        self._create_variables()

    def _create_variables(self):
        """根据十要素模型创建决策变量"""
        # 这里会根据具体的决策变量配置生成代码
        pass

    def get_variable(self, name: str, *indices) -> Any:
        """获取决策变量"""
        pass

    def validate_structure(self) -> bool:
        """验证变量结构"""
        pass
'''

    # 根据具体配置定制代码
    return customize_code_template(code_template, decision_variables)
```

#### 步骤3.2: 实现约束条件模块

```python
def generate_constraints_code(constraints_config, decision_variables):
    """生成约束条件代码"""

    code_template = '''
class Constraints:
    """约束条件管理类"""

    def __init__(self, solver, decision_variables, constraint_config):
        self.solver = solver
        self.decision_vars = decision_variables
        self.config = constraint_config
        self.constraints = {}
        self._add_constraints()

    def _add_constraints(self):
        """添加所有约束条件"""
        # 根据约束配置添加约束
        pass

    def add_capacity_constraint(self, resources, capacity):
        """添加容量约束"""
        pass

    def add_time_window_constraint(self, tasks, time_windows):
        """添加时间窗约束"""
        pass

    def add_precedence_constraint(self, precedence_relations):
        """添加优先级约束"""
        pass

    def validate_constraints(self) -> bool:
        """验证约束条件"""
        pass
'''

    return customize_code_template(code_template, constraints_config)
```

#### 步骤3.3: 实现目标函数模块

```python
def generate_objectives_code(objectives_config, decision_variables):
    """生成目标函数代码"""

    code_template = '''
class Objectives:
    """目标函数管理类"""

    def __init__(self, solver, decision_variables, objectives_config):
        self.solver = solver
        self.decision_vars = decision_variables
        self.config = objectives_config
        self.objectives = {}
        self._set_objectives()

    def _set_objectives(self):
        """设置目标函数"""
        # 根据目标配置设置目标
        pass

    def set_single_objective(self, objective_expr, sense='Minimize'):
        """设置单目标函数"""
        pass

    def set_multi_objective(self, objectives, weights, method='weighted_sum'):
        """设置多目标函数"""
        pass

    def get_objective_value(self, solution=None):
        """获取目标函数值"""
        pass
'''

    return customize_code_template(code_template, objectives_config)
```

#### 步骤3.4: 实现算法模块

```python
def generate_algorithm_code(algorithm_config, decision_variables, constraints, objectives):
    """生成算法实现代码"""

    algorithm_type = algorithm_config.get('type')
    solver_type = algorithm_config.get('solver', 'ortools')

    if algorithm_type == 'exact':
        return generate_exact_algorithm_code(solver_type, algorithm_config)
    elif algorithm_type == 'heuristic':
        return generate_heuristic_algorithm_code(solver_type, algorithm_config)
    elif algorithm_type == 'meta_heuristic':
        return generate_meta_heuristic_code(solver_type, algorithm_config)
    else:
        raise ValueError(f"Unsupported algorithm type: {algorithm_type}")
```

### Phase 4: 代码集成和测试 (3-5分钟)

#### 步骤4.1: 集成所有模块

```python
def generate_main_integration_code():
    """生成主程序集成代码"""

    code_template = '''
#!/usr/bin/env python3
"""
调度优化主程序
基于TenElementModel和专家建议生成
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.solver_config import SolverConfig
from config.model_config import ModelConfig
from models.decision_variables import DecisionVariables
from models.constraints import Constraints
from models.objectives import Objectives
from algorithms.solver_wrapper import SolverWrapper
from utils.data_loader import DataLoader
from utils.solution_processor import SolutionProcessor
from utils.validators import ModelValidator

class SchedulingOptimizer:
    """调度优化主类"""

    def __init__(self, config_path=None):
        self.config_path = config_path or "config/"
        self.solver_config = SolverConfig(self.config_path)
        self.model_config = ModelConfig(self.config_path)
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def solve(self, data_path=None):
        """求解调度优化问题"""
        try:
            # 1. 加载配置和数据
            self.logger.info("加载配置和数据...")
            data = self._load_data(data_path)

            # 2. 创建求解器
            self.logger.info("创建求解器...")
            solver = self._create_solver()

            # 3. 构建模型
            self.logger.info("构建优化模型...")
            model = self._build_model(solver, data)

            # 4. 求解
            self.logger.info("开始求解...")
            solution = self._solve_problem(model)

            # 5. 处理解
            self.logger.info("处理求解结果...")
            processed_solution = self._process_solution(solution)

            # 6. 验证解
            self.logger.info("验证解的有效性...")
            if self._validate_solution(processed_solution):
                self.logger.info("求解成功完成！")
                return processed_solution
            else:
                self.logger.error("解验证失败！")
                return None

        except Exception as e:
            self.logger.error(f"求解过程出错: {str(e)}")
            raise

    def _load_data(self, data_path):
        """加载数据"""
        loader = DataLoader()
        return loader.load(data_path)

    def _create_solver(self):
        """创建求解器"""
        return SolverWrapper(
            solver_type=self.solver_config.solver_type,
            solver_params=self.solver_config.solver_params
        )

    def _build_model(self, solver, data):
        """构建优化模型"""
        # 创建决策变量
        decision_vars = DecisionVariables(solver, self.model_config)

        # 添加约束条件
        constraints = Constraints(solver, decision_vars, self.model_config)

        # 设置目标函数
        objectives = Objectives(solver, decision_vars, self.model_config)

        return {
            'decision_variables': decision_vars,
            'constraints': constraints,
            'objectives': objectives
        }

    def _solve_problem(self, model):
        """求解问题"""
        # 这里会根据具体的算法配置调用相应的求解方法
        solver = SolverWrapper()
        return solver.solve(model)

    def _process_solution(self, solution):
        """处理求解结果"""
        processor = SolutionProcessor()
        return processor.process(solution)

    def _validate_solution(self, solution):
        """验证解的有效性"""
        validator = ModelValidator()
        return validator.validate(solution)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='调度优化求解器')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--data', help='数据文件路径')
    parser.add_argument('--output', help='输出文件路径')

    args = parser.parse_args()

    # 创建优化器
    optimizer = SchedulingOptimizer(args.config)

    # 求解
    solution = optimizer.solve(args.data)

    # 输出结果
    if solution:
        if args.output:
            solution.save_to_file(args.output)
        else:
            solution.print_summary()
    else:
        print("求解失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    return code_template
```

#### 步骤4.2: 生成测试代码

```python
def generate_test_code():
    """生成测试代码"""

    test_template = '''
import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.decision_variables import DecisionVariables
from models.constraints import Constraints
from models.objectives import Objectives
from config.model_config import ModelConfig

class TestSchedulingModel(unittest.TestCase):
    """调度模型测试类"""

    def setUp(self):
        """测试初始化"""
        self.config = ModelConfig("config/")
        self.solver = self._create_test_solver()

    def _create_test_solver(self):
        """创建测试求解器"""
        import pulp
        return pulp.LpProblem("test_model")

    def test_decision_variables_creation(self):
        """测试决策变量创建"""
        decision_vars = DecisionVariables(self.solver, self.config)

        # 测试变量是否正确创建
        self.assertIsNotNone(decision_vars.variables)

        # 测试变量访问
        if decision_vars.variables:
            first_var_name = list(decision_vars.variables.keys())[0]
            var = decision_vars.get_variable(first_var_name)
            self.assertIsNotNone(var)

    def test_constraints_addition(self):
        """测试约束添加"""
        decision_vars = DecisionVariables(self.solver, self.config)
        constraints = Constraints(self.solver, decision_vars, self.config)

        # 测试约束是否正确添加
        self.assertIsNotNone(constraints.constraints)

    def test_objectives_setting(self):
        """测试目标函数设置"""
        decision_vars = DecisionVariables(self.solver, self.config)
        objectives = Objectives(self.solver, decision_vars, self.config)

        # 测试目标函数是否正确设置
        self.assertIsNotNone(objectives.objectives)

    def test_model_integration(self):
        """测试模型集成"""
        # 创建完整的模型
        decision_vars = DecisionVariables(self.solver, self.config)
        constraints = Constraints(self.solver, decision_vars, self.config)
        objectives = Objectives(self.solver, decision_vars, self.config)

        # 验证模型完整性
        self.assertIsNotNone(decision_vars.variables)
        self.assertIsNotNone(constraints.constraints)
        self.assertIsNotNone(objectives.objectives)

if __name__ == '__main__':
    unittest.main()
'''

    return test_template
```

## 📤 输出要求

### 必需输出

1. **可执行代码包**
   - 完整的Python包结构
   - 包含所有必要的模块文件
   - 符合PEP8代码规范
   - 完整的类型注解和文档字符串

2. **代码文档**
   - README.md：项目介绍和使用指南
   - API文档：所有公共接口的详细说明
   - 架构文档：系统架构和设计决策
   - 使用示例：完整的使用示例代码

3. **实现说明**
   - 技术实现报告
   - 十要素映射对照表
   - 算法实现细节说明
   - 性能基准测试结果

### 可选输出

4. **测试代码**
   - 单元测试套件
   - 集成测试用例
   - 性能基准测试
   - 测试覆盖率报告

5. **配置文件**
   - 求解器配置
   - 模型参数配置
   - 环境配置文件

6. **示例数据**
   - 测试数据集
   - 示例输入输出
   - 性能测试数据

## ✅ 质量标准

### 十要素映射完整性检查

- [ ] 决策变量：100%映射，类型正确
- [ ] 参数配置：完整配置，验证机制
- [ ] 约束条件：正确编码，逻辑一致
- [ ] 优化目标：数学等价，权重正确
- [ ] 算法框架：正确实现，参数匹配
- [ ] 时间模型：准确处理，动态支持
- [ ] 不确定性：适当建模，场景覆盖
- [ ] 求解配置：优化调参，性能保证
- [ ] 数据接口：格式标准，验证完整
- [ ] 输出格式：结果完整，可视化支持

### 代码质量检查

- [ ] PEP8合规性：0个风格错误
- [ ] 类型注解：≥90%覆盖率
- [ ] 文档字符串：≥95%覆盖率
- [ ] 代码复杂度：McCabe < 10
- [ ] 测试覆盖率：≥90%

### 功能性检查

- [ ] 代码可执行性：能够正常运行
- [ ] 算法正确性：与理论一致
- [ ] 结果准确性：通过验证测试
- [ ] 性能要求：满足时间指标
- [ ] 错误处理：异常情况处理完善

## 🔍 验证机制

### 自动化验证

```python
def validate_code_generation(implementation_result):
    """自动化代码生成验证"""

    validator = CodeGenerationValidator()

    # 1. 十要素映射验证
    mapping_validation = validator.validate_ten_element_mapping(
        implementation_result.decision_variables,
        implementation_result.constraints,
        implementation_result.objectives
    )

    # 2. 代码质量验证
    quality_validation = validator.validate_code_quality(
        implementation_result.code_files
    )

    # 3. 功能性验证
    functional_validation = validator.validate_functionality(
        implementation_result.executable_code
    )

    # 4. 性能验证
    performance_validation = validator.validate_performance(
        implementation_result.benchmark_results
    )

    return {
        'mapping_validation': mapping_validation,
        'quality_validation': quality_validation,
        'functional_validation': functional_validation,
        'performance_validation': performance_validation,
        'overall_result': all([
            mapping_validation['passed'],
            quality_validation['passed'],
            functional_validation['passed'],
            performance_validation['passed']
        ])
    }
```

### 人工验证点

- [ ] 代码架构合理性审查
- [ ] 算法实现正确性检查
- [ ] 接口设计一致性验证
- [ ] 文档完整性确认
- [ ] 用户体验评估

## 🚨 错误处理

### 常见错误及解决方案

1. **十要素映射不完整**
   - 错误：某些要素没有对应的代码实现
   - 解决：检查要素定义，补充缺失的实现

2. **算法实现错误**
   - 错误：算法逻辑与理论不符
   - 解决：参考算法专家的建议，重新实现

3. **代码质量不达标**
   - 错误：违反PEP8规范或缺少文档
   - 解决：使用代码格式化工具，补充文档

4. **性能不满足要求**
   - 错误：执行时间或内存使用超标
   - 解决：优化算法和数据结构

5. **集成问题**
   - 错误：模块间接口不匹配
   - 解决：检查接口定义，统一数据格式

## 📞 支持和联系

**技术支持**：代码实现专家（吴实现）
**专家咨询**：可咨询算法专家、约束专家、目标专家
**问题反馈**：通过项目Issue系统报告问题
**文档更新**：定期更新最佳实践和模板

---

**任务版本**: 1.0.0
**最后更新**: 2025-11-04
**下次审查**: 2025-12-04
**状态**: 就绪实施

---

_本任务模板持续优化中，欢迎反馈使用体验！_
