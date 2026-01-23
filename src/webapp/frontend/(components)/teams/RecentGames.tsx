import { TeamScheduleGame } from "@/types";

export function RecentGames({ games }: { games: TeamScheduleGame[] }) {
  const recentGames = games.slice(-5).reverse();
  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Recent Games</h2>
      <div className="space-y-3">
        {recentGames.map((game) => (
          <div
            key={game.game_id}
            className="flex items-center justify-between text-sm"
          >
            <div className="font-medium text-gray-900">
              {game.location === "HOME" ? "vs" : "@"} {game.opponent_abbrev}
            </div>
            <div className="text-gray-500">
              {game.team_score !== null && game.team_score !== undefined
                ? `${game.team_score}-${game.opponent_score}`
                : "TBD"}
            </div>
            <div className="text-gray-400">{game.result ?? "-"}</div>
          </div>
        ))}
        {recentGames.length === 0 && (
          <p className="text-sm text-gray-500">
            Schedule data will appear here.
          </p>
        )}
      </div>
    </div>
  );
}
