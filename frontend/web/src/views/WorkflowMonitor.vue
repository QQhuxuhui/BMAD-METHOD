<template>
  <div class="workflow-monitor">
    <a-page-header
      title="工作流监控"
      sub-title="实时监控工作流执行状态"
      style="margin-bottom: 24px"
    >
      <template #extra>
        <a-space>
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索工作流"
            style="width: 200px"
            @search="handleSearch"
          />
          <a-select
            v-model:value="statusFilter"
            style="width: 120px"
            @change="handleSearch"
          >
            <a-select-option value="">全部状态</a-select-option>
            <a-select-option value="running">运行中</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="failed">失败</a-select-option>
          </a-select>
          <a-button type="primary" @click="handleRefresh" :loading="loading">
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <!-- 工作流列表 -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="filteredWorkflows"
        :loading="loading"
        row-key="id"
        :pagination="pagination"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-badge :status="getStatusBadge(record.status)" />
            <span>{{ getStatusText(record.status) }}</span>
          </template>

          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleViewDetail(record)">
                查看详情
              </a-button>
              <a-button
                type="link"
                size="small"
                danger
                @click="handleDelete(record.id)"
              >
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 工作流详情Drawer -->
    <a-drawer
      v-model:open="detailDrawerVisible"
      title="工作流详情"
      width="90%"
      :body-style="{ padding: '24px' }"
      @close="handleCloseDetail"
    >
      <a-row :gutter="16">
        <!-- 左侧：状态卡片 -->
        <a-col :span="6">
          <WorkflowStatusCard
            :current-phase="currentPhase"
            :current-agent="currentAgent"
            :is-connected="isConnected"
            :total-agents="8"
            :completed-agents="completedAgentsCount"
          />
        </a-col>

        <!-- 右侧：详细内容 -->
        <a-col :span="18">
          <a-tabs v-model:activeKey="activeTab">
            <a-tab-pane key="topology" tab="拓扑视图">
              <WorkflowTopologyView
                :current-phase="currentPhase"
                :current-agent="currentAgent"
                :agent-executions="agentExecutions"
                :is-approval-required="isApprovalRequired"
                :approval-point="approvalPoint"
              />
            </a-tab-pane>

            <a-tab-pane key="agents" tab="智能体执行">
              <AgentExecutionList :agent-executions="agentExecutions" />
            </a-tab-pane>

            <a-tab-pane key="logs" tab="实时日志">
              <RealTimeLog :events="events" @clear="handleClearLogs" />
            </a-tab-pane>

            <a-tab-pane key="history" tab="执行历史">
              <WorkflowHistory :events="events" />
            </a-tab-pane>
          </a-tabs>
        </a-col>
      </a-row>
    </a-drawer>

    <!-- HITL审批Modal -->
    <ApprovalModal
      v-model:visible="approvalModalVisible"
      :workflow-id="currentWorkflowId"
      :approval-point="approvalPoint || 'P1'"
      :approval-context="approvalContext"
      :current-phase="currentPhase"
      @submitted="handleApprovalSubmitted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, h } from 'vue'
import { message, notification } from 'ant-design-vue'
import { workflowService } from '@/services/workflowService'
import { useWorkflowStream } from '@/composables/useWorkflowStream'
import WorkflowStatusCard from '@/components/workflow/WorkflowStatusCard.vue'
import WorkflowTopologyView from '@/components/workflow/WorkflowTopologyView.vue'
import AgentExecutionList from '@/components/workflow/AgentExecutionList.vue'
import RealTimeLog from '@/components/workflow/RealTimeLog.vue'
import WorkflowHistory from '@/components/workflow/WorkflowHistory.vue'
import ApprovalModal from '@/components/workflow/ApprovalModal.vue'
import type { Workflow } from '@/types/api'

// State
const searchText = ref('')
const statusFilter = ref('')
const loading = ref(false)
const workflows = ref<Workflow[]>([])
const detailDrawerVisible = ref(false)
const currentWorkflowId = ref('')
const activeTab = ref('topology')
const approvalModalVisible = ref(false)
const pollingTimer = ref<number | null>(null)

// 表格列定义
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 200 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '状态', key: 'status', width: 120 },
  { title: '开始时间', dataIndex: 'startTime', key: 'startTime', width: 180 },
  { title: '结束时间', dataIndex: 'endTime', key: 'endTime', width: 180 },
  { title: '操作', key: 'action', width: 200 },
]

// 分页配置
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: (total: number) => `共 ${total} 条`,
})

