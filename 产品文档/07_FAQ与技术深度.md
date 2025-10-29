# 十三、常见问题FAQ

## 13.1 产品相关

**Q1: APS与传统优化软件（如Gurobi、CPLEX）有什么区别？**

A:

- **定位不同**: 传统软件是求解器，需要用户手工建模；APS是端到端平台，自动完成建模到代码生成
- **易用性**: 传统软件需要OR专家；APS只需自然语言描述需求
- **开发效率**: 传统方式2-4周；APS只需70-130分钟
- **知识沉淀**: 传统方式依赖个人；APS通过知识模板持续积累
- **交付物**: 传统方式仅代码；APS包含代码+文档+可追溯性

**Q2: APS能保证生成的代码直接可用吗？**

A:

- **92%可用率**: 当前版本基于大量测试，92%的代码可以直接运行
- **8%需调试**: 主要是特殊业务逻辑、数据格式适配
- **质量保证**: 通过6层质量门禁验证，包括语法、逻辑、一致性检查
- **持续优化**: 目标是在V2.0达到95%可用率

**Q3: 如果APS生成的方案不满足需求怎么办？**

A:

1. **使用优化功能** (\*optimize-solution): 自然语言描述优化需求，系统迭代改进
2. **调整参数**: 修改TenElementModel中的约束/目标权重
3. **人工介入**: 在关键决策点(P0-P4)进行人工干预

**Q4: APS支持哪些类型的调度问题？**

A: 目前覆盖：

- **物流配送**: 车辆路径问题(VRP)、时间窗约束(VRPTW)、多配送中心等
- **生产调度**: 作业车间调度(JSP)、流水线调度、设备维护排程
- **人员排班**: 护士排班、客服排班、保安巡逻
- **项目管理**: 任务调度、资源分配、关键路径
- **供应链**: 库存优化、补货计划、供应商选择

未来将扩展至云计算资源调度、电网调度、医院手术室排程等领域。

---

## 13.2 技术相关

**Q5: APS的AI模型是什么？Token消耗如何？**

A:

- **默认模型**: Claude Sonnet 4.5 (Anthropic)
- **Token优化**: 通过Sidecar模式，平均每次求解8-15K tokens
- **成本估算**:
  - 单次求解: ¥15-30 (LLM调用成本)

**Q6: 状态持久化是如何工作的？**

A:

- **自动保存**: 每个Phase完成后自动保存状态文件(YAML格式)
- **保存位置**: 本地文件系统或云存储(S3/OSS)
- **验证机制**: 保存后立即验证文件完整性，失败则重试
- **智能恢复**: \*resume命令自动检测断点，加载上下文，继续执行
- **保留策略**: 保留最近30天和最新5个版本

**Q7: APS的数据安全如何保障？**

A:

- **数据加密**:
  - 传输加密: TLS 1.3
  - 存储加密: AES-256
- **隔离保护**: 多租户隔离或私有化部署
- **访问控制**:
  - API认证: JWT Token
  - 权限管理: RBAC
- **审计日志**: 完整记录所有操作
- **合规性**: 符合GDPR、等保2.0要求

**Q8: 如何扩展APS的知识库？**

A:

1. **社区贡献** (开源版):
   - Fork仓库，添加新模板
   - Pull Request审核后合并
   - 贡献者可获得社区积分

2. **算法扩展指导**:
   ```bash
   bmad extension-guide
   > *analyze-code
   # 输入现有算法代码
   # 系统自动提取知识，生成模板
   ```

---

## 13.3 使用相关

**Q9: 完成一次完整求解需要多长时间？**

A:

- **模式A (集中确认)**: 70-95分钟
  - 适合需求清晰的专家用户
  - 一次性确认完整TenElementModel
  - 专家并行分析

- **模式B (增量确认)**: 95-130分钟
  - 适合需求探索的业务用户
  - 分步确认，上下文丰富
  - 专家串行分析

- **优化现有方案**: 15-30分钟
  - 基于已有方案迭代
  - 局部调整，快速验证

**Q10: 我没有调度优化背景，能使用APS吗？**

A: 完全可以！

- **自然语言输入**: 用业务语言描述需求，无需懂数学建模
- **引导式交互**: 系统会在关键点提示和引导
- **模式B推荐**: 增量确认模式更适合非专家用户
- **学习资源**:
  - 50+案例库学习
  - 在线文档和教程
  - 社区问答支持

**Q11: APS支持实时调度吗？**

A:

