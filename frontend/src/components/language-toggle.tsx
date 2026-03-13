import { useTranslation } from 'react-i18next'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LANGUAGES } from '@/lib/i18n'

export function LanguageToggle() {
  const { i18n } = useTranslation()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="inline-flex items-center justify-center rounded-md px-2 py-1.5 text-xs font-semibold text-muted-foreground outline-none hover:text-primary focus-visible:ring-1 focus-visible:ring-ring">
        {i18n.language.toUpperCase()}
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {LANGUAGES.map(({ code, label }) => (
          <DropdownMenuItem
            key={code}
            onClick={() => i18n.changeLanguage(code)}
            className={i18n.language === code ? 'font-semibold bg-accent' : ''}
          >
            {label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
