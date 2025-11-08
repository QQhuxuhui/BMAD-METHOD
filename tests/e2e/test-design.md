# Phase 1 端到端测试设计

## 测试范围说明

基于实际完成的功能，本测试聚焦于**后端API集成测试**和**前端组件测试**，而非完整的浏览器端到端测试。

### 已完成功能

✅ 后端API：

- 用户注册/登录（JWT认证）
- 工作流CRUD操作
- HITL人机交互（暂停/恢复）
- LangServe流式传输端点

✅ 前端功能：

- 工作流监控界面
- 实时状态更新（SSE）
- HITL审批界面
- 拓扑可视化

## 1. 核心测试场景

### 场景1: API端点集成测试（优先级：P0）

**测试流程**：

```
用户注册 → 用户登录 → 创建工作流 → 查询状态 → HITL审批 → 查看结果
```

**测试文件**: `tests/e2e/test_api_integration.py`

**测试步骤**：

1. 注册新用户（POST /api/v1/auth/register）
2. 用户登录获取JWT Token（POST /api/v1/auth/login）
3. 创建优化工作流（POST /api/v1/workflows/）
4. 轮询查询工作流状态（GET /api/v1/workflows/{id}）
5. 等待HITL中断点（status=paused）
6. 提交审批决策（POST /api/v1/workflows/{id}/resume）
7. 等待工作流完成（status=completed）
8. 验证输出结果

**预期结果**：

- 所有API响应200/201
- 工作流状态流转正确：pending → running → paused → running → completed
- 输出包含：算法推荐、代码生成、性能分析

---

### 场景2: LangServe流式传输测试（优先级：P0）

**测试流程**：

```
建立SSE连接 → 实时接收Agent输出 → 验证事件格式 → 连接正常关闭
```

**测试文件**: `tests/e2e/test_langserve_streaming.py`

**测试步骤**：

1. 通过LangServe端点创建工作流（POST /bmad-workflow/invoke）
2. 建立SSE流连接（GET /bmad-workflow/stream）
3. 接收并解析Agent输出事件
4. 验证事件类型（on_chain_start, on_chain_stream, on_chain_end）
5. 验证输出结构和内容
6. 确认连接正常关闭

**预期结果**：

- SSE连接成功建立
- 接收到完整的事件流
- 事件格式符合LangServe规范
- 无连接超时或异常断开

---

### 场景3: HITL人机交互完整流程（优先级：P0）

**测试流程**：

```
创建工作流 → P1审批点 → 批准 → P2.5审批点 → 修改参数 → 完成
```

**测试文件**: `tests/e2e/test_hitl_workflow.py`

**测试步骤**：

1. 创建包含HITL的工作流
2. 等待P1审批点（Phase 1算法推荐）
3. 提交批准决策（decision="approve"）
4. 工作流继续执行
5. 等待P2.5审批点（Phase 2.5代码生成）
6. 提交修改决策（decision="modify", modified_data={...}）
7. 工作流应用修改并完成
8. 验证最终输出包含修改后的内容

**预期结果**：

- 工作流在正确的Phase暂停
- 审批决策正确传递到Agent
- 修改的参数正确应用
- 人工反馈记录在数据库中

---

### 场景4: 并发工作流测试（优先级：P1）

**测试流程**：

```
同时创建10个工作流 → 验证隔离性 → 验证性能
```

**测试文件**: `tests/e2e/test_concurrent_workflows.py`

**测试步骤**：

1. 使用asyncio并发创建10个工作流
2. 每个工作流使用不同的问题描述
3. 同时监控所有工作流状态
4. 验证每个工作流的thread_id唯一
5. 验证checkpoint数据不会混淆
6. 测量平均响应时间

**预期结果**：

- 所有工作流成功创建
- 无数据混淆或覆盖
- 平均响应时间 < 3秒
- 无死锁或资源竞争

---

### 场景5: 异常恢复测试（优先级：P1）

**测试流程**：

```
模拟LLM失败 → 验证错误处理 → 重试机制
```

**测试文件**: `tests/e2e/test_error_handling.py`

**测试步骤**：

1. 配置Mock LLM返回错误
2. 创建工作流
3. 验证工作流状态变为failed
4. 验证error_message字段包含错误详情
5. 测试重试机制（如已实现）
6. 验证checkpoint能够从失败点恢复

**预期结果**：

- 错误正确捕获和记录
- 用户收到友好的错误提示
- 不会导致系统崩溃
- Checkpoint数据保持一致性

---

## 2. 测试数据集

### 简单问题（预期<10秒）

```python
{
    "problem_description": "给定数组 [3, 1, 4, 1, 5, 9]，找出最大值",
    "domain": "算法基础",
    "constraints": {},
    "expected_algorithm": "Linear Search",
    "expected_complexity": "O(n)"
}
```

### 中等问题（预期<60秒）

```python
{
    "problem_description": "优化物流配送路径，有10个配送点，需要最小化总行驶距离",
    "domain": "物流优化",
    "constraints": {
        "vehicle_capacity": 100,
        "time_windows": [(8, 18)] * 10,
        "max_distance": 200
    },
    "expected_algorithm": "VRP (Vehicle Routing Problem)",
    "expected_complexity": "NP-Hard"
}
```

### 复杂问题（预期<5分钟）

