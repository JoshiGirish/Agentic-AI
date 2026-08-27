

interface StopButtonProps {
  onClick: () => void
  disabled?: boolean
}

export function StopButton({ onClick, disabled }: StopButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-lg font-medium transition-all ${
        disabled
          ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed'
          : 'bg-red-500/20 text-red-300 hover:bg-red-500/30'
      }`}
    >
      Stop
    </button>
  )
}
