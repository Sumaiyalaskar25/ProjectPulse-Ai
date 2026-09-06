# ProjectPulse AI — Frontend

ProjectPulse AI is an AI-powered risk monitoring dashboard for national
infrastructure projects. It turns monthly cost/schedule/snapshot data into a
"command center" UI: a portfolio dashboard with live KPIs and risk matrices,
project deep dives, a what-if counterfactual risk simulator, alert triage,
maintenance tracking, and an AI assistant. The frontend is a Next.js 14 client
using the App Router, TypeScript, Tailwind CSS, React Query (TanStack Query) for
server state, Zustand for a couple of client-side stores, and Recharts for the
visualizations.

---

## Getting Started

- **Prerequisites:** [Node.js](https://nodejs.org) **18.17+** (Next.js 14
  requirement) and [pnpm](https://pnpm.io). This app lives in a pnpm workspace
  (`apps/web`), so pnpm is the expected package manager. No `.nvmrc` is
  committed — pin whatever Node works with your setup.

```bash
pnpm install        # install dependencies in the workspace
pnpm dev            # start the dev server
```

Open [http://localhost:3000](http://localhost:3000) — the root route redirects
you to `/dashboard`.

Production / lint commands:

```bash
pnpm build          # production build
pnpm start          # serve the production build
pnpm lint           # next lint
```

---

## Routes

All pages live under `app/(app)/` (the `(app)` group wraps them in the shared
`AppShell` with the sidebar + topbar). The root `app/page.tsx` just redirects
to `/dashboard`.

| Route | Page | Status |
| :--- | :--- | :--- |
| `/dashboard` | `app/(app)/dashboard/page.tsx` | **Fully built** — the only page wired to real-data hooks |
| `/national-assets` | `app/(app)/national-assets/page.tsx` | **Fully built** (inline mock data) |
| `/assistant` | `app/(app)/assistant/page.tsx` | **Fully built** (inline mock data) |
| `/risk-analytics` | `app/(app)/risk-analytics/page.tsx` | **Fully built** (inline mock data) |
| `/maintenance-log` | `app/(app)/maintenance-log/page.tsx` | **Fully built** (inline mock data) |
| `/alerts` | `app/(app)/alerts/page.tsx` | **Fully built** (inline mock data) |
| `/sources` (Data Sources) | `app/(app)/sources/page.tsx` | **Fully built** (renders `SOURCES` from `lib/data-sources`) |
| `/projects/[id]` (Project Deep Dive) | `app/(app)/projects/[id]/page.tsx` | **Fully built** (reads `lib/projects` local mock) |
| `/projects/[id]/simulate` (Risk Simulator) | `app/(app)/projects/[id]/simulate/page.tsx` | **Fully built** (local simulation engine) |
| `/settings` | `app/(app)/settings/page.tsx` | **Placeholder (no design yet)** — renders `ComingSoonPage` |

---

## Folder Structure

- **`app/`** — Next.js App Router pages and the root layout.
  `app/(app)/` groups all dashboard pages behind `AppShell`; `app/providers.tsx`
  mounts the React Query client and the toast renderer.
- **`components/`** — React components, grouped by feature area: `alerts/`,
  `assistant/`, `dashboard/`, `data-sources/`, `layout/` (Sidebar, Topbar,
  AppShell, ComingSoonPage), `maintenance-log/`, `national-assets/`,
  `project-deep-dive/`, `risk-analytics/`, `simulator/`, and `ui/` (shared
  primitives).
- **`hooks/`** — React Query hooks that wrap the API client and branch between
  mock and live data.
- **`lib/`** — Non-React logic: `api-client.ts` (fetch layer), `mock-data.ts`
  (mock implementations), `toast-store.ts` & `simulation-store.ts` (Zustand
  stores), `simulation.ts` (local simulator engine), plus mock data modules
  (`projects.ts`, `maintenance-records.ts`, `data-sources.ts`) and
  `design-tokens.ts` / `utils.ts`.
- **`types/`** — Shared TypeScript types describing the backend API contract
  (`types/api.ts`).
- **`styles/`** — Currently empty; the global Tailwind sheet lives in
  `app/globals.css`.

---

## Design System

**Design tokens** live in `tailwind.config.ts`. Under `theme.extend.colors` it
defines the dark "command center" palette (`background` with `surface`/`card`/
`card-hover`/`border` tones, the `status` colors `critical`/`high`/`moderate`/
`stable`/`info`, and `text` shades `primary`/`secondary`/`muted`). It also maps
the Inter and JetBrains Mono fonts loaded via `next/font` in `app/layout.tsx`.
Typography conventions (page titles, eyebrows, stat numbers, tech readouts) are
additionally centralized as reusable strings in `lib/design-tokens.ts`.

**Reusable UI primitives** live in `components/ui/` and currently contain:
`Badge.tsx`, `Button.tsx`, `Card.tsx`, `StatCard.tsx`, `PendingAction.tsx`, and
`Toasts.tsx`. `PendingAction` is the wrapper used on backend-dependent action
buttons (see below).

---

## Connecting to the Real Backend (read this first)

Today the app runs entirely on mock data. The Dashboard is the one page already
structured to consume real data through React Query; everything else renders
inline mock data. Here is how to flip the app to live mode.

1. **Copy the env template:**
   ```bash
   cp apps/web/.env.local.example apps/web/.env.local
   ```
2. **Set `NEXT_PUBLIC_API_BASE_URL`** to your real FastAPI server URL. The
   example defaults to `http://localhost:8000/api/v1`.
3. **Set `NEXT_PUBLIC_USE_MOCK_DATA=false`.** Every hook reads this flag at
   module load and switches between its mock and live query function.
4. **How the wiring works:** `lib/api-client.ts` contains the actual `fetch`
   functions (`getDashboardSummary`, `getProjects`, `getProject`, `getAlerts`,
   `getInterventions`, `queryAssistant`, etc.) whose endpoints already match the
   documented backend routes (`/dashboard/summary`, `/projects`, `/alerts`,
   `/assistant/query`, ...). `hooks/` contains the React Query hooks (`use-dashboard.ts`,
   `use-projects.ts`, `use-alerts.ts`, `use-assistant.ts`) that branch between
   the mock (`lib/mock-data.ts`) and live (`lib/api-client.ts`) implementations
   based on `NEXT_PUBLIC_USE_MOCK_DATA`.
5. **The reference pattern (the only page fully wired):** the Dashboard page
   (`app/(app)/dashboard/page.tsx`) renders `components/dashboard/
   DashboardWorkspace.tsx`, which renders `components/dashboard/DashboardData.tsx`.
   `DashboardData.tsx` calls `useDashboardSummary()` from `hooks/use-dashboard.ts`
   and `useProjects()` from `hooks/use-projects.ts`, and renders loading
   (`isLoading`), error (`isError`), and success states for each. **This is the
   pattern to copy for the other built pages.**

**Migrating the other pages** (National Assets, Risk Analytics, Maintenance
Log, Alerts, AI Assistant, Data Sources, Project Deep Dive, Risk Simulator) from
inline mock data to the hook pattern looks like this, using the Dashboard as the
worked example:

1. **Import the relevant hook.** In `DashboardData.tsx` that was
   `import { useDashboardSummary } from '@/hooks/use-dashboard'` and
   `import { useProjects } from '@/hooks/use-projects'`. A table page would
   import `useProjects(filters)` or `useAlerts(filters)`, etc.
2. **Replace the inline mock array with the hook's data.** The Dashboard reads
   `summary.data` / `projects.data` instead of a hard-coded `PROJECTS` array.
3. **Add a loading state.** Show a placeholder while `isLoading` is true (the
   Dashboard renders a `LOADING PORTFOLIO DATA...` line).
4. **Add an error state.** When `isError` is true, show a failure message
   (the Dashboard renders a `FAILED TO LOAD PORTFOLIO DATA` warning with an
   `AlertTriangle` icon).

The hooks already return properly typed data matching each page's component
props, so the migration is mostly swapping the data source and adding the
two branch states.

---

## State Management

- **Most UI state is local `useState`** per page/component — tabs, filters,
  search, toggles (e.g. `DashboardWorkspace` keeps its `quickView` filter in a
  `useState`). No global store for this.
- **The What-If Simulator uses a dedicated Zustand store**
  (`lib/simulation-store.ts`). This exists because the simulator's inputs,
  running flag, and result need to be shared across several sub-components
  (`SimulatorControls`, `InterventionParameters`, `SimulatedOutcome`,
  `AiRecommendation`) on the `simulate` page, and the slider positions must stay
  in sync everywhere. The actual computation lives in `lib/simulation.ts`
  (`runSimulation`).
- **The toast system** (`lib/toast-store.ts`) is another small Zustand store.
  It powers the "not yet connected to backend" message: `PendingAction` buttons
  call `show(backendPendingMessage)` (`"This action will be available once
  connected to the backend."`) and `Toasts.tsx` renders the stack. This is
  exactly how backend-dependent action buttons currently behave.

---

## Known Limitations / Not Yet Done

- **Settings page has no design yet** — `/settings` renders
  `components/layout/ComingSoonPage.tsx` with placeholder text.
- **Backend-dependent action buttons show a placeholder toast instead of
  performing real actions.** Wrapped in `components/ui/PendingAction.tsx`, these
  currently include: **Approve** (AlertTable), **Discuss** and **Execute**
  (AlertInsights), **Export Dossier** (ProjectHeader), **Escalate to Ministry
  Level** (RecommendationBar), **Export as Executive Brief** (AiRecommendation),
  **View** in the deteriorating projects table, **Force Resync** and the row
  eye/`View` action (MaintenanceTable), **Export Data** (ResultsTable),
  **Share Session** and **Export Insights** (ChatPanel), plus page-header
  buttons **View History** (Alerts), **Export Log** and **Schedule Maintenance**
  (Maintenance Log), **Export Portfolio** (National Assets), **Compare Period**,
  **Export Analysis** and **Re-Run Model** (Risk Analytics), and **Commit
  Scenario to Strategic Plan** (Simulator).
- **Almost every page is not yet wired to real data.** Only the Dashboard
  (`DashboardData.tsx`) consumes the React Query hooks; the other built pages
  still render inline mock / local data.
- **No authentication is implemented.** There is no login flow anywhere in the
  frontend — a post-hackathon requirement.

---

## For the Backend Developer Specifically

The API contract this frontend expects is defined in `types/api.ts` and
`lib/api-client.ts`. If your actual FastAPI response shapes differ from what's
assumed there (field names, nesting, date formats), the fastest fix is updating
`types/api.ts` and the corresponding function in `api-client.ts` to match your
real schema — the hooks and components don't need to change as long as the shape
returned by `api-client.ts` matches what `components/dashboard/
DashboardWorkspace.tsx` already expects.
