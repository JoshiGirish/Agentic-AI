interface RoleSelectorProps {
  value: 'host_guest' | 'skeptic_enthusiast'
  onChange: (value: 'host_guest' | 'skeptic_enthusiast') => void
}

const MODES: { value: 'host_guest' | 'skeptic_enthusiast'; title: string; subtitle: string }[] = [
  { value: 'host_guest', title: 'Host & Guest', subtitle: 'Guided discussion' },
  { value: 'skeptic_enthusiast', title: 'Debate', subtitle: 'Skeptic & Enthusiast' },
]

export function RoleSelector({ value, onChange }: RoleSelectorProps) {
  return (
    <div>
      <label className="block text-[11px] font-semibold uppercase tracking-wider text-muted mb-2">
        Conversation mode
      </label>
      <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-field border border-line">
        {MODES.map((mode) => {
          const isActive = value === mode.value
          return (
            <button
              key={mode.value}
              onClick={() => onChange(mode.value)}
              className={`rounded-lg px-3 py-2.5 text-left transition-colors ${
                isActive ? 'bg-accent text-white' : 'text-sub hover:bg-hovered'
              }`}
            >
              <div className="text-[14px] font-medium leading-tight">{mode.title}</div>
              <div className={`text-[11px] mt-0.5 ${isActive ? 'text-white/80' : 'text-muted'}`}>
                {mode.subtitle}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}