# src/webapp/frontend AGENTS.md

**Context:** Next.js 15 (App Router) Frontend.
**Parent:** `../AGENTS.md` (Webapp), `../../AGENTS.md` (Root)

## STRUCTURE
```
frontend/
├── app/             # App Router pages/layouts
├── components/
│   ├── ui/          # Generic UI (Button, Card)
│   ├── stats/       # Domain components
│   └── layout/      # Nav, Footer
├── lib/             # Utils, API client
└── hooks/           # Custom React hooks
```

## COMMANDS
```bash
# Dev
npm run dev

# Lint/Format
npm run lint
npm run format
```

## CONVENTIONS
- **Styling:** Tailwind CSS + `clsx`/`tailwind-merge`.
- **State:** Server Components (default) + TanStack Query (client).
- **Imports:** `@/*` alias for `src/webapp/frontend/*`.
- **API:** Proxy requests to backend via Next.js rewrites.

## ANTI-PATTERNS
- `useEffect` for data fetching (use TanStack Query).
- Client Components where Server Components suffice.
- Inline styles (use Tailwind).
