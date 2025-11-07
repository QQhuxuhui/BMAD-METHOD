# Story 1.7 测试补充实施指南

**状态**: 🚨 阻塞发布 - 必须完成
**预计工作量**: 1-2天
**优先级**: P0 (最高)
**截止时间**: 2天内完成并通知QA重审

---

## 📋 总览

Story 1.7的功能实现质量良好,但完全缺少测试(Tasks 17-19)。根据团队决策(稳健路径),需要补充以下**核心测试**才能发布:

### 必须完成(P0)

- [ ] **Test 1**: useWorkflowStream Composable单元测试
- [ ] **Test 2**: ApprovalModal组件单元测试

### 建议完成(P1,可选)

- [ ] Test 3: WorkflowStatusCard组件测试
- [ ] Test 4: WorkflowHistory组件测试

---

## 🛠️ 环境准备

### 1. 安装测试依赖

```bash
cd frontend/web

# 检查是否已安装Vitest
npm list vitest @vue/test-utils

# 如果未安装,执行以下命令
npm install -D vitest @vue/test-utils @vitest/ui jsdom
npm install -D @testing-library/vue @testing-library/user-event
```

### 2. 配置Vitest

**检查 `vite.config.ts` 是否包含测试配置**:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts', // 可选
  },
});
```

### 3. 创建测试目录结构

```bash
# 创建测试目录
mkdir -p frontend/web/src/composables/__tests__
mkdir -p frontend/web/src/components/workflow/__tests__
mkdir -p frontend/web/src/tests
```

---

## 📝 Test 1: useWorkflowStream Composable单元测试

**文件位置**: `frontend/web/src/composables/__tests__/useWorkflowStream.spec.ts`

**测试目标**: 验证SSE连接、事件解析、错误处理

### 完整测试代码

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { nextTick } from 'vue';
import { useWorkflowStream } from '../useWorkflowStream';
import type { WorkflowEvent } from '@/types/workflow';

// Mock @vueuse/core
vi.mock('@vueuse/core', () => ({
  useEventSource: vi.fn(() => ({
    data: { value: null },
    status: { value: 'CLOSED' },
    error: { value: null },
    close: vi.fn(),
    open: vi.fn(),
  })),
}));

describe('useWorkflowStream', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock localStorage
    global.localStorage = {
      getItem: vi.fn(() => 'mock-token'),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn(),
    };
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('初始化', () => {
    it('应该正确初始化状态', () => {
      const { events, currentPhase, currentAgent, isApprovalRequired } = useWorkflowStream({
        workflowId: 'test-workflow-123',
        autoConnect: false,
      });

      expect(events.value).toEqual([]);
      expect(currentPhase.value).toBe('P0');
      expect(currentAgent.value).toBeNull();
      expect(isApprovalRequired.value).toBe(false);
    });

    it('应该构建正确的SSE URL', () => {
      const { useEventSource } = require('@vueuse/core');

      useWorkflowStream({
        workflowId: 'workflow-456',
        autoConnect: false,
      });

      // 验证useEventSource被正确调用
      expect(useEventSource).toHaveBeenCalled();
      const callArgs = useEventSource.mock.calls[0];
      expect(callArgs[0].value).toContain('workflow-456');
      expect(callArgs[0].value).toContain('token=mock-token');
    });
  });

  describe('事件解析', () => {
    it('应该正确解析workflow_started事件', async () => {
      const mockEventSource = {
        data: { value: null },
        status: { value: 'OPEN' },
        error: { value: null },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      const { events, currentPhase } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      });

      // 模拟接收workflow_started事件
      const testEvent: WorkflowEvent = {
        event: 'workflow_started',
        data: {
          timestamp: '2025-01-01T00:00:00Z',
          workflow_id: 'test-workflow',
        },
      };

      mockEventSource.data.value = JSON.stringify(testEvent);
      await nextTick();

      expect(currentPhase.value).toBe('P0');
      expect(events.value.length).toBeGreaterThan(0);
    });

    it('应该正确解析phase_changed事件', async () => {
      const mockEventSource = {
        data: { value: null },
        status: { value: 'OPEN' },
        error: { value: null },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      const { currentPhase } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      });

      // 模拟phase_changed事件
      const testEvent: WorkflowEvent = {
        event: 'phase_changed',
        data: {
          timestamp: '2025-01-01T00:01:00Z',
          workflow_id: 'test-workflow',
          phase: 'P1',
        },
      };

      mockEventSource.data.value = JSON.stringify(testEvent);
      await nextTick();

      expect(currentPhase.value).toBe('P1');
    });

    it('应该正确解析agent_started事件', async () => {
      const mockEventSource = {
        data: { value: null },
        status: { value: 'OPEN' },
        error: { value: null },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      const { currentAgent, agentExecutions } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      });

      const testEvent: WorkflowEvent = {
        event: 'agent_started',
        data: {
          timestamp: '2025-01-01T00:02:00Z',
          workflow_id: 'test-workflow',
          agent_name: 'Algorithm Expert',
        },
      };

      mockEventSource.data.value = JSON.stringify(testEvent);
      await nextTick();

      expect(currentAgent.value).toBe('Algorithm Expert');
      expect(agentExecutions.value.length).toBeGreaterThan(0);
      expect(agentExecutions.value[0].status).toBe('running');
    });

    it('应该正确解析approval_required事件', async () => {
      const mockCallback = vi.fn();
      const mockEventSource = {
        data: { value: null },
        status: { value: 'OPEN' },
        error: { value: null },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      const { isApprovalRequired, approvalPoint, approvalContext } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
        onApprovalRequired: mockCallback,
      });

      const testEvent: WorkflowEvent = {
        event: 'approval_required',
        data: {
          timestamp: '2025-01-01T00:03:00Z',
          workflow_id: 'test-workflow',
          approval_point: 'P1',
          approval_context: { test: 'data' },
        },
      };

      mockEventSource.data.value = JSON.stringify(testEvent);
      await nextTick();

      expect(isApprovalRequired.value).toBe(true);
      expect(approvalPoint.value).toBe('P1');
      expect(approvalContext.value).toEqual({ test: 'data' });
      expect(mockCallback).toHaveBeenCalledWith({ test: 'data' });
    });
  });

  describe('错误处理', () => {
    it('应该处理JSON解析错误', async () => {
      const mockErrorCallback = vi.fn();
      const mockEventSource = {
        data: { value: null },
        status: { value: 'OPEN' },
        error: { value: null },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      const { events } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
        onError: mockErrorCallback,
      });

      // 发送无效JSON
      mockEventSource.data.value = 'invalid json';
      await nextTick();

      expect(events.value.length).toBe(0); // 不应添加到events
      expect(mockErrorCallback).toHaveBeenCalled();
    });

    it('应该调用onError回调当SSE失败', async () => {
      const mockErrorCallback = vi.fn();
      const mockEventSource = {
        data: { value: null },
        status: { value: 'OPEN' },
        error: { value: 'Connection failed' },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
        onError: mockErrorCallback,
      });

      await nextTick();

      expect(mockErrorCallback).toHaveBeenCalled();
    });
  });

  describe('连接管理', () => {
    it('应该提供connect和disconnect方法', () => {
      const mockEventSource = {
        data: { value: null },
        status: { value: 'CLOSED' },
        error: { value: null },
        close: vi.fn(),
        open: vi.fn(),
      };

      vi.mocked(require('@vueuse/core').useEventSource).mockReturnValue(mockEventSource);

      const { connect, disconnect } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      });

      connect();
      expect(mockEventSource.open).toHaveBeenCalled();

      disconnect();
      expect(mockEventSource.close).toHaveBeenCalled();
    });

    it('应该提供clearEvents方法', () => {
      const { events, clearEvents } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      });

      // 手动添加事件
      events.value.push({
        event: 'workflow_started',
        data: { timestamp: '', workflow_id: '' },
      });

      expect(events.value.length).toBe(1);

      clearEvents();
      expect(events.value.length).toBe(0);
    });
  });
});
```

