module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        slateish: {
          950: '#07111f',
          900: '#0d1728',
          800: '#152338',
          700: '#243452',
        },
        signal: {
          500: '#7dd3fc',
          600: '#38bdf8',
          700: '#0ea5e9',
        },
        danger: {
          500: '#fb7185',
          600: '#f43f5e',
        },
        calm: {
          500: '#34d399',
          600: '#10b981',
        },
        warn: {
          500: '#fbbf24',
          600: '#f59e0b',
        },
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(125, 211, 252, 0.2), 0 20px 40px rgba(0, 0, 0, 0.35)',
      },
    },
  },
  plugins: [],
}
