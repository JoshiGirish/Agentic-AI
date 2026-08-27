

interface StartButtonProps {
  onClick: () => void
  disabled?: boolean
}

export function StartButton({ onClick, disabled }: StartButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full py-4 rounded-xl font-bold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] ${
        disabled
          ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed'
          : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-500 hover:to-blue-500 shadow-lg shadow-purple-500/25'
      }`}
    >
      Start Conversation
    </button>
  )
}
