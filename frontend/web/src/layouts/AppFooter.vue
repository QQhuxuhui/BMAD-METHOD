<template>
  <div class="footer">
    BMAD 监控平台 © {{ currentYear }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.footer {
  padding: 12px 0;
}
</style>
