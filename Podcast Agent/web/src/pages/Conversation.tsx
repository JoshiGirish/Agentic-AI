import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ServerRail } from '../components/Layout/ServerRail'
import { ChannelSidebar } from '../components/Layout/ChannelSidebar'
import { SpeakerBadge } from '../components/Conversation/SpeakerBadge'
import { StopButton } from '../components/Controls'
import { agentProfile } from '../lib/agentConfig'

interface ChatMessage {
  agent: string
  content: string
  timestamp: string
}

// Roles that can appear in a conversation.
const ALL_AGENTS = ['host', 'guest', 'skeptic', 'enthusiast']

export function Conversation() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<{ turnCount: number; maxTurns: number; isComplete: boolean } | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [streamingAgent, setStreamingAgent] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (!id) return

    const eventSource = new EventSource(`/api/v1/stream/${id}`)
    setIsConnected(true)

    eventSource.addEventListener('message', (event) => {
      const data = JSON.parse(event.data)
      setStreamingAgent(null)
      setMessages((prev) => {
        if (!data || !data.agent) return prev
        // The current speaker's response is already rendered token-by-token via
        // 'token' events. This trailing 'message' event carries the same full
        // response, so reconcile it with the last rendered bubble instead of
        // appending a duplicate/triplicate.
        const last = prev[prev.length - 1]
        if (last && last.agent === data.agent) {
          return [...prev.slice(0, -1), { ...last, ...data }]
        }
        return [...prev, data]
      })
    })

    eventSource.addEventListener('token', (event) => {
      const tokenData = JSON.parse(event.data)
      setStreamingAgent(tokenData.agent)
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
      if (data.is_complete) setStreamingAgent(null)
    })

    eventSource.addEventListener('complete', () => {
      setStreamingAgent(null)
      setIsConnected(false)
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

  const activeAgents = messages.length > 0
    ? Array.from(new Set(messages.map(m => m.agent)))
    : ALL_AGENTS

  // Determine which messages should render an avatar/name header.
  const showHeader = (index: number) =>
    index === 0 || messages[index - 1].agent !== messages[index].agent

  const turnCount = status?.turnCount ?? 0
  const maxTurns = status?.maxTurns ?? 20
  const isComplete = status?.isComplete ?? false

  return (
    <div className="h-screen flex overflow-hidden bg-app">
      <ServerRail />
      <ChannelSidebar
        agents={activeAgents}
        turnCount={turnCount}
        maxTurns={maxTurns}
        isComplete={isComplete}
        streamingAgent={streamingAgent}
      />

      {/* Chat column */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Channel header */}
        <header className="h-12 px-4 flex items-center gap-2 border-b border-line bg-panel">
          <span className="text-sub">#</span>
          <span className="text-ink font-semibold text-[15px]">podcast-live</span>
          <span className="text-[13px] text-muted ml-1 truncate">
            {isComplete ? 'Conversation complete' : isConnected ? 'Streaming live — agents are conversing' : 'Disconnected'}
          </span>
          <div className="flex-1" />
          {/* Live pill */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium ${isConnected ? 'bg-online/15 text-online' : 'bg-warning/15 text-warning'}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-online animate-pulse' : 'bg-warning'}`} />
            {isConnected ? 'Live' : 'Offline'}
          </div>
          <StopButton onClick={handleStop} disabled={!isConnected && messages.length > 0} />
        </header>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-4 pt-8">
            {/* Start-of-channel banner */}
            <div className="flex items-center gap-4 mb-6 pb-5 border-b border-line">
              <div className="w-14 h-14 rounded-full bg-accent/15 ring-1 ring-accent/25 flex items-center justify-center text-2xl">🎙</div>
              <div>
                <h1 className="text-xl font-extrabold text-ink tracking-tight">Welcome to #podcast-live</h1>
                <p className="text-sm text-sub mt-0.5">
                  This is the start of the <span className="text-ink">AI agent podcast</span>. Sit back and watch the conversation unfold.
                </p>
              </div>
            </div>

            {messages.length === 0 ? (
              <div className="text-center text-sub mt-16">
                <div className="animate-pulse text-5xl mb-4">🎙️</div>
                <p className="text-lg font-semibold text-ink">Connecting to the studio…</p>
                <p className="text-sm mt-1 text-muted">Waiting for the agents to begin their conversation</p>
              </div>
            ) : (
              <div className="space-y-0.5">
                {messages.map((msg, index) => {
                  const isStreaming = streamingAgent === msg.agent && index === messages.length - 1
                  const p = agentProfile(msg.agent)
                  const time = new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  return (
                    <div
                      key={index}
                      className={`group flex items-start gap-4 px-2 py-1 rounded-md transition-colors msg-enter ${isStreaming ? 'bg-hovered/40' : 'hover:bg-hovered/60'}`}
                    >
                      {showHeader(index) ? (
                        <>
                          <div className="mt-0.5 w-10 shrink-0"><SpeakerBadge agent={msg.agent} /></div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-baseline gap-2 flex-wrap">
                              <span className="text-[15px] font-semibold hover:underline cursor-pointer" style={{ color: p.usernameColor }}>
                                {p.label}
                              </span>
                              {isStreaming && <span className="inline-flex items-center gap-1 text-[12px] font-semibold text-warning">
                                <span className="w-1.5 h-1.5 rounded-full bg-warning animate-pulse" />TYPING…
                              </span>}
                              <span className="text-[11px] text-muted/70">{time}</span>
                            </div>
                            <div className={`pt-1 text-[15px] text-ink/90 whitespace-pre-wrap leading-relaxed break-words ${isStreaming ? 'streaming-caret' : ''}`}>
                              {msg.content}
                            </div>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="w-10 shrink-0" />
                          <div className="min-w-0 flex-1">
                            <div className="pt-1 text-[15px] text-ink/90 whitespace-pre-wrap leading-relaxed break-words">
                              {msg.content}
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Message input bar (visual) */}
        <footer className="px-4 pt-3 pb-4 bg-panel">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-field border border-line transition-colors focus-within:border-accent/60">
              <span className="text-base text-muted" title="Attach">➕</span>
              <span className="flex-1 text-ink text-[15px] truncate">
                {isComplete
                  ? 'Conversation complete — head back Home to start a new one.'
                  : streamingAgent
                    ? <span className="text-warning font-medium">{agentProfile(streamingAgent!).label} is speaking…</span>
                    : <span className="text-muted">{isConnected ? 'Agents are taking the mic…' : 'Connecting…'}</span>}
              </span>
              <span
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium tabular-nums ${
                  isConnected ? 'bg-accent text-white' : 'bg-elevated text-muted'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-white animate-pulse' : 'bg-muted'}`} />
                Turn {Math.min(turnCount + (isConnected && !isComplete ? 1 : 0), maxTurns)}/{maxTurns}
              </span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}