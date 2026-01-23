import Link from "next/link";
import { SearchBar } from "./SearchBar";

export function Header() {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link
              href="/"
              className="font-display text-2xl uppercase tracking-[0.2em] text-slate-900"
            >
              Baller Hub
            </Link>
            <nav className="hidden space-x-6 md:flex">
              <NavLink href="/players">Players</NavLink>
              <NavLink href="/teams">Teams</NavLink>
              <NavLink href="/seasons">Seasons</NavLink>
              <NavLink href="/standings">Standings</NavLink>
              <NavLink href="/games">Games</NavLink>
              <NavLink href="/draft">Draft</NavLink>
              <NavLink href="/awards">Awards</NavLink>
            </nav>
          </div>
          <div className="w-64">
            <SearchBar />
          </div>
        </div>
      </div>
    </header>
  );
}

function NavLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 transition-colors hover:text-slate-900"
    >
      {children}
    </Link>
  );
}
