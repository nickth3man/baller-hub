import "./globals.css";
import type { Metadata } from "next";
import { Bebas_Neue, Space_Grotesk } from "next/font/google";
import { Header } from "@/(components)/layout/Header";
import { Footer } from "@/(components)/layout/Footer";
import { Providers } from "./providers";

const displayFont = Bebas_Neue({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
});
const bodyFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Basketball Reference Clone",
  description:
    "Local clone of basketball-reference.com with comprehensive NBA statistics",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${displayFont.variable} ${bodyFont.variable} font-sans`}
      >
        <Providers>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="container mx-auto flex-1 px-4 py-6">
              {children}
            </main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}
