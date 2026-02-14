# Design Alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update all UI pages to match the design references in `designs/`, bringing dark mode, Lexend font, podium layout, card rows, styled dropdowns, and modal-style log match page.

**Architecture:** The current UI is functional but uses default light-mode styling with basic HTML tables and generic form elements. The designs call for a dark-mode-first app with Lexend font, primary color `#135bec`, podium top-3 layout on the leaderboard, card-based rows for 4th+ players, floating action button, and a modal-style match logging page. We restyle all existing components in-place — no new functionality needed.

**Tech Stack:** Next.js (App Router), Tailwind CSS v4, Google Fonts (Lexend, Material Symbols Outlined)

---

### Task 1: Set Up Global Theme (Dark Mode, Lexend Font, Color Tokens)

**Files:**
- Modify: `src/app/globals.css`
- Modify: `src/app/layout.tsx`

**Step 1: Write the failing test**

No automated test — this is a styling-only change. Validation: `npx tsc --noEmit` passes.

**Step 2: Update globals.css with Tailwind theme tokens and font imports**

Add Google Fonts imports for Lexend and Material Symbols Outlined. Define CSS custom properties or Tailwind `@theme` tokens for:
- `--color-primary: #135bec`
- `--color-background-dark: #0b121e`
- `--color-card-dark: #0d1625`
- `--color-background-log-match: #101622`
- `--font-display: 'Lexend', sans-serif`

```css
@import "tailwindcss";
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

@theme {
  --color-primary: #135bec;
  --color-bg-dark: #0b121e;
  --color-card-dark: #0d1625;
  --color-bg-log-match: #101622;
  --font-display: 'Lexend', sans-serif;
}
```

**Step 3: Update layout.tsx for dark mode shell**

Replace the current light-mode body and nav:
- `<html lang="en" class="dark">`
- `<body>` with `font-family: Lexend`, dark background `bg-bg-dark`, white text
- Remove the existing light `<nav>` (each page will handle its own header per design)
- Keep `<main>` wrapper with `max-w-md mx-auto` to match design's mobile container

```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="font-display bg-bg-dark text-white min-h-screen">
        <div className="relative flex min-h-screen w-full flex-col max-w-md mx-auto overflow-x-hidden shadow-2xl bg-bg-dark">
          {children}
        </div>
      </body>
    </html>
  );
}
```

**Step 4: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/globals.css src/app/layout.tsx
git commit -m "style: set up dark mode theme with Lexend font and color tokens"
```

---

### Task 2: Restyle Leaderboard Page — Sticky Header and FAB

**Files:**
- Modify: `src/app/page.tsx`

**Step 1: Add sticky header with app title**

Replace the simple `<h1>Standings</h1>` with a sticky header matching the design:
- Sticky top, blur backdrop, transparent-ish dark background
- `sports_tennis` Material Symbol icon in primary color
- "TGSB Leaderboard" title text, bold, tracking-tight
- NO search bar (out of v1 scope)

```tsx
<header className="sticky top-0 z-30 bg-bg-dark/80 backdrop-blur-lg px-6 pt-10 pb-4">
  <div className="flex items-center gap-2">
    <span className="material-symbols-outlined text-primary text-4xl font-bold">sports_tennis</span>
    <h1 className="text-2xl font-bold tracking-tight">TGSB Leaderboard</h1>
  </div>
</header>
```

**Step 2: Add floating "Log Match" FAB**

Add a fixed-position FAB button linking to `/log-match`:
```tsx
<a href="/log-match" className="fixed bottom-8 right-6 z-40 px-8 py-4 bg-primary text-white rounded-full shadow-[0_8px_30px_rgb(19,91,236,0.4)] flex items-center justify-center hover:scale-105 active:scale-95 transition-transform">
  <span className="text-sm font-bold tracking-wide">Log Match</span>
