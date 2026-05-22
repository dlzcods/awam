import { Header } from './components/Header.tsx'
import { ChatInterface } from './components/ChatInterface.tsx'

function App() {
  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto w-full bg-[#fafafa]">
      <Header />
      <ChatInterface />
    </div>
  )
}

export default App
