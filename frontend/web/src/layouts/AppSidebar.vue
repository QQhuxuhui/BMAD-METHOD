<template>
  <div class="sidebar">
    <div class="logo">
      <h3 style="color: #fff; text-align: center; padding: 16px">BMAD</h3>
    </div>
    <a-menu
      v-model:selectedKeys="selectedKeys"
      theme="dark"
      mode="inline"
      @click="handleMenuClick"
    >
      <a-menu-item key="/dashboard">
        <dashboard-outlined />
        <span>仪表板</span>
      </a-menu-item>
      <a-menu-item key="/workflows">
        <deployment-unit-outlined />
        <span>工作流监控</span>
      </a-menu-item>
      <a-menu-item key="/settings">
        <setting-outlined />
        <span>设置</span>
      </a-menu-item>
    </a-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  DeploymentUnitOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const selectedKeys = ref<string[]>([route.path])

watch(
  () => route.path,
  (newPath) => {
    selectedKeys.value = [newPath]
  }
)

const handleMenuClick = ({ key }: { key: string }) => {
  router.push(key)
}
</script>

<style scoped>
.sidebar {
  height: 100%;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
