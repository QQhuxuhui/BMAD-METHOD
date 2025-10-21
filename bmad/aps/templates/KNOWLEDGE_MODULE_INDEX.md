# 知识模块路径索引 - Knowledge Module Path Index

**版本**: v2.0
**更新日期**: 2025-10-21
**模块**: BMAD APS (Advanced Planning & Scheduling)

本文档提供所有已迁移知识模块的路径映射索引，帮助智能体正确引用知识模块。

---

## 📋 路径引用规范

### 标准引用格式

```yaml
@专家库/<category>/<path>/<filename>.md
```

### 支持的引用路径类型

1. **英文路径** (推荐): `@专家库/算法库/heuristic/遗传算法.md`
2. **中文路径** (别名): `@专家库/调度算法专家库/启发式算法/遗传算法.md`
3. **实际文件路径**: `bmad/aps/templates/algorithm-library/heuristic/遗传算法.md`

---

## 🗂️ 算法库 (Algorithm Library)

### 精确算法 (Exact Algorithms)

| 模块名称 | 英文路径                                | 中文路径别名                                              | 实际文件路径                                             |
| -------- | --------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------- |
| 分支定界 | `@专家库/algorithm库/exact/分支定界.md` | `@专家库/算法库 (Algorithm Library)/精确算法/分支定界.md` | `bmad/aps/templates/algorithm-library/exact/分支定界.md` |
| 动态规划 | `@专家库/algorithm库/exact/动态规划.md` | `@专家库/算法库 (Algorithm Library)/精确算法/动态规划.md` | `bmad/aps/templates/algorithm-library/exact/动态规划.md` |
| 整数规划 | `@专家库/algorithm库/exact/整数规划.md` | `@专家库/算法库 (Algorithm Library)/精确算法/整数规划.md` | `bmad/aps/templates/algorithm-library/exact/整数规划.md` |

### 启发式算法 (Heuristic Algorithms)

| 模块名称     | 英文路径                                        | 中文路径别名                                                    | 实际文件路径                                                     |
| ------------ | ----------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------- |
| 改进式启发式 | `@专家库/algorithm库/heuristic/改进式启发式.md` | `@专家库/算法库 (Algorithm Library)/启发式算法/改进式启发式.md` | `bmad/aps/templates/algorithm-library/heuristic/改进式启发式.md` |
| 构造式启发式 | `@专家库/algorithm库/heuristic/构造式启发式.md` | `@专家库/算法库 (Algorithm Library)/启发式算法/构造式启发式.md` | `bmad/aps/templates/algorithm-library/heuristic/构造式启发式.md` |
| 贪心算法     | `@专家库/algorithm库/heuristic/贪心算法.md`     | `@专家库/算法库 (Algorithm Library)/启发式算法/贪心算法.md`     | `bmad/aps/templates/algorithm-library/heuristic/贪心算法.md`     |
| 遗传算法     | `@专家库/algorithm库/heuristic/遗传算法.md`     | `@专家库/算法库 (Algorithm Library)/启发式算法/遗传算法.md`     | `bmad/aps/templates/algorithm-library/heuristic/遗传算法.md`     |

### 元启发式算法 (Meta-Heuristic Algorithms)

