import { useTheme } from './lib/use-theme.ts'
import { Header } from './components/Header.tsx'
import { ChatInterface } from './components/ChatInterface.tsx'

function App() {
  const { theme, toggle } = useTheme()

  return (
    <div className="flex flex-col h-dvh w-full bg-background overflow-hidden">
      <Header theme={theme} onToggleTheme={toggle} />
      <ChatInterface />
    </div>
  )
}

export default App