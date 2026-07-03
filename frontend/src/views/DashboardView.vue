<template>
  <div>
    <el-row :gutter="16">
      <el-col v-for="w in warehouses" :key="w.code" :xs="24" :sm="12" :md="8" :lg="6">
        <WarehouseCard :warehouse="w" @click="goToTrend(w.code)" />
      </el-col>
    </el-row>
    <el-empty v-if="!loading && warehouses.length === 0" description="暂无仓库数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import WarehouseCard from '../components/WarehouseCard.vue'
import client from '../api/client'

const router = useRouter()
const warehouses = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const resp: any = await client.get('/warehouses')
    warehouses.value = resp.data
  } catch {
    /* 忽略 */
  } finally {
    loading.value = false
  }
})

function goToTrend(code: string) {
  router.push(`/trends/${code}`)
}
</script>
