import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import it from '../locales/it.json'
import en from '../locales/en.json'
import de from '../locales/de.json'

i18n.use(initReactI18next).init({
  lng: 'it',
  fallbackLng: 'en',
  resources: {
    it: { translation: it },
    en: { translation: en },
    de: { translation: de },
  },
  interpolation: {
    escapeValue: false,
  },
})

export default i18n
