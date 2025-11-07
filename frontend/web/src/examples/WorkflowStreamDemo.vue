<template>
  <div class="workflow-demo">
    <h2>BMAD Workflow Stream Demo</h2>

    <!-- Input Form -->
    <div class="input-form">
      <h3>Workflow Input</h3>

      <div class="form-group">
        <label for="problem">Problem Description:</label>
        <textarea
          id="problem"
          v-model="input.problem_description"
          rows="4"
          placeholder="描述你要解决的优化问题..."
          :disabled="isStreaming"
        />
      </div>

      <div class="form-group">
        <label for="domain">Domain (Optional):</label>
        <input
          id="domain"
          v-model="input.domain"
          type="text"
          placeholder="例如: logistics, scheduling, recommendation"
          :disabled="isStreaming"
        />
      </div>

      <div class="form-group">
        <label>Constraints (Optional):</label>
        <div v-for="(_, index) in input.constraints" :key="index" class="constraint-row">
          <input
            v-model="input.constraints![index]"
            type="text"
            placeholder="输入约束条件..."
            :disabled="isStreaming"
          />
          <button @click="removeConstraint(index)" :disabled="isStreaming">删除</button>
        </div>
        <button @click="addConstraint" :disabled="isStreaming">+ 添加约束</button>
      </div>

      <div class="button-group">
        <button @click="handleStreamWorkflow" :disabled="isStreaming || !isValidInput" class="btn-primary">
          {{ isStreaming ? '执行中...' : '流式执行' }}
        </button>
        <button @click="handleInvokeWorkflow" :disabled="isStreaming || !isValidInput" class="btn-secondary">
          {{ isStreaming ? '执行中...' : '同步执行' }}
        </button>
        <button @click="handleReset" :disabled="isStreaming" class="btn-reset">重置</button>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-box">
      <h3>错误</h3>
      <p>{{ error.message }}</p>
    </div>

    <!-- Events Stream Display -->
    <div v-if="events.length > 0" class="events-box">
      <h3>执行事件流 ({{ events.length }} events)</h3>
      <div class="events-list">
        <div v-for="(event, index) in events" :key="index" class="event-item" :class="`event-${event.event}`">
          <div class="event-header">
            <span class="event-type">{{ event.event }}</span>
            <span class="event-time">{{ formatTime(event.timestamp) }}</span>
          </div>
          <div class="event-data">
            <pre>{{ JSON.stringify(event.data, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Display -->
    <div v-if="result" class="result-box">
      <h3>执行结果</h3>
      <div class="result-content">
        <div class="result-item">
          <strong>Workflow ID:</strong> {{ result.workflow_id }}
        </div>
        <div class="result-item">
          <strong>Status:</strong>
          <span :class="`status-${result.status}`">{{ result.status }}</span>
        </div>
        <div class="result-item">
          <strong>Current Phase:</strong> {{ result.current_phase }}
        </div>
        <div class="result-item">
          <strong>Total Tokens:</strong> {{ result.total_tokens }}
        </div>
        <div class="result-item">
          <strong>Total Cost:</strong> ${{ result.total_cost.toFixed(2) }}
        </div>
        <div v-if="result.output_data" class="result-item">
          <strong>Output Data:</strong>
          <pre>{{ JSON.stringify(result.output_data, null, 2) }}</pre>
        </div>
        <div v-if="result.error_message" class="result-item error">
          <strong>Error Message:</strong> {{ result.error_message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBMADWorkflow, type WorkflowInput } from '@/composables/useBMADWorkflow'

// Use the composable
const { isStreaming, events, result, error, runWorkflowStream, runWorkflowInvoke, reset } = useBMADWorkflow()

// Input form data
const input = ref<WorkflowInput>({
  problem_description: '',
  domain: '',
  constraints: [],
})

// Computed
const isValidInput = computed(() => {
  return input.value.problem_description.trim().length >= 10
})

// Methods
const addConstraint = () => {
  input.value.constraints = input.value.constraints || []
  input.value.constraints.push('')
}

const removeConstraint = (index: number) => {
  input.value.constraints?.splice(index, 1)
}

const handleStreamWorkflow = async () => {
  await runWorkflowStream({
    ...input.value,
    constraints: input.value.constraints?.filter((c) => c.trim() !== '') || [],
  })
}

const handleInvokeWorkflow = async () => {
  await runWorkflowInvoke({
    ...input.value,
    constraints: input.value.constraints?.filter((c) => c.trim() !== '') || [],
  })
}

const handleReset = () => {
  reset()
  input.value = {
    problem_description: '',
    domain: '',
    constraints: [],
  }
}

const formatTime = (timestamp?: string): string => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleTimeString()
}
</script>

<style scoped>
.workflow-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.input-form {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
}

.constraint-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.constraint-row input {
  flex: 1;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-secondary {
  background: #52c41a;
  color: white;
}

.btn-reset {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.error-box {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  color: #cf1322;
}

.events-box {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.events-list {
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  background: white;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  border-left: 4px solid #1890ff;
}

.event-item.event-error {
  border-left-color: #ff4d4f;
}

.event-item.event-workflow_complete {
  border-left-color: #52c41a;
}

.event-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.event-type {
  font-weight: bold;
  color: #1890ff;
}

.event-time {
  color: #999;
  font-size: 12px;
}

.event-data pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.result-box {
  background: #f0f9ff;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #91d5ff;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-item {
  display: flex;
  gap: 10px;
}

.result-item.error {
  color: #cf1322;
}

.status-completed {
  color: #52c41a;
  font-weight: bold;
}

.status-failed {
  color: #ff4d4f;
  font-weight: bold;
}

.status-running {
  color: #1890ff;
  font-weight: bold;
}
</style>
