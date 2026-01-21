/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Warm Dark Theme (Bear's Den)
        background: '#18181b',      // zinc-900
        surface: '#27272a',         // zinc-800
        'surface-hover': '#3f3f46', // zinc-700
        border: '#3f3f46',          // zinc-700
        'border-subtle': '#27272a', // zinc-800

        // Brand colors
        amber: {
          DEFAULT: '#f59e0b',
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },

        // Status colors
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',

        // Tier colors (matching game)
        tier: {
          s: '#f59e0b',      // Gold/Amber for S+/S
          a: '#a855f7',      // Purple for A
          b: '#3b82f6',      // Blue for B
          c: '#22c55e',      // Green for C
          d: '#6b7280',      // Gray for D
        },

        // Class colors
        class: {
          infantry: '#ef4444',  // Red
          lancer: '#22c55e',    // Green
          marksman: '#3b82f6',  // Blue
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(245, 158, 11, 0.15)',
        'glow-sm': '0 0 10px rgba(245, 158, 11, 0.1)',
      },
    },
  },
  plugins: [],
}
