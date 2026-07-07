import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isDark = ref(false)
  const locale = ref<'zh-CN' | 'zh-TW'>('zh-CN')

  function toggleDark() {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  function setLocale(lang: 'zh-CN' | 'zh-TW') {
    locale.value = lang
  }

  return { isDark, locale, toggleDark, setLocale }
})
