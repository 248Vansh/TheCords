/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx,css}", // <-- include src files and CSS
    "./public/index.html",             // optional, in case you use Tailwind classes in index.html
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1e40af',   // matches your PostCSS config
        secondary: '#f97316',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        display: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
};


