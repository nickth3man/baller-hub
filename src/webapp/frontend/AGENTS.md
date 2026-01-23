# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-22
**Context:** Next.js 15 App Router

## OVERVIEW
The user interface built with Next.js 15, utilizing the App Router for routing and React Server Components for performance. It interacts with the FastAPI backend via a strongly typed client.

## FOLDER STRUCTURE
- `app/`: App Router pages, layouts, and route groups.
- `(components)/`: Co-located domain components (e.g., `stats`, `layout`).
- `lib/`: Shared utilities and API client configuration.
- `hooks/`: Custom React hooks (strictly for logic reuse).

## CORE BEHAVIORS & PATTERNS
- **Server Components**: Default to Server Components; use `'use client'` only for interactivity.
- **Client Components**: Leaf nodes for state/effects; minimize client bundle size.
- **Data Fetching**: Use TanStack Query for client-side fetching/caching; native `fetch` for SCs.
- **Component Colocation**: Store domain-specific components near their usage (e.g., inside `(components)`).

## CONVENTIONS
- **Styling**: Tailwind CSS for all styling; `clsx`/`tailwind-merge` for class manipulation.
- **State**: `zustand` for global client state; URL search params for bookmarkable state.
- **Types**: Strict TypeScript; `interface` for Props.

## WORKING AGREEMENTS
- **Props**: Explicitly type all component props.
- **Hooks**: Isolate complex logic into custom hooks.
- **Imports**: Use absolute imports via `@/` alias.
- **Performance**: Monitor bundle size; import heavy libs dynamically if needed.
