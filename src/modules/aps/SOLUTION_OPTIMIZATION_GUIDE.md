# 方案优化使用指南

**版本**: V4.3
**创建日期**: 2025-10-27

---

## 📋 目录

1. [快速开始](#快速开始)
2. [使用场景](#使用场景)
3. [详细示例](#详细示例)
4. [常见问题](#常见问题)
5. [进阶技巧](#进阶技巧)

---

## 快速开始

### 基本流程

```bash
# 1. 生成初始方案
optimize-solution

# 2. 调用方案优化
optimize-solution

# 3. 用自然语言描述需求
用户: "增加一个资源互斥约束，确保同一设备不能同时处理多个任务"

# 4. Orchestrator自动理解并调用专家
Orchestrator:
  ✓ 识别意图: 约束修改
  ✓ 将调用: 约束专家
  [自动执行...]
  ✅ 完成！新代码已生成

# 5. 测试代码
python aps-outputs/models/scheduling_solution_xxx.py
```

### 三步使用

1. **生成初始方案** - 运行完整workflow获得第一版方案
2. **用自然语言说明需求** - 告诉Orchestrator你想调整什么
3. **测试新代码** - Orchestrator自动生成优化后的代码

---

## 使用场景

### 场景1: 增加约束条件

**你的需求**：
"我发现方案没有考虑资源互斥，同一台设备不能同时处理多个任务，需要增加这个约束"

**Orchestrator自动完成**：

- 识别为约束修改
- 调用约束专家
- 从专家库检索"资源互斥约束"
- 添加硬约束并维护引用
- 同步到TenElementModel
- 生成新代码

**你的操作**：

```bash
optimize-solution

# 描述需求
"增加资源互斥约束，同一设备不能同时处理多个任务"

# 等待完成...
✅ 完成！新代码已生成
```

---

### 场景2: 优化算法性能

**你的需求**：
"遗传算法运行太慢了，能不能优化一下参数"

**Orchestrator自动完成**：

- 识别为算法优化
- 调用算法专家
- 分析当前参数
- 提出优化建议（增加种群、减少迭代）
- 更新配置并生成代码

**你的操作**：

```bash
optimize-solution

"算法太慢了，能优化吗"

# Orchestrator自动优化参数
✅ 算法专家已调整参数，预计速度提升40%
```

---

### 场景3: 调整目标权重

**你的需求**：
"准时交货应该是最重要的目标，比最小化完工时间更重要"

**Orchestrator自动完成**：

- 识别为目标调整
- 调用目标专家
- 分析当前目标层级
- 交换主次目标
- 更新多目标权重
- 生成新代码

**你的操作**：

```bash
optimize-solution

"准时交货应该是最重要的"

# Orchestrator自动调整目标层级
✅ 目标专家已将准时交货提升为主目标
```

---

### 场景4: 领域适配

**你的需求**：
"这个方案对生鲜配送不太适用，需要考虑温度控制和保质期"

**Orchestrator自动完成**：

- 识别为领域适配
- 调用领域专家 + 约束专家（协同）
- 识别"冷链物流"领域特性
- 建议增加温度控制、保质期等约束
- 自动添加这些约束
- 生成新代码

**你的操作**：

```bash
optimize-solution

"需要考虑冷链物流的温度控制"

# Orchestrator自动协调多个专家
✅ 已适配冷链物流领域，增加了4个约束
```

---

### 场景5: 多意图组合

**你的需求**：
"准时交货应该更重要，另外再加一个时间窗约束，允许30分钟误差"

**Orchestrator自动完成**：

- 识别多个意图（目标调整 + 约束添加）
- 需要多专家协同
- 确定调用顺序（约束专家 → 目标专家）
- 依次执行
- 生成新代码

**你的操作**：

```bash
optimize-solution

"准时交货应该更重要，另外再加一个时间窗约束，允许30分钟误差"

# Orchestrator自动协调多专家
🤝 多专家协同模式
  1️⃣ 约束专家
  2️⃣ 目标专家
✅ 完成！
```

---

## 详细示例

### 示例1：增加资源互斥约束（完整输出）

```
用户: optimize-solution

Orchestrator: 请告诉我您想如何优化方案？

用户: 增加一个资源互斥约束，确保同一设备不能同时处理多个任务

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 理解您的需求...
━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 识别意图: 约束修改 (置信度: 0.92)
  ✓ 复杂度: 简单
  📞 将调用: constraint-expert

━━━━━━━━━━━━━━━━━━━━━━━━
📂 加载现有方案...
━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 文件: solution_data_20251027_143530.yaml
  ✓ 版本: 1.0
  ✓ 优化次数: 0

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 调用 constraint-expert
━━━━━━━━━━━━━━━━━━━━━━━━
  📋 约束专家分析用户需求...
    ✓ 操作类型: 增加约束
    ✓ 识别约束类型: 资源互斥约束
    📚 专家库引用: @constraint-library/logical/互斥约束.md
    ✓ 已添加硬约束: 资源互斥约束
       - 类型: 硬约束
       - 处理方法: repair
       - 引用: @constraint-library/logical/互斥约束.md
       - 置信度: 0.90
  ✓ constraint-expert 完成

━━━━━━━━━━━━━━━━━━━━━━━━
🔄 同步到TenElementModel...
━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 已同步约束列表: 6个约束
  ✓ 已同步目标列表: 3个目标
  ✓ TenElementModel版本: 1.0.refined

━━━━━━━━━━━━━━━━━━━━━━━━
💾 保存优化方案...
━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 文件: solution_data_optimized_v1_20251027_154530.yaml
  ✓ 路径: aps-outputs/docs/solution_data_optimized_v1_20251027_154530.yaml
  ✓ 大小: 15234 bytes
  ✓ 优化版本: v1

━━━━━━━━━━━━━━━━━━━━━━━━
💻 自动生成代码...
━━━━━━━━━━━━━━━━━━━━━━━━
  📂 输入: solution_data_optimized_v1_20251027_154530.yaml
  🔄 调用: generate-code-from-yaml.md
  ✓ 代码已生成: scheduling_solution_20251027_154530.py
  ✓ 路径: aps-outputs/models/scheduling_solution_20251027_154530.py

==================================================
✅ 优化完成！
==================================================

📊 修改摘要:

👥 调用专家: constraint-expert

📝 具体修改:
  约束专家:
    - 新增硬约束: 资源互斥约束
    - 影响范围: 约束验证模块

📁 生成文件:
  ✓ 优化方案: solution_data_optimized_v1_20251027_154530.yaml
     版本: v1
  ✓ 生成代码: scheduling_solution_20251027_154530.py

💡 下一步:
  1. 测试新代码: python aps-outputs/models/scheduling_solution_20251027_154530.py
  2. 如需继续优化，再次运行 optimize-solution
  3. 查看方案文档: aps-outputs/docs/solution_data_optimized_v1_20251027_154530.yaml
```

---

### 示例2：多专家协同（领域+约束）

```
用户: "这个方案对生鲜配送不太适用，需要考虑温度控制和保质期"

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 理解您的需求...
━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 识别意图1: 领域适配 (置信度: 0.85)
  ✓ 识别意图2: 约束修改 (置信度: 0.70)
  ⚠️ 复杂度: 中等
  ⚠️ 需要多专家协同
  📞 将调用: domain-expert, constraint-expert

📋 专家调用顺序:
  1️⃣ domain-expert
  2️⃣ constraint-expert

🤝 多专家协同模式

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 第1步：调用 domain-expert
━━━━━━━━━━━━━━━━━━━━━━━━
  📋 领域专家分析用户需求...
    ✓ 识别领域: 冷链物流
    📚 专家库引用: @domain-library/vehicle/冷链物流最佳实践.md
    💡 领域专家建议:
       该领域的核心特点:
         - 温度控制
         - 保质期管理
         - 时效性
         - 包装要求
       建议增加以下约束:
         - 温度控制约束
         - 保质期约束
         - 配送时效约束
    ⚠️ 提示: 领域专家会触发约束专家自动添加这些约束
  ✓ domain-expert 完成

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 第2步：调用 constraint-expert
━━━━━━━━━━━━━━━━━━━━━━━━
  基于领域专家建议，添加约束...

  ✓ 已添加约束1: 温度控制约束
     - 类型: 硬约束
     - 温度范围: 0-4°C（冷藏）/-18°C（冷冻）

  ✓ 已添加约束2: 保质期约束
     - 类型: 硬约束
     - 最大配送时长: 24小时

  ✓ 已添加约束3: 配送时效约束
     - 类型: 软约束
     - 理想时效: 2小时
     - 惩罚权重: 0.8

  ✓ constraint-expert 完成

[同步TenElementModel...]
[保存优化方案...]
[自动生成代码...]

==================================================
✅ 优化完成！
==================================================

📊 修改摘要:

👥 调用专家: domain-expert, constraint-expert

📝 具体修改:
  领域专家:
    - 适配了领域特性: 冷链物流
  约束专家:
    - 新增硬约束: 温度控制约束, 保质期约束
    - 新增软约束: 配送时效约束

📁 生成文件:
  ✓ 优化方案: solution_data_optimized_v1_20251027_160530.yaml
  ✓ 生成代码: scheduling_solution_20251027_160530.py

⚠️ 重要提示:
  生鲜配送场景下，建议您：
  1. 准备温度传感器数据接口
  2. 确保车辆信息包含冷藏设备参数
  3. 测试时使用真实的保质期数据
```

---

## 常见问题

### Q1: Orchestrator无法识别我的需求怎么办？

**A**: 如果意图不明确，Orchestrator会主动澄清：

```
Orchestrator: 我理解您想做一些调整，但有两种可能：

1. 修改约束条件
   例如：增加新约束、调整约束参数等
   将调用: 约束专家

2. 调整目标权重
   例如：改变目标优先级、修改权重等
   将调用: 目标专家

请告诉我您具体想调整哪一项。
```

**解决方法**：

- 更明确地描述需求
- 使用关键词："约束"、"算法"、"目标"、"领域"
- 举例说明

---

### Q2: 如何查看修改了哪些内容？

**A**: 有三种方式：

1. **查看修改摘要**（自动显示）

   ```
   📊 修改摘要:
     - 新增硬约束：资源互斥约束
     - 影响范围：约束验证模块
   ```

2. **对比YAML文件**

   ```bash
   # 原始方案
   cat aps-outputs/docs/solution_data_20251027_143530.yaml

   # 优化后方案
   cat aps-outputs/docs/solution_data_optimized_v1_20251027_154530.yaml
   ```

3. **查看代码diff**
   ```bash
   diff aps-outputs/models/scheduling_solution_old.py \
        aps-outputs/models/scheduling_solution_new.py
   ```

---

### Q3: 可以连续多次优化吗？

**A**: 完全可以！每次优化都会基于上一版本：

```bash
# 第1次优化
optimize-solution
"增加资源互斥约束"
✅ v1 生成

# 测试发现还需要调整...

# 第2次优化（基于v1）
optimize-solution
"再增加一个时间窗约束"
✅ v2 生成

# 第3次优化（基于v2）
optimize-solution
"时间窗的惩罚权重提高到0.8"
✅ v3 生成
```

每个版本都会保留，方便回溯。

---

### Q4: 优化会破坏之前的代码吗？

**A**: 不会！每次优化都会：

- 生成新的文件（带时间戳和版本号）
- 保留原有文件
- 文件命名清晰可区分

```
aps-outputs/docs/
├── solution_data_20251027_143530.yaml          # 原始
├── solution_data_optimized_v1_20251027_154530.yaml  # 优化v1
├── solution_data_optimized_v2_20251027_160530.yaml  # 优化v2
└── solution_data_optimized_v3_20251027_162530.yaml  # 优化v3

aps-outputs/models/
├── scheduling_solution_20251027_143530.py      # 原始
├── scheduling_solution_20251027_154530.py      # 优化v1
├── scheduling_solution_20251027_160530.py      # 优化v2
└── scheduling_solution_20251027_162530.py      # 优化v3
```

---

### Q5: 如何知道哪个版本最好？

**A**: 建议建立测试流程：

```bash
# 测试脚本
for version in v1 v2 v3; do
  echo "测试版本: $version"
  python aps-outputs/models/scheduling_solution_${version}.py \
    --test-data test_data.json \
    --output results_${version}.json
done

# 比较结果
python compare_results.py results_v1.json results_v2.json results_v3.json
```

---

## 进阶技巧

### 技巧1: 使用更精确的描述

**普通描述**：

```
"算法慢"
```

**更好的描述**：

```
"遗传算法的收敛速度慢，希望在保证解质量的前提下提升30%的速度"
```

Orchestrator会更准确地理解你的需求。

---

### 技巧2: 一次描述多个需求

**可以这样**：

```
"准时交货应该是最重要的目标，另外再加一个时间窗约束，允许30分钟误差，
 同时算法参数也需要优化，现在跑得太慢了"
```

Orchestrator会：

1. 识别3个意图（目标、约束、算法）
2. 自动协调3个专家
3. 按正确顺序执行

---

### 技巧3: 利用领域知识

**如果你说**：

```
"这是冷链物流场景"
```

Orchestrator会自动：

- 调用领域专家识别冷链特性
- 建议增加温度、保质期等约束
- 自动添加这些约束

**比手动逐个添加约束快得多！**

---

### 技巧4: 参数化调整

**可以指定具体数值**：

```
"时间窗约束的允许误差从15分钟调整到30分钟"
"遗传算法的种群大小改成200"
"准时交货的权重提高到0.8"
```

Orchestrator会提取并应用这些具体数值。

---

### 技巧5: 查看专家调用历史

```bash
# 查看优化历史
cat aps-outputs/docs/solution_data_optimized_v3_xxx.yaml | grep refinement

# 输出
refinement_count: 3
last_refined_at: 2025-10-27T16:25:30
refinement_history:
  - iteration: 1
    expert: constraint-expert
    change: 添加资源互斥约束
  - iteration: 2
    expert: objective-expert
    change: 调整目标权重
  - iteration: 3
    expert: algorithm-expert
    change: 优化算法参数
```

---

## 总结

### ✅ 优势

1. **简单** - 自然语言交互，无需懂YAML
2. **智能** - 自动识别意图，调用合适专家
3. **快速** - 10分钟/次迭代
4. **安全** - 不破坏原有文件，可随时回溯
5. **完整** - 保持引用和可追溯性

### 🎯 使用流程

```
描述需求 → Orchestrator理解 → 自动调用专家 → 生成代码 → 测试
                                                         ↓
                                        如需继续调整 ←─┘
```

### 📞 获取帮助

- 查看示例：menu中的usage_examples
- 查看任务文档：src/modules/aps/tasks/orchestrate-solution-optimization.md
- 遇到问题：让Orchestrator澄清

---

**维护者**: APS Team
**反馈**: 如有问题或建议，请提交Issue

---

**最后更新**: 2025-10-27
