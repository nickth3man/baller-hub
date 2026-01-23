import { BoxScoreResponse } from "@/types";

export function GameHeader({ boxScore }: { boxScore: BoxScoreResponse }) {
  const { game, home_team, away_team } = boxScore;
  const isFinal = game.is_final;
  const awayLabel = away_team.team_abbrev ?? String(away_team.team_id);
  const homeLabel = home_team.team_abbrev ?? String(home_team.team_id);
  const awayName = away_team.team_name ?? "Away";
  const homeName = home_team.team_name ?? "Home";
  const awayScore = away_team.score ?? 0;
  const homeScore = home_team.score ?? 0;

  return (
    <div className="mb-6 rounded-2xl bg-white p-6 shadow-lg">
      <div className="mb-4 text-center text-sm text-gray-500">
        {new Date(game.date).toLocaleDateString("en-US", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
        })}
        {game.arena && ` - ${game.arena}`}
      </div>

      <div className="flex items-center justify-center gap-8">
        {/* Away Team */}
        <div className="flex-1 text-center">
          <div className="mx-auto mb-2 flex h-20 w-20 items-center justify-center rounded-lg bg-gray-200 text-2xl font-bold text-gray-600">
            {awayLabel}
          </div>
          <p className="text-lg font-semibold text-gray-900">{awayName}</p>
          <p
            className={`text-4xl font-bold ${!isFinal ? "text-gray-400" : awayScore > homeScore ? "text-green-600" : "text-gray-900"}`}
          >
            {away_team.score ?? "-"}
          </p>
        </div>

        {/* VS / Final */}
        <div className="text-center">
          <p
            className={`text-lg font-bold ${isFinal ? "text-red-600" : "text-gray-400"}`}
          >
            {isFinal ? "FINAL" : "VS"}
          </p>
        </div>

        {/* Home Team */}
        <div className="flex-1 text-center">
          <div className="mx-auto mb-2 flex h-20 w-20 items-center justify-center rounded-lg bg-gray-200 text-2xl font-bold text-gray-600">
            {homeLabel}
          </div>
          <p className="text-lg font-semibold text-gray-900">{homeName}</p>
          <p
            className={`text-4xl font-bold ${!isFinal ? "text-gray-400" : homeScore > awayScore ? "text-green-600" : "text-gray-900"}`}
          >
            {home_team.score ?? "-"}
          </p>
        </div>
      </div>

      {/* Quarter Scores */}
      {(home_team.box_score?.quarter_scores ||
        away_team.box_score?.quarter_scores) && (
        <div className="mt-6 flex justify-center">
          <table className="text-sm">
            <thead>
              <tr className="text-gray-500">
                <th className="px-4 py-1"></th>
                <th className="px-3 py-1 text-center">Q1</th>
                <th className="px-3 py-1 text-center">Q2</th>
                <th className="px-3 py-1 text-center">Q3</th>
                <th className="px-3 py-1 text-center">Q4</th>
                <th className="px-3 py-1 text-center font-semibold">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="px-4 py-1 font-medium">{awayLabel}</td>
                <td className="px-3 py-1 text-center">
                  {away_team.box_score?.quarter_scores?.["1"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center">
                  {away_team.box_score?.quarter_scores?.["2"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center">
                  {away_team.box_score?.quarter_scores?.["3"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center">
                  {away_team.box_score?.quarter_scores?.["4"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center font-bold">
                  {away_team.score ?? "-"}
                </td>
              </tr>
              <tr>
                <td className="px-4 py-1 font-medium">{homeLabel}</td>
                <td className="px-3 py-1 text-center">
                  {home_team.box_score?.quarter_scores?.["1"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center">
                  {home_team.box_score?.quarter_scores?.["2"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center">
                  {home_team.box_score?.quarter_scores?.["3"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center">
                  {home_team.box_score?.quarter_scores?.["4"] ?? "-"}
                </td>
                <td className="px-3 py-1 text-center font-bold">
                  {home_team.score ?? "-"}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
