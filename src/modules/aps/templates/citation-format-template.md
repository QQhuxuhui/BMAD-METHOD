# 引用格式规范模板

**模板ID**: `citation-format-template`
**版本**: V4.3  
**用途**: 定义方案文档中引用信息的标准格式

---

## 📋 引用格式标准

###1️⃣ **章节级引用块**（用于主要决策点）

```markdown
### X.X 章节标题

**关键决策/内容**: XXX

**📖 专家库引用**:

- `@专家库名/分类/具体文件.md`
- `@专家库名/分类/另一个文件.md`

**📍 数据来源**:

- **Phase**: Phase X - XXX专家分析
- **状态文件**: `phase_X_state_YYYYMMDD_HHMMSS.yaml`
- **字段路径**: `state_data.expert_analysis.specific_field`
- **时间戳**: YYYY-MM-DD HH:MM:SS
- **Hash**: `xxxxxxxx`

**💯 置信度**: 0.XX (可选)

**🔗 详细追溯**: 见 [附录A2 - X.X](#a2-详细引用映射表)
```

###2️⃣ **表格中的引用**（用于参数配置等）

```markdown
| 参数名 | 值     | 理由     | 专家库引用                  |
| ------ | ------ | -------- | --------------------------- |
| param1 | value1 | 理由说明 | `@library/category/file.md` |
| param2 | value2 | 理由说明 | `@library/category/file.md` |
```

### 3️⃣ **简短引用**（用于次要信息）

```markdown
**来源**: Phase X - XXX专家 (`phase_X_state_xxx.yaml`)
```

---

## 📖 专家库引用格式

### 标准格式

```
@库名/分类路径/文件名.md
```

### 示例

#### 算法专家库

```
@algorithm-library/genetic-algorithms/hybrid-ga.md
@algorithm-library/parameter-tuning/population-sizing.md
@algorithm-library/local-search/tabu-search.md
```

#### 约束专家库

```
@constraint-library/classification/hard-soft.md
@constraint-library/handling-methods/repair-strategies.md
@constraint-library/validation/constraint-checking.md
```

#### 目标专家库

```
@objective-library/multi-objective/weighted-sum.md
@objective-library/delivery/order-fulfillment.md
@objective-library/utilization/resource-efficiency.md
```

#### 领域专家库

```
@domain-library/manufacturing/job-shop.md
@domain-library/logistics/vehicle-routing.md
@domain-library/healthcare/patient-scheduling.md
```

---

## 🗂️ 状态文件字段路径格式

### 标准格式

```
state_data.专家分析类型.具体字段.子字段
```

### 示例

#### Phase 1.5 (TenElementModel)

```
state_data.ten_element_model.decision_variables
state_data.ten_element_model.constraints
state_data.model_baseline.hash
```

#### Phase 2 (专家分析)

```
state_data.algorithm_recommendations.selected_algorithm
state_data.algorithm_recommendations.parameters.population_size
state_data.constraint_analysis.hard_constraints
state_data.constraint_analysis.handling_method.hard_constraint
state_data.objective_analysis.primary_objective
state_data.objective_analysis.multi_objective_approach
state_data.domain_analysis.industry_identification
```

---

## 📊 附录A1: 数据来源概览格式

```markdown
## 附录A1: 数据来源概览

本方案的所有数据来自以下状态文件，确保完整可追溯。

### Phase 1.5: TenElementModel (十要素建模)

- **文件路径**: `aps-outputs/states/phase_1_5_state_YYYYMMDD_HHMMSS.yaml`
- **时间戳**: YYYY-MM-DD HH:MM:SS
- **Hash**: `xxxxxxxxxxxxxxxx`
- **版本**: 4.3
- **包含内容**: 10要素完整定义（决策变量、参数、约束、目标等）

### Phase 2: 专家分析结果

- **文件路径**: `aps-outputs/states/phase_2_state_YYYYMMDD_HHMMSS.yaml`
- **时间戳**: YYYY-MM-DD HH:MM:SS
- **Hash**: `xxxxxxxxxxxxxxxx`
- **版本**: 4.3
- **包含内容**:
  - 领域专家分析 (domain_analysis)
  - 约束专家分析 (constraint_analysis)
  - 目标专家分析 (objective_analysis)
  - 算法专家分析 (algorithm_recommendations)
  - 一致性报告 (consistency_report)
```

---

## 📊 附录A2: 详细引用映射表格式

