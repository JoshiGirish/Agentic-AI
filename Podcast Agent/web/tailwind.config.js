// Design tokens (single source of truth for utility colors).
// NOTE: literal hex values are used (not CSS vars) so Tailwind can compile
// opacity modifiers like `bg-online/15`. Mirror these in `src/index.css`
// for the small set of global (non-utility) styles.
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        app: '#0f1218',
        rail: '#0a0d12',
        sidebar: '#141a24',
        panel: '#171d28',
        elevated: '#1d2532',
        hovered: '#232d3d',
        field: '#0c0f15',
        line: '#242c3c',
        ink: '#eef2f7',
        sub: '#a8b2c0',
        muted: '#6d7887',
        accent: {
          DEFAULT: '#e0455f',
          hover: '#ff5d77',
        },
        online: '#2bb673',
        warning: '#f2b93f',
        error: '#f04d4d',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}