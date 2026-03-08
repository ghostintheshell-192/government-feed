import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'

export function LanguageToggle() {
  const { i18n } = useTranslation()
  const isItalian = i18n.language === 'it'

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => i18n.changeLanguage(isItalian ? 'en' : 'it')}
      aria-label={isItalian ? 'Switch to English' : 'Passa all\'italiano'}
      className="w-auto px-2 text-xs font-semibold text-muted-foreground hover:text-primary"
    >
      {isItalian ? 'EN' : 'IT'}
    </Button>
  )
}