### 运行测试

```bash
npm run test -- useWorkflowStream.spec.ts
```

**预期结果**: 所有测试通过 ✅

---

## 📝 Test 2: ApprovalModal组件单元测试

**文件位置**: `frontend/web/src/components/workflow/__tests__/ApprovalModal.spec.ts`

**测试目标**: 验证审批界面、3种决策提交、JSON验证

### 完整测试代码

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import ApprovalModal from '../ApprovalModal.vue';
import { message } from 'ant-design-vue';

// Mock workflowService
vi.mock('@/services/workflowService', () => ({
  workflowService: {
    resumeWorkflow: vi.fn(() => Promise.resolve({ data: {} })),
  },
}));

// Mock ant-design-vue message
vi.mock('ant-design-vue', async () => {
  const actual = await vi.importActual('ant-design-vue');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
    },
  };
});

describe('ApprovalModal', () => {
  const defaultProps = {
    visible: true,
    workflowId: 'test-workflow-123',
    approvalPoint: 'P1' as const,
    approvalContext: {
      algorithm_recommendation: { name: 'Genetic Algorithm', score: 0.95 },
    },
    currentPhase: 'P1',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('渲染', () => {
    it('应该正确渲染Modal', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      expect(wrapper.find('.approval-modal').exists()).toBe(true);
      expect(wrapper.text()).toContain('P1 审批点');
    });

    it('应该显示工作流信息', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      expect(wrapper.text()).toContain('test-workflow-123');
      expect(wrapper.text()).toContain('P1');
    });

    it('应该显示审批上下文', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      expect(wrapper.text()).toContain('algorithm_recommendation');
    });

    it('应该显示3个决策按钮', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      const buttons = wrapper.findAll('button');
      const buttonTexts = buttons.map((b) => b.text());

      expect(buttonTexts).toContain('拒绝');
      expect(buttonTexts).toContain('批准');
      expect(buttonTexts).toContain('修改后批准');
    });
  });

  describe('审批决策', () => {
    it('应该提交approved决策', async () => {
      const { workflowService } = await import('@/services/workflowService');
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      // 点击批准按钮
      const approveButton = wrapper.findAll('button').find((b) => b.text() === '批准');
      await approveButton?.trigger('click');
      await nextTick();

      expect(workflowService.resumeWorkflow).toHaveBeenCalledWith('test-workflow-123', expect.objectContaining({ decision: 'approved' }));

      expect(message.success).toHaveBeenCalledWith('审批已提交');
    });

    it('应该提交rejected决策', async () => {
      const { workflowService } = await import('@/services/workflowService');
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      const rejectButton = wrapper.findAll('button').find((b) => b.text() === '拒绝');
      await rejectButton?.trigger('click');
      await nextTick();

      expect(workflowService.resumeWorkflow).toHaveBeenCalledWith('test-workflow-123', expect.objectContaining({ decision: 'rejected' }));
    });

    it('应该包含反馈意见', async () => {
      const { workflowService } = await import('@/services/workflowService');
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      // 输入反馈意见
      const textarea = wrapper.find('textarea');
      await textarea.setValue('测试反馈意见');
      await nextTick();

      // 提交批准
      const approveButton = wrapper.findAll('button').find((b) => b.text() === '批准');
      await approveButton?.trigger('click');
      await nextTick();

      expect(workflowService.resumeWorkflow).toHaveBeenCalledWith(
        'test-workflow-123',
        expect.objectContaining({
          decision: 'approved',
          feedback: '测试反馈意见',
        }),
      );
    });
  });

  describe('修改数据', () => {
    it('应该打开修改Modal', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      const modifyButton = wrapper.findAll('button').find((b) => b.text().includes('修改'));
      await modifyButton?.trigger('click');
      await nextTick();

      // 验证修改Modal是否显示(通过查找相关元素)
      expect(wrapper.text()).toContain('修改智能体输出');
    });

    it('应该验证JSON格式', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      // 打开修改Modal
      const modifyButton = wrapper.findAll('button').find((b) => b.text().includes('修改'));
      await modifyButton?.trigger('click');
      await nextTick();

      // 找到JSON输入框
      const jsonTextarea = wrapper.findAll('textarea').at(1); // 第二个textarea是JSON编辑器
      await jsonTextarea?.setValue('invalid json');
      await nextTick();

      // 点击验证按钮
      const validateButton = wrapper.findAll('button').find((b) => b.text().includes('验证'));
      await validateButton?.trigger('click');
      await nextTick();

      expect(message.error).toHaveBeenCalled();
    });

    it('应该提交修改后的数据', async () => {
      const { workflowService } = await import('@/services/workflowService');
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      // 打开修改Modal
      const modifyButton = wrapper.findAll('button').find((b) => b.text().includes('修改'));
      await modifyButton?.trigger('click');
      await nextTick();

      // 修改JSON数据
      const modifiedData = { test: 'modified data' };
      const jsonTextarea = wrapper.findAll('textarea').at(1);
      await jsonTextarea?.setValue(JSON.stringify(modifiedData));
      await nextTick();

      // 提交修改
      const okButton = wrapper.findAll('button').find((b) => b.text() === '确定');
      await okButton?.trigger('click');
      await nextTick();

      expect(workflowService.resumeWorkflow).toHaveBeenCalledWith(
        'test-workflow-123',
        expect.objectContaining({
          decision: 'modified',
          modified_data: modifiedData,
        }),
      );
    });
  });

  describe('错误处理', () => {
    it('应该处理API错误', async () => {
      const { workflowService } = await import('@/services/workflowService');
      vi.mocked(workflowService.resumeWorkflow).mockRejectedValueOnce(new Error('API Error'));

      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      const approveButton = wrapper.findAll('button').find((b) => b.text() === '批准');
      await approveButton?.trigger('click');
      await nextTick();

      expect(message.error).toHaveBeenCalled();
    });

    it('应该处理JSON格式错误', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      // 打开修改Modal
      const modifyButton = wrapper.findAll('button').find((b) => b.text().includes('修改'));
      await modifyButton?.trigger('click');
      await nextTick();

      // 输入无效JSON
      const jsonTextarea = wrapper.findAll('textarea').at(1);
      await jsonTextarea?.setValue('invalid json');
      await nextTick();

      // 尝试提交
      const okButton = wrapper.findAll('button').find((b) => b.text() === '确定');
      await okButton?.trigger('click');
      await nextTick();

      expect(message.error).toHaveBeenCalledWith('JSON格式错误,请检查');
    });
  });

  describe('事件emit', () => {
    it('应该emit update:visible事件', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      // 提交审批
      const approveButton = wrapper.findAll('button').find((b) => b.text() === '批准');
      await approveButton?.trigger('click');
      await nextTick();

      expect(wrapper.emitted('update:visible')).toBeTruthy();
      expect(wrapper.emitted('update:visible')?.[0]).toEqual([false]);
    });

    it('应该emit submitted事件', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
      });

      const approveButton = wrapper.findAll('button').find((b) => b.text() === '批准');
      await approveButton?.trigger('click');
      await nextTick();

      expect(wrapper.emitted('submitted')).toBeTruthy();
      expect(wrapper.emitted('submitted')?.[0]).toMatchObject([expect.objectContaining({ decision: 'approved' })]);
    });
  });
});
```

### 运行测试

```bash
npm run test -- ApprovalModal.spec.ts
```

**预期结果**: 所有测试通过 ✅

---

## 🎯 测试覆盖率目标

### 核心测试(P0)

- **useWorkflowStream**: 覆盖率 ≥ 80%
  - ✅ 初始化和配置
  - ✅ 8种事件类型解析
  - ✅ 错误处理
  - ✅ 连接管理

- **ApprovalModal**: 覆盖率 ≥ 80%
  - ✅ 3种审批决策
  - ✅ JSON验证和格式化
  - ✅ 错误处理
  - ✅ 事件emit

### 可选测试(P1)

- WorkflowStatusCard: 状态显示
- WorkflowHistory: 数据渲染和导出

---

## ✅ 完成检查清单

完成后请确认:

- [ ] useWorkflowStream.spec.ts 创建完成,所有测试通过
- [ ] ApprovalModal.spec.ts 创建完成,所有测试通过
- [ ] `npm run test` 全部通过
- [ ] 测试覆盖率 ≥ 80% (运行 `npm run test:coverage`)
- [ ] 更新Story 1.7的File List,添加测试文件
- [ ] 通知QA重新审查

---

## 📞 需要帮助?

如果在实施过程中遇到问题:

1. 查看Vitest官方文档: https://vitest.dev
2. 查看@vue/test-utils文档: https://test-utils.vuejs.org
3. 联系QA Agent (Quinn)进行技术支持

---

**预计完成时间**: 1-2天
**重审周期**: 提交后24小时内
**目标**: 质量门从FAIL改为PASS,发布Story 1.7
