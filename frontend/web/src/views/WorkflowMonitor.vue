<template>
  <div class="workflow-monitor">
    <a-typography-title :level="2">工作流监控</a-typography-title>
    <a-space style="margin-bottom: 16px">
      <a-input-search
        v-model:value="searchText"
        placeholder="搜索工作流"
        style="width: 200px"
      />
      <a-select v-model:value="statusFilter" style="width: 120px">
        <a-select-option value="">全部状态</a-select-option>
        <a-select-option value="running">运行中</a-select-option>
        <a-select-option value="completed">已完成</a-select-option>
        <a-select-option value="failed">失败</a-select-option>
      </a-select>
      <a-button type="primary">刷新</a-button>
    </a-space>
    <a-table :columns="columns" :data-source="workflows" :loading="loading" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const searchText = ref('')
const statusFilter = ref('')
const loading = ref(false)

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '开始时间', dataIndex: 'startTime', key: 'startTime' },
  { title: '结束时间', dataIndex: 'endTime', key: 'endTime' },
  { title: '操作', key: 'action', slots: { customRender: 'action' } },
]

const workflows = ref([
  {
    id: '1',
    name: '工作流示例1',
    status: 'running',
    startTime: '2025-11-05 12:00:00',
    endTime: '-',
  },
  {
    id: '2',
    name: '工作流示例2',
    status: 'completed',
    startTime: '2025-11-05 11:30:00',
    endTime: '2025-11-05 11:45:00',
  },
])
</script>

<style scoped>
.workflow-monitor {
  padding: 24px;
}
</style>
