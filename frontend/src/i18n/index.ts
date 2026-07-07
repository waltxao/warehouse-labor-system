import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import zhTW from './zh-TW'

const savedLang = localStorage.getItem('app-lang') || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  locale: savedLang,
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': zhCN, 'zh-TW': zhTW },
})

export default i18n
