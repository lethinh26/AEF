import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AEO — Engineering OS",
  description: "A calmer control plane for autonomous engineering.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
