import { agentProfile, roleIcon } from '../../lib/agentConfig'

interface ChannelSidebarProps {
  agents: string[]          // roles currently in the conversation
  turnCount: number
  maxTurns: number
  isComplete: boolean
  streamingAgent: string | null
}

// Discord-style channel / member sidebar (second column).
export function ChannelSidebar({ agents, turnCount, maxTurns, isComplete, streamingAgent }: ChannelSidebarProps) {
  return (
    <aside className="w-64 flex-shrink-0 bg-[#2b2d31] flex flex-col overflow-hidden select-none">
      {/* Guild header */}
      <div className="h-12 px-4 flex items-center justify-between border-b border-[#26292c] shadow-sm">
        <span className="text-white/90 font-semibold text-[15px]">AI Podcast</span>
        <span className="w-5 h-5 rounded-full bg-[#5865f2] text-white text-[11px] flex items-center justify-center">🎙</span>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-4">
        {/* Channel list */}
        <div className="space-y-1">
          <div className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-[#949ba4]">Channels</div>
          <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md bg-[#404249]/80 text-white text-[15px] font-semibold">
            <span className="text-[#b5bac1]">#</span>
            <span className="truncate">podcast-live</span>
          </button>
          <div className="px-2 pl-4 py-0.5 text-[#6d6f78] text-[15px] font-medium hover:text-[#dbdee1] hover:bg-[#35373c] rounded cursor-pointer transition-colors">
            # transcript
          </div>
          <div className="px-2 pl-4 py-0.5 text-[#6d6f78] text-[15px] font-medium hover:text-[#dbdee1] hover:bg-[#35373c] rounded cursor-pointer transition-colors">
            # notes
          </div>
        </div>

        {/* Members / online agents */}
        <div className="space-y-1">
          <div className="px-2 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-[#949ba4] flex items-center gap-1">
            On air — <span className="text-[#23a55a]">{agents.length}</span>
          </div>
          {agents.map((agent) => {
            const p = agentProfile(agent)
            const isStreaming = streamingAgent === agent
            return (
              <div key={agent} className="flex items-center gap-3 px-2 py-1.5 rounded-md hover:bg-[#35373c] transition-colors cursor-pointer">
                <span className="relative inline-flex">
                  <span className="w-8 h-8 rounded-full flex items-center justify-center text-sm" style={{ backgroundColor: p.avatarColor }}>
                    {roleIcon(agent)}
                  </span>
                  <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-[#2b2d31] p-[2px] flex items-center justify-center">
                    <span className={`w-2.5 h-2.5 rounded-full ${isStreaming ? 'bg-[#f0b232] animate-pulse' : 'bg-[#23a55a]'}`} />
                  </span>
                </span>
                <span className="flex-1 text-[15px] font-medium" style={{ color: p.usernameColor }}>
                  {p.label}
                  {isStreaming && <span className="ml-1.5 text-[11px] text-[#f0b232]">● typing</span>}
                </span>
              </div>
            )
          })}

          {/* Turn progress in member area */}
          <div className="mx-2 mt-3 p-3 rounded-lg bg-[#232428]/60 border border-[#26292c]">
            <div className="text-[11px] uppercase tracking-wide text-[#949ba4] font-semibold mb-1.5">Progress</div>
            <div className="h-1.5 w-full rounded-full bg-[#1e1f22] overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${isComplete ? 'bg-[#23a55a]' : 'bg-[#5865f2]'}`}
                style={{ width: `${Math.min(100, (turnCount / Math.max(1, maxTurns)) * 100)}%` }}
              />
            </div>
            <div className="flex justify-between mt-1.5 text-[11px] text-[#949ba4]">
              <span>Turn {turnCount} / {maxTurns}</span>
              <span>{isComplete ? 'Done' : `${Math.round((turnCount / Math.max(1, maxTurns)) * 100)}%`}</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}