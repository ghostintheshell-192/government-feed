interface ProgressBarProps {
  current: number
  total: number
  label: string
  className?: string
}

export function ProgressBar({ current, total, label, className = '' }: ProgressBarProps) {
  const percent = total > 0 ? Math.round((current / total) * 100) : 0

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="truncate pr-4">{label}</span>
        <span className="shrink-0 tabular-nums">
          {current}/{total}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-primary/20">
        <div
          className="h-full rounded-full bg-primary transition-[width] duration-300 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}
