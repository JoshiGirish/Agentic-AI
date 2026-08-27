import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RoleSelector } from '../components/Controls/RoleSelector'
import { StartButton } from '../components/Controls/StartButton'

export function Home() {
  const [topic, setTopic] = useState('')
  const [roleMode, setRoleMode] = useState<'host_guest' | 'skeptic_enthusiast'>('host_guest')
  const [maxTurns, setMaxTurns] = useState(20)
  const navigate = useNavigate()

  const handleStart = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic')
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
      alert('Failed to start conversation. Make sure the server is running.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🎙️ Agentic AI Podcast
          </h1>
          <p className="text-purple-200">
            Watch two AI agents with distinct personalities engage in a podcast-style conversation
          </p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-2">Topic</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a topic (e.g., 'The future of quantum computing')"
              className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
              onKeyDown={(e) => e.key === 'Enter' && handleStart()}
            />
          </div>

          <RoleSelector
            value={roleMode}
            onChange={setRoleMode}
          />

          <div>
            <label className="block text-white font-medium mb-2">
              Max Turns: <span className="text-purple-300">{maxTurns}</span>
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={maxTurns}
              onChange={(e) => setMaxTurns(Number(e.target.value))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-xs text-white/60 mt-1">
              <span>5 turns</span>
              <span>50 turns</span>
            </div>
          </div>

          <StartButton onClick={handleStart} />
        </div>

        <div className="mt-8 pt-6 border-t border-white/20 text-center text-sm text-white/50">
          <p>Powered by LangGraph & FastAPI</p>
        </div>
      </div>
    </div>
  )
}