| 模块名称   | 英文路径                                           | 中文路径别名                                                    | 实际文件路径                                                        |
| ---------- | -------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| 差分进化   | `@专家库/algorithm库/meta-heuristic/差分进化.md`   | `@专家库/算法库 (Algorithm Library)/元启发式算法/差分进化.md`   | `bmad/aps/templates/algorithm-library/meta-heuristic/差分进化.md`   |
| 模拟退火   | `@专家库/algorithm库/meta-heuristic/模拟退火.md`   | `@专家库/算法库 (Algorithm Library)/元启发式算法/模拟退火.md`   | `bmad/aps/templates/algorithm-library/meta-heuristic/模拟退火.md`   |
| 禁忌搜索   | `@专家库/algorithm库/meta-heuristic/禁忌搜索.md`   | `@专家库/算法库 (Algorithm Library)/元启发式算法/禁忌搜索.md`   | `bmad/aps/templates/algorithm-library/meta-heuristic/禁忌搜索.md`   |
| 粒子群算法 | `@专家库/algorithm库/meta-heuristic/粒子群算法.md` | `@专家库/算法库 (Algorithm Library)/元启发式算法/粒子群算法.md` | `bmad/aps/templates/algorithm-library/meta-heuristic/粒子群算法.md` |
| 蚁群算法   | `@专家库/algorithm库/meta-heuristic/蚁群算法.md`   | `@专家库/算法库 (Algorithm Library)/元启发式算法/蚁群算法.md`   | `bmad/aps/templates/algorithm-library/meta-heuristic/蚁群算法.md`   |
| 遗传算法   | `@专家库/algorithm库/meta-heuristic/遗传算法.md`   | `@专家库/算法库 (Algorithm Library)/元启发式算法/遗传算法.md`   | `bmad/aps/templates/algorithm-library/meta-heuristic/遗传算法.md`   |

**专家**: 张效率 (Algorithm Expert)
**主入口**: `bmad/aps/templates/algorithm-library/README.md`
**文件数量**: 13 个

---

## 🗂️ 约束库 (Constraint Library)

### 容量约束 (Capacity Constraints)

| 模块名称     | 英文路径                                        | 中文路径别名                                                   | 实际文件路径                                                     |
| ------------ | ----------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------- |
| 仓库容量约束 | `@专家库/constraint库/capacity/仓库容量约束.md` | `@专家库/约束库 (Constraint Library)/容量约束/仓库容量约束.md` | `bmad/aps/templates/constraint-library/capacity/仓库容量约束.md` |
| 资源容量约束 | `@专家库/constraint库/capacity/资源容量约束.md` | `@专家库/约束库 (Constraint Library)/容量约束/资源容量约束.md` | `bmad/aps/templates/constraint-library/capacity/资源容量约束.md` |
| 车辆容量约束 | `@专家库/constraint库/capacity/车辆容量约束.md` | `@专家库/约束库 (Constraint Library)/容量约束/车辆容量约束.md` | `bmad/aps/templates/constraint-library/capacity/车辆容量约束.md` |

### 时间约束 (Temporal Constraints)

| 模块名称               | 英文路径                                                  | 中文路径别名                                                             | 实际文件路径                                                               |
| ---------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| time-window-constraint | `@专家库/constraint库/temporal/time-window-constraint.md` | `@专家库/约束库 (Constraint Library)/时间约束/time-window-constraint.md` | `bmad/aps/templates/constraint-library/temporal/time-window-constraint.md` |
| 工作时间约束           | `@专家库/constraint库/temporal/工作时间约束.md`           | `@专家库/约束库 (Constraint Library)/时间约束/工作时间约束.md`           | `bmad/aps/templates/constraint-library/temporal/工作时间约束.md`           |
| 截止期约束             | `@专家库/constraint库/temporal/截止期约束.md`             | `@专家库/约束库 (Constraint Library)/时间约束/截止期约束.md`             | `bmad/aps/templates/constraint-library/temporal/截止期约束.md`             |
| 时序依赖约束           | `@专家库/constraint库/temporal/时序依赖约束.md`           | `@专家库/约束库 (Constraint Library)/时间约束/时序依赖约束.md`           | `bmad/aps/templates/constraint-library/temporal/时序依赖约束.md`           |
| 时间窗约束             | `@专家库/constraint库/temporal/时间窗约束.md`             | `@专家库/约束库 (Constraint Library)/时间约束/时间窗约束.md`             | `bmad/aps/templates/constraint-library/temporal/时间窗约束.md`             |

### 空间约束 (Spatial Constraints)

