# P2: 质量评估能力增强

**优先级**: 🟢 P2 - 90天内完成
**预计工期**: 8周
**负责模块**: 质量评估专家 + 代码生成
**影响范围**: Phase 3 代码生成 + Phase 4 质量保证

---

## 📋 问题描述

### 现状

**质量评估能力不足**:

```
当前能力:
  ✅ 语法检查 (Python syntax)
  ⚠️ 逻辑验证 (缺少标准和方法)
  ⚠️ 一致性检查 (主要依赖引用标记)
  ❌ 运行时测试 (缺失)
  ❌ 性能测试 (缺失)
  ❌ 基准对比 (缺失)

问题:
  → 92%可用率承诺难以保证
  → 可能放过"能运行但逻辑错误"的代码
  → 无法量化代码质量
  → 用户收到代码后仍需大量调试
```

---

## 🎯 解决方案

### 总体架构

```
┌──────────────────────────────────────────────────┐
│  增强的质量保证体系                               │
├──────────────────────────────────────────────────┤
│                                                   │
│  第1层: 静态分析                                  │
│  ├─ 语法检查 ✅                                   │
│  ├─ 代码规范 ✅                                   │
│  └─ 引用完整性 ✅                                 │
│                                                   │
│  第2层: 逻辑验证（新增）                          │
│  ├─ 单元测试自动生成 🆕                          │
│  ├─ 约束一致性测试 🆕                            │
│  └─ 目标函数测试 🆕                              │
│                                                   │
│  第3层: 运行时测试（新增）                        │
│  ├─ 简单案例测试 🆕                              │
│  ├─ 边界条件测试 🆕                              │
│  └─ 异常处理测试 🆕                              │
│                                                   │
│  第4层: 基准对比（新增）                          │
│  ├─ 经典测试集 🆕                                │
│  ├─ 性能基准 🆕                                  │
│  └─ 质量评分 🆕                                  │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## 🛠️ 实施步骤

### Step 1: 单元测试自动生成（Week 1-2）

#### 1.1 新增测试生成任务

**新建文件**: `bmad/aps/tasks/generate-unit-tests.md`

````markdown
# Task: Generate Unit Tests

**任务ID**: `generate-unit-tests`
**版本**: V1.0
**用途**: 基于十要素和生成的代码，自动生成单元测试

## 输入

- implementation_code: 生成的Python代码
- ten_element_model: 十要素模型

## 处理逻辑

### 为约束生成测试

```python
def generate_constraint_tests(constraints, code):
    """
    为每个约束生成单元测试

    测试覆盖:
    1. 合法输入 → 返回True
    2. 非法输入 → 返回False
    3. 边界条件
    """
    test_code = []

    test_code.append("import unittest")
    test_code.append("from solver import *")
    test_code.append("")
    test_code.append("class TestConstraints(unittest.TestCase):")
    test_code.append("")

    for constraint in constraints:
        constraint_name = constraint['name']
        constraint_id = constraint['id']

        # 测试1: 合法输入
        test_code.append(f"    def test_{constraint_name}_valid(self):")
        test_code.append(f'        """测试{constraint_id} - 合法输入"""')
        test_code.append(f"        # 构造合法场景")
        test_code.append(f"        solution = create_valid_solution()")
        test_code.append(f"        result = validate_{constraint_name}(solution)")
        test_code.append(f"        self.assertTrue(result, '合法输入应该通过验证')")
        test_code.append("")

        # 测试2: 非法输入
        test_code.append(f"    def test_{constraint_name}_invalid(self):")
        test_code.append(f'        """测试{constraint_id} - 非法输入"""')
        test_code.append(f"        # 构造违反约束的场景")
        test_code.append(f"        solution = create_invalid_solution_{constraint_name}()")
        test_code.append(f"        result = validate_{constraint_name}(solution)")
        test_code.append(f"        self.assertFalse(result, '非法输入应该检测出来')")
        test_code.append("")

    return "\n".join(test_code)
