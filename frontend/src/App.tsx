import { ChatProvider } from './context/ChatContext'
import { DocumentsProvider } from './context/DocumentsContext'
import { Sidebar } from './components/Sidebar/Sidebar'
import { ChatWindow } from './components/Chat/ChatWindow'

export default function App() {
  return (
    <DocumentsProvider>
      <ChatProvider>
        <div className="flex h-screen w-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-hidden">
            <ChatWindow />
          </main>
        </div>
      </ChatProvider>
    </DocumentsProvider>
  )
}
