<template>
  <el-card>
    <el-upload drag :auto-upload="false" :on-change="onFileChange" :on-remove="onFileRemove" accept=".xlsx">
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽 Excel 文件到此处或点击上传</div>
      <template #tip>
        <div class="el-upload__tip">仅支持 .xlsx 格式</div>
      </template>
    </el-upload>

    <div style="margin-top: 16px">
      <el-checkbox v-model="forceOverwrite">覆盖已存在的周数据</el-checkbox>
    </div>
    <el-button type="primary" style="margin-top: 16px" :loading="loading" @click="doUpload">
      上传
    </el-button>

    <el-alert
      v-if="parseReport"
      type="success"
      :title="`解析成功：${parseReport.iso_week}`"
      style="margin-top: 16px"
      :closable="false"
    >
      <div>仓库：{{ parseReport.warehouses_found?.join(', ') }}</div>
      <div>新仓库：{{ parseReport.new_warehouses?.length ? parseReport.new_warehouses.join(', ') : '无' }}</div>
      <div>缺失仓库：{{ parseReport.missing_warehouses?.length ? parseReport.missing_warehouses.join(', ') : '无' }}</div>
      <div>解析记录：{{ parseReport.records_parsed }}</div>
    </el-alert>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { uploadExcel } from '../api/upload'
import { ElMessage } from 'element-plus'

const file = ref<File | null>(null)
const forceOverwrite = ref(false)
const loading = ref(false)
const parseReport = ref<any>(null)

function onFileChange(uploadFile: any) {
  file.value = uploadFile.raw
}

function onFileRemove() {
  file.value = null
}

async function doUpload() {
  if (!file.value) {
    ElMessage.warning('请选择文件')
    return
  }
  loading.value = true
  try {
    const resp: any = await uploadExcel(file.value, forceOverwrite.value)
    parseReport.value = resp.data
    ElMessage.success('上传成功')
  } catch (err: any) {
    if (err?.code === 409) {
      ElMessage.warning(`周次 ${err?.data?.iso_week} 已存在，请勾选覆盖`)
    } else {
      ElMessage.error(err?.message || '上传失败')
    }
  } finally {
    loading.value = false
  }
}
</script>
