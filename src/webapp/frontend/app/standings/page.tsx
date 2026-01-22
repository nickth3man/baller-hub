import { getSeasons, getStandings, StandingsTeam, StandingsView } from '@/lib/api';

function StandingsTable({ title, teams }: { title: string; teams: StandingsTeam[] }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      <div className="px-6 py-4 bg-slate-900 text-white">
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Team</th>
              <th className="px-3 py-3 text-center">W</th>
              <th className="px-3 py-3 text-center">L</th>
              <th className="px-3 py-3 text-center">PCT</th>
              <th className="px-3 py-3 text-center">GB</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team, idx) => (
              <tr key={team.team_id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-4 py-3 font-medium text-gray-900">{team.abbreviation}</td>
                <td className="px-3 py-3 text-center">{team.wins}</td>
                <td className="px-3 py-3 text-center">{team.losses}</td>
                <td className="px-3 py-3 text-center">{(team.win_pct * 100).toFixed(1)}%</td>
                <td className="px-3 py-3 text-center">{team.games_back.toFixed(1)}</td>
              </tr>
            ))}
            {teams.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-gray-500">
                  No standings available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface PageProps {
  searchParams: Promise<{ year?: string; view?: StandingsView }>;
}

export default async function StandingsPage({ searchParams }: PageProps) {
  const seasons = await getSeasons();
  const params = await searchParams;
  const current = seasons.find((season) => season.is_active) || seasons[0];

  if (!current) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-gray-500">
        Standings unavailable.
      </div>
    );
  }

  const seasonYear = params.year ? Number(params.year) || current.year : current.year;
  const view = params.view === 'league' ? 'league' : 'conference';
  const standings = await getStandings(seasonYear, view);

  return (
    <div className="max-w-6xl mx-auto py-12 space-y-8">
      <header className="text-center">
        <h1 className="text-5xl font-display uppercase tracking-[0.2em] text-gray-900">
          Standings
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          {seasonYear} season snapshot
        </p>
      </header>

      <form method="GET" className="flex flex-col md:flex-row gap-4 items-center justify-center">
        <select
          name="year"
          defaultValue={seasonYear}
          className="px-4 py-2 rounded-full border border-slate-300 text-sm uppercase tracking-[0.2em]"
        >
          {seasons.map((season) => (
            <option key={season.season_id} value={season.year}>
              {season.year}
            </option>
          ))}
        </select>
        <select
          name="view"
          defaultValue={view}
          className="px-4 py-2 rounded-full border border-slate-300 text-sm uppercase tracking-[0.2em]"
        >
          <option value="conference">Conference</option>
          <option value="league">League</option>
        </select>
        <button
          type="submit"
          className="px-6 py-2 rounded-full bg-slate-900 text-white text-xs uppercase tracking-[0.3em]"
        >
          Update
        </button>
      </form>

      {view === 'league' ? (
        <StandingsTable title="League Standings" teams={standings.league || []} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StandingsTable title="Eastern Conference" teams={standings.eastern || []} />
          <StandingsTable title="Western Conference" teams={standings.western || []} />
        </div>
      )}
    </div>
  );
}
