"use client";

import Link from "next/link";

export function StandingsPreview() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">Standings</h2>
        <Link href="/standings" className="text-sm text-primary-600 hover:underline">
          Full Standings
        </Link>
      </div>
      
      <div className="space-y-6">
        <ConferenceStandings conference="Eastern" teams={EAST_TEAMS} />
        <ConferenceStandings conference="Western" teams={WEST_TEAMS} />
      </div>
    </div>
  );
}

interface TeamStanding {
  abbrev: string;
  wins: number;
  losses: number;
}

function ConferenceStandings({
  conference,
  teams,
}: {
  conference: string;
  teams: TeamStanding[];
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
            <tr key={team.abbrev} className="border-b border-gray-100 last:border-0">
              <td className="py-1">
                <span className="text-gray-400 mr-2">{i + 1}</span>
                <Link
                  href={`/teams/${team.abbrev}`}
                  className="font-medium hover:text-primary-600"
                >
                  {team.abbrev}
                </Link>
              </td>
              <td className="text-right">{team.wins}</td>
              <td className="text-right">{team.losses}</td>
              <td className="text-right">
                {((team.wins / (team.wins + team.losses)) * 100).toFixed(1)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const EAST_TEAMS: TeamStanding[] = [
  { abbrev: "BOS", wins: 35, losses: 10 },
  { abbrev: "CLE", wins: 34, losses: 11 },
  { abbrev: "NYK", wins: 30, losses: 15 },
  { abbrev: "MIL", wins: 28, losses: 17 },
  { abbrev: "ORL", wins: 27, losses: 18 },
];

const WEST_TEAMS: TeamStanding[] = [
  { abbrev: "OKC", wins: 36, losses: 9 },
  { abbrev: "HOU", wins: 32, losses: 13 },
  { abbrev: "MEM", wins: 31, losses: 14 },
  { abbrev: "LAC", wins: 29, losses: 16 },
  { abbrev: "DEN", wins: 28, losses: 17 },
];
