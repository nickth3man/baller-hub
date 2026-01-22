import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white/70">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 py-10">
          <div>
            <h3 className="font-display text-2xl uppercase tracking-[0.2em] text-slate-900 mb-3">
              Baller Hub
            </h3>
            <p className="text-slate-500 text-sm">
              A local basketball-reference clone for NBA statistics, game logs,
              and historical data.
            </p>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 mb-3">
              Players
            </h4>
            <ul className="space-y-2 text-slate-500 text-sm">
              <li>
                <Link href="/players" className="hover:text-slate-900">
                  All Players
                </Link>
              </li>
              <li>
                <Link href="/players?is_active=true" className="hover:text-slate-900">
                  Active Players
                </Link>
              </li>
              <li>
                <Link href="/search?type=player" className="hover:text-slate-900">
                  Search Players
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 mb-3">
              Teams
            </h4>
            <ul className="space-y-2 text-slate-500 text-sm">
              <li>
                <Link href="/teams" className="hover:text-slate-900">
                  All Teams
                </Link>
              </li>
              <li>
                <Link href="/standings" className="hover:text-slate-900">
                  Standings
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 mb-3">
              Seasons
            </h4>
            <ul className="space-y-2 text-slate-500 text-sm">
              <li>
                <Link href="/seasons/2025" className="hover:text-slate-900">
                  2024-25 Season
                </Link>
              </li>
              <li>
                <Link href="/seasons" className="hover:text-slate-900">
                  All Seasons
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-slate-200 pb-8 pt-6 text-center text-slate-400 text-xs uppercase tracking-[0.3em]">
          <p>Data sourced from basketball-reference.com</p>
        </div>
      </div>
    </footer>
  );
}