| 模块名称     | 英文路径                                       | 中文路径别名                                                   | 实际文件路径                                                    |
| ------------ | ---------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| 地理位置约束 | `@专家库/constraint库/spatial/地理位置约束.md` | `@专家库/约束库 (Constraint Library)/空间约束/地理位置约束.md` | `bmad/aps/templates/constraint-library/spatial/地理位置约束.md` |
| 服务范围约束 | `@专家库/constraint库/spatial/服务范围约束.md` | `@专家库/约束库 (Constraint Library)/空间约束/服务范围约束.md` | `bmad/aps/templates/constraint-library/spatial/服务范围约束.md` |
| 距离约束     | `@专家库/constraint库/spatial/距离约束.md`     | `@专家库/约束库 (Constraint Library)/空间约束/距离约束.md`     | `bmad/aps/templates/constraint-library/spatial/距离约束.md`     |

### 逻辑约束 (Logical Constraints)

| 模块名称   | 英文路径                                     | 中文路径别名                                                 | 实际文件路径                                                  |
| ---------- | -------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------- |
| 互斥约束   | `@专家库/constraint库/logical/互斥约束.md`   | `@专家库/约束库 (Constraint Library)/逻辑约束/互斥约束.md`   | `bmad/aps/templates/constraint-library/logical/互斥约束.md`   |
| 优先级约束 | `@专家库/constraint库/logical/优先级约束.md` | `@专家库/约束库 (Constraint Library)/逻辑约束/优先级约束.md` | `bmad/aps/templates/constraint-library/logical/优先级约束.md` |
| 依赖约束   | `@专家库/constraint库/logical/依赖约束.md`   | `@专家库/约束库 (Constraint Library)/逻辑约束/依赖约束.md`   | `bmad/aps/templates/constraint-library/logical/依赖约束.md`   |

### 业务规则 (Business Rules)

| 模块名称     | 英文路径                                              | 中文路径别名                                                   | 实际文件路径                                                           |
| ------------ | ----------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 合规性约束   | `@专家库/constraint库/business-rules/合规性约束.md`   | `@专家库/约束库 (Constraint Library)/业务规则/合规性约束.md`   | `bmad/aps/templates/constraint-library/business-rules/合规性约束.md`   |
| 成本约束     | `@专家库/constraint库/business-rules/成本约束.md`     | `@专家库/约束库 (Constraint Library)/业务规则/成本约束.md`     | `bmad/aps/templates/constraint-library/business-rules/成本约束.md`     |
| 服务质量约束 | `@专家库/constraint库/business-rules/服务质量约束.md` | `@专家库/约束库 (Constraint Library)/业务规则/服务质量约束.md` | `bmad/aps/templates/constraint-library/business-rules/服务质量约束.md` |

**专家**: 李严谨 (Constraint Expert)
**主入口**: `bmad/aps/templates/constraint-library/README.md`
**文件数量**: 17 个

---

## 🗂️ 目标库 (Objective Library)

### 成本目标 (Cost Objectives)

| 模块名称          | 英文路径                                        | 中文路径别名                                                       | 实际文件路径                                                     |
| ----------------- | ----------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| cost-minimization | `@专家库/objective库/cost/cost-minimization.md` | `@专家库/目标库 (Objective Library)/成本目标/cost-minimization.md` | `bmad/aps/templates/objective-library/cost/cost-minimization.md` |
| 总成本目标        | `@专家库/objective库/cost/总成本目标.md`        | `@专家库/目标库 (Objective Library)/成本目标/总成本目标.md`        | `bmad/aps/templates/objective-library/cost/总成本目标.md`        |
| 资源成本目标      | `@专家库/objective库/cost/资源成本目标.md`      | `@专家库/目标库 (Objective Library)/成本目标/资源成本目标.md`      | `bmad/aps/templates/objective-library/cost/资源成本目标.md`      |
| 运营成本目标      | `@专家库/objective库/cost/运营成本目标.md`      | `@专家库/目标库 (Objective Library)/成本目标/运营成本目标.md`      | `bmad/aps/templates/objective-library/cost/运营成本目标.md`      |

### 时间目标 (Time Objectives)

