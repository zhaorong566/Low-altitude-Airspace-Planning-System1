/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1890ff',
        danger: '#ff4d4f',
        warning: '#faad14',
        success: '#52c41a',
        dark: {
          bg: '#0a0e1a',
          panel: '#111827',
          card: '#1a2235',
          border: '#2a3a55',
        }
      }
    },
  },
  plugins: [],
}
