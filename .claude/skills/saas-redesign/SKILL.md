---
name: saas-redesign
description: Redesigns a Vue 3 application's UI into a modern SaaS-style interface with a vertical navigation sidebar on the left instead of a top nav bar, consistent spacing, and a polished professional look.
---

# SaaS UI Redesign

Transform the current top-nav layout into a modern SaaS-style interface with a fixed vertical sidebar, a clean content area, and a consistent design system. This skill targets `client/src/App.vue` and is aware of this project's specific components.

---

## Step 1 — Read the current layout

Read these files before making any changes:

- `client/src/App.vue` — current top nav, filter bar placement, global styles
- `client/src/components/FilterBar.vue` — filter bar markup and styles
- `client/src/components/ProfileMenu.vue` — user avatar trigger and dropdown
- `client/src/components/LanguageSwitcher.vue` — EN/JA toggle
- `client/src/main.js` — route list (to confirm all nav items)

This gives you the full picture before you propose anything.

---

## Step 2 — Confirm the design direction with the user

Present the following design plan and ask for approval before writing a single line of code. Show it as a concise before/after summary:

### What changes

| Area | Before | After |
|------|--------|-------|
| Navigation | Horizontal top bar, all links in a row | Fixed vertical sidebar, 240px wide |
| Logo/branding | Top-left in the nav bar | Top of sidebar |
| Nav links | Text-only horizontal tabs | Icon + label vertical list items |
| ProfileMenu | Top-right corner | Bottom of sidebar |
| LanguageSwitcher | Top-right corner | Bottom of sidebar, above profile |
| FilterBar | Full-width below the nav | Horizontal strip at top of the content area |
| Layout root | `flex-direction: column` | `flex-direction: row` |
| Content area | `max-width: 1600px; margin: auto` | Fills remaining width after sidebar |

### Sidebar design

- **Width:** 240px fixed
- **Background:** `#0f172a` (dark slate) with white/muted text — the existing brand color
- **Active item:** `#1e40af` background pill, white label
- **Hover item:** `#1e293b` background
- **Nav icons:** Inline SVG, 18px, one per route
- **Bottom section:** LanguageSwitcher + ProfileMenu, separated by a hairline border

### Content area design

- Background stays `#f8fafc`
- FilterBar becomes a sticky top strip (`background: white; border-bottom: 1px solid #e2e8f0; padding: 0.75rem 1.5rem`)
- Page content: `padding: 1.5rem`
- Global card/table/badge styles unchanged

Ask: **"Does this design direction look good? Any adjustments before I implement?"**

Wait for the user's answer. Adjust the plan if they request changes (e.g. light sidebar instead of dark, different width, collapsed sidebar, etc.) then re-confirm before proceeding.

---

## Step 3 — Delegate implementation to vue-expert

Once the user approves, hand off to the **vue-expert** subagent with the following precise brief. Do not implement `.vue` files yourself — the CLAUDE.md rule requires vue-expert for all significant `.vue` changes.

Tell vue-expert:

