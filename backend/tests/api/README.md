# Workflow API 测试文档

## 测试概览

本目录包含完整的Workflow API端点测试套件，覆盖所有5个API端点和HITL功能。

### 测试统计

- **总测试数**: 29个
- **通过率**: 100%
- **覆盖的API端点**: 5个
- **测试场景**: 正常流程、错误处理、并发访问、HITL流程

## 测试文件

### test_workflows.py

完整的Workflow API测试套件，包括：

#### 1. CreateWorkflow测试 (4个测试)

- ✅ `test_create_workflow_success` - 成功创建工作流
- ✅ `test_create_workflow_minimal_data` - 最小数据创建
- ✅ `test_create_workflow_missing_required_field` - 缺少必填字段
- ✅ `test_create_workflow_without_auth` - 无认证访问

#### 2. GetWorkflow测试 (4个测试)

- ✅ `test_get_workflow_success` - 成功获取工作流
- ✅ `test_get_workflow_not_found` - 工作流不存在
- ✅ `test_get_workflow_access_denied` - 访问权限被拒绝
- ✅ `test_get_workflow_invalid_uuid` - 无效的UUID格式

#### 3. ListWorkflows测试 (5个测试)

- ✅ `test_list_workflows_empty` - 空列表
- ✅ `test_list_workflows_with_data` - 包含数据的列表
- ✅ `test_list_workflows_with_status_filter` - 状态过滤
- ✅ `test_list_workflows_pagination` - 分页功能
- ✅ `test_list_workflows_max_limit` - 最大限制验证

#### 4. ResumeWorkflow测试 (4个测试)

- ✅ `test_resume_workflow_approved` - 批准恢复
- ✅ `test_resume_workflow_rejected` - 拒绝恢复
- ✅ `test_resume_workflow_not_paused` - 非暂停状态恢复
- ✅ `test_resume_workflow_no_pending_approval` - 无待处理审批

#### 5. CancelWorkflow测试 (3个测试)

- ✅ `test_cancel_workflow_success` - 成功取消
- ✅ `test_cancel_paused_workflow` - 取消暂停的工作流
- ✅ `test_cancel_completed_workflow` - 取消已完成的工作流

#### 6. StreamWorkflow测试 (2个测试)

- ✅ `test_stream_workflow_initial_event` - SSE初始事件
- ✅ `test_stream_workflow_not_found` - 工作流不存在

#### 7. ConcurrentAccess测试 (2个测试)

- ✅ `test_concurrent_workflow_creation` - 并发创建工作流
- ✅ `test_concurrent_workflow_reads` - 并发读取工作流

#### 8. ErrorScenarios测试 (3个测试)

- ✅ `test_invalid_json_body` - 无效JSON
- ✅ `test_invalid_decision_value` - 无效决策值
- ✅ `test_extremely_large_payload` - 超大负载

#### 9. HITLWorkflow测试 (2个测试)

- ✅ `test_complete_hitl_workflow` - 完整HITL流程
- ✅ `test_hitl_workflow_rejection` - HITL拒绝流程

## 运行测试

### 运行所有测试

```bash
pytest tests/api/test_workflows.py -v
```

### 运行特定测试类

```bash
pytest tests/api/test_workflows.py::TestCreateWorkflow -v
```

### 运行特定测试

```bash
pytest tests/api/test_workflows.py::TestCreateWorkflow::test_create_workflow_success -v
```

### 查看测试覆盖率

```bash
pytest tests/api/test_workflows.py --cov=app/api/v1/workflows --cov-report=html
```

## 测试配置

### conftest.py

提供测试fixture和配置：

- `test_db_engine` - 内存SQLite数据库引擎
- `test_db_session` - 测试数据库会话
- `test_user` - 测试用户
- `auth_token` - JWT认证令牌
- `client` - 异步HTTP客户端
- `sample_workflow_data` - 示例工作流数据
- `sample_resume_data` - 示例恢复请求数据

### Mock策略

为了避免PostgreSQL和LangGraph依赖，测试使用以下mock策略：

```python
# Mock PostgreSQL模块
sys.modules['psycopg'] = MagicMock()
sys.modules['psycopg_pool'] = MagicMock()
sys.modules['langgraph.checkpoint.postgres'] = MagicMock()
```

## 测试数据

### 标准测试数据

```python
sample_workflow_data = {
    "problem_description": "优化100辆车的配送路线",
    "domain": "logistics",
    "constraints": ["实时交通", "电动车电池限制"]
}
```

### 最小测试数据

```python
minimal_data = {
    "problem_description": "这是一个简单的优化问题"
}
```

## 已知限制

1. **LangGraph集成**: 测试使用mock，不包含实际的LangGraph工作流执行
2. **SSE流式传输**: 仅测试初始事件，完整流式传输需要集成测试
3. **Database**: 使用SQLite内存数据库，与生产PostgreSQL可能有差异

## 未来改进

- [ ] 添加性能基准测试
- [ ] 添加压力测试
- [ ] 集成实际LangGraph工作流
- [ ] 添加端到端测试
- [ ] 增加代码覆盖率到90%+

## 测试最佳实践

1. **独立性**: 每个测试使用独立的数据库会话
2. **清理**: 使用function级别的fixture确保测试间隔离
3. **并发**: 测试并发场景确保线程安全
4. **错误处理**: 覆盖各种错误场景
5. **文档**: 每个测试都有清晰的docstring说明测试目的
