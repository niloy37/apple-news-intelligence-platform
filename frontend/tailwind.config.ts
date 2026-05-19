import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18202a",
        panel: "#f8faf7",
        line: "#d8dfd8",
        apple: "#2f7d5c",
        signal: "#1d6f99",
        amber: "#b7791f",
        rose: "#b0445a"
      },
      boxShadow: {
        dashboard: "0 8px 24px rgba(24, 32, 42, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
