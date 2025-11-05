# Coding Standards

**Critical Rules:**

- Type Sharing: TypeScript类型通过OpenAPI生成
- API Calls: 必须通过service层，禁止直接axios
- State Updates: 使用Pinia actions，禁止直接修改state

**Naming Conventions:**

| Element    | Frontend   | Backend    |
| ---------- | ---------- | ---------- |
| Components | PascalCase | -          |
| Functions  | camelCase  | snake_case |
| API Routes | -          | kebab-case |
| Tables     | -          | snake_case |

---
