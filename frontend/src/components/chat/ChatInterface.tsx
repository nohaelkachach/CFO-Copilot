// src/components/chat/ChatInterface.tsx
import { useState } from 'react'
import LoadingSpinner from '../ui/LoadingSpinner'
import { askQuestion } from '../../services/api'

type Message = {
  role: "user" | "assistant"
  content: string
  sources?: string[]
}

function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSend() {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: "user", content: input }
    setMessages(prev => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await askQuestion(input)
      const { answer, sources } = response.data

      setMessages(prev => [...prev, {
        role: "assistant",
        content: answer,
        sources
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I couldn't process your question. Please try again."
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-gray-200">

      {/* Message history */}
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-12">
            <p className="text-lg mb-2">Ask anything about your finances</p>
            <p className="text-sm">Example: "What were my top expenses last month?"</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] rounded-xl px-4 py-3 text-sm ${
              msg.role === "user"
                ? "bg-slate-900 text-white"
                : "bg-gray-100 text-gray-800"
            }`}>
              <p>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <p className="text-xs mt-2 opacity-60">
                  Sources: {msg.sources.join(", ")}
                </p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-xl px-4 py-3">
              <LoadingSpinner message="Analyzing your documents..." />
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
          placeholder="Ask about your finances..."
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatInterface