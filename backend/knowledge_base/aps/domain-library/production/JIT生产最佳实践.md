<!-- Powered by BMAD-CORE™ -->
<!-- Module ID: bmad/aps/templates/domain-library/production/JIT生产最佳实践.md -->
<!-- Aliases: @backend/knowledge_base/aps/domain-library/production/JIT生产最佳实践.md, @backend/knowledge_base/aps/domain-library/生产调度/JIT生产最佳实践.md -->
<!-- Version: v1.0 -->
<!-- Owner: 领域应用专家智能体 (Domain Expert) -->

# JIT生产最佳实践 - Just-In-Time Best Practices

---

module_name: JIT生产最佳实践
module_id: jit-best-practices
category: 生产调度
expert: 领域应用专家
version: 1.0.0
difficulty: 中等
applicable_scenarios: ["精益生产", "准时制造"]
keywords: ["JIT", "零库存", "看板"]
created: 2025-10-05
updated: 2025-10-05

---

## 📖 JIT原则

**核心理念**: 在正确的时间、以正确的数量、生产正确的产品

**关键指标**:

- 库存周转率
- 交付准时率
- 生产节拍时间

## 🔧 代码实现

```python
class JITProductionAdapter:
    """JIT生产适配器"""

    def calculate_takt_time(self, available_time: float, demand: int) -> float:
        """
        计算节拍时间

        Takt Time = 可用生产时间 / 客户需求数量
        """
        takt_time = available_time / demand if demand > 0 else float('inf')
        return takt_time

    def validate_pull_system(self, inventory: int, threshold: int) -> bool:
        """验证拉动式生产"""
        # 库存低于阈值时才生产
        return inventory <= threshold
```

---

**模块版本**: 1.0.0
**状态**: ✅ 已完成
