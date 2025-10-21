<!-- Powered by BMAD-CORE™ -->
<!-- Module ID: bmad/aps/templates/modeling-library/core/uncertainty-modeling.md -->
<!-- Aliases: @专家库/建模库/core/uncertainty-modeling.md, @专家库/建模模块/不确定性建模.md -->

---

module_name: 不确定性建模
category: 建模模块
version: v1.0.0
updated: 2025-10-10
keywords: ['不确定性', '随机规划', '鲁棒优化', '场景方法']

---

# 不确定性建模 - Uncertainty Modeling

## 🎯 作用

- 标准化描述需求波动、处理时间波动、交通/故障等不确定因素，指导算法选择、评估与风险控制。

## 🧩 类型与特征

| 类型       | 描述         | 典型要素       | 适用策略                             |
| ---------- | ------------ | -------------- | ------------------------------------ |
| none       | 确定性       | 固定参数       | 精确/启发/元启发式均可               |
| stochastic | 概率分布     | 分布/期望/方差 | 两阶段/多阶段随机规划、SAA、在线学习 |
| robust     | 最坏情况集合 | 不确定性集合   | 盒式/椭球/多面体鲁棒优化、RC         |
| scenario   | 有限场景集   | 场景权重/样本  | 场景生成/筛选/重采样、场景法         |

## 🛠️ 参数结构

```yaml
uncertainty_model:
  type: none|stochastic|robust|scenario
  distributions:                 # stochastic
    demand_kg: Normal(mu: 8, sigma: 2)
    travel_time: LogNormal(mu: 2.1, sigma: 0.3)
  uncertainty_set:               # robust
    demand_kg: {type: box, lower: -2, upper: 3}
    travel_time: {type: ellipsoid, radius: 0.2}
  scenarios:                     # scenario
    - {name: peak, weight: 0.4, demand_scale: 1.3}
    - {name: normal, weight: 0.4, demand_scale: 1.0}
    - {name: low, weight: 0.2, demand_scale: 0.8}
```

## 🔗 影响映射

- 目标：引入期望/风险度量（CVaR、方差）、鲁棒对偶项
- 约束：机会约束/鲁棒约束/场景约束合并
- 算法：
  - stochastic：SAA、RL/在线算法
  - robust：RC/调整型鲁棒优化
  - scenario：多场景评估与选择

## 🧪 评估口径（建议）

- 期望值/方差/分位数（95%/99%）
- 鲁棒性指标（最坏/平均性能比）
- 场景覆盖率与稳定性

## 🌰 示例

```yaml
uncertainty_model:
  type: robust
  uncertainty_set:
    demand_kg: { type: box, lower: -1.5, upper: 2.5 }
```
