import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ServerRail } from '../components/Layout/ServerRail'
import { RoleSelector, StartButton } from '../components/Controls'
import { agentProfile } from '../lib/agentConfig'

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
    <div className="min-h-screen flex bg-app">
      <ServerRail />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-[440px]">
          <div className="relative rounded-2xl bg-panel border border-line shadow-2xl shadow-black/40 overflow-hidden">
            {/* Soft accent wash behind the card header */}
            <div className="absolute inset-x-0 top-0 h-36 bg-gradient-to-b from-accent/15 to-transparent pointer-events-none" />

            <div className="relative px-8 pt-9 pb-2 text-center">
              <div className="relative mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-accent/25 to-accent/5 flex items-center justify-center text-4xl ring-1 ring-accent/30 shadow-lg shadow-accent/10">
                🎙️
              </div>
              <h1 className="mt-4 text-[22px] font-bold tracking-tight text-ink">AI Agent Podcast</h1>
              <p className="text-sub text-sm mt-2 leading-relaxed max-w-[340px] mx-auto">
                Two AI agents with distinct personalities chat live in a podcast-style conversation.
              </p>
            </div>

            <div className="relative px-8 py-5 space-y-5">
              <div>
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-muted mb-2">
                  Topic
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. The future of quantum computing"
                  className="w-full px-4 py-2.5 rounded-xl bg-field border border-line text-ink placeholder:text-muted text-[15px] transition-colors"
                  onKeyDown={(e) => e.key === 'Enter' && handleStart()}
                />
              </div>

              <RoleSelector value={roleMode} onChange={setRoleMode} />

              <div>
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-muted mb-2">
                  On air
                </label>
                <div className="flex flex-wrap gap-2">
                  {FEATURED_ROLES.map((role) => {
                    const profile = agentProfile(role)
                    return (
                      <span
                        key={role}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-elevated border border-line"
                        style={{ color: profile.usernameColor }}
                      >
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: profile.usernameColor }} />
                        {profile.label}
                      </span>
                    )
                  })}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                    Max turns
                  </label>
                  <span className="text-sm font-semibold tabular-nums text-accent">{maxTurns}</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="50"
                  value={maxTurns}
                  onChange={(e) => setMaxTurns(Number(e.target.value))}
                  className="w-full cursor-pointer"
                />
              </div>
            </div>

            <div className="relative px-8 pb-7">
              <StartButton onClick={handleStart} disabled={!topic.trim()} />
              <p className="text-center text-[11px] text-muted mt-3">
                Powered by LangGraph &amp; FastAPI
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}