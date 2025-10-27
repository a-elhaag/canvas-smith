import type { Config } from 'tailwindcss'

export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb', // blue-600
          light: '#3b82f6', // blue-500
          dark: '#1e40af', // blue-800
        },
        secondary: {
          DEFAULT: '#f59e42', // orange-400
          light: '#fbbf24', // orange-300
          dark: '#b45309', // orange-700
        },
        accent: {
          DEFAULT: '#10b981', // emerald-500
          light: '#6ee7b7', // emerald-300
          dark: '#047857', // emerald-800
        },
        background: '#f8fafc', // slate-50
        surface: '#ffffff',
        error: '#ef4444', // red-500
        success: '#22c55e', // green-500
        text: {
          DEFAULT: '#1e293b', // slate-800
          light: '#64748b', // slate-400
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        md: '0.5rem',
        lg: '1rem',
      },
    },
  },
  plugins: [],
} satisfies Config
