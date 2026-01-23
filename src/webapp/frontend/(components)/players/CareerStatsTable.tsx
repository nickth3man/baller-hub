import { PlayerSeasonStats } from "@/types";

function formatPercentage(made: number, attempted: number): string {
  if (attempted === 0) return "-";
  return ((made / attempted) * 100).toFixed(1);
}

export function CareerStatsTable({ stats }: { stats: PlayerSeasonStats[] }) {
  return (
    <div className="mb-6 overflow-hidden rounded-2xl bg-white shadow-lg">
      <div className="bg-slate-900 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Career Statistics</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-3 py-2 text-left">Season</th>
              <th className="px-3 py-2 text-center">G</th>
              <th className="px-3 py-2 text-center">GS</th>
              <th className="px-3 py-2 text-center">MPG</th>
              <th className="px-3 py-2 text-center">PPG</th>
              <th className="px-3 py-2 text-center">RPG</th>
              <th className="px-3 py-2 text-center">APG</th>
              <th className="px-3 py-2 text-center">SPG</th>
              <th className="px-3 py-2 text-center">BPG</th>
              <th className="px-3 py-2 text-center">FG%</th>
              <th className="px-3 py-2 text-center">3P%</th>
              <th className="px-3 py-2 text-center">FT%</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((season, idx) => {
              const gp = season.games_played || 1;
              return (
                <tr
                  key={`${season.season_id}-${season.season_type}`}
                  className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                >
                  <td className="px-3 py-2 font-medium">
                    {season.season_year}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {season.games_played}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {season.games_started}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {(season.minutes_played / gp).toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-center font-medium">
                    {(season.points / gp).toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {(season.rebounds / gp).toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {(season.assists / gp).toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {(season.steals / gp).toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {(season.blocks / gp).toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {formatPercentage(season.fg_made, season.fg_attempted)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {formatPercentage(season.fg3_made, season.fg3_attempted)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    {formatPercentage(season.ft_made, season.ft_attempted)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
