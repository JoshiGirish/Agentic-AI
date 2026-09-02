import { useNavigate } from 'react-router-dom'

// Minimal server rail: clean navigation with subtle interactions
export function ServerRail() {
  const navigate = useNavigate()
  return (
    <nav className="w-[64px] flex-shrink-0 bg-[var(--bg-primary)] flex flex-col items-center py-2.5 gap-1 select-none border-r border-[var(--border-color)]">
      {/* Home button */}
      <button
        onClick={() => navigate('/home')}
        aria-label="Home"
        title="Home"
        className="group relative flex items-center justify-center w-10 h-10 rounded-xl text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors duration-200 hover:bg-[var(--bg-tertiary)] hover:rounded-lg"
      >
        <span className="text-lg" aria-hidden="true">🏠</span>
        <span className="absolute left-[44px] px-2 py-1.5 rounded-md bg-[var(--bg-primary)] text-[var(--text-primary)] text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-lg border border-[var(--border-color)]">
          Home
        </span>
      </button>

      {/* Active podcast button - primary action */}
      <button
        onClick={() => navigate('/conversation')}
        aria-label="AI Podcast"
        title="AI Podcast"
        className="group relative flex items-center justify-center w-10 h-10 rounded-xl text-[var(--text-primary)] transition-colors duration-200 bg-[var(--primary)] hover:bg-[var(--primary-hover)] shadow-lg shadow-black/20"
      >
        <span className="text-lg" aria-hidden="true">🎙</span>
        <span className="absolute left-[44px] px-2 py-1.5 rounded-md bg-[var(--bg-primary)] text-[var(--text-primary)] text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-lg border border-[var(--border-color)]">
          AI Podcast
        </span>
      </button>

      {/* Spacing for scroll buffer */}
      <div className="flex-1" />
    </nav>
  )
}