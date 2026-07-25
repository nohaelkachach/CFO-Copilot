// src/pages/Chat.tsx
import ChatInterface from '../components/chat/ChatInterface'

function Chat() {
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="bg-gradient-to-r from-slate-900 to-slate-700 rounded-2xl p-8 text-white">
        <p className="text-slate-400 text-sm font-semibold uppercase tracking-widest mb-2">
          Powered by AI
        </p>
        <h1 className="text-3xl font-bold mb-2">AI Financial Assistant</h1>
        <p className="text-slate-300">
          Ask anything about your financial documents in plain language.
          Answers are grounded strictly in your data.
        </p>
      </div>
      <div className="flex-1 min-h-[500px]">
        <ChatInterface />
      </div>
    </div>
  )
}

export default Chat