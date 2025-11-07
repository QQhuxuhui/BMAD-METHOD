<template>
  <a-modal
    :open="visible"
    :title="`${approvalPoint} 审批点 - 人工确认`"
    width="900px"
    :closable="false"
    :maskClosable="false"
    class="approval-modal"
  >
    <template #footer>
      <a-space>
        <a-button @click="handleDecision('rejected')" danger :loading="submitting">
          拒绝
        </a-button>
        <a-button
          @click="handleDecision('approved')"
          type="primary"
          :loading="submitting"
        >
          批准
        </a-button>
        <a-button @click="showModifyModal = true" :loading="submitting">
          修改后批准
        </a-button>
      </a-space>
    </template>

    <a-alert
      message="需要人工审批"
      description="请仔细审查智能体输出的内容，确认是否批准继续执行工作流。"
      type="warning"
      show-icon
      style="margin-bottom: 24px"
    />

    <a-descriptions :column="1" bordered>
      <a-descriptions-item label="审批点">
        <a-tag color="warning">{{ approvalPoint }}</a-tag>
      </a-descriptions-item>
      <a-descriptions-item label="工作流ID">
        {{ workflowId }}
      </a-descriptions-item>
      <a-descriptions-item label="当前阶段">
        {{ currentPhase }}
      </a-descriptions-item>
      <a-descriptions-item label="时间">
        {{ formatDateTime(new Date().toISOString()) }}
      </a-descriptions-item>
    </a-descriptions>

    <a-divider>智能体输出上下文</a-divider>

    <template v-if="approvalContext">
      <a-collapse v-model:activeKey="activeCollapseKeys">
        <a-collapse-panel
          v-for="(value, key) in approvalContext"
          :key="String(key)"
          :header="getContextLabel(key)"
        >
          <a-card size="small" class="context-content">
            <pre>{{ formatJSON(value) }}</pre>
          </a-card>
        </a-collapse-panel>
      </a-collapse>
    </template>
    <a-empty v-else description="暂无上下文数据" />

    <a-divider>审批意见（可选）</a-divider>

    <a-form-item label="反馈意见" help="您可以提供审批意见或修改建议">
      <a-textarea
        v-model:value="feedback"
        :rows="4"
        placeholder="请输入审批意见..."
      />
    </a-form-item>
  </a-modal>

  <!-- 修改数据Modal -->
  <a-modal
    v-model:open="showModifyModal"
    title="修改智能体输出"
    width="1000px"
    @ok="handleDecision('modified')"
    :confirm-loading="submitting"
  >
    <a-alert
      message="请修改JSON数据后提交"
      description="修改后的数据将被用于后续工作流执行。请确保JSON格式正确。"
      type="info"
      show-icon
      style="margin-bottom: 16px"
    />

    <a-tabs v-model:activeKey="activeModifyTab">
      <a-tab-pane key="editor" tab="编辑器">
        <a-textarea
          v-model:value="modifiedDataJson"
          :rows="20"
          placeholder="{}"
          style="font-family: monospace"
        />
      </a-tab-pane>
      <a-tab-pane key="preview" tab="预览">
        <a-card size="small">
          <pre class="json-preview">{{ formatModifiedJSON() }}</pre>
        </a-card>
      </a-tab-pane>
    </a-tabs>

    <div class="json-actions" style="margin-top: 12px">
      <a-space>
        <a-button size="small" @click="handleFormatJSON">格式化JSON</a-button>
        <a-button size="small" @click="handleValidateJSON">验证JSON</a-button>
        <a-tag v-if="jsonValidation.isValid" color="success">JSON格式正确</a-tag>
        <a-tag v-else-if="jsonValidation.error" color="error">
          {{ jsonValidation.error }}
        </a-tag>
      </a-space>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { workflowService } from '@/services/workflowService'
import type { ApprovalDecision, ApprovalPoint } from '@/types/workflow'

interface Props {
  visible: boolean
  workflowId: string
  approvalPoint: ApprovalPoint
  approvalContext: any
  currentPhase: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submitted', decision: ApprovalDecision): void
}>()

