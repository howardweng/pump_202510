/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // Adjust paths if your project structure is different
  ],
  theme: {
    extend: {
      spacing: {
        21: "5.25rem", // 21 (84px)
        22: "5.5rem",  // 22 (88px)
        23: "5.75rem", // 23 (92px)
        25: "6.25rem", // 25 (100px)
        26: "6.5rem",  // 26 (104px)
        27: "6.75rem", // 27 (108px)
        29: "7.25rem", // 29 (116px)
        30: "7.5rem",  // 30 (120px)
        34: "8.5rem",  // 34 (136px)
        38: "9.5rem",  // 38 (152px)
      },
    }, // Use this to customize Tailwind’s default settings
  },
  plugins: [],
};


