import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-bold mb-4">Basketball Reference Clone</h3>
            <p className="text-gray-400 text-sm">
              A local clone of basketball-reference.com for NBA statistics and historical data.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Players</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li><Link href="/players" className="hover:text-white">All Players</Link></li>
              <li><Link href="/players?active=true" className="hover:text-white">Active Players</Link></li>
              <li><Link href="/search?type=player" className="hover:text-white">Search Players</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Teams</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li><Link href="/teams" className="hover:text-white">All Teams</Link></li>
              <li><Link href="/standings" className="hover:text-white">Standings</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Seasons</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li><Link href="/seasons/2025" className="hover:text-white">2024-25 Season</Link></li>
              <li><Link href="/seasons" className="hover:text-white">All Seasons</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>Data sourced from basketball-reference.com</p>
        </div>
      </div>
    </footer>
  );
}
