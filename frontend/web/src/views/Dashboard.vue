<template>
  <div class="dashboard">
    <a-typography-title :level="2">仪表板</a-typography-title>
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card title="总工作流" :bordered="false">
          <a-statistic
            :value="112893"
            :value-style="{ color: '#3f8600' }"
          >
            <template #prefix>
              <arrow-up-outlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="运行中" :bordered="false">
          <a-statistic :value="93" suffix="/ 100" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="已完成" :bordered="false">
          <a-statistic :value="112800" :value-style="{ color: '#52c41a' }" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="失败" :bordered="false">
          <a-statistic :value="0" :value-style="{ color: '#cf1322' }" />
        </a-card>
      </a-col>
    </a-row>
    <a-divider />
    <a-typography-title :level="4">最近工作流</a-typography-title>
    <a-table :columns="columns" :data-source="data" :pagination="false" />
  </div>
</template>

<script setup lang="ts">
import { ArrowUpOutlined } from '@ant-design/icons-vue'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
]

const data = [
  { id: '1', name: '工作流示例1', status: 'running', createdAt: '2025-11-05 12:00:00' },
  { id: '2', name: '工作流示例2', status: 'completed', createdAt: '2025-11-05 11:30:00' },
  { id: '3', name: '工作流示例3', status: 'running', createdAt: '2025-11-05 11:00:00' },
]
</script>

<style scoped>
.dashboard {
  padding: 24px;
}
</style>