```
````

### 为目标函数生成测试

```python
def generate_objective_tests(objectives, code):
    """
    为每个目标函数生成单元测试

    测试覆盖:
    1. 简单案例的正确性
    2. 边界值
    3. 数值精度
    """
    test_code = []

    test_code.append("class TestObjectives(unittest.TestCase):")
    test_code.append("")

    for objective in objectives:
        obj_name = objective['name']

        # 测试简单案例
        test_code.append(f"    def test_{obj_name}_simple_case(self):")
        test_code.append(f'        """测试{obj_name} - 简单案例"""')
        test_code.append(f"        # 已知输入和期望输出")
        test_code.append(f"        solution = create_simple_solution()")
        test_code.append(f"        result = calculate_{obj_name}(solution)")
        test_code.append(f"        expected = {get_expected_value(obj_name)}")
        test_code.append(f"        self.assertAlmostEqual(result, expected, places=2)")
        test_code.append("")

        # 测试边界值
        test_code.append(f"    def test_{obj_name}_boundary(self):")
        test_code.append(f'        """测试{obj_name} - 边界值"""')
        test_code.append(f"        # 空解")
        test_code.append(f"        empty_solution = create_empty_solution()")
        test_code.append(f"        result = calculate_{obj_name}(empty_solution)")
        test_code.append(f"        self.assertEqual(result, 0.0)")
        test_code.append("")

    return "\n".join(test_code)
```

### 为数据加载生成测试

```python
def generate_data_loading_tests(input_data_spec, code):
    """
    为数据加载函数生成测试

    测试覆盖:
    1. 正常文件加载
    2. 文件不存在
    3. 格式错误
    4. 缺失字段
    """
    test_code = []

    test_code.append("class TestDataLoading(unittest.TestCase):")
    test_code.append("")

    sources = input_data_spec.get('sources', [])
    for source in sources:
        file_name = source['file_path'].split('/')[-1].replace('.csv', '')
        func_name = f"load_{file_name}"

        # 测试正常加载
        test_code.append(f"    def test_{func_name}_success(self):")
        test_code.append(f'        """测试{func_name} - 正常加载"""')
        test_code.append(f"        df = {func_name}('test_data/{file_name}.csv')")
        test_code.append(f"        self.assertIsNotNone(df)")
        test_code.append(f"        self.assertGreater(len(df), 0)")
        test_code.append("")

        # 测试文件不存在
        test_code.append(f"    def test_{func_name}_file_not_found(self):")
        test_code.append(f'        """测试{func_name} - 文件不存在"""')
        test_code.append(f"        with self.assertRaises(FileNotFoundError):")
        test_code.append(f"            {func_name}('nonexistent.csv')")
        test_code.append("")

        # 测试缺失字段
        test_code.append(f"    def test_{func_name}_missing_columns(self):")
        test_code.append(f'        """测试{func_name} - 缺失必需字段"""')
        test_code.append(f"        with self.assertRaises(ValueError):")
        test_code.append(f"            {func_name}('test_data/{file_name}_incomplete.csv')")
        test_code.append("")

    return "\n".join(test_code)
```

## 输出

- test_code: 完整的单元测试代码
- test_coverage: 测试覆盖率估算

````

#### 1.2 在代码生成流程中集成

**文件**: `bmad/aps/workflows/scheduling-orchestration/workflow.yaml`

**位置**: Step 3.6之后新增

```yaml
- step_id: "3.6.7"
  name: "🧪 生成单元测试"
  action: "exec"
  target: "bmad/aps/tasks/generate-unit-tests.md"
  description: "自动生成单元测试，提升代码可靠性"

  inputs:
    - implementation_code
    - ten_element_model: "${phase_1_5_state.state_data.ten_element_model}"

  outputs:
    - test_code
    - test_coverage_estimate

- step_id: "3.6.8"
  name: "💾 保存测试文件"
  action: "exec"
  target: "bmad/aps/tasks/save-test-file.md"

  inputs:
    - test_code
    - output_folder: "${config.output_folder}"

  outputs:
    - test_file_path
````

---

### Step 2: 基准测试库建设（Week 3-5）

#### 2.1 建立基准测试集

**新建目录和文件**: `bmad/aps/benchmarks/`

```yaml
# bmad/aps/benchmarks/benchmark-library.yaml

benchmark_library:
  version: '1.0'
  categories:
    # 作业车间调度问题
    job_shop_scheduling:
      - name: 'LA01'
        description: 'Lawrence 10x5 JSSP'
        source: 'Lawrence, 1984'
        problem_size:
          jobs: 10
          machines: 5
        optimal_solution: 666
        data_file: 'benchmarks/jssp/LA01.txt'
        timeout: 60
        acceptance_criteria:
          objective_value_max: 700 # 允许5%偏差
          runtime_max: 60
          constraints_satisfied: true

      - name: 'FT06'
        description: 'Fisher-Thompson 6x6'
        problem_size:
          jobs: 6
          machines: 6
        optimal_solution: 55
        data_file: 'benchmarks/jssp/FT06.txt'

    # 柔性作业车间调度
    flexible_job_shop:
      - name: 'Mk01'
        description: 'Brandimarte 10x6 FJSP'
        problem_size:
          jobs: 10
          machines: 6
        best_known: 40
        data_file: 'benchmarks/fjsp/Mk01.txt'

    # 车辆路径问题
    vehicle_routing:
      - name: 'C101'
        description: 'Solomon C101 VRPTW'
        problem_size:
          customers: 100
          vehicles: 25
        optimal_solution: 828.94
        data_file: 'benchmarks/vrp/C101.txt'
        timeout: 300
```

