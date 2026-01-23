import "./globals.css";
import type { Metadata } from "next";
import { Bebas_Neue, Space_Grotesk } from "next/font/google";
import { PageLayout } from "@/(components)/layout/PageLayout";
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
          <PageLayout>{children}</PageLayout>
        </Providers>
      </body>
    </html>
  );
}
