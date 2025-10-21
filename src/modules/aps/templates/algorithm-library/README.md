# 算法专家知识库 - Algorithm Library

**专家**: 张效率 (Algorithm Expert)
**版本**: V4.2
**用途**: 调度算法推荐、复杂度分析、性能优化、代码生成

## 知识库结构

```
algorithm-library/
├── README.md                    # 本文档
├── greedy/                      # 贪心算法
│   ├── basic-greedy.md
│   ├── priority-based.md
│   └── constructive-heuristics.md
├── heuristic/                   # 启发式算法
│   ├── 遗传算法.md
│   ├── 构造式启发式.md
│   ├── 改进式启发式.md
│   └── 贪心算法.md
├── exact/                       # 精确算法
│   ├── branch-and-bound.md
│   ├── branch-and-cut.md
│   ├── dynamic-programming.md
│   ├── integer-programming.md
│   └── constraint-programming.md
├── hybrid/                      # 混合算法
│   ├── matheuristics.md
│   ├── large-neighborhood-search.md
│   └── adaptive-hybrid.md
├── local-search/                # 局部搜索
│   ├── hill-climbing.md
│   ├── iterated-local-search.md
│   └── guided-local-search.md
└── specialized/                 # 领域特定算法
    ├── column-generation.md
    ├── benders-decomposition.md
    └── lagrangian-relaxation.md
```

## 算法分类矩阵

### 按问题规模

| 规模 | 决策变量数 | 推荐算法           | 引用路径                                                                     |
| ---- | ---------- | ------------------ | ---------------------------------------------------------------------------- |
| 极小 | < 20       | 精确算法           | @专家库/算法库/exact/\*                                                      |
| 小   | 20-100     | 精确算法、动态规划 | @专家库/算法库/exact/dynamic-programming.md                                  |
| 中   | 100-1000   | 启发式、混合算法   | @专家库/算法库/heuristic/\*                                                  |
| 大   | 1000-10000 | 元启发式、分解算法 | @专家库/算法库/specialized/\*                                                |
| 超大 | > 10000    | 贪心、大邻域搜索   | @专家库/算法库/greedy/\*, @专家库/算法库/hybrid/large-neighborhood-search.md |

### 按优化目标

| 目标类型     | 推荐算法                | 引用路径                                             |
| ------------ | ----------------------- | ---------------------------------------------------- |
| 单目标最小化 | 所有算法适用            | 根据规模选择                                         |
| 单目标最大化 | 所有算法适用            | 根据规模选择                                         |
| 多目标       | NSGA-II, MOEA/D, 加权和 | @专家库/算法库/heuristic/遗传算法.md#multi-objective |
| 鲁棒优化     | 场景优化、随机规划      | @专家库/算法库/specialized/robust-optimization.md    |

### 按约束类型

| 约束复杂度      | 推荐算法               | 引用路径                                            |
| --------------- | ---------------------- | --------------------------------------------------- |
| 线性约束        | 线性规划、单纯形法     | @专家库/算法库/exact/integer-programming.md         |
| 非线性约束      | 非线性规划、SQP        | @专家库/算法库/exact/nonlinear-programming.md       |
| 混合整数约束    | MILP、分支定界         | @专家库/算法库/exact/branch-and-bound.md            |
| 逻辑约束        | 约束规划、SAT          | @专家库/算法库/exact/constraint-programming.md      |
| 硬约束 + 软约束 | 惩罚函数、拉格朗日松弛 | @专家库/算法库/specialized/lagrangian-relaxation.md |

### 按时间限制

| 时间要求           | 推荐算法           | 引用路径                                |
| ------------------ | ------------------ | --------------------------------------- |
| 离线优化（小时级） | 精确算法、分解算法 | @专家库/算法库/exact/\*                 |
| 批处理（分钟级）   | 启发式、元启发式   | @专家库/算法库/heuristic/\*             |
| 实时调度（秒级）   | 贪心、快速启发式   | @专家库/算法库/greedy/\*                |
| 在线调度（毫秒级） | 规则驱动、预计算   | @专家库/算法库/greedy/priority-based.md |

## 算法模板结构

每个算法文件包含：