#### 2.2 创建基准测试运行器

**新建文件**: `bmad/aps/scripts/run-benchmarks.py`

```python
#!/usr/bin/env python3
"""
基准测试运行器

Usage:
    python scripts/run-benchmarks.py --code solver.py --benchmarks LA01,FT06
"""

import argparse
import yaml
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class BenchmarkRunner:
    """基准测试运行器"""

    def __init__(self, benchmark_file: str = "bmad/aps/benchmarks/benchmark-library.yaml"):
        with open(benchmark_file) as f:
            self.benchmarks = yaml.safe_load(f)

    def run_benchmark(self, code_file: str, benchmark_name: str) -> dict:
        """
        运行单个基准测试

        Returns:
            result: {
                "benchmark": str,
                "status": "PASS" | "FAIL" | "TIMEOUT",
                "objective_value": float,
                "runtime": float,
                "optimal_gap": float,
                "constraints_ok": bool,
                "error_message": str | None
            }
        """
        # 查找基准测试
        benchmark = self.find_benchmark(benchmark_name)
        if not benchmark:
            return {"status": "NOT_FOUND", "benchmark": benchmark_name}

        print(f"\n▶️ 运行基准测试: {benchmark_name}")
        print(f"   问题规模: {benchmark['problem_size']}")
        print(f"   最优解: {benchmark.get('optimal_solution', 'N/A')}")

        # 准备数据
        data_file = benchmark['data_file']
        output_file = f"output/{benchmark_name}_result.csv"

        # 运行代码
        start_time = time.time()
        try:
            result = subprocess.run(
                ["python", code_file, data_file, output_file],
                timeout=benchmark.get('timeout', 300),
                capture_output=True,
                text=True
            )
            runtime = time.time() - start_time

            if result.returncode != 0:
                return {
                    "benchmark": benchmark_name,
                    "status": "FAIL",
                    "error_message": result.stderr,
                    "runtime": runtime
                }

            # 解析结果
            objective_value = self.parse_objective(output_file, benchmark)
            constraints_ok = self.validate_constraints(output_file, benchmark)

            # 计算与最优解的gap
            optimal = benchmark.get('optimal_solution')
            if optimal:
                gap = (objective_value - optimal) / optimal * 100
            else:
                gap = None

            # 判断是否通过
            criteria = benchmark.get('acceptance_criteria', {})
            passed = True

            if 'objective_value_max' in criteria:
                passed &= (objective_value <= criteria['objective_value_max'])

            if 'runtime_max' in criteria:
                passed &= (runtime <= criteria['runtime_max'])

            passed &= constraints_ok

            return {
                "benchmark": benchmark_name,
                "status": "PASS" if passed else "FAIL",
                "objective_value": objective_value,
                "runtime": runtime,
                "optimal_gap": gap,
                "constraints_ok": constraints_ok
            }

        except subprocess.TimeoutExpired:
            return {
                "benchmark": benchmark_name,
                "status": "TIMEOUT",
                "runtime": benchmark.get('timeout', 300)
            }
        except Exception as e:
            return {
                "benchmark": benchmark_name,
                "status": "ERROR",
                "error_message": str(e)
            }

    def run_all_benchmarks(self, code_file: str, category: str = None) -> list:
        """运行所有基准测试"""
        results = []

        benchmarks_to_run = self.get_benchmarks_by_category(category)

        for benchmark_name in benchmarks_to_run:
            result = self.run_benchmark(code_file, benchmark_name)
            results.append(result)

        return results

    def generate_report(self, results: list) -> dict:
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.get("status") == "PASS"),
            "failed": sum(1 for r in results if r.get("status") == "FAIL"),
            "timeout": sum(1 for r in results if r.get("status") == "TIMEOUT"),
            "results": results,
            "summary": {
                "avg_runtime": None,
                "avg_gap": None,
                "pass_rate": None
            }
        }

        # 计算平均值
        successful = [r for r in results if r.get("status") == "PASS"]
        if successful:
            report["summary"]["avg_runtime"] = sum(r["runtime"] for r in successful) / len(successful)

            gaps = [r["optimal_gap"] for r in successful if r.get("optimal_gap") is not None]
            if gaps:
                report["summary"]["avg_gap"] = sum(gaps) / len(gaps)

        report["summary"]["pass_rate"] = report["passed"] / report["total_tests"] if report["total_tests"] > 0 else 0

        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行基准测试")
    parser.add_argument("--code", required=True, help="代码文件路径")
    parser.add_argument("--benchmarks", help="基准测试名称（逗号分隔）")
    parser.add_argument("--category", help="测试类别")
    parser.add_argument("--output", default="benchmark_report.json", help="输出报告路径")

    args = parser.parse_args()

    runner = BenchmarkRunner()

    if args.benchmarks:
        benchmark_list = args.benchmarks.split(",")
        results = [runner.run_benchmark(args.code, b.strip()) for b in benchmark_list]
    else:
        results = runner.run_all_benchmarks(args.code, args.category)

    report = runner.generate_report(results)

    # 保存报告
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # 打印摘要
    print("\n" + "="*60)
    print("📊 基准测试报告")
    print("="*60)
    print(f"总测试数: {report['total_tests']}")
    print(f"通过: {report['passed']} ✅")
    print(f"失败: {report['failed']} ❌")
    print(f"超时: {report['timeout']} ⏱️")
    print(f"通过率: {report['summary']['pass_rate']:.1%}")
    if report['summary']['avg_gap'] is not None:
        print(f"平均Gap: {report['summary']['avg_gap']:.2f}%")
    print(f"\n详细报告已保存到: {args.output}")
```

