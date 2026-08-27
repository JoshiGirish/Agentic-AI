

interface SpeakerBadgeProps {
  agent: string
}

export function SpeakerBadge({ agent }: SpeakerBadgeProps) {
  const colors: Record<string, string> = {
    host: 'bg-blue-500',
    guest: 'bg-purple-500',
    skeptic: 'bg-red-500',
    enthusiast: 'bg-green-500'
  }

  const labels: Record<string, string> = {
    host: 'HOST',
    guest: 'GUEST',
    skeptic: 'SKEPTIC',
    enthusiast: 'ENTHUSIAST'
  }

  return (
    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-lg ${colors[agent] || 'bg-gray-500'}`}>
      {labels[agent] || agent.toUpperCase()}
    </div>
  )
}