```markdown
# [算法名称]

**算法ID**: `algorithm-id`
**分类**: greedy | heuristic | exact | hybrid
**复杂度**: O(...)

## 适用场景

- 问题规模: ...
- 约束类型: ...
- 优化目标: ...
- 时间要求: ...

## 算法原理

[简要说明算法原理]

## 伪代码
```

procedure AlgorithmName(input):
initialization
while termination_criteria not met:
step1
step2
return solution

````

## Python实现模板

```python
def algorithm_name(problem_data):
    """
    算法名称实现

    参数:
        problem_data: 问题数据

    返回:
        solution: 调度方案
    """
    # 实现代码
    pass
````

## 参数配置

```yaml
parameters:
  param1: 默认值
  param2: 默认值
```

## 性能特征

- 时间复杂度: O(...)
- 空间复杂度: O(...)
- 平均解质量: ...
- 稳定性: ...

## 示例应用

[实际案例]

## 相关算法

- 改进版: @专家库/算法库/.../improved-version.md
- 变体: @专家库/算法库/.../variant.md

## 参考文献

[学术文献引用]

````

## 算法推荐决策树

```mermaid
graph TD
    A[开始] --> B{问题规模?}
    B -->|< 100变量| C{时间充足?}
    B -->|100-1000变量| D[启发式算法]
    B -->|> 1000变量| E{实时要求?}

    C -->|Yes| F[精确算法]
    C -->|No| G[快速启发式]

    D --> H{约束复杂?}
    H -->|简单| I[遗传算法/模拟退火]
    H -->|复杂| J[约束规划/混合算法]

    E -->|Yes| K[贪心算法]
    E -->|No| L[大邻域搜索]
````

## 使用指南

### 如何选择算法

1. **评估问题规模**
   - 决策变量数量
   - 约束数量
   - 时间范围

2. **分析约束类型**
   - 线性/非线性
   - 硬约束/软约束
   - 约束复杂度

3. **确定时间要求**
   - 离线/在线
   - 可接受求解时间
   - 实时性要求

4. **查找推荐算法**
   - 使用分类矩阵
   - 参考决策树
   - 查阅具体算法文档

5. **验证适用性**
   - 检查适用场景
   - 对比性能特征
   - 考虑实现难度

### 引用规范

在TenElementModel的算法元素中引用：

```yaml
5_algorithm:
  name: '遗传算法'
  type: 'heuristic'
  citation: '@专家库/算法库/heuristic/遗传算法.md'
  configuration:
    population_size: 100
    generations: 500
    crossover_rate: 0.8
    mutation_rate: 0.1
  justification: '问题规模中等(500变量)，需要平衡解质量和求解时间'
```

## 知识扩展指南

### 添加新算法

1. **确定分类目录**
   - greedy / heuristic / exact / hybrid / local-search / specialized

2. **创建算法文件**
   - 使用标准模板
   - 完整填写所有部分

3. **添加引用路径**
   - 更新分类矩阵
   - 更新决策树（如需要）

4. **提供实现代码**
   - Python模板代码
   - 参数说明
   - 使用示例

5. **性能验证**
   - 基准测试
   - 性能数据
   - 适用场景验证

### 知识来源

可接受的知识来源：

✅ **允许**:

- 已验证的算法实现
- 学术文献和教材
- 实际项目经验
- 基准测试结果

❌ **禁止**:

- 虚构的算法
- 未经验证的性能声明
- 无引用的推断

## Token优化

本知识库采用Sidecar模式：

- **Agent文件**: 仅包含加载指令（~200 tokens）
- **知识库**: 按需加载特定算法（~1-5K tokens/算法）
- **总节省**: 87% token减少（vs 全量内嵌）

## 质量保证

所有算法模板必须：

- [ ] 有明确的适用场景
- [ ] 包含伪代码或实现
- [ ] 提供参数配置指南
- [ ] 标注时间/空间复杂度
- [ ] 包含示例应用
- [ ] 有学术或实践依据

## 维护日志

| 版本 | 日期       | 变更         |
| ---- | ---------- | ------------ |
| V4.2 | 2025-10-20 | 初始框架创建 |

---

**维护**: 算法专家团队
**BMAD版本**: v6-alpha
**最后更新**: 2025-10-20

**使用此知识库**: 在 `agents/algorithm-expert.md` 的 `<critical-actions>` 中自动加载
