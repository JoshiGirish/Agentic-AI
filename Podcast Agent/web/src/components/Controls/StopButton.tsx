interface StopButtonProps {
  onClick: () => void
  disabled?: boolean
}

export function StopButton({ onClick, disabled }: StopButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title="Leave / stop conversation"
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
        disabled
          ? 'bg-elevated text-muted cursor-not-allowed'
          : 'bg-error/15 text-error hover:bg-error/30'
      }`}
    >
      Stop
    </button>
  )
}