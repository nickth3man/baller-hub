import Link from "next/link";
import { PlayerBoxScore } from "@/types";

function formatMinutes(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function PlayerStatsTable({
  players,
  teamLabel,
}: {
  players: PlayerBoxScore[];
  teamLabel: string;
}) {
  const starters = players.filter((p) => p.is_starter);
  const bench = players.filter((p) => !p.is_starter);

  const renderPlayerRow = (player: PlayerBoxScore, idx: number) => (
    <tr
      key={player.player_id}
      className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
    >
      <td className="px-3 py-2">
        <Link
          href={`/players/${player.slug}`}
          className="font-medium text-blue-600 hover:text-blue-800"
        >
          {player.name}
        </Link>
        <span className="ml-2 text-xs text-gray-500">
          {player.position
            ?.split("_")
            .map((w) => w[0])
            .join("") || ""}
        </span>
      </td>
      <td className="px-2 py-2 text-center text-gray-600">
        {formatMinutes(player.minutes)}
      </td>
      <td className="px-2 py-2 text-center font-semibold">{player.points}</td>
      <td className="px-2 py-2 text-center">{player.rebounds}</td>
      <td className="px-2 py-2 text-center">{player.assists}</td>
      <td className="px-2 py-2 text-center">{player.steals}</td>
      <td className="px-2 py-2 text-center">{player.blocks}</td>
      <td className="px-2 py-2 text-center">
        {player.fg_made}-{player.fg_attempted}
      </td>
      <td className="px-2 py-2 text-center">
        {player.fg3_made}-{player.fg3_attempted}
      </td>
      <td className="px-2 py-2 text-center">
        {player.ft_made}-{player.ft_attempted}
      </td>
      <td className="px-2 py-2 text-center">{player.turnovers}</td>
      <td className="px-2 py-2 text-center">{player.personal_fouls}</td>
      <td className="px-2 py-2 text-center">
        {player.plus_minus !== null
          ? player.plus_minus > 0
            ? `+${player.plus_minus}`
            : player.plus_minus
          : "-"}
      </td>
    </tr>
  );

  return (
    <div className="mb-6 overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">{teamLabel}</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="min-w-[150px] px-3 py-2 text-left">Player</th>
              <th className="px-2 py-2 text-center">MIN</th>
              <th className="px-2 py-2 text-center">PTS</th>
              <th className="px-2 py-2 text-center">REB</th>
              <th className="px-2 py-2 text-center">AST</th>
              <th className="px-2 py-2 text-center">STL</th>
              <th className="px-2 py-2 text-center">BLK</th>
              <th className="px-2 py-2 text-center">FG</th>
              <th className="px-2 py-2 text-center">3PT</th>
              <th className="px-2 py-2 text-center">FT</th>
              <th className="px-2 py-2 text-center">TO</th>
              <th className="px-2 py-2 text-center">PF</th>
              <th className="px-2 py-2 text-center">+/-</th>
            </tr>
          </thead>
          <tbody>
            {/* Starters */}
            {starters.length > 0 && (
              <>
                <tr className="bg-gray-200">
                  <td
                    colSpan={13}
                    className="px-3 py-1 text-xs font-semibold uppercase text-gray-600"
                  >
                    Starters
                  </td>
                </tr>
                {starters.map(renderPlayerRow)}
              </>
            )}

            {/* Bench */}
            {bench.length > 0 && (
              <>
                <tr className="bg-gray-200">
                  <td
                    colSpan={13}
                    className="px-3 py-1 text-xs font-semibold uppercase text-gray-600"
                  >
                    Bench
                  </td>
                </tr>
                {bench.map(renderPlayerRow)}
              </>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
