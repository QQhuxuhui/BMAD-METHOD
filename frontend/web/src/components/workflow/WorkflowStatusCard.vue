<template>
  <a-card :loading="loading" class="workflow-status-card">
    <template #title>
      <div class="status-header">
        <span>工作流状态</span>
        <a-badge
          :status="statusBadge"
          :text="statusText"
          class="status-badge"
        />
      </div>
    </template>

    <a-space direction="vertical" :size="16" style="width: 100%">
      <!-- 当前阶段 -->
      <div class="status-item">
        <div class="status-label">当前阶段</div>
        <div class="status-value">
          <a-tag :color="phaseColor">{{ currentPhase }}</a-tag>
          <span class="phase-description">{{ phaseDescription }}</span>
        </div>
      </div>

      <!-- 当前执行的智能体 -->
      <div class="status-item">
        <div class="status-label">当前智能体</div>
        <div class="status-value">
          <template v-if="currentAgent">
            <a-tag color="processing">{{ currentAgent }}</a-tag>
            <a-spin size="small" style="margin-left: 8px" />
          </template>
          <span v-else class="text-muted">无</span>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="status-item">
        <div class="status-label">总体进度</div>
        <a-progress
          :percent="progressPercent"
          :status="progressStatus"
          :stroke-color="progressColor"
        />
      </div>

      <!-- 连接状态 -->
      <div class="status-item">
        <div class="status-label">连接状态</div>
        <div class="status-value">
          <a-badge
            :status="isConnected ? 'success' : 'default'"
            :text="isConnected ? '已连接' : '未连接'"
          />
        </div>
      </div>
    </a-space>
  </a-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { WorkflowPhase } from '@/types/workflow'

interface Props {
  currentPhase: WorkflowPhase
  currentAgent: string | null
  isConnected: boolean
  loading?: boolean
  totalAgents?: number
  completedAgents?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  totalAgents: 8,
  completedAgents: 0,
})

// 阶段映射
const phaseMap: Record<WorkflowPhase, { description: string; color: string }> = {
  P0: { description: '初始化', color: 'default' },
  P1: { description: '算法推荐', color: 'blue' },
  P2: { description: '约束分析', color: 'cyan' },
  'P2.5': { description: '代码实现', color: 'purple' },
  P3: { description: '扩展优化', color: 'orange' },
  P4: { description: '质量审查', color: 'green' },
}

// 阶段信息
const phaseColor = computed(() => phaseMap[props.currentPhase]?.color || 'default')
const phaseDescription = computed(
  () => phaseMap[props.currentPhase]?.description || '',
)

// 状态徽章
const statusBadge = computed(() => {
  if (!props.isConnected) return 'default'
  if (props.currentAgent) return 'processing'
  return 'success'
})

const statusText = computed(() => {
  if (!props.isConnected) return '未运行'
  if (props.currentAgent) return '执行中'
  return '等待中'
})

// 进度计算
const progressPercent = computed(() => {
  if (props.totalAgents === 0) return 0
  return Math.round((props.completedAgents / props.totalAgents) * 100)
})

const progressStatus = computed(() => {
  if (progressPercent.value === 100) return 'success'
  if (progressPercent.value > 0) return 'active'
  return 'normal'
})

const progressColor = computed(() => {
  if (progressPercent.value >= 100) return '#52c41a'
  if (progressPercent.value >= 50) return '#1890ff'
  return '#faad14'
})
</script>

<style scoped lang="scss">
.workflow-status-card {
  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .status-badge {
      margin-left: auto;
    }
  }

  .status-item {
    .status-label {
      font-size: 14px;
      color: rgba(0, 0, 0, 0.45);
      margin-bottom: 8px;
    }

    .status-value {
      font-size: 14px;
      display: flex;
      align-items: center;

      .phase-description {
        margin-left: 8px;
        color: rgba(0, 0, 0, 0.65);
      }

      .text-muted {
        color: rgba(0, 0, 0, 0.25);
      }
    }
  }
}
</style>
