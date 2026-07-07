<template>
  <div class="page-intro">
    <div class="intro-title">
      <svg class="intro-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;flex-shrink:0;">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4"/>
        <path d="M12 8h.01"/>
      </svg>
      <span>页面使用说明</span>
    </div>
    <ul class="intro-list">
      <li v-for="(item, idx) in items" :key="idx">{{ item }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: string[]
}>()
</script>

<style scoped>
.page-intro {
  background: #F5F5F7;
  border-radius: 16px;
  padding: 20px 24px;
  margin-top: 24px;
}
.intro-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #6E6E73;
  margin-bottom: 12px;
}
.intro-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.intro-list li {
  font-size: 13px;
  color: #6E6E73;
  line-height: 1.8;
  padding-left: 16px;
  position: relative;
}
.intro-list li::before {
  content: "·";
  position: absolute;
  left: 4px;
  font-weight: bold;
}
</style>
