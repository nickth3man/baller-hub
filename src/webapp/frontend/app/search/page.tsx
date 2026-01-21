import { Metadata } from 'next';
import Link from 'next/link';
import { search as apiSearch } from '@/lib/api';

export const metadata: Metadata = {
  title: 'Search Results | Basketball Reference',
  description: 'Search results for players and teams.',
};

interface PageProps {
  searchParams: Promise<{ q?: string }>;
}

export default async function SearchPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const query = params.q || '';
  
  const results = query ? await apiSearch(query) : { players: [], teams: [] };
  const hasResults = results.players.length > 0 || results.teams.length > 0;

  return (
    <div className="max-w-6xl mx-auto space-y-12 py-8 animate-in fade-in duration-500">
      <section className="border-b-4 border-black pb-8">
        <h1 className="text-6xl font-black text-gray-900 tracking-tighter uppercase">
          Search
        </h1>
        <div className="mt-6">
          <form action="/search" method="GET" className="flex gap-4">
            <input
              type="text"
              name="q"
              defaultValue={query}
              placeholder="Search players or teams..."
              className="flex-1 bg-white border-4 border-black px-6 py-4 text-2xl font-bold focus:outline-none focus:bg-yellow-50 transition-colors shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
            />
            <button
              type="submit"
              className="bg-black text-white px-10 py-4 text-2xl font-black uppercase hover:bg-gray-800 transition-colors shadow-[8px_8px_0px_0px_rgba(0,0,0,0.3)] active:shadow-none active:translate-x-1 active:translate-y-1"
            >
              Go
            </button>
          </form>
        </div>
      </section>

      {!query && (
        <div className="py-20 text-center">
          <p className="text-3xl font-black text-gray-300 uppercase tracking-widest">Enter a query to begin</p>
        </div>
      )}

      {query && !hasResults && (
        <div className="py-20 text-center bg-gray-50 border-4 border-dashed border-gray-200 rounded-3xl">
          <p className="text-2xl font-bold text-gray-400">No matches found for &quot;{query}&quot;</p>
          <p className="mt-2 text-gray-400">Try searching for a different name or team abbreviation.</p>
        </div>
      )}

      {hasResults && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Players Column */}
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <h2 className="text-3xl font-black uppercase tracking-tight text-black bg-yellow-400 px-4 py-1">Players</h2>
              <span className="text-sm font-black text-gray-400 uppercase">{results.players.length} Matches</span>
            </div>
            
            <div className="space-y-4">
              {results.players.map((player) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.slug}`}
                  className="group block bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-1 hover:-translate-y-1 transition-all"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-black group-hover:text-blue-700 transition-colors">
                        {player.full_name}
                      </h3>
                      <p className="text-sm font-bold text-gray-500 uppercase tracking-widest mt-1">
                        {player.position?.replace('_', ' ') || 'Unknown Position'}
                      </p>
                    </div>
                    {player.is_active && (
                      <span className="bg-green-100 text-green-700 text-[10px] font-black uppercase px-2 py-1 border border-green-700">
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
              <h2 className="text-3xl font-black uppercase tracking-tight text-white bg-blue-900 px-4 py-1">Teams</h2>
              <span className="text-sm font-black text-gray-400 uppercase">{results.teams.length} Matches</span>
            </div>

            <div className="space-y-4">
              {results.teams.map((team) => (
                <Link
                  key={team.team_id}
                  href={`/teams/${team.abbreviation}`}
                  className="group block bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-1 hover:-translate-y-1 transition-all"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-black group-hover:text-blue-900 transition-colors">
                        {team.name}
                      </h3>
                      <p className="text-sm font-bold text-gray-500 uppercase tracking-widest mt-1">
                        {team.city}
                      </p>
                    </div>
                    <span className="text-2xl font-black text-gray-200 group-hover:text-blue-900 transition-colors">
                      {team.abbreviation}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
