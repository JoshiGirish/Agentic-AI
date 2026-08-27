

interface RoleSelectorProps {
  value: 'host_guest' | 'skeptic_enthusiast'
  onChange: (value: 'host_guest' | 'skeptic_enthusiast') => void
}

export function RoleSelector({ value, onChange }: RoleSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="block text-white font-medium">Conversation Mode</label>
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => onChange('host_guest')}
          className={`p-4 rounded-xl border-2 transition-all ${
            value === 'host_guest'
              ? 'border-purple-500 bg-purple-500/20 text-white'
              : 'border-white/10 bg-white/5 text-white/60 hover:border-white/30'
          }`}
        >
          <div className="font-semibold">Host & Guest</div>
          <div className="text-xs text-white/50 mt-1">Guided discussion with expert insights</div>
        </button>
        <button
          onClick={() => onChange('skeptic_enthusiast')}
          className={`p-4 rounded-xl border-2 transition-all ${
            value === 'skeptic_enthusiast'
              ? 'border-green-500 bg-green-500/20 text-white'
              : 'border-white/10 bg-white/5 text-white/60 hover:border-white/30'
          }`}
        >
          <div className="font-semibold">Skeptic & Enthusiast</div>
          <div className="text-xs text-white/50 mt-1">Debate with critical & positive views</div>
        </button>
      </div>
    </div>
  )
}
