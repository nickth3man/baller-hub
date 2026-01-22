import { Metadata } from "next";
import Link from "next/link";
import { search as apiSearch } from "@/lib/api";

export const metadata: Metadata = {
  title: "Search Results | Basketball Reference",
  description: "Search results for players and teams.",
};

interface PageProps {
  searchParams: Promise<{ q?: string }>;
}

export default async function SearchPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const query = params.q || "";

  const results = query
    ? await apiSearch(query)
    : { players: [], teams: [], games: [] };
  const hasResults =
    results.players.length > 0 ||
    results.teams.length > 0 ||
    results.games.length > 0;

  return (
    <div className="animate-in fade-in mx-auto max-w-6xl space-y-12 py-8 duration-500">
      <section className="border-b-4 border-black pb-8">
        <h1 className="font-display text-6xl uppercase tracking-[0.2em] text-gray-900">
          Search
        </h1>
        <div className="mt-6">
          <form action="/search" method="GET" className="flex gap-4">
            <input
              type="text"
              name="q"
              defaultValue={query}
              placeholder="Search players or teams..."
              className="flex-1 border-4 border-black bg-white px-6 py-4 text-2xl font-bold shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-colors focus:bg-yellow-50 focus:outline-none"
            />
            <button
              type="submit"
              className="bg-black px-10 py-4 text-2xl font-black uppercase text-white shadow-[8px_8px_0px_0px_rgba(0,0,0,0.3)] transition-colors hover:bg-gray-800 active:translate-x-1 active:translate-y-1 active:shadow-none"
            >
              Go
            </button>
          </form>
        </div>
      </section>

      {!query && (
        <div className="py-20 text-center">
          <p className="text-3xl font-black uppercase tracking-widest text-gray-300">
            Enter a query to begin
          </p>
        </div>
      )}

      {query && !hasResults && (
        <div className="rounded-3xl border-4 border-dashed border-gray-200 bg-gray-50 py-20 text-center">
          <p className="text-2xl font-bold text-gray-400">
            No matches found for &quot;{query}&quot;
          </p>
          <p className="mt-2 text-gray-400">
            Try searching for a different name or team abbreviation.
          </p>
        </div>
      )}

      {hasResults && (
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
          {/* Players Column */}
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <h2 className="bg-yellow-400 px-4 py-1 text-3xl font-black uppercase tracking-tight text-black">
                Players
              </h2>
              <span className="text-sm font-black uppercase text-gray-400">
                {results.players.length} Matches
              </span>
            </div>

            <div className="space-y-4">
              {results.players.map((player) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.slug}`}
                  className="group block border-2 border-black bg-white p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:-translate-x-1 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-black transition-colors group-hover:text-blue-700">
                        {player.full_name}
                      </h3>
                      <p className="mt-1 text-sm font-bold uppercase tracking-widest text-gray-500">
                        {player.position?.replace("_", " ") ||
                          "Unknown Position"}
                      </p>
                    </div>
                    {player.is_active && (
                      <span className="border border-green-700 bg-green-100 px-2 py-1 text-[10px] font-black uppercase text-green-700">
                        Active
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Teams Column */}
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <h2 className="bg-blue-900 px-4 py-1 text-3xl font-black uppercase tracking-tight text-white">
                Teams
              </h2>
              <span className="text-sm font-black uppercase text-gray-400">
                {results.teams.length} Matches
              </span>
            </div>

            <div className="space-y-4">
              {results.teams.map((team) => (
                <Link
                  key={team.team_id}
                  href={`/teams/${team.abbreviation}`}
                  className="group block border-2 border-black bg-white p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:-translate-x-1 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-black transition-colors group-hover:text-blue-900">
                        {team.name}
                      </h3>
                      <p className="mt-1 text-sm font-bold uppercase tracking-widest text-gray-500">
                        {team.city}
                      </p>
                    </div>
                    <span className="text-2xl font-black text-gray-200 transition-colors group-hover:text-blue-900">
                      {team.abbreviation}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Games Column */}
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <h2 className="bg-slate-900 px-4 py-1 text-3xl font-black uppercase tracking-tight text-white">
                Games
              </h2>
              <span className="text-sm font-black uppercase text-gray-400">
                {results.games.length} Matches
              </span>
            </div>

            <div className="space-y-4">
              {results.games.map((game) => (
                <Link
                  key={game.game_id}
                  href={`/games/${game.game_id}`}
                  className="group block border-2 border-black bg-white p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:-translate-x-1 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="text-xl font-black transition-colors group-hover:text-orange-600">
                        {game.matchup}
                      </h3>
                      <p className="mt-1 text-xs font-bold uppercase tracking-widest text-gray-500">
                        {new Date(game.game_date).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </p>
                    </div>
                    <span className="text-lg font-black text-gray-400">
                      {game.score || "TBD"}
                    </span>
                  </div>
                </Link>
              ))}
              {results.games.length === 0 && (
                <div className="border-2 border-dashed border-gray-200 p-6 text-sm text-gray-400">
                  No game matches for this query.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
