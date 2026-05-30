import { ThemeToggle } from './ThemeToggle.tsx'

interface HeaderProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function Header({ theme, onToggleTheme }: HeaderProps) {
  return (
    <header className="border-b border-border px-4 py-4">
      <div className="max-w-3xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground leading-tight">
            <span className="bg-gradient-to-r from-brand to-brand/80 bg-clip-text text-transparent">
              AWAM
            </span>
          </h1>
          <p className="text-sm text-muted leading-tight">
            Accessible Wisdom for Law & Advocacy Matters
          </p>
        </div>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </div>
    </header>
  )
}