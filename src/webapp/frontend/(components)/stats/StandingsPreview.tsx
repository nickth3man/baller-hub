import Link from "next/link";
import { getSeasons, getStandings, StandingsTeam } from "@/lib/api";

export async function StandingsPreview() {
  const seasons = await getSeasons();
  const current = seasons.find((season) => season.is_active) || seasons[0];

  if (!current) {
    return (
      <div className="rounded-lg bg-white p-6 text-sm text-gray-500 shadow">
        Standings unavailable.
      </div>
    );
  }

  const standings = await getStandings(current.year);

  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xs uppercase tracking-[0.3em] text-slate-500">
          Standings
        </h2>
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
      <h3 className="mb-2 font-semibold text-gray-700">{conference}</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-xs text-gray-500">
            <th className="pb-1 text-left">Team</th>
            <th className="pb-1 text-right">W</th>
            <th className="pb-1 text-right">L</th>
            <th className="pb-1 text-right">PCT</th>
          </tr>
        </thead>
        <tbody>
          {teams.slice(0, 5).map((team, i) => (
            <tr
              key={team.abbreviation}
              className="border-b border-gray-100 last:border-0"
            >
              <td className="py-1">
                <span className="mr-2 text-gray-400">{i + 1}</span>
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
              <td
                colSpan={4}
                className="py-3 text-center text-xs text-gray-400"
              >
                No standings data.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
