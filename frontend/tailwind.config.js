import {heroui} from "@heroui/theme"

/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      },
      animation: {
        "gradient-shift": "gradient-shift 8s ease infinite",
      },
      keyframes: {
        "gradient-shift": {
          "0%, 100%": {
            transform: "translate(0%, 0%)",
          },
          "25%": {
            transform: "translate(10%, 10%)",
          },
          "50%": {
            transform: "translate(-5%, 15%)",
          },
          "75%": {
            transform: "translate(-10%, -5%)",
          },
        },
      },
    },
  },
  darkMode: "class",
  plugins: [heroui()],
}

module.exports = config;