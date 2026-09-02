import { useNavigate } from 'react-router-dom'

// App rail: brand + home navigation with hover tooltips.
export function ServerRail() {
  const navigate = useNavigate()
  return (
    <nav className="w-16 flex-shrink-0 bg-rail border-r border-line flex flex-col items-center pt-3 pb-3 gap-2 select-none">
      {/* Studio / brand button */}
      <button
        onClick={() => navigate('/home')}
        aria-label="Studio"
        title="Studio"
        className="group relative flex items-center justify-center w-10 h-10 rounded-xl bg-accent text-white hover:bg-accent-hover transition-colors duration-200 shadow-lg shadow-black/30"
      >
        <span className="text-lg" aria-hidden="true">🎙</span>
        <span className="absolute left-[46px] px-2 py-1.5 rounded-md bg-elevated border border-line text-ink text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-lg">
          Studio
        </span>
      </button>

      {/* Home button */}
      <button
        onClick={() => navigate('/home')}
        aria-label="Home"
        title="Home"
        className="group relative flex items-center justify-center w-10 h-10 rounded-xl text-sub hover:text-ink transition-colors duration-200 hover:bg-elevated"
      >
        <span className="text-lg" aria-hidden="true">🏠</span>
        <span className="absolute left-[46px] px-2 py-1.5 rounded-md bg-elevated border border-line text-ink text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-lg">
          Home
        </span>
      </button>

      {/* Spacing for scroll buffer */}
      <div className="flex-1" />
    </nav>
  )
}