</a>
```

**Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 4: Commit**

```bash
git add src/app/page.tsx
git commit -m "style: add sticky header and floating Log Match FAB to leaderboard"
```

---

### Task 3: Restyle Leaderboard Page — Top-3 Podium Layout

**Files:**
- Modify: `src/app/page.tsx`

**Step 1: Build the podium section**

Replace the table-based leaderboard with a two-part layout:
1. **Podium** (top 3): A flex row with 2nd on left, 1st centered+raised, 3rd on right
2. **Card list** (4th+): Individual card rows

For the podium, each player gets:
- Initials circle (colored based on name hash or fixed colors) — NOT avatar images
- 1st place: larger circle (w-20 h-20) with primary border + glow shadow, "1st" badge in primary
- 2nd place: medium circle (w-16 h-16) with slate border, "2nd" badge in slate
- 3rd place: medium circle (w-16 h-16) with bronze border (`#b87333`), "3rd" badge in bronze
- Below each: player name (truncated), ELO in primary, "XW - YL" subtitle

Helper function for initials:
```tsx
function getInitials(name: string): string {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}
```

Helper function for initials background color (deterministic from name):
```tsx
function getAvatarColor(name: string): string {
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
}
```

Podium layout:
```tsx
<section className="px-6 py-4">
  <div className="flex items-end justify-center gap-4 py-4">
    {/* 2nd place */}
    <div className="flex flex-col items-center gap-3 flex-1">...</div>
    {/* 1st place - raised with -mt-4 */}
    <div className="flex flex-col items-center gap-3 flex-1 -mt-4">...</div>
    {/* 3rd place */}
    <div className="flex flex-col items-center gap-3 flex-1">...</div>
  </div>
</section>
```

Handle edge cases: fewer than 3 players → show only available positions, hide empty podium slots.

**Step 2: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 3: Commit**

```bash
git add src/app/page.tsx
git commit -m "style: add top-3 podium layout to leaderboard page"
```

---

### Task 4: Restyle Leaderboard Page — Card Rows for 4th+ Players

**Files:**
- Modify: `src/app/page.tsx`

**Step 1: Replace table rows with card rows for 4th+ players**

Remove the `<table>` entirely. For players ranked 4th and below, render card rows:

```tsx
<main className="flex-1 px-6 pb-24">
  <div className="space-y-4 mt-6">
    {rankedRows.slice(3).map((player) => (
      <div key={player.id} className="flex items-center gap-4 bg-card-dark p-4 rounded-2xl hover:bg-slate-800/40 transition-all">
        <span className="w-4 text-sm font-bold text-slate-400">{player.rank}</span>
        <div className="w-12 h-12 rounded-full shrink-0 flex items-center justify-center text-white font-bold text-sm"
             style={{ backgroundColor: getAvatarColor(player.name) }}>
          {getInitials(player.name)}
        </div>
        <div className="flex-1">
          <p className="text-sm font-bold">{player.name}</p>
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
</main>
```

Update empty state styling for dark mode:
```tsx
<p className="text-slate-500 text-center py-12">No players yet</p>
```

**Step 2: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 3: Commit**

```bash
git add src/app/page.tsx
git commit -m "style: replace table with card rows for 4th+ players on leaderboard"
```

---

### Task 5: Restyle Log Match Page — Modal-Style Layout and Header

**Files:**
- Modify: `src/app/log-match/page.tsx`
- Modify: `src/app/log-match/LogMatchForm.tsx`

**Step 1: Add modal-style header with close button**

