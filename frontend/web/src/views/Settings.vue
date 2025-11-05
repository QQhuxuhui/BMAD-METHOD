<template>
  <div class="settings">
    <a-typography-title :level="2">设置</a-typography-title>
    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane key="general" tab="通用设置">
        <a-form :model="formState" layout="vertical">
          <a-form-item label="系统名称">
            <a-input v-model:value="formState.systemName" />
          </a-form-item>
          <a-form-item label="语言">
            <a-select v-model:value="formState.language" style="width: 200px">
              <a-select-option value="zh-CN">简体中文</a-select-option>
              <a-select-option value="en-US">English</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item>
            <a-button type="primary">保存</a-button>
          </a-form-item>
        </a-form>
      </a-tab-pane>
      <a-tab-pane key="notification" tab="通知设置">
        <p>通知设置内容</p>
      </a-tab-pane>
      <a-tab-pane key="security" tab="安全设置">
        <p>安全设置内容</p>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const activeKey = ref('general')

const formState = reactive({
  systemName: 'BMAD 监控平台',
  language: 'zh-CN',
})
</script>

<style scoped>
.settings {
  padding: 24px;
}
</style>
