/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");

module.exports = {
  content: [
    "./index.html",              // Vite entry
    "./src/**/*.{js,ts,jsx,tsx}" // All components/pages
  ],
  theme: {
    extend: {
      colors: {
        softBlue: "#E0ECF8",
        softGray: "#F7F9FC",
        rose: "#FDE2E2",
        slate: colors.slate,
        sky: colors.sky,
        indigo: colors.indigo,
        gray: colors.gray,
        blue: colors.blue,
        red: colors.red,
        green: colors.green,
        yellow: colors.yellow,
        white: colors.white,
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      boxShadow: {
        soft: "0 4px 14px rgba(0, 0, 0, 0.05)",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography")
  ],
};
