import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isDark = ref(false)
  const locale = ref<'zh' | 'en'>('zh')

  function toggleDark() {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  function setLocale(lang: 'zh' | 'en') {
    locale.value = lang
  }

  return { isDark, locale, toggleDark, setLocale }
})
