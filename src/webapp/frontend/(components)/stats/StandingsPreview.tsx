import Link from "next/link";
import { getSeasons, getStandings, StandingsTeam } from "@/lib/api";

export async function StandingsPreview() {
  const seasons = await getSeasons();
  const current = seasons.find((season) => season.is_active) || seasons[0];

  if (!current) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-sm text-gray-500">
        Standings unavailable.
      </div>
    );
  }

  const standings = await getStandings(current.year);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">Standings</h2>
        <Link
          href="/standings"
          className="text-sm text-primary-600 hover:underline"
        >
          Full Standings
        </Link>
      </div>

      <div className="space-y-6">
        <ConferenceStandings
          conference="Eastern"
          teams={standings.eastern || []}
        />
        <ConferenceStandings
          conference="Western"
          teams={standings.western || []}
        />
      </div>
    </div>
  );
}

function ConferenceStandings({
  conference,
  teams,
}: {
  conference: string;
  teams: StandingsTeam[];
}) {
  return (
    <div>
      <h3 className="font-semibold text-gray-700 mb-2">{conference}</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-500 text-xs">
            <th className="text-left pb-1">Team</th>
            <th className="text-right pb-1">W</th>
            <th className="text-right pb-1">L</th>
            <th className="text-right pb-1">PCT</th>
          </tr>
        </thead>
        <tbody>
          {teams.slice(0, 5).map((team, i) => (
            <tr
              key={team.abbreviation}
              className="border-b border-gray-100 last:border-0"
            >
              <td className="py-1">
                <span className="text-gray-400 mr-2">{i + 1}</span>
                <Link
                  href={`/teams/${team.abbreviation}`}
                  className="font-medium hover:text-primary-600"
                >
                  {team.abbreviation}
                </Link>
              </td>
              <td className="text-right">{team.wins}</td>
              <td className="text-right">{team.losses}</td>
              <td className="text-right">{(team.win_pct * 100).toFixed(1)}%</td>
            </tr>
          ))}
          {teams.length === 0 && (
            <tr>
              <td colSpan={4} className="py-3 text-center text-xs text-gray-400">
                No standings data.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
