# 15. Coding Standards

## 15.1 关键规则

1. **类型共享**: 始终在`shared/types/`定义类型
2. **API调用**: 前端必须通过service层
3. **环境变量**: 通过config对象访问
4. **错误处理**: 使用标准错误处理器
5. **状态管理**: 使用Pinia actions修改state

## 15.2 命名约定

| 元素        | 前端                 | 后端       | 示例                  |
| ----------- | -------------------- | ---------- | --------------------- |
| 组件        | PascalCase           | -          | `WorkflowMonitor.vue` |
| Composables | camelCase with 'use' | -          | `useWorkflow.ts`      |
| API路由     | -                    | kebab-case | `/api/user-profile`   |
| 数据库表    | -                    | snake_case | `agent_executions`    |

---