| 模块名称         | 英文路径                                       | 中文路径别名                                                      | 实际文件路径                                                    |
| ---------------- | ---------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| 加权延迟目标     | `@专家库/objective库/time/加权延迟目标.md`     | `@专家库/目标库 (Objective Library)/时间目标/加权延迟目标.md`     | `bmad/aps/templates/objective-library/time/加权延迟目标.md`     |
| 总延迟时间目标   | `@专家库/objective库/time/总延迟时间目标.md`   | `@专家库/目标库 (Objective Library)/时间目标/总延迟时间目标.md`   | `bmad/aps/templates/objective-library/time/总延迟时间目标.md`   |
| 最大完成时间目标 | `@专家库/objective库/time/最大完成时间目标.md` | `@专家库/目标库 (Objective Library)/时间目标/最大完成时间目标.md` | `bmad/aps/templates/objective-library/time/最大完成时间目标.md` |

### 效率目标 (Efficiency Objectives)

| 模块名称       | 英文路径                                           | 中文路径别名                                                    | 实际文件路径                                                        |
| -------------- | -------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| 吞吐量目标     | `@专家库/objective库/efficiency/吞吐量目标.md`     | `@专家库/目标库 (Objective Library)/效率目标/吞吐量目标.md`     | `bmad/aps/templates/objective-library/efficiency/吞吐量目标.md`     |
| 负载均衡目标   | `@专家库/objective库/efficiency/负载均衡目标.md`   | `@专家库/目标库 (Objective Library)/效率目标/负载均衡目标.md`   | `bmad/aps/templates/objective-library/efficiency/负载均衡目标.md`   |
| 资源利用率目标 | `@专家库/objective库/efficiency/资源利用率目标.md` | `@专家库/目标库 (Objective Library)/效率目标/资源利用率目标.md` | `bmad/aps/templates/objective-library/efficiency/资源利用率目标.md` |

### 质量目标 (Quality Objectives)

| 模块名称       | 英文路径                                        | 中文路径别名                                                    | 实际文件路径                                                     |
| -------------- | ----------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------- |
| 准确率目标     | `@专家库/objective库/quality/准确率目标.md`     | `@专家库/目标库 (Objective Library)/质量目标/准确率目标.md`     | `bmad/aps/templates/objective-library/quality/准确率目标.md`     |
| 客户满意度目标 | `@专家库/objective库/quality/客户满意度目标.md` | `@专家库/目标库 (Objective Library)/质量目标/客户满意度目标.md` | `bmad/aps/templates/objective-library/quality/客户满意度目标.md` |
| 服务质量目标   | `@专家库/objective库/quality/服务质量目标.md`   | `@专家库/目标库 (Objective Library)/质量目标/服务质量目标.md`   | `bmad/aps/templates/objective-library/quality/服务质量目标.md`   |

### 可持续性目标 (Sustainability Objectives)

| 模块名称   | 英文路径                                           | 中文路径别名                                                    | 实际文件路径                                                        |
| ---------- | -------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| 碳排放目标 | `@专家库/objective库/sustainability/碳排放目标.md` | `@专家库/目标库 (Objective Library)/可持续性目标/碳排放目标.md` | `bmad/aps/templates/objective-library/sustainability/碳排放目标.md` |
| 能耗目标   | `@专家库/objective库/sustainability/能耗目标.md`   | `@专家库/目标库 (Objective Library)/可持续性目标/能耗目标.md`   | `bmad/aps/templates/objective-library/sustainability/能耗目标.md`   |

### 多目标优化 (Multi-Objective Optimization)

| 模块名称     | 英文路径                                              | 中文路径别名                                                    | 实际文件路径                                                           |
| ------------ | ----------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 加权优化方法 | `@专家库/objective库/multi-objective/加权优化方法.md` | `@专家库/目标库 (Objective Library)/多目标优化/加权优化方法.md` | `bmad/aps/templates/objective-library/multi-objective/加权优化方法.md` |
| 帕累托前沿   | `@专家库/objective库/multi-objective/帕累托前沿.md`   | `@专家库/目标库 (Objective Library)/多目标优化/帕累托前沿.md`   | `bmad/aps/templates/objective-library/multi-objective/帕累托前沿.md`   |

