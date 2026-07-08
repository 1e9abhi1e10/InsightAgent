import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "InsightAgent — Conversational Data Analyst",
  description:
    "Ask your retail database anything in plain English. NL → SQL → grounded answers and live charts.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans text-slate-800 antialiased">{children}</body>
    </html>
  );
}
