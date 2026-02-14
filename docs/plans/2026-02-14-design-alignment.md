# Design Alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restyle all UI pages from light mode to dark mode, matching the design references in `designs/`.

**Architecture:** Pure CSS/JSX styling changes — no functionality, API, or schema modifications. All changes are in 5 files: `globals.css`, `layout.tsx`, `page.tsx`, `LogMatchForm.tsx`, `AdminRosterForm.tsx`. Tailwind v4 uses `@theme {}` blocks in CSS (no JS config file).

**Tech Stack:** Next.js 16 (App Router), Tailwind CSS v4, Google Fonts (Lexend, Material Symbols Outlined)

---

### Task 1: Global dark theme — fonts, color tokens, layout shell

**Files:**
- Modify: `src/app/globals.css`
- Modify: `src/app/layout.tsx`

**Step 1: Update globals.css with font imports, theme tokens, and base styles**

Replace the entire contents of `src/app/globals.css` with:

```css
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
@import "tailwindcss";

@theme {
  --color-primary: #135bec;
  --color-background-dark: #0b121e;
  --color-card-dark: #0d1625;
  --color-background-light: #f6f6f8;
}

body {
  font-family: 'Lexend', sans-serif;
  -webkit-tap-highlight-color: transparent;
}
```

**Step 2: Update layout.tsx — dark class, remove nav, add max-w-md container**

Replace `src/app/layout.tsx` with:

```tsx
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
```

Key changes:
- `className="dark"` on `<html>`
- `bg-background-dark text-white` on `<body>` (uses theme token)
- Removed `<nav>` entirely (pages handle their own headers)
- Removed `<main>` wrapper, replaced with `<div className="max-w-md mx-auto">`

**Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS (no type changes, only className strings)

**Step 4: Commit**

```bash
git add src/app/globals.css src/app/layout.tsx
git commit -m "style: add dark theme, Lexend font, and color tokens (US-013)"
```

---

### Task 2: Leaderboard — sticky header and FAB

**Files:**
- Modify: `src/app/page.tsx`

**Step 1: Add sticky header with Material Symbol icon**

Replace the `<h1 className="text-2xl font-bold mb-4">Standings</h1>` with:

```tsx
<header className="sticky top-0 z-30 bg-background-dark/80 backdrop-blur-lg px-6 pt-10 pb-4">
  <div className="flex items-center gap-2">
    <span className="material-symbols-outlined text-primary text-4xl font-bold">sports_tennis</span>
    <h1 className="text-2xl font-bold tracking-tight">TGSB Leaderboard</h1>
  </div>
</header>
```

**Step 2: Add FAB (floating action button) at the bottom of the page**

