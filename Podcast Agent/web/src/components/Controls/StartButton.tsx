interface StartButtonProps {
  onClick: () => void
  disabled?: boolean
}

export function StartButton({ onClick, disabled }: StartButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full py-3 rounded-xl font-semibold text-[15px] transition-all duration-200 ${
        disabled
          ? 'bg-elevated text-muted cursor-not-allowed'
          : 'bg-accent text-white hover:bg-accent-hover shadow-lg shadow-accent/25 active:scale-[0.99]'
      }`}
    >
      Launch Session
    </button>
  )
}