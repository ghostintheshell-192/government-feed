import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'

const LANGUAGES = ['it', 'en', 'de'] as const

export function LanguageToggle() {
  const { i18n } = useTranslation()

  const currentIndex = LANGUAGES.indexOf(i18n.language as (typeof LANGUAGES)[number])
  const nextIndex = (currentIndex + 1) % LANGUAGES.length
  const nextLang = LANGUAGES[nextIndex >= 0 ? nextIndex : 1]

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => i18n.changeLanguage(nextLang)}
      aria-label={`Switch to ${nextLang.toUpperCase()}`}
      className="w-auto px-2 text-xs font-semibold text-muted-foreground hover:text-primary"
    >
      {i18n.language.toUpperCase()}
    </Button>
  )
}
