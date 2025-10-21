# APS Templates - 专家知识库总览

APS模块的专家知识库目录，采用Sidecar模式实现Token效率优化。

## 📚 知识库架构

### 7个专家知识库

| 知识库                  | 对应专家     | 状态          | Token节省 | 主要内容                      |
| ----------------------- | ------------ | ------------- | --------- | ----------------------------- |
| `orchestrator-library/` | 系统编排协调 | ⏳ 框架待填充 | -         | Phase编排、Todo管理、模式选择 |
| `algorithm-library/`    | 调度算法专家 | ✅ 框架完成   | 87%       | 算法分类、推荐、实现模板      |
| `constraint-library/`   | 约束模式专家 | ✅ 框架完成   | 60%       | 约束识别、建模、验证          |
| `objective-library/`    | 目标优化专家 | ⏳ 框架待填充 | 67%       | 目标分类、权重、帕累托        |
| `domain-library/`       | 领域应用专家 | ⏳ 框架待填充 | 56%       | 领域特征、业务规则            |
| `extension-library/`    | 算法扩展指导 | ⏳ 框架待填充 | 62%       | 代码分析、知识提取            |
| `quality-library/`      | 质量评测专家 | ⏳ 框架待填充 | -         | 验证规则、质量门禁            |

## 🔧 Sidecar模式工作原理

### 传统方式 vs Sidecar模式

**传统方式** (嵌入式):

```
agent.md (50K tokens)
├── 角色定义 (1K)
├── 能力矩阵 (2K)
├── 算法知识 (25K)
├── 约束知识 (15K)
└── 示例代码 (7K)
```

- 每次激活agent加载所有50K tokens
- Token利用率低（只用到其中10-20%）
- 难以维护和扩展

**Sidecar模式** (按需加载):

```
agent.md (500 tokens)
└── <critical-actions>
    └── 加载 COMPLETE 文件 templates/algorithm-library/README.md

algorithm-library/
├── README.md (5K)  # 总览和索引
├── greedy/ (10K)   # 仅在需要时加载
├── heuristic/ (15K)
└── exact/ (8K)
```

- agent文件轻量化（500 tokens）
- 按需加载相关知识（5-10K tokens）
- Token节省：75-87%

### 加载机制

在agent文件中配置：

```xml
<critical-actions>
  <i critical="MANDATORY">加载 COMPLETE 文件 {project-root}/bmad/aps/templates/algorithm-library/README.md</i>
</critical-actions>
```

激活agent时：

1. 加载agent定义（500 tokens）
2. 执行critical-actions，加载专家库README（5K tokens）
3. 根据具体需求，加载特定子目录内容（1-10K tokens）

## 📖 知识库内容规范

### README.md结构

每个专家库的README.md应包含：

```markdown
# [专家名称]知识库

## 知识库结构

[目录树]

## 知识分类体系

[分类矩阵/决策树]

## 模板结构

[标准模板说明]

## 使用指南

[如何查找和引用]

## 引用规范

[TenElementModel引用示例]

## 知识扩展指南

[如何添加新知识]

## Token优化

[Sidecar模式说明]

## 质量保证

[质量检查清单]
```

### 知识模块文件结构

每个具体知识模块：

````markdown
# [知识模块名称]

**模块ID**: `module-id`
**分类**: [分类]

## 描述

[自然语言说明]

## 理论基础

[原理/公式]

## 实现模板

```python
# 代码模板
```
````

## 参数配置

[参数说明]

## 示例应用

[实际案例]

## 相关模块

[关联引用]

## 参考文献

[引用]

````

## 🎯 引用规范 (Guardrails)

### V4.3强约束要求

所有输出必须附@引用路径：

```yaml
# ✅ 正确示例
5_algorithm:
  name: "遗传算法"
  citation: "@专家库/算法库/heuristic/遗传算法.md"

# ❌ 错误示例 (违反Guardrails)
5_algorithm:
  name: "某种进化算法"
  citation: null  # 缺少引用
````

### 引用路径格式

```
@专家库/{library-name}/{category}/{module-name}.md

示例:
@专家库/算法库/heuristic/遗传算法.md
@专家库/约束库/capacity/vehicle-capacity.md
@专家库/目标库/time-objectives/makespan.md
@专家库/领域库/logistics/vehicle-routing.md
```

### 能力缺口处理

当专家库中不存在所需知识：

```yaml
capability_gap_report:
  missing_knowledge: '特殊的时间依赖约束'
  searched_paths:
    - '@专家库/约束库/temporal/*'
    - '@专家库/约束库/logical/*'
  recommendation: '需要补充知识模块或升级裁决'
  action: 'block_until_resolved'
