import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ApprovalModal from '../ApprovalModal.vue'

// Mock workflowService
vi.mock('@/services/workflowService', () => ({
  workflowService: {
    resumeWorkflow: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

// Mock ant-design-vue message
vi.mock('ant-design-vue', async () => {
  const actual: any = await vi.importActual('ant-design-vue')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
    },
  }
})

// Mock dayjs
vi.mock('dayjs', () => {
  const dayjs: any = (date?: any) => ({
    format: () => '2025-01-01 00:00:00',
  })
  dayjs.extend = vi.fn()
  return { default: dayjs }
})

describe('ApprovalModal', () => {
  const defaultProps = {
    visible: true,
    workflowId: 'test-workflow-123',
    approvalPoint: 'P1' as const,
    approvalContext: {
      algorithm_recommendation: { name: 'Genetic Algorithm', score: 0.95 },
    },
    currentPhase: 'P1',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('渲染', () => {
    it('应该正确渲染Modal', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': {
              template:
                '<div class="approval-modal"><slot /><slot name="footer" /></div>',
            },
            'a-alert': { template: '<div class="alert"><slot /></div>' },
            'a-descriptions': { template: '<div><slot /></div>' },
            'a-descriptions-item': { template: '<div><slot /></div>' },
            'a-divider': { template: '<div class="divider"><slot /></div>' },
            'a-collapse': { template: '<div><slot /></div>' },
            'a-collapse-panel': { template: '<div><slot /></div>' },
            'a-card': { template: '<div><slot /></div>' },
            'a-empty': { template: '<div>empty</div>' },
            'a-form-item': { template: '<div><slot /></div>' },
            'a-textarea': { template: '<textarea />' },
            'a-button': { template: '<button><slot /></button>' },
            'a-space': { template: '<div><slot /></div>' },
            'a-tag': { template: '<span><slot /></span>' },
            'a-tabs': { template: '<div><slot /></div>' },
            'a-tab-pane': { template: '<div><slot /></div>' },
          },
        },
      })

      expect(wrapper.find('.approval-modal').exists()).toBe(true)
    })

    it('应该显示工作流ID', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': {
              template:
                '<div><slot /><slot name="footer" /></div>',
            },
            'a-alert': { template: '<div />' },
            'a-descriptions': { template: '<div><slot /></div>' },
            'a-descriptions-item': { template: '<div><slot /></div>' },
            'a-divider': { template: '<div />' },
            'a-collapse': { template: '<div />' },
            'a-empty': { template: '<div />' },
            'a-form-item': { template: '<div><slot /></div>' },
            'a-textarea': { template: '<textarea />' },
            'a-button': { template: '<button><slot /></button>' },
            'a-space': { template: '<div><slot /></div>' },
            'a-tag': { template: '<span><slot /></span>' },
          },
        },
      })

      expect(wrapper.text()).toContain('test-workflow-123')
    })

    it('应该显示3个决策按钮', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': {
              template:
                '<div><slot /><slot name="footer" /></div>',
            },
            'a-alert': { template: '<div />' },
            'a-descriptions': { template: '<div />' },
            'a-descriptions-item': { template: '<div />' },
            'a-divider': { template: '<div />' },
            'a-collapse': { template: '<div />' },
            'a-empty': { template: '<div />' },
            'a-form-item': { template: '<div><slot /></div>' },
            'a-textarea': { template: '<textarea />' },
            'a-button': { template: '<button><slot /></button>' },
            'a-space': { template: '<div><slot /></div>' },
            'a-tag': { template: '<span />' },
          },
        },
      })

      const buttons = wrapper.findAll('button')
      const buttonTexts = buttons.map((b) => b.text())

      expect(buttonTexts).toContain('拒绝')
      expect(buttonTexts).toContain('批准')
      expect(buttonTexts).toContain('修改后批准')
    })
  })

  describe('审批决策', () => {
    it('应该调用resumeWorkflow当点击批准', async () => {
      const { workflowService } = await import('@/services/workflowService')

      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': {
              template:
                '<div><slot /><slot name="footer" /></div>',
            },
            'a-alert': { template: '<div />' },
            'a-descriptions': { template: '<div />' },
            'a-descriptions-item': { template: '<div />' },
            'a-divider': { template: '<div />' },
            'a-collapse': { template: '<div />' },
            'a-empty': { template: '<div />' },
            'a-form-item': { template: '<div><slot /></div>' },
            'a-textarea': { template: '<textarea />' },
            'a-button': {
              template: '<button @click="$attrs.onClick"><slot /></button>',
            },
            'a-space': { template: '<div><slot /></div>' },
            'a-tag': { template: '<span />' },
          },
        },
      })

      // 找到批准按钮并点击
      const buttons = wrapper.findAll('button')
      const approveButton = buttons.find((b) => b.text() === '批准')

      if (approveButton) {
        await approveButton.trigger('click')
        // 由于是异步操作，需要等待
        await new Promise((resolve) => setTimeout(resolve, 100))

        expect(workflowService.resumeWorkflow).toHaveBeenCalledWith(
          'test-workflow-123',
          expect.objectContaining({ decision: 'approved' }),
        )
      }
    })
  })

  describe('事件emit', () => {
    it('应该emit update:visible事件', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': {
              template:
                '<div><slot /><slot name="footer" /></div>',
            },
            'a-alert': { template: '<div />' },
            'a-descriptions': { template: '<div />' },
            'a-descriptions-item': { template: '<div />' },
            'a-divider': { template: '<div />' },
            'a-collapse': { template: '<div />' },
            'a-empty': { template: '<div />' },
            'a-form-item': { template: '<div><slot /></div>' },
            'a-textarea': { template: '<textarea />' },
            'a-button': {
              template: '<button @click="$attrs.onClick"><slot /></button>',
            },
            'a-space': { template: '<div><slot /></div>' },
            'a-tag': { template: '<span />' },
          },
        },
      })

      const buttons = wrapper.findAll('button')
      const approveButton = buttons.find((b) => b.text() === '批准')

      if (approveButton) {
        await approveButton.trigger('click')
        await new Promise((resolve) => setTimeout(resolve, 100))

        expect(wrapper.emitted('update:visible')).toBeTruthy()
      }
    })

    it('应该emit submitted事件', async () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': {
              template:
                '<div><slot /><slot name="footer" /></div>',
            },
            'a-alert': { template: '<div />' },
            'a-descriptions': { template: '<div />' },
            'a-descriptions-item': { template: '<div />' },
            'a-divider': { template: '<div />' },
            'a-collapse': { template: '<div />' },
            'a-empty': { template: '<div />' },
            'a-form-item': { template: '<div><slot /></div>' },
            'a-textarea': { template: '<textarea />' },
            'a-button': {
              template: '<button @click="$attrs.onClick"><slot /></button>',
            },
            'a-space': { template: '<div><slot /></div>' },
            'a-tag': { template: '<span />' },
          },
        },
      })

      const buttons = wrapper.findAll('button')
      const approveButton = buttons.find((b) => b.text() === '批准')

      if (approveButton) {
        await approveButton.trigger('click')
        await new Promise((resolve) => setTimeout(resolve, 100))

        expect(wrapper.emitted('submitted')).toBeTruthy()
      }
    })
  })

  describe('Props验证', () => {
    it('应该接受所有必需的props', () => {
      const wrapper = mount(ApprovalModal, {
        props: defaultProps,
        global: {
          stubs: {
            'a-modal': { template: '<div />' },
            'a-alert': { template: '<div />' },
            'a-descriptions': { template: '<div />' },
            'a-descriptions-item': { template: '<div />' },
            'a-divider': { template: '<div />' },
            'a-collapse': { template: '<div />' },
            'a-empty': { template: '<div />' },
            'a-form-item': { template: '<div />' },
            'a-textarea': { template: '<textarea />' },
            'a-button': { template: '<button />' },
            'a-space': { template: '<div />' },
            'a-tag': { template: '<span />' },
          },
        },
      })

      expect(wrapper.props('visible')).toBe(true)
      expect(wrapper.props('workflowId')).toBe('test-workflow-123')
      expect(wrapper.props('approvalPoint')).toBe('P1')
      expect(wrapper.props('currentPhase')).toBe('P1')
    })
  })
})
