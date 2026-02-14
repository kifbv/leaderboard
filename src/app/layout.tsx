import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ping Pong Leaderboard",
  description: "Office ping pong rankings",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background-dark text-white min-h-screen">
        <div className="max-w-md mx-auto">{children}</div>
      </body>
    </html>
  );
}