**专家**: 王目标 (Objective Expert)
**主入口**: `bmad/aps/templates/objective-library/README.md`
**文件数量**: 17 个

---

## 🗂️ 领域库 (Domain Library)

### 车辆调度 (Vehicle Scheduling)

| 模块名称               | 英文路径                                             | 中文路径别名                                                         | 实际文件路径                                                          |
| ---------------------- | ---------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------- |
| VRP领域适配器          | `@专家库/domain库/vehicle/VRP领域适配器.md`          | `@专家库/领域库 (Domain Library)/车辆调度/VRP领域适配器.md`          | `bmad/aps/templates/domain-library/vehicle/VRP领域适配器.md`          |
| vehicle-routing-domain | `@专家库/domain库/vehicle/vehicle-routing-domain.md` | `@专家库/领域库 (Domain Library)/车辆调度/vehicle-routing-domain.md` | `bmad/aps/templates/domain-library/vehicle/vehicle-routing-domain.md` |
| 冷链物流最佳实践       | `@专家库/domain库/vehicle/冷链物流最佳实践.md`       | `@专家库/领域库 (Domain Library)/车辆调度/冷链物流最佳实践.md`       | `bmad/aps/templates/domain-library/vehicle/冷链物流最佳实践.md`       |

### 生产调度 (Production Scheduling)

| 模块名称        | 英文路径                                         | 中文路径别名                                                  | 实际文件路径                                                      |
| --------------- | ------------------------------------------------ | ------------------------------------------------------------- | ----------------------------------------------------------------- |
| JIT生产最佳实践 | `@专家库/domain库/production/JIT生产最佳实践.md` | `@专家库/领域库 (Domain Library)/生产调度/JIT生产最佳实践.md` | `bmad/aps/templates/domain-library/production/JIT生产最佳实践.md` |
| 生产调度适配器  | `@专家库/domain库/production/生产调度适配器.md`  | `@专家库/领域库 (Domain Library)/生产调度/生产调度适配器.md`  | `bmad/aps/templates/domain-library/production/生产调度适配器.md`  |

### 服务调度 (Service Scheduling)

| 模块名称        | 英文路径                                      | 中文路径别名                                                  | 实际文件路径                                                   |
| --------------- | --------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------- |
| SLA服务质量管理 | `@专家库/domain库/service/SLA服务质量管理.md` | `@专家库/领域库 (Domain Library)/服务调度/SLA服务质量管理.md` | `bmad/aps/templates/domain-library/service/SLA服务质量管理.md` |
| 人员排班适配器  | `@专家库/domain库/service/人员排班适配器.md`  | `@专家库/领域库 (Domain Library)/服务调度/人员排班适配器.md`  | `bmad/aps/templates/domain-library/service/人员排班适配器.md`  |

### 项目调度 (Project Scheduling)

| 模块名称         | 英文路径                                       | 中文路径别名                                                   | 实际文件路径                                                    |
| ---------------- | ---------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| 敏捷开发最佳实践 | `@专家库/domain库/project/敏捷开发最佳实践.md` | `@专家库/领域库 (Domain Library)/项目调度/敏捷开发最佳实践.md` | `bmad/aps/templates/domain-library/project/敏捷开发最佳实践.md` |
| 项目调度适配器   | `@专家库/domain库/project/项目调度适配器.md`   | `@专家库/领域库 (Domain Library)/项目调度/项目调度适配器.md`   | `bmad/aps/templates/domain-library/project/项目调度适配器.md`   |

### 供应链调度 (Supply Chain Scheduling)

| 模块名称         | 英文路径                                            | 中文路径别名                                                     | 实际文件路径                                                         |
| ---------------- | --------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| VMI协同库存管理  | `@专家库/domain库/supply-chain/VMI协同库存管理.md`  | `@专家库/领域库 (Domain Library)/供应链调度/VMI协同库存管理.md`  | `bmad/aps/templates/domain-library/supply-chain/VMI协同库存管理.md`  |
| 供应链调度适配器 | `@专家库/domain库/supply-chain/供应链调度适配器.md` | `@专家库/领域库 (Domain Library)/供应链调度/供应链调度适配器.md` | `bmad/aps/templates/domain-library/supply-chain/供应链调度适配器.md` |