- **当前版本**: 主要用于离线优化（批量调度规划）
- **响应时间**: 70-130分钟完成建模和代码生成
- **代码可实时**: 生成的代码可部署为实时服务
- **V2.0规划**: 将支持在线优化和秒级响应

**Q12: 能否将APS集成到现有系统？**

A: 完全支持：

- **数据对接**: 支持多种数据格式(JSON/CSV/Excel/数据库)
- **集成示例**: 提供ERP、MES、WMS等系统集成案例

---

# 十四、技术深度解析

## 14.1 "Agent as Doc"架构剖析

### 传统LLM Agent架构的问题

```
┌─────────────────────────────────────────┐
│  Prompt (巨大的单体Prompt)              │
│  ├─ System Prompt (角色定义)            │
│  ├─ Domain Knowledge (领域知识嵌入)     │
│  │   ├─ 算法知识 (25K tokens)          │
│  │   ├─ 约束知识 (15K tokens)          │
│  │   ├─ 目标知识 (10K tokens)          │
│  │   └─ 领域知识 (12K tokens)          │
│  ├─ Examples (示例)                     │
│  └─ Instructions (指令)                 │
│                                          │
│  总计: 70K+ tokens                       │
│  利用率: 10-20%                          │
│  维护成本: 极高                          │
└─────────────────────────────────────────┘

问题:
  ✗ Token浪费严重（加载全部知识，使用很少）
  ✗ 维护困难（修改需重写整个Prompt）
  ✗ 扩展性差（新增知识导致Prompt膨胀）
  ✗ 版本管理混乱
  ✗ 团队协作冲突
```

### APS的"Agent as Doc"创新架构

```
┌─────────────────────────────────────────────────────────┐
│  Agent Definition (轻量级智能体定义 ~500 tokens)       │
│  ├─ metadata: {id, name, title, icon, module}          │
│  ├─ persona: {role, identity, communication, principles}│
│  ├─ critical_actions:                                   │
│  │   └─ "加载 COMPLETE 文件 templates/xxx-library/README.md" │
│  └─ menu: {commands and workflows}                     │
└─────────────────────────────────────────────────────────┘
                            ↓ 运行时动态加载
┌─────────────────────────────────────────────────────────┐
│  Knowledge Library (知识文档库 - Sidecar模式)          │
│  ├─ algorithm-library/                                  │
│  │   ├─ README.md (5K tokens) ← 总览和索引            │
│  │   ├─ exact/分支定界.md (2K)                         │
│  │   ├─ heuristic/遗传算法.md (2.5K)                   │
│  │   └─ meta-heuristic/禁忌搜索.md (2K)                │
│  ├─ constraint-library/                                 │
│  │   ├─ README.md (5K tokens)                          │
│  │   ├─ temporal/时间窗约束.md (1.5K)                  │
│  │   └─ capacity/容量约束.md (1K)                      │
│  └─ ...                                                 │
│                                                          │
│  按需加载: 仅加载相关模块 (~8-15K tokens)               │
│  利用率: 80-90%                                         │
│  维护成本: 低（模块化，独立维护）                        │
└─────────────────────────────────────────────────────────┘

优势:
  ✓ Token效率: 节省75-87%
  ✓ 维护性: 模块化，独立版本
  ✓ 扩展性: 新增模板不影响其他
  ✓ 协作性: 多人并行开发知识模块
  ✓ 复用性: 知识模板跨智能体复用
```

### 动态加载流程

```python
# 伪代码示例
class AlgorithmExpert(Agent):
    def __init__(self):
        # 1. 加载轻量Agent定义 (500 tokens)
        self.load_agent_definition("agents/algorithm-expert.yaml")

        # 2. 执行critical_actions，加载专家库README (5K tokens)
        self.load_knowledge_index(
            "templates/algorithm-library/README.md"
        )
        # 此时拥有算法分类体系、决策树、索引

    def recommend_algorithm(self, problem_features):
        # 3. 根据问题特征，动态加载相关模块
        if problem_features.scale == "medium" and \
           problem_features.constraints_complexity == "high":
            # 仅加载需要的算法模块 (2.5K tokens)
            ga_template = self.load_template(
                "meta-heuristic/遗传算法.md"
            )

        # 4. 基于模板生成方案
        return self.generate_solution(ga_template, problem_features)

# 总Token消耗: 500 + 5000 + 2500 = 8000 tokens
# 传统方式: 50000+ tokens
# 节省: 84%
```

---

## 14.2 TenElementModel 统一真相源

### 为什么需要TenElementModel？