> Redesign `client/src/App.vue` to replace the horizontal top nav with a fixed 240px vertical sidebar. Here is the exact spec:
>
> **Layout root (`.app`):**
> - Change from `flex-direction: column` to `flex-direction: row`
> - Height: `100vh`, overflow: hidden
>
> **Sidebar (new `<aside class="sidebar">`):**
> - Fixed position is NOT needed — it's a flex child that stays in place
> - Width: `240px`, flex-shrink: 0
> - Height: `100vh`, overflow-y: auto
> - Background: `#0f172a`
> - Display: flex, flex-direction: column
> - Contains three sections:
>   1. **Top:** Logo block (`companyName` + `subtitle` from `useI18n`) with `padding: 1.25rem 1rem 1rem`
>   2. **Middle (flex: 1):** Vertical nav list — one item per route using `<router-link>`, each with an inline SVG icon (18×18) and a text label. Use `useRoute()` to detect the active path. Active style: `background: #1e40af; color: white; border-radius: 8px`. Hover style: `background: #1e293b`. Padding per item: `0.625rem 0.875rem`, gap between icon and label: `0.625rem`. Nav list padding: `0 0.75rem`.
>   3. **Bottom:** A `border-top: 1px solid #1e293b` separator, then `LanguageSwitcher` stacked above `ProfileMenu`, padding `0.75rem`.
>
> **Route → label → icon mapping** (use these exact inline SVGs):
>
> | Path | Label | Icon (outline style, stroke="currentColor" stroke-width="1.5") |
> |------|-------|------|
> | `/` | Overview (use `t('nav.overview')`) | `<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />` |
> | `/inventory` | Inventory (use `t('nav.inventory')`) | `<path stroke-linecap="round" stroke-linejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />` |
> | `/orders` | Orders (use `t('nav.orders')`) | `<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />` |
> | `/spending` | Finance (use `t('nav.finance')`) | `<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0 1 15.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 0 1 3 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 0 0-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 0 1-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 0 0 3 15h-.75M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm3 0h.008v.008H18V10.5Zm-12 0h.008v.008H6V10.5Z" />` |
> | `/demand` | Demand (use `t('nav.demandForecast')`) | `<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z" />` |
> | `/restocking` | Restocking (use `t('nav.restocking')`) | `<path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />` |
> | `/reports` | Reports | `<path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />` |
>
> **Content wrapper (new `<div class="content-wrapper">`):**
> - `flex: 1`, `overflow-y: auto`, `display: flex`, `flex-direction: column`
>
> **Filter bar (keep `<FilterBar />` but restyle):**
> - It stays at the top of the content wrapper, above `<router-view />`
> - Add a wrapper div: `background: white; border-bottom: 1px solid #e2e8f0; padding: 0 1.5rem; position: sticky; top: 0; z-index: 50`
> - The FilterBar itself should not need changes
>
> **Main content area (`.main-content`):**
> - Remove `max-width` and `margin: 0 auto` — it should stretch full width
> - Keep `padding: 1.5rem`
> - `flex: 1`
>
> **Global styles to update in `<style>` (not scoped):**
> - `.app`: `display: flex; flex-direction: row; min-height: 100vh; overflow: hidden`
> - Remove all `.top-nav`, `.nav-container`, `.nav-tabs` styles (they're replaced)
> - Keep all card, table, badge, stat-card, loading, error styles unchanged
> - Update `.main-content`: remove `max-width` and `margin: auto`, keep padding
>
> **Script changes:**
> - Add `import { useRoute } from 'vue-router'` and `const route = useRoute()` in setup()
> - Return `route` from setup()
> - Keep all existing task management logic (`loadTasks`, `addTask`, `deleteTask`, `toggleTask`) exactly as-is
> - Keep all existing imports and component registrations
>
> After implementing, verify in the browser at `http://localhost:3000` that:
> 1. The sidebar is visible and all 7 nav links render with icons
> 2. Clicking a nav link navigates correctly and the active item highlights
> 3. The FilterBar is visible below the sidebar top, above the page content
> 4. ProfileMenu and LanguageSwitcher are accessible at the bottom of the sidebar
> 5. The page content scrolls independently (sidebar stays fixed)
> 6. No regressions in cards, tables, or badges

---

## Step 4 — Post-implementation verification

After vue-expert completes, use Playwright to do a quick visual check:

1. Navigate to `http://localhost:3000` — confirm sidebar visible, Dashboard loads
2. Click each nav link — confirm route changes and active highlight moves
3. Click the profile avatar — confirm ProfileMenu opens
4. Check the FilterBar — confirm dropdowns are accessible and filter data

If anything is broken, use the **debugger** subagent to diagnose, then delegate fixes back to **vue-expert**.

---

## Design tokens reference

These are the existing tokens from `App.vue` — do not introduce new ones unless adding the sidebar:

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#f8fafc` | Page background |
| `--surface` | `#ffffff` | Cards, filter bar |
| `--border` | `#e2e8f0` | All borders |
| `--text-primary` | `#0f172a` | Headings |
| `--text-secondary` | `#64748b` | Labels, muted |
| `--text-body` | `#334155` | Table cells |
| `--blue` | `#2563eb` | Active states, links |
| `--sidebar-bg` | `#0f172a` | Sidebar background |
| `--sidebar-active` | `#1e40af` | Active nav item |
| `--sidebar-hover` | `#1e293b` | Hover nav item |
| `--sidebar-width` | `240px` | Fixed sidebar width |
