# 建模专家知识库 - Modeling Library

**专家**: 王建模 (Modeling Expert)
**版本**: V1.0
**用途**: 问题建模、十要素结构化、时间模型设计、不确定性建模

## 概述

建模专家知识库提供标准化的优化问题建模方法论和框架，帮助将业务问题转化为可求解的数学模型。核心内容包括十要素建模流程、时间模型设计和不确定性建模策略。

## 知识库结构

```
modeling-library/
├── README.md                         # 本文档
└── core/                             # 核心建模方法
    ├── ten-element-modeling.md       # 十要素建模流程
    ├── time-model.md                 # 时间模型
    └── uncertainty-modeling.md       # 不确定性建模
```

## 知识目录

### 核心建模方法

#### **十要素建模流程** [@backend/knowledge_base/aps/modeling-library/core/ten-element-modeling.md]

描述: 标准化的十要素建模对话与产出结构，将业务问题转化为包含资源、任务、决策变量、参数、约束、目标、时间模型、不确定性模型、领域知识和求解策略的统一数据结构。作为后续算法推荐、约束建模、目标建模与代码生成的唯一真相源（SSOT）。

**适用场景**:

- 新问题的初始建模
- 跨领域调度问题的结构化分析
- 多专家协作的标准化输入输出

**核心输出**:

- 资源与任务定义
- 决策变量设计（binary/integer/real/vector/matrix）
- 约束分类（时间/容量/逻辑/空间/业务）
- 目标函数（单/多目标）
- 时间模型选择（continuous/discrete/event/rolling）
- 不确定性建模策略（none/stochastic/robust/scenario）
- 领域知识嵌入
- 求解策略建议（exact/heuristic/metaheuristic）

#### **时间模型** [@backend/knowledge_base/aps/modeling-library/core/time-model.md]

描述: 为调度问题提供统一的时间刻画方式，包括连续时间、离散时间、事件驱动和滚动期四种模型类型。指导变量定义、约束表达与算法选择，确保与评估/验证口径保持一致。

**时间模型类型**:

- **continuous（连续时间轴）**: 适用于高精度加工/排程，变量为实数，MILP/CP常见
- **discrete（等间隔离散刻度）**: 适用于配送/排班/批处理，启发式/元启发式友好
- **event（事件触发时刻）**: 适用于作业切换/状态变化，图搜索/动态规划
- **rolling（滚动规划窗口）**: 适用于动态/在线调度，需设定窗口宽度与重叠策略

**关键参数**:

- 时间分辨率（resolution）
- 规划期（horizon）
- 时间窗（windows）

#### **不确定性建模** [@backend/knowledge_base/aps/modeling-library/core/uncertainty-modeling.md]

描述: 标准化描述需求波动、处理时间波动、交通/故障等不确定因素，指导算法选择、评估与风险控制。

**不确定性类型**:

- **none（确定性）**: 固定参数，精确/启发/元启发式均可
- **stochastic（概率分布）**: 两阶段/多阶段随机规划、SAA、在线学习
- **robust（最坏情况集合）**: 盒式/椭球/多面体鲁棒优化、RC
- **scenario（有限场景集）**: 场景生成/筛选/重采样、场景法

**建模要素**:

- 不确定参数识别
- 分布/不确定性集合定义
- 场景生成与权重
- 风险度量与约束

## 建模决策矩阵

### 按问题特征选择时间模型

| 问题特征           | 时间精度要求  | 推荐时间模型 | 引用路径                                                                   |
| ------------------ | ------------- | ------------ | -------------------------------------------------------------------------- |
| 生产调度、机器排程 | 精确到秒/分钟 | continuous   | @backend/knowledge_base/aps/modeling-library/core/time-model.md#continuous |
| 车辆路径、人员排班 | 小时/班次级别 | discrete     | @backend/knowledge_base/aps/modeling-library/core/time-model.md#discrete   |
| 订单处理、工序切换 | 事件驱动      | event        | @backend/knowledge_base/aps/modeling-library/core/time-model.md#event      |
| 实时调度、在线优化 | 动态更新      | rolling      | @backend/knowledge_base/aps/modeling-library/core/time-model.md#rolling    |

### 按不确定性程度选择建模策略