```markdown
## 附录A2: 详细引用映射表

以下表格提供了方案中每个关键决策的完整追溯信息。

### 5. 算法选择与配置

| 项目            | 值        | 状态文件字段路径                                                  | 专家库引用                                                 | 置信度 |
| --------------- | --------- | ----------------------------------------------------------------- | ---------------------------------------------------------- | ------ |
| 算法名称        | Hybrid GA | `state_data.algorithm_recommendations.selected_algorithm`         | `@algorithm-library/genetic-algorithms/hybrid-ga.md`       | 0.95   |
| population_size | 150       | `state_data.algorithm_recommendations.parameters.population_size` | `@algorithm-library/parameter-tuning/population-sizing.md` | 0.90   |

### 3. 约束处理策略

| 项目       | 方法/策略 | 状态文件字段路径                                        | 专家库引用                                                  | 置信度 |
| ---------- | --------- | ------------------------------------------------------- | ----------------------------------------------------------- | ------ |
| 硬约束处理 | repair    | `state_data.constraint_analysis.hard_constraint_method` | `@constraint-library/handling-methods/repair-strategies.md` | 0.92   |

### 4. 目标优化策略

| 项目       | 值/方法      | 状态文件字段路径                                         | 专家库引用                                           | 置信度 |
| ---------- | ------------ | -------------------------------------------------------- | ---------------------------------------------------- | ------ |
| 多目标方法 | weighted_sum | `state_data.objective_analysis.multi_objective_approach` | `@objective-library/multi-objective/weighted-sum.md` | 0.88   |

**说明**:

- 置信度范围 0.0-1.0，值越高表示该决策的可信度越高
- 状态文件字段路径格式: `state_data.专家分析.具体字段`
- 专家库引用格式: `@库名/分类/具体文件.md`
- 通过状态文件字段路径可以直接定位到原始数据
- 通过专家库引用可以查看详细的知识来源
```

---

## 🎨 图标使用规范

### 标准图标

- **📖** - 专家库引用
- **📍** - 数据来源/状态文件
- **🔗** - 详细追溯链接
- **💯** - 置信度
- **📊** - 数据/统计
- **🎯** - 目标/结果
- **⚙️** - 配置/参数
- **✅** - 验证通过
- **⚠️** - 警告/注意

### 使用场景

```markdown
**📖 专家库引用**: 标识来自专家知识库的内容
**📍 数据来源**: 标识状态文件和字段路径
**🔗 详细追溯**: 提供附录链接
**💯 置信度**: 标识决策的可信度
```

---

## 🔗 完整引用链示例

### 完整示例: 算法选择的可追溯链

```markdown
### 5.1 选定算法

**算法名称**: 混合遗传算法 (Hybrid Genetic Algorithm)

**选择理由**:

- 适合组合优化问题（作业车间调度）
- 支持复杂约束处理
- 已在类似制造业场景中验证有效

**📖 专家库引用**:

- `@algorithm-library/genetic-algorithms/hybrid-ga.md`
- `@algorithm-library/problem-types/job-shop-scheduling.md`
- `@algorithm-library/constraint-handling/penalty-repair-hybrid.md`

**📍 数据来源**:

- **Phase**: Phase 2 - 算法专家分析
- **状态文件**: `phase_2_state_20251024_160312.yaml`
- **字段路径**: `state_data.algorithm_recommendations.selected_algorithm`
- **时间戳**: 2025-10-24 16:03:12
- **Hash**: `b4c6d8e2f1a5b7c9`
- **专家**: 算法专家（张效率）

**💯 置信度**: 0.95

**🔗 详细追溯**: 见 [附录A2 - 5.1](#a2-详细引用映射表)

**追溯链**:
```

本决策 → phase_2_state.yaml → @algorithm-library/xxx → 专家知识

```

```

---

## 📝 使用指南

### 何时使用完整引用块？

✅ **使用场景**:

- 关键决策点（算法选择、约束方法、目标策略）
- 重要参数配置
- 复杂的技术决策
- 需要审计的内容

❌ **不使用场景**:

- 显而易见的信息
- 纯描述性内容
- 中间步骤
- 辅助说明

### 如何选择引用粒度？

| 内容重要性             | 推荐格式              |
| ---------------------- | --------------------- |
| 极其关键（算法选择等） | 完整引用块 + 附录表格 |
| 重要（参数配置等）     | 表格中包含引用列      |
| 一般（说明性内容）     | 简短引用格式          |
| 次要（辅助信息）       | 可省略引用            |

---

## ✅ 质量检查清单

方案文档应包含：

- [ ] 每个关键决策都有专家库引用
- [ ] 所有引用格式统一
- [ ] 附录A1完整（包含所有状态文件）
- [ ] 附录A2完整（包含所有关键决策）
- [ ] 字段路径准确
- [ ] Hash值正确
- [ ] 时间戳一致
- [ ] 引用链接有效

---

**创建**: 2025-10-24  
**BMAD版本**: v6-alpha  
**用途**: 确保方案文档引用格式的一致性和完整性
