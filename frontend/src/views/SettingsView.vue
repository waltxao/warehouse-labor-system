<template>
  <div class="page-container">
    <div class="content-card">
      <h3>系统设置</h3>
      <el-form label-width="120px" style="max-width: 480px">
        <el-form-item label="暗色主题">
          <el-switch v-model="isDark" @change="toggleDark" />
        </el-form-item>
        <el-form-item label="界面语言">
          <el-radio-group v-model="lang" @change="changeLocale">
            <el-radio-button value="zh-CN">简体中文</el-radio-button>
            <el-radio-button value="zh-TW">繁體中文</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </div>

    <PageIntro :items="[
      '切换系统语言（简体中文 / 繁体中文）',
      '语言设置自动保存，刷新页面后保持',
      '仅管理员可访问系统设置'
    ]" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUiStore } from '../stores/ui'
import PageIntro from '../components/PageIntro.vue'

const ui = useUiStore()
const { locale } = useI18n()
const isDark = ref(ui.isDark)
const lang = ref(locale.value === 'zh-TW' ? 'zh-TW' : 'zh-CN')

function toggleDark(val: boolean) {
  ui.toggleDark()
  if (ui.isDark !== val) ui.toggleDark()
}

function changeLocale(val: string | number | boolean | undefined) {
  const l = String(val) as 'zh-CN' | 'zh-TW'
  locale.value = l
  ui.setLocale(l)
  localStorage.setItem('app-lang', l)
}
</script>