**专家**: 赵领域 (Domain Expert)
**主入口**: `bmad/aps/templates/domain-library/README.md`
**文件数量**: 11 个

---

## 🗂️ 质量评估库 (Quality Library)

### 基准评测 (Benchmark)

| 模块名称   | 英文路径                                    | 中文路径别名                                                  | 实际文件路径                                                 |
| ---------- | ------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------ |
| 基准运行器 | `@专家库/quality库/benchmark/基准运行器.md` | `@专家库/质量评估库 (Quality Library)/基准评测/基准运行器.md` | `bmad/aps/templates/quality-library/benchmark/基准运行器.md` |

### 报告聚合 (Report Aggregation)

| 模块名称   | 英文路径                                 | 中文路径别名                                                  | 实际文件路径                                              |
| ---------- | ---------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------- |
| 报告聚合器 | `@专家库/quality库/report/报告聚合器.md` | `@专家库/质量评估库 (Quality Library)/报告聚合/报告聚合器.md` | `bmad/aps/templates/quality-library/report/报告聚合器.md` |

### 约束一致性 (Consistency Checking)

| 模块名称         | 英文路径                                            | 中文路径别名                                                          | 实际文件路径                                                         |
| ---------------- | --------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 约束一致性检查器 | `@专家库/quality库/consistency/约束一致性检查器.md` | `@专家库/质量评估库 (Quality Library)/约束一致性/约束一致性检查器.md` | `bmad/aps/templates/quality-library/consistency/约束一致性检查器.md` |

### 语法检查 (Syntax Checking)

| 模块名称         | 英文路径                                       | 中文路径别名                                                        | 实际文件路径                                                    |
| ---------------- | ---------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------- |
| Python语法检查器 | `@专家库/quality库/syntax/Python语法检查器.md` | `@专家库/质量评估库 (Quality Library)/语法检查/Python语法检查器.md` | `bmad/aps/templates/quality-library/syntax/Python语法检查器.md` |

### 逻辑验证 (Logic Validation)

| 模块名称   | 英文路径                                | 中文路径别名                                                  | 实际文件路径                                             |
| ---------- | --------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------- |
| 逻辑验证器 | `@专家库/quality库/logic/逻辑验证器.md` | `@专家库/质量评估库 (Quality Library)/逻辑验证/逻辑验证器.md` | `bmad/aps/templates/quality-library/logic/逻辑验证器.md` |

**专家**: 质量与评测智能体 (Quality Expert)
**主入口**: `bmad/aps/templates/quality-library/README.md`
**文件数量**: 5 个

---

## 🗂️ 系统编排库 (Orchestrator Library)

### 决策策略 (Decision Strategies)

| 模块名称       | 英文路径                                            | 中文路径别名                                                           | 实际文件路径                                                         |
| -------------- | --------------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 专家选择策略   | `@专家库/orchestrator库/decision/专家选择策略.md`   | `@专家库/系统编排库 (Orchestrator Library)/决策策略/专家选择策略.md`   | `bmad/aps/templates/orchestrator-library/decision/专家选择策略.md`   |
| 冲突解决策略   | `@专家库/orchestrator库/decision/冲突解决策略.md`   | `@专家库/系统编排库 (Orchestrator Library)/决策策略/冲突解决策略.md`   | `bmad/aps/templates/orchestrator-library/decision/冲突解决策略.md`   |
| 复杂度评估策略 | `@专家库/orchestrator库/decision/复杂度评估策略.md` | `@专家库/系统编排库 (Orchestrator Library)/决策策略/复杂度评估策略.md` | `bmad/aps/templates/orchestrator-library/decision/复杂度评估策略.md` |
| 质量评估策略   | `@专家库/orchestrator库/decision/质量评估策略.md`   | `@专家库/系统编排库 (Orchestrator Library)/决策策略/质量评估策略.md`   | `bmad/aps/templates/orchestrator-library/decision/质量评估策略.md`   |

