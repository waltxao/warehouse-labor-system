<template>
  <el-card class="warehouse-card" shadow="hover" @click="emit('click')">
    <div class="warehouse-card__code">{{ warehouse.code }}</div>
    <div v-if="warehouse.name" class="warehouse-card__name">{{ warehouse.name }}</div>
    <div class="warehouse-card__hint">{{ hint }}</div>
  </el-card>
</template>

<script setup lang="ts">
interface Warehouse {
  code: string
  name?: string
}

const props = withDefaults(
  defineProps<{
    warehouse: Warehouse
    hint?: string
  }>(),
  { hint: '点击查看趋势' }
)

const emit = defineEmits<{ (e: 'click'): void }>()
</script>

<style scoped>
.warehouse-card {
  cursor: pointer;
  margin-bottom: 16px;
  transition: transform 0.2s ease;
}
.warehouse-card:hover {
  transform: translateY(-2px);
}
.warehouse-card__code {
  font-size: 20px;
  font-weight: bold;
}
.warehouse-card__name {
  color: #606266;
  font-size: 14px;
  margin-top: 4px;
}
.warehouse-card__hint {
  color: #999;
  font-size: 13px;
  margin-top: 8px;
}
</style>
