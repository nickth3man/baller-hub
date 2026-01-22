import { getTodaysGames, getTeams, Game, Team } from "@/lib/api";

function formatTime(time: string | null) {
  if (!time) return "Scheduled";
  const [hourStr, minute] = time.split(":");
  const hour = Number(hourStr);
  const displayHour = hour % 12 || 12;
  const suffix = hour >= 12 ? "PM" : "AM";
  return `${displayHour}:${minute} ${suffix} ET`;
}

function buildTeamMap(teams: Team[]) {
  return new Map(teams.map((team) => [team.abbreviation, team.name]));
}

export async function TodaysGames() {
  const [games, teams] = await Promise.all([getTodaysGames(), getTeams()]);
  const teamMap = buildTeamMap(teams);

  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-xs uppercase tracking-[0.3em] text-slate-500">
        Today's Games
      </h2>
      <div className="space-y-4">
        {games.map((game) => (
          <GameCard key={game.game_id} game={game} teamMap={teamMap} />
        ))}
        {games.length === 0 && (
          <div className="rounded-lg border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
            No games scheduled today.
          </div>
        )}
      </div>
    </div>
  );
}

function GameCard({
  game,
  teamMap,
}: {
  game: Game;
  teamMap: Map<string, string>;
}) {
  const isFinal = game.is_final;
  const awayAbbrev = game.away_team_abbrev || String(game.away_team_id);
  const homeAbbrev = game.home_team_abbrev || String(game.home_team_id);
  const awayName = teamMap.get(awayAbbrev) || awayAbbrev;
  const homeName = teamMap.get(homeAbbrev) || homeAbbrev;
  const status = isFinal ? "Final" : formatTime(game.time);

  return (
    <div className="rounded-lg border border-gray-200 p-4">
      <div className="mb-2 flex items-center justify-between">
        <span
          className={`text-xs font-medium ${
            isFinal ? "text-gray-500" : "text-green-600"
          }`}
        >
          {status}
        </span>
      </div>
      <div className="space-y-2">
        <TeamRow
          abbrev={awayAbbrev}
          name={awayName}
          score={game.away_score}
          isWinner={isFinal && (game.away_score ?? 0) > (game.home_score ?? 0)}
        />
        <TeamRow
          abbrev={homeAbbrev}
          name={homeName}
          score={game.home_score}
          isWinner={isFinal && (game.home_score ?? 0) > (game.away_score ?? 0)}
        />
      </div>
    </div>
  );
}

function TeamRow({
  abbrev,
  name,
  score,
  isWinner,
}: {
  abbrev: string;
  name: string;
  score: number | null | undefined;
  isWinner: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span
          className={`font-medium ${
            isWinner ? "text-gray-900" : "text-gray-600"
          }`}
        >
          {abbrev}
        </span>
        <span className="text-sm text-gray-500">{name}</span>
      </div>
      {score !== null && score !== undefined && (
        <span
          className={`text-lg font-bold ${
            isWinner ? "text-gray-900" : "text-gray-500"
          }`}
        >
          {score}
        </span>
      )}
    </div>
  );
}
