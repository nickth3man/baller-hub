import { SeasonScheduleGame } from "@/types";

export function ScheduleTable({ games }: { games: SeasonScheduleGame[] }) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Season Schedule</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-left">Visitor</th>
              <th className="px-4 py-3 text-left">Home</th>
              <th className="px-4 py-3 text-center">Score</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game, idx) => (
              <tr
                key={game.game_id}
                className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
              >
                <td className="px-4 py-3">
                  {new Date(game.date).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })}
                </td>
                <td className="px-4 py-3">{game.away_team_abbrev}</td>
                <td className="px-4 py-3">{game.home_team_abbrev}</td>
                <td className="px-4 py-3 text-center">
                  {game.home_score !== null && game.away_score !== null
                    ? `${game.away_score}-${game.home_score}`
                    : "TBD"}
                </td>
              </tr>
            ))}
            {games.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                  No schedule data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
