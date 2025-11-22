# VMI协同库存管理 - Vendor Managed Inventory

---

module_name: VMI协同库存管理
module_id: vmi-management
category: 供应链调度
expert: 领域应用专家
version: 1.0.0
difficulty: 中等
applicable_scenarios: ["协同库存", "供应商管理", "自动补货"]
keywords: ["VMI", "协同", "自动补货"]
created: 2025-10-05
updated: 2025-10-05

---

## 📖 VMI概述

**VMI (Vendor Managed Inventory)** 供应商管理库存，由供应商负责客户的库存管理和补货。

**优势**:

- 降低库存成本
- 提高库存周转
- 减少缺货风险

## 🔧 代码实现

```python
class VMIAdapter:
    """VMI协同库存管理适配器"""

    def __init__(self, min_level: float, max_level: float):
        self.min_level = min_level
        self.max_level = max_level

    def check_replenishment_needed(self, current_inventory: float) -> bool:
        """检查是否需要补货"""
        return current_inventory <= self.min_level

    def calculate_replenishment_quantity(self, current_inventory: float) -> float:
        """计算补货数量"""
        if self.check_replenishment_needed(current_inventory):
            return self.max_level - current_inventory
        return 0
```

---

**模块版本**: 1.0.0
**状态**: ✅ 已完成
