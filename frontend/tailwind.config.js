/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Arctic Night Theme - Dark Glacier Blue
        glacier: {
          50: '#E8F4F8',
          100: '#D1E9F1',
          200: '#A3D3E3',
          300: '#75BDD5',
          400: '#4A90D9',
          500: '#2E5A8C',
          600: '#1A3A5C',
          700: '#122340',
          800: '#0A1628',
          900: '#060D15',
        },

        // Primary colors
        ice: {
          DEFAULT: '#4A90D9',
          light: '#7DD3FC',
          dark: '#2E5A8C',
        },
        frost: {
          DEFAULT: '#E8F4F8',
          muted: '#B8D4E8',
        },

        // Accent colors
        fire: {
          DEFAULT: '#FF6B35',
          light: '#FF8C42',
          dark: '#D35400',
        },
        gold: '#FFD700',

        // Background colors
        background: {
          DEFAULT: '#0A1628',
          light: '#122340',
          card: 'rgba(35, 61, 93, 0.4)',
        },

        // Surface colors
        surface: {
          DEFAULT: '#1A3A5C',
          hover: '#2E5A8C',
          border: 'rgba(74, 144, 217, 0.3)',
        },

        // Text colors
        text: {
          primary: '#E8F4F8',
          secondary: '#8F9DB4',
          muted: '#5A6A7A',
        },

        // Status colors
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',

        // Tier colors (matching game)
        tier: {
          splus: '#FF4444',
          s: '#FF8C00',
          a: '#9932CC',
          b: '#4169E1',
          c: '#32CD32',
          d: '#808080',
        },

        // Class colors
        class: {
          infantry: '#EF4444',
          lancer: '#22C55E',
          marksman: '#3B82F6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(74, 144, 217, 0.3)',
        'glow-sm': '0 0 10px rgba(74, 144, 217, 0.2)',
        'glow-lg': '0 0 30px rgba(74, 144, 217, 0.4)',
        'glow-xl': '0 0 40px rgba(74, 144, 217, 0.5)',
        'glow-2xl': '0 0 60px rgba(74, 144, 217, 0.6)',
        'glow-fire': '0 0 20px rgba(255, 107, 53, 0.3)',
        'card': '0 4px 20px rgba(0, 0, 0, 0.3)',
      },
      dropShadow: {
        'glow': '0 0 30px rgba(125, 211, 252, 0.6)',
      },
      backgroundImage: {
        'gradient-main': 'linear-gradient(135deg, #060D15 0%, #0A1628 25%, #122340 50%, #1A3A5C 75%, #122340 90%, #0A1628 100%)',
        'gradient-sidebar': 'linear-gradient(180deg, #0A1628 0%, #122340 30%, #1A3A5C 50%, #122340 70%, #0A1628 100%)',
        'gradient-card': 'linear-gradient(135deg, rgba(26, 58, 92, 0.6), rgba(46, 90, 140, 0.3))',
        'gradient-fire': 'linear-gradient(135deg, #FF6B35, #FF8C42)',
        'gradient-landing': 'linear-gradient(180deg, #0A1628 0%, #0F2847 45%, #1A4B6E 70%, #2E7DA8 88%, #5AADD6 96%, #7DD3FC 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'drift': 'drift 8s ease-in-out infinite',
        'fadeIn': 'fadeIn 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(74, 144, 217, 0.2)' },
          '50%': { boxShadow: '0 0 20px rgba(74, 144, 217, 0.4)' },
        },
        drift: {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-20px) rotate(10deg)' },
        },
      },
      // Mobile-first breakpoints
      screens: {
        'xs': '375px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [],
}
