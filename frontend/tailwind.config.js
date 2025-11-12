/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./docs/**/*.{html,md}",
    "./*.html"
  ],
  theme: {
    extend: {
      colors: {
        // Palette Luna Arkalia
        'luna': {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        'arkalia': {
          'black': '#090c12',
          'dark': '#0f1419',
          'slate': '#1e293b',
          'blue': '#7ecbff',
          'cyan': '#0ff',
          'white': '#f8fafc',
          'gray': '#b6c2d6',
        },
        'neural': {
          'blue': '#7ecbff',
          'cyan': '#0ff',
          'glow': '#b6d0ff',
        }
      },
      fontFamily: {
        'orbitron': ['Orbitron', 'monospace'],
        'inter': ['Inter', 'sans-serif'],
        'jetbrains': ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'luna-glow': 'luna-glow 4s ease-in-out infinite alternate',
        'lightning-pulse': 'lightning-pulse 8s ease-in-out infinite',
        'moon-pulse': 'moon-pulse 3s ease-in-out infinite',
        'neural-flicker': 'neural-flicker 2s ease-in-out infinite',
        'cyber-glow': 'cyber-glow 6s ease-in-out infinite',
      },
      keyframes: {
        'luna-glow': {
          '0%': {
            filter: 'drop-shadow(0 0 40px rgba(126, 203, 255, 0.5)) drop-shadow(0 0 80px rgba(126, 203, 255, 0.3))'
          },
          '100%': {
            filter: 'drop-shadow(0 0 80px rgba(182, 208, 255, 0.8)) drop-shadow(0 0 160px rgba(126, 203, 255, 0.5))'
          }
        },
        'lightning-pulse': {
          '0%, 100%': { opacity: '0.08' },
          '50%': { opacity: '0.25' }
        },
        'moon-pulse': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' }
        },
        'neural-flicker': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' }
        },
        'cyber-glow': {
          '0%': {
            boxShadow: '0 0 20px rgba(126, 203, 255, 0.3)',
            textShadow: '0 0 8px rgba(126, 203, 255, 0.5)'
          },
          '50%': {
            boxShadow: '0 0 40px rgba(126, 203, 255, 0.6)',
            textShadow: '0 0 16px rgba(126, 203, 255, 0.8)'
          },
          '100%': {
            boxShadow: '0 0 20px rgba(126, 203, 255, 0.3)',
            textShadow: '0 0 8px rgba(126, 203, 255, 0.5)'
          }
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'luna-glow': '0 0 60px rgba(126, 203, 255, 0.5)',
        'neural-glow': '0 0 120px rgba(126, 203, 255, 0.3)',
        'cyber-glow': '0 0 40px rgba(126, 203, 255, 0.6)',
      },
      textShadow: {
        'luna': '0 0 32px rgba(126, 203, 255, 0.4)',
        'neural': '0 0 16px rgba(126, 203, 255, 0.6)',
        'cyber': '0 0 8px rgba(126, 203, 255, 0.8)',
      },
      letterSpacing: {
        'wider': '0.12em',
        'widest': '0.32em',
        'ultra-wide': '0.5em',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    function({ addUtilities }) {
      const newUtilities = {
        '.text-shadow': {
          'text-shadow': '0 0 8px rgba(126, 203, 255, 0.6)',
        },
        '.text-shadow-lg': {
          'text-shadow': '0 0 16px rgba(126, 203, 255, 0.8)',
        },
        '.text-shadow-xl': {
          'text-shadow': '0 0 32px rgba(126, 203, 255, 0.4)',
        },
        '.neural-border': {
          'border': '1px solid rgba(126, 203, 255, 0.3)',
          'box-shadow': 'inset 0 0 20px rgba(126, 203, 255, 0.1)',
        },
        '.cyber-gradient': {
          'background': 'linear-gradient(135deg, rgba(126, 203, 255, 0.1) 0%, rgba(0, 255, 255, 0.05) 100%)',
        },
        '.luna-gradient': {
          'background': 'radial-gradient(circle at center, rgba(126, 203, 255, 0.1) 0%, transparent 70%)',
        }
      }
      addUtilities(newUtilities)
    }
  ],
}
