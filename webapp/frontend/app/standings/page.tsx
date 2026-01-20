import { getSeasons, getStandings, StandingsTeam } from '@/lib/api';

function StandingsTable({ title, teams }: { title: string; teams: StandingsTeam[] }) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 bg-blue-900 text-white">
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

export default async function StandingsPage() {
  const seasons = await getSeasons();
  const current = seasons.find((season) => season.is_active) || seasons[0];

  if (!current) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-gray-500">
        Standings unavailable.
      </div>
    );
  }

  const standings = await getStandings(current.year);

  return (
    <div className="max-w-6xl mx-auto py-12 space-y-8">
      <header className="text-center">
        <h1 className="text-5xl font-black text-gray-900">Standings</h1>
        <p className="mt-3 text-lg text-gray-500">
          {current.season_name} conference standings
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StandingsTable title="Eastern Conference" teams={standings.eastern || []} />
        <StandingsTable title="Western Conference" teams={standings.western || []} />
      </div>
    </div>
  );
}
