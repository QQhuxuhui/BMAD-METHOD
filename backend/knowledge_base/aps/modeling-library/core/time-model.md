<!-- Powered by BMAD-CORE™ -->
<!-- Module ID: bmad/aps/templates/modeling-library/core/time-model.md -->
<!-- Aliases: @backend/knowledge_base/aps/modeling-library/core/time-model.md, @backend/knowledge_base/aps/modeling-library/时间模型.md -->

---

module_name: 时间模型
category: 建模模块
version: v1.0.0
updated: 2025-10-10
keywords: ['时间模型', '连续时间', '离散时间', '事件驱动', '滚动期']

---

# 时间模型 - Time Model

## 🎯 作用

- 为调度问题提供统一的时间刻画方式，指导变量定义、约束表达与算法选择，并与评估/验证口径保持一致。

## 🧩 类型与适用性

| 类型       | 描述           | 典型适用          | 影响点                                             |
| ---------- | -------------- | ----------------- | -------------------------------------------------- |
| continuous | 连续时间轴     | 高精度加工/排程   | 变量为实数，约束为不等式，MILP/CP常见              |
| discrete   | 等间隔离散刻度 | 配送/排班/批处理  | 变量离散化，时间窗/容量易实现，启发式/元启发式友好 |
| event      | 事件触发时刻   | 作业切换/状态变化 | 事件序列与先后约束，图搜索/动态规划                |
| rolling    | 滚动规划窗口   | 动态/在线调度     | 需设定窗口宽度与重叠，重优化策略                   |

## 🛠️ 参数结构

```yaml
time_model:
  type: continuous|discrete|event|rolling
  resolution: 5m|1m|null # 离散/滚动必填
  horizon: 8h|12h|null # 规划周期
  windows: # 可选：任务/资源的时间窗
    - { entity: 'task#C101', start: '09:00', end: '12:00', hard: true }
  rolling:
    overlap: 10m # 窗口重叠（滚动专用）
    reopt_policy: periodic|event # 触发方式
```

## 🔁 转换与校验

### 连续→离散刻度建议

```python
def continuous_to_discrete(ts_hours: float, step_min: int) -> int:
    return int(round(ts_hours * 60 / step_min))
```

校验要点：

- resolution 应能覆盖最小服务/运输时间粒度
- horizon/rolling.overlap 与 SLA/时间窗兼容
- 时间窗传播与可达性检查需统一粒度

## 🔗 影响映射

- 变量：到达/开始/完成时间的类型与范围
- 约束：时间窗、工序先后、工作时段等表达形式
- 算法：
  - 连续：MILP/CP、分支定界、DP
  - 离散：贪心/局部搜索/GA/SA/TS
  - 事件：图搜索、拓扑序、DP
  - 滚动：任一上法+重优化策略

## 🧪 示例

```yaml
time_model:
  type: discrete
  resolution: 5m
  horizon: 10h
  windows:
    - { entity: 'order#A', start: '09:00', end: '11:00', hard: true }
```