### 编排模式 (Collaboration Patterns)

| 模块名称     | 英文路径                                               | 中文路径别名                                                         | 实际文件路径                                                            |
| ------------ | ------------------------------------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 串行协作模式 | `@专家库/orchestrator库/collaboration/串行协作模式.md` | `@专家库/系统编排库 (Orchestrator Library)/编排模式/串行协作模式.md` | `bmad/aps/templates/orchestrator-library/collaboration/串行协作模式.md` |
| 并行协作模式 | `@专家库/orchestrator库/collaboration/并行协作模式.md` | `@专家库/系统编排库 (Orchestrator Library)/编排模式/并行协作模式.md` | `bmad/aps/templates/orchestrator-library/collaboration/并行协作模式.md` |
| 混合协作模式 | `@专家库/orchestrator库/collaboration/混合协作模式.md` | `@专家库/系统编排库 (Orchestrator Library)/编排模式/混合协作模式.md` | `bmad/aps/templates/orchestrator-library/collaboration/混合协作模式.md` |

### 集成优化 (Integration Optimization)

| 模块名称       | 英文路径                                               | 中文路径别名                                                           | 实际文件路径                                                            |
| -------------- | ------------------------------------------------------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 一致性保证策略 | `@专家库/orchestrator库/integration/一致性保证策略.md` | `@专家库/系统编排库 (Orchestrator Library)/集成优化/一致性保证策略.md` | `bmad/aps/templates/orchestrator-library/integration/一致性保证策略.md` |
| 方案融合策略   | `@专家库/orchestrator库/integration/方案融合策略.md`   | `@专家库/系统编排库 (Orchestrator Library)/集成优化/方案融合策略.md`   | `bmad/aps/templates/orchestrator-library/integration/方案融合策略.md`   |
| 迭代优化策略   | `@专家库/orchestrator库/integration/迭代优化策略.md`   | `@专家库/系统编排库 (Orchestrator Library)/集成优化/迭代优化策略.md`   | `bmad/aps/templates/orchestrator-library/integration/迭代优化策略.md`   |

### 风险控制 (Risk Control)

| 模块名称     | 英文路径                                      | 中文路径别名                                                         | 实际文件路径                                                   |
| ------------ | --------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------- |
| 风险控制策略 | `@专家库/orchestrator库/risk/风险控制策略.md` | `@专家库/系统编排库 (Orchestrator Library)/风险控制/风险控制策略.md` | `bmad/aps/templates/orchestrator-library/risk/风险控制策略.md` |
| 风险识别矩阵 | `@专家库/orchestrator库/risk/风险识别矩阵.md` | `@专家库/系统编排库 (Orchestrator Library)/风险控制/风险识别矩阵.md` | `bmad/aps/templates/orchestrator-library/risk/风险识别矩阵.md` |

**专家**: 系统编排协调智能体 (CoreOrchestrator)
**主入口**: `bmad/aps/templates/orchestrator-library/README.md`
**文件数量**: 12 个

---

## 🗂️ 建模库 (Modeling Library)

### 核心建模模块 (Core Modeling Modules)

| 模块名称             | 英文路径                                          | 中文路径别名                                                             | 实际文件路径                                                       |
| -------------------- | ------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| ten-element-modeling | `@专家库/modeling库/core/ten-element-modeling.md` | `@专家库/建模库 (Modeling Library)/核心建模模块/ten-element-modeling.md` | `bmad/aps/templates/modeling-library/core/ten-element-modeling.md` |
| time-model           | `@专家库/modeling库/core/time-model.md`           | `@专家库/建模库 (Modeling Library)/核心建模模块/time-model.md`           | `bmad/aps/templates/modeling-library/core/time-model.md`           |
| uncertainty-modeling | `@专家库/modeling库/core/uncertainty-modeling.md` | `@专家库/建模库 (Modeling Library)/核心建模模块/uncertainty-modeling.md` | `bmad/aps/templates/modeling-library/core/uncertainty-modeling.md` |

