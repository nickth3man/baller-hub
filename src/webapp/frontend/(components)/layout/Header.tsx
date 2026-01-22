import Link from "next/link";
import { SearchBar } from "./SearchBar";

export function Header() {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link
              href="/"
              className="text-2xl font-display uppercase tracking-[0.2em] text-slate-900"
            >
              Baller Hub
            </Link>
            <nav className="hidden md:flex space-x-6">
              <NavLink href="/players">Players</NavLink>
              <NavLink href="/teams">Teams</NavLink>
              <NavLink href="/seasons">Seasons</NavLink>
              <NavLink href="/standings">Standings</NavLink>
              <NavLink href="/games">Games</NavLink>
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

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 hover:text-slate-900 transition-colors"
    >
      {children}
    </Link>
  );
}