// State
const feedback = ref('')
const showModifyModal = ref(false)
const modifiedDataJson = ref('')
const submitting = ref(false)
const activeCollapseKeys = ref<string[]>([])
const activeModifyTab = ref('editor')
const jsonValidation = ref<{ isValid: boolean; error?: string }>({
  isValid: true,
})

// 初始化修改数据
watch(
  () => props.approvalContext,
  (ctx) => {
    if (ctx) {
      modifiedDataJson.value = JSON.stringify(ctx, null, 2)
      // 默认展开第一个面板
      const keys = Object.keys(ctx)
      if (keys.length > 0 && keys[0]) {
        activeCollapseKeys.value = [keys[0]]
      } else {
        activeCollapseKeys.value = []
      }
    } else {
      activeCollapseKeys.value = []
    }
  },
  { immediate: true },
)

// 格式化时间
const formatDateTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 格式化JSON
const formatJSON = (data: any): string => {
  try {
    return JSON.stringify(data, null, 2)
  } catch (e) {
    return String(data)
  }
}

// 获取上下文标签
const getContextLabel = (key: string | number): string => {
  const keyStr = String(key)
  const labels: Record<string, string> = {
    algorithm_recommendation: '算法推荐',
    constraint_analysis: '约束分析',
    objective_definition: '目标定义',
    domain_validation: '领域验证',
    code_implementation: '代码实现',
    extension_plan: '扩展方案',
    quality_report: '质量报告',
  }
  return labels[keyStr] || keyStr
}

// 格式化修改后的JSON
const formatModifiedJSON = (): string => {
  try {
    const parsed = JSON.parse(modifiedDataJson.value)
    return JSON.stringify(parsed, null, 2)
  } catch (e) {
    return modifiedDataJson.value
  }
}

// 格式化JSON
const handleFormatJSON = () => {
  try {
    const parsed = JSON.parse(modifiedDataJson.value)
    modifiedDataJson.value = JSON.stringify(parsed, null, 2)
    message.success('JSON已格式化')
    jsonValidation.value = { isValid: true }
  } catch (e: any) {
    message.error('JSON格式错误，无法格式化')
    jsonValidation.value = { isValid: false, error: e.message }
  }
}

// 验证JSON
const handleValidateJSON = () => {
  try {
    JSON.parse(modifiedDataJson.value)
    jsonValidation.value = { isValid: true }
    message.success('JSON格式正确')
  } catch (e: any) {
    jsonValidation.value = { isValid: false, error: e.message }
    message.error(`JSON格式错误: ${e.message}`)
  }
}

// 处理决策
const handleDecision = async (decision: ApprovalDecision['decision']) => {
  try {
    submitting.value = true

    const payload: ApprovalDecision = { decision }

    // 添加反馈意见
    if (feedback.value) {
      payload.feedback = feedback.value
    }

    // 如果是修改决策，解析修改后的数据
    if (decision === 'modified') {
      try {
        payload.modified_data = JSON.parse(modifiedDataJson.value)
      } catch (e: any) {
        message.error('JSON格式错误，请检查')
        return
      }
    }

    // 调用API
    await workflowService.resumeWorkflow(props.workflowId, payload)

    message.success('审批已提交')
    emit('submitted', payload)
    emit('update:visible', false)

    // 重置状态
    resetState()
  } catch (error: any) {
    message.error(error.message || '提交失败，请重试')
    console.error('Approval submission failed:', error)
  } finally {
    submitting.value = false
  }
}

// 重置状态
const resetState = () => {
  feedback.value = ''
  showModifyModal.value = false
  modifiedDataJson.value = ''
  jsonValidation.value = { isValid: true }
  activeModifyTab.value = 'editor'
}
</script>

<style scoped lang="scss">
.approval-modal {
  .context-content {
    pre {
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 12px;
      line-height: 1.5;
      max-height: 300px;
      overflow: auto;
      background: #f5f5f5;
      padding: 12px;
      border-radius: 4px;
      margin: 0;
    }
  }

  .json-preview {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
    max-height: 400px;
    overflow: auto;
    background: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
    margin: 0;
  }

  .json-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
</style>