// SSE Hook（条件性初始化）
const {
  events,
  currentPhase,
  currentAgent,
  isApprovalRequired,
  approvalContext,
  approvalPoint,
  agentExecutions,
  isConnected,
  connect,
  disconnect,
  clearEvents,
  resetApprovalState,
} = useWorkflowStream({
  workflowId: currentWorkflowId.value,
  autoConnect: false,
  onApprovalRequired: () => {
    // 审批通知
    notification.warning({
      message: '需要人工审批',
      description: `工作流 ${currentWorkflowId.value} 在 ${approvalPoint.value} 需要您的审批决策`,
      duration: 0,
      btn: () => {
        return h('a-button', {
          type: 'primary',
          size: 'small',
          onClick: () => {
            approvalModalVisible.value = true
            notification.destroy()
          },
        }, '立即审批')
      },
    })
  },
  onError: (err) => {
    message.error(`连接错误: ${err.message}`)
    startPolling()
  },
  onComplete: () => {
    message.success('工作流执行完成')
    stopPolling()
  },
})

// 过滤后的工作流列表
const filteredWorkflows = computed(() => {
  let result = workflows.value

  // 按状态过滤
  if (statusFilter.value) {
    result = result.filter((w) => w.status === statusFilter.value)
  }

  // 按关键词搜索
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    result = result.filter(
      (w) =>
        w.name.toLowerCase().includes(keyword) || w.id.toLowerCase().includes(keyword),
    )
  }

  // 更新分页总数
  pagination.value.total = result.length

  return result
})

// 已完成智能体数量
const completedAgentsCount = computed(() => {
  return agentExecutions.value.filter((a) => a.status === 'completed').length
})

// 获取状态徽章
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'running':
      return 'processing'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    default:
      return 'default'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    case 'pending':
      return '等待中'
    default:
      return status
  }
}

// 加载工作流列表
const loadWorkflows = async () => {
  loading.value = true
  try {
    const response = await workflowService.getWorkflows()
    workflows.value = response.data
    pagination.value.total = response.data.length
  } catch (error: any) {
    message.error(`加载失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 查看详情
const handleViewDetail = (workflow: Workflow) => {
  currentWorkflowId.value = workflow.id
  detailDrawerVisible.value = true
  activeTab.value = 'topology'

  // 清空之前的事件
  clearEvents()

  // 建立SSE连接
  connect()

  // 如果连接失败，启动轮询兜底
  setTimeout(() => {
    if (!isConnected.value) {
      startPolling()
    }
  }, 3000)
}

// 关闭详情
const handleCloseDetail = () => {
  detailDrawerVisible.value = false
  disconnect()
  stopPolling()
  resetApprovalState()
  currentWorkflowId.value = ''
}

// SSE连接失败时的轮询兜底
const startPolling = () => {
  if (pollingTimer.value) return

  message.info('SSE连接失败，切换到轮询模式')

  pollingTimer.value = window.setInterval(async () => {
    if (!currentWorkflowId.value) return

    try {
      const response = await workflowService.getWorkflowById(currentWorkflowId.value)
      const workflow = response.data

      // 更新工作流状态
      const index = workflows.value.findIndex((w) => w.id === workflow.id)
      if (index !== -1) {
        workflows.value[index] = workflow
      }

      // 如果工作流完成，停止轮询
      if (workflow.status === 'completed' || workflow.status === 'failed') {
        stopPolling()
      }

      // 尝试重新连接SSE
      if (!isConnected.value) {
        connect()
      } else {
        // SSE已恢复，停止轮询
        stopPolling()
      }
    } catch (error) {
      console.error('Polling failed:', error)
    }
  }, 5000) // 每5秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

// 审批提交后处理
const handleApprovalSubmitted = () => {
  approvalModalVisible.value = false
  resetApprovalState()
  message.success('审批已提交，工作流继续执行')
}

// 监听审批需求，自动弹出Modal
watch(isApprovalRequired, (required) => {
  if (required) {
    approvalModalVisible.value = true
  }
})

// 清空日志
const handleClearLogs = () => {
  clearEvents()
  message.success('日志已清空')
}

// 搜索
const handleSearch = () => {
  // 过滤已通过computed实现
}

// 刷新
const handleRefresh = () => {
  loadWorkflows()
}

// 删除工作流
const handleDelete = async (id: string) => {
  try {
    await workflowService.deleteWorkflow(id)
    message.success('删除成功')
    loadWorkflows()
  } catch (error: any) {
    message.error(`删除失败: ${error.message}`)
  }
}

// 生命周期
onMounted(() => {
  loadWorkflows()
})

onUnmounted(() => {
  disconnect()
  stopPolling()
})
</script>

<style scoped lang="scss">
.workflow-monitor {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}
</style>
