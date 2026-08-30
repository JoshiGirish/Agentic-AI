import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { StopButton } from '../components/Controls/StopButton'
import { SpeakerBadge } from '../components/Conversation/SpeakerBadge'

export function Conversation() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<{ agent: string; content: string; timestamp: string }[]>([])
  const [status, setStatus] = useState<{ turnCount: number; maxTurns: number; isComplete: boolean } | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (!id) return

    const eventSource = new EventSource(`/api/v1/stream/${id}`)

    eventSource.addEventListener('message', (event) => {
      const data = JSON.parse(event.data)
      setMessages((prev) => {
        if (!data || !data.agent) return prev
        const last = prev[prev.length - 1]
        if (last && last.agent === data.agent) {
          return [...prev.slice(0, -1), { ...last, ...data }]
        }
        return [...prev, data]
      })
    })

    eventSource.addEventListener('token', (event) => {
      const tokenData = JSON.parse(event.data)
      setMessages((prev) => {
        if (prev.length === 0) {
          return [{
            agent: tokenData.agent,
            content: tokenData.token,
            timestamp: new Date().toISOString()
          }]
        }
        
        const lastMessage = prev[prev.length - 1]
        if (lastMessage.agent === tokenData.agent) {
          // Append token to last message from same agent
          const updatedMessages = [...prev]
          updatedMessages[updatedMessages.length - 1] = {
            ...lastMessage,
            content: lastMessage.content + tokenData.token,
            timestamp: new Date().toISOString()
          }
          return updatedMessages
        } else {
          // New message from different agent
          return [...prev, {
            agent: tokenData.agent,
            content: tokenData.token,
            timestamp: new Date().toISOString()
          }]
        }
      })
    })

    eventSource.addEventListener('update', (event) => {
      const data = JSON.parse(event.data)
      setStatus({
        turnCount: data.turn_count,
        maxTurns: data.max_turns,
        isComplete: data.is_complete
      })
    })

    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      setIsConnected(false)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [id])

  useEffect(() => {
    if (id) {
      fetch(`/api/v1/conversation/${id}`)
        .then(res => res.json())
        .then(data => {
          setStatus({
            turnCount: data.turn_count,
            maxTurns: data.max_turns,
            isComplete: data.is_complete
          })
        })
        .catch(console.error)
    }
  }, [id])

  const handleStop = async () => {
    if (id) {
      await fetch(`/api/v1/conversation/${id}`, { method: 'DELETE' })
      navigate('/home')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col">
      <div className="bg-white/10 backdrop-blur-lg border-b border-white/20 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button
            onClick={() => navigate('/home')}
            className="text-white hover:text-purple-300 transition-colors flex items-center gap-2"
          >
            ← Back
          </button>
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${isConnected ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'}`}>
              {isConnected ? '● Live' : '○ Connecting'}
            </div>
            <StopButton onClick={handleStop} disabled={!isConnected && messages.length > 0} />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-white/50 mt-20">
              <div className="animate-pulse text-4xl mb-4">🎙️</div>
              <p>Starting conversation...</p>
              <p className="text-sm mt-2">Waiting for agents to begin...</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="flex gap-4">
                <div className="flex-shrink-0">
                  <SpeakerBadge agent={msg.agent} />
                </div>
                <div className="flex-1">
                  <div className={`p-4 rounded-2xl max-w-[85%] ${msg.agent === 'host' ? 'bg-blue-500/20' : msg.agent === 'guest' ? 'bg-purple-500/20' : msg.agent === 'skeptic' ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                    <p className="text-white whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-xs text-white/40 mt-2 text-right">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {status && (
        <div className="bg-white/5 backdrop-blur-lg border-t border-white/20 p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="text-white/70">
              Turn {status.turnCount} of {status.maxTurns}
            </div>
            {status.isComplete && (
              <span className="text-green-400 font-medium">Conversation complete</span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
