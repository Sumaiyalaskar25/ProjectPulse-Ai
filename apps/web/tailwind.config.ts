import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#0A0E1A',
          surface: '#0F1420',
          card: '#141925',
          'card-hover': '#181F2E',
          border: '#1F2637',
        },
        status: {
          critical: '#EF4444',
          high: '#F59E0B',
          moderate: '#F97316',
          stable: '#22C55E',
          info: '#38BDF8',
        },
        text: {
          primary: '#F8FAFC',
          secondary: '#94A3B8',
          muted: '#64748B',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', '"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config