| 不确定性程度       | 数据可用性        | 推荐策略   | 引用路径                                                                             |
| ------------------ | ----------------- | ---------- | ------------------------------------------------------------------------------------ |
| 无不确定性         | 参数固定          | none       | @backend/knowledge_base/aps/modeling-library/core/uncertainty-modeling.md#none       |
| 历史数据充足       | 可拟合分布        | stochastic | @backend/knowledge_base/aps/modeling-library/core/uncertainty-modeling.md#stochastic |
| 数据不足但知道范围 | 知道上下界        | robust     | @backend/knowledge_base/aps/modeling-library/core/uncertainty-modeling.md#robust     |
| 有典型情景         | 专家经验/历史场景 | scenario   | @backend/knowledge_base/aps/modeling-library/core/uncertainty-modeling.md#scenario   |

### 建模流程与专家协作

| 建模阶段   | 输入                        | 输出               | 协作专家          | 引用路径                                                                                        |
| ---------- | --------------------------- | ------------------ | ----------------- | ----------------------------------------------------------------------------------------------- |
| 问题理解   | 业务描述                    | 领域识别、实体定义 | Orchestrator      | @backend/knowledge_base/aps/modeling-library/core/ten-element-modeling.md#domain-identification |
| 结构化建模 | 领域信息                    | 十要素完整结构     | Domain Expert     | @backend/knowledge_base/aps/modeling-library/core/ten-element-modeling.md#ten-elements          |
| 约束建模   | 十要素中的constraints       | 约束数学表达       | Constraint Expert | @backend/knowledge_base/aps/constraint-library/                                                 |
| 目标建模   | 十要素中的objectives        | 目标函数表达       | Objective Expert  | @backend/knowledge_base/aps/objective-library/                                                  |
| 算法选择   | 十要素中的solution_strategy | 算法推荐           | Algorithm Expert  | @backend/knowledge_base/aps/algorithm-library/                                                  |

## 使用场景

### 1. 新问题建模

当面对一个全新的优化调度问题时，使用十要素建模流程进行系统化分析和结构化：

```
业务描述 → 十要素建模流程 → 统一数据结构 → 专家分工处理
```

### 2. 时间模型设计

根据问题的时间特征选择合适的时间模型：

- **连续时间**: 生产线排程、机器加工调度
- **离散时间**: 车辆路径规划、人员排班
- **事件驱动**: 订单处理、状态机调度
- **滚动期**: 实时调度、在线优化

### 3. 不确定性处理

根据问题的不确定性特征选择建模策略：

- **确定性**: 参数固定、历史稳定的场景
- **随机规划**: 需求波动、处理时间不确定
- **鲁棒优化**: 最坏情况保护、风险规避
- **场景方法**: 多种情景预案、敏感性分析

### 4. 多专家协作

十要素建模作为SSOT（Single Source of Truth），支持多个专家并行工作：

- Orchestrator: 领域识别、任务分配
- Domain Expert: 领域知识注入
- Constraint Expert: 基于十要素的约束建模
- Objective Expert: 基于十要素的目标建模
- Algorithm Expert: 基于十要素的算法推荐

## 建模最佳实践

### 1. 结构化优先

- 始终使用十要素框架进行问题分析
- 确保所有要素都被识别和定义
- 维护十要素结构的完整性和一致性

### 2. 时间模型选择

- 根据问题精度要求选择时间模型
- 考虑算法复杂度与时间模型的匹配
- 确保评估口径与建模口径一致

### 3. 不确定性量化

- 识别所有不确定参数
- 根据数据可用性选择建模策略
- 考虑风险承受能力和计算复杂度

### 4. 可追溯性

- 记录建模假设和决策依据
- 使用@引用标注知识来源
- 维护问题演化的版本历史

## 与其他专家库的关系

```
建模专家库（核心地位）
    ↓
    ├─→ 领域专家库：提供领域特定的建模模板
    ├─→ 约束专家库：消费十要素中的constraints定义
    ├─→ 目标专家库：消费十要素中的objectives定义
    ├─→ 算法专家库：基于solution_strategy和time_model推荐算法
    └─→ 代码实现库：基于完整十要素生成代码
```

## 参考资料

- [调度优化建模方法论](<https://en.wikipedia.org/wiki/Scheduling_(production_processes)>)
- [时间建模最佳实践](https://en.wikipedia.org/wiki/Time_complexity)
- [不确定性优化综述](https://en.wikipedia.org/wiki/Robust_optimization)
- [多目标优化建模](https://en.wikipedia.org/wiki/Multi-objective_optimization)

---

**创建日期**: 2025-11-06
**最后更新**: 2025-11-06
**维护者**: BMAD Development Team
**Story**: 1.5.0 - 专家库迁移和加载器实现
