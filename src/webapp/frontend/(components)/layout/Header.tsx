import Link from "next/link";
import { SearchBar } from "./SearchBar";

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-bold text-gray-900">
              Basketball Reference
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
      className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
    >
      {children}
    </Link>
  );
}