```python
{
    "problem_description": """
    生产调度优化：3台机器，8个作业，每个作业有不同的处理时间和优先级。
    目标：最小化最大完工时间（makespan）。
    约束：每个作业必须按指定顺序经过多台机器。
    """,
    "domain": "制造业调度",
    "constraints": {
        "machines": 3,
        "jobs": 8,
        "precedence_constraints": True,
        "priorities": [1, 2, 3, 1, 2, 3, 1, 2]
    },
    "expected_algorithm": "Job Shop Scheduling (JSP)",
    "expected_complexity": "NP-Hard"
}
```

---

## 3. 成功标准

### 功能性标准

| 测试项        | 成功标准               | 优先级 |
| ------------- | ---------------------- | ------ |
| API端点可用性 | 所有端点返回正确状态码 | P0     |
| 工作流创建    | 100%成功率             | P0     |
| HITL审批      | 正确暂停和恢复         | P0     |
| 输出质量      | 包含算法、代码、分析   | P0     |
| 并发处理      | 10个并发无错误         | P1     |
| 错误处理      | 优雅降级，无崩溃       | P1     |

### 性能标准

| 指标               | 目标值  | 测量方法         |
| ------------------ | ------- | ---------------- |
| API响应时间（p50） | < 200ms | pytest-benchmark |
| API响应时间（p95） | < 1s    | pytest-benchmark |
| API响应时间（p99） | < 3s    | pytest-benchmark |
| 简单问题端到端时间 | < 10s   | 实际测量         |
| 中等问题端到端时间 | < 60s   | 实际测量         |
| 复杂问题端到端时间 | < 300s  | 实际测量         |
| 并发QPS            | > 10    | locust负载测试   |

### 稳定性标准

| 测试项           | 成功标准       | 测试时长  |
| ---------------- | -------------- | --------- |
| 长时间运行       | 4小时无崩溃    | 4小时     |
| 内存泄漏         | 内存增长 < 10% | 1小时     |
| 连接池           | 无连接泄漏     | 1小时     |
| Checkpoint一致性 | 100%可恢复     | 100次测试 |

---

## 4. 测试环境配置

### 依赖服务

```yaml
services:
  - PostgreSQL 16 (Checkpoint存储)
  - Redis 7 (会话缓存)
  - 模拟LLM服务（用于快速测试）
```

### 环境变量

```bash
# 测试环境配置
TEST_DATABASE_URL=postgresql://test:test@localhost:5432/bmad_test
TEST_REDIS_URL=redis://localhost:6379/1
TEST_MODEL_PROVIDER=mock  # 使用mock模型加速测试
TEST_TIMEOUT=300  # 5分钟超时
```

### 测试用户

```python
TEST_USERS = [
    {"email": "test1@example.com", "password": "Test123!@#"},
    {"email": "test2@example.com", "password": "Test456!@#"},
    {"email": "test3@example.com", "password": "Test789!@#"},
]
```

---

## 5. 测试执行计划

### Phase 1: API集成测试（1-2天）

- [x] Task 1.1: 设计测试场景和数据集
- [ ] Task 1.2: 实现测试框架和fixtures
- [ ] Task 1.3: 编写API端点测试
- [ ] Task 1.4: 编写HITL流程测试
- [ ] Task 1.5: 执行测试并记录结果

### Phase 2: 性能和稳定性测试（1天）

- [ ] Task 2.1: 编写并发测试
- [ ] Task 2.2: 编写长时间运行测试
- [ ] Task 2.3: 性能基准测试
- [ ] Task 2.4: 内存和资源监控

### Phase 3: 测试报告（0.5天）

- [ ] Task 3.1: 生成测试报告
- [ ] Task 3.2: 截图和数据可视化
- [ ] Task 3.3: 问题汇总和建议

---

## 6. 风险和限制

### 已知限制

1. **无前端登录界面**：测试将直接使用API Token，跳过浏览器登录
2. **无Playwright配置**：暂时专注于API测试，前端测试使用Vitest
3. **LLM响应不确定性**：使用固定的mock响应确保测试可重复

### 缓解措施

1. 使用Mock LLM服务加速测试并保证一致性
2. 使用独立的测试数据库避免污染生产数据
3. 每次测试前清理数据库状态
4. 使用pytest fixtures管理测试依赖

---

## 7. 测试工具栈

```python
# 测试框架
pytest >= 8.3.5
pytest-asyncio >= 0.21.0
pytest-benchmark >= 4.0.0
pytest-timeout >= 2.2.0

# HTTP客户端
httpx >= 0.27.0  # 支持异步

# Mock工具
pytest-mock >= 3.12.0
responses >= 0.24.0

# 性能测试
locust >= 2.15.0  # 负载测试

# 报告生成
pytest-html >= 4.1.0
allure-pytest >= 2.13.0
```

---

## 附录A: 测试命令速查

```bash
# 运行所有端到端测试
pytest tests/e2e/ -v

# 运行特定场景
pytest tests/e2e/test_api_integration.py -v

# 运行性能测试
pytest tests/e2e/ -v --benchmark-only

# 生成HTML报告
pytest tests/e2e/ -v --html=reports/e2e-report.html

# 运行负载测试
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

---

**创建日期**: 2025-11-07
**创建人**: Dev Agent (James)
**版本**: 1.0