After the closing `</main>` (or at the end of the page's return JSX), add:

```tsx
<a
  href="/log-match"
  className="fixed bottom-8 right-6 z-40 px-8 py-4 bg-primary text-white rounded-full shadow-[0_8px_30px_rgb(19,91,236,0.4)] flex items-center justify-center hover:scale-105 active:scale-95 transition-transform"
>
  <span className="text-sm font-bold tracking-wide">Log Match</span>
</a>
```

**Step 3: Update the outer wrapper div**

The page's outer `<div>` should have padding for content below the header. Update to:

```tsx
<div className="relative flex min-h-screen flex-col">
  {/* header */}
  {/* content sections */}
  {/* FAB */}
</div>
```

**Step 4: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/page.tsx
git commit -m "style: add sticky header and FAB to leaderboard (US-014)"
```

---

### Task 3: Leaderboard — top-3 podium

**Files:**
- Modify: `src/app/page.tsx`

**Step 1: Add a helper function for deterministic avatar colors**

Add at the top of the file (outside the component):

```tsx
const AVATAR_COLORS = [
  "bg-blue-600", "bg-emerald-600", "bg-purple-600", "bg-rose-600",
  "bg-amber-600", "bg-cyan-600", "bg-indigo-600", "bg-pink-600",
];

function getAvatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}
```

**Step 2: Add podium section**

After the header, before the card rows, add a podium section. Only render if there are 2+ players:

```tsx
{rankedRows.length >= 2 && (
  <section className="px-6 py-4">
    <div className="flex items-end justify-center gap-4 py-4">
      {/* 2nd place (left) */}
      <div className="flex flex-col items-center gap-3 flex-1">
        <div className="relative">
          <div className={`w-16 h-16 rounded-full border-2 border-slate-700 flex items-center justify-center text-xl font-bold ${getAvatarColor(rankedRows[1].name)}`}>
            {rankedRows[1].name.charAt(0)}
          </div>
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-slate-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">2nd</div>
        </div>
        <div className="text-center">
          <p className="text-xs font-bold truncate max-w-[80px]">{rankedRows[1].name}</p>
          <p className="text-sm font-semibold text-primary">{rankedRows[1].eloRating}</p>
          <p className="text-[9px] text-slate-500 uppercase tracking-tighter">{rankedRows[1].wins}W - {rankedRows[1].losses}L</p>
        </div>
      </div>

      {/* 1st place (center, raised) */}
      <div className="flex flex-col items-center gap-3 flex-1 -mt-4">
        <div className="relative">
          <div className={`w-20 h-20 rounded-full border-4 border-primary shadow-[0_0_20px_rgba(19,91,236,0.3)] flex items-center justify-center text-2xl font-bold ${getAvatarColor(rankedRows[0].name)}`}>
            {rankedRows[0].name.charAt(0)}
          </div>
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">1st</div>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold truncate max-w-[100px]">{rankedRows[0].name}</p>
          <p className="text-lg font-bold text-primary">{rankedRows[0].eloRating}</p>
          <p className="text-[10px] text-slate-500 uppercase font-medium tracking-tight">{rankedRows[0].wins}W - {rankedRows[0].losses}L</p>
        </div>
      </div>

      {/* 3rd place (right) — only if 3+ players */}
      {rankedRows.length >= 3 && (
        <div className="flex flex-col items-center gap-3 flex-1">
          <div className="relative">
            <div className={`w-16 h-16 rounded-full border-2 border-[#b87333]/50 flex items-center justify-center text-xl font-bold ${getAvatarColor(rankedRows[2].name)}`}>
              {rankedRows[2].name.charAt(0)}
            </div>
            <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-[#b87333]/80 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">3rd</div>
          </div>
          <div className="text-center">
            <p className="text-xs font-bold truncate max-w-[80px]">{rankedRows[2].name}</p>
            <p className="text-sm font-semibold text-primary">{rankedRows[2].eloRating}</p>
            <p className="text-[9px] text-slate-500 uppercase tracking-tighter">{rankedRows[2].wins}W - {rankedRows[2].losses}L</p>
          </div>
        </div>
      )}
    </div>
  </section>
)}
```

**Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 4: Commit**

```bash
git add src/app/page.tsx
git commit -m "style: add top-3 podium with initials avatars (US-015)"
```

---

### Task 4: Leaderboard — card rows for 4th+ players

**Files:**
- Modify: `src/app/page.tsx`

**Step 1: Replace the existing `<table>` with card rows**

Remove the entire `<div className="overflow-x-auto">...<table>...</table></div>` block.

Replace with card rows for players ranked 4th and below (index >= 3, or all players if fewer than 2):

```tsx
<main className="flex-1 px-6 pb-40">
  {rankedRows.length === 0 ? (
    <p className="text-slate-500 text-center py-12">No players yet</p>
  ) : (
    <div className="space-y-4 mt-6">
      {rankedRows.slice(rankedRows.length >= 2 ? 3 : 0).map((player) => (
        <div
          key={player.id}
          className="flex items-center gap-4 bg-card-dark p-4 rounded-2xl hover:bg-slate-800/40 transition-all"
        >
          <span className="w-4 text-sm font-bold text-slate-400">{player.rank}</span>
          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold shrink-0 ${getAvatarColor(player.name)}`}>
            {player.name.charAt(0)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold truncate">{player.name}</p>
            <p className="text-[10px] text-slate-500 font-medium uppercase tracking-tight">
              {player.wins}W - {player.losses}L · {player.winRate}% Win
            </p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-primary tracking-tight">{player.eloRating}</p>
          </div>
        </div>
      ))}
    </div>
  )}
</main>
```

Note: If there are 0–1 players, skip the podium and show all players (or "no players" state) in cards. The `slice(rankedRows.length >= 2 ? 3 : 0)` handles this — when podium isn't shown, all players go into cards.

**Step 2: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 3: Visual verification**

Run: `npm run dev`
Check: http://localhost:3000 at 375px viewport.
- Header sticky with tennis icon
- Podium shows top 3 (if seeded)
- Card rows for 4th+
- FAB in bottom-right
- All dark mode

**Step 4: Commit**

```bash
git add src/app/page.tsx
git commit -m "style: replace table with card rows for 4th+ players (US-016)"
```

---

### Task 5: Log match — modal header and dark theme container

**Files:**
- Modify: `src/app/log-match/LogMatchForm.tsx`

**Step 1: Update outer container and add modal header**

In `LogMatchForm.tsx`, replace the outer `<div>` and `<h1>` with:

```tsx
<div className="min-h-screen bg-background-dark flex flex-col">
  {/* Header */}
  <header className="sticky top-0 z-10 bg-background-dark/80 backdrop-blur-md px-4 py-4 flex items-center justify-between border-b border-slate-800">
    <a href="/" className="w-10 h-10 flex items-center justify-start text-slate-500 hover:text-primary transition-colors">
      <span className="material-symbols-outlined text-2xl">close</span>
    </a>
    <h1 className="text-lg font-semibold tracking-tight">Log Match</h1>
    <div className="w-10"></div>
  </header>

  <main className="flex-1 px-6 py-8 flex flex-col gap-8">
    {/* Toggle + form content here */}
  </main>
</div>
```

**Step 2: Restyle the Singles/Doubles toggle**

Replace the toggle button classes:

```tsx
<div className="flex gap-2">
  <button
    onClick={() => handleTypeChange("SINGLES")}
    className={`flex-1 py-2 px-4 rounded-lg font-medium text-base transition-colors ${
      matchType === "SINGLES"
        ? "bg-primary text-white"
        : "bg-slate-800 text-slate-400"
    }`}
  >
    Singles
  </button>
  <button
    onClick={() => handleTypeChange("DOUBLES")}
    className={`flex-1 py-2 px-4 rounded-lg font-medium text-base transition-colors ${
      matchType === "DOUBLES"
        ? "bg-primary text-white"
        : "bg-slate-800 text-slate-400"
    }`}
  >
    Doubles
  </button>
</div>
```

**Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 4: Commit**

```bash
git add src/app/log-match/LogMatchForm.tsx
git commit -m "style: add modal header and dark theme to log match (US-017)"
```

---

### Task 6: Log match — restyle dropdowns and "Who played?" section

**Files:**
- Modify: `src/app/log-match/LogMatchForm.tsx`

**Step 1: Add "Who played?" heading above the dropdowns**

Before the player selects in both singles and doubles mode, add:

```tsx
<div className="text-center">
  <h2 className="text-2xl font-bold mb-1">Who played?</h2>
  <p className="text-slate-500 text-sm">Select the match participants.</p>
</div>
```

**Step 2: Update PlayerSelect component for dark mode**

Replace the `PlayerSelect` component's JSX:

```tsx
function PlayerSelect({
  id,
  label,
  value,
  onChange,
  players,
  disabledIds,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (val: string) => void;
  players: Player[];
  disabledIds: string[];
}) {
  return (
    <div className="flex flex-col gap-2">
      <label
        htmlFor={id}
        className="text-[10px] font-bold uppercase tracking-widest text-primary ml-1"
      >
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 px-3 text-sm text-white focus:ring-2 focus:ring-primary/50 transition-all cursor-pointer"
      >
        <option value="">Select Player</option>
        {players.map((p) => (
          <option
            key={p.id}
            value={p.id}
            disabled={disabledIds.includes(String(p.id))}
          >
            {p.name} ({p.eloRating})
          </option>
        ))}
      </select>
    </div>
  );
}
```

**Step 3: Use 2-column grid for singles player dropdowns**

Replace the `<div className="space-y-4">` wrapping the two PlayerSelect components in singles mode with:

```tsx
<div className="grid grid-cols-2 gap-4">
  <PlayerSelect id="player1" label="Player 1" ... />
  <PlayerSelect id="player2" label="Player 2" ... />
</div>
```

**Step 4: Update doubles mode team headers**

Replace `text-gray-800` with `text-slate-400`:

```tsx
<p className="text-sm font-semibold text-slate-400 mb-3">Team 1</p>
```

Also update each team's player selects to use `grid grid-cols-2 gap-4` instead of `space-y-3`.

**Step 5: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 6: Commit**

```bash
git add src/app/log-match/LogMatchForm.tsx
git commit -m "style: restyle dropdowns with dark theme and 2-col grid (US-018)"
```

---

### Task 7: Log match — winner buttons and feedback

**Files:**
- Modify: `src/app/log-match/LogMatchForm.tsx`

**Step 1: Update winner buttons (both singles and doubles)**

Replace active winner button classes:

```tsx
className="flex-1 py-4 px-4 bg-primary hover:bg-primary/90 text-white font-bold rounded-2xl shadow-lg shadow-primary/20 text-base disabled:opacity-50 active:scale-[0.98] transition-all"
```

**Step 2: Update disabled state button**

Replace `bg-gray-300 text-gray-500` with:

```tsx
className="w-full py-4 px-4 bg-slate-800 text-slate-500 font-semibold rounded-2xl text-base cursor-not-allowed"
```

**Step 3: Update success feedback (both singles and doubles)**

Replace `bg-green-50 border-green-200` styling with:

```tsx
className="mb-6 p-4 bg-green-900/30 border border-green-800 rounded-xl"
```

Update text colors: `text-green-800` / `text-green-700` → `text-green-400`.
Update red delta text: `text-red-600` → `text-red-400`.

**Step 4: Update error feedback**

Replace `bg-red-50 border-red-200` with:

```tsx
className="mb-6 p-4 bg-red-900/30 border border-red-800 rounded-xl"
```

Text: `text-red-400` instead of `text-red-700`.

**Step 5: Update loading text**

Replace `text-gray-500` with `text-slate-400`.

**Step 6: Update "Who won?" / "Which team won?" text**

Replace `text-gray-700` with `text-slate-400`.

**Step 7: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 8: Visual verification**

Run: `npm run dev`
Check: http://localhost:3000/log-match at 375px viewport.
- Modal-style header with X close button
- Dark background throughout
- Toggle: active = blue, inactive = dark
- 2-column dropdowns with primary labels
- Blue winner buttons with shadow
- Dark mode success/error feedback

**Step 9: Commit**

```bash
git add src/app/log-match/LogMatchForm.tsx
git commit -m "style: dark mode winner buttons and feedback (US-019)"
```

---

### Task 8: Admin page — dark mode consistency

**Files:**
- Modify: `src/app/admin/[secret]/AdminRosterForm.tsx`

**Step 1: Update heading**

The `<h1>` inherits white text from body — no class change needed.

**Step 2: Update form label and input**

Replace label class `text-gray-700` with `text-slate-400`.

Replace input classes to:

```tsx
className="flex-1 bg-slate-900 border border-slate-800 text-white rounded-xl px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary/50"
```

**Step 3: Update "Add Player" button**

Replace `bg-blue-600 ... hover:bg-blue-700 active:bg-blue-800` with:

```tsx
className="px-4 py-2 bg-primary text-white font-medium rounded-xl text-base disabled:opacity-50 hover:bg-primary/90 transition-colors"
```

**Step 4: Update player list**

Replace the `<ul>` wrapper:

```tsx
className="bg-card-dark rounded-2xl overflow-hidden divide-y divide-slate-800"
```

Replace each `<li>`:

```tsx
className="flex items-center justify-between px-4 py-3"
```

Player name: remove `text-gray-900` (inherits white).
ELO text: replace `text-gray-500` with `text-slate-400`.

**Step 5: Update empty state**

Replace `text-gray-500` with `text-slate-500`.

**Step 6: Update error/success messages**

Error: `text-red-400` (was `text-red-600`).
Success: `text-green-400` (was `text-green-600`).

**Step 7: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 8: Commit**

```bash
git add src/app/admin/[secret]/AdminRosterForm.tsx
git commit -m "style: dark mode for admin roster page (US-020)"
```

---

### Task 9: Final QA — build, lint, typecheck

**Files:** None (validation only)

**Step 1: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS, zero errors

**Step 2: Run lint**

Run: `npm run lint`
Expected: PASS

**Step 3: Run build**

Run: `npm run build`
Expected: PASS, successful production build

**Step 4: Visual verification**

Run: `npm run dev`
Check all three pages at 375px viewport:
- `/` — dark leaderboard with podium, card rows, FAB
- `/log-match` — modal-style dark form
- `/admin/{secret}` — dark admin page

**Step 5: Commit any fixes**

Only commit if fixes were needed during QA.

---

## Reference: File Change Summary

| File | Task | Changes |
|------|------|---------|
| `src/app/globals.css` | 1 | Font imports, `@theme {}` tokens, body font-family |
| `src/app/layout.tsx` | 1 | Dark class, remove nav, max-w-md container |
| `src/app/page.tsx` | 2, 3, 4 | Sticky header, FAB, podium, card rows, avatar colors |
| `src/app/log-match/LogMatchForm.tsx` | 5, 6, 7 | Modal header, dark dropdowns, 2-col grid, dark buttons/feedback |
| `src/app/admin/[secret]/AdminRosterForm.tsx` | 8 | Dark mode input, buttons, list, messages |

## Reference: Design Decisions

- **No search bar** — out of v1 scope (design has it, we skip it)
- **No bottom nav** — out of v1 scope (design has it, we skip it)
- **No score inputs** — log-match design shows "Set Scores" section, but our app only records winner/loser
- **FAB at bottom-8** — design shows bottom-28 (for bottom nav padding), but we use bottom-8 since no bottom nav
- **Initials avatars** — design uses photos, we use first-letter circles with deterministic colors
- **`#0b121e` for all background-dark** — log-match design uses `#101622`, we standardize on leaderboard value