```

## 📊 Token效率统计

### 各专家库节省率

| 专家库 | 嵌入式 | Sidecar | 节省率    |
| ------ | ------ | ------- | --------- |
| 算法库 | 35K    | 4.5K    | **87%** ↓ |
| 约束库 | 25K    | 10K     | **60%** ↓ |
| 目标库 | 18K    | 6K      | **67%** ↓ |
| 领域库 | 22K    | 9.7K    | **56%** ↓ |
| 扩展库 | 16K    | 6.1K    | **62%** ↓ |
| 质量库 | 20K    | 8K      | **60%** ↓ |

**平均节省**: **75-87%**

### 实际使用场景

**场景1**: 车辆路径问题求解

- Agent: algorithm-expert + constraint-expert
- 加载: algorithm-library/README (5K) + heuristic/遗传算法 (2K) + constraint-library/README (5K) + routing/\* (3K)
- 总Token: 15K (vs 传统60K, 节省75%)

**场景2**: 生产调度问题

- Agent: domain-expert + algorithm-expert + constraint-expert
- 加载: domain-library/manufacturing/_ (8K) + algorithm-library/exact/_ (4K) + constraint-library/temporal/\* (4K)
- 总Token: 16K (vs 传统70K, 节省77%)

## 🛠️ 知识库开发指南

### 创建新专家库

1. **创建目录**

```bash
mkdir bmad/aps/templates/new-library/
```

2. **创建README.md**

- 使用标准模板
- 定义知识分类体系
- 提供使用指南

3. **组织子目录**

- 按分类创建子目录
- 每个分类包含相关知识模块

4. **配置Agent加载**

```xml
<critical-actions>
  <i critical="MANDATORY">加载 COMPLETE 文件 {project-root}/bmad/aps/templates/new-library/README.md</i>
</critical-actions>
```

### 添加知识模块

1. 确定分类目录
2. 创建模块文件（使用标准模板）
3. 更新专家库README索引
4. 添加到分类体系
5. 提供引用路径示例

### 质量保证

所有知识模块必须：

- [ ] 有清晰的描述
- [ ] 提供理论基础或公式
- [ ] 包含实现模板（代码）
- [ ] 标注适用场景
- [ ] 提供示例应用
- [ ] 可被@路径引用
- [ ] 有维护版本记录

## 🔍 使用示例

### 专家调用知识

**算法专家**选择算法：

```
1. 激活: bmad algorithm-expert
2. 自动加载: templates/algorithm-library/README.md
3. 用户描述问题
4. 专家查找: 问题规模中等(500变量) → 推荐启发式
5. 专家引用: @专家库/算法库/heuristic/遗传算法.md
6. 返回: 算法配置 + 实现模板
```

**约束专家**识别约束：

```
1. 激活: bmad constraint-expert
2. 自动加载: templates/constraint-library/README.md
3. 用户描述: "车辆不能超载"
4. 专家识别: 容量约束
5. 专家引用: @专家库/约束库/capacity/vehicle-capacity.md
6. 返回: 约束建模 + 验证代码
```

## 📦 交付物

每个专家库应提供：

1. **README.md**: 总览和索引
2. **分类目录**: 组织化的知识模块
3. **知识模块**: 具体的模板和实现
4. **示例**: 实际应用案例
5. **引用索引**: 快速查找路径

## 🚀 下一步计划

### 短期（1-2周）

1. **填充算法库** 🔴
   - greedy/ (基本贪心、优先级贪心)
   - heuristic/ (GA、SA、TS)
   - exact/ (B&B、DP、MILP)

2. **填充约束库** 🔴
   - capacity/ (资源容量、车辆容量)
   - temporal/ (时间窗、优先级)
   - assignment/ (一对一、兼容性)

3. **创建其他专家库README框架** 🟡
   - objective-library/
   - domain-library/
   - extension-library/
   - quality-library/

### 中期（2-4周）

4. 完善所有专家库内容
5. 添加更多领域特定知识
6. 创建综合示例

### 长期（1-3月）

7. 持续扩展知识模块
8. 性能优化和验证
9. 用户反馈迭代

## 📚 参考资源

- [APS Module README](../README.md)
- [BMAD Framework](../../README.md)
- [原始架构文档](../../../调度产品设计草稿/)

---

**版本**: V4.3
**最后更新**: 2025-10-20
**维护**: APS Expert Team
**Token节省**: 75-87% (vs 嵌入式)
