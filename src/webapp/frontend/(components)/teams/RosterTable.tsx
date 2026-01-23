import Link from "next/link";
import { RosterPlayer } from "@/types";

export function RosterTable({ roster, seasonYear }: { roster: RosterPlayer[], seasonYear: number }) {
  return (
    <div className="mb-6 overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="flex items-center justify-between bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Current Roster</h2>
        <span className="text-xs uppercase tracking-[0.2em] text-orange-200">
          {seasonYear} Season
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Player</th>
              <th className="px-3 py-3 text-center">Pos</th>
              <th className="px-3 py-3 text-center">GP</th>
              <th className="px-3 py-3 text-center">GS</th>
              <th className="px-3 py-3 text-center">PPG</th>
            </tr>
          </thead>
          <tbody>
            {roster.map((player, idx) => (
              <tr
                key={player.player_id}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/players/${player.slug}`}
                    className="font-medium text-blue-600 hover:text-blue-800"
                  >
                    {player.name}
                  </Link>
                </td>
                <td className="px-3 py-3 text-center text-gray-600">
                  {player.position
                    ? player.position
                        .replace("_", " ")
                        .split(" ")
                        .map((word) => word[0])
                        .join("")
                    : "-"}
                </td>
                <td className="px-3 py-3 text-center">{player.games_played}</td>
                <td className="px-3 py-3 text-center">
                  {player.games_started}
                </td>
                <td className="px-3 py-3 text-center font-medium">
                  {player.ppg !== null && player.ppg !== undefined
                    ? player.ppg.toFixed(1)
                    : "-"}
                </td>
              </tr>
            ))}
            {roster.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No roster data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
