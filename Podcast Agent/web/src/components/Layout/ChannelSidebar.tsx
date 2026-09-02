import { agentProfile, roleIcon } from '../../lib/agentConfig'

interface ChannelSidebarProps {
  agents: string[]          // roles currently in the conversation
  turnCount: number
  maxTurns: number
  isComplete: boolean
  streamingAgent: string | null
}

// Channel / member sidebar (second column) for a conversation.
export function ChannelSidebar({ agents, turnCount, maxTurns, isComplete, streamingAgent }: ChannelSidebarProps) {
  return (
    <aside className="w-64 flex-shrink-0 bg-sidebar flex flex-col overflow-hidden select-none">
      {/* Guild header */}
      <div className="h-12 px-4 flex items-center justify-between border-b border-line bg-sidebar">
        <span className="text-ink font-semibold text-[15px]">AI Podcast</span>
        <span className="w-5 h-5 rounded-md bg-accent text-white text-[11px] flex items-center justify-center">🎙</span>
      </div>

      <div className="flex-1 overflow-y-auto p-2.5 space-y-5">
        {/* Channel list */}
        <div className="space-y-1">
          <div className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted">Channels</div>
          <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md bg-elevated text-ink text-[15px] font-semibold">
            <span className="text-sub">#</span>
            <span className="truncate">podcast-live</span>
          </button>
          <div className="px-9 py-1 text-muted text-[14px] font-medium hover:text-sub hover:bg-hovered rounded cursor-pointer transition-colors">
            # transcript
          </div>
          <div className="px-9 py-1 text-muted text-[14px] font-medium hover:text-sub hover:bg-hovered rounded cursor-pointer transition-colors">
            # notes
          </div>
        </div>

        {/* Members / online agents */}
        <div className="space-y-1">
          <div className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted flex items-center gap-1">
            On air — <span className="text-online">{agents.length}</span>
          </div>
          {agents.map((agent) => {
            const p = agentProfile(agent)
            const isStreaming = streamingAgent === agent
            return (
              <div key={agent} className="flex items-center gap-3 px-2 py-1.5 rounded-md hover:bg-hovered transition-colors cursor-pointer">
                <span className="relative inline-flex">
                  <span className="w-8 h-8 rounded-full flex items-center justify-center text-sm ring-2 ring-sidebar" style={{ backgroundColor: p.avatarColor }}>
                    {roleIcon(agent)}
                  </span>
                  <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-sidebar p-[2px] flex items-center justify-center">
                    <span className={`w-2.5 h-2.5 rounded-full ${isStreaming ? 'bg-warning animate-pulse' : 'bg-online'}`} />
                  </span>
                </span>
                <span className="flex-1 text-[15px] font-medium" style={{ color: p.usernameColor }}>
                  {p.label}
                  {isStreaming && <span className="ml-1.5 text-[11px] text-warning font-semibold">● typing</span>}
                </span>
              </div>
            )
          })}

          {/* Turn progress in member area */}
          <div className="mt-4 p-3 rounded-lg bg-elevated/50 border border-line">
            <div className="text-[11px] uppercase tracking-wide text-muted font-semibold mb-2">Progress</div>
            <div className="h-1.5 w-full rounded-full bg-field overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${isComplete ? 'bg-online' : 'bg-accent'}`}
                style={{ width: `${Math.min(100, (turnCount / Math.max(1, maxTurns)) * 100)}%` }}
              />
            </div>
            <div className="flex justify-between mt-2 text-[11px] text-muted tabular-nums">
              <span>Turn {turnCount} / {maxTurns}</span>
              <span>{isComplete ? 'Done' : `${Math.round((turnCount / Math.max(1, maxTurns)) * 100)}%`}</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}