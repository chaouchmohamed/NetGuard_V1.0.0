/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber': {
          'dark': '#0a0e1a',
          'darker': '#05070c',
          'card': '#0d1117',
          'cyan': '#00f5ff',
          'amber': '#ffb800',
          'red': '#ff2d55',
          'green': '#00ff88',
          'purple': '#7b2eda',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
        'sans': ['Rajdhani', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
        'flicker': 'flicker 0.15s infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: 1, filter: 'brightness(1)' },
          '50%': { opacity: 0.8, filter: 'brightness(1.2)' },
        },
        'scanline': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'flicker': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.8 },
        },
        'slideIn': {
          '0%': { transform: 'translateY(-20px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        'blink': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0 },
        },
      },
      backgroundImage: {
        'cyber-grid': 'linear-gradient(rgba(0, 245, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 245, 255, 0.05) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid': '20px 20px',
      },
    },
  },
  plugins: [],
}
