/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'healthy': '#10B981',
        'unhealthy': '#EF4444',
        'inactive': '#6B7280',
        'connected': '#10B981',
        'disconnected': '#EF4444'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flow': 'flow 2s linear infinite'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
}