调度优化涉及多个专家（算法、约束、目标、领域），如果没有统一的数据模型，会导致：

- 专家之间信息不一致
- 重复沟通和确认
- 集成时发现冲突
- 无法追溯决策依据

### TenElementModel设计

```yaml
TenElementModel:
  # 1. 决策变量 (What to decide)
  decision_variables:
    - name: 'vehicle_routes'
      type: 'sequence'
      domain: '客户集合的排列'
      size: '12条路径（对应12辆车）'

    - name: 'delivery_time'
      type: 'continuous'
      domain: '[11:00, 19:00]'
      size: '100个时间点（对应100个客户）'

  # 2. 参数 (Known data)
  parameters:
    vehicles:
      count: 12
      capacity: 150 # 件/车
      type: '冷藏车'

    customers:
      count: 100
      demands: '5-20件/客户'
      time_windows: '11:00-19:00'

  # 3. 约束 (Constraints)
  constraints:
    - id: 'C1'
      name: '车辆容量约束'
      type: 'hard_constraint'
      formula: '∀j: Σ(demand_i) ≤ 150, i∈route_j'
      citation: '@专家库/约束库/capacity/车辆容量约束.md'

    - id: 'C2'
      name: '时间窗约束'
      type: 'hard_constraint'
      formula: '∀i: start_time_i ∈ [11:00, 19:00]'
      citation: '@专家库/约束库/temporal/时间窗约束.md'

  # 4. 优化目标 (Objectives)
  objectives:
    primary:
      name: '总成本最小化'
      formula: |
        minimize:
          Σ(Fixed_Cost × Vehicles_Used) +
          Σ(Distance × Distance_Rate × 1.3) +
          Σ(Work_Time × Labor_Rate)
      weight: 0.7
      citation: '@专家库/目标库/cost/成本最小化.md'

  # 5. 算法 (Algorithm)
  algorithm:
    primary:
      name: '遗传算法 (Genetic Algorithm)'
      type: 'meta-heuristic'
      config:
        population_size: 100
        crossover_rate: 0.8
        mutation_rate: 0.05
        max_generations: 500
      citation: '@专家库/算法库/meta-heuristic/遗传算法.md'

  # 6. 时间模型 (Time Model)
  time_model:
    planning_horizon: '1天 (11:00-19:00)'
    time_granularity: '分钟级'
    travel_time_calculation: '距离/平均速度(30km/h)'

  # 7. 不确定性 (Uncertainty)
  uncertainty:
    - factor: '客户需求量'
      type: 'deterministic'
      note: '假设订单确定'

    - factor: '交通状况'
      type: 'stochastic'
      distribution: '正态分布 N(μ, 0.15μ)'
      handling: '鲁棒优化 + 15%时间缓冲'

  # 8. 求解配置 (Solver Configuration)
  solver_config:
    time_limit: '600秒'
    optimality_gap: '5%'
    solution_pool_size: 10
    parallel_threads: 4

  # 9. 输入数据 (Input Data)
  input_data_format:
    customers:
      format: 'CSV'
      fields:
        - customer_id: '整数'
        - latitude: '浮点数'
        - longitude: '浮点数'
        - demand: '整数'

  # 10. 输出格式 (Output Format)
  output_format:
    solution:
      format: 'JSON'
      structure:
        routes: 'List[List[int]]'
        delivery_times: 'List[str]'
        total_cost: 'float'

# 元数据
metadata:
  created_at: '2025-10-28T10:15:00Z'
  phase: 'phase_1_5'
  mode: 'mode_a'
  user_confirmed: true
  model_hash: 'sha256:abc123...' # 用于一致性验证
```

### TenElementModel的价值

```yaml
作为统一真相源:
  ✓ 专家协调: 所有专家基于同一模型工作
  ✓ 一致性保证: Phase 2-4持续验证与模型一致性
  ✓ 可追溯性: 代码每个部分都能追溯到模型元素
  ✓ 沟通语言: 用户、专家、系统的共同语言

作为质量标准:
  ✓ 完整性检查: 10个要素必须全部定义
  ✓ 引用验证: 每个元素必须有@引用路径
  ✓ 参数合理性: 自动检查参数值的合理范围
  ✓ 冲突检测: 约束与目标的冲突检测

作为持久化对象:
  ✓ Phase 1.5保存: 作为关键依赖状态保存
  ✓ Phase 2加载: 专家分析时加载
  ✓ Phase 3验证: 代码生成时对齐验证
  ✓ Phase 4审计: 质量门禁最终审计
```
