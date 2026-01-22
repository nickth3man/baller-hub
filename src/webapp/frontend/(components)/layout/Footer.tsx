import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white/70">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 gap-8 py-10 md:grid-cols-4">
          <div>
            <h3 className="mb-3 font-display text-2xl uppercase tracking-[0.2em] text-slate-900">
              Baller Hub
            </h3>
            <p className="text-sm text-slate-500">
              A local basketball-reference clone for NBA statistics, game logs,
              and historical data.
            </p>
          </div>
          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
              Players
            </h4>
            <ul className="space-y-2 text-sm text-slate-500">
              <li>
                <Link href="/players" className="hover:text-slate-900">
                  All Players
                </Link>
              </li>
              <li>
                <Link
                  href="/players?is_active=true"
                  className="hover:text-slate-900"
                >
                  Active Players
                </Link>
              </li>
              <li>
                <Link
                  href="/search?type=player"
                  className="hover:text-slate-900"
                >
                  Search Players
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
              Teams
            </h4>
            <ul className="space-y-2 text-sm text-slate-500">
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
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
              Seasons
            </h4>
            <ul className="space-y-2 text-sm text-slate-500">
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
        <div className="border-t border-slate-200 pb-8 pt-6 text-center text-xs uppercase tracking-[0.3em] text-slate-400">
          <p>Data sourced from basketball-reference.com</p>
        </div>
      </div>
    </footer>
  );
}
