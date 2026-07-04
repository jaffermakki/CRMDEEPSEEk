/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./modules/**/*.py"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f4f6fa',
          100: '#e9edf5',
          500: '#1e5c3a', // Forest Green
          900: '#0f172a',
        },
        accent: '#ffd34d', // Gold
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
