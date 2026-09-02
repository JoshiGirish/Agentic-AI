interface RoleSelectorProps {
  value: 'host_guest' | 'skeptic_enthusiast'
  onChange: (value: 'host_guest' | 'skeptic_enthusiast') => void
}

export function RoleSelector({ value, onChange }: RoleSelectorProps) {
  return (
    <div>
      <label className="block text-xs font-semibold uppercase tracking-wider text-[#6b7280] mb-1.5">
        Conversation mode
      </label>
      <div className="grid grid-cols-2 gap-1.5 p-1 rounded-lg bg-[#0d0f12]">
        <button
          onClick={() => onChange('host_guest')}
          className={`rounded-md px-3 py-2.5 text-left transition-colors ${
            value === 'host_guest' ? 'bg-[#e94560] text-white' : 'text-[#9ca3af] hover:bg-[#1a1d24]'
          }`}
        >
          <div className="text-[14px] font-medium">Host & Guest</div>
          <div className={`text-[11px] ${value === 'host_guest' ? 'text-white/80' : 'text-[#6b7280]'}`}>
            Guided discussion
          </div>
        </button>
        <button
          onClick={() => onChange('skeptic_enthusiast')}
          className={`rounded-md px-3 py-2.5 text-left transition-colors ${
            value === 'skeptic_enthusiast' ? 'bg-[#e94560] text-white' : 'text-[#9ca3af] hover:bg-[#1a1d24]'
          }`}
        >
          <div className="text-[14px] font-medium">Debate</div>
          <div className={`text-[11px] ${value === 'skeptic_enthusiast' ? 'text-white/80' : 'text-[#6b7280]'}`}>
            Skeptic & Enthusiast
          </div>
        </button>
      </div>
    </div>
  )
}
