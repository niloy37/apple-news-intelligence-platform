import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Apple News Intelligence Platform",
  description: "Portfolio data engineering dashboard for Apple-related news and social intelligence"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
