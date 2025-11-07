# Story 1.7 测试补充检查清单

**状态**: 🚨 阻塞发布
**截止时间**: 2天内完成
**负责人**: Dev Team

---

## 📋 快速任务清单

### Day 1: 环境准备和useWorkflowStream测试

#### 上午 (2-3小时)

- [ ] **Task 1.1**: 安装测试依赖

  ```bash
  cd frontend/web
  npm install -D vitest @vue/test-utils @vitest/ui jsdom
  npm install -D @testing-library/vue @testing-library/user-event
  ```

- [ ] **Task 1.2**: 配置vite.config.ts (如果未配置)

  ```typescript
  test: {
    globals: true,
    environment: 'jsdom',
  }
  ```

- [ ] **Task 1.3**: 创建测试目录
  ```bash
  mkdir -p src/composables/__tests__
  mkdir -p src/components/workflow/__tests__
  ```

#### 下午 (3-4小时)

- [ ] **Task 1.4**: 创建useWorkflowStream.spec.ts
  - 参考: `docs/qa/test-implementation-guide-1.7.md`
  - 复制完整测试代码
  - 运行: `npm run test -- useWorkflowStream.spec.ts`
  - 确保所有测试通过 ✅

- [ ] **Task 1.5**: 验证覆盖率
  ```bash
  npm run test:coverage -- useWorkflowStream
  ```

  - 目标: ≥ 80%

---

### Day 2: ApprovalModal测试和验证

#### 上午 (3-4小时)

- [ ] **Task 2.1**: 创建ApprovalModal.spec.ts
  - 参考: `docs/qa/test-implementation-guide-1.7.md`
  - 复制完整测试代码
  - 运行: `npm run test -- ApprovalModal.spec.ts`
  - 确保所有测试通过 ✅

- [ ] **Task 2.2**: 修复任何失败的测试
  - 调试失败原因
  - 调整mock配置
  - 重新运行测试

#### 下午 (2-3小时)

- [ ] **Task 2.3**: 运行完整测试套件

  ```bash
  npm run test
  ```

  - 确保所有测试通过
  - 检查测试覆盖率报告

- [ ] **Task 2.4**: 更新Story文档
  - 在Story 1.7的"File List"中添加:
    - `frontend/web/src/composables/__tests__/useWorkflowStream.spec.ts`
    - `frontend/web/src/components/workflow/__tests__/ApprovalModal.spec.ts`

- [ ] **Task 2.5**: 提交代码并通知QA
  ```bash
  git add .
  git commit -m "test: 添加Story 1.7核心测试(useWorkflowStream + ApprovalModal)"
  git push
  ```

---

## ✅ 完成验证

运行以下命令进行最终验证:

```bash
# 1. 运行所有测试
npm run test

# 2. 生成覆盖率报告
npm run test:coverage

# 3. 构建验证
npm run build
```

**期望结果**:

- ✅ 所有测试通过
- ✅ useWorkflowStream覆盖率 ≥ 80%
- ✅ ApprovalModal覆盖率 ≥ 80%
- ✅ 构建成功,无TypeScript错误

---

## 📞 通知QA重审

完成后请在Story 1.7评论:

```
@Quinn 测试已补充完成,请重新审查:
- ✅ useWorkflowStream.spec.ts (X个测试通过)
- ✅ ApprovalModal.spec.ts (Y个测试通过)
- ✅ 测试覆盖率: Z%
- ✅ 构建成功

请重新进行质量门审查。
```

---

## 🚀 重审后预期

QA将在24小时内:

1. 运行测试验证
2. 检查测试质量和覆盖率
3. 更新质量门决策: FAIL → PASS
4. 批准Story 1.7发布

---

**预计总工作量**: 8-10小时 (2天)
**当前状态**: 等待Dev补充测试
**下一步**: 开始Task 1.1环境准备
