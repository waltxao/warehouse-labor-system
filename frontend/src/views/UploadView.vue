<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="filter-group">
        <div class="page-title">数据上传</div>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content-card">
      <div class="upload-wrapper">
        <el-upload
          drag
          :auto-upload="false"
          :on-change="onFileChange"
          :on-remove="onFileRemove"
          accept=".xlsx"
          class="upload-dragger"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽 Excel 文件到此处或点击上传</div>
          <template #tip>
            <div class="el-upload__tip">仅支持 .xlsx 格式</div>
          </template>
        </el-upload>

        <div class="upload-options">
          <el-checkbox v-model="forceOverwrite">覆盖已存在的周数据</el-checkbox>
          <el-button type="primary" :loading="loading" @click="doUpload">上传</el-button>
        </div>
      </div>

      <!-- 解析报告：琥珀色说明卡 -->
      <div v-if="parseReport" class="chart-description">
        <div class="desc-title">解析成功：{{ parseReport.iso_week }}</div>
        <div class="desc-content">
          <p><span class="desc-label">仓库：</span>{{ parseReport.warehouses_found?.join(', ') }}</p>
          <p><span class="desc-label">新仓库：</span>{{ parseReport.new_warehouses?.length ? parseReport.new_warehouses.join(', ') : '无' }}</p>
          <p><span class="desc-label">缺失仓库：</span>{{ parseReport.missing_warehouses?.length ? parseReport.missing_warehouses.join(', ') : '无' }}</p>
          <p><span class="desc-label">解析记录：</span>{{ parseReport.records_parsed }}</p>
        </div>
      </div>
    </div>
  </div>
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

<style scoped>
.page-container {
  padding: 20px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(30, 58, 138, 0.08);
  border: 1px solid #DBEAFE;
}

.filter-group {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1E3A8A;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(30, 58, 138, 0.08);
  border: 1px solid #DBEAFE;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.content-card:hover {
  box-shadow: 0 8px 24px rgba(30, 58, 138, 0.16);
}

.upload-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-dragger {
  width: 100%;
  max-width: 640px;
}

.upload-dragger :deep(.el-upload-dragger) {
  border: 2px dashed #93C5FD;
  border-radius: 12px;
  background: #F8FAFC;
  transition: all 200ms ease;
  padding: 48px 20px;
}
.upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: #1E40AF;
  background: #EFF6FF;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(30, 58, 138, 0.12);
}
.upload-dragger :deep(.el-icon--upload) {
  color: #3B82F6;
  font-size: 52px;
  margin-bottom: 8px;
}
.upload-dragger :deep(.el-upload__text) {
  color: #1E3A8A;
  font-size: 15px;
}
.upload-dragger :deep(.el-upload__tip) {
  color: #64748B;
  font-size: 13px;
  margin-top: 8px;
}

.upload-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 640px;
  margin-top: 24px;
}

:deep(.el-checkbox__label) {
  color: #1E3A8A;
  font-size: 14px;
}

:deep(.el-button--primary) {
  background-color: #1E40AF;
  border-color: #1E40AF;
  font-weight: 500;
  transition: all 200ms ease;
}
:deep(.el-button--primary:hover) {
  background-color: #1E3A8A;
  border-color: #1E3A8A;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.25);
}

/* 琥珀色说明卡 */
.chart-description {
  background: #FEF3C7;
  border-radius: 12px;
  padding: 16px 20px;
  margin-top: 24px;
  box-shadow: 0 1px 3px rgba(217, 119, 6, 0.10);
  border-left: 4px solid #D97706;
}

.desc-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E3A8A;
  margin-bottom: 8px;
}

.desc-content {
  font-size: 13px;
  color: #78350F;
  line-height: 1.8;
}

.desc-content p {
  margin: 2px 0;
}

.desc-label {
  font-weight: 600;
  color: #92400E;
}
</style>
