<!-- Powered by BMAD-CORE™ -->
<!-- Module ID: bmad/aps/templates/domain-library/vehicle/VRP领域适配器.md -->
<!-- Aliases: @专家库/domain库/vehicle/VRP领域适配器.md, @专家库/领域应用专家库/车辆调度/VRP领域适配器.md -->
<!-- Version: v1.0 -->
<!-- Owner: 领域应用专家智能体 (Domain Expert) -->

# VRP领域适配器 - Vehicle Routing Problem Domain Adapter

---

module_name: VRP领域适配器
module_id: vrp-domain-adapter
category: 车辆调度
expert: 领域应用专家
version: 1.0.0
difficulty: 中等
applicable_scenarios: ["物流配送", "出行服务", "货运调度"]
keywords: ["VRP", "车辆路径", "配送优化"]
created: 2025-10-05
updated: 2025-10-05

---

## 📖 领域概述

### 定义

**VRP (Vehicle Routing Problem)** 是车辆调度领域的经典问题，目标是优化多辆车服务多个客户的路径。

**问题变体**:

```
CVRP  - 容量约束VRP
VRPTW - 带时间窗VRP
MDVRP - 多车场VRP
SDVRP - 分割配送VRP
VRPPD - 取送货VRP
```

## 🔧 代码实现

```python
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Customer:
    """客户定义"""
    id: str
    location: tuple  # (lat, lon)
    demand: float
    time_window: tuple = None  # (earliest, latest)
    service_time: float = 0

@dataclass
class Vehicle:
    """车辆定义"""
    id: str
    capacity: float
    depot: tuple  # 车场位置
    max_distance: float = float('inf')
    max_time: float = float('inf')

class VRPDomainAdapter:
    """VRP领域适配器"""

    def __init__(self):
        self.domain_type = "vehicle_routing"
        self.industry = "logistics"

    def analyze_domain_context(self, requirements: Dict) -> Dict:
        """分析VRP领域上下文"""
        context = {
            'problem_type': self._identify_vrp_variant(requirements),
            'vehicles': self._parse_vehicles(requirements),
            'customers': self._parse_customers(requirements),
            'constraints': self._extract_constraints(requirements)
        }
        return context

    def _identify_vrp_variant(self, requirements: Dict) -> str:
        """识别VRP变体"""
        has_capacity = bool(requirements.get('vehicle_capacity'))
        has_time_windows = bool(requirements.get('time_windows'))
        has_multi_depot = len(requirements.get('depots', [])) > 1

        if has_capacity and has_time_windows:
            return "CVRPTW"
        elif has_capacity:
            return "CVRP"
        elif has_time_windows:
            return "VRPTW"
        elif has_multi_depot:
            return "MDVRP"
        else:
            return "VRP"

    def extract_business_rules(self, context: Dict) -> List[Dict]:
        """提取VRP业务规则"""
        rules = []

        # 容量约束规则
        if context['problem_type'] in ['CVRP', 'CVRPTW']:
            rules.append({
                'type': 'capacity_constraint',
                'description': '车辆装载不得超过容量',
                'validation': lambda route, vehicle: sum(c.demand for c in route) <= vehicle.capacity
            })

        # 时间窗约束规则
        if context['problem_type'] in ['VRPTW', 'CVRPTW']:
            rules.append({
                'type': 'time_window_constraint',
                'description': '必须在客户时间窗内到达',
                'validation': lambda arrival_time, customer: (
                    customer.time_window[0] <= arrival_time <= customer.time_window[1]
                )
            })

        return rules
```

## 📊 示例

```python
# VRP问题定义
customers = [
    Customer(id='C1', location=(34.05, -118.25), demand=10, time_window=(8, 12)),
    Customer(id='C2', location=(34.10, -118.30), demand=15, time_window=(9, 14)),
    Customer(id='C3', location=(34.08, -118.28), demand=12, time_window=(10, 15))
]

vehicles = [
    Vehicle(id='V1', capacity=50, depot=(34.00, -118.20)),
    Vehicle(id='V2', capacity=50, depot=(34.00, -118.20))
]

# 使用适配器
adapter = VRPDomainAdapter()
context = adapter.analyze_domain_context({
    'customers': customers,
    'vehicles': vehicles,
    'vehicle_capacity': 50,
    'time_windows': True
})

print(f"识别为: {context['problem_type']}")  # 输出: CVRPTW
```

---

**模块版本**: 1.0.0
**维护者**: 领域应用专家智能体
**状态**: ✅ 已完成
