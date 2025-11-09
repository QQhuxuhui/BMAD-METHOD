<template>
  <div class="poc-page">
    <a-page-header
      title="G6 POC测试页面"
      sub-title="验证AntV G6图可视化功能"
      @back="handleBack"
    >
      <template #extra>
        <a-tag color="orange">
          <template #icon>
            <ExperimentOutlined />
          </template>
          实验功能
        </a-tag>
      </template>
    </a-page-header>

    <div class="poc-content">
      <WorkflowGraphPOC />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ExperimentOutlined } from '@ant-design/icons-vue'
import WorkflowGraphPOC from '@/views/WorkflowMonitor/components/WorkflowGraphPOC.vue'

const router = useRouter()

const handleBack = () => {
  router.push('/workflows')
}
</script>

<style scoped lang="scss">
.poc-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;

  .poc-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
  }
}
</style>
