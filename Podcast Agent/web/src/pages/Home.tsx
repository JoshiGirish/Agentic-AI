import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ServerRail } from '../components/Layout/ServerRail'
import { RoleSelector } from '../components/Controls'

const FEATURED_ROLES = ['host', 'guest', 'skeptic', 'enthusiast']

export function Home() {
  const [topic, setTopic] = useState('')
  const [roleMode, setRoleMode] = useState<'host_guest' | 'skeptic_enthusiast'>('host_guest')
  const [maxTurns, setMaxTurns] = useState(20)
  const navigate = useNavigate()

  const handleStart = async () => {
    if (!topic.trim()) {
      return
    }

    try {
      const response = await fetch('/api/v1/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic.trim(),
          role_mode: roleMode,
          max_turns: maxTurns
        })
      })

      const data = await response.json()
      navigate(`/conversation/${data.conversation_id}`)
    } catch (error) {
      console.error('Failed to start conversation:', error)
    }
  }

  return (
    <div className="min-h-screen flex bg-[#0f1115]">
      <ServerRail />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-[420px]">
          <div className="rounded-2xl bg-[#16191f] border border-[#2a2e38] shadow-2xl overflow-hidden">
            <div className="px-6 pt-6 pb-3 text-center">
              <div className="mx-auto w-16 h-16 rounded-2xl bg-[#e94560]/10 flex items-center justify-center text-4xl mb-3">
                🎙️
              </div>
              <h1 className="text-xl font-semibold text-[#e8ecef]">AI Agent Podcast</h1>
              <p className="text-[#9ca3af] text-sm mt-1.5 leading-relaxed max-w-[320px] mx-auto">
                Two AI agents with distinct personalities chat live in a podcast-style conversation.
              </p>
            </div>

            <div className="px-6 py-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#6b7280] mb-1.5">
                  Topic
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. The future of quantum computing"
                  className="w-full px-3.5 py-2.5 rounded-lg bg-[#0d0f12] border border-[#2a2e38] text-[#e8ecef] placeholder:text-[#6b7280] text-[15px] focus:outline-none focus:border-[#e94560] focus:shadow-[0_0_0_1px_rgba(233,69,96,0.15)] transition-colors"
                  onKeyDown={(e) => e.key === 'Enter' && handleStart()}
                />
              </div>

              <RoleSelector value={roleMode} onChange={setRoleMode} />

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#6b7280] mb-1.5">
                  On air
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {FEATURED_ROLES.map((a) => {
                    return (
                      <span
                        key={a}
                        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs transition-colors"
                      >
                        <span className="w-3 h-3 rounded-full bg-[#e94560]" />
                        <span className="text-[#9ca3af]">{a}</span>
                      </span>
                    )
                  })}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold uppercase tracking-wider text-[#6b7280]">
                    Max turns
                  </label>
                  <span className="text-sm font-medium text-[#e94560]">{maxTurns}</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="50"
                  value={maxTurns}
                  onChange={(e) => setMaxTurns(Number(e.target.value))}
                  className="w-full accent-[#e94560] cursor-pointer"
                />
              </div>
            </div>

            <div className="px-6 pb-5">
              <button
                onClick={handleStart}
                disabled={!topic.trim()}
                className="w-full py-2.5 rounded-xl bg-[#e94560] hover:bg-[#c42c44] active:bg-[#c42c44] disabled:bg-[#e94560]/50 disabled:cursor-not-allowed text-[#e8ecef] font-semibold text-[15px] transition-colors shadow-lg shadow-[#e94560]/10"
              >
                Launch Session
              </button>
              <p className="text-center text-[10px] text-[#6b7280] mt-2.5">
                Powered by LangGraph & FastAPI
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
