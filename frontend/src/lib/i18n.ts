import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import it from '../locales/it.json'
import en from '../locales/en.json'
import de from '../locales/de.json'
import fr from '../locales/fr.json'

export const LANGUAGES = [
  { code: 'it', label: 'Italiano' },
  { code: 'en', label: 'English' },
  { code: 'de', label: 'Deutsch' },
  { code: 'fr', label: 'Français' },
] as const

i18n.use(initReactI18next).init({
  lng: 'it',
  fallbackLng: 'en',
  resources: {
    it: { translation: it },
    en: { translation: en },
    de: { translation: de },
    fr: { translation: fr },
  },
  interpolation: {
    escapeValue: false,
  },
})

export default i18n
