import { agentProfile, roleIcon } from '../../lib/agentConfig'

interface SpeakerBadgeProps {
  agent: string
  size?: 'md' | 'lg'
}

// Discord-style circular avatar for an agent role.
export function SpeakerBadge({ agent, size = 'md' }: SpeakerBadgeProps) {
  const p = agentProfile(agent)
  const dim = size === 'lg' ? 'w-11 h-11 text-lg' : 'w-10 h-10 text-base'
  return (
    <span
      className={`${dim} rounded-full flex items-center justify-center text-white/95 shrink-0 shadow`}
      style={{ backgroundColor: p.avatarColor }}
      aria-label={p.label}
    >
      {roleIcon(agent)}
    </span>
  )
}