---

### Step 3: 集成到质量门禁（Week 6-8）

#### 3.1 增强质量评估专家

**文件**: `bmad/aps/agents/quality-evaluator.md`

**新增能力**:

````markdown
## 新增质量检查维度

### 3. 运行时测试（新增）

**检查内容**:

- 运行单元测试
- 检查测试通过率
- 分析失败原因

**命令**: `*run-unit-tests`

```python
def run_unit_tests(test_file_path):
    """运行单元测试"""
    result = subprocess.run(
        ["python", "-m", "pytest", test_file_path, "-v"],
        capture_output=True
    )

    return {
        "passed": result.returncode == 0,
        "output": result.stdout.decode(),
        "test_count": parse_test_count(result.stdout),
        "pass_rate": calculate_pass_rate(result.stdout)
    }
```
````

### 4. 基准测试（新增）

**检查内容**:

- 运行标准基准测试
- 对比最优解gap
- 评估性能表现

**命令**: `*run-benchmarks`

### 5. 综合质量评分（更新）

```python
def calculate_quality_score(all_checks):
    """
    计算综合质量评分

    权重分配:
    - 语法检查: 10%
    - 引用完整性: 15%
    - 单元测试通过率: 30%
    - 基准测试表现: 30%
    - 代码规范: 15%
    """
    weights = {
        "syntax": 0.10,
        "citations": 0.15,
        "unit_tests": 0.30,
        "benchmarks": 0.30,
        "code_style": 0.15
    }

    scores = {}
    scores["syntax"] = 1.0 if all_checks["syntax_check"]["passed"] else 0.0
    scores["citations"] = all_checks["citation_check"]["coverage"]
    scores["unit_tests"] = all_checks["unit_test_results"]["pass_rate"]
    scores["benchmarks"] = calculate_benchmark_score(all_checks["benchmark_results"])
    scores["code_style"] = all_checks["style_check"]["score"]

    total = sum(scores[k] * weights[k] for k in scores)

    return {
        "total_score": total,
        "grade": get_grade(total),
        "dimension_scores": scores
    }
```

```

---

## ✅ 验证清单

- [ ] 单元测试生成任务已创建
- [ ] 基准测试库已建立（10个案例）
- [ ] 基准测试运行器已实现
- [ ] 质量评估专家已增强
- [ ] 工作流已集成新检查
- [ ] 端到端测试通过
- [ ] 质量评分算法已验证

---

## 📊 预期收益

### 短期收益（90天）
- ✅ 单元测试覆盖率50%+
- ✅ 建立10个基准测试案例
- ✅ 质量评分更科学

### 中期收益（6个月）
- ✅ 代码可用率：92% → 95%+
- ✅ 用户调试时间减少40%
- ✅ 建立行业基准

### 长期收益
- ✅ 形成质量标准
- ✅ 增强产品可信度
- ✅ 支撑商业化

---

## 📞 相关资源

- **单元测试任务**: `bmad/aps/tasks/generate-unit-tests.md`
- **基准测试库**: `bmad/aps/benchmarks/`
- **测试运行器**: `bmad/aps/scripts/run-benchmarks.py`

---

**创建日期**: 2025-10-31
**最后更新**: 2025-10-31
**状态**: ⏳ 待实施
```