Update the page/form to have:
- A sticky header with close (X) button linking back to `/`, centered "Log Match" title, and a spacer div for alignment
- Background `bg-bg-log-match` (or inherit from layout — the design uses `#101622` which is slightly different from the leaderboard's `#0b121e`)

```tsx
<header className="sticky top-0 z-10 bg-bg-dark/80 backdrop-blur-md px-4 py-4 flex items-center justify-between border-b border-slate-800">
  <a href="/" className="w-10 h-10 flex items-center justify-start text-slate-500 hover:text-primary transition-colors">
    <span className="material-symbols-outlined text-2xl">close</span>
  </a>
  <h1 className="text-lg font-semibold tracking-tight">Log Match</h1>
  <div className="w-10"></div>
</header>
```

**Step 2: Restyle the match type toggle**

Update Singles/Doubles toggle buttons for dark mode:
- Active state: `bg-primary text-white border-primary`
- Inactive state: `bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800`

**Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 4: Commit**

```bash
git add src/app/log-match/page.tsx src/app/log-match/LogMatchForm.tsx
git commit -m "style: add modal-style header and dark mode to log match page"
```

---

### Task 6: Restyle Log Match Page — Player Dropdowns and "Who Played?" Section

**Files:**
- Modify: `src/app/log-match/LogMatchForm.tsx`

**Step 1: Restyle "Who played?" section**

Add the centered heading and subtitle from the design:
```tsx
<div className="text-center">
  <h2 className="text-2xl font-bold mb-1">Who played?</h2>
  <p className="text-slate-500 text-sm">Select the match participants.</p>
</div>
```

**Step 2: Restyle PlayerSelect for dark mode**

Update the PlayerSelect component to match the design:
- Labels: `text-[10px] font-bold uppercase tracking-widest text-primary ml-1`
- Select elements: `bg-slate-900 border border-slate-800 rounded-xl py-3 px-3 text-sm text-white focus:ring-2 focus:ring-primary/50`
- Custom chevron SVG via CSS (appearance: none with background-image)
- Grid layout: `grid grid-cols-2 gap-4` for singles mode

**Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 4: Commit**

```bash
git add src/app/log-match/LogMatchForm.tsx
git commit -m "style: restyle player dropdowns and Who Played section for dark mode"
```

---

### Task 7: Restyle Log Match Page — Winner Selection and Submit Button

**Files:**
- Modify: `src/app/log-match/LogMatchForm.tsx`

**Step 1: Restyle winner buttons**

Update the "Who won?" / "Which team won?" buttons:
- Primary color background, rounded-xl, full width or side-by-side
- Match the design's button styling with shadow

**Step 2: Restyle footer submit area**

Add a sticky/fixed footer with the "Submit Result" styled button per design:
- Full-width primary button with `rounded-2xl`, shadow, send icon
- Subtitle text below: "Rankings will be updated automatically."

Note: The current implementation uses winner-selection buttons (not a separate submit), which is the correct v1 adaptation of the design. Keep this pattern but style the buttons to match the design aesthetic.

**Step 3: Restyle result/error feedback for dark mode**

- Success: dark green tint background with green text
- Error: dark red tint background with red text

**Step 4: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 5: Commit**

```bash
git add src/app/log-match/LogMatchForm.tsx
git commit -m "style: restyle winner selection and feedback for dark mode design"
```

---

### Task 8: Restyle Admin Page for Dark Mode Consistency

**Files:**
- Modify: `src/app/admin/[secret]/AdminRosterForm.tsx`

**Step 1: Update admin page styling for dark mode**

No design reference exists for admin, but it should inherit the global dark theme for consistency:
- Form inputs: dark background, slate borders, white text
- Buttons: primary color
- Player list: card-dark background, slate dividers
- Labels and headings: white/slate text

**Step 2: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 3: Commit**

```bash
git add src/app/admin/[secret]/AdminRosterForm.tsx
git commit -m "style: update admin roster page for dark mode consistency"
```

---

### Task 9: Final Visual QA and Cleanup

**Files:**
- Possibly any of the above files

**Step 1: Run build to check for errors**

Run: `npm run build`
Expected: PASS (no build errors)

**Step 2: Run typecheck**

Run: `npx tsc --noEmit`
Expected: PASS

**Step 3: Run lint**

Run: `npm run lint`
Expected: PASS or only pre-existing warnings

**Step 4: Visual spot check**

Run dev server and verify:
- Leaderboard at 375px: dark theme, podium, card rows, FAB
- Log Match at 375px: dark theme, modal header, styled dropdowns, winner buttons
- Admin page: dark theme, functional form

**Step 5: Commit any cleanup**

```bash
git add -A
git commit -m "style: final QA cleanup for design alignment"
```
