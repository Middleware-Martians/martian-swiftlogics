/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0B63E5",
        secondary: "#00A86B", 
        accent: "#FF7A18",
        bg: "#F4F7FB",
        card: "#FFFFFF",
        text: "#0F1724",
        muted: "#64748B",
        error: "#E02424"
      }
    },
  },
  plugins: [],
}