**专家**: 系统编排协调智能体 (CoreOrchestrator)
**主入口**: `bmad/aps/templates/modeling-library/README.md (待创建)`
**文件数量**: 3 个

---

## 🗂️ 协作机制 (Collaboration Mechanisms)

| 模块名称                       | 英文路径                                                  | 中文路径别名                                                                    | 实际文件路径                                                         |
| ------------------------------ | --------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| agent-as-doc-mode              | `@专家库/collaboration/agent-as-doc-mode.md`              | `@专家库/协作机制 (Collaboration Mechanisms)/agent-as-doc-mode.md`              | `bmad/aps/templates/collaboration/agent-as-doc-mode.md`              |
| agent-collaboration-protocol   | `@专家库/collaboration/agent-collaboration-protocol.md`   | `@专家库/协作机制 (Collaboration Mechanisms)/agent-collaboration-protocol.md`   | `bmad/aps/templates/collaboration/agent-collaboration-protocol.md`   |
| knowledge-dependency-framework | `@专家库/collaboration/knowledge-dependency-framework.md` | `@专家库/协作机制 (Collaboration Mechanisms)/knowledge-dependency-framework.md` | `bmad/aps/templates/collaboration/knowledge-dependency-framework.md` |

**专家**: 系统编排协调智能体 (CoreOrchestrator)
**主入口**: `bmad/aps/templates/collaboration/README.md (待创建)`
**文件数量**: 3 个

---

## 🗂️ 实例化案例 (Example Cases)

| 模块名称                 | 英文路径                                       | 中文路径别名                                                     | 实际文件路径                                              |
| ------------------------ | ---------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------- |
| algorithm-extension-case | `@专家库/examples/algorithm-extension-case.md` | `@专家库/实例化案例 (Example Cases)/algorithm-extension-case.md` | `bmad/aps/templates/examples/algorithm-extension-case.md` |
| fresh-delivery-case      | `@专家库/examples/fresh-delivery-case.md`      | `@专家库/实例化案例 (Example Cases)/fresh-delivery-case.md`      | `bmad/aps/templates/examples/fresh-delivery-case.md`      |

**专家**: 所有专家智能体
**主入口**: `bmad/aps/templates/examples/README.md (待创建)`
**文件数量**: 2 个

---

## 🎯 智能体引用规范

### 在智能体Prompt中引用

```xml
<i critical="MANDATORY">
  每个推荐必须附@引用，如: @专家库/算法库/heuristic/遗传算法.md
</i>
```

### 在TenElementModel中引用

```yaml
5_algorithm:
  name: '遗传算法'
  type: 'heuristic'
  citation: '@专家库/算法库/heuristic/遗传算法.md'
  configuration:
    population_size: 100
    crossover_rate: 0.8
    mutation_rate: 0.05
```

---

## 📊 统计信息

- **interaction-templates**: 3 个文件
- **协作机制 (Collaboration Mechanisms)**: 3 个文件
- **算法库 (Algorithm Library)**: 13 个文件
- **质量评估库 (Quality Library)**: 5 个文件
- **实例化案例 (Example Cases)**: 2 个文件
- **系统编排库 (Orchestrator Library)**: 12 个文件
- **目标库 (Objective Library)**: 17 个文件
- **建模库 (Modeling Library)**: 3 个文件
- **约束库 (Constraint Library)**: 17 个文件
- **领域库 (Domain Library)**: 11 个文件

**总计**: 86 个知识模块文件

---

## 📝 更新历史

| 日期       | 版本 | 更新内容                         |
| ---------- | ---- | -------------------------------- |
| 2025-10-21 | v2.0 | 完整迁移专家库，包含87个知识模块 |
| 2025-10-21 | v1.0 | 初始版本，包含12个已迁移知识模块 |

---

## 🔗 相关文档

- [APS模块README](../README.md)
- [算法库README](./algorithm-library/README.md)
- [约束库README](./constraint-library/README.md)
- [APS配置文件](../config.yaml)
- [迁移指南](../MIGRATION_GUIDE.md)
