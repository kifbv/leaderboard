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
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-lg mx-auto flex items-center justify-between">
            <span className="font-bold text-lg">🏓 Leaderboard</span>
            <a
              href="/log-match"
              className="text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              Log Match
            </a>
          </div>
        </nav>
        <main className="max-w-lg mